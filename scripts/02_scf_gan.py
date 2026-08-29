import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import os
import re
import json
import argparse
from datetime import datetime

# 全局路径配置（匹配项目文件夹结构）
ROOT_PATH = "./"
CSV_PATH = os.path.join(ROOT_PATH, "data", "hf_csv")
MODEL_SAVE = os.getenv("SCF_MODEL_DIR", os.path.join(ROOT_PATH, "model"))
OUTPUT_PATH = os.getenv("SCF_OUTPUT_DIR", os.path.join(ROOT_PATH, "output"))
TARGET_BATTERY = os.getenv("TARGET_BATTERY", "B0018").strip()
TARGET_BATTERIES = [
    item.strip() for item in os.getenv("SCF_TARGET_BATTERIES", TARGET_BATTERY).split(",")
    if item.strip()
]
SOURCE_BATTERIES = [
    item.strip() for item in os.getenv("SCF_SOURCE_BATTERIES", "B0005,B0006").split(",")
    if item.strip()
]
SCF_ACTION = os.getenv("SCF_GAN_ACTION", "both").strip().lower()
SCF_SEED = int(os.getenv("SCF_GAN_SEED", "42"))
TARGET_TRAIN_FRACTION = float(os.getenv("TARGET_TRAIN_FRACTION", "0.6"))
os.makedirs(MODEL_SAVE, exist_ok=True)
os.makedirs(OUTPUT_PATH, exist_ok=True)

# 论文固定超参
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
NOISE_DIM = 8
COND_DIM = 2
FEAT_DIM = 3
HID_DIM = 256
LAMBDA_FM = float(os.getenv("SCF_LAMBDA_FM", "0.1"))
LR = float(os.getenv("SCF_LR", "0.001"))
BATCH_SIZE = int(os.getenv("SCF_BATCH_SIZE", "32"))
EPOCHS = int(os.getenv("SCF_EPOCHS", "800"))
SCALER_PATH = os.path.join(MODEL_SAVE, "scf_scaler.json")

# CSV脏数据清洗（处理[xx.xxx]字符串格式）
def clean_num(x):
    if isinstance(x, str):
        num = re.findall(r"\d+\.\d+|\d+", x)
        return float(num[0]) if num else np.nan
    return float(x)

# 数据集类：默认源电池B0005/B0006；可通过SCF_SOURCE_BATTERIES配置对照协议。
class BatteryHFDataset(Dataset):
    def __init__(self):
        source_bats = SOURCE_BATTERIES
        if len(source_bats) < 2:
            raise ValueError("SCF_SOURCE_BATTERIES 至少需要两个源电池")
        all_data = []
        for name in source_bats:
            csv_file = os.path.join(CSV_PATH, f"{name}_hf.csv")
            df = pd.read_csv(csv_file)
            # 清洗所有特征列
            for col in ["HF1","HF2","HF3","SOH"]:
                df[col] = df[col].apply(clean_num)
            df = df.dropna()
            feat = df[["HF1","HF2","HF3"]].values
            # 条件1：归一化循环序号；条件2：源电池域标识
            cycle_norm = np.linspace(0, 1, len(df)).reshape(-1,1)
            battery_domain = np.full((len(df), 1), len(all_data), dtype=float)
            cond_arr = np.hstack([cycle_norm, battery_domain])
            combine = np.hstack([feat, cond_arr])
            all_data.append(combine)
        data = np.vstack(all_data).astype(np.float32)
        self.feature_min = data[:, :FEAT_DIM].min(axis=0)
        self.feature_max = data[:, :FEAT_DIM].max(axis=0)
        scale = np.maximum(self.feature_max - self.feature_min, 1e-8)
        # Generator uses Tanh, therefore real features must use the same [-1, 1] domain.
        data[:, :FEAT_DIM] = 2.0 * (data[:, :FEAT_DIM] - self.feature_min) / scale - 1.0
        self.data = data

    def __len__(self):
        return len(self.data)
    def __getitem__(self, idx):
        row = self.data[idx]
        feat = row[:FEAT_DIM]
        cond = row[FEAT_DIM:]
        return torch.from_numpy(feat), torch.from_numpy(cond)

class ConditionalBatchNorm1d(nn.Module):
    """Batch normalization modulated by the two conditioning variables."""
    def __init__(self, num_features, cond_dim):
        super().__init__()
        self.bn = nn.BatchNorm1d(num_features, affine=False)
        self.affine = nn.Linear(cond_dim, num_features * 2)
        nn.init.zeros_(self.affine.weight)
        with torch.no_grad():
            self.affine.bias[:num_features].fill_(1.0)
            self.affine.bias[num_features:].zero_()

    def forward(self, x, c):
        gamma, beta = self.affine(c).chunk(2, dim=1)
        return gamma * self.bn(x) + beta


