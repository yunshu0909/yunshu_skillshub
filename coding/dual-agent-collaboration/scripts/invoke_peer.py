#!/usr/bin/env python3
"""Invoke Claude Code or Codex as a read-only peer reviewer.

The wrapper gives both CLIs the same review contract, structured output schema,
session continuation, recursion protection, and normalized JSON result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone
import shutil
import subprocess
import sys
import tempfile
import re
from typing import Any
import uuid


SKILL_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = SKILL_ROOT / "references" / "review-output.schema.json"
PHASES = ("intent", "plan", "implementation", "final")
PEERS = ("auto", "claude", "codex")
HANDOFF_MARKERS = (
    "raw_user_request",
    "artifact_manifest",
    "validation_evidence",
    "known_gaps",
)
PLACEHOLDER_TEXT = (
    "按时间顺序逐字保留",
    "/absolute/project/root",
    "path/to/plan.md",
    "path/to/diff.patch",
    "Intent contract / plan / diff：",
    "尚未验证：",
)
STATE_SCHEMA_VERSION = 1
GATE_ORDER = ("intent", "plan", "implementation", "final")


def fail(message: str, *, details: str | None = None, code: int = 2) -> None:
    payload: dict[str, Any] = {
        "status": "error",
        "verdict": "BLOCKED",
        "error": message,
    }
    if details:
        payload["details"] = details[-4000:]
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(code)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Invoke the opposite CLI model as a structured read-only reviewer."
    )
    parser.add_argument("--peer", choices=PEERS, default="auto")
    parser.add_argument("--phase", choices=PHASES, required=True)
    parser.add_argument("--cwd", required=True, help="Trusted project root for peer inspection")
    state_group = parser.add_mutually_exclusive_group(required=True)
    state_group.add_argument(
        "--state-file",
        help="Explicit machine-readable workflow state path",
    )
    state_group.add_argument(
        "--task-id",
        help=(
            "Stable per-task id; stores state outside the repository in the "
            "user state directory"
        ),
    )
    parser.add_argument(
        "--add-dir",
        action="append",
        default=[],
        help="Additional read-only evidence directory for Claude (repeatable)",
    )
    prompt_group = parser.add_mutually_exclusive_group()
    prompt_group.add_argument("--prompt-file")
    prompt_group.add_argument("--prompt")
    parser.add_argument("--session-id", help="Resume an existing peer review session")
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--save-raw", help="Directory for raw CLI stdout/stderr")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def detect_peer(requested: str) -> str:
    if os.environ.get("DUAL_AGENT_PEER") == "1":
        fail("RECURSIVE_PEER_INVOCATION_BLOCKED")
    if requested != "auto":
        return requested

    in_claude = os.environ.get("CLAUDECODE") == "1"
    in_codex = bool(os.environ.get("CODEX_THREAD_ID"))
    if in_claude and not in_codex:
        return "codex"
    if in_codex and not in_claude:
        return "claude"
    if in_claude and in_codex:
        fail("AMBIGUOUS_PRIMARY_AGENT", details="Specify --peer claude or --peer codex.")
    fail("PRIMARY_AGENT_NOT_DETECTED", details="Specify --peer claude or --peer codex.")
    raise AssertionError("unreachable")


def load_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        path = Path(args.prompt_file).expanduser().resolve()
        if not path.is_file():
            fail("PROMPT_FILE_NOT_FOUND", details=str(path))
        prompt = path.read_text(encoding="utf-8")
    elif args.prompt is not None:
        prompt = args.prompt
    elif not sys.stdin.isatty():
        prompt = sys.stdin.read()
    else:
        fail("PROMPT_REQUIRED")
        raise AssertionError("unreachable")

    if not prompt.strip():
        fail("PROMPT_REQUIRED")
    return prompt


def resolve_state_path(args: argparse.Namespace, cwd: str) -> Path:
    if args.state_file:
        return Path(args.state_file).expanduser().resolve()

    task_id = args.task_id
    if (
        not isinstance(task_id, str)
        or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,79}", task_id)
        or ".." in task_id
    ):
        fail(
            "INVALID_TASK_ID",
            details="Use 3-80 characters: letters, digits, dot, underscore, hyphen.",
        )

    configured_root = os.environ.get("DUAL_AGENT_STATE_DIR")
    if configured_root:
        root = Path(configured_root).expanduser().resolve()
    elif sys.platform == "darwin":
        root = (
            Path.home()
            / "Library"
            / "Application Support"
            / "CodePal"
            / "dual-agent-workflows"
        )
    elif os.environ.get("XDG_STATE_HOME"):
        root = (
            Path(os.environ["XDG_STATE_HOME"]).expanduser()
            / "codepal"
            / "dual-agent-workflows"
        )
    else:
        root = Path.home() / ".local" / "state" / "codepal" / "dual-agent-workflows"

    project_key = hashlib.sha256(cwd.encode("utf-8")).hexdigest()[:16]
    return (root / project_key / f"{task_id}.json").resolve()


def marker_content(handoff: str, marker: str) -> str:
    match = re.search(
        rf"<{marker}>\s*(.*?)\s*</{marker}>",
        handoff,
        flags=re.DOTALL,
    )
    return match.group(1).strip() if match else ""


def extract_manifest_paths(handoff: str) -> list[str]:
    manifest = marker_content(handoff, "artifact_manifest")
    paths = []
    for raw_line in manifest.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if not line.startswith("- "):
            fail(
                "INCOMPLETE_HANDOFF",
                details="Every artifact_manifest entry must be a '- path' line.",
            )
        value = line[2:].strip().strip("`\"'")
        candidate = Path(value).expanduser()
        if not candidate.is_absolute():
            fail(
                "INCOMPLETE_HANDOFF",
                details=f"artifact_manifest path must be absolute before validation: {value}",
            )
        if not candidate.exists():
            fail("ARTIFACT_NOT_FOUND", details=str(candidate))
        paths.append(str(candidate.resolve()))
    return sorted(set(paths))


def validate_handoff(handoff: str) -> list[str]:
    for marker in HANDOFF_MARKERS:
        content = marker_content(handoff, marker)
        if len(content) < 10:
            fail(
                "INCOMPLETE_HANDOFF",
                details=f"Missing or empty <{marker}>...</{marker}> section.",
            )
        if any(placeholder in content for placeholder in PLACEHOLDER_TEXT):
            fail(
                "INCOMPLETE_HANDOFF",
                details=f"Placeholder text remains in <{marker}> section.",
            )
    manifest_paths = extract_manifest_paths(handoff)
    if not manifest_paths:
        fail(
            "INCOMPLETE_HANDOFF",
            details="artifact_manifest must include at least one existing absolute path.",
        )
    return manifest_paths


def normalize_manifest_paths(handoff: str, cwd: str) -> str:
    """Resolve relative manifest entries before validation without changing other text."""
    manifest = marker_content(handoff, "artifact_manifest")
    normalized_lines = []
    for raw_line in manifest.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if not line.startswith("- "):
            normalized_lines.append(line)
            continue
        value = line[2:].strip().strip("`\"'")
        candidate = Path(value).expanduser()
        if not candidate.is_absolute():
            candidate = Path(cwd) / candidate
        normalized_lines.append(f"- {candidate.resolve()}")
    normalized = "\n".join(normalized_lines)
    return re.sub(
        r"<artifact_manifest>\s*.*?\s*</artifact_manifest>",
        f"<artifact_manifest>\n{normalized}\n</artifact_manifest>",
        handoff,
        flags=re.DOTALL,
    )


def is_within(path: str, directory: str) -> bool:
    candidate = Path(path).resolve()
    root = Path(directory).resolve()
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def validate_artifact_access(
    peer: str,
    manifest_paths: list[str],
    cwd: str,
    add_dirs: list[str],
) -> None:
    # Codex read-only sandbox blocks writes but permits absolute-path reads.
    # Claude constrains filesystem tools to cwd/add-dir roots, so only that
    # peer needs an explicit scope preflight.
    if peer == "codex":
        return
    allowed = [cwd, *add_dirs]
    inaccessible = [
        path for path in manifest_paths
        if not any(is_within(path, directory) for directory in allowed)
    ]
    if inaccessible:
        fail(
            "ARTIFACT_OUTSIDE_CLAUDE_READ_SCOPE",
            details=(
                "Pass --add-dir for each external evidence directory: "
                + ", ".join(inaccessible)
            ),
        )


def reviewer_prompt(phase: str, handoff: str) -> str:
    return f"""You are the independent peer reviewer in a Codex × Claude Code collaboration.

