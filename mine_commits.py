#!/usr/bin/env python3
"""Replicate and extend the Heim (2026) Ascend commit counts from local clones.

Method: local ``git log`` mining over full clones, no API required. For each
declared repository the script counts Ascend-related commits under either a
dedicated-repository rule (every commit counts) or a keyword/path candidate
rule, attributes commits to observed email-domain tiers (confirmed / likely /
unknown), and records monthly series plus insertions/deletions where blob
data is available.

Windows:
  Heim window:     2025-04-01 through 2026-03-31 (fixed, for comparison)
  Extended window: 2025-04-01 through --as-of (this project's increment)

Privacy: output rows omit author names and email addresses. Each row keeps
the email domain plus two deterministic SHA-256 pseudonyms (identity and
name) so the aggregate statistics remain recomputable from the rows. These
are linkable pseudonyms, not anonymous identifiers.

Note: computing insertions/deletions on blob-filtered clones triggers lazy
blob fetches from the network. Run against complete local clones for fully
offline behavior.

Usage: python3 mine_commits.py <repos_dir> <out_dir> --as-of YYYY-MM-DD
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from urllib.parse import urlsplit

HEIM_START = "2025-04-01"
HEIM_END = "2026-03-31"

# Confirmed Huawei: the email domain belongs directly to Huawei.
CONFIRMED_DOMAINS = ("huawei.com", "hisilicon.com")
# Likely Huawei: long-term Huawei outsourcing/partner company domains.
LIKELY_DOMAINS = ("h-partners.com", "huawei-partners.com")

# Repository rules: mode=dedicated (every commit counts) or filtered
# (a commit counts when its message or touched paths match the rule).
# numstat: whether to compute insertions/deletions (requires blob data).
# The --grep patterns use \b word boundaries, which GNU and BSD git regex
# engines support; the frozen snapshot was produced with these patterns.
REPOS = {
    "vllm-ascend":   {"mode": "dedicated", "numstat": True,
                      "origin": "vllm-project/vllm-ascend"},
    "triton-ascend": {"mode": "dedicated", "numstat": True,
                      "origin": "triton-lang/triton-ascend"},
    "torch_npu":     {"mode": "dedicated", "numstat": False,
                      "origin": "Ascend/pytorch"},
    "sglang":        {"mode": "filtered", "numstat": True,
                      "origin": "sgl-project/sglang",
                      "grep": r"ascend|cann|\bnpu\b",
                      "paths": [":(glob,icase)**/*ascend*", ":(glob,icase)**/*npu*"]},
    "llama.cpp":     {"mode": "filtered", "numstat": True,
                      "origin": "ggml-org/llama.cpp",
                      "grep": r"cann|ascend",
                      "paths": [":(glob,icase)**/*cann*"]},
    "lmdeploy":      {"mode": "filtered", "numstat": True,
                      "origin": "InternLM/lmdeploy",
                      "grep": r"ascend|dlinfer|\bnpu\b",
                      "paths": [":(glob,icase)**/*ascend*"]},
    "pytorch":       {"mode": "filtered", "numstat": False,  # tree:0 clone
                      "origin": "pytorch/pytorch",
                      "grep": r"ascend|torch_npu|\bnpu\b", "paths": []},
    "transformers":  {"mode": "filtered", "numstat": False,
                      "origin": "huggingface/transformers",
                      "grep": r"ascend|\bnpu\b", "paths": []},
}

SEP = "\x1e"  # record separator
FMT = f"%H{SEP}%aI{SEP}%an{SEP}%ae{SEP}%s"

EMAIL_IN_TEXT_RE = re.compile(
    r"(?i)(?<![A-Z0-9._%+\-])[A-Z0-9._%+\-]+@"
    r"[A-Z0-9\-]+(?:\.[A-Z0-9\-]+)*(?![A-Z0-9.\-])"
)


class MiningError(RuntimeError):
    """A user-facing validation or mining failure."""


def git(repo_dir, *args):
    environment = os.environ.copy()
    environment.update({"LC_ALL": "C", "LANG": "C", "GIT_OPTIONAL_LOCKS": "0"})
    r = subprocess.run(
        ["git", "-C", repo_dir, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=1800,
        env=environment,
    )
    if r.returncode != 0:
        raise MiningError(
            f"git {' '.join(args[:3])} failed in {repo_dir}: {r.stderr[:500]}"
        )
    return r.stdout


def matches_domain(domain, candidates):
    return any(
        domain == candidate or domain.endswith("." + candidate)
        for candidate in candidates
    )


def email_domain(email):
    return email.rsplit("@", 1)[-1] if "@" in email else ""


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def redact_emails(text):
    return EMAIL_IN_TEXT_RE.sub("[redacted-email]", text)


def validate_repository(repo_dir, repo, expected_slug):
    inside = git(repo_dir, "rev-parse", "--is-inside-work-tree").strip()
    bare = git(repo_dir, "rev-parse", "--is-bare-repository").strip()
    if inside != "true" and bare != "true":
        raise MiningError(f"{repo}: directory is not a Git repository")
    shallow = git(repo_dir, "rev-parse", "--is-shallow-repository").strip()
    if shallow != "false":
        raise MiningError(
            f"{repo}: shallow clone cannot support complete-history counts"
        )
    origin = git(repo_dir, "config", "--get", "remote.origin.url").strip()
    try:
        parsed = urlsplit(origin)
    except ValueError as exc:
        raise MiningError(f"{repo}: malformed origin URL") from exc
    expected_paths = {
        f"/{expected_slug.lower()}",
        f"/{expected_slug.lower()}.git",
    }
    if not (
        parsed.scheme.lower() == "https"
        and (parsed.hostname or "").lower() == "github.com"
        and parsed.username is None
        and parsed.path.lower().rstrip("/") in expected_paths
    ):
        raise MiningError(
            f"{repo}: origin must be https://github.com/{expected_slug}.git, "
            f"found {origin!r}"
        )
    return origin


def log_commits(repo_dir, grep=None, paths=None):
    """Return {hash: record}. The grep and path rules are unioned."""
    out = {}

    def run(extra):
        raw = git(repo_dir, "log", "HEAD", f"--format={FMT}", *extra)
        # Not splitlines(): it would also treat the \x1e separator as a
        # line boundary.
        for line in raw.split("\n"):
            parts = line.split(SEP)
            if len(parts) != 5:
                continue
            h, dt, name, email, subj = parts
            out[h] = {"hash": h, "date": dt[:10], "name": name.strip(),
                      "email": email.strip().lower(), "subject": subj}

    if grep is None and not paths:
        run([])
    else:
        if grep:
            run(["-i", "-E", f"--grep={grep}"])
        for p in (paths or []):
            run(["--", p])
    return out


def numstat_for(repo_dir, hashes):
    """Sum insertions/deletions per commit (may lazily fetch blobs)."""
    ins = defaultdict(int)
    dels = defaultdict(int)
    batch = 400
    hl = list(hashes)
    for i in range(0, len(hl), batch):
        chunk = hl[i:i + batch]
        raw = git(repo_dir, "show", "--numstat", "--format=@@%H", *chunk)
        cur = None
        for line in raw.split("\n"):
            if line.startswith("@@"):
                cur = line[2:]
            elif line and cur and "\t" in line:
                a, d, _ = line.split("\t", 2)
                if a.isdigit():
                    ins[cur] += int(a)
                if d.isdigit():
                    dels[cur] += int(d)
    return ins, dels


def classify(email, name, confirmed_names):
    dom = email_domain(email)
    if matches_domain(dom, CONFIRMED_DOMAINS):
        return "confirmed"
    if matches_domain(dom, LIKELY_DOMAINS):
        return "likely"
    if name in confirmed_names:  # same author name used a Huawei address elsewhere
        return "likely"
    return "unknown"


def validate_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected YYYY-MM-DD") from exc
    return value


def public_row(record):
    """Build the pseudonymized output row for one mined commit."""
    row = {
        "hash": record["hash"],
        "date": record["date"],
        "domain": email_domain(record["email"]),
        "affiliation": record["affiliation"],
        "subject": redact_emails(record["subject"]),
        "identity_hash": sha256_text(
            record["name"] + "\x00" + record["email"].lower()
        ),
        "name_hash": sha256_text(record["name"]),
    }
    if "insertions" in record:
        row["insertions"] = record["insertions"]
        row["deletions"] = record["deletions"]
    return row


def main(repos_dir, out_dir, as_of):
    os.makedirs(out_dir, exist_ok=True)
    all_records = {}

    for repo, cfg in REPOS.items():
        rd = os.path.join(repos_dir, repo)
        if not os.path.isdir(rd):
            raise MiningError(
                f"required repository is missing: {rd}. "
                "Clone every declared repository before running the snapshot."
            )
        origin = validate_repository(rd, repo, cfg["origin"])
        print(f"[mine] {repo} ({cfg['mode']}) ...", file=sys.stderr)
        ref_sha = git(rd, "rev-parse", "HEAD").strip()
        if cfg["mode"] == "dedicated":
            recs = log_commits(rd)
        else:
            recs = log_commits(rd, cfg.get("grep"), cfg.get("paths"))
        # Keep the Heim-window start through the fixed cutoff; the current
        # ref's full-history count is stored separately.
        full_count = len(recs)
        recs = {
            h: r for h, r in recs.items()
            if HEIM_START <= r["date"] <= as_of
        }
        if cfg["numstat"] and recs:
            ins, dels = numstat_for(rd, recs.keys())
            for h, r in recs.items():
                r["insertions"] = ins.get(h, 0)
                r["deletions"] = dels.get(h, 0)
        all_records[repo] = {
            "full_history_count": full_count,
            "origin": origin,
            "ref": "HEAD",
            "ref_sha": ref_sha,
            "records": recs,
        }
        print(f"  {repo}: {len(recs)} commits since {HEIM_START} "
              f"(full history {full_count})", file=sys.stderr)

    # Cross-repository identity merge: any author name that has used a
    # confirmed-domain address anywhere in the mined set.
    confirmed_names = set()
    for repo, blob in all_records.items():
        for r in blob["records"].values():
            if matches_domain(email_domain(r["email"]), CONFIRMED_DOMAINS):
                confirmed_names.add(r["name"])

    summary = {
        "schema_version": 2,
        "generated": as_of,
        "snapshot_as_of": as_of,
        "heim_window": [HEIM_START, HEIM_END],
        "extended_window": [HEIM_START, as_of],
        "privacy_note": (
            "Raw rows omit author names and email addresses; they retain "
            "the email domain and deterministic identity/name hashes. "
            "These are linkable pseudonyms, not anonymous identifiers."
        ),
        "repos": {},
    }
    for repo, blob in all_records.items():
        recs = list(blob["records"].values())
        for r in recs:
            r["affiliation"] = classify(r["email"], r["name"], confirmed_names)

        def window(rows, end):
            rows = [r for r in rows if r["date"] <= end]
            n = len(rows)
            aff = defaultdict(int)
            loc = defaultdict(int)
            monthly = defaultdict(int)
            authors = defaultdict(set)
            for r in rows:
                aff[r["affiliation"]] += 1
                loc[r["affiliation"]] += r.get("insertions", 0)
                monthly[r["date"][:7]] += 1
                authors[r["affiliation"]].add(r["name"])
            hw = aff["confirmed"] + aff["likely"]
            hw_loc = loc["confirmed"] + loc["likely"]
            tot_loc = sum(loc.values())
            return {
                "commits": n,
                "commits_confirmed": aff["confirmed"],
                "commits_likely": aff["likely"],
                "commits_unknown": aff["unknown"],
                "huawei_commit_share": round(hw / n, 3) if n else None,
                "lines_added_total": tot_loc or None,
                "lines_added_huawei": hw_loc or None,
                "huawei_loc_share": round(hw_loc / tot_loc, 3) if tot_loc else None,
                "authors_confirmed": len(authors["confirmed"]),
                "authors_likely": len(authors["likely"]),
                "authors_unknown": len(authors["unknown"]),
                "monthly": dict(sorted(monthly.items())),
            }

        summary["repos"][repo] = {
            "full_history_count": blob["full_history_count"],
            "origin": blob["origin"],
            "ref": blob["ref"],
            "ref_sha": blob["ref_sha"],
            "heim_window": window(recs, HEIM_END),
            "extended_window": window(recs, as_of),
        }
        out_name = f"raw_{repo.replace('/', '_')}.jsonl"
        with open(os.path.join(out_dir, out_name), "w", encoding="utf-8") as f:
            for r in sorted(recs, key=lambda x: (x["date"], x["hash"])):
                f.write(json.dumps(public_row(r), ensure_ascii=False,
                                   sort_keys=True) + "\n")

    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Replicate and extend the Heim Ascend commit counts."
    )
    parser.add_argument("repos_dir", help="parent directory containing clones")
    parser.add_argument("out_dir", help="directory for summary and JSONL output")
    parser.add_argument(
        "--as-of",
        required=True,
        type=validate_date,
        help="inclusive author-date cutoff (YYYY-MM-DD)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        main(args.repos_dir, args.out_dir, args.as_of)
    except MiningError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