# 生成器：Eq. (7) 条件BN 8噪声+2条件 →256→512→256→3
class Generator(nn.Module):
    def __init__(self):
        super().__init__()
        self.in_dim = NOISE_DIM + COND_DIM
        self.fc1 = nn.Linear(self.in_dim, HID_DIM)
        self.bn1 = ConditionalBatchNorm1d(HID_DIM, COND_DIM)
        self.fc2 = nn.Linear(HID_DIM, HID_DIM*2)
        self.bn2 = ConditionalBatchNorm1d(HID_DIM*2, COND_DIM)
        self.fc3 = nn.Linear(HID_DIM*2, HID_DIM)
        self.bn3 = ConditionalBatchNorm1d(HID_DIM, COND_DIM)
        self.out = nn.Linear(HID_DIM, FEAT_DIM)
        self.leaky = nn.LeakyReLU(0.2)
        self.tanh = nn.Tanh()
    def forward(self, z, c):
        x = torch.cat([z, c], dim=1)
        x = self.leaky(self.bn1(self.fc1(x), c))
        x = self.leaky(self.bn2(self.fc2(x), c))
        x = self.leaky(self.bn3(self.fc3(x), c))
        return self.tanh(self.out(x))

# 判别器：Eq. (9)-(11)
# 输入5维(3特征+2条件) →256 →512 →256 →1
class Discriminator(nn.Module):
    def __init__(self):
        super().__init__()
        self.in_dim = FEAT_DIM + COND_DIM
        self.fc1 = nn.utils.spectral_norm(nn.Linear(self.in_dim, HID_DIM))       # 6 → 256
        self.fc2 = nn.utils.spectral_norm(nn.Linear(HID_DIM, HID_DIM*2))         # 256 → 512
        self.fc3 = nn.utils.spectral_norm(nn.Linear(HID_DIM*2, HID_DIM))         # 512 → 256
        self.out = nn.utils.spectral_norm(nn.Linear(HID_DIM, 1))                # 256 → 1
        self.leaky = nn.LeakyReLU(0.2)
    def forward(self, x, c):
        inp = torch.cat([x, c], dim=1)
        h1 = self.leaky(self.fc1(inp))    # [32,256]
        h2 = self.leaky(self.fc2(h1))    # [32,512]
        h3 = self.leaky(self.fc3(h2))    # [32,256]
        score = self.out(h3)
        return score, h3  # h3用于特征匹配损失


def feature_matching_loss(h_fake, h_real):
    """Eq. (12): E[||Phi_D(G(z|c)) - Phi_D(x)||_2^2]."""
    return torch.mean(torch.sum(torch.square(h_fake - h_real), dim=1))

