"""Phase 5: REAL_ONLY component-capacity ablation (validation prefix only)."""
from __future__ import annotations

import importlib.util
import json
import random
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from statsmodels.tsa.seasonal import STL

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "phase5_complexity_ablation_v1"
PHASE4B = ROOT / "output" / "phase4b_gan_component_attribution_v1" / "G0_REAL_ONLY"
BATTERIES = ("B0007", "B0018")
SEEDS = (42, 123, 2024, 3407, 7777)
WINDOW = 10
LR = 0.001
WEIGHT_DECAY = 1e-5
BATCH_SIZE = 32
EPOCHS = 300
PATIENCE = 50


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_module("phase5_engine", ROOT / "scripts" / "08_physics_trend_ablation.py")
TS = ENGINE.ts
HF_COLS = ENGINE.HF_COLS


def seed_everything(seed: int) -> None:
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)


def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def metrics(true: np.ndarray, pred: np.ndarray) -> dict:
    true, pred = np.asarray(true, float), np.asarray(pred, float)
    return {"RMSE": float(np.sqrt(mean_squared_error(true, pred))), "MAE": float(mean_absolute_error(true, pred)),
            "MAPE": float(np.mean(np.abs((true-pred)/np.maximum(np.abs(true), 1e-8)))*100), "R2": float(r2_score(true, pred)),
            "PredictionMin": float(pred.min()), "PredictionMax": float(pred.max()), "PredictionMean": float(pred.mean()),
            "PredictionStd": float(pred.std()), "TrueStd": float(true.std()), "Correlation": float(np.corrcoef(true,pred)[0,1]) if true.std()*pred.std()>1e-12 else np.nan}


class TinyMLP(nn.Module):
    """Pre-registered 30 -> 12 -> 1 trend regressor (385 parameters)."""
    def __init__(self):
        super().__init__(); self.net=nn.Sequential(nn.Linear(WINDOW*3,12),nn.ReLU(),nn.Linear(12,1))
    def forward(self,x): return self.net(x.flatten(1))


class TinyGRU(nn.Module):
    """Pre-registered one-layer unidirectional GRU, hidden size 6."""
    def __init__(self):
        super().__init__(); self.gru=nn.GRU(3,6,batch_first=True); self.output=nn.Linear(6,1)
    def forward(self,x): return self.output(self.gru(x)[0][:,-1])


