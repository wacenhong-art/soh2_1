import os
import random
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# ============================================================
# 04_attention_fusion_fixed.py
# 修复点：
# 1) 禁止使用 True_Trend/True_Seasonal/True_Residual 构造输入，避免标签泄漏
# 2) 对最终 SOH 目标做训练集标准化
# 3) 不再对三个物理分量做 LayerNorm(3)，保留 STL 加性尺度
# 4) 严格采用论文动态权重与3->16->1预测头
# 5) 删除单层 LSTM 无效 dropout，消除 PyTorch 警告
# ============================================================

ROOT_PATH = "./"
OUTPUT_PATH = os.path.join(ROOT_PATH, "output")
MODEL_SAVE = os.path.join(ROOT_PATH, "model")
OUT_GMTC = os.path.join(OUTPUT_PATH, "gmtc_pred_result.csv")

os.makedirs(OUTPUT_PATH, exist_ok=True)
os.makedirs(MODEL_SAVE, exist_ok=True)

SEED = 42
SEQ_LEN = 10
BATCH_SIZE = 32
LR = 1e-3
EPOCHS = 800
PATIENCE = 50
WEIGHT_DECAY = 1e-5
LSTM_HIDDEN = 16

# Eq. (24) only publishes L_total = L_pred + lambda * L_weight.  The paper
# does not disclose L_weight itself.  This repository therefore uses the
# explicitly project-defined load-balancing completion documented below.
LAMBDA_WEIGHT = 0.0
L_WEIGHT_STATUS = "REPRO_DEFINED_NOT_PAPER_ORIGINAL"
L_WEIGHT_FORMULA = "KL(mean_batch(component_weights) || Uniform(3))"
L_WEIGHT_DISABLED_STATUS = "UNVERIFIED_DISABLED"
CATASTROPHIC_MIN = 50.0
CATASTROPHIC_MAX = 110.0
RESIDUAL_BOUND_NUMERICAL_TOLERANCE = 1e-4

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def set_seed(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def zscore_fit(x, axis=0):
    mean = np.mean(x, axis=axis)
    std = np.std(x, axis=axis)
    std = np.where(std < 1e-8, 1.0, std)
    return mean, std


def sliding_windows(seq_features, comp_features, target, seq_len):
    xs, comps, ys = [], [], []
    for i in range(len(target) - seq_len):
        xs.append(seq_features[i:i + seq_len])
        comps.append(comp_features[i + seq_len])
        ys.append(target[i + seq_len])
    return (
        np.asarray(xs, dtype=np.float32),
        np.asarray(comps, dtype=np.float32),
        np.asarray(ys, dtype=np.float32),
    )


def validate_component_df(df, name):
    required = {"Pred_Trend", "Pred_Seasonal", "Pred_Residual"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"{name} 缺少列：{sorted(missing)}")
    has_true_soh = "True_SOH" in df.columns
    has_true_components = {
        "True_Trend", "True_Seasonal", "True_Residual"
    }.issubset(df.columns)
    if not (has_true_soh or has_true_components):
        raise ValueError(
            f"{name} 必须包含 True_SOH，或完整的三个 True_* 分量列"
        )
    if len(df) <= SEQ_LEN:
        raise ValueError(f"{name} 仅有 {len(df)} 行，必须大于 SEQ_LEN={SEQ_LEN}")
    if df.isna().any().any():
        raise ValueError(f"{name} 含 NaN，请先清洗。")


def build_causal_features(df, comp_mean, comp_std):
    """
    仅使用推理时可获得的预测分量构造 9 维特征：
    1) 三个预测分量的标准化值
    2) 三个预测分量的一阶增量
    3) 三个分量绝对值占比

    严格测试段不使用当前或此前测试循环的真实 SOH/STL 分量标签。
    """
    pred = df[["Pred_Trend", "Pred_Seasonal", "Pred_Residual"]].to_numpy(dtype=np.float32)
    pred_z = (pred - comp_mean) / comp_std
    delta_z = np.vstack([np.zeros((1, 3), dtype=np.float32), np.diff(pred_z, axis=0)])

    abs_sum = np.abs(pred).sum(axis=1, keepdims=True)
    ratio = np.abs(pred) / np.maximum(abs_sum, 1e-8)

    return np.concatenate([pred_z, delta_z, ratio], axis=1).astype(np.float32)


def true_soh_target(df):
    """Return the evaluation/training target without exposing it to model inputs."""
    if "True_SOH" in df.columns:
        return df["True_SOH"].to_numpy(dtype=np.float32)
    return (
        df["True_Trend"].to_numpy(dtype=np.float32)
        + df["True_Seasonal"].to_numpy(dtype=np.float32)
        + df["True_Residual"].to_numpy(dtype=np.float32)
    )


class FusionDataset(Dataset):
    def __init__(self, x_seq, x_comp, y_z):
        self.x_seq = torch.as_tensor(x_seq, dtype=torch.float32)
        self.x_comp_z = torch.as_tensor(x_comp, dtype=torch.float32)
        self.y_z = torch.as_tensor(y_z, dtype=torch.float32).unsqueeze(-1)

    def __len__(self):
        return len(self.y_z)

    def __getitem__(self, idx):
        return self.x_seq[idx], self.x_comp_z[idx], self.y_z[idx]


class ComponentAttention(nn.Module):
    def __init__(self, feat_dim=9):
        super().__init__()
        self.theta_c = nn.Parameter(torch.zeros(feat_dim))

    def forward(self, x):
        # Eq. (25): x_attn = x * Softmax(theta_c).
        attn = torch.softmax(self.theta_c, dim=0)
        return x * attn


class TemporalAttention(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.score = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, 1),
        )

    def forward(self, x):
        alpha = torch.softmax(self.score(x), dim=1)
        return torch.sum(alpha * x, dim=1)


