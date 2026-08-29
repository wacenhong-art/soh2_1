import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_grid():
    spec = importlib.util.spec_from_file_location(
        "grid_800_contract", ROOT / "scripts" / "64_train_800_grid.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


grid = load_grid()


class Grid800ContractTests(unittest.TestCase):
    def test_coarse_grid_is_compact_and_unique(self):
        records = grid.coarse_records()
        self.assertEqual(len(records), 18)
        self.assertEqual(len({r["config_id"] for r in records}), 18)

    def test_every_config_locks_test_and_uses_800_epoch_cap(self):
        for record in grid.coarse_records():
            self.assertEqual(record["training"]["max_epochs"], 800)
            self.assertFalse(record["data_boundary"]["test_loaded"])
            self.assertEqual(record["data_boundary"]["target_train_prefix"], 0.20)

    def test_l_weight_is_not_claimed_as_paper_original(self):
        for record in grid.coarse_records():
            self.assertFalse(record["l_weight"]["paper_definition_disclosed"])
            self.assertEqual(
                record["l_weight"]["status"], "REPRO_DEFINED_NOT_PAPER_ORIGINAL"
            )


if __name__ == "__main__":
    unittest.main()
