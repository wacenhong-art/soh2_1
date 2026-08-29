import importlib.util
import unittest
from pathlib import Path

import numpy as np
import torch

from soh_pipeline.protocol import ExperimentTrack, FusionConfig, PAPER_FUSION_CONFIG


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


fusion = load("phase1_fusion", ROOT / "scripts" / "04_attention_fusion.py")
runner = load("phase1_runner", ROOT / "scripts" / "65_phase1_failure_isolation.py")


class Phase1FailureIsolationTests(unittest.TestCase):
    def test_paper_contract_is_locked(self):
        PAPER_FUSION_CONFIG.validate()
        self.assertEqual(PAPER_FUSION_CONFIG.component_window, 10)
        self.assertEqual(PAPER_FUSION_CONFIG.fusion_seq_len, 10)
        self.assertEqual(PAPER_FUSION_CONFIG.hidden_size, 16)
        self.assertEqual(PAPER_FUSION_CONFIG.patience, 50)
        self.assertEqual(PAPER_FUSION_CONFIG.kl_lambda, 0.0)

    def test_paper_track_rejects_every_enhancement(self):
        with self.assertRaises(ValueError):
            FusionConfig(track=ExperimentTrack.PAPER_FUSION, residual_fusion=True).validate()
        with self.assertRaises(ValueError):
            FusionConfig(track=ExperimentTrack.PAPER_FUSION, kl_lambda=0.01).validate()
        with self.assertRaises(ValueError):
            FusionConfig(track=ExperimentTrack.PAPER_FUSION, layer_norm=True).validate()

    def test_phase1_enhancement_rejects_unregistered_epsilon(self):
        with self.assertRaises(ValueError):
            FusionConfig(
                track=ExperimentTrack.ENHANCEMENT,
                residual_fusion=True, residual_epsilon=0.03,
            ).validate()

    def test_residual_correction_obeys_epsilon_bound(self):
        epsilon = 0.02
        model = fusion.AttentionBiLSTMFusion(
            np.zeros(3), np.ones(3), 80.0, 5.0,
            fusion_mode="residual", residual_epsilon=epsilon,
        ).eval()
        x = torch.randn(8, fusion.SEQ_LEN, 9)
        comp = torch.randn(8, 3) + torch.tensor([80.0, 1.0, 0.0])
        with torch.no_grad():
            pred_z, _ = model(x, comp)
        prediction = pred_z * 5.0 + 80.0
        delta = prediction - comp.sum(dim=1, keepdim=True)
        self.assertTrue(torch.all(torch.abs(delta) <= epsilon * 100 + 1e-6))

    def test_runtime_contract_disables_unverified_weight_loss(self):
        runner.assert_runtime_contract()
        self.assertEqual(fusion.LAMBDA_WEIGHT, 0.0)

    def test_phase1_seed_and_battery_contract(self):
        self.assertEqual(runner.SEEDS, (42, 123, 2024, 3407, 7777))
        self.assertEqual(runner.BATTERIES, ("B0007", "B0018"))
        self.assertEqual(runner.EPSILONS, (0.02, 0.05, 0.10))


if __name__ == "__main__":
    unittest.main()
