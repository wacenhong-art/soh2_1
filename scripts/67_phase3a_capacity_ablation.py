"""Phase 3A: preregistered fusion-capacity ablation (locked validation only)."""
from __future__ import annotations
import argparse, importlib.util, json, sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT_DEFAULT=ROOT/'output'/'phase3a_capacity_ablation_v1'
PHASE2=ROOT/'output'/'phase2_fusion_seq_ablation_v1'
BATTERIES=('B0007','B0018'); SEEDS=(42,123,2024,3407,7777)
EPOCHS=800; PATIENCE=50; SEQ_LEN=4; EPSILON=.05
CONFIGS={
 'C0_FULL_BILSTM': {'variant':'C0_FULL_BILSTM','source':'phase2_reference','description':'Phase-2 best IPRF reference'},
 'C1_SMALL_BILSTM': {'variant':'C1_SMALL_BILSTM','source':'train','description':'Bi-LSTM hidden=8; 64/32/16 weight MLP'},
 'C2_TINY_GRU': {'variant':'C2_TINY_GRU','source':'train','description':'unidirectional GRU(8); 8/24/3 weight and 11/24/1 residual heads'},
}

def load(name,path):
 s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); assert s and s.loader; sys.modules[name]=m; s.loader.exec_module(m); return m
phase2=load('phase2_capacity',ROOT/'scripts'/'66_phase2_fusion_seq_ablation.py')
fusion=phase2.fusion

def phase2_dir(kind,seed,battery): return PHASE2/kind/'seq_04'/f'seed_{seed}'/battery
def sample_count(battery): return 19 if battery=='B0007' else 11

def c0_reference(seed,battery):
 d=phase2_dir('IPRF_RESIDUAL_FUSION',seed,battery)
 metric=pd.read_csv(d/'fusion_validation_metrics.csv').iloc[0].to_dict()
 metric.update({'Configuration':'C0_FULL_BILSTM','Battery':battery,'Seed':seed,'FusionTrainingSamples':sample_count(battery),'TestLoaded':False,'TestEvaluated':False,'ReferenceSource':str(d)})
 metric['ParametersPerSample']=float(metric['ParameterCount'])/sample_count(battery)
 return metric, pd.read_csv(d/'gmtc_pred_validation_result.csv')

def new_run(out,config,seed,battery):
 component=phase2.source_dir(seed,battery); phase2.source_manifest(seed,battery)
 run=out/config/f'seed_{seed}'/battery; metric_path=run/'fusion_validation_metrics.csv'
 if metric_path.exists() and (run/'run_manifest.json').exists():
  metric=pd.read_csv(metric_path).iloc[0].to_dict(); frame=pd.read_csv(run/'gmtc_pred_validation_result.csv')
 else:
  old=fusion.SEQ_LEN; fusion.SEQ_LEN=SEQ_LEN
  try:
   run.mkdir(parents=True,exist_ok=True)
   metric,frame=fusion.run_fusion(str(component),str(run),str(run/'fusion_model.pth'),phase2.phase1.engine.stable_seed(seed,battery,'Trend')+900,EPOCHS,PATIENCE,fusion_mode='residual',evaluate_test=False,stable_init=False,residual_epsilon=EPSILON,experiment_track='ENHANCEMENT',capacity_variant=CONFIGS[config]['variant'])
   metric.update({'Phase':'PHASE3A_CAPACITY_ABLATION','Configuration':config,'FusionSeqLen':SEQ_LEN,'ComponentWindow':10,'FusionTrainingSamples':sample_count(battery),'TestLoaded':False,'TestEvaluated':False,'ReferenceComponentPredictions':str(component)})
   metric['ParametersPerSample']=float(metric['ParameterCount'])/sample_count(battery)
   pd.DataFrame([metric]).to_csv(metric_path,index=False)
   (run/'run_manifest.json').write_text(json.dumps({'Phase':'PHASE3A','Configuration':config,'Architecture':CONFIGS[config]['description'],'Fixed':{'component_window':10,'fusion_seq_len':4,'epsilon':.05,'lr':.001,'batch_size':32,'patience':50,'weight_decay':1e-5,'L_weight':'UNVERIFIED_DISABLED'},'TestLoaded':False,'TestEvaluated':False,'SourceComponentManifest':phase2.source_manifest(seed,battery)},ensure_ascii=False,indent=2),encoding='utf-8')
  finally: fusion.SEQ_LEN=old
 metric.update({'Configuration':config,'Battery':battery,'Seed':seed,'FusionTrainingSamples':sample_count(battery),'TestLoaded':False,'TestEvaluated':False})
 metric['ParametersPerSample']=float(metric['ParameterCount'])/sample_count(battery)
 return metric,frame

