#!/usr/bin/env python3
"""Author-domain audit for Kimi-K3 candidate PRs in a fixed creation window.

For every PR matching the full-text query in each target repository, the
script collects the PR author's login and the commit author emails, then
publishes only aggregate, data-minimized results:

  - per-PR rows containing public work metadata (number, creation time,
    title) without author logins or per-PR email domains;
  - one aggregate email-domain histogram across the window;
  - aggregate flag counts for Moonshot-affiliated domains and public
    MoonshotAI organization membership, plus the flagged PR numbers.

Method notes:
  - The query is a raw full-text match, so the PR set is an upper bound that
    includes PRs merely mentioning the model.
  - Commit emails are self-reported git metadata; absence of a corporate
    domain is not evidence of non-affiliation.
  - Public org membership is opt-in; non-membership proves nothing on its
    own.

Requires: gh (authenticated), python3. Read-only; no repository is modified.

Usage: ./audit_k3_pr_authors.py [--window 2026-07-26..2026-08-01] [--out FILE]
"""

import argparse
import datetime
import json
import pathlib
import subprocess
import sys

REPOS = [
    "vllm-project/vllm",
    "sgl-project/sglang",
    "vllm-project/vllm-ascend",
]
QUERY = "Kimi-K3"
SEARCH_LIMIT = 300
# Corporate domains that indicate a human Moonshot-affiliated commit author.
# msh.team is Moonshot's engineering domain (seen in Kimi technical reports).
FLAG_DOMAINS = ("moonshot.cn", "moonshot.ai", "msh.team", "kimi.com", "kimi.team")
# noreply@ addresses on these domains are AI/bot attributions (the Kimi model
# credited as a commit co-author by third-party developers), not evidence of a
# human Moonshot employee. Counted separately.
BOT_PREFIX = "noreply@"


def gh(*args: str) -> str:
    return subprocess.run(
        ["gh", *args], check=True, capture_output=True, text=True
    ).stdout


def matches_domain(domain: str, candidates) -> bool:
    domain = domain.lower()
    return any(
        domain == candidate or domain.endswith("." + candidate)
        for candidate in candidates
    )


def search_prs(repo: str, window: str) -> list:
    out = gh(
        "search", "prs", QUERY, "--repo", repo, "--created", window,
        "--limit", str(SEARCH_LIMIT),
        "--json", "number,title,author,createdAt",
    )
    return json.loads(out)


def pr_commit_emails(repo: str, number: int) -> list:
    out = gh(
        "pr", "view", str(number), "--repo", repo, "--json", "commits",
        "--jq", "[.commits[].authors[].email]",
    )
    return json.loads(out)


def moonshot_public_members() -> list:
    try:
        out = gh("api", "orgs/MoonshotAI/public_members", "--paginate",
                 "--jq", "[.[].login]")
        members = []
        for line in out.strip().splitlines():
            members.extend(json.loads(line))
        return sorted(set(members))
    except subprocess.CalledProcessError:
        return []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", default="2026-07-26..2026-08-01")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    today = datetime.date.today().isoformat()
    out_path = pathlib.Path(
        args.out
        or pathlib.Path(__file__).parent
        / "snapshots" / f"authors-{args.window.replace('..', '_')}-run{today}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)

    members = moonshot_public_members()
    result = {
        "run_date": today,
        "query": QUERY,
        "search_limit": SEARCH_LIMIT,
        "window_created": args.window,
        "flag_domains": list(FLAG_DOMAINS),
        "moonshotai_public_member_count": len(members),
        "privacy_note": (
            "Author logins and per-PR email domains are collected for "
            "aggregation but not published. Rows retain public work "
            "metadata only; domains appear in one aggregate histogram."
        ),
        "repos": {},
        "domain_histogram": {},
        "flagged_prs": [],
    }

    histogram = {}
    for repo in REPOS:
        prs = search_prs(repo, args.window)
        rows = []
        for pr in sorted(prs, key=lambda p: p["number"]):
            n = pr["number"]
            login = (pr.get("author") or {}).get("login", "")
            try:
                emails = sorted(set(pr_commit_emails(repo, n)))
                fetch_error = False
            except subprocess.CalledProcessError:
                emails = []
                fetch_error = True
            human = [e for e in emails if not e.lower().startswith(BOT_PREFIX)]
            bots = [
                e for e in emails
                if e.lower().startswith(BOT_PREFIX)
                and matches_domain(e.rsplit("@", 1)[-1], FLAG_DOMAINS)
            ]
            domains = sorted({e.split("@")[-1].lower() for e in human if "@" in e})
            for d in domains:
                histogram[d] = histogram.get(d, 0) + 1
            flag_reasons = []
            if any(matches_domain(d, FLAG_DOMAINS) for d in domains):
                flag_reasons.append("moonshot_domain_commit_email")
            if login and login in members:
                flag_reasons.append("moonshotai_public_member_author")
            row = {
                "number": n,
                "created_at": pr["createdAt"],
                "title": pr["title"],
                "model_bot_attribution_count": len(bots),
            }
            if fetch_error:
                row["commit_email_fetch_error"] = True
            rows.append(row)
            if flag_reasons:
                result["flagged_prs"].append(
                    {"repo": repo, "number": n, "reasons": flag_reasons}
                )
        limit_reached = len(prs) >= SEARCH_LIMIT
        result["repos"][repo] = {
            "pr_count": len(rows),
            "limit_reached": limit_reached,
            "prs": rows,
        }

    result["domain_histogram"] = dict(
        sorted(histogram.items(), key=lambda kv: (-kv[1], kv[0]))
    )
    out_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    total = sum(r["pr_count"] for r in result["repos"].values())
    print(f"window={args.window}  PRs audited: {total}")
    for repo, r in result["repos"].items():
        print(f"  {repo}: {r['pr_count']}")
    print(f"flagged PRs: {len(result['flagged_prs'])}")
    for f in result["flagged_prs"]:
        print("  FLAG:", f["repo"], f["number"], ",".join(f["reasons"]))
    print(f"top domains: {dict(list(result['domain_histogram'].items())[:8])}")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FileNotFoundError as exc:
        print(f"error: required executable not found: {exc.filename}", file=sys.stderr)
        raise SystemExit(1)
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip()[:500]
        print(f"error: gh command failed: {detail}", file=sys.stderr)
        raise SystemExit(1)