class AttentionBiLSTMFusion(nn.Module):
    def __init__(self, comp_mean, comp_std, y_mean, y_std, feat_dim=9, hidden=LSTM_HIDDEN,
                 fusion_mode="paper", stable_init=False, residual_epsilon=None,
                 capacity_variant="C0_FULL_BILSTM"):
        super().__init__()
        if fusion_mode not in {"paper", "residual"}:
            raise ValueError("fusion_mode 仅支持 paper 或 residual")
        if fusion_mode == "residual" and residual_epsilon not in {0.02, 0.05, 0.10}:
            raise ValueError("residual 模式的 epsilon 只允许 0.02/0.05/0.10")
        self.fusion_mode = fusion_mode
        if capacity_variant not in {"C0_FULL_BILSTM", "C1_SMALL_BILSTM", "C2_TINY_GRU", "C3_NONRECURRENT", "C4_MINIMAL"}:
            raise ValueError("未知 capacity_variant")
        self.capacity_variant = capacity_variant
        self.residual_epsilon = residual_epsilon
        self.residual_bound_pp = None if residual_epsilon is None else 100.0 * residual_epsilon
        self.register_buffer("comp_mean", torch.as_tensor(comp_mean, dtype=torch.float32))
        self.register_buffer("comp_std", torch.as_tensor(comp_std, dtype=torch.float32))
        self.register_buffer("y_mean", torch.tensor(float(y_mean), dtype=torch.float32))
        self.register_buffer("y_std", torch.tensor(float(y_std), dtype=torch.float32))
        self.comp_attn = ComponentAttention(feat_dim)
        if capacity_variant == "C4_MINIMAL":
            # Phase 3B: only current [T,S,R] may generate weights/correction.
            self.recurrent = None
            self.temp_attn = None
            context_dim = 3
            self.weight_net = nn.Linear(3, 3)
            residual_hidden = 4
        elif capacity_variant == "C3_NONRECURRENT":
            # Phase 3B: current 9-D causal fusion feature, no recurrent state.
            self.recurrent = None
            self.temp_attn = None
            context_dim = feat_dim
            self.weight_net = nn.Sequential(nn.Linear(feat_dim, 16), nn.ReLU(), nn.Linear(16, 3))
            residual_hidden = 8
        elif capacity_variant == "C2_TINY_GRU":
            # Phase 3A pre-registered tiny recurrent enhancement: 9-D input,
            # one unidirectional GRU(8), 8->24->3 weight head, 11->24->1 residual head.
            self.recurrent = nn.GRU(feat_dim, 8, num_layers=1, batch_first=True)
            self.temp_attn = None
            context_dim = 8
            self.weight_net = nn.Sequential(nn.Linear(8, 24), nn.ReLU(), nn.Linear(24, 3))
            residual_hidden = 24
        else:
            recurrent_hidden = 16 if capacity_variant == "C0_FULL_BILSTM" else 8
            self.recurrent = nn.LSTM(
                input_size=feat_dim, hidden_size=recurrent_hidden, num_layers=1,
                batch_first=True, bidirectional=True, dropout=0.0,
            )
            context_dim = recurrent_hidden * 2
            self.temp_attn = TemporalAttention(context_dim)
            if capacity_variant == "C0_FULL_BILSTM":
                widths = (128, 64, 32); residual_hidden = 16
            else:
                # C1 scales all post-Bi-LSTM MLP widths by one half.
                widths = (64, 32, 16); residual_hidden = 8
            self.weight_net = nn.Sequential(
                nn.Linear(context_dim, widths[0]), nn.LeakyReLU(0.1), nn.BatchNorm1d(widths[0]),
                nn.Linear(widths[0], widths[1]), nn.LeakyReLU(0.1), nn.BatchNorm1d(widths[1]),
                nn.Linear(widths[1], widths[2]), nn.LeakyReLU(0.1), nn.Dropout(0.3),
                nn.Linear(widths[2], 3),
            )

        # Paper Table 4 / Eq. (28): weighted three components -> 3 -> 16 -> 1.
        self.predict_head = (nn.Identity() if capacity_variant in {"C3_NONRECURRENT", "C4_MINIMAL"}
                             else nn.Sequential(nn.Linear(3, 16), nn.ReLU(), nn.Linear(16, 1)))
        # New module: STL Identity-Preserving Residual Fusion (IPRF).
        # It retains T+S+R and learns only a bounded attention correction.
        residual_input_dim = context_dim if capacity_variant in {"C3_NONRECURRENT", "C4_MINIMAL"} else context_dim + 3
        self.residual_head = nn.Sequential(
            nn.Linear(residual_input_dim, residual_hidden),
            nn.ReLU(),
            nn.Linear(residual_hidden, 1),
        )
        if stable_init and fusion_mode == "paper":
            self.initialize_additive_reconstruction()

    def initialize_additive_reconstruction(self):
        """P1 initialization: begin near T+S+R without changing the network."""
        final_weight_layer = self.weight_net[-1]
        nn.init.zeros_(final_weight_layer.weight)
        nn.init.zeros_(final_weight_layer.bias)
        hidden_layer, output_layer = self.predict_head[0], self.predict_head[2]
        nn.init.zeros_(hidden_layer.weight); nn.init.zeros_(hidden_layer.bias)
        nn.init.zeros_(output_layer.weight); nn.init.zeros_(output_layer.bias)
        for index in range(3):
            hidden_layer.weight.data[2 * index, index] = 1.0
            hidden_layer.weight.data[2 * index + 1, index] = -1.0
            coefficient = 3.0
            output_layer.weight.data[0, 2 * index] = coefficient
            output_layer.weight.data[0, 2 * index + 1] = -coefficient
        output_layer.bias.data.zero_()

    def encode_context(self, x_seq):
        """Return the existing Attention Bi-LSTM temporal representation.

        This is an interface extraction only: the paper-path forward pass uses
        the same operations and parameters as before.  CILA consumes this
        representation in a separate experiment runner without replacing the
        fusion network.
        """
        x_seq = self.comp_attn(x_seq)
        if self.capacity_variant == "C4_MINIMAL":
            return None
        if self.capacity_variant == "C3_NONRECURRENT":
            return x_seq[:, -1, :]
        recurrent_out, _ = self.recurrent(x_seq)
        return recurrent_out[:, -1, :] if self.temp_attn is None else self.temp_attn(recurrent_out)

    def forward(self, x_seq, comp, return_context=False):
        context = self.encode_context(x_seq)
        if self.capacity_variant == "C4_MINIMAL":
            context = comp
        weights = torch.softmax(self.weight_net(context), dim=-1)
        if self.fusion_mode == "paper":
            # Eq. (28) operates on the original component predictions.  Only
            # the loss-space output is standardized after physical prediction.
            weighted_comp = weights * comp
            physical_prediction = self.predict_head(weighted_comp)
            prediction_z = (physical_prediction - self.y_mean) / self.y_std
        else:
            comp_z = (comp - self.comp_mean) / self.comp_std
            base = ((weights * comp).sum(dim=1, keepdim=True)
                    if self.capacity_variant == "C4_MINIMAL" else comp.sum(dim=1, keepdim=True))
            residual_input = context if self.capacity_variant in {"C3_NONRECURRENT", "C4_MINIMAL"} else torch.cat([context, weights * comp_z], dim=1)
            correction = self.residual_bound_pp * torch.tanh(
                self.residual_head(residual_input)
            )
            physical_prediction = base + correction
            prediction_z = (physical_prediction - self.y_mean) / self.y_std
        if return_context:
            return prediction_z, weights, context
        return prediction_z, weights