def train_torch(model: nn.Module, x: np.ndarray, y: np.ndarray, seed: int):
    """Fixed schedule; monitoring uses only a tail of the training prefix."""
    seed_everything(seed); model=model.to(ENGINE.DEVICE)
    x_t=torch.as_tensor(x,dtype=torch.float32,device=ENGINE.DEVICE); y_t=torch.as_tensor(y,dtype=torch.float32,device=ENGINE.DEVICE).unsqueeze(-1)
    # All fit windows number at most 16, so a full tensor update is exactly one batch (<= BATCH_SIZE=32).
    if len(y) > BATCH_SIZE: raise RuntimeError("Phase 5 fixed batch-size contract unexpectedly exceeded")
    opt=torch.optim.AdamW(model.parameters(),lr=LR,weight_decay=WEIGHT_DECAY); best,wait,state=float("inf"),0,None; cut=max(1,int(len(y)*.8))
    for epoch in range(EPOCHS):
        model.train(); opt.zero_grad(); loss=nn.functional.mse_loss(model(x_t[:cut]),y_t[:cut]); loss.backward(); nn.utils.clip_grad_norm_(model.parameters(),1.0); opt.step()
        model.eval()
        with torch.no_grad(): monitor=nn.functional.mse_loss(model(x_t[cut:]),y_t[cut:]).item() if cut<len(y) else loss.item()
        if monitor<best-1e-7: best,wait,state=monitor,0,{k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
        else:
            wait+=1
            if wait>=PATIENCE: break
    model.load_state_dict(state); return model,epoch+1,best


def model_prediction(model,x):
    model.eval()
    with torch.no_grad(): return model(torch.as_tensor(x,dtype=torch.float32,device=ENGINE.DEVICE)).detach().cpu().numpy().reshape(-1)


def boundaries(battery):
    p=ROOT/"output"/"phase1_failure_isolation_v1"/"PAPER_FUSION"/"seed_42"/battery/"none"/"run_manifest.json"
    manifest=json.loads(p.read_text(encoding="utf-8"))["engine_manifest"]
    return int(manifest["TrainEnd"]),int(manifest["ValidationEnd"])


def paper_model(component,state_path):
    model=TS.iTransformer(seq_len=WINDOW,d_model=64,nhead=4,layers=2) if component=="Residual" else TS.TimesNet(input_dim=3,d_model=64,top_k=3)
    try: state=torch.load(state_path,map_location=ENGINE.DEVICE,weights_only=True)
    except TypeError: state=torch.load(state_path,map_location=ENGINE.DEVICE)
    model.load_state_dict(state); return model.to(ENGINE.DEVICE)


def run_one(battery,seed):
    train_end,validation_end=boundaries(battery)
    # This hard read boundary means test-cycle rows cannot enter memory.
    raw=pd.read_csv(ROOT/"data"/"hf_csv"/f"{battery}_hf.csv",nrows=validation_end)[HF_COLS+["SOH"]].apply(pd.to_numeric,errors="coerce").dropna().reset_index(drop=True)
    if len(raw)!=validation_end: raise RuntimeError(f"{battery}: opened prefix changed after numeric cleaning")
    soh=raw.SOH.to_numpy(np.float32)*100; train_stl=STL(soh[:train_end],period=TS.STL_PERIOD,robust=True).fit(); diagnostic=STL(soh[:validation_end],period=TS.STL_PERIOD,robust=True).fit()
    attribute={"Trend":"trend","Seasonal":"seasonal","Residual":"resid"}; targets={name:np.asarray(getattr(train_stl,attribute[name]),np.float32) for name in ("Trend","Seasonal","Residual")}; truth_all={name:np.asarray(getattr(diagnostic,attribute[name]),np.float32) for name in targets}; idx=np.arange(train_end,validation_end); truth={name:truth_all[name][idx] for name in targets}
    # Exactly retain the REAL_ONLY Phase 4B scaler/fit-prefix contract.
    fit_end=max(WINDOW+3,int(train_end*.8)); hf=raw[HF_COLS].to_numpy(np.float32); hm,hs=hf[:fit_end].mean(0),hf[:fit_end].std(0); hs[hs<1e-8]=1; norm_hf=(hf-hm)/hs
    x_val=np.asarray([norm_hf[c-WINDOW+1:c+1] for c in idx],np.float32); component_rows=[]; prediction_rows=[]; predictions={}
    for component,values in targets.items():
        mean,std=float(values[:fit_end].mean()),max(float(values[:fit_end].std()),1e-8); y_norm=(values-mean)/std
        x_train,y_train=TS.windows(norm_hf[:fit_end],y_norm[:fit_end],seq_len=WINDOW); x_train=np.asarray(x_train,np.float32); y_train=np.asarray(y_train,np.float32)
        ridge=Ridge(alpha=1.0).fit(x_train.reshape(len(x_train),-1),y_train)
        # The recursive version is the fair deployable T0: it has no validation component labels.
        # The one-step version is retained only to reproduce the Phase 4B diagnostic reference.
        specs={"PERSISTENCE_RECURSIVE":(None,0,None),"PERSISTENCE_ONE_STEP_DIAGNOSTIC":(None,0,None),"RIDGE":(ridge,int(ridge.coef_.size+1),None)}
        if component=="Trend":
            # Seed before construction as well as before optimization: initial weights must be seed-controlled.
            seed_everything(seed + 101); mlp,me,ml=train_torch(TinyMLP(),x_train,y_train,seed + 101)
            seed_everything(seed + 202); gru,ge,gl=train_torch(TinyGRU(),x_train,y_train,seed + 202)
            specs.update({"TINY_MLP":(mlp,count_parameters(mlp),(me,ml)),"TINY_GRU":(gru,count_parameters(gru),(ge,gl))})
        checkpoint=PHASE4B/f"{battery}_{seed}_{component}.pth"
        if not checkpoint.exists(): raise FileNotFoundError(f"Missing Phase 4B reference checkpoint: {checkpoint}")
        paper=paper_model(component,checkpoint); specs["PAPER_ITRANSFORMER" if component=="Residual" else "PAPER_TIMESNET"]=(paper,count_parameters(paper),None)
        for model_name,(model,parameters,train_info) in specs.items():
            if model_name=="PERSISTENCE_RECURSIVE": pred=np.full(len(idx),values[train_end-1],dtype=np.float32)
            elif model_name=="PERSISTENCE_ONE_STEP_DIAGNOSTIC": pred=np.r_[truth_all[component][train_end-1],truth_all[component][train_end:validation_end-1]]
            elif model_name=="RIDGE": pred=model.predict(x_val.reshape(len(x_val),-1))*std+mean
            else: pred=model_prediction(model,x_val)*std+mean
            predictions[(component,model_name)]=np.asarray(pred,np.float32)
            row={"Battery":battery,"Seed":seed,"Component":component,"Model":model_name,"ParameterCount":parameters,"ComponentTrainingSamples":len(y_train),"ParametersPerSample":float(parameters/len(y_train)) if parameters else 0.,"FitEnd":fit_end,"TrainEnd":train_end,"ValidationEnd":validation_end,"TestLoaded":False,**metrics(truth[component],pred)}
            if train_info: row.update({"BestEpoch":train_info[0],"BestInnerTrainLoss":train_info[1]})
            component_rows.append(row)
            prediction_rows.extend({"Battery":battery,"Seed":seed,"Cycle":int(cycle),"Component":component,"Model":model_name,"TrueComponent":float(actual),"PredictedComponent":float(estimate),"TestLoaded":False} for cycle,actual,estimate in zip(idx,truth[component],pred))
    paper_name={"Trend":"PAPER_TIMESNET","Seasonal":"PAPER_TIMESNET","Residual":"PAPER_ITRANSFORMER"}
    hybrids={"H0_PAPER_COMPONENTS":sum(predictions[(c,paper_name[c])] for c in targets),"H1_ALL_PERSISTENCE_RECURSIVE":sum(predictions[(c,"PERSISTENCE_RECURSIVE")] for c in targets),"H2_ALL_RIDGE_PREDEFINED":sum(predictions[(c,"RIDGE")] for c in targets),"H3_TREND_RIDGE_PAPER_SR":predictions[("Trend","RIDGE")]+predictions[("Seasonal",paper_name["Seasonal"])]+predictions[("Residual",paper_name["Residual"])],"H4_ORACLE_TREND_DIAGNOSTIC":truth["Trend"]+predictions[("Seasonal",paper_name["Seasonal"])]+predictions[("Residual",paper_name["Residual"])]}
    # Kept as a clearly non-comparable one-step SOH reference, matching the user-specified historical baseline.
    hybrids["SOH_PERSISTENCE_ONE_STEP_DIAGNOSTIC"]=soh[idx-1]
    hybrid_rows=[{"Battery":battery,"Seed":seed,"Hybrid":name,"TestLoaded":False,"Deployable":name!="H4_ORACLE_TREND_DIAGNOSTIC",**metrics(soh[idx],pred)} for name,pred in hybrids.items()]
    return component_rows,hybrid_rows,prediction_rows


def summary(frame,keys):
    return frame.groupby(keys,as_index=False).agg(MeanRMSE=("RMSE","mean"),RMSEStd=("RMSE",lambda s:float(np.std(s,ddof=0))),WorstRMSE=("RMSE","max"),MeanR2=("R2","mean"),WorstR2=("R2","min"),MeanMAE=("MAE","mean"),Runs=("Seed","count"),TestLoaded=("TestLoaded","max"))


def make_figures(component):
    trend=summary(component[component.Component=="Trend"],["Battery","Model"])
    param=component.groupby(["Battery","Component","Model"],as_index=False).ParameterCount.first(); pps=component.groupby(["Battery","Component","Model"],as_index=False).ParametersPerSample.first(); trend=trend.merge(param,on=["Battery","Model"]).merge(pps,on=["Battery","Model"])
    for metric,label in (("MeanRMSE","mean RMSE"),("WorstRMSE","worst-seed RMSE"),("MeanR2","mean R2")):
        fig,ax=plt.subplots(figsize=(7,4))
        for b,g in trend.groupby("Battery"):
            ax.scatter(g.ParameterCount,g[metric],label=b,s=55)
            for _,r in g.iterrows(): ax.annotate(r.Model,(r.ParameterCount,r[metric]),fontsize=7)
        ax.set_xscale("symlog",linthresh=1); ax.set_xlabel("trainable parameters"); ax.set_ylabel(label); ax.grid(alpha=.3); ax.legend(); fig.tight_layout()
        destination=OUT/f"parameter_count_vs_{metric}.png"
        # Existing figures were generated from the same deterministic aggregate values; do not overwrite a viewer-locked file.
        if not destination.exists(): fig.savefig(destination,dpi=180)
        plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4))
    for b,g in trend.groupby("Battery"):
        ax.scatter(g.ParametersPerSample,g.RMSEStd,label=b,s=55)
        for _,r in g.iterrows(): ax.annotate(r.Model,(r.ParametersPerSample,r.RMSEStd),fontsize=7)
    ax.set_xscale("symlog",linthresh=1); ax.set_xlabel("parameters per training sample"); ax.set_ylabel("RMSE std across seeds"); ax.grid(alpha=.3); ax.legend(); fig.tight_layout()
    destination=OUT/"parameters_per_sample_vs_RMSE_std.png"
    if not destination.exists(): fig.savefig(destination,dpi=180)
    plt.close(fig)