Review phase: {phase}

Hard rules:
1. Do not edit, create, delete, stage, commit, push, deploy, or otherwise mutate files or external state.
2. Do not invoke another model, subagent, peer CLI, or this collaboration skill.
3. Inspect the raw user request and named artifacts directly. Do not trust the primary agent's summary alone.
4. First test whether the stated contract matches the user's actual desired outcome. A technically correct implementation of the wrong contract must be NOT_ACK.
5. Separate verified facts, inferences, and assumptions. Cite concrete files, behavior, commands, or missing evidence.
6. For implementation/final review, inspect relevant diff, source, tests, failure paths, and user-visible behavior. Recheck old findings and perform a fresh scan.
7. Do not end with a plan, tool request, or vague advice. Finish this turn with the required structured verdict.
8. ACK only when evidence is sufficient and there are no unresolved P0/P1 findings. Use BLOCKED when evidence or authority is missing.
9. The <raw_user_request> section must contain the user's verbatim words. If it is a paraphrase or insufficient to verify intent, return NOT_ACK or BLOCKED.
10. If any artifact in <artifact_manifest> cannot be read because of permissions or path scope, return BLOCKED. Never silently review a subset.

The output schema is enforced by the caller. Keep findings precise and actionable.

--- PRIMARY HANDOFF START ---
{handoff}
--- PRIMARY HANDOFF END ---
"""


def requested_model(peer: str) -> str:
    if peer == "claude":
        return os.environ.get("DUAL_AGENT_CLAUDE_MODEL", "opus")
    return os.environ.get("DUAL_AGENT_CODEX_MODEL", "configured-default")


def sandbox_profile(paths: list[str]) -> str:
    def quote(value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"')

    denied = " ".join(f'(subpath "{quote(path)}")' for path in paths)
    return f"(version 1) (allow default) (deny file-write* {denied})"


def build_claude_command(
    args: argparse.Namespace,
    schema_text: str,
    profile: str | None,
) -> list[str]:
    model = os.environ.get("DUAL_AGENT_CLAUDE_MODEL", "opus")
    effort = os.environ.get("DUAL_AGENT_CLAUDE_EFFORT", "max")
    claude_command = [
        "claude",
        "--print",
        "--model",
        model,
        "--effort",
        effort,
        "--permission-mode",
        "dontAsk",
        "--safe-mode",
        "--tools",
        "Read,Grep,Glob",
        "--strict-mcp-config",
        "--no-chrome",
        "--output-format",
        "json",
        "--json-schema",
        schema_text,
        "--name",
        f"dual-agent-{args.phase}",
    ]
    if args.session_id:
        claude_command.extend(["--resume", args.session_id])
    for directory in args.add_dir:
        claude_command.extend(["--add-dir", directory])
    if profile is None:
        return claude_command
    return ["sandbox-exec", "-p", profile, *claude_command]


def build_codex_command(
    args: argparse.Namespace,
    last_message_path: Path,
) -> list[str]:
    model = os.environ.get("DUAL_AGENT_CODEX_MODEL")
    reasoning = os.environ.get("DUAL_AGENT_CODEX_REASONING", "max")
    if args.session_id:
        command = ["codex", "exec", "resume", args.session_id]
        if model:
            command.extend(["--model", model])
        command.extend(
            [
                "--config",
                f'model_reasoning_effort="{reasoning}"',
                "--config",
                'sandbox_mode="read-only"',
                "--config",
                'approval_policy="never"',
                "--skip-git-repo-check",
                "--output-schema",
                str(SCHEMA_PATH),
                "--json",
                "--output-last-message",
                str(last_message_path),
                "-",
            ]
        )
        return command

    command = [
        "codex",
        "exec",
        "--cd",
        args.cwd,
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
        "--config",
        f'model_reasoning_effort="{reasoning}"',
        "--config",
        'sandbox_mode="read-only"',
        "--config",
        'approval_policy="never"',
        "--output-schema",
        str(SCHEMA_PATH),
        "--json",
        "--output-last-message",
        str(last_message_path),
    ]
    if model:
        command.extend(["--model", model])
    command.append("-")
    return command


def safe_command(command: list[str]) -> list[str]:
    safe = []
    skip_next = False
    for index, value in enumerate(command):
        if skip_next:
            safe.append("<schema>")
            skip_next = False
            continue
        safe.append(value)
        if value == "--json-schema":
            skip_next = True
    return safe


def parse_structured(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict) and value.get("verdict") in {"ACK", "NOT_ACK", "BLOCKED"}:
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return None
        if isinstance(parsed, dict) and parsed.get("verdict") in {"ACK", "NOT_ACK", "BLOCKED"}:
            return parsed
    return None


def validate_json_schema(instance: Any, schema: dict[str, Any], path: str = "$") -> None:
    expected_type = schema.get("type")
    type_map = {
        "object": dict,
        "array": list,
        "string": str,
        "boolean": bool,
    }
    if expected_type:
        expected = type_map.get(expected_type)
        if expected is None:
            fail("UNSUPPORTED_LOCAL_SCHEMA", details=f"{path}: {expected_type}")
        if expected_type == "boolean":
            valid_type = isinstance(instance, bool)
        else:
            valid_type = isinstance(instance, expected) and not (
                expected_type != "boolean" and isinstance(instance, bool)
            )
        if not valid_type:
            fail(
                "SCHEMA_REPORT_VALIDATION_FAILED",
                details=f"{path}: expected {expected_type}",
            )

    if "enum" in schema and instance not in schema["enum"]:
        fail("SCHEMA_REPORT_VALIDATION_FAILED", details=f"{path}: value outside enum")
    if isinstance(instance, str) and len(instance) < schema.get("minLength", 0):
        fail("SCHEMA_REPORT_VALIDATION_FAILED", details=f"{path}: string too short")
    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            fail("SCHEMA_REPORT_VALIDATION_FAILED", details=f"{path}: array too short")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                validate_json_schema(item, item_schema, f"{path}[{index}]")
    if isinstance(instance, dict):
        required = schema.get("required", [])
        missing = [key for key in required if key not in instance]
        if missing:
            fail(
                "SCHEMA_REPORT_VALIDATION_FAILED",
                details=f"{path}: missing keys {missing}",
            )
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extras = sorted(set(instance) - set(properties))
            if extras:
                fail(
                    "SCHEMA_REPORT_VALIDATION_FAILED",
                    details=f"{path}: unexpected keys {extras}",
                )
        for key, value in instance.items():
            if key in properties:
                validate_json_schema(value, properties[key], f"{path}.{key}")


def validate_report(
    report: dict[str, Any],
    *,
    expected_phase: str,
    expected_artifacts: list[str],
) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validate_json_schema(report, schema)
    verdict = report.get("verdict")
    summary = report.get("summary")
    findings = report.get("findings")
    outcome = report.get("user_outcome_check") or {}
    verification = report.get("verification") or {}
    challenges = report.get("contract_challenges")
    limitations = report.get("limitations")

    if report.get("phase") != expected_phase:
        fail(
            "SEMANTIC_REPORT_VALIDATION_FAILED",
            details=f"phase mismatch: expected={expected_phase}, actual={report.get('phase')}",
        )
    if not isinstance(summary, str) or len(summary.strip()) < 20:
        fail("SEMANTIC_REPORT_VALIDATION_FAILED", details="summary is too short")
    if not isinstance(challenges, list) or not challenges:
        fail("SEMANTIC_REPORT_VALIDATION_FAILED", details="contract_challenges is empty")
    if not isinstance(findings, list):
        fail("SEMANTIC_REPORT_VALIDATION_FAILED", details="findings is not an array")
    if not all(isinstance(finding, dict) for finding in findings):
        fail("SEMANTIC_REPORT_VALIDATION_FAILED", details="finding item is not an object")
    if not isinstance(limitations, list) or not limitations:
        fail("SEMANTIC_REPORT_VALIDATION_FAILED", details="limitations is empty")
    if not isinstance(outcome, dict):
        fail("SEMANTIC_REPORT_VALIDATION_FAILED", details="user_outcome_check is not an object")
    if not isinstance(verification, dict):
        fail("SEMANTIC_REPORT_VALIDATION_FAILED", details="verification is not an object")
    inspected = verification.get("artifacts_inspected")
    if not isinstance(inspected, list) or not inspected:
        fail("SEMANTIC_REPORT_VALIDATION_FAILED", details="artifacts_inspected is empty")
    if not isinstance(verification.get("tests_assessed"), list) or not verification["tests_assessed"]:
        fail("SEMANTIC_REPORT_VALIDATION_FAILED", details="tests_assessed is empty")
    normalized_inspected = set()
    for item in inspected:
        candidate = Path(str(item)).expanduser()
        if not candidate.is_absolute():
            fail(
                "SEMANTIC_REPORT_VALIDATION_FAILED",
                details=f"inspected artifact is not an absolute path: {item}",
            )
        normalized_inspected.add(str(candidate.resolve()))
    missing_artifacts = sorted(set(expected_artifacts) - normalized_inspected)
    if missing_artifacts:
        fail(
            "SEMANTIC_REPORT_VALIDATION_FAILED",
            details=f"artifacts_inspected missing manifest paths: {missing_artifacts}",
        )

    if verdict == "ACK":
        blocking = [
            finding for finding in findings
            if finding.get("severity") in {"P0", "P1"}
        ]
        if blocking:
            fail("INVALID_ACK_WITH_BLOCKING_FINDINGS")
        if outcome.get("aligned") is not True:
            fail("INVALID_ACK_WITH_MISALIGNED_OUTCOME")
        if verification.get("fresh_scan_completed") is not True:
            fail("INVALID_ACK_WITHOUT_FRESH_SCAN")
    elif verdict == "NOT_ACK" and not findings:
        fail("INVALID_NOT_ACK_WITHOUT_FINDINGS")


def parse_claude(
    stdout: str,
    *,
    expected_phase: str,
    expected_artifacts: list[str],
) -> tuple[str | None, str | None, dict[str, Any]]:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as error:
        fail("CLAUDE_INVALID_JSON", details=str(error))
        raise AssertionError("unreachable")

    if payload.get("is_error"):
        fail("CLAUDE_REVIEW_FAILED", details=json.dumps(payload, ensure_ascii=False))

    report = parse_structured(payload.get("structured_output"))
    if report is None:
        report = parse_structured(payload.get("result"))
    if report is None:
        fail("CLAUDE_MISSING_STRUCTURED_VERDICT", details=stdout)
    validate_report(
        report,
        expected_phase=expected_phase,
        expected_artifacts=expected_artifacts,
    )

    model_usage = payload.get("modelUsage") or {}
    actual_model = next(iter(model_usage.keys()), None)
    return payload.get("session_id"), actual_model, report


def parse_codex(
    stdout: str,
    last_message_path: Path,
    *,
    expected_phase: str,
    expected_artifacts: list[str],
) -> tuple[str | None, str | None, dict[str, Any]]:
    session_id = None
    actual_model = None
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        event_type = event.get("type")
        if event_type in {"thread.started", "thread_started"}:
            session_id = event.get("thread_id") or event.get("threadId")
        if event.get("model"):
            actual_model = event.get("model")

    if not last_message_path.is_file():
        fail("CODEX_MISSING_LAST_MESSAGE", details=stdout)
    report_text = last_message_path.read_text(encoding="utf-8")
    report = parse_structured(report_text)
    if report is None:
        fail("CODEX_MISSING_STRUCTURED_VERDICT", details=report_text)
    validate_report(
        report,
        expected_phase=expected_phase,
        expected_artifacts=expected_artifacts,
    )
    return session_id, actual_model, report


def save_raw(
    directory: str | None,
    peer: str,
    phase: str,
    stdout: str,
    stderr: str,
    normalized: dict[str, Any],
) -> None:
    if not directory:
        return
    target = Path(directory).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    session_fragment = str(normalized.get("sessionId") or "new")[:8]
    stem = f"{peer}-{phase}-{timestamp}-{session_fragment}"
    (target / f"{stem}.stdout").write_text(stdout, encoding="utf-8")
    (target / f"{stem}.stderr").write_text(stderr, encoding="utf-8")
    (target / f"{stem}.result.json").write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def validate_session_id(session_id: str | None) -> None:
    if session_id is None:
        return
    try:
        parsed = uuid.UUID(session_id)
    except (ValueError, AttributeError):
        fail("INVALID_SESSION_ID", details=str(session_id))
    if str(parsed) != session_id.lower():
        fail("INVALID_SESSION_ID", details=str(session_id))


def load_workflow(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail("INVALID_WORKFLOW_STATE", details=str(error))
    if not isinstance(state, dict) or state.get("schemaVersion") != STATE_SCHEMA_VERSION:
        fail("INVALID_WORKFLOW_STATE", details="unsupported state schema")
    return state


def validate_gate_preconditions(
    args: argparse.Namespace,
    peer: str,
    cwd: str,
    state: dict[str, Any] | None,
) -> dict[str, Any]:
    validate_session_id(args.session_id)
    if state is None:
        if args.phase != "intent":
            fail("GATE_ORDER_VIOLATION", details="intent must run first")
        if args.session_id is not None:
            fail("COLD_INTENT_REVIEW_REQUIRED")
        return {
            "schemaVersion": STATE_SCHEMA_VERSION,
            "workflowId": str(uuid.uuid4()),
            "cwd": cwd,
            "peer": peer,
            "gates": {},
        }

    if state.get("cwd") != cwd or state.get("peer") != peer:
        fail("WORKFLOW_IDENTITY_MISMATCH")
    gates = state.get("gates")
    if not isinstance(gates, dict):
        fail("INVALID_WORKFLOW_STATE", details="gates must be an object")

    phase_index = GATE_ORDER.index(args.phase)
    for prerequisite in GATE_ORDER[:phase_index]:
        if (gates.get(prerequisite) or {}).get("verdict") != "ACK":
            fail(
                "GATE_ORDER_VIOLATION",
                details=f"{prerequisite} must ACK before {args.phase}",
            )

    current = gates.get(args.phase)
    if current and current.get("verdict") == "ACK":
        fail("GATE_ALREADY_ACKED", details=args.phase)

    if args.phase == "plan":
        expected = (current or gates["intent"]).get("sessionId")
        if args.session_id != expected:
            fail("SESSION_CONTINUITY_REQUIRED", details=f"expected {expected}")
    elif args.phase == "implementation":
        if current is None and args.session_id is not None:
            fail("COLD_IMPLEMENTATION_REVIEW_REQUIRED")
        if current is not None and args.session_id != current.get("sessionId"):
            fail(
                "SESSION_CONTINUITY_REQUIRED",
                details=f"expected {current.get('sessionId')}",
            )
    elif args.phase == "final":
        expected = (
            current.get("sessionId")
            if current is not None
            else gates["implementation"].get("sessionId")
        )
        if args.session_id not in {None, expected}:
            fail(
                "SESSION_CONTINUITY_REQUIRED",
                details=f"expected a cold session or {expected}",
            )
    elif args.phase == "intent" and current is not None:
        if args.session_id != current.get("sessionId"):
            fail(
                "SESSION_CONTINUITY_REQUIRED",
                details=f"expected {current.get('sessionId')}",
            )
    return state


def write_workflow(
    path: Path,
    state: dict[str, Any],
    phase: str,
    normalized: dict[str, Any],
) -> None:
    session_id = normalized.get("sessionId")
    validate_session_id(session_id)
    if not session_id:
        fail("MISSING_REVIEW_SESSION_ID")
    report_json = json.dumps(
        normalized["report"],
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    state["gates"][phase] = {
        "verdict": normalized["verdict"],
        "sessionId": session_id,
        "reportHash": hashlib.sha256(report_json.encode("utf-8")).hexdigest(),
        "completedAt": datetime.now(timezone.utc).isoformat(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temp_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temp_path, path)


def main() -> None:
    args = parse_args()
    peer = detect_peer(args.peer)
    cwd = Path(args.cwd).expanduser().resolve()
    if not cwd.is_dir():
        fail("PROJECT_ROOT_NOT_FOUND", details=str(cwd))
    args.cwd = str(cwd)
    state_path = resolve_state_path(args, str(cwd))
    normalized_add_dirs = []
    for directory in args.add_dir:
        candidate = Path(directory).expanduser().resolve()
        if not candidate.is_dir():
            fail("ADD_DIR_NOT_FOUND", details=str(candidate))
        normalized_add_dirs.append(str(candidate))
    args.add_dir = sorted(set(normalized_add_dirs))
    if args.timeout_seconds < 30:
        fail("TIMEOUT_TOO_SHORT", details="Use at least 30 seconds.")

    binary = shutil.which(peer)
    if not binary:
        fail("PEER_CLI_NOT_FOUND", details=peer)

    workflow = validate_gate_preconditions(
        args,
        peer,
        str(cwd),
        load_workflow(state_path),
    )
    handoff = normalize_manifest_paths(load_prompt(args), str(cwd))
    manifest_paths = validate_handoff(handoff)
    validate_artifact_access(
        peer,
        manifest_paths,
        str(cwd),
        args.add_dir,
    )
    prompt = reviewer_prompt(args.phase, handoff)
    schema_text = SCHEMA_PATH.read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory(prefix="dual-agent-review-") as temp_dir:
        last_message_path = Path(temp_dir) / "last-message.json"
        profile = None
        if peer == "claude":
            sandbox_binary = shutil.which("sandbox-exec")
            if sys.platform == "darwin" and sandbox_binary:
                profile = sandbox_profile([str(cwd), *args.add_dir])
            elif os.environ.get("DUAL_AGENT_ALLOW_TOOL_ONLY_READONLY") != "1":
                fail(
                    "CLAUDE_OS_SANDBOX_UNAVAILABLE",
                    details=(
                        "Set DUAL_AGENT_ALLOW_TOOL_ONLY_READONLY=1 only after "
                        "accepting tool-level rather than OS-level isolation."
                    ),
                )
        command = (
            build_claude_command(args, schema_text, profile)
            if peer == "claude"
            else build_codex_command(args, last_message_path)
        )
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "status": "dry-run",
                        "peer": peer,
                        "phase": args.phase,
                        "cwd": str(cwd),
                        "requestedModel": requested_model(peer),
                        "resuming": bool(args.session_id),
                        "stateFile": str(state_path),
                        "command": safe_command(command),
                        "promptChars": len(prompt),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return

        environment = os.environ.copy()
        environment["DUAL_AGENT_PEER"] = "1"
        environment["DUAL_AGENT_DEPTH"] = "1"
        try:
            completed = subprocess.run(
                command,
                input=prompt,
                text=True,
                capture_output=True,
                cwd=str(cwd),
                env=environment,
                timeout=args.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            fail(
                "PEER_REVIEW_TIMEOUT",
                details=f"peer={peer}, timeout={args.timeout_seconds}, stderr={error.stderr or ''}",
            )
        except KeyboardInterrupt:
            fail("PEER_REVIEW_INTERRUPTED", code=130)

        if completed.returncode != 0:
            fail(
                "PEER_CLI_FAILED",
                details=f"exit={completed.returncode}\n{completed.stderr}\n{completed.stdout}",
            )

        if peer == "claude":
            session_id, actual_model, report = parse_claude(
                completed.stdout,
                expected_phase=args.phase,
                expected_artifacts=manifest_paths,
            )
        else:
            session_id, actual_model, report = parse_codex(
                completed.stdout,
                last_message_path,
                expected_phase=args.phase,
                expected_artifacts=manifest_paths,
            )

        normalized = {
            "status": "completed",
            "peer": peer,
            "phase": args.phase,
            "sessionId": session_id or args.session_id,
            "requestedModel": requested_model(peer),
            "actualModel": actual_model,
            "verdict": report["verdict"],
            "report": report,
        }
        write_workflow(state_path, workflow, args.phase, normalized)
        save_raw(
            args.save_raw,
            peer,
            args.phase,
            completed.stdout,
            completed.stderr,
            normalized,
        )
        print(json.dumps(normalized, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
