# GitCode activity snapshot through 2026-08-19

This directory was first produced as a live observation of the three declared
`master` branches:

```bash
python3 mine_gitcode_activity.py <gitcode_repos_dir> \
  data/gitcode-2026-08-19 --as-of 2026-08-19
```

The live command intentionally omitted `--replay-summary`. It was then replayed
from the newly recorded SHAs, and all three generated files were byte-identical:

```bash
python3 mine_gitcode_activity.py <gitcode_repos_dir> <replay_out> \
  --as-of 2026-08-19 \
  --replay-summary data/gitcode-2026-08-19/gitcode_summary.json
```

The cutoff is inclusive and uses each commit's author-local calendar date.
Because retrieval occurred during 2026-08-19 in Asia/Taipei, both the day and
the August monthly bucket are partial observations. `RUN.json` records the
retrieval and reproducibility metadata; `gitcode_summary.json` records the
three exact source SHAs.

The observation contains 8,283 commits: 5,264 in `ops-transformer`, 2,501 in
`ops-math`, and 518 in `catlass`. Of 7,562 non-merge, non-automation commits,
6,547 touch the declared core implementation roots (86.6%). These are three
purposively selected repositories, not a census of the CANN organization.

Files:

- `gitcode_summary.json`: repository/ref provenance and aggregate metrics.
- `gitcode_commits.jsonl`: one data-minimized row per included commit.
- `gitcode_monthly.csv`: per-repository and combined monthly series.
- `RUN.json`: retrieval and reproducibility metadata for this observation.

Names and full email addresses are omitted. Commit hashes, subjects, top-level
paths, domain tiers, and deterministic identity hashes remain auditable and
linkable to public history. The snapshot measures visible activity, not code
quality, hardware performance, deployment, or employment.
