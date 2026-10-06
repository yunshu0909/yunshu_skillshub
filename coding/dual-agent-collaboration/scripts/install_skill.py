#!/usr/bin/env python3
"""Atomically install this Skill into one or more tool skill directories."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import uuid


IGNORED_DIRS = {"__pycache__"}
IGNORED_FILES = {".DS_Store"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def fail(message: str, *, details: str | None = None) -> None:
    payload = {"status": "error", "error": message}
    if details:
        payload["details"] = details
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stage, verify, atomically replace, and roll back Skill copies."
    )
    parser.add_argument("--source", required=True)
    parser.add_argument("--target", action="append", required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def should_ignore(path: Path) -> bool:
    return (
        any(part in IGNORED_DIRS for part in path.parts)
        or path.name in IGNORED_FILES
        or path.suffix in IGNORED_SUFFIXES
    )


def content_manifest(root: Path) -> dict[str, str]:
    manifest: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if should_ignore(relative):
            continue
        if path.is_symlink():
            fail("SYMLINK_NOT_SUPPORTED", details=str(path))
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            manifest[relative.as_posix()] = digest
    return manifest


def validate_paths(source: Path, targets: list[Path]) -> None:
    if not source.is_dir() or not (source / "SKILL.md").is_file():
        fail("INVALID_SKILL_SOURCE", details=str(source))
    if len(set(targets)) != len(targets):
        fail("DUPLICATE_TARGET")
    for target in targets:
        if target.name != source.name:
            fail(
                "TARGET_NAME_MISMATCH",
                details=f"expected final directory name {source.name}: {target}",
            )
        if target == source:
            fail("SOURCE_IS_TARGET", details=str(target))
        try:
            target.relative_to(source)
        except ValueError:
            pass
        else:
            fail("TARGET_INSIDE_SOURCE", details=str(target))


def copy_to_stage(source: Path, stage: Path) -> None:
    shutil.copytree(
        source,
        stage,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".DS_Store"),
    )


def remove_owned_path(path: Path) -> None:
    """Remove only a unique stage/backup path created by this invocation."""
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def install(source: Path, targets: list[Path], *, dry_run: bool) -> dict:
    validate_paths(source, targets)
    source_manifest = content_manifest(source)
    if not source_manifest:
        fail("EMPTY_SKILL_SOURCE")

    operation_id = uuid.uuid4().hex
    records = []
    for target in targets:
        parent = target.parent
        stage = parent / f".{target.name}.stage-{operation_id}"
        backup = parent / f".{target.name}.backup-{operation_id}"
        records.append(
            {
                "target": target,
                "stage": stage,
                "backup": backup,
                "had_original": target.exists(),
                "installed": False,
            }
        )

    if dry_run:
        return {
            "status": "dry-run",
            "source": str(source),
            "targets": [str(record["target"]) for record in records],
            "fileCount": len(source_manifest),
            "ignored": sorted([*IGNORED_DIRS, *IGNORED_FILES, *IGNORED_SUFFIXES]),
        }

    try:
        for record in records:
            target = record["target"]
            stage = record["stage"]
            target.parent.mkdir(parents=True, exist_ok=True)
            if stage.exists() or record["backup"].exists():
                fail("INSTALL_TEMP_COLLISION", details=str(stage))
            copy_to_stage(source, stage)
            if content_manifest(stage) != source_manifest:
                fail("STAGING_CONTENT_MISMATCH", details=str(target))

        for record in records:
            target = record["target"]
            backup = record["backup"]
            stage = record["stage"]
            if record["had_original"]:
                os.replace(target, backup)
            os.replace(stage, target)
            record["installed"] = True

        mismatched = [
            str(record["target"])
            for record in records
            if content_manifest(record["target"]) != source_manifest
        ]
        if mismatched:
            fail("INSTALLED_CONTENT_MISMATCH", details=", ".join(mismatched))

        for record in records:
            remove_owned_path(record["backup"])
        return {
            "status": "installed",
            "source": str(source),
            "targets": [str(record["target"]) for record in records],
            "fileCount": len(source_manifest),
            "manifestSha256": hashlib.sha256(
                json.dumps(source_manifest, sort_keys=True).encode("utf-8")
            ).hexdigest(),
        }
    except BaseException:
        for record in reversed(records):
            target = record["target"]
            backup = record["backup"]
            if record["installed"] and target.exists():
                failed_copy = (
                    target.parent
                    / f".{target.name}.failed-{operation_id}"
                )
                os.replace(target, failed_copy)
                remove_owned_path(failed_copy)
            if record["had_original"] and backup.exists():
                os.replace(backup, target)
            remove_owned_path(record["stage"])
            remove_owned_path(backup)
        raise


def main() -> None:
    args = parse_args()
    source = Path(args.source).expanduser().resolve()
    targets = [Path(value).expanduser().resolve() for value in args.target]
    result = install(source, targets, dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