def weight_regularization(weights):
    """Reproduction-defined completion of the unpublished ``L_weight``.

    Let ``w_bar`` be the batch-average component allocation and
    ``u=(1/3,1/3,1/3)``.  We use ``KL(w_bar || u)``.  It is zero when the
    *batch as a whole* uses all three STL branches evenly, while individual
    samples may still specialize.  This is ``REPRO_DEFINED`` and must never
    be cited as the paper's original formula.
    """
    if weights.ndim != 2 or weights.shape[1] != 3:
        raise ValueError("weights 必须是 [batch, 3] 的概率矩阵")
    mean_weight = weights.mean(dim=0)
    safe = mean_weight.clamp_min(torch.finfo(weights.dtype).eps)
    return torch.sum(safe * torch.log(safe * weights.shape[1]))


def weight_diagnostics(weights):
    """Return interpretable diagnostics for the reproduction-defined prior."""
    values = torch.as_tensor(weights, dtype=torch.float32)
    mean_weight = values.mean(dim=0)
    entropy = -(values.clamp_min(1e-8) * values.clamp_min(1e-8).log()).sum(dim=1).mean()
    temporal_variation = (
        torch.abs(values[1:] - values[:-1]).mean()
        if len(values) > 1 else torch.tensor(0.0)
    )
    return {
        "WeightBalanceKL": float(weight_regularization(values)),
        "WeightEntropy": float(entropy),
        "WeightTemporalVariation": float(temporal_variation),
        "WeightMin": float(values.min()),
        "WeightMax": float(values.max()),
        "MeanWeightTrend": float(mean_weight[0]),
        "MeanWeightSeasonal": float(mean_weight[1]),
        "MeanWeightResidual": float(mean_weight[2]),
    }


