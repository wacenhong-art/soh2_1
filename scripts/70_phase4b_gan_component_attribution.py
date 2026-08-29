"""Phase 4B: component-only REAL_ONLY vs REAL_PLUS_GAN attribution."""
from __future__ import annotations
import importlib.util,json,sys
from pathlib import Path
import numpy as np,pandas as pd
from statsmodels.tsa.seasonal import STL
from sklearn.metrics import mean_squared_error,mean_absolute_error,r2_score
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'/'phase4b_gan_component_attribution_v1';AUG=ROOT/'output'/'scf_gan_800_v1'/'aug';BAT=('B0007','B0018');SEEDS=(42,123,2024,3407,7777);EPOCHS=800;PATIENCE=50
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);assert s and s.loader;sys.modules[n]=m;s.loader.exec_module(m);return m
engine=load('engine4b',ROOT/'scripts'/'08_physics_trend_ablation.py');HF=engine.HF_COLS
def reg(y,p):return {'RMSE':float(np.sqrt(mean_squared_error(y,p))),'MAE':float(mean_absolute_error(y,p)),'R2':float(r2_score(y,p)),'StdTrue':float(np.std(y)),'StdPred':float(np.std(p)),'MeanTrue':float(np.mean(y)),'MeanPred':float(np.mean(p)),'Correlation':float(np.corrcoef(y,p)[0,1]) if np.std(y)>1e-12 and np.std(p)>1e-12 else np.nan}
def run_one(source,b,seed):
 manifest=json.loads((ROOT/'output'/'phase1_failure_isolation_v1'/'PAPER_FUSION'/'seed_42'/b/'none'/'run_manifest.json').read_text())['engine_manifest'];te,ve=int(manifest['TrainEnd']),int(manifest['ValidationEnd'])
 # Read only the opened train+validation prefix; no test-cycle row is loaded.
 raw=pd.read_csv(ROOT/'data'/'hf_csv'/f'{b}_hf.csv',nrows=ve)[HF+['SOH']].apply(pd.to_numeric,errors='coerce').dropna().reset_index(drop=True);soh=raw.SOH.to_numpy(np.float32)*100
 dec=STL(soh[:te],period=engine.ts.STL_PERIOD,robust=True).fit();targets={'Trend':np.asarray(dec.trend,np.float32),'Seasonal':np.asarray(dec.seasonal,np.float32),'Residual':np.asarray(dec.resid,np.float32)}
 # Diagnostic truth is train+validation prefix only; it never reads test.
 td=STL(soh[:ve],period=engine.ts.STL_PERIOD,robust=True).fit();truth={'Trend':np.asarray(td.trend),'Seasonal':np.asarray(td.seasonal),'Residual':np.asarray(td.resid)}
 fit=max(engine.ts.SEQ_LEN+3,int(te*.8));hf=raw[HF].to_numpy(np.float32);hm,hs=hf[:fit].mean(0),hf[:fit].std(0);hs[hs<1e-8]=1;norm=lambda f:(f[HF].to_numpy(np.float32)-hm)/hs;nh=norm(raw);aug=pd.read_csv(AUG/f'{b}_aug_train_hf.csv');fitaug=aug[(aug.Cycle.astype(int)<fit) & ((aug.DatasetID==0) if source=='G0_REAL_ONLY' else True)].copy();pred={}
 for name in ('Trend','Seasonal','Residual'):
  engine.reset_seed(engine.stable_seed(seed,b,name));v=targets[name];mean,std=float(v[:fit].mean()),max(float(v[:fit].std()),1e-8);state=((v-mean)/std).reshape(-1,1);lag=np.vstack([state[:1],state[:-1]]);traj=engine.make_trajectories(fitaug,norm,lag,v,mean,std,False)
  (OUT/source).mkdir(parents=True,exist_ok=True);model=engine.ts.iTransformer(seq_len=engine.ts.SEQ_LEN,d_model=64,nhead=4,layers=2).to(engine.DEVICE) if name=='Residual' else engine.ts.TimesNet(input_dim=3,d_model=64,top_k=3).to(engine.DEVICE)
  model,_=engine.train_component(model,traj,(nh,v,fit,te),'none',0.,mean,std,EPOCHS,PATIENCE,OUT/source/f'{b}_{seed}_{name}.csv',False,False);start=te-engine.ts.SEQ_LEN;rec=engine.causal_component_predict(model,nh,v,mean,std,start,ve,te,False,False);pred[name]=rec[te-start:]
 idx=np.arange(te,ve);rows=[]
 for k in pred:rows.append({'DataSource':source,'Battery':b,'Seed':seed,'Component':k,**reg(truth[k][idx],pred[k]),'TestLoaded':False})
 y=sum(pred.values());rows.append({'DataSource':source,'Battery':b,'Seed':seed,'Component':'RECONSTRUCTED_SOH',**reg(soh[idx],y),'TestLoaded':False});base=[]
 for k in truth:base.append({'DataSource':source,'Battery':b,'Seed':seed,'Baseline':'PERSISTENCE_COMPONENT','Component':k,**reg(truth[k][idx],truth[k][idx-1]),'TestLoaded':False})
 base.append({'DataSource':source,'Battery':b,'Seed':seed,'Baseline':'PERSISTENCE_SOH','Component':'RECONSTRUCTED_SOH',**reg(soh[idx],soh[idx-1]),'TestLoaded':False});return rows,base
