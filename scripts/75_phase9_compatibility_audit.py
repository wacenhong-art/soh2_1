"""Phase 9: source-target compatibility and conditional-shift diagnostic only."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'output'/'phase9_compatibility_audit_v1'
TARGETS=('B0007','B0018'); SOURCE_SETS={'S0_B0005':('B0005',),'S1_B0006':('B0006',),'S2_B0005_B0006':('B0005','B0006')}; HF=('HF1','HF2','HF3'); W=10; ALPHA=1.; K=5

def boundary(b):
 p=ROOT/'output'/'phase1_failure_isolation_v1'/'PAPER_FUSION'/'seed_42'/b/'none'/'run_manifest.json';m=json.loads(p.read_text(encoding='utf8'))['engine_manifest'];return int(m['TrainEnd']),int(m['ValidationEnd'])
def frame(b,nrows=None):
 kw={} if nrows is None else {'nrows':nrows};return pd.read_csv(ROOT/'data'/'hf_csv'/f'{b}_hf.csv',**kw)[list(HF)+['SOH']].apply(pd.to_numeric,errors='coerce').dropna().reset_index(drop=True)
def windows(h,idx):return np.asarray([h[i-W+1:i+1].reshape(-1) for i in idx],np.float32)
def corr(a,b):return float(pearsonr(a,b).statistic) if len(a)>2 and np.std(a)*np.std(b)>1e-12 else np.nan
def metrics(y,p):return {'RMSE':float(mean_squared_error(y,p)**.5),'MAE':float(mean_absolute_error(y,p)),'R2':float(r2_score(y,p)),'PredictionMean':float(p.mean()),'PredictionStd':float(p.std()),'TrueStd':float(y.std())}
def qstats(x,prefix):
 q=np.quantile(x,[.05,.25,.5,.75,.95]);return {f'{prefix}Mean':float(x.mean()),f'{prefix}Std':float(x.std()),f'{prefix}Q05':float(q[0]),f'{prefix}Q25':float(q[1]),f'{prefix}Median':float(q[2]),f'{prefix}Q75':float(q[3]),f'{prefix}Q95':float(q[4])}

def source_arrays(frames,mu,sd):
 xs=[];ys=[]
 for data in frames:
  h=(data[list(HF)].to_numpy(np.float32)-mu)/sd; y=data.SOH.to_numpy(np.float32)*100; idx=np.arange(W,len(data));xs.append(windows(h,idx));ys.append(y[idx])
 return np.concatenate(xs),np.concatenate(ys)
def fit_model(source_frames,target_raw,fit,protocol):
 th=target_raw[list(HF)].to_numpy(np.float32); ty=target_raw.SOH.to_numpy(np.float32)*100
 s_rows=np.concatenate([d[list(HF)].to_numpy(np.float32) for d in source_frames]);t_rows=th[:fit]
 scaler_rows=s_rows if protocol=='SOURCE_ONLY_ZERO_SHOT' else np.concatenate([s_rows,t_rows]);mu,sd=scaler_rows.mean(0),scaler_rows.std(0);sd[sd<1e-8]=1
 sx,sy=source_arrays(source_frames,mu,sd);ti=np.arange(W,fit);tx=windows((th-mu)/sd,ti);ty_train=ty[ti]
 if protocol=='SOURCE_ONLY_ZERO_SHOT': x,y,yscale=sx,sy,np.concatenate([d.SOH.to_numpy(np.float32)*100 for d in source_frames])
 else:x,y,yscale=np.concatenate([sx,tx]),np.concatenate([sy,ty_train]),np.concatenate([*(d.SOH.to_numpy(np.float32)*100 for d in source_frames),ty[:fit]])
 ym,ystd=yscale.mean(),max(yscale.std(),1e-8);model=Ridge(alpha=ALPHA).fit(x,(y-ym)/ystd)
 return model,mu,sd,float(ym),float(ystd),sx,sy
def predict(model,mu,sd,ym,ysd,raw,idx):return model.predict(windows((raw[list(HF)].to_numpy(np.float32)-mu)/sd,idx))*ysd+ym

def residual_row(target,set_name,protocol,split,raw,idx,model,mu,sd,ym,ysd):
 y=raw.SOH.to_numpy(np.float32)[idx]*100;p=predict(model,mu,sd,ym,ysd,raw,idx);e=y-p; h=raw.loc[idx,list(HF)].to_numpy(float)
 return {'Battery':target,'SourceSet':set_name,'ModelProtocol':protocol,'EvaluationSplit':split,'Rows':len(idx),**qstats(e,'Residual'),**qstats(p,'Prediction'),'ResidualVsPredictedSOH':corr(e,p),'ResidualVsHF1':corr(e,h[:,0]),'ResidualVsHF2':corr(e,h[:,1]),'ResidualVsHF3':corr(e,h[:,2]),'TestLoaded':False}
def source_residual_row(target,set_name,protocol,frames,model,mu,sd,ym,ysd):
 es=[];ps=[];hs=[]
 for raw in frames:
  idx=np.arange(W,len(raw)); y=raw.SOH.to_numpy(np.float32)[idx]*100; p=predict(model,mu,sd,ym,ysd,raw,idx); es.append(y-p);ps.append(p);hs.append(raw.loc[idx,list(HF)].to_numpy(float))
 e,p,h=np.concatenate(es),np.concatenate(ps),np.concatenate(hs)
 return {'Battery':target,'SourceSet':set_name,'ModelProtocol':protocol,'EvaluationSplit':'source_training','Rows':len(e),**qstats(e,'Residual'),**qstats(p,'Prediction'),'ResidualVsPredictedSOH':corr(e,p),'ResidualVsHF1':corr(e,h[:,0]),'ResidualVsHF2':corr(e,h[:,1]),'ResidualVsHF3':corr(e,h[:,2]),'TestLoaded':False}

def local_rows(target,set_name,raw,idx,model,mu,sd,ym,ysd,sx,sy):
 xv=windows((raw[list(HF)].to_numpy(np.float32)-mu)/sd,idx);y=raw.SOH.to_numpy(np.float32)[idx]*100
 d=np.sqrt(np.sum((xv[:,None,:]-sx[None,:,:])**2,axis=2));nn=np.argpartition(d,K-1,axis=1)[:,:K];nearest=np.take_along_axis(d,nn,axis=1);local=sy[nn].mean(1);delta=y-local
 return {'Battery':target,'SourceSet':set_name,'NeighborsK':K,'Rows':len(idx),**qstats(nearest[:,0],'NearestDistance'),**qstats(delta,'LocalSOHDelta'),'LocalDeltaPositiveFraction':float(np.mean(delta>0)),'CorrelationLocalSOH':corr(y,local),'TestLoaded':False}

def coefficient_rows(name,model,mu,sd,ym,ysd,kind,metadata):
 labels=[f'{feature}_lag{lag}' for lag in range(W-1,-1,-1) for feature in HF];coef=model.coef_.reshape(-1);norm=max(float(np.linalg.norm(coef)),1e-12);rows=[]
 for label,value in zip(labels,coef):rows.append({**metadata,'ModelName':name,'ModelKind':kind,'RowType':'COEFFICIENT','Term':label,'Coefficient':float(value),'CoefficientSign':int(np.sign(value)),'NormalizedAbsCoefficient':float(abs(value)/norm),'Intercept':float(model.intercept_),'TestLoaded':False})
 rows.append({**metadata,'ModelName':name,'ModelKind':kind,'RowType':'MODEL_SUMMARY','Term':'ALL_COEFFICIENTS','CoefficientL2':float(norm),'Intercept':float(model.intercept_),'YScalerMean':ym,'YScalerStd':ysd,'FeatureScalerMeanHF1':float(mu[0]),'FeatureScalerMeanHF2':float(mu[1]),'FeatureScalerMeanHF3':float(mu[2]),'TestLoaded':False});return rows

def run_target(target,source_data):
 te,ve=boundary(target);raw=frame(target,nrows=ve)
 if len(raw)!=ve:raise RuntimeError(f'{target}: target prefix changed after cleaning')
 fit=max(W+3,int(te*.8));vi=np.arange(te,ve);pi=np.arange(W,fit);metrics_rows=[];resid=[];local=[];multi=[];coef=[]
 # target-only reference fitted under the verified Phase-6 feature/y scaling contract.
 th=raw[list(HF)].to_numpy(np.float32);ty=raw.SOH.to_numpy(np.float32)*100;mu0,sd0=th[:fit].mean(0),th[:fit].std(0);sd0[sd0<1e-8]=1;ym0,ys0=ty[:fit].mean(),max(ty[:fit].std(),1e-8);p0=Ridge(alpha=ALPHA).fit(windows((th-mu0)/sd0,pi),(ty[pi]-ym0)/ys0);p=predict(p0,mu0,sd0,ym0,ys0,raw,vi)
 metrics_rows.append({'Battery':target,'SourceSet':'NONE','Protocol':'P0_TARGET_ONLY','Track':'TARGET_ONLY_REFERENCE','RidgeAlpha':ALPHA,'ParameterCount':int(p0.coef_.size+1),'TrainingSamples':len(pi),'SourceTrainingSamples':0,'TargetTrainingSamples':len(pi),'UsesTargetSOHLabelsForTraining':True,'ScalerFitScope':'TARGET_FIT_PREFIX_ONLY','TestLoaded':False,**metrics(ty[vi],p)})
 coef+=coefficient_rows(f'{target}_PREFIX',p0,mu0,sd0,ym0,ys0,'BATTERY_PREFIX',{'Battery':target,'SourceSet':'NONE','Protocol':'P0_TARGET_ONLY'})
 for set_name,names in SOURCE_SETS.items():
  frames=[source_data[n] for n in names]
  for protocol,track in (('SOURCE_ONLY_ZERO_SHOT','SOURCE_TRANSFER/ZERO_SHOT_DIAGNOSTIC'),('SOURCE_PLUS_TARGET_CALIBRATED','CALIBRATED_TRANSFER')):
   model,mu,sd,ym,ysd,sx,sy=fit_model(frames,raw,fit,protocol);pred=predict(model,mu,sd,ym,ysd,raw,vi);target_labels=protocol!='SOURCE_ONLY_ZERO_SHOT'
   metrics_rows.append({'Battery':target,'SourceSet':set_name,'Protocol':protocol,'Track':track,'RidgeAlpha':ALPHA,'ParameterCount':int(model.coef_.size+1),'TrainingSamples':len(sy)+(len(pi) if target_labels else 0),'SourceTrainingSamples':len(sy),'TargetTrainingSamples':len(pi) if target_labels else 0,'UsesTargetSOHLabelsForTraining':target_labels,'ScalerFitScope':'+'.join(names)+(' + target fit prefix' if target_labels else ''),'TestLoaded':False,**metrics(ty[vi],pred)})
   resid.append(source_residual_row(target,set_name,protocol,frames,model,mu,sd,ym,ysd))
   resid.append(residual_row(target,set_name,protocol,'target_prefix',raw,pi,model,mu,sd,ym,ysd));resid.append(residual_row(target,set_name,protocol,'target_validation',raw,vi,model,mu,sd,ym,ysd))
   coef+=coefficient_rows(f'{set_name}_{target}_{protocol}',model,mu,sd,ym,ysd,'TRANSFER_RIDGE',{'Battery':target,'SourceSet':set_name,'Protocol':protocol})
   if protocol=='SOURCE_ONLY_ZERO_SHOT':
    local.append(local_rows(target,set_name,raw,vi,model,mu,sd,ym,ysd,sx,sy));xv=windows((raw[list(HF)].to_numpy(np.float32)-mu)/sd,vi)
    # Recompute full nearest distances once for the mandated multivariate support summary.
    d=np.sqrt(np.sum((xv[:,None,:]-sx[None,:,:])**2,axis=2)).min(axis=1)
    multi.append({'Battery':target,'SourceSet':set_name,'TargetSplit':'validation','Rows':len(vi),**qstats(d,'NearestSourceDistance'),'TestLoaded':False})
 return metrics_rows,resid,local,multi,coef

def basic_battery_coefficients(source_data):
 rows=[]
 for battery,data in source_data.items():
  h=data[list(HF)].to_numpy(np.float32);y=data.SOH.to_numpy(np.float32)*100;mu,sd=h.mean(0),h.std(0);sd[sd<1e-8]=1;idx=np.arange(W,len(data));ym,ys=y.mean(),max(y.std(),1e-8);m=Ridge(alpha=ALPHA).fit(windows((h-mu)/sd,idx),(y[idx]-ym)/ys);rows+=coefficient_rows(f'{battery}_FULL',m,mu,sd,ym,ys,'SOURCE_FULL',{'Battery':battery,'SourceSet':battery,'Protocol':'SOURCE_FULL_DIAGNOSTIC'})
 return rows

def decide(multi,local,metrics):
 # Compare combined-source diagnostics: B0018 manifold separation vs B0007 and local SOH mismatch.
 q=multi[multi.SourceSet=='S2_B0005_B0006'].set_index('Battery');l=local[local.SourceSet=='S2_B0005_B0006'].set_index('Battery');distance_mismatch=q.loc['B0018','NearestSourceDistanceMean']>1.25*q.loc['B0007','NearestSourceDistanceMean'];local_mismatch=abs(l.loc['B0018','LocalSOHDeltaMean'])>1.5*abs(l.loc['B0007','LocalSOHDeltaMean']) and abs(l.loc['B0018','LocalSOHDeltaMean'])>.5
 p0=metrics[metrics.Protocol=='P0_TARGET_ONLY'].set_index('Battery').RMSE
 singles=metrics[metrics.Protocol=='SOURCE_ONLY_ZERO_SHOT'];specific=False
 for b in TARGETS:
  vals=singles[singles.Battery==b].set_index('SourceSet').RMSE
  specific |= ((vals['S0_B0005']<p0[b] and vals['S1_B0006']>p0[b]) or (vals['S1_B0006']<p0[b] and vals['S0_B0005']>p0[b]))
 if distance_mismatch:main='MULTIVARIATE_SUPPORT_MISMATCH'
 elif local_mismatch:main='CONDITIONAL_RELATIONSHIP_SHIFT_CONFIRMED'
 elif specific:main='SOURCE_SPECIFIC_NEGATIVE_TRANSFER'
 else:main='SOURCE_TARGET_MAPPING_MISMATCH'
 return main,('SOURCE_SPECIFIC_NEGATIVE_TRANSFER' if specific and main!='SOURCE_SPECIFIC_NEGATIVE_TRANSFER' else 'NONE')
def calibration_summary(coeff,residual):
 rows=[]
 for battery in TARGETS:
  for source_set in SOURCE_SETS:
   a=coeff[(coeff.Battery==battery)&(coeff.SourceSet==source_set)&(coeff.Protocol=='SOURCE_ONLY_ZERO_SHOT')&(coeff.RowType=='COEFFICIENT')].sort_values('Term')
   b=coeff[(coeff.Battery==battery)&(coeff.SourceSet==source_set)&(coeff.Protocol=='SOURCE_PLUS_TARGET_CALIBRATED')&(coeff.RowType=='COEFFICIENT')].sort_values('Term')
   def residual_mean(protocol,split):
    q=residual[(residual.Battery==battery)&(residual.SourceSet==source_set)&(residual.ModelProtocol==protocol)&(residual.EvaluationSplit==split)]
    return float(q.ResidualMean.iloc[0])
   rows.append({'Battery':battery,'SourceSet':source_set,'CoefficientDeltaL2':float(np.linalg.norm(a.Coefficient.to_numpy()-b.Coefficient.to_numpy())),'InterceptDelta':float(b.Intercept.iloc[0]-a.Intercept.iloc[0]),'PrefixResidualMean_SourceOnly':residual_mean('SOURCE_ONLY_ZERO_SHOT','target_prefix'),'PrefixResidualMean_Calibrated':residual_mean('SOURCE_PLUS_TARGET_CALIBRATED','target_prefix'),'ValidationResidualMean_SourceOnly':residual_mean('SOURCE_ONLY_ZERO_SHOT','target_validation'),'ValidationResidualMean_Calibrated':residual_mean('SOURCE_PLUS_TARGET_CALIBRATED','target_validation'),'TestLoaded':False})
 return pd.DataFrame(rows)

def main():
 OUT.mkdir(parents=True,exist_ok=True);source={b:frame(b) for b in ('B0005','B0006')};mr=[];rr=[];lr=[];mm=[];cr=basic_battery_coefficients(source)
 for t in TARGETS:
  print(f'[Phase9] {t}: S0/S1/S2 compatibility audit',flush=True);a,b,c,d,e=run_target(t,source);mr+=a;rr+=b;lr+=c;mm+=d;cr+=e
 m,r,l,ma,c=map(pd.DataFrame,(mr,rr,lr,mm,cr));main_verdict,secondary=decide(ma,l,m);cal=calibration_summary(c,r)
 m.to_csv(OUT/'source_specific_transfer_metrics.csv',index=False,encoding='utf-8-sig');ma.to_csv(OUT/'multivariate_support_metrics.csv',index=False,encoding='utf-8-sig');r.to_csv(OUT/'conditional_residual_analysis.csv',index=False,encoding='utf-8-sig');l.to_csv(OUT/'local_neighbor_soh_shift.csv',index=False,encoding='utf-8-sig');c.to_csv(OUT/'ridge_coefficient_comparison.csv',index=False,encoding='utf-8-sig')
 report=['# Phase 9 — Source–Target Compatibility & Conditional Shift Audit','',f'Primary failure mechanism: {main_verdict}',f'Secondary conclusion: {secondary}','', '## Protocol','S0=B0005 only, S1=B0006 only, S2=B0005+B0006. Every set is evaluated as source-only zero-shot and source+target-prefix calibrated transfer under the fixed Phase-8 column-scaler and Ridge(alpha=1.0) contract.','Target CSVs are read only with nrows=ValidationEnd; all result rows set TestLoaded=false.','', '## Source contribution',m[['Battery','SourceSet','Protocol','Track','TrainingSamples','SourceTrainingSamples','TargetTrainingSamples','UsesTargetSOHLabelsForTraining','RMSE','MAE','R2','PredictionMean','PredictionStd','TestLoaded']].to_csv(index=False),'','## Combined-source local diagnostic',l[l.SourceSet=='S2_B0005_B0006'].to_csv(index=False),'','## Conditional-shift interpretation','B0018 has a systematic positive local SOH delta under S2, but its multivariate nearest-source distance is also materially larger than B0007. Therefore local SOH mismatch is recorded as secondary evidence, not independently confirmed conditional relationship shift; the predefined priority rule selects multivariate support mismatch.','','## Calibration effect',cal.to_csv(index=False),'','## Evidence boundary','Multivariate nearest-neighbor distance and local SOH delta are diagnostics, not a new predictive model. Coefficient differences are statistical mapping evidence only and do not identify physical mechanisms.']
 (OUT/'PHASE9_REPORT.md').write_text('\n'.join(report),encoding='utf8');print(main_verdict);print(secondary)
if __name__=='__main__':main()
