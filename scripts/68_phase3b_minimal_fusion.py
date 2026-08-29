"""Phase 3B: fixed non-recurrent and minimal-fusion validation."""
from __future__ import annotations
import importlib.util,json,sys
from pathlib import Path
import numpy as np,pandas as pd
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'output'/'phase3b_minimal_fusion_v1'; P3A=ROOT/'output'/'phase3a_capacity_ablation_v1'
BATTERIES=('B0007','B0018');SEEDS=(42,123,2024,3407,7777);SEQ=4;EPS=.05;EPOCHS=800;PATIENCE=50
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);assert s and s.loader;sys.modules[n]=m;s.loader.exec_module(m);return m
p3=load('p3a_phase3b',ROOT/'scripts'/'67_phase3a_capacity_ablation.py'); fusion=p3.fusion; p2=p3.phase2
CONFIGS={'C3_NONRECURRENT':'9->16->3 Softmax; 9->8->1 bounded correction','C4_MINIMAL':'[T,S,R]->Linear(3,3)->Softmax; 3->4->1 bounded correction'}
def samples(b):return 19 if b=='B0007' else 11
def direct_frame(seed,battery):
 d=p2.source_dir(seed,battery); f=pd.read_csv(d/'comp_pred_val.csv').iloc[SEQ:].copy(); f['True_SOH']=f['True_SOH'];f['Pred_SOH']=f[['Pred_Trend','Pred_Seasonal','Pred_Residual']].sum(axis=1);f['Delta_SOH']=0.;f['Base_SOH']=f.Pred_SOH;f['w_Trend']=1.;f['w_Seasonal']=1.;f['w_Residual']=1.;return f
def direct_metrics(seed,battery):
 f=direct_frame(seed,battery);return {'Configuration':'DIRECT_COMPONENT_RECONSTRUCTION','Battery':battery,'Seed':seed,'ParameterCount':0,'FusionTrainingSamples':samples(battery),'ParametersPerSample':0.,'RMSE':float(np.sqrt(np.mean((f.True_SOH-f.Pred_SOH)**2))),'MAE':float(np.mean(np.abs(f.True_SOH-f.Pred_SOH))),'MAPE':float(np.abs(f.True_SOH-f.Pred_SOH).sum()/np.abs(f.True_SOH).sum()*100),'R2':float(1-((f.True_SOH-f.Pred_SOH)**2).sum()/((f.True_SOH-f.True_SOH.mean())**2).sum()),'CatastrophicPredictionCount':0,'ResidualBoundViolationCount':0,'WeightEntropy':0.,'WeightMin':1.,'WeightMax':1.,'WeightTemporalVariation':0.,'MeanAbsDelta':0.,'MaxAbsDelta':0.,'TestLoaded':False,'TestEvaluated':False},f
def run(config,seed,battery):
 run=OUT/config/f'seed_{seed}'/battery;p=run/'fusion_validation_metrics.csv';comp=p2.source_dir(seed,battery)
 if p.exists() and (run/'run_manifest.json').exists() and (config!='C4_MINIMAL' or json.loads((run/'run_manifest.json').read_text()).get('InferenceDeltaBase')=='weighted_component_base'):
  m=pd.read_csv(p).iloc[0].to_dict();f=pd.read_csv(run/'gmtc_pred_validation_result.csv');m['ResidualBoundViolationCount']=int((np.abs(f.Delta_SOH)>EPS*100+1e-4).sum());pd.DataFrame([m]).to_csv(p,index=False)
 else:
  old=fusion.SEQ_LEN;fusion.SEQ_LEN=SEQ
  try:
   run.mkdir(parents=True,exist_ok=True);m,f=fusion.run_fusion(str(comp),str(run),str(run/'fusion_model.pth'),p2.phase1.engine.stable_seed(seed,battery,'Trend')+900,EPOCHS,PATIENCE,fusion_mode='residual',evaluate_test=False,residual_epsilon=EPS,experiment_track='ENHANCEMENT',capacity_variant=config)
   m.update({'Phase':'PHASE3B_MINIMAL_FUSION','Configuration':config,'FusionTrainingSamples':samples(battery),'TestLoaded':False,'TestEvaluated':False});m['ParametersPerSample']=m['ParameterCount']/samples(battery);pd.DataFrame([m]).to_csv(p,index=False);(run/'run_manifest.json').write_text(json.dumps({'Phase':'PHASE3B','Architecture':CONFIGS[config],'InferenceDeltaBase':'weighted_component_base' if config=='C4_MINIMAL' else 'additive_component_base','Fixed':{'component_window':10,'fusion_seq_len':4,'epsilon':.05,'lr':.001,'batch_size':32,'patience':50,'weight_decay':1e-5},'TestLoaded':False,'TestEvaluated':False},ensure_ascii=False,indent=2),encoding='utf8')
  finally:fusion.SEQ_LEN=old
 m.update({'Configuration':config,'Battery':battery,'Seed':seed,'FusionTrainingSamples':samples(battery),'TestLoaded':False,'TestEvaluated':False});m['ParametersPerSample']=m['ParameterCount']/samples(battery);return m,f
