"""Phase 8: fixed Ridge source-transfer and HF-shift attribution audit."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, wasserstein_distance, pearsonr
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'output'/'phase8_source_transfer_audit_v1'
TARGETS=('B0007','B0018'); SOURCES=('B0005','B0006'); HF=('HF1','HF2','HF3'); W=10; ALPHA=1.0

def boundary(b):
 p=ROOT/'output'/'phase1_failure_isolation_v1'/'PAPER_FUSION'/'seed_42'/b/'none'/'run_manifest.json'
 m=json.loads(p.read_text(encoding='utf8'))['engine_manifest']; return int(m['TrainEnd']),int(m['ValidationEnd'])
def frame(b,nrows=None):
 kwargs={} if nrows is None else {'nrows':nrows}
 return pd.read_csv(ROOT/'data'/'hf_csv'/f'{b}_hf.csv',**kwargs)[list(HF)+['SOH']].apply(pd.to_numeric,errors='coerce').dropna().reset_index(drop=True)
def features(x,indices): return np.asarray([x[i-W+1:i+1].reshape(-1) for i in indices],np.float32)
def metrics(y,p):
 return {'RMSE':float(mean_squared_error(y,p)**.5),'MAE':float(mean_absolute_error(y,p)),'R2':float(r2_score(y,p)),'PredictionStd':float(np.std(p)),'TrueStd':float(np.std(y)),'Correlation':float(pearsonr(y,p).statistic) if np.std(y)*np.std(p)>1e-12 else np.nan}
def train_windows(data,limit=None):
 h=data[list(HF)].to_numpy(np.float32); y=data.SOH.to_numpy(np.float32)*100; end=len(data) if limit is None else limit
 return h, y, np.arange(W,end)
def support(train,val):
 return float(np.mean((val>=train.min())&(val<=train.max())))

def protocol_rows(target,source_frames):
 te,ve=boundary(target); raw=frame(target,nrows=ve)
 if len(raw)!=ve:raise RuntimeError(f'{target}: target prefix changed after cleaning')
 fit=max(W+3,int(te*.8)); th,ty,ti=train_windows(raw,fit); vh,vy,_=train_windows(raw); vi=np.arange(te,ve); vy_val=vy[vi]
 source_y=np.concatenate([data.SOH.to_numpy(np.float32)[W:]*100 for data in source_frames.values()])
 source_y_for_scaler=np.concatenate([data.SOH.to_numpy(np.float32)*100 for data in source_frames.values()])
 target_y=ty[ti]
 protocols={
  'P0_TARGET_ONLY':('TARGET_FIT_PREFIX_ONLY',True,'TARGET_ONLY'),
  'P1_SOURCE_ONLY_ZERO_SHOT':('B0005+B0006_FULL_REAL_ONLY',False,'SOURCE_TRANSFER/ZERO_SHOT_DIAGNOSTIC'),
  'P2_SOURCE_PLUS_TARGET_CALIBRATED':('B0005+B0006_FULL_REAL_PLUS_TARGET_FIT_PREFIX',True,'CALIBRATED_TRANSFER'),
 }
 rows=[]
 for name,(composition,target_labels,track) in protocols.items():
  # Phase-6-compatible column scaler: fit HF1/HF2/HF3 only, then form windows.
  scaler_rows=th[:fit] if name=='P0_TARGET_ONLY' else np.concatenate([*(d[list(HF)].to_numpy(np.float32) for d in source_frames.values()), *( [th[:fit]] if name=='P2_SOURCE_PLUS_TARGET_CALIBRATED' else [])])
  mu,sd=scaler_rows.mean(0),scaler_rows.std(0); sd[sd<1e-8]=1
  source_x=np.concatenate([features((data[list(HF)].to_numpy(np.float32)-mu)/sd,np.arange(W,len(data))) for data in source_frames.values()])
  target_x=features((th-mu)/sd,ti); val_x=features((vh-mu)/sd,vi)
  if name=='P0_TARGET_ONLY': x,y,y_scale=target_x,target_y,ty[:fit]
  elif name=='P1_SOURCE_ONLY_ZERO_SHOT': x,y,y_scale=source_x,source_y,source_y_for_scaler
  else: x,y,y_scale=np.concatenate([source_x,target_x]),np.concatenate([source_y,target_y]),np.concatenate([source_y_for_scaler,ty[:fit]])
  y_mu,y_sd=y_scale.mean(),max(y_scale.std(),1e-8)
  model=Ridge(alpha=ALPHA).fit(x,(y-y_mu)/y_sd); pred=model.predict(val_x)*y_sd+y_mu
  rows.append({'Battery':target,'Protocol':name,'Track':track,'RidgeAlpha':ALPHA,'ParameterCount':int(model.coef_.size+1),'TrainingSamples':len(y),'SourceTrainingSamples':len(source_y) if name!='P0_TARGET_ONLY' else 0,'TargetTrainingSamples':len(target_y) if name!='P1_SOURCE_ONLY_ZERO_SHOT' else 0,'TrainingComposition':composition,'ScalerFitScope':composition,'UsesTargetSOHLabelsForTraining':target_labels,'TargetTrainEnd':te,'TargetFitEnd':fit,'ValidationEnd':ve,'TestLoaded':False,**metrics(vy_val,pred)})
 return rows,raw,te,ve,fit

def distributions(target,raw,te,ve,source_frames):
 tr=raw.iloc[:te]; va=raw.iloc[te:ve]; source=pd.concat(list(source_frames.values()),ignore_index=True); rows=[]; cov=[]
 for feature in HF:
  a,b,s=tr[feature].to_numpy(float),va[feature].to_numpy(float),source[feature].to_numpy(float); both=np.r_[a,s]
  rows.append({'Battery':target,'Feature':feature,'SourceRows':len(s),'TargetTrainRows':len(a),'TargetValidationRows':len(b),'SourceMean':float(s.mean()),'SourceStd':float(s.std()),'TargetTrainMean':float(a.mean()),'TargetTrainStd':float(a.std()),'TargetValidationMean':float(b.mean()),'TargetValidationStd':float(b.std()),'KS_SourceVsTargetValidation':float(ks_2samp(s,b).statistic),'Wasserstein_SourceVsTargetValidation':float(wasserstein_distance(s,b)),'StandardizedWassersteinByTargetTrain':float(wasserstein_distance(s,b)/max(a.std(),1e-8)),'TestLoaded':False})
  target_cover=support(a,b); source_cover=support(s,b); both_cover=support(both,b)
  cov.append({'Battery':target,'Feature':feature,'TargetOnlyValidationSupportCoverage':target_cover,'SourceOnlyValidationSupportCoverage':source_cover,'SourcePlusTargetValidationSupportCoverage':both_cover,'SourceCoverageGainOverTargetOnly':source_cover-target_cover,'TargetTrainMin':float(a.min()),'TargetTrainMax':float(a.max()),'SourceMin':float(s.min()),'SourceMax':float(s.max()),'ValidationMin':float(b.min()),'ValidationMax':float(b.max()),'TestLoaded':False})
 return rows,cov

def decide(m,cov):
 tab=m.pivot(index='Battery',columns='Protocol',values=['RMSE','R2'])
 p0=tab['RMSE']['P0_TARGET_ONLY']; p1=tab['RMSE']['P1_SOURCE_ONLY_ZERO_SHOT']; p2=tab['RMSE']['P2_SOURCE_PLUS_TARGET_CALIBRATED']
 r0=tab['R2']['P0_TARGET_ONLY'];r2=tab['R2']['P2_SOURCE_PLUS_TARGET_CALIBRATED']
 # Predeclared: require at least 1% RMSE reduction plus R2 increase to call a transfer benefit.
 improve={b:(p2[b]<=.99*p0[b] and r2[b]>r0[b]) for b in TARGETS}
 if all(improve.values()): main='SOURCE_DATA_MITIGATES_TARGET_SHIFT'
 elif all(p2[b]>=p0[b] for b in TARGETS): main='NEGATIVE_TRANSFER_DETECTED'
 elif not any(improve.values()): main='SOURCE_TRANSFER_NOT_SUFFICIENT'
 else: main='BATTERY_SPECIFIC_DOMAIN_SHIFT_REMAINS'
 b7gain=cov[cov.Battery=='B0007'].SourceCoverageGainOverTargetOnly.mean()>0
 b7fail=not improve['B0007']
 return main, ('CONDITIONAL_RELATIONSHIP_SHIFT_REMAINS' if b7gain and b7fail else 'NOT_ESTABLISHED')

def main():
 OUT.mkdir(parents=True,exist_ok=True); source={b:frame(b) for b in SOURCES}; metrics_rows=[];dist=[];cov=[];manifest=[]
 for target in TARGETS:
  print(f'[Phase8] {target}: P0/P1/P2 fixed Ridge',flush=True); rows,raw,te,ve,fit=protocol_rows(target,source);metrics_rows+=rows;d,c=distributions(target,raw,te,ve,source);dist+=d;cov+=c;manifest.append({'Battery':target,'TrainEnd':te,'FitEnd':fit,'ValidationEnd':ve,'SourceBatteries':','.join(SOURCES),'TestLoaded':False})
 m,pdists,coverage=map(pd.DataFrame,(metrics_rows,dist,cov)); verdict,b7=decide(m,coverage)
 m.to_csv(OUT/'transfer_protocol_metrics.csv',index=False,encoding='utf-8-sig');pdists.to_csv(OUT/'source_target_distribution.csv',index=False,encoding='utf-8-sig');coverage.to_csv(OUT/'support_coverage_analysis.csv',index=False,encoding='utf-8-sig')
 lines=['# Phase 8 — Source Transfer & HF Shift Attribution','',f'Decision: {verdict}',f'B0007 attribution: {b7}','','## Protocol','P0 TARGET_ONLY uses the target fit prefix. P1 is SOURCE_TRANSFER/ZERO_SHOT diagnostic and does not train on target SOH labels. P2 is CALIBRATED_TRANSFER and uses source real data plus target fit-prefix labels.','Source B0005/B0006 use full real labelled lifecycle data; target CSVs are read with nrows=ValidationEnd only.','Ridge alpha=1.0 is fixed from Phase 6; no validation tuning or test access.','','## Metrics',m[['Battery','Protocol','Track','TrainingSamples','SourceTrainingSamples','TargetTrainingSamples','UsesTargetSOHLabelsForTraining','RMSE','MAE','R2','PredictionStd','TestLoaded']].to_csv(index=False),'','## HF support coverage',coverage.groupby('Battery').agg(MeanTargetOnlyCoverage=('TargetOnlyValidationSupportCoverage','mean'),MeanSourceOnlyCoverage=('SourceOnlyValidationSupportCoverage','mean'),MeanCoverageGain=('SourceCoverageGainOverTargetOnly','mean')).reset_index().to_csv(index=False),'','## Evidence boundary','A source coverage gain is univariate feature-wise support evidence, not proof that source and target share the same conditional HF-to-SOH relationship. P1/P2 are diagnostics, not claims of a final deployed model.']
 (OUT/'PHASE8_REPORT.md').write_text('\n'.join(lines),encoding='utf8'); print(verdict);print(b7)
if __name__=='__main__':main()
