#!/usr/bin/env python3
"""Unit tests for atomic Skill distribution."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


sys.dont_write_bytecode = True
MODULE_PATH = Path(__file__).with_name("install_skill.py")
SPEC = importlib.util.spec_from_file_location("install_skill", MODULE_PATH)
install_skill = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(install_skill)


def create_skill(path: Path, marker: str) -> None:
    (path / "scripts" / "__pycache__").mkdir(parents=True)
    (path / "SKILL.md").write_text(f"skill {marker}")
    (path / "scripts" / "tool.py").write_text(f"tool {marker}")
    (path / "scripts" / "__pycache__" / "tool.pyc").write_bytes(b"generated")


class InstallSkillTests(unittest.TestCase):
    def test_install_and_update_exclude_generated_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source" / "dual-agent-collaboration"
            target_one = root / "codex" / "dual-agent-collaboration"
            target_two = root / "claude" / "dual-agent-collaboration"
            create_skill(source, "v1")

            result = install_skill.install(
                source,
                [target_one, target_two],
                dry_run=False,
            )
            self.assertEqual(result["status"], "installed")
            self.assertFalse((target_one / "scripts" / "__pycache__").exists())
            self.assertEqual(
                install_skill.content_manifest(target_one),
                install_skill.content_manifest(source),
            )

            (source / "SKILL.md").write_text("skill v2")
            install_skill.install(
                source,
                [target_one, target_two],
                dry_run=False,
            )
            self.assertEqual((target_one / "SKILL.md").read_text(), "skill v2")
            self.assertEqual((target_two / "SKILL.md").read_text(), "skill v2")

    def test_second_target_failure_rolls_back_first(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source" / "dual-agent-collaboration"
            target_one = root / "codex" / "dual-agent-collaboration"
            target_two = root / "claude" / "dual-agent-collaboration"
            create_skill(source, "new")
            create_skill(target_one, "old")
            create_skill(target_two, "old")
            original_replace = install_skill.os.replace

            def fail_second_stage(source_path, target_path):
                source_value = str(source_path)
                target_value = str(target_path)
                if ".stage-" in source_value and target_value == str(target_two):
                    raise OSError("simulated second target failure")
                return original_replace(source_path, target_path)

            with mock.patch.object(
                install_skill.os,
                "replace",
                side_effect=fail_second_stage,
            ), self.assertRaises(OSError):
                install_skill.install(
                    source,
                    [target_one, target_two],
                    dry_run=False,
                )

            self.assertEqual((target_one / "SKILL.md").read_text(), "skill old")
            self.assertEqual((target_two / "SKILL.md").read_text(), "skill old")
            self.assertFalse(any(root.rglob("*.stage-*")))
            self.assertFalse(any(root.rglob("*.backup-*")))


if __name__ == "__main__":
    unittest.main()