def references():
 t=pd.read_csv(P3A/'capacity_ablation_metrics.csv');return t.loc[t.Configuration.isin(['C0_FULL_BILSTM','C2_TINY_GRU'])].copy()
def gate(metrics,baselines):
 metrics=metrics.drop(columns=['MeanBaselineRMSE'],errors='ignore')
 mean=baselines.loc[baselines.Baseline=='MEAN_PREDICTOR',['Battery','Seed','RMSE']].drop_duplicates(['Battery','Seed']).rename(columns={'RMSE':'MeanBaselineRMSE'});x=metrics.merge(mean,on=['Battery','Seed'],how='left');x['RunQualified']=(x.R2>0)&(x.RMSE<x.MeanBaselineRMSE)&(x.CatastrophicPredictionCount==0)&(x.ResidualBoundViolationCount==0)&(~x.TestLoaded.astype(bool))&(~x.TestEvaluated.astype(bool));rows=[]
 for c,g in x.groupby('Configuration'):
  if c=='DIRECT_COMPONENT_RECONSTRUCTION':continue
  rows.append({'Configuration':c,'CompletedRuns':len(g),'CompletedSeeds':g.groupby('Battery').Seed.nunique().min(),'Qualified':bool(len(g)==10 and g.RunQualified.all()),'WorstBatteryR2':g.groupby('Battery').R2.mean().min(),'WorstSeedRMSE':g.RMSE.max(),'RMSEStd':g.RMSE.std(ddof=0),'MeanRMSE':g.RMSE.mean(),'MeanR2':g.R2.mean(),'WorstR2':g.R2.min(),'FailureRate':(g.CatastrophicPredictionCount>0).mean(),'ParameterCount':g.ParameterCount.iloc[0]})
 return x,pd.DataFrame(rows).sort_values(['Qualified','WorstBatteryR2','WorstSeedRMSE','RMSEStd','MeanRMSE'],ascending=[False,False,True,True,True],kind='stable')
def md(d):
 h='| '+' | '.join(d.columns)+' |';b='| '+' | '.join(['---']*len(d.columns))+' |';r=['| '+' | '.join(f'{x:.5g}' if isinstance(x,(float,np.floating)) else str(x) for x in q)+' |' for q in d.itertuples(index=False,name=None)];return '\n'.join([h,b,*r])