# SCF-GAN训练函数（论文损失：对抗损失+0.1特征匹配损失）
def train_scf_gan():
    # The function is also imported by the grid runner, so seed here rather
    # than only in the legacy __main__ path.
    np.random.seed(SCF_SEED)
    torch.manual_seed(SCF_SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SCF_SEED)
    dataset = BatteryHFDataset()
    with open(SCALER_PATH, "w", encoding="utf-8") as f:
        json.dump({"min": dataset.feature_min.tolist(), "max": dataset.feature_max.tolist()}, f)
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, drop_last=True)
    gen = Generator().to(device)
    dis = Discriminator().to(device)
    opt_g = optim.Adam(gen.parameters(), lr=LR)
    opt_d = optim.Adam(dis.parameters(), lr=LR)
    loss_adv = nn.BCEWithLogitsLoss()

    print(f"==== 开始训练SCF-GAN：device={device}, epochs={EPOCHS}, seed={SCF_SEED} ====")
    history = []
    for ep in range(EPOCHS):
        total_d_loss = 0.0
        total_g_loss = 0.0
        total_fm_loss = 0.0
        for feat, cond in loader:
            feat, cond = feat.to(device), cond.to(device)
            bs = feat.shape[0]
            real_label = torch.ones((bs,1), device=device)
            fake_label = torch.zeros((bs,1), device=device)

            # 更新判别器
            opt_d.zero_grad()
            real_score, _ = dis(feat, cond)
            loss_d_real = loss_adv(real_score, real_label)
            z = torch.randn((bs, NOISE_DIM), device=device)
            fake_feat = gen(z, cond)
            fake_score, _ = dis(fake_feat.detach(), cond)
            loss_d_fake = loss_adv(fake_score, fake_label)
            loss_d = loss_d_real + loss_d_fake
            loss_d.backward()
            opt_d.step()
            total_d_loss += loss_d.item()

            # 更新生成器
            opt_g.zero_grad()
            fake_score, h_fake = dis(fake_feat, cond)
            loss_g_adv = loss_adv(fake_score, real_label)
            with torch.no_grad():
                _, h_real = dis(feat, cond)
            # Eq. (12) pairs real/fake discriminator features under the same c.
            loss_fm = feature_matching_loss(h_fake, h_real)
            loss_g = loss_g_adv + LAMBDA_FM * loss_fm
            loss_g.backward()
            opt_g.step()
            total_g_loss += loss_g.item()
            total_fm_loss += loss_fm.item()

        record = {
            "Epoch": ep + 1,
            "DLoss": total_d_loss / len(loader),
            "GLoss": total_g_loss / len(loader),
            "FMLoss": total_fm_loss / len(loader),
        }
        history.append(record)
        if ep == 0 or (ep + 1) % 50 == 0 or ep + 1 == EPOCHS:
            print(f"Epoch {ep + 1:04} | D Loss:{record['DLoss']:.4f} | G Loss:{record['GLoss']:.4f} | FM Loss:{record['FMLoss']:.4f}")
    # 保存模型权重
    torch.save(gen.state_dict(), os.path.join(MODEL_SAVE, "scf_generator.pth"))
    torch.save(dis.state_dict(), os.path.join(MODEL_SAVE, "scf_discriminator.pth"))
    pd.DataFrame(history).to_csv(
        os.path.join(MODEL_SAVE, "scf_training_log.csv"), index=False, encoding="utf-8-sig"
    )
    manifest = {
        "schema": "scf_gan_training/2",
        "completed_at": datetime.now().isoformat(),
        "source_batteries": SOURCE_BATTERIES,
        "epochs_requested": EPOCHS,
        "epochs_completed": len(history),
        "seed": SCF_SEED,
        "device": str(device),
        "noise_dim": NOISE_DIM,
        "condition_dim": COND_DIM,
        "feature_dim": FEAT_DIM,
        "hidden_dim": HID_DIM,
        "lambda_feature_matching": LAMBDA_FM,
        "learning_rate": LR,
        "batch_size": BATCH_SIZE,
        "paper_alignment": {
            "generator": "Eq.7 conditional-BN MLP with LeakyReLU and Tanh",
            "discriminator": "Eq.9-11 spectral-normalized MLP",
            "feature_matching": "Eq.12 samplewise squared L2 expectation",
        },
    }
    with open(os.path.join(MODEL_SAVE, "scf_training_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"==== SCF-GAN训练完成，权重已保存至 {MODEL_SAVE} ====")
    return manifest

# 为目标电池真实训练段生成5套HF特征；SOH标签始终来自真实目标电池。
def generate_aug_data(target_battery=None):
    target_battery = (target_battery or TARGET_BATTERY).strip()
    gen = Generator().to(device)
    checkpoint_path = os.path.join(MODEL_SAVE, "scf_generator.pth")
    try:
        gen.load_state_dict(torch.load(checkpoint_path, map_location=device))
    except RuntimeError as exc:
        raise RuntimeError(
            "SCF-GAN结构已按论文Eq. (7)更新，旧生成器权重不兼容；"
            "请使用 SCF_GAN_ACTION=both 重新训练后再生成数据。"
        ) from exc
    gen.eval()
    with open(SCALER_PATH, "r", encoding="utf-8") as f:
        scaler = json.load(f)
    feature_min = np.asarray(scaler["min"], dtype=np.float32)
    feature_max = np.asarray(scaler["max"], dtype=np.float32)
    if target_battery in SOURCE_BATTERIES:
        raise ValueError(f"目标电池 {target_battery} 已在源电池 {SOURCE_BATTERIES} 中，拒绝生成目标增强数据")
    target_path = os.path.join(CSV_PATH, f"{target_battery}_hf.csv")
    if not os.path.isfile(target_path):
        raise FileNotFoundError(f"目标电池HF文件不存在: {target_path}")
    df_raw = pd.read_csv(target_path)
    # 清洗数据
    for col in ["HF1","HF2","HF3","SOH"]:
        df_raw[col] = df_raw[col].apply(clean_num)
    df_raw = df_raw.dropna()
    if not 0 < TARGET_TRAIN_FRACTION < 1:
        raise ValueError("TARGET_TRAIN_FRACTION 必须在(0,1)内")
    train_len = int(len(df_raw) * TARGET_TRAIN_FRACTION)
    train_df = df_raw.iloc[:train_len].reset_index(drop=True)
    cycle_cond = np.arange(train_len, dtype=np.float32) / max(len(df_raw) - 1, 1)
    rows = []
    # Dataset 0 is the untouched real training trajectory.
    for i, row in train_df.iterrows():
        rows.append([0, i, row.HF1, row.HF2, row.HF3, row.SOH])
    with torch.no_grad():
        for dataset_id in range(1, 6):
            # 0.5 interpolates between the two source-battery domains.
            cond_np = np.column_stack([cycle_cond, np.full(train_len, 0.5)]).astype(np.float32)
            cond = torch.from_numpy(cond_np).to(device)
            z = torch.randn((train_len, NOISE_DIM), device=device)
            fake_scaled = gen(z, cond).cpu().numpy()
            fake_hf = (fake_scaled + 1.0) * 0.5 * (feature_max - feature_min) + feature_min
            fake_hf = np.maximum(fake_hf, 0.0)
            for i in range(train_len):
                # The label is the real target SOH at this training cycle.
                rows.append([dataset_id, i, *fake_hf[i], train_df.loc[i, "SOH"]])
    aug_df = pd.DataFrame(rows, columns=["DatasetID", "Cycle", "HF1", "HF2", "HF3", "SOH"])
    save_path = os.path.join(OUTPUT_PATH, f"{target_battery}_aug_train_hf.csv")
    aug_df.to_csv(save_path, index=False, encoding="utf-8-sig")
    print(f"{target_battery} 训练集增强完成：真实{train_len}条 + 5套合成HF，共{len(aug_df)}条；验证/测试未增强")
    return save_path


def parse_args():
    parser = argparse.ArgumentParser(description="Train and run the paper-aligned SCF-GAN")
    parser.add_argument("--action", choices=["train", "generate", "both"], default=SCF_ACTION)
    parser.add_argument("--sources", default=",".join(SOURCE_BATTERIES))
    parser.add_argument("--targets", default=",".join(TARGET_BATTERIES))
    parser.add_argument("--epochs", type=int, default=EPOCHS)
    parser.add_argument("--seed", type=int, default=SCF_SEED)
    parser.add_argument("--target-fraction", type=float, default=TARGET_TRAIN_FRACTION)
    parser.add_argument("--model-dir", default=MODEL_SAVE)
    parser.add_argument("--output-dir", default=OUTPUT_PATH)
    parser.add_argument("--lr", type=float, default=LR)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--lambda-fm", type=float, default=LAMBDA_FM)
    return parser.parse_args()


def apply_args(args):
    global SOURCE_BATTERIES, TARGET_BATTERIES, SCF_ACTION, SCF_SEED
    global TARGET_TRAIN_FRACTION, MODEL_SAVE, OUTPUT_PATH, SCALER_PATH
    global EPOCHS, LR, BATCH_SIZE, LAMBDA_FM
    SOURCE_BATTERIES = [x.strip() for x in args.sources.split(",") if x.strip()]
    TARGET_BATTERIES = [x.strip() for x in args.targets.split(",") if x.strip()]
    SCF_ACTION = args.action
    SCF_SEED = args.seed
    TARGET_TRAIN_FRACTION = args.target_fraction
    MODEL_SAVE = os.path.abspath(args.model_dir)
    OUTPUT_PATH = os.path.abspath(args.output_dir)
    EPOCHS, LR, BATCH_SIZE, LAMBDA_FM = args.epochs, args.lr, args.batch_size, args.lambda_fm
    SCALER_PATH = os.path.join(MODEL_SAVE, "scf_scaler.json")
    os.makedirs(MODEL_SAVE, exist_ok=True)
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    if EPOCHS <= 0 or BATCH_SIZE <= 1 or LR <= 0 or LAMBDA_FM < 0:
        raise ValueError("epochs/LR/batch-size/lambda-fm 参数非法")
    if not 0 < TARGET_TRAIN_FRACTION < 1:
        raise ValueError("target-fraction 必须在 (0,1) 内")

if __name__ == "__main__":
    apply_args(parse_args())
    if SCF_ACTION not in {"train", "generate", "both"}:
        raise ValueError("SCF_GAN_ACTION 必须为 train/generate/both")
    np.random.seed(SCF_SEED)
    torch.manual_seed(SCF_SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SCF_SEED)
    if SCF_ACTION in {"train", "both"}:
        train_scf_gan()
    if SCF_ACTION in {"generate", "both"}:
        for target in TARGET_BATTERIES:
            generate_aug_data(target)
