import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_runner():
    spec = importlib.util.spec_from_file_location("phase2_runner_test", ROOT / "scripts" / "66_phase2_fusion_seq_ablation.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_phase2_only_allows_preregistered_sequence_lengths():
    runner = load_runner()
    assert runner.SEQ_LENS == (4, 6, 8, 10)
    paper = runner.protocol.FusionConfig(
        track=runner.protocol.ExperimentTrack.PAPER_FUSION,
        fusion_seq_len=4, allow_fusion_seq_ablation=True,
    ).validate()
    assert paper.fusion_seq_len == 4
    try:
        runner.protocol.FusionConfig(
            track=runner.protocol.ExperimentTrack.PAPER_FUSION,
            fusion_seq_len=5, allow_fusion_seq_ablation=True,
        ).validate()
    except ValueError:
        pass
    else:
        raise AssertionError("seq_len=5 must be rejected")


def test_actual_phase2_sample_counts_match_production_windowing():
    runner = load_runner()
    counts = runner.build_sample_counts().set_index(["Battery", "FusionSeqLen"])
    assert counts.loc[("B0007", 10), "FusionTrainingSamples"] == 13
    assert counts.loc[("B0007", 4), "FusionTrainingSamples"] == 19
    assert counts.loc[("B0018", 10), "FusionTrainingSamples"] == 5
    assert counts.loc[("B0018", 4), "FusionTrainingSamples"] == 11
