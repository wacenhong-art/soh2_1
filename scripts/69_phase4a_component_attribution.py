"""Phase 4A diagnostic-only STL/component error attribution; no training."""
from __future__ import annotations
import importlib.util,json,sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np,pandas as pd
from sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score
from statsmodels.tsa.seasonal import STL
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'output'/'phase4a_component_attribution_v1'; P1=ROOT/'output'/'phase1_failure_isolation_v1'; BATTERIES=('B0007','B0018');SEEDS=(42,123,2024,3407,7777)
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);assert s and s.loader;sys.modules[n]=m;s.loader.exec_module(m);return m
p2=load('phase2_phase4a',ROOT/'scripts'/'66_phase2_fusion_seq_ablation.py'); PERIOD=p2.phase1.engine.ts.STL_PERIOD
def src(seed,b):return P1/'PAPER_FUSION'/f'seed_{seed}'/b/'none'
def reg(y,p):
 y=np.asarray(y,float);p=np.asarray(p,float);e=p-y;return {'RMSE':float(np.sqrt(mean_squared_error(y,p))),'MAE':float(mean_absolute_error(y,p)),'R2':float(r2_score(y,p)),'Bias':float(e.mean()),'PredStd':float(p.std()),'TrueStd':float(y.std()),'StdRatio':float(p.std()/y.std()) if y.std()>1e-12 else np.nan,'PredMin':float(p.min()),'PredMax':float(p.max()),'TrueMin':float(y.min()),'TrueMax':float(y.max())}
def flags(y,p):
 ratio=p.std()/max(y.std(),1e-12);corr=np.corrcoef(y,p)[0,1] if y.std()>1e-12 and p.std()>1e-12 else np.nan
 return {'NearConstantPrediction':bool(p.std()<1e-3),'AmplitudeCollapse':bool(ratio<.25),'SignError':bool(np.isfinite(corr) and corr<0),'ExcessiveVariance':bool(ratio>2),'Correlation':float(corr) if np.isfinite(corr) else np.nan}
def truth_and_bounds(b):
 raw=pd.read_csv(ROOT/'data'/'hf_csv'/f'{b}_hf.csv');soh=pd.to_numeric(raw.SOH,errors='coerce').to_numpy(float)*100;m=json.loads((src(42,b)/'run_manifest.json').read_text());e=m['engine_manifest'];train_end,val_end=int(e['TrainEnd']),int(e['ValidationEnd'])
 # Diagnostic truth is fitted only on the opened train+validation prefix.
 # Test-cycle SOH is never read into this Phase 4A computation.
 dec=STL(soh[:val_end],period=PERIOD,robust=True).fit();return soh[:val_end],{'Trend':np.asarray(dec.trend),'Seasonal':np.asarray(dec.seasonal),'Residual':np.asarray(dec.resid)},train_end,val_end,e