def main():
 OUT.mkdir(parents=True,exist_ok=True);rows=[];base=[]
 for source in ('G0_REAL_ONLY','G1_REAL_PLUS_GAN'):
  for s in SEEDS:
   for b in BAT:
    print(f'[Phase4B] {source} {b} seed={s}',flush=True);r,q=run_one(source,b,s);rows+=r;base+=q
 m=pd.DataFrame(rows);bl=pd.DataFrame(base);m.to_csv(OUT/'component_metrics_by_data_source.csv',index=False,encoding='utf-8-sig');bl.to_csv(OUT/'component_baseline_comparison.csv',index=False,encoding='utf-8-sig')
 dist=[]
 for b in BAT:
  a=pd.read_csv(AUG/f'{b}_aug_train_hf.csv');
  for group,g in [('REAL_PREFIX',a[a.DatasetID==0]),('GAN_SYNTHETIC',a[a.DatasetID!=0])]:
   for col in HF:
    x=g[col];dist.append({'Battery':b,'Group':group,'Feature':col,'Mean':x.mean(),'Std':x.std(),'Min':x.min(),'Q25':x.quantile(.25),'Median':x.median(),'Q75':x.quantile(.75),'Max':x.max(),'CorrSOH':x.corr(g.SOH),'CorrCycle':x.corr(g.Cycle)})
 pd.DataFrame(dist).to_csv(OUT/'gan_vs_real_distribution.csv',index=False,encoding='utf-8-sig')
 g=m.groupby(['DataSource','Component']).agg(RMSE=('RMSE','mean'),R2=('R2','mean'),StdPred=('StdPred','mean')).reset_index();real=g[g.DataSource=='G0_REAL_ONLY'].set_index('Component');gan=g[g.DataSource=='G1_REAL_PLUS_GAN'].set_index('Component');by_battery=m[m.Component=='RECONSTRUCTED_SOH'].pivot(index='Battery',columns='DataSource',values='RMSE');improved=by_battery.G0_REAL_ONLY<by_battery.G1_REAL_PLUS_GAN;decision='GAN_AUGMENTATION_IS_MAJOR_CONTRIBUTOR' if improved.all() and real.loc['RECONSTRUCTED_SOH','R2']>0 else ('GAN_CONTRIBUTES_BUT_IS_NOT_PRIMARY_CAUSE' if improved.all() else ('COMPONENT_MODEL_GENERALIZATION_FAILURE' if (~improved).all() else 'MIXED_COMPONENT_FAILURE'))
 lines=['# Phase 4B — GAN vs Component Model Attribution','',g.to_csv(index=False),'',f'Decision: {decision}','NO_MODEL_CHANGE_PERFORMED','TEST_NOT_LOADED','G2_GAN_ONLY not run: synthetic trajectories reuse target-cycle SOH labels as their generated conditioning alignment, so removing all real supervised rows changes the supervision semantics rather than isolating augmentation.']
 (OUT/'PHASE4B_REPORT.md').write_text('\n'.join(lines),encoding='utf8');print(g);print(decision)
if __name__=='__main__':main()
