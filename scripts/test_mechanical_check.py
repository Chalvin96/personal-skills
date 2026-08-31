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
    def run_checker(
        self,
        source: str,
        filename: str = "unsafe.py",
        extra_files: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source, encoding="utf-8")
            for relative, content in (extra_files or {}).items():
                extra = root / relative
                extra.parent.mkdir(parents=True, exist_ok=True)
                extra.write_text(content, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(K_CHECKER), "--root", str(root), filename],
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

    def test_local_dynamic_private_access_is_not_cross_module_access(self):
        result = self.run_checker('value = getattr(self, "_value")\n')

        self.assertEqual(0, result.returncode)
        self.assertEqual("No mechanical findings.\n", result.stdout)

    def test_imported_dynamic_private_access_is_reported(self):
        result = self.run_checker(
            "import package\n"
            'value = getattr(package, "_value")\n'
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("UME-PY002", result.stdout)


class FrameworkEvidenceTest(unittest.TestCase):
    def run_checker(
        self,
        source: str,
        filename: str = "module.py",
        extra_files: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source, encoding="utf-8")
            for relative, content in (extra_files or {}).items():
                extra = root / relative
                extra.parent.mkdir(parents=True, exist_ok=True)
                extra.write_text(content, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(K_CHECKER), "--root", str(root), filename],
                capture_output=True,
                check=False,
                text=True,
            )

    def test_plain_python_query_method_is_not_sqlalchemy_finding(self):
        result = self.run_checker("records = builder.query()\n")

        self.assertEqual(0, result.returncode)

    def test_sqlalchemy_import_enables_query_check(self):
        result = self.run_checker(
            "from sqlalchemy import select\n"
            "records = builder.query()\n"
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("UME-SA001", result.stdout)

    def test_sqlalchemy_dependency_enables_query_check(self):
        result = self.run_checker(
            "records = builder.query()\n",
            extra_files={"requirements.txt": "SQLAlchemy>=2\n"},
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("UME-SA001", result.stdout)

    def test_plain_route_decorator_is_not_fastapi_finding(self):
        result = self.run_checker(
            '@app.get("/")\n'
            "def read(db):\n"
            "    db.commit()\n"
        )

        self.assertEqual(0, result.returncode)

    def test_fastapi_import_enables_route_check(self):
        result = self.run_checker(
            "from fastapi import FastAPI\n"
            "app = FastAPI()\n"
            '@app.get("/")\n'
            "def read(db):\n"
            "    db.commit()\n"
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("UME-FAPI001", result.stdout)

    def test_fastapi_dependency_enables_route_check(self):
        result = self.run_checker(
            '@app.get("/")\n'
            "def read(db):\n"
            "    db.commit()\n",
            extra_files={"requirements.txt": "fastapi>=0.1\n"},
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("UME-FAPI001", result.stdout)

    def test_plain_typescript_hook_expression_is_not_react_finding(self):
        result = self.run_checker("const value = compose(useValue());\n", "module.ts")

        self.assertEqual(0, result.returncode)

    def test_react_import_enables_hook_check(self):
        result = self.run_checker(
            'import { useValue } from "react";\n'
            "const value = compose(useValue());\n",
            "module.ts",
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("UME-REACT001", result.stdout)

    def test_react_dependency_enables_hook_check(self):
        result = self.run_checker(
            "const value = compose(useValue());\n",
            "module.ts",
            extra_files={"package.json": '{"dependencies":{"react":"^19.0.0"}}\n'},
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("UME-REACT001", result.stdout)

    def test_client_checks_are_limited_to_client_modules(self):
        result = self.run_checker(
            "import requests\n"
            "requests.get(\"/health\", timeout=1)\n",
            "manager.py",
        )

        self.assertEqual(0, result.returncode)

    def test_client_manager_transport_check_has_client_path_evidence(self):
        result = self.run_checker(
            "import requests\n",
            "clients/acme/manager.py",
            extra_files={
                "app.py": "from fastapi import FastAPI\n",
                "clients/acme/api.py": "",
                "clients/acme/config.py": "",
            },
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("UME-FAPI003", result.stdout)

    def test_client_manager_transport_check_requires_fastapi_evidence(self):
        result = self.run_checker(
            "import requests\n",
            "clients/acme/manager.py",
            extra_files={
                "clients/acme/api.py": "",
                "clients/acme/config.py": "",
            },
        )

        self.assertEqual(0, result.returncode)

    def test_client_layout_requires_fastapi_evidence(self):
        result = self.run_checker("", "clients/acme/api.py")

        self.assertEqual(0, result.returncode)

    def test_client_layout_is_checked_with_fastapi_evidence(self):
        result = self.run_checker(
            "",
            "clients/acme/api.py",
            extra_files={"app.py": "from fastapi import FastAPI\n"},
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("UME-FAPI002", result.stdout)


class ConstantScopeTest(unittest.TestCase):
    def run_checker(self, filename: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("EXPECTED = 1\n", encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(K_CHECKER), "--root", str(root), filename],
                capture_output=True,
                check=False,
                text=True,
            )

    def test_test_module_at_repository_root_is_exempt(self):
        result = self.run_checker("test_demo.py")

        self.assertEqual(0, result.returncode)

    def test_nested_test_module_outside_tests_is_exempt(self):
        result = self.run_checker("package/test_demo.py")

        self.assertEqual(0, result.returncode)

    def test_unit_test_module_under_tests_is_exempt(self):
        result = self.run_checker("tests/unit/fixtures.py")

        self.assertEqual(0, result.returncode)

    def test_production_module_still_requires_k_prefix(self):
        result = self.run_checker("package/config.py")

        self.assertEqual(1, result.returncode)
        self.assertIn("UME-PY006", result.stdout)

    def test_integration_test_still_requires_k_prefix(self):
        result = self.run_checker("tests/integration/test_demo.py")

        self.assertEqual(1, result.returncode)
        self.assertIn("UME-PY006", result.stdout)


if __name__ == "__main__":
    unittest.main()