def main():
 OUT.mkdir(parents=True,exist_ok=True);learn=[];base=[];direct=[]
 for c in CONFIGS:
  for s in SEEDS:
   for b in BATTERIES:
    print(f'[Phase3B] {c} seed={s} battery={b}',flush=True);m,f=run(c,s,b);learn.append(m);base.extend(p2.paired_baselines(b,s,p2.source_dir(s,b),f))
 for s in SEEDS:
  for b in BATTERIES:
   m,f=direct_metrics(s,b);direct.append(m);base.extend(p2.paired_baselines(b,s,p2.source_dir(s,b),f))
 metrics=pd.concat([references(),pd.DataFrame(learn),pd.DataFrame(direct)],ignore_index=True,sort=False);base=pd.DataFrame(base);x,summary=gate(metrics,base);x.to_csv(OUT/'minimal_fusion_metrics.csv',index=False,encoding='utf-8-sig');base.to_csv(OUT/'baseline_metrics.csv',index=False,encoding='utf-8-sig');summary.to_csv(OUT/'configuration_gate_summary.csv',index=False,encoding='utf-8-sig');param=x.groupby(['Configuration','Battery'],as_index=False).agg(ParameterCount=('ParameterCount','first'),FusionTrainingSamples=('FusionTrainingSamples','first'),ParametersPerSample=('ParametersPerSample','first'),MeanRMSE=('RMSE','mean'),RMSEStd=('RMSE',lambda z:z.std(ddof=0)),MeanR2=('R2','mean'));param.to_csv(OUT/'parameter_sample_analysis.csv',index=False,encoding='utf-8-sig')
 for b,g in param.groupby('Battery'):
  fig,ax=plt.subplots(figsize=(7,4));ax.scatter(g.ParameterCount+1,g.MeanRMSE);[ax.annotate(c,(a+1,y),fontsize=8) for c,a,y in zip(g.Configuration,g.ParameterCount,g.MeanRMSE)];ax.set_xscale('log');ax.set_xlabel('parameter count (+1)');ax.set_ylabel('mean RMSE');ax.set_title(f'{b}: parameter count vs RMSE');ax.grid(alpha=.25);fig.tight_layout();fig.savefig(OUT/f'{b}_parameter_vs_rmse.png',dpi=160);plt.close(fig)
 c0=summary.loc[summary.Configuration=='C0_FULL_BILSTM'].iloc[0];c2=summary.loc[summary.Configuration=='C2_TINY_GRU'].iloc[0];c3=summary.loc[summary.Configuration=='C3_NONRECURRENT'].iloc[0];c4=summary.loc[summary.Configuration=='C4_MINIMAL'].iloc[0];direct=x.loc[x.Configuration=='DIRECT_COMPONENT_RECONSTRUCTION'];learned=x.loc[x.Configuration.isin(['C0_FULL_BILSTM','C2_TINY_GRU','C3_NONRECURRENT','C4_MINIMAL'])];direct_better=direct.RMSE.mean()<learned.groupby('Configuration').RMSE.mean().min();final='CAPACITY_IS_CONTRIBUTING_BUT_NOT_SUFFICIENT' if (c3.MeanRMSE<c0.MeanRMSE or c4.MeanRMSE<c0.MeanRMSE) else 'CAPACITY_NOT_PRIMARY_BOTTLENECK';lines=['# Phase 3B — Minimal Fusion Validation','','## Protocol','C3/C4 only change the fusion architecture. Components, seq_len=4, epsilon=.05, five seeds and validation-only protocol are unchanged.','','## Parameter/sample analysis','',md(param),'','## Gate ranking','',md(summary),'','## Direct reconstruction',f'Mean RMSE={direct.RMSE.mean():.4f}; best learned-fusion mean RMSE={learned.groupby("Configuration").RMSE.mean().min():.4f}.','LEARNED_FUSION_NOT_JUSTIFIED_UNDER_CURRENT_SAMPLE_REGIME' if direct_better else 'DIRECT_RECONSTRUCTION_NOT_BETTER_THAN_ALL_LEARNED_FUSION','','## Final judgement','',final,'QUALIFIED_CONFIGURATION_FOUND' if summary.Qualified.any() else 'NO_QUALIFIED_CONFIGURATION','','No further fusion-architecture search was started. Next diagnostic targets only: component prediction, SCF-GAN, target-prefix protocol, or separately pre-registered transfer/calibration.'];(OUT/'PHASE3B_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8');print(summary.to_string(index=False))
if __name__=='__main__':main()
