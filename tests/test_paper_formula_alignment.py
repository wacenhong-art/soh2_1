import importlib.util
import unittest
from pathlib import Path

import numpy as np
import torch


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


hf = load("formula_hf", ROOT / "scripts" / "01_extract_hf.py")
gan = load("formula_gan", ROOT / "scripts" / "02_scf_gan.py")
ts = load("formula_ts", ROOT / "scripts" / "03_time_series.py")
fusion = load("formula_fusion", ROOT / "scripts" / "04_attention_fusion.py")


class CountingInception(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.calls = 0

    def forward(self, x):
        self.calls += 1
        return x


class PaperFormulaAlignmentTests(unittest.TestCase):
    def test_eq_1_to_3_health_feature_intervals(self):
        voltage = np.array([3.0, 3.6, 3.8, 4.0, 4.2, 4.2])
        current = np.array([1.5, 1.5, 1.5, 1.5, 1.0, 0.01])
        time = np.array([0.0, 10.0, 20.0, 30.0, 40.0, 50.0])
        self.assertEqual(hf.calc_h_features(voltage, current, time), (40.0, 10.0, 10.0))

    def test_eq_7_generator_uses_leaky_relu(self):
        model = gan.Generator()
        self.assertIsInstance(model.leaky, torch.nn.LeakyReLU)
        self.assertFalse(hasattr(model.fc1, "weight_orig"))

    def test_eq_9_to_11_discriminator_uses_spectral_normalization(self):
        model = gan.Discriminator()
        self.assertTrue(hasattr(model.fc1, "weight_orig"))
        self.assertTrue(hasattr(model.out, "weight_orig"))

    def test_eq_12_feature_matching_is_expected_squared_l2(self):
        fake = torch.tensor([[1.0, 2.0], [3.0, 5.0]])
        real = torch.tensor([[0.0, 0.0], [1.0, 2.0]])
        expected = ((1.0 ** 2 + 2.0 ** 2) + (2.0 ** 2 + 3.0 ** 2)) / 2
        self.assertAlmostEqual(float(gan.feature_matching_loss(fake, real)), expected)

    def test_eq_18_to_20_process_every_top_k_period(self):
        model = ts.TimesNet(input_dim=3, d_model=6, top_k=3).eval()
        counter = CountingInception()
        model.inception = counter
        signal = torch.arange(36, dtype=torch.float32).reshape(1, 12, 3)
        with torch.no_grad():
            output = model(signal)
        self.assertEqual(counter.calls, 3)
        self.assertEqual(tuple(output.shape), (1, 1))

    def test_eq_17_split_stl_reconstructs_without_test_influence(self):
        soh = 90.0 - np.linspace(0.0, 6.0, 72) + 0.2 * np.sin(np.arange(72))
        components = ts.split_stl_components(soh, 36, 54, period=6)
        reconstructed = components["Trend"] + components["Seasonal"] + components["Residual"]
        np.testing.assert_allclose(reconstructed, soh, atol=1e-5)

        changed_test = soh.copy()
        changed_test[54:] += 100.0
        changed = ts.split_stl_components(changed_test, 36, 54, period=6)
        for name in ("Trend", "Seasonal", "Residual"):
            np.testing.assert_allclose(changed[name][:36], components[name][:36], atol=1e-6)

    def test_eq_23_projects_each_token_before_aggregation(self):
        model = ts.iTransformer(seq_len=10, d_model=8, nhead=2, layers=1).eval()
        x = torch.randn(2, 10, 3)
        with torch.no_grad():
            tokens = model.temporal_proj(x.permute(0, 2, 1))
            expected = model.output(model.encoder(tokens)).mean(dim=1)
            actual = model(x)
        torch.testing.assert_close(actual, expected)

    def test_eq_25_component_attention_uses_softmax_theta(self):
        attention = fusion.ComponentAttention(3)
        with torch.no_grad():
            attention.theta_c.copy_(torch.tensor([0.0, 1.0, 2.0]))
        x = torch.ones(2, 4, 3)
        expected = torch.softmax(attention.theta_c, dim=0).view(1, 1, 3).expand_as(x)
        torch.testing.assert_close(attention(x), expected)

    def test_eq_28_uses_raw_weighted_components(self):
        model = fusion.AttentionBiLSTMFusion(
            np.array([70.0, 1.0, 0.0]), np.ones(3), 71.0, 8.0,
            fusion_mode="paper", stable_init=True,
        ).eval()
        component = torch.tensor([[75.0, 3.0, 1.0]])
        with torch.no_grad():
            prediction_z, weights = model(
                torch.zeros(1, fusion.SEQ_LEN, 9), component
            )
        torch.testing.assert_close(weights, torch.full((1, 3), 1 / 3))
        torch.testing.assert_close(prediction_z, torch.tensor([[1.0]]))

    def test_repro_defined_weight_loss_is_zero_for_balanced_batch_usage(self):
        uniform = torch.full((4, 3), 1 / 3)
        complementary = torch.tensor([
            [0.98, 0.01, 0.01],
            [0.01, 0.98, 0.01],
            [0.01, 0.01, 0.98],
        ])
        self.assertAlmostEqual(float(fusion.weight_regularization(uniform)), 0.0, places=6)
        self.assertAlmostEqual(float(fusion.weight_regularization(complementary)), 0.0, places=6)

    def test_repro_defined_weight_loss_penalizes_branch_starvation(self):
        starved = torch.tensor([[0.90, 0.09, 0.01]]).repeat(5, 1)
        self.assertGreater(float(fusion.weight_regularization(starved)), 0.5)
        self.assertEqual(fusion.L_WEIGHT_STATUS, "REPRO_DEFINED_NOT_PAPER_ORIGINAL")


if __name__ == "__main__":
    unittest.main()
