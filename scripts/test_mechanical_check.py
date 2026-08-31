import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


K_CHECKER = (
    Path(__file__).parents[1]
    / "skills"
    / "ume-conventions"
    / "scripts"
    / "mechanical_check.py"
)


class MechanicalCheckSuppressionTest(unittest.TestCase):
    def run_checker(self, source: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "unsafe.py"
            target.write_text(source, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(K_CHECKER), "--root", str(root), target.name],
                capture_output=True,
                check=False,
                text=True,
            )

    def test_bare_noqa_does_not_suppress_ume_rule(self):
        result = self.run_checker("result = eval(payload)  # noqa\n")

        self.assertEqual(1, result.returncode)
        self.assertIn("UME-SEC001", result.stdout)

    def test_matching_noqa_rule_suppresses_finding(self):
        result = self.run_checker("result = eval(payload)  # noqa: UME-SEC001\n")

        self.assertEqual(0, result.returncode)
        self.assertEqual("No mechanical findings.\n", result.stdout)

    def test_unrelated_noqa_rule_does_not_suppress_finding(self):
        result = self.run_checker("result = eval(payload)  # noqa: UME-PY001\n")

        self.assertEqual(1, result.returncode)
        self.assertIn("UME-SEC001", result.stdout)

    def test_matching_ume_ignore_suppresses_finding(self):
        result = self.run_checker(
            "# ume-ignore: UME-SEC001\n"
            "result = eval(payload)\n"
        )

        self.assertEqual(0, result.returncode)
        self.assertEqual("No mechanical findings.\n", result.stdout)

    def test_bare_ume_ignore_does_not_suppress_finding(self):
        result = self.run_checker(
            "# ume-ignore\n"
            "result = eval(payload)\n"
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("UME-SEC001", result.stdout)

    def test_unrelated_ume_ignore_rule_does_not_suppress_finding(self):
        result = self.run_checker(
            "# ume-ignore: UME-PY001\n"
            "result = eval(payload)\n"
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("UME-SEC001", result.stdout)


if __name__ == "__main__":
    unittest.main()