def train_model(model, train_loader, val_loader, save_path, epochs=EPOCHS, patience=PATIENCE):
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=20, min_lr=1e-6
    )
    criterion = nn.MSELoss()

    best_val = float("inf")
    best_epoch = 0
    wait = 0
    history = []

    for epoch in range(1, epochs + 1):
        model.train()
        train_total = 0.0
        gradient_norms = []

        for x_seq, comp_z, y_z in train_loader:
            x_seq = x_seq.to(device)
            comp_z = comp_z.to(device)
            y_z = y_z.to(device)
            pred_z, weights = model(x_seq, comp_z)
            pred_loss = criterion(pred_z, y_z)
            loss = pred_loss + LAMBDA_WEIGHT * weight_regularization(weights)

            optimizer.zero_grad()
            loss.backward()
            gradient_norm = nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            gradient_norms.append(float(gradient_norm))
            optimizer.step()
            train_total += loss.item()

        model.eval()
        val_total = 0.0
        with torch.no_grad():
            for x_seq, comp_z, y_z in val_loader:
                x_seq = x_seq.to(device)
                comp_z = comp_z.to(device)
                y_z = y_z.to(device)
                pred_z, weights = model(x_seq, comp_z)
                pred_loss = criterion(pred_z, y_z)
                loss = pred_loss + LAMBDA_WEIGHT * weight_regularization(weights)
                val_total += loss.item()

        avg_train = train_total / max(len(train_loader), 1)
        avg_val = val_total / max(len(val_loader), 1)
        scheduler.step(avg_val)
        history.append({
            "epoch": epoch, "train_loss": avg_train, "val_loss": avg_val,
            "learning_rate": optimizer.param_groups[0]["lr"],
            "gradient_norm": float(np.mean(gradient_norms)) if gradient_norms else 0.0,
            "gradient_norm_max": float(np.max(gradient_norms)) if gradient_norms else 0.0,
        })

        if epoch == 1 or epoch % 25 == 0:
            print(
                f"Epoch {epoch:04d} | train={avg_train:.6f} | "
                f"val={avg_val:.6f} | lr={optimizer.param_groups[0]['lr']:.2e}"
            )

        if avg_val < best_val - 1e-6:
            best_val = avg_val
            best_epoch = epoch
            wait = 0
            torch.save(model.state_dict(), save_path)
        else:
            wait += 1
            if wait >= patience:
                print(f"Early stopping at epoch {epoch}")
                break

    model.load_state_dict(torch.load(save_path, map_location=device))
    print(f"[融合模型] 最优验证损失（标准化空间）：{best_val:.6f}")
    return model, pd.DataFrame(history), best_epoch


