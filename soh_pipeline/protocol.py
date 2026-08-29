"""Paper-faithful and enhancement experiment contracts.

The paper discloses two target-data descriptions (chronological 60/20/20 and
first-20%-of-life small-sample augmentation). This repository records the
chosen protocol explicitly and never calls either one zero-shot.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import hashlib
import itertools
import json


class ExperimentTrack(str, Enum):
    PAPER_FUSION = "PAPER_FUSION"
    ENHANCEMENT = "ENHANCEMENT"
    ZERO_SHOT = "ZERO_SHOT"
    CALIBRATED = "CALIBRATED"


PAPER_DEFINED = {
    "component_window": 10, "hidden_size": 16, "num_layers": 1,
    "normalization": "BatchNorm1d", "learning_rate": 0.001,
    "batch_size": 32, "patience": 50, "weight_decay": 1e-5,
}

REPRO_DEFINED = {
    "fusion_seq_len": 10, "stl_period": 12,
    "target_labeled_prefix_fraction": 0.20,
    "target_validation_fraction": 0.20,
}


@dataclass(frozen=True)
class FusionConfig:
    track: ExperimentTrack
    component_window: int = 10
    fusion_seq_len: int = 10
    allow_fusion_seq_ablation: bool = False
    hidden_size: int = 16
    num_layers: int = 1
    normalization: str = "BatchNorm1d"
    learning_rate: float = 0.001
    batch_size: int = 32
    patience: int = 50
    weight_decay: float = 1e-5
    stable_init: bool = False
    residual_fusion: bool = False
    residual_epsilon: float | None = None
    layer_norm: bool = False
    kl_lambda: float = 0.0
    smooth_lambda: float = 0.0
    transfer_learning: bool = False

    def validate(self) -> "FusionConfig":
        for key, expected in PAPER_DEFINED.items():
            if getattr(self, key) != expected:
                raise ValueError(f"论文固定参数 {key} 必须为 {expected!r}")
        allowed_sequences = {4, 6, 8, 10}
        if self.allow_fusion_seq_ablation:
            if self.fusion_seq_len not in allowed_sequences:
                raise ValueError("Phase 2 fusion_seq_len 只允许 4/6/8/10")
        elif self.fusion_seq_len != REPRO_DEFINED["fusion_seq_len"]:
            raise ValueError("非消融运行的 REPRO_DEFINED fusion_seq_len 必须固定为10")
        enhancements = {
            "stable_init": self.stable_init,
            "residual_fusion": self.residual_fusion,
            "layer_norm": self.layer_norm,
            "kl_regularization": self.kl_lambda != 0.0,
            "temporal_smoothing": self.smooth_lambda != 0.0,
            "transfer_learning": self.transfer_learning,
        }
        if self.track == ExperimentTrack.PAPER_FUSION and any(enhancements.values()):
            enabled = sorted(name for name, value in enhancements.items() if value)
            raise ValueError(f"PAPER_FUSION 禁止 enhancement: {enabled}")
        if self.track == ExperimentTrack.ENHANCEMENT:
            if not self.residual_fusion:
                raise ValueError("Phase 1 ENHANCEMENT 只允许 constrained residual fusion")
            if self.residual_epsilon not in {0.02, 0.05, 0.10}:
                raise ValueError("residual_epsilon 只允许 0.02/0.05/0.10")
            forbidden = (self.stable_init or self.layer_norm or self.kl_lambda != 0
                         or self.smooth_lambda != 0 or self.transfer_learning)
            if forbidden:
                raise ValueError("Phase 1 residual 对照禁止叠加其他 enhancement")
        return self

    def manifest(self) -> dict:
        value = asdict(self)
        value["track"] = self.track.value
        value["fusion_seq_len_status"] = "REPRO_DEFINED"
        value["fusion_seq_ablation"] = self.allow_fusion_seq_ablation
        value["l_weight_status"] = "UNVERIFIED_DISABLED"
        return value


PAPER_FUSION_CONFIG = FusionConfig(track=ExperimentTrack.PAPER_FUSION).validate()

PAPER_FIXED = {
    "scf_gan_source_batteries": ["B0005", "B0006"],
    "target_batteries": ["B0007", "B0018"],
    "synthetic_trajectories_per_target": 5,
    **PAPER_DEFINED, **REPRO_DEFINED,
    "trend_model": "original TimesNet", "seasonal_model": "original TimesNet",
    "residual_model": "iTransformer", "fusion_model": "Attention Bi-LSTM",
    "l_weight_source_status": "UNVERIFIED_DISABLED",
    "forbidden": [
        "fit scaler on target validation/test", "test-label offset calibration",
        "test-set hyperparameter selection", "OSELM", "causal multirate",
        "transfer learning", "LayerNorm", "stable initialization",
        "KL regularization", "temporal smoothing", "final SOH monotonic constraint",
    ],
}

# Retained only for old enhancement experiments. It is no longer described as
# a paper grid because it varies a paper-defined component window.
STAGES = {
    "A_representation": {
        "sequence_length": [8, 10, 12], "stl_period": [8, 12, 16],
        "timesnet_width": [32, 64], "timesnet_top_k": [2, 3],
        "itransformer_heads": [2, 4], "itransformer_layers": [1, 2],
    },
}

REPEAT_CONTROL = {
    "coarse_seed": 42, "promotion_seeds": [42, 52, 62],
    "final_validation_seeds": [42, 52, 62, 72, 82],
    "selection_metric": "legacy enhancement-grid validation RMSE",
}


def digest(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def build_stage(stage: str) -> list[dict]:
    tunable = STAGES[stage]
    keys = list(tunable)
    result = []
    for number, values in enumerate(itertools.product(*(tunable[k] for k in keys)), 1):
        record = {
            "schema": "enhancement_grid_config/3", "stage": stage,
            "track": ExperimentTrack.ENHANCEMENT.value,
            "paper_fixed": PAPER_FIXED, "tunable": dict(zip(keys, values)),
            "repeat_control": REPEAT_CONTROL,
            "data_boundary": "target prefix 20% train; validation selects; test remains unopened",
        }
        record["attempt_id"] = f"{stage[0]}{number:03d}"
        record["config_hash"] = digest(record)
        result.append(record)
    return result
