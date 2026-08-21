# GitHub activity snapshot through 2026-08-19

This directory is the checked-in output of:

```bash
python3 mine_commits.py <github_repos_dir> data/github-2026-08-19 \
  --as-of 2026-08-19
```

The cutoff is inclusive and uses each commit's author-local calendar date.
The run finished during 2026-08-19 in Asia/Taipei, so both the day and the
August monthly bucket are partial observations. The retrieval timestamp,
miner revision, and determinism result are recorded in `RUN.json`; each
repository's exact source SHA is recorded in `summary.json`.

The eight declared repositories yielded 11,265 data-minimized rows from
2025-04-01 through the cutoff. The frozen 2026-07-10 snapshot remains at the
repository root and is not overwritten by this observation.

This is a full recomputation, not an append. In particular, the current
`triton-ascend` history contains many commits with author dates before the old
cutoff that were not reachable from the earlier observed ref. Therefore the
difference from 2026-07-10 must not be described as only work performed after
July 10. See `../UPDATE-2026-08-19.md` for the hash-level reconciliation.

Files:

- `summary.json`: aggregate metrics, origins, and resolved `HEAD` SHAs.
- `raw_*.jsonl`: one pseudonymized row per included commit under each
  repository's declared mining rule.
- `RUN.json`: retrieval and reproducibility metadata for this observation.

Author names and full email addresses are omitted. Deterministic identity
hashes, public commit hashes, subjects, and email domains remain linkable to
public Git history; this is data minimization, not anonymity. Commit or line
volume does not establish quality, performance, deployment, or employment.
