#!/usr/bin/env python3
"""Unit tests for invoke_peer without contacting either model."""

from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock


MODULE_PATH = Path(__file__).with_name("invoke_peer.py")
sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location("invoke_peer", MODULE_PATH)
invoke_peer = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(invoke_peer)


def valid_report(phase: str, artifacts: list[str], verdict: str = "ACK") -> dict:
    return {
        "phase": phase,
        "reviewer": "independent test reviewer",
        "verdict": verdict,
        "summary": "A complete summary with enough detail for semantic validation.",
        "user_outcome_check": {
            "stated_outcome": "The user needs a complete dual-agent review workflow.",
            "actual_outcome": "The reviewed artifact implements the requested workflow.",
            "aligned": verdict == "ACK",
        },
        "contract_challenges": ["The contract was challenged against raw user words."],
        "findings": [] if verdict == "ACK" else [{
            "severity": "P1",
            "title": "blocking finding",
            "evidence": "concrete evidence",
            "required_action": "fix the issue",
        }],
        "verification": {
            "artifacts_inspected": artifacts,
            "tests_assessed": ["unit tests assessed"],
            "fresh_scan_completed": True,
        },
        "limitations": ["No live model was contacted by this unit test."],
    }


class InvokePeerTests(unittest.TestCase):
    def assert_blocked(self, expected_error: str, callable_under_test) -> None:
        output = io.StringIO()
        with redirect_stdout(output), self.assertRaises(SystemExit):
            callable_under_test()
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["verdict"], "BLOCKED")
        self.assertEqual(payload["error"], expected_error)

    def test_schema_and_semantic_ack(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifact = str(Path(directory).resolve())
            invoke_peer.validate_report(
                valid_report("final", [artifact]),
                expected_phase="final",
                expected_artifacts=[artifact],
            )

    def test_partial_schema_is_blocked(self) -> None:
        self.assert_blocked(
            "SCHEMA_REPORT_VALIDATION_FAILED",
            lambda: invoke_peer.validate_report(
                {"phase": "final", "verdict": "ACK"},
                expected_phase="final",
                expected_artifacts=["/tmp/missing"],
            ),
        )

    def test_all_manifest_artifacts_must_be_inspected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "one.txt"
            second = root / "two with space.txt"
            first.write_text("one")
            second.write_text("two")
            self.assert_blocked(
                "SEMANTIC_REPORT_VALIDATION_FAILED",
                lambda: invoke_peer.validate_report(
                    valid_report("implementation", [str(first)]),
                    expected_phase="implementation",
                    expected_artifacts=[str(first), str(second)],
                ),
            )

    def test_manifest_resolves_relative_and_space_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "two with space.txt"
            artifact.write_text("ok")
            handoff = f"""<raw_user_request>verbatim user request long enough</raw_user_request>
<artifact_manifest>
- two with space.txt
</artifact_manifest>
<validation_evidence>validation evidence is present</validation_evidence>
<known_gaps>known gaps are explicit</known_gaps>"""
            normalized = invoke_peer.normalize_manifest_paths(handoff, str(root))
            self.assertEqual(
                invoke_peer.validate_handoff(normalized),
                [str(artifact.resolve())],
            )

    def test_missing_manifest_artifact_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            handoff = f"""<raw_user_request>verbatim user request long enough</raw_user_request>
<artifact_manifest>
- {directory}/missing.txt
</artifact_manifest>
<validation_evidence>validation evidence is present</validation_evidence>
<known_gaps>known gaps are explicit</known_gaps>"""
            self.assert_blocked(
                "ARTIFACT_NOT_FOUND",
                lambda: invoke_peer.validate_handoff(handoff),
            )

    def test_invalid_session_option_is_blocked(self) -> None:
        self.assert_blocked(
            "INVALID_SESSION_ID",
            lambda: invoke_peer.validate_session_id(
                "--dangerously-bypass-approvals-and-sandbox"
            ),
        )

    def test_gate_order_and_cold_implementation(self) -> None:
        args = mock.Mock(phase="final", session_id=None)
        state = {
            "schemaVersion": 1,
            "workflowId": "w",
            "cwd": "/tmp/project",
            "peer": "claude",
            "gates": {},
        }
        self.assert_blocked(
            "GATE_ORDER_VIOLATION",
            lambda: invoke_peer.validate_gate_preconditions(
                args, "claude", "/tmp/project", state
            ),
        )

        state["gates"] = {
            "intent": {"verdict": "ACK", "sessionId": "00000000-0000-4000-8000-000000000001"},
            "plan": {"verdict": "ACK", "sessionId": "00000000-0000-4000-8000-000000000001"},
        }
        cold_args = mock.Mock(phase="implementation", session_id="00000000-0000-4000-8000-000000000001")
        self.assert_blocked(
            "COLD_IMPLEMENTATION_REVIEW_REQUIRED",
            lambda: invoke_peer.validate_gate_preconditions(
                cold_args, "claude", "/tmp/project", state
            ),
        )

    def test_gate_happy_path_and_atomic_state_write(self) -> None:
        session = "00000000-0000-4000-8000-000000000001"
        cwd = "/tmp/project"
        intent_args = mock.Mock(phase="intent", session_id=None)
        state = invoke_peer.validate_gate_preconditions(
            intent_args, "claude", cwd, None
        )
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "workflow.json"
            artifact = str(Path(directory).resolve())
            normalized = {
                "sessionId": session,
                "verdict": "ACK",
                "report": valid_report("intent", [artifact]),
            }
            invoke_peer.write_workflow(
                state_path,
                state,
                "intent",
                normalized,
            )
            loaded = invoke_peer.load_workflow(state_path)
            self.assertEqual(loaded["gates"]["intent"]["verdict"], "ACK")
            self.assertFalse(any(state_path.parent.glob(f".{state_path.name}.tmp-*")))

            plan_args = mock.Mock(phase="plan", session_id=session)
            invoke_peer.validate_gate_preconditions(
                plan_args,
                "claude",
                cwd,
                loaded,
            )

    def test_task_id_resolves_to_persistent_isolated_state(self) -> None:
        args = mock.Mock(state_file=None, task_id="feature-123")
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.dict(
                invoke_peer.os.environ,
                {"DUAL_AGENT_STATE_DIR": directory},
                clear=False,
            ):
                first = invoke_peer.resolve_state_path(args, "/project/one")
                second = invoke_peer.resolve_state_path(args, "/project/two")
        self.assertNotEqual(first.parent, second.parent)
        self.assertEqual(first.name, "feature-123.json")
        self.assertEqual(first.parents[1], Path(directory).resolve())

    def test_invalid_task_id_is_blocked(self) -> None:
        args = mock.Mock(state_file=None, task_id="../escape")
        self.assert_blocked(
            "INVALID_TASK_ID",
            lambda: invoke_peer.resolve_state_path(args, "/tmp/project"),
        )

    def test_claude_command_is_read_only_and_resumable(self) -> None:
        session = "00000000-0000-4000-8000-000000000001"
        args = mock.Mock(
            phase="implementation",
            session_id=session,
            add_dir=["/tmp/evidence"],
        )
        command = invoke_peer.build_claude_command(
            args,
            '{"type":"object"}',
            "(version 1) (allow default)",
        )
        self.assertEqual(command[:3], ["sandbox-exec", "-p", "(version 1) (allow default)"])
        self.assertIn("--safe-mode", command)
        self.assertIn("--strict-mcp-config", command)
        self.assertIn("--no-chrome", command)
        self.assertIn("Read,Grep,Glob", command)
        self.assertEqual(command[command.index("--resume") + 1], session)
        self.assertEqual(command[command.index("--add-dir") + 1], "/tmp/evidence")

    def test_codex_fresh_and_resume_commands_stay_read_only(self) -> None:
        session = "00000000-0000-4000-8000-000000000002"
        with tempfile.TemporaryDirectory() as directory:
            last = Path(directory) / "last.json"
            fresh_args = mock.Mock(cwd=directory, session_id=None)
            fresh = invoke_peer.build_codex_command(fresh_args, last)
            resume_args = mock.Mock(cwd=directory, session_id=session)
            resume = invoke_peer.build_codex_command(resume_args, last)
        for command in (fresh, resume):
            joined = " ".join(command)
            self.assertIn('sandbox_mode="read-only"', joined)
            self.assertIn('approval_policy="never"', joined)
            self.assertIn("--skip-git-repo-check", command)
            self.assertIn("--output-schema", command)
            self.assertEqual(command[-1], "-")
        self.assertEqual(resume[:4], ["codex", "exec", "resume", session])

    def test_main_blocks_when_peer_cli_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state_path = str(Path(directory) / "state.json")
            argv = [
                "invoke_peer.py",
                "--peer",
                "codex",
                "--phase",
                "intent",
                "--cwd",
                directory,
                "--state-file",
                state_path,
                "--prompt",
                "unused because binary validation runs first",
            ]
            with mock.patch.object(invoke_peer.sys, "argv", argv), mock.patch.object(
                invoke_peer.shutil,
                "which",
                return_value=None,
            ):
                self.assert_blocked("PEER_CLI_NOT_FOUND", invoke_peer.main)
            self.assertFalse(Path(state_path).exists())

    def test_main_blocks_on_peer_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            artifact = root / "artifact.txt"
            artifact.write_text("evidence")
            state_path = root / "state.json"
            handoff = f"""<raw_user_request>verbatim user request long enough</raw_user_request>
<artifact_manifest>
- {artifact}
</artifact_manifest>
<validation_evidence>validation evidence is present</validation_evidence>
<known_gaps>known gaps are explicit</known_gaps>"""
            argv = [
                "invoke_peer.py",
                "--peer",
                "codex",
                "--phase",
                "intent",
                "--cwd",
                str(root),
                "--state-file",
                str(state_path),
                "--prompt",
                handoff,
                "--timeout-seconds",
                "30",
            ]
            timeout = invoke_peer.subprocess.TimeoutExpired(
                cmd=["codex"],
                timeout=30,
            )
            with mock.patch.object(invoke_peer.sys, "argv", argv), mock.patch.object(
                invoke_peer.shutil,
                "which",
                return_value="/usr/local/bin/codex",
            ), mock.patch.object(
                invoke_peer.subprocess,
                "run",
                side_effect=timeout,
            ):
                self.assert_blocked("PEER_REVIEW_TIMEOUT", invoke_peer.main)
            self.assertFalse(state_path.exists())

    def test_parse_claude_real_shape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifact = str(Path(directory).resolve())
            report = valid_report("implementation", [artifact])
            payload = {
                "is_error": False,
                "session_id": "00000000-0000-4000-8000-000000000001",
                "structured_output": report,
                "modelUsage": {"claude-opus-5": {}},
            }
            session, model, parsed = invoke_peer.parse_claude(
                json.dumps(payload),
                expected_phase="implementation",
                expected_artifacts=[artifact],
            )
            self.assertEqual(session, payload["session_id"])
            self.assertEqual(model, "claude-opus-5")
            self.assertEqual(parsed, report)

    def test_parse_codex_real_shape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = str(root.resolve())
            report = valid_report("implementation", [artifact])
            last = root / "last.json"
            last.write_text(json.dumps(report))
            stdout = json.dumps({
                "type": "thread.started",
                "thread_id": "00000000-0000-4000-8000-000000000002",
            })
            session, _model, parsed = invoke_peer.parse_codex(
                stdout,
                last,
                expected_phase="implementation",
                expected_artifacts=[artifact],
            )
            self.assertEqual(session, "00000000-0000-4000-8000-000000000002")
            self.assertEqual(parsed, report)


if __name__ == "__main__":
    unittest.main()
