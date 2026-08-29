import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_capacity_variants_are_preregistered_and_tiny_is_small():
 p=ROOT/'scripts'/'67_phase3a_capacity_ablation.py';s=importlib.util.spec_from_file_location('phase3a_test',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 assert tuple(m.CONFIGS)==('C0_FULL_BILSTM','C1_SMALL_BILSTM','C2_TINY_GRU')
 assert m.SEQ_LEN==4 and m.EPSILON==.05