def prepare_split(df, comp_mean, comp_std, feat_mean, feat_std, y_mean, y_std):
    features = build_causal_features(df, comp_mean, comp_std)
    features = (features - feat_mean) / feat_std

    comp = df[["Pred_Trend", "Pred_Seasonal", "Pred_Residual"]].to_numpy(dtype=np.float32)

    y = true_soh_target(df)
    y_z = (y - y_mean) / y_std
    return sliding_windows(features, comp, y_z, SEQ_LEN), y


def run_fusion(input_dir=OUTPUT_PATH, output_dir=OUTPUT_PATH, model_path=None, seed=SEED,
               epochs=EPOCHS, patience=PATIENCE, fusion_mode="paper", evaluate_test=True,
               stable_init=False, residual_epsilon=None, experiment_track=None,
               capacity_variant="C0_FULL_BILSTM"):
    set_seed(seed)
    os.makedirs(output_dir, exist_ok=True)
    track = experiment_track or ("PAPER_FUSION" if fusion_mode == "paper" else "ENHANCEMENT")
    if track == "PAPER_FUSION":
        if fusion_mode != "paper" or stable_init or residual_epsilon is not None:
            raise ValueError("PAPER_FUSION 禁止 residual/stable_init 等 enhancement")
        if LAMBDA_WEIGHT != 0.0:
            raise ValueError("PAPER_FUSION 必须关闭未公开定义的 L_weight")
    elif track == "ENHANCEMENT" and fusion_mode != "residual":
        raise ValueError("Phase 1 ENHANCEMENT 只允许 residual fusion")

    print("=" * 64)
    print("步骤4：修正版双注意力 Bi-LSTM 融合模型")
    print("=" * 64)
    print(f"device = {device}")

    train_df = pd.read_csv(os.path.join(input_dir, "comp_pred_train.csv"))
    val_df = pd.read_csv(os.path.join(input_dir, "comp_pred_val.csv"))
    test_df = None
    if evaluate_test:
        test_df = pd.read_csv(os.path.join(input_dir, "comp_pred_test.csv"))

    validate_component_df(train_df, "train")
    validate_component_df(val_df, "val")
    if evaluate_test:
        validate_component_df(test_df, "test")

    train_comp = train_df[["Pred_Trend", "Pred_Seasonal", "Pred_Residual"]].to_numpy(dtype=np.float32)
    comp_mean, comp_std = zscore_fit(train_comp, axis=0)

    train_feat_raw = build_causal_features(train_df, comp_mean, comp_std)
    feat_mean, feat_std = zscore_fit(train_feat_raw, axis=0)

    train_y_raw = true_soh_target(train_df)
    y_mean = float(train_y_raw.mean())
    y_std = float(train_y_raw.std())
    if y_std < 1e-8:
        y_std = 1.0

    (X_train, C_train, y_train_z), _ = prepare_split(
        train_df, comp_mean, comp_std, feat_mean, feat_std, y_mean, y_std
    )
    (X_val, C_val, y_val_z), _ = prepare_split(
        val_df, comp_mean, comp_std, feat_mean, feat_std, y_mean, y_std
    )
    test_arrays = None
    if evaluate_test:
        test_arrays, _ = prepare_split(
            test_df, comp_mean, comp_std, feat_mean, feat_std, y_mean, y_std
        )

    count_text = f"训练样本={len(X_train)}, 验证样本={len(X_val)}"
    if evaluate_test:
        count_text += f", 测试样本={len(test_arrays[0])}"
    print(count_text)
    print(f"训练目标均值={y_mean:.4f}, 标准差={y_std:.4f}")

    train_loader = DataLoader(
        FusionDataset(X_train, C_train, y_train_z),
        batch_size=min(BATCH_SIZE, len(X_train)),
        shuffle=True,
        drop_last=False,
    )
    val_loader = DataLoader(
        FusionDataset(X_val, C_val, y_val_z),
        batch_size=min(BATCH_SIZE, len(X_val)),
        shuffle=False,
        drop_last=False,
    )
    model = AttentionBiLSTMFusion(
        comp_mean, comp_std, y_mean, y_std, fusion_mode=fusion_mode,
        stable_init=stable_init, residual_epsilon=residual_epsilon,
        capacity_variant=capacity_variant,
    ).to(device)
    save_path = model_path or os.path.join(MODEL_SAVE, "fusion_att_bilstm_paper.pth")
    model, history, best_epoch = train_model(model, train_loader, val_loader, save_path, epochs, patience)
    history.to_csv(os.path.join(output_dir, "training_history.csv"), index=False, encoding="utf-8-sig")

    def infer_split(split_name, source_df, arrays):
        x_seq, comp, target_z = arrays
        loader = DataLoader(
            FusionDataset(x_seq, comp, target_z),
            batch_size=min(BATCH_SIZE, len(x_seq)), shuffle=False,
        )
        pred_z_all, weight_all = [], []
        model.eval()
        with torch.no_grad():
            for xb, cb, _ in loader:
                pred_z, split_weights = model(xb.to(device), cb.to(device))
                pred_z_all.append(pred_z.cpu().numpy().reshape(-1))
                weight_all.append(split_weights.cpu().numpy())
        pred = np.concatenate(pred_z_all) * y_std + y_mean
        split_weights = np.concatenate(weight_all)
        true = true_soh_target(source_df)[SEQ_LEN:]
        meta = source_df.iloc[SEQ_LEN:].reset_index(drop=True)
        component_values = comp
        base = (
            (split_weights * component_values).sum(axis=1)
            if model.capacity_variant == "C4_MINIMAL" else component_values.sum(axis=1)
        )
        delta = pred - base
        result = pd.DataFrame({
            "Cycle": meta["Cycle"].to_numpy(dtype=int),
            "HF1": meta["HF1"].to_numpy(dtype=float),
            "HF2": meta["HF2"].to_numpy(dtype=float),
            "HF3": meta["HF3"].to_numpy(dtype=float),
            "True_SOH": true,
            "Pred_Trend": component_values[:, 0],
            "Pred_Seasonal": component_values[:, 1],
            "Pred_Residual": component_values[:, 2],
            "Base_SOH": base,
            "Delta_SOH": delta,
            "Pred_SOH": pred,
            "w_Trend": split_weights[:, 0],
            "w_Seasonal": split_weights[:, 1],
            "w_Residual": split_weights[:, 2],
        })
        result.to_csv(
            os.path.join(output_dir, f"gmtc_pred_{split_name}.csv"),
            index=False, encoding="utf-8-sig",
        )
        return result, split_weights

    infer_split("train", train_df, (X_train, C_train, y_train_z))
    val_out, val_weights = infer_split("val", val_df, (X_val, C_val, y_val_z))
    if evaluate_test:
        out_df, weights = infer_split("test", test_df, test_arrays)
        evaluated_split = "test"
    else:
        out_df, weights = val_out, val_weights
        evaluated_split = "validation"
    y_test = out_df["True_SOH"].to_numpy()
    y_pred = out_df["Pred_SOH"].to_numpy()

    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mape = np.sum(np.abs(y_test - y_pred)) / np.sum(np.abs(y_test)) * 100
    r2 = r2_score(y_test, y_pred)

    print("\n" + "=" * 64)
    print(f"G-MTC 修正版{evaluated_split}指标")
    print("=" * 64)
    print(f"MAE   : {mae:.4f} percentage points")
    print(f"MAPE  : {mape:.4f}%")
    print(f"RMSE  : {rmse:.4f} percentage points")
    print(f"R2    : {r2:.4f}")
    print(
        "平均权重："
        f"Trend={weights[:, 0].mean():.3f}, "
        f"Seasonal={weights[:, 1].mean():.3f}, "
        f"Residual={weights[:, 2].mean():.3f}"
    )
    print("=" * 64)

    result_name = "gmtc_pred_result.csv" if evaluate_test else "gmtc_pred_validation_result.csv"
    out_path = os.path.join(output_dir, result_name)
    out_df.to_csv(out_path, index=False, encoding="utf-8-sig")
    catastrophic = (y_pred < CATASTROPHIC_MIN) | (y_pred > CATASTROPHIC_MAX)
    residual_bound = None if residual_epsilon is None else 100.0 * residual_epsilon
    bound_violation = (
        int(np.sum(np.abs(out_df["Delta_SOH"].to_numpy()) > residual_bound + RESIDUAL_BOUND_NUMERICAL_TOLERANCE))
        if residual_bound is not None else 0
    )
    diagnostics = {
        "PredictionMin": float(np.min(y_pred)), "PredictionMax": float(np.max(y_pred)),
        "PredictionMean": float(np.mean(y_pred)), "PredictionStd": float(np.std(y_pred)),
        "CatastrophicPredictionCount": int(np.sum(catastrophic)),
        "CatastrophicPredictionRate": float(np.mean(catastrophic)),
        "CatastrophicLowerBound": CATASTROPHIC_MIN,
        "CatastrophicUpperBound": CATASTROPHIC_MAX,
        "GradientNormMean": float(history["gradient_norm"].mean()),
        "GradientNormMax": float(history["gradient_norm_max"].max()),
        "BestTrainLoss": float(history["train_loss"].min()),
        "BestValidationLoss": float(history["val_loss"].min()),
        "BestEpoch": int(best_epoch),
        "EpochsCompleted": int(len(history)),
        "ParameterCount": int(sum(parameter.numel() for parameter in model.parameters())),
        "MeanAbsDelta": float(np.mean(np.abs(out_df["Delta_SOH"]))) if fusion_mode == "residual" else float("nan"),
        "MaxAbsDelta": float(np.max(np.abs(out_df["Delta_SOH"]))) if fusion_mode == "residual" else float("nan"),
        "ResidualEpsilon": residual_epsilon,
        "ResidualBoundPercentagePoints": residual_bound,
        "ResidualBoundViolationCount": bound_violation,
        "FusionSeqLen": int(SEQ_LEN),
    }
    metrics = {"ExperimentTrack": track, "EvaluatedSplit": evaluated_split, "FusionMode": fusion_mode,
               "CapacityVariant": capacity_variant,
               "MAE": mae, "MAPE": mape, "RMSE": rmse, "R2": r2,
               "LWeightStatus": L_WEIGHT_DISABLED_STATUS if LAMBDA_WEIGHT == 0 else L_WEIGHT_STATUS,
               "LWeightFormula": L_WEIGHT_FORMULA,
               "LWeightLambda": LAMBDA_WEIGHT,
               **diagnostics, **weight_diagnostics(weights)}
    metrics_name = "fusion_metrics.csv" if evaluate_test else "fusion_validation_metrics.csv"
    pd.DataFrame([metrics]).to_csv(os.path.join(output_dir, metrics_name), index=False)
    pd.DataFrame([diagnostics]).to_csv(
        os.path.join(output_dir, "diagnostic_summary.csv"), index=False, encoding="utf-8-sig"
    )
    print(f"结果已保存：{out_path}")
    return metrics, out_df


def main():
    input_dir = os.getenv("COMPONENT_INPUT_DIR", OUTPUT_PATH)
    output_dir = os.getenv("FUSION_OUTPUT_DIR", OUTPUT_PATH)
    model_path = os.getenv("FUSION_MODEL_PATH")
    seed = int(os.getenv("FUSION_SEED", str(SEED)))
    epochs = int(os.getenv("FUSION_EPOCHS", str(EPOCHS)))
    patience = int(os.getenv("FUSION_PATIENCE", str(PATIENCE)))
    fusion_mode = os.getenv("FUSION_MODE", "paper").strip().lower()
    run_fusion(input_dir, output_dir, model_path, seed, epochs, patience, fusion_mode)


if __name__ == "__main__":
    main()
