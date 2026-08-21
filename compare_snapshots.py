#!/usr/bin/env python3
"""Build a privacy-preserving, hash-level diff between dated snapshots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def compact(row: dict[str, Any], *, github: bool) -> dict[str, Any]:
    result: dict[str, Any] = {"hash": row["hash"], "date": row["date"]}
    if github:
        result["affiliation"] = row["affiliation"]
    else:
        result.update(
            {
                "domain_tier": row["domain_tier"],
                "is_automation": row["is_automation"],
                "is_merge": row["is_merge"],
                "touches_core": row["touches_core"],
            }
        )
    return result


def compare_rows(
    old_rows: list[dict[str, Any]],
    new_rows: list[dict[str, Any]],
    *,
    old_cutoff: str,
    github: bool,
) -> dict[str, Any]:
    old = {row["hash"]: row for row in old_rows}
    new = {row["hash"]: row for row in new_rows}
    added_hashes = sorted(new.keys() - old.keys())
    removed_hashes = sorted(old.keys() - new.keys())

    if github:
        compared_fields = ("affiliation", "domain", "identity_hash", "name_hash")
    else:
        compared_fields = (
            "domain_tier",
            "identity_hash",
            "is_automation",
            "is_merge",
            "touches_core",
            "top_level_dirs",
        )

    changed: list[dict[str, Any]] = []
    for commit_hash in sorted(old.keys() & new.keys()):
        before = old[commit_hash]
        after = new[commit_hash]
        fields = {
            field: {"old": before.get(field), "new": after.get(field)}
            for field in compared_fields
            if before.get(field) != after.get(field)
        }
        if fields:
            changed.append(
                {
                    "hash": commit_hash,
                    "date": after["date"],
                    "fields": fields,
                }
            )

    added = [compact(new[commit_hash], github=github) for commit_hash in added_hashes]
    removed = [compact(old[commit_hash], github=github) for commit_hash in removed_hashes]
    backfilled = [row for row in added if row["date"] <= old_cutoff]
    post_cutoff = [row for row in added if row["date"] > old_cutoff]
    return {
        "counts": {
            "old": len(old),
            "new": len(new),
            "added": len(added),
            "removed": len(removed),
            "backfilled_through_old_cutoff": len(backfilled),
            "added_after_old_cutoff": len(post_cutoff),
            "changed_existing_rows": len(changed),
        },
        "added": added,
        "removed": removed,
        "backfilled_through_old_cutoff": backfilled,
        "changed_existing_rows": changed,
    }


def github_block(old_dir: Path, new_dir: Path, old_cutoff: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    old_files = {path.name.removeprefix("raw_").removesuffix(".jsonl"): path for path in old_dir.glob("raw_*.jsonl")}
    new_files = {path.name.removeprefix("raw_").removesuffix(".jsonl"): path for path in new_dir.glob("raw_*.jsonl")}
    if old_files.keys() != new_files.keys():
        raise ValueError("GitHub repository sets differ between snapshots")
    for repo in sorted(old_files):
        result[repo] = compare_rows(
            load_jsonl(old_files[repo]),
            load_jsonl(new_files[repo]),
            old_cutoff=old_cutoff,
            github=True,
        )
    return result


def gitcode_block(old_dir: Path, new_dir: Path, old_cutoff: str) -> dict[str, Any]:
    old_rows = load_jsonl(old_dir / "gitcode_commits.jsonl")
    new_rows = load_jsonl(new_dir / "gitcode_commits.jsonl")
    old_by_repo: dict[str, list[dict[str, Any]]] = {}
    new_by_repo: dict[str, list[dict[str, Any]]] = {}
    for row in old_rows:
        old_by_repo.setdefault(row["repository"], []).append(row)
    for row in new_rows:
        new_by_repo.setdefault(row["repository"], []).append(row)
    if old_by_repo.keys() != new_by_repo.keys():
        raise ValueError("GitCode repository sets differ between snapshots")
    return {
        repo: compare_rows(
            old_by_repo[repo],
            new_by_repo[repo],
            old_cutoff=old_cutoff,
            github=False,
        )
        for repo in sorted(old_by_repo)
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old-github", type=Path, required=True)
    parser.add_argument("--new-github", type=Path, required=True)
    parser.add_argument("--old-gitcode", type=Path, required=True)
    parser.add_argument("--new-gitcode", type=Path, required=True)
    parser.add_argument("--old-cutoff", default="2026-07-10")
    parser.add_argument("--new-cutoff", default="2026-08-19")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    payload = {
        "schema_version": 1,
        "old_cutoff": args.old_cutoff,
        "new_cutoff": args.new_cutoff,
        "date_basis": "author_local_calendar_date",
        "privacy_note": "Contains public commit hashes and derived fields; author names, emails, subjects, and identity hashes are omitted.",
        "github": github_block(args.old_github, args.new_github, args.old_cutoff),
        "gitcode": gitcode_block(args.old_gitcode, args.new_gitcode, args.old_cutoff),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
