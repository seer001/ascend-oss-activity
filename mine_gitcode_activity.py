#!/usr/bin/env python3
"""Build a small, reproducible activity snapshot for three public CANN repos.

The miner intentionally measures commit activity, author-domain tiers, and work in
selected operator-code paths.  It does not attempt to infer performance or the
employment status of authors using personal email domains.

The commit output omits author names and email addresses, but its deterministic
identity hashes and public commit hashes remain linkable to public Git history.
The output is pseudonymized, not anonymous.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
from urllib.parse import urlsplit


REPOSITORIES: Tuple[str, ...] = ("ops-transformer", "ops-math", "catlass")
DEFAULT_REF = "master"

CORE_PATHS: Mapping[str, Tuple[str, ...]] = {
    "ops-transformer": (
        "attention",
        "common",
        "experimental",
        "ffn",
        "gmm",
        "mamba",
        "mc2",
        "mhc",
        "moe",
        "posembedding",
        "torch_extension",
    ),
    "ops-math": ("common", "conversion", "experimental", "math", "random"),
    "catlass": ("include", "python", "experimental"),
}

HUAWEI_DOMAINS = frozenset(("huawei.com", "hisilicon.com"))
PARTNER_DOMAINS = frozenset(("h-partners.com", "huawei-partners.com"))
AUTOMATION_DOMAINS = frozenset(("cann.team",))
# Name-based automation detection matches whole tokens only, so human names
# that merely contain the letters "bot" (for example "ren-botao") are not
# swept into the automation tier.
AUTOMATION_NAME_TOKENS = frozenset(("bot", "robot"))
_NAME_TOKEN_RE = re.compile(r"[^0-9a-z]+")
DOMAIN_TIERS: Tuple[str, ...] = (
    "huawei_domain",
    "partner_domain",
    "automation",
    "other",
)

OUTPUT_FILENAMES: Tuple[str, ...] = (
    "gitcode_summary.json",
    "gitcode_commits.jsonl",
    "gitcode_monthly.csv",
)

# NUL cannot occur in Git identity fields or paths, so this marker gives us a
# robust boundary while retaining raw, NUL-terminated paths from ``git log -z``.
LOG_MARKER = b"\x00\x00GITCODE_ACTIVITY_COMMIT\x00"
LOG_FORMAT = (
    "%x00%x00GITCODE_ACTIVITY_COMMIT%x00"
    "%H%x00%aI%x00%an%x00%ae%x00%P%x00%s"
)

EMAIL_IN_TEXT_RE = re.compile(
    r"(?i)(?<![A-Z0-9._%+\-])[A-Z0-9._%+\-]+@"
    r"[A-Z0-9\-]+(?:\.[A-Z0-9\-]+)*(?![A-Z0-9.\-])"
)


class PipelineError(RuntimeError):
    """A user-facing validation or mining failure."""


@dataclass(frozen=True)
class RepositoryInput:
    name: str
    path: Path
    origin_url: str
    ref: str
    resolved_sha: str


def parse_as_of(value: str) -> date:
    """Parse a strict ISO calendar date for an inclusive author-date cutoff."""

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise argparse.ArgumentTypeError("--as-of must use YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid --as-of date: {value}") from exc


def _decode_git_field(value: bytes) -> str:
    return value.decode("utf-8", errors="replace")


def _run_git(git_executable: str, repo_path: Path, args: Sequence[str]) -> bytes:
    command = [git_executable, "-C", str(repo_path), *args]
    environment = os.environ.copy()
    environment.update({"LC_ALL": "C", "LANG": "C", "GIT_OPTIONAL_LOCKS": "0"})
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=1800,
            env=environment,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PipelineError(
            f"git failed for {repo_path.name}: {type(exc).__name__}: {exc}"
        ) from exc
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        if len(detail) > 500:
            detail = detail[:497] + "..."
        raise PipelineError(
            f"git {' '.join(args[:3])} failed for {repo_path.name}: "
            f"{detail or 'unknown git error'}"
        )
    return result.stdout


def _is_domain(domain: str, candidates: Iterable[str]) -> bool:
    return any(domain == candidate or domain.endswith("." + candidate) for candidate in candidates)


def _email_domain(email: str) -> str:
    _, separator, domain = email.lower().rpartition("@")
    return domain.rstrip(".") if separator else ""


def _has_automation_name(name: str) -> bool:
    tokens = _NAME_TOKEN_RE.split(name.casefold())
    return any(token in AUTOMATION_NAME_TOKENS for token in tokens if token)


def _classify_domain_tier(name: str, email: str) -> Tuple[str, bool]:
    domain = _email_domain(email)
    is_automation = _is_domain(domain, AUTOMATION_DOMAINS) or _has_automation_name(name)
    if is_automation:
        return "automation", True
    if _is_domain(domain, HUAWEI_DOMAINS):
        return "huawei_domain", False
    if _is_domain(domain, PARTNER_DOMAINS):
        return "partner_domain", False
    return "other", False


def _identity_hash(name: str, email: str) -> str:
    identity = name + "\x00" + email.lower()
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def _redact_emails(text: str) -> str:
    return EMAIL_IN_TEXT_RE.sub("[redacted-email]", text)


def _validate_public_origin(origin_url: str, repository: str) -> None:
    try:
        parsed = urlsplit(origin_url)
        port = parsed.port
    except ValueError as exc:
        raise PipelineError(f"{repository}: malformed origin URL") from exc

    expected_paths = {f"/cann/{repository}", f"/cann/{repository}.git"}
    if not (
        parsed.scheme.lower() == "https"
        and (parsed.hostname or "").lower() == "gitcode.com"
        and parsed.username is None
        and parsed.password is None
        and port in (None, 443)
        and parsed.path.rstrip("/") in expected_paths
        and not parsed.query
        and not parsed.fragment
    ):
        raise PipelineError(
            f"{repository}: origin must be the public HTTPS GitCode URL "
            f"https://gitcode.com/cann/{repository}.git"
        )


def _find_repository(repos_dir: Path, repository: str) -> Path:
    candidates = (repos_dir / repository, repos_dir / f"cann-{repository}")
    matches = [candidate for candidate in candidates if candidate.is_dir()]
    if not matches:
        names = " or ".join(candidate.name for candidate in candidates)
        raise PipelineError(f"missing repository {repository}: expected {names} in {repos_dir}")
    if len(matches) > 1:
        raise PipelineError(
            f"ambiguous repository {repository}: both {matches[0].name} and "
            f"{matches[1].name} exist"
        )
    return matches[0]


def _validate_inputs(
    repos_dir: Path,
    git_executable: str,
    replay_shas: Optional[Mapping[str, str]] = None,
) -> List[RepositoryInput]:
    if not repos_dir.is_dir():
        raise PipelineError(f"repositories directory does not exist: {repos_dir}")

    inputs: List[RepositoryInput] = []
    for repository in REPOSITORIES:
        repo_path = _find_repository(repos_dir, repository)
        inside = _run_git(
            git_executable, repo_path, ("rev-parse", "--is-inside-work-tree")
        ).strip()
        if inside != b"true":
            raise PipelineError(f"{repository}: directory is not a Git working tree")

        shallow = _run_git(
            git_executable, repo_path, ("rev-parse", "--is-shallow-repository")
        ).strip()
        if shallow == b"true":
            raise PipelineError(
                f"{repository}: shallow clone is not a complete history; "
                "use a full or blob-filtered clone"
            )
        if shallow != b"false":
            raise PipelineError(f"{repository}: could not verify complete Git history")

        try:
            origin_url = _decode_git_field(
                _run_git(
                    git_executable,
                    repo_path,
                    ("config", "--get", "remote.origin.url"),
                )
            ).strip()
        except PipelineError as exc:
            raise PipelineError(f"{repository}: missing origin URL") from exc
        if not origin_url:
            raise PipelineError(f"{repository}: missing origin URL")
        _validate_public_origin(origin_url, repository)

        requested_revision = (
            replay_shas[repository] if replay_shas is not None else DEFAULT_REF
        )
        try:
            resolved_sha = _decode_git_field(
                _run_git(
                    git_executable,
                    repo_path,
                    ("rev-parse", "--verify", f"{requested_revision}^{{commit}}"),
                )
            ).strip()
        except PipelineError as exc:
            raise PipelineError(
                f"{repository}: required revision {requested_revision!r} is "
                "missing or invalid"
            ) from exc
        if not re.fullmatch(r"[0-9a-fA-F]{40,64}", resolved_sha):
            raise PipelineError(f"{repository}: Git returned an invalid resolved SHA")

        inputs.append(
            RepositoryInput(
                name=repository,
                path=repo_path,
                origin_url=origin_url,
                ref=DEFAULT_REF,
                resolved_sha=resolved_sha.lower(),
            )
        )
    return inputs


def _touches_core_path(repository: str, raw_paths: Iterable[bytes]) -> bool:
    prefixes = tuple(prefix.encode("utf-8") for prefix in CORE_PATHS[repository])
    for path in raw_paths:
        if any(path == prefix or path.startswith(prefix + b"/") for prefix in prefixes):
            return True
    return False


def _parse_log(repository: str, raw_log: bytes, as_of: date) -> List[Dict[str, object]]:
    chunks = raw_log.split(LOG_MARKER)
    if len(chunks) == 1:
        raise PipelineError(f"{repository}: git log returned no parseable commits")
    if chunks[0]:
        raise PipelineError(f"{repository}: unexpected bytes before first git log record")

    records: List[Dict[str, object]] = []
    for chunk in chunks[1:]:
        fields = chunk.split(b"\x00", 6)
        if len(fields) != 7:
            raise PipelineError(f"{repository}: malformed git log record")
        raw_hash, raw_timestamp, raw_name, raw_email, raw_parents, raw_subject, raw_paths = fields

        commit_hash = _decode_git_field(raw_hash)
        author_timestamp = _decode_git_field(raw_timestamp)
        try:
            author_date = date.fromisoformat(author_timestamp[:10])
        except ValueError as exc:
            raise PipelineError(
                f"{repository}: invalid author date for commit {commit_hash}"
            ) from exc
        if author_date > as_of:
            continue

        # Git inserts one LF between the pretty record and its NUL-terminated paths.
        if raw_paths.startswith(b"\n"):
            raw_paths = raw_paths[1:]
        paths = tuple(path for path in raw_paths.split(b"\x00") if path)

        name = _decode_git_field(raw_name)
        email = _decode_git_field(raw_email)
        domain_tier, is_automation = _classify_domain_tier(name, email)
        parents = raw_parents.split()
        day = author_date.isoformat()
        records.append(
            {
                "repository": repository,
                "hash": commit_hash.lower(),
                "date": day,
                "month": day[:7],
                "subject": _redact_emails(_decode_git_field(raw_subject)),
                "domain_tier": domain_tier,
                "identity_hash": _identity_hash(name, email),
                "is_merge": len(parents) > 1,
                "is_automation": is_automation,
                "touches_core": _touches_core_path(repository, paths),
                "top_level_dirs": sorted(
                    {
                        _decode_git_field(path.split(b"/", 1)[0])
                        for path in paths
                    }
                ),
            }
        )
    return records


def _mine_repository(
    git_executable: str, repo_input: RepositoryInput, as_of: date
) -> List[Dict[str, object]]:
    # Exactly one log traversal per repository.  The resolved SHA pins the history
    # even if the local branch moves while the three repositories are being read.
    raw_log = _run_git(
        git_executable,
        repo_input.path,
        (
            "log",
            "--no-color",
            "--no-ext-diff",
            "--no-renames",
            "--no-show-signature",
            "-z",
            "--name-only",
            f"--format={LOG_FORMAT}",
            repo_input.resolved_sha,
        ),
    )
    return _parse_log(repo_input.name, raw_log, as_of)


def _share(numerator: int, denominator: int) -> Optional[float]:
    return round(numerator / denominator, 6) if denominator else None


def _statistics(records: Sequence[Mapping[str, object]]) -> Dict[str, object]:
    tier_counts = Counter(str(record["domain_tier"]) for record in records)
    total = len(records)
    eligible = [
        record
        for record in records
        if not bool(record["is_merge"]) and not bool(record["is_automation"])
    ]
    core_count = sum(bool(record["touches_core"]) for record in eligible)
    monthly_counts = Counter(str(record["month"]) for record in records)
    identities = {str(record["identity_hash"]) for record in records}
    author_dates = sorted(str(record["date"]) for record in records)

    return {
        "total_commits": total,
        "author_date_range": (
            [author_dates[0], author_dates[-1]] if author_dates else [None, None]
        ),
        "unique_pseudonymous_author_identities": len(identities),
        "domain_tiers": {
            tier: {
                "commits": tier_counts[tier],
                "share": _share(tier_counts[tier], total),
            }
            for tier in DOMAIN_TIERS
        },
        "non_merge_non_automation_commits": len(eligible),
        "core_path_commits": core_count,
        "core_path_share": _share(core_count, len(eligible)),
        "monthly_counts": dict(sorted(monthly_counts.items())),
    }


def _build_summary(
    repo_inputs: Sequence[RepositoryInput],
    records_by_repo: Mapping[str, Sequence[Mapping[str, object]]],
    as_of: date,
) -> Dict[str, object]:
    all_records = [
        record
        for repository in REPOSITORIES
        for record in records_by_repo[repository]
    ]
    repositories: Dict[str, object] = {}
    for repo_input in repo_inputs:
        repositories[repo_input.name] = {
            "origin_url": repo_input.origin_url,
            "ref": repo_input.ref,
            "resolved_sha": repo_input.resolved_sha,
            **_statistics(records_by_repo[repo_input.name]),
        }

    return {
        "schema_version": 2,
        "as_of": as_of.isoformat(),
        "date_basis": "author_date",
        "ref": DEFAULT_REF,
        "privacy_note": (
            "Author name and email fields are omitted. Identity and commit hashes "
            "are linkable pseudonyms, not anonymous identifiers."
        ),
        "totals": _statistics(all_records),
        "repositories": repositories,
    }


def _build_jsonl(records: Sequence[Mapping[str, object]]) -> bytes:
    ordered = sorted(
        records,
        key=lambda record: (
            str(record["date"]),
            str(record["repository"]),
            str(record["hash"]),
        ),
    )
    lines = [
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for record in ordered
    ]
    return (("\n".join(lines) + "\n") if lines else "").encode("utf-8")


def _monthly_values(records: Sequence[Mapping[str, object]]) -> Dict[str, int]:
    values = {"total_commits": len(records)}
    for tier in DOMAIN_TIERS:
        values[f"{tier}_commits"] = sum(
            str(record["domain_tier"]) == tier for record in records
        )
    eligible = [
        record
        for record in records
        if not bool(record["is_merge"]) and not bool(record["is_automation"])
    ]
    values["non_merge_non_automation_commits"] = len(eligible)
    values["core_path_commits"] = sum(
        bool(record["touches_core"]) for record in eligible
    )
    return values


def _build_monthly_csv(
    records_by_repo: Mapping[str, Sequence[Mapping[str, object]]]
) -> bytes:
    fieldnames = (
        "repository",
        "month",
        "total_commits",
        "huawei_domain_commits",
        "partner_domain_commits",
        "automation_commits",
        "other_commits",
        "non_merge_non_automation_commits",
        "core_path_commits",
    )
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()

    scopes: List[Tuple[str, Sequence[Mapping[str, object]]]] = [
        (
            "ALL",
            [
                record
                for repository in REPOSITORIES
                for record in records_by_repo[repository]
            ],
        )
    ]
    scopes.extend((repository, records_by_repo[repository]) for repository in REPOSITORIES)
    for label, records in scopes:
        monthly: Dict[str, List[Mapping[str, object]]] = defaultdict(list)
        for record in records:
            monthly[str(record["month"])].append(record)
        for month in sorted(monthly):
            writer.writerow(
                {
                    "repository": label,
                    "month": month,
                    **_monthly_values(monthly[month]),
                }
            )
    return output.getvalue().encode("utf-8")


def load_replay_shas(summary_path: Path) -> Dict[str, str]:
    """Read the three resolved SHAs from an earlier pipeline summary."""

    summary_path = Path(summary_path)
    try:
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
        repositories = payload["repositories"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise PipelineError(f"invalid replay summary {summary_path}: {exc}") from exc

    replay_shas: Dict[str, str] = {}
    try:
        for repository in REPOSITORIES:
            resolved_sha = repositories[repository]["resolved_sha"]
            if not isinstance(resolved_sha, str) or not re.fullmatch(
                r"[0-9a-fA-F]{40,64}", resolved_sha
            ):
                raise ValueError(f"invalid resolved SHA for {repository}")
            replay_shas[repository] = resolved_sha.lower()
    except (KeyError, TypeError, ValueError) as exc:
        raise PipelineError(f"invalid replay summary {summary_path}: {exc}") from exc
    return replay_shas


def run_pipeline(
    repos_dir: Path,
    out_dir: Path,
    as_of: date,
    replay_shas: Optional[Mapping[str, str]] = None,
) -> Dict[str, object]:
    """Validate, mine, and write the three deterministic output artifacts."""

    git_executable = shutil.which("git")
    if git_executable is None:
        raise PipelineError("git executable not found in PATH")

    repos_dir = Path(repos_dir)
    out_dir = Path(out_dir)
    if replay_shas is not None:
        if set(replay_shas) != set(REPOSITORIES):
            raise PipelineError("replay SHAs must specify exactly the three fixed repositories")
        for repository, resolved_sha in replay_shas.items():
            if not isinstance(resolved_sha, str) or not re.fullmatch(
                r"[0-9a-fA-F]{40,64}", resolved_sha
            ):
                raise PipelineError(f"invalid replay SHA for {repository}")
    repo_inputs = _validate_inputs(repos_dir, git_executable, replay_shas)

    records_by_repo: Dict[str, Sequence[Mapping[str, object]]] = {}
    for repo_input in repo_inputs:
        records_by_repo[repo_input.name] = _mine_repository(
            git_executable, repo_input, as_of
        )

    summary = _build_summary(repo_inputs, records_by_repo, as_of)
    all_records = [
        record
        for repository in REPOSITORIES
        for record in records_by_repo[repository]
    ]
    payloads = {
        "gitcode_summary.json": (
            json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8"),
        "gitcode_commits.jsonl": _build_jsonl(all_records),
        "gitcode_monthly.csv": _build_monthly_csv(records_by_repo),
    }

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        if not out_dir.is_dir():
            raise OSError("output path is not a directory")
        for filename in OUTPUT_FILENAMES:
            (out_dir / filename).write_bytes(payloads[filename])
    except OSError as exc:
        raise PipelineError(f"could not write outputs to {out_dir}: {exc}") from exc
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Mine reproducible activity metrics from three local CANN GitCode clones."
    )
    parser.add_argument("repos_dir", type=Path, help="directory containing the three clones")
    parser.add_argument("out_dir", type=Path, help="directory for deterministic outputs")
    parser.add_argument(
        "--as-of",
        required=True,
        type=parse_as_of,
        metavar="YYYY-MM-DD",
        help="inclusive cutoff using each commit's author date",
    )
    parser.add_argument(
        "--replay-summary",
        type=Path,
        metavar="JSON",
        help="reuse the three resolved SHAs from an earlier gitcode_summary.json",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        replay_shas = (
            load_replay_shas(args.replay_summary) if args.replay_summary else None
        )
        summary = run_pipeline(
            args.repos_dir, args.out_dir, args.as_of, replay_shas=replay_shas
        )
    except PipelineError as exc:
        parser.error(str(exc))
    print(
        f"wrote {len(OUTPUT_FILENAMES)} files; "
        f"{summary['totals']['total_commits']} commits through {args.as_of.isoformat()}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