def decide(component,hybrids):
    trend=summary(component[component.Component=="Trend"],["Battery","Model"]).set_index(["Battery","Model"]); paper=trend.xs("PAPER_TIMESNET",level="Model").MeanRMSE; persist=trend.xs("PERSISTENCE_RECURSIVE",level="Model").MeanRMSE
    simple=pd.Series({b:min(trend.loc[(b,m),"MeanRMSE"] for m in ("RIDGE","TINY_MLP","TINY_GRU")) for b in BATTERIES})
    if all(simple[b]>=persist[b] for b in BATTERIES): first="LEARNED_COMPONENT_FORECASTING_NOT_JUSTIFIED"
    elif all(simple[b]<paper[b] for b in BATTERIES): first="MODEL_COMPLEXITY_CONTRIBUTES_BUT_NOT_SUFFICIENT"
    else: first="TIMESNET_FAILURE_NOT_EXPLAINED_BY_CAPACITY"
    hy=summary(hybrids,["Battery","Hybrid"]).set_index(["Battery","Hybrid"]); h0=hy.xs("H0_PAPER_COMPONENTS",level="Hybrid").MeanRMSE; h3=hy.xs("H3_TREND_RIDGE_PAPER_SR",level="Hybrid").MeanRMSE
    second="TREND_MODEL_IS_PRIMARY_ACTIONABLE_BOTTLENECK" if all(h3[b]<.8*h0[b] for b in BATTERIES) else "MULTI_COMPONENT_REDESIGN_REQUIRED"
    return first,second