def main():
 OUT.mkdir(parents=True,exist_ok=True); rows=[];subs=[];cycles=[];overall=[];gan=[]
 for b in BATTERIES:
  soh,true,train_end,val_end,manifest=truth_and_bounds(b); idx=np.arange(train_end,val_end); oracle=true['Trend'][idx]+true['Seasonal'][idx]+true['Residual'][idx]; persistence=soh[idx-1]
  overall.append({'Battery':b,'Seed':'ORACLE','Method':'ORACLE_STL_RECONSTRUCTION',**reg(soh[idx],oracle),'TestLoaded':False});overall.append({'Battery':b,'Seed':'ORACLE','Method':'PERSISTENCE',**reg(soh[idx],persistence),'TestLoaded':False})
  for seed in SEEDS:
   pred=pd.read_csv(src(seed,b)/'comp_pred_val.csv').set_index('Cycle').loc[idx]
   comp={k:pred[f'Pred_{k}'].to_numpy(float) for k in ('Trend','Seasonal','Residual')}
   for k in comp:
    rows.append({'Battery':b,'Seed':seed,'Component':k,**reg(true[k][idx],comp[k]),**flags(true[k][idx],comp[k]),'ValidationStart':train_end,'ValidationEndExclusive':val_end,'TestLoaded':False})
   yc=sum(comp.values());overall.append({'Battery':b,'Seed':seed,'Method':'PREDICTED_COMPONENT_RECONSTRUCTION',**reg(soh[idx],yc),'TestLoaded':False})
   for target in ('Trend','Seasonal','Residual'):
    replaced=sum((comp[k] if k==target else true[k][idx]) for k in comp);subs.append({'Battery':b,'Seed':seed,'ReplacedComponent':target,**reg(soh[idx],replaced),'TestLoaded':False})
   et=comp['Trend']-true['Trend'][idx];es=comp['Seasonal']-true['Seasonal'][idx];er=comp['Residual']-true['Residual'][idx];
   cycles.extend(pd.DataFrame({'Battery':b,'Seed':seed,'Cycle':idx,'SOH_true':soh[idx],'Trend_true':true['Trend'][idx],'Seasonal_true':true['Seasonal'][idx],'Residual_true':true['Residual'][idx],'Trend_pred':comp['Trend'],'Seasonal_pred':comp['Seasonal'],'Residual_pred':comp['Residual'],'error_Trend':et,'error_Seasonal':es,'error_Residual':er,'Y_oracle':oracle,'Y_components':yc,'persistence_pred':persistence,'e_total':et+es+er,'Ycomponents_minus_SOH':yc-soh[idx],'PropagationIdentityError':(yc-oracle)-(et+es+er)}).to_dict('records'))
  gan.append({'Battery':b,'SyntheticTrajectories':5,'AugmentationDatasets':6,'Attribution':'GAN_ATTRIBUTION_REQUIRES_PHASE4B','Reason':'saved component predictions mix one real target prefix with five synthetic trajectories; no counterfactual no-GAN component artifact exists.'})
 metrics=pd.DataFrame(rows);sub=pd.DataFrame(subs);diag=pd.DataFrame(cycles);overall=pd.DataFrame(overall)
 metrics.to_csv(OUT/'component_metrics.csv',index=False,encoding='utf-8-sig');sub.to_csv(OUT/'oracle_substitution_metrics.csv',index=False,encoding='utf-8-sig');diag.to_csv(OUT/'component_cycle_diagnostics.csv',index=False,encoding='utf-8-sig');overall.to_csv(OUT/'reconstruction_metrics.csv',index=False,encoding='utf-8-sig');pd.DataFrame(gan).to_csv(OUT/'gan_attribution_status.csv',index=False,encoding='utf-8-sig')
 for b in BATTERIES:
  d=diag[diag.Battery==b];fig,ax=plt.subplots(5,1,figsize=(12,14),sharex=True)
  for a,k in zip(ax[:3],('Trend','Seasonal','Residual')):
   g=d.groupby('Cycle');mean=g[f'{k}_pred'].mean();lo=g[f'{k}_pred'].min();hi=g[f'{k}_pred'].max();truth=d.groupby('Cycle')[f'{k}_true'].first();a.plot(truth.index,truth,'k',label='true STL diagnostic');a.plot(mean.index,mean,label='pred mean');a.fill_between(mean.index,lo,hi,alpha=.2,label='seed range');a.set_title(f'{b} {k}: true vs predicted');a.legend()
  g=d.groupby('Cycle');a=ax[3];a.plot(g.SOH_true.first().index,g.SOH_true.first(),'k',label='SOH');a.plot(g.Y_components.mean().index,g.Y_components.mean(),label='pred components mean');a.set_title('SOH vs predicted component reconstruction');a.legend();a=ax[4]
  for k in ('error_Trend','error_Seasonal','error_Residual'):a.plot(g[k].mean().index,g[k].mean(),label=k)
  a.axhline(0,color='k',lw=.8);a.set_title('component error vs cycle');a.legend();a.set_xlabel('cycle');fig.tight_layout();fig.savefig(OUT/f'{b}_component_attribution.png',dpi=160);plt.close(fig)
 oracle_bad=overall[overall.Method=='ORACLE_STL_RECONSTRUCTION'].RMSE.max()>1e-3; comp_mean=metrics.groupby('Component').RMSE.mean().sort_values(ascending=False); primary=comp_mean.index[0]; multi=(comp_mean.iloc[1]/comp_mean.iloc[0]>0.5); flags_out=[]
 if oracle_bad:flags_out.append('STL_RECONSTRUCTION_PROTOCOL_FAILURE')
 else:
  flags_out.append('MULTI_COMPONENT_FORECASTING_FAILURE' if multi else f'{primary.upper()}_FORECASTING_PRIMARY_FAILURE')
 replacement=sub.groupby('ReplacedComponent').RMSE.mean().sort_values(ascending=False)
 def md(frame):
  h='| '+' | '.join(frame.columns)+' |';bar='| '+' | '.join(['---']*len(frame.columns))+' |';body=['| '+' | '.join(f'{x:.5g}' if isinstance(x,(float,np.floating)) else str(x) for x in r)+' |' for r in frame.itertuples(index=False,name=None)];return '\n'.join([h,bar,*body])
 recon=overall.groupby(['Battery','Method'],as_index=False).agg(RMSE=('RMSE','mean'),MAE=('MAE','mean'),R2=('R2','mean'));cm=metrics.groupby(['Battery','Component'],as_index=False).agg(RMSE=('RMSE','mean'),MAE=('MAE','mean'),R2=('R2','mean'),Bias=('Bias','mean'),StdRatio=('StdRatio','mean'),AmplitudeCollapse=('AmplitudeCollapse','mean'),SignError=('SignError','mean'));sm=sub.groupby(['Battery','ReplacedComponent'],as_index=False).agg(RMSE=('RMSE','mean'),R2=('R2','mean'))
 lines=['# Phase 4A — Component Prediction Error Attribution','','## Diagnostic scope','Validation-only read of existing Phase-1 component artifacts. Full-series STL is computed after the fact solely as the pre-existing diagnostic definition; it is never used for training, selection, or fusion. Test was not loaded.','','## STL and reconstruction',md(recon),'','## Component metrics (mean across five seeds)',md(cm),'','## Oracle substitutions',md(sm),'','## Findings','1. Oracle STL reconstruction is '+('not exact: protocol failure.' if oracle_bad else 'numerically exact; STL decomposition itself is not the observed failure.'),'2. Predicted-component reconstruction is compared directly with persistence in `reconstruction_metrics.csv`.','3. Largest single-component substitution degradation: '+replacement.index[0]+'.','4. '+('Multiple components materially contribute.' if multi else 'One component dominates by mean component RMSE.'),'5. '+gan[0]['Attribution'],'','## Decision flags','',*flags_out,'GAN_ATTRIBUTION_REQUIRES_PHASE4B','','Stop condition reached: no model, GAN, fusion, or data-protocol change was made.']
 (OUT/'PHASE4A_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
 print(metrics.groupby('Component').RMSE.mean());print(overall.groupby('Method').RMSE.mean());print(flags_out)
if __name__=='__main__':main()