def baselines(seed,battery,frame):
 rows=phase2.paired_baselines(battery,seed,phase2.source_dir(seed,battery),frame)
 for r in rows:r.update({'Configuration':'BASELINE_'+r['Baseline'],'FusionTrainingSamples':sample_count(battery),'TestLoaded':False,'TestEvaluated':False})
 paper=pd.read_csv(phase2_dir('PAPER_FUSION',seed,battery)/'fusion_validation_metrics.csv').iloc[0].to_dict()
 paper.update({'Configuration':'BASELINE_PAPER_FUSION','Battery':battery,'Seed':seed,'FusionTrainingSamples':sample_count(battery),'TestLoaded':False,'TestEvaluated':False})
 return rows+[paper]

def aggregate(metrics,baselines):
 mean=baselines.loc[baselines.Baseline=='MEAN_PREDICTOR',['Battery','Seed','RMSE']].drop_duplicates(['Battery','Seed']).rename(columns={'RMSE':'MeanBaselineRMSE'})
 runs=metrics.merge(mean,on=['Battery','Seed'],validate='many_to_one')
 runs['R2Gate']=runs.R2>0; runs['MeanGate']=runs.RMSE<runs.MeanBaselineRMSE; runs['CatastrophicGate']=runs.CatastrophicPredictionCount==0; runs['BoundGate']=runs.ResidualBoundViolationCount==0; runs['TestLockGate']=~runs.TestLoaded.astype(bool)&~runs.TestEvaluated.astype(bool)
 runs['RunQualified']=runs[['R2Gate','MeanGate','CatastrophicGate','BoundGate','TestLockGate']].all(axis=1)
 summary=[]
 for config,g in runs.groupby('Configuration',sort=False):
  complete=len(g)==10 and g.groupby('Battery').Seed.nunique().min()==5
  summary.append({'Configuration':config,'CompletedRuns':len(g),'CompletedSeeds':g.groupby('Battery').Seed.nunique().min(),'Qualified':bool(complete and g.RunQualified.all()),'WorstBatteryR2':g.groupby('Battery').R2.mean().min(),'WorstSeedRMSE':g.RMSE.max(),'FailureRate':(g.CatastrophicPredictionCount>0).mean(),'RMSEStd':g.RMSE.std(ddof=0),'MeanRMSE':g.RMSE.mean(),'MeanR2':g.R2.mean(),'WorstR2':g.R2.min(),'ParameterCount':g.ParameterCount.iloc[0]})
 summary=pd.DataFrame(summary).sort_values(['Qualified','WorstBatteryR2','WorstSeedRMSE','FailureRate','RMSEStd','MeanRMSE'],ascending=[False,False,True,True,True,True],kind='stable').reset_index(drop=True)
 return runs,summary

def plots(out,runs):
 for battery,g in runs.groupby('Battery'):
  s=g.groupby('Configuration',as_index=False).agg(ParameterCount=('ParameterCount','first'),ParametersPerSample=('ParametersPerSample','first'),MeanRMSE=('RMSE','mean'),WorstRMSE=('RMSE','max'),MeanR2=('R2','mean'),RMSEStd=('RMSE',lambda x:x.std(ddof=0)))
  fig,axes=plt.subplots(2,2,figsize=(10,8)); specs=[('ParameterCount','MeanRMSE','parameter count vs mean RMSE'),('ParameterCount','WorstRMSE','parameter count vs worst RMSE'),('ParameterCount','MeanR2','parameter count vs mean R2'),('ParametersPerSample','RMSEStd','parameters/sample vs RMSE std')]
  for ax,(x,y,title) in zip(axes.ravel(),specs):
   ax.scatter(s[x],s[y]); [ax.annotate(c,(a,b),fontsize=8) for c,a,b in zip(s.Configuration,s[x],s[y])]; ax.set_xscale('log'); ax.set_title(title); ax.grid(alpha=.25)
  fig.suptitle(f'{battery}: Phase 3A capacity ablation'); fig.tight_layout(); fig.savefig(out/f'{battery}_capacity_vs_metrics.png',dpi=160); plt.close(fig)