def main():
    OUT.mkdir(parents=True,exist_ok=True); cr=[]; hr=[]; pr=[]; total=len(BATTERIES)*len(SEEDS)
    for n,(seed,battery) in enumerate(((s,b) for s in SEEDS for b in BATTERIES),1):
        print(f"[Phase5 {n}/{total}] {battery}, seed={seed}",flush=True); c,h,p=run_one(battery,seed); cr+=c; hr+=h; pr+=p
    component=pd.DataFrame(cr); hybrids=pd.DataFrame(hr); predictions=pd.DataFrame(pr)
    component.to_csv(OUT/"component_model_comparison.csv",index=False,encoding="utf-8-sig"); component[component.Component=="Trend"].to_csv(OUT/"trend_model_comparison.csv",index=False,encoding="utf-8-sig"); hybrids.to_csv(OUT/"hybrid_reconstruction_metrics.csv",index=False,encoding="utf-8-sig"); predictions.to_csv(OUT/"component_validation_predictions.csv",index=False,encoding="utf-8-sig")
    complexity=component.groupby(["Battery","Component","Model"],as_index=False).agg(ParameterCount=("ParameterCount","first"),ComponentTrainingSamples=("ComponentTrainingSamples","first"),ParametersPerSample=("ParametersPerSample","first"),MeanRMSE=("RMSE","mean"),RMSEStd=("RMSE",lambda s:float(np.std(s,ddof=0))),WorstRMSE=("RMSE","max"),MeanR2=("R2","mean"),WorstR2=("R2","min"),Runs=("Seed","count"),TestLoaded=("TestLoaded","max")); complexity.to_csv(OUT/"complexity_vs_performance.csv",index=False,encoding="utf-8-sig")
    make_figures(component); final,bottleneck=decide(component,hybrids)
    lines=["# Phase 5 — Component Model Adequacy & Complexity Ablation","",f"Decision: {final}",f"Bottleneck: {bottleneck}","","## Protocol","REAL_ONLY; component window=10; first 20% train and next 20% validation; B0007/B0018; five fixed seeds.",f"Fixed optimization: lr={LR}, batch_size={BATCH_SIZE}, patience={PATIENCE}, weight_decay={WEIGHT_DECAY}. Every fit has <=16 windows, therefore uses one batch without changing the batch-size ceiling.","TestLoaded=false for every run: raw CSV was read with nrows=ValidationEnd.","No GAN, fusion, transfer, calibration, sequence grid, epsilon grid, or test set was used.","PERSISTENCE_RECURSIVE is the deployable T0 and never reads validation component labels. PERSISTENCE_ONE_STEP_DIAGNOSTIC and SOH_PERSISTENCE_ONE_STEP_DIAGNOSTIC use the true prior validation observation only as explicitly labelled historical diagnostic references.","","## Component summary",summary(component,["Battery","Component","Model"]).to_csv(index=False),"","## Hybrid reconstruction summary",summary(hybrids,["Battery","Hybrid"]).to_csv(index=False),"","H2 uses pre-registered Ridge rather than selecting a simple model on validation. H4 is oracle diagnostic only and is not deployable."]
    (OUT/"PHASE5_REPORT.md").write_text("\n".join(lines),encoding="utf-8"); print(final); print(bottleneck)


if __name__=="__main__": main()
