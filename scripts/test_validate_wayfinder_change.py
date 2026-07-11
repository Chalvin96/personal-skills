import importlib.util
import tempfile
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "validator", Path(__file__).with_name("validate-wayfinder-change.py")
)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(validator)


class ValidatorTest(unittest.TestCase):
    def make_change(self) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / "specs/cap").mkdir(parents=True)
        (root / "tickets").mkdir()
        (root / "tasks").mkdir()
        (root / "proposal.md").write_text("# Proposal\n")
        (root / "specs/cap/spec.md").write_text("### Requirement: R-001\n")
        (root / "tickets/index.md").write_text("# Tickets\n")
        (root / "tickets/D-001-choice.md").write_text(
            "---\nid: D-001\nstatus: CLOSED\nblocking: true\n"
            "depends_on: []\nintegrated: true\n---\n\n# Choice\n\n"
            "## Decision\n\nUse it.\n\n## Consequences\n\nIt applies.\n"
        )
        (root / "trd.md").write_text("# TRD\n\nD-001\n")
        (root / "tasks/C-01-build.md").write_text(
            "---\nid: C-01\ndepends_on: []\n---\n\n# Build\n\n"
            "## Outcome\n\nWorking increment.\n\n## Scope\n\nOne module.\n\n"
            "## Procedure\n\nImplement it.\n\n## Tests and verification\n\nRun tests.\n\n"
            "## Rollback\n\nRevert.\n\n## Stop conditions\n\nStop on drift.\n"
        )
        (root / "tasks.md").write_text("- [ ] C-01 Build\n")
        return root

    def test_valid_change(self):
        self.assertEqual([], validator.validate(self.make_change()))

    def test_rejects_unresolved_blocker(self):
        root = self.make_change()
        ticket = root / "tickets/D-001-choice.md"
        ticket.write_text(ticket.read_text().replace("CLOSED", "OPEN"))
        self.assertTrue(any("unresolved blocking" in e for e in validator.validate(root)))

    def test_rejects_cycle_checkbox(self):
        root = self.make_change()
        cycle = root / "tasks/C-01-build.md"
        cycle.write_text(cycle.read_text() + "\n- [ ] C-02 Wrong\n")
        self.assertTrue(any("checkboxes belong" in e for e in validator.validate(root)))


if __name__ == "__main__":
    unittest.main()