def table(df):
 h='| '+' | '.join(df.columns)+' |'; d='| '+' | '.join(['---']*len(df.columns))+' |'; rows=['| '+' | '.join(f'{x:.5g}' if isinstance(x,(float,np.floating)) else str(x) for x in r)+' |' for r in df.itertuples(index=False,name=None)]; return '\n'.join([h,d,*rows])
def report(out,runs,summary):
 p=runs.groupby(['Configuration','Battery'],as_index=False).agg(ParameterCount=('ParameterCount','first'),FusionTrainingSamples=('FusionTrainingSamples','first'),ParametersPerSample=('ParametersPerSample','first'),MeanRMSE=('RMSE','mean'),WorstRMSE=('RMSE','max'),RMSEStd=('RMSE',lambda x:x.std(ddof=0)),MeanR2=('R2','mean'),WorstR2=('R2','min'),FailureRate=('CatastrophicPredictionCount',lambda x:(x>0).mean()),WeightEntropy=('WeightEntropy','mean'))
 c0=summary.loc[summary.Configuration=='C0_FULL_BILSTM'].iloc[0]; c2=summary.loc[summary.Configuration=='C2_TINY_GRU'].iloc[0]
 partial = (c2.MeanRMSE < c0.MeanRMSE and c2.WorstSeedRMSE < c0.WorstSeedRMSE and c2.WorstBatteryR2 > c0.WorstBatteryR2)
 effective='CAPACITY_REDUCTION_EFFECTIVE' if bool(summary.Qualified.any()) else ('CAPACITY_REDUCTION_PARTIALLY_EFFECTIVE' if partial else 'CAPACITY_REDUCTION_NOT_EFFECTIVE')
 lines=['# Phase 3A — Fusion Capacity Ablation','','## Protocol','Only capacity changed. Component predictions, fusion_seq_len=4, epsilon=0.05, seeds, splits, optimizer and locked-test status are identical to Phase 2. C0 is the Phase-2 residual reference; C1/C2 are newly trained.','','## Parameter/sample analysis','',table(p),'','## Gate ranking','',table(summary),'','## Answers','',f'RQ3A.1 worst-seed performance: see `WorstSeedRMSE` in the ranked table.',f'RQ3A.2 parameter/sample and seed variance are reported per battery above.',f'RQ3A.3 Tiny versus Full: Mean RMSE {c2.MeanRMSE:.4f} vs {c0.MeanRMSE:.4f}; RMSE std {c2.RMSEStd:.4f} vs {c0.RMSEStd:.4f}.','RQ3A.4 A recurrent fusion is retained only if the preregistered qualification gate passes; this report does not promote a best seed.','','## Final decision','',effective,'QUALIFIED_CONFIGURATION_FOUND' if bool(summary.Qualified.any()) else 'NO_QUALIFIED_CONFIGURATION','','Stop condition reached: Phase 3B and all forbidden experiments were not started.']
 (out/'PHASE3A_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
 p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,default=OUT_DEFAULT);args=p.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
 metrics=[]; base=[]
 for config in CONFIGS:
  for seed in SEEDS:
   for battery in BATTERIES:
    print(f'[Phase3A] {config} seed={seed} battery={battery}',flush=True)
    m,f=c0_reference(seed,battery) if config=='C0_FULL_BILSTM' else new_run(out,config,seed,battery)
    metrics.append(m);base.extend(baselines(seed,battery,f))
 metrics=pd.DataFrame(metrics);base=pd.DataFrame(base);runs,summary=aggregate(metrics,base)
 runs.to_csv(out/'capacity_ablation_metrics.csv',index=False,encoding='utf-8-sig'); runs.groupby(['Configuration','Battery'],as_index=False).agg(ParameterCount=('ParameterCount','first'),FusionTrainingSamples=('FusionTrainingSamples','first'),ParametersPerSample=('ParametersPerSample','first')).to_csv(out/'parameter_sample_analysis.csv',index=False,encoding='utf-8-sig'); summary.to_csv(out/'configuration_gate_summary.csv',index=False,encoding='utf-8-sig'); base.to_csv(out/'baseline_metrics.csv',index=False,encoding='utf-8-sig'); plots(out,runs);report(out,runs,summary);print(summary.to_string(index=False))
if __name__=='__main__':main()
