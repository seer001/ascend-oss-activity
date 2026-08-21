# GitCode activity snapshot with author dates through 2026-07-10

This directory is the checked-in output of:

```bash
python3 mine_gitcode_activity.py <repos_dir> data/gitcode-2026-07-10 \
  --as-of 2026-07-10 \
  --replay-summary data/gitcode-2026-07-10/gitcode_summary.json
```

The three public repositories were resolved on 2026-08-07 at the `master`
SHAs recorded in `gitcode_summary.json`. The date filter uses author date
to remain consistent with the original Heim-calibration script. This is not
a historical snapshot of the branch tips as they stood on July 10; a live
rerun may drift if a later-added commit carries an earlier author date. Use
the recorded SHAs for exact replay.

Files:

- `gitcode_summary.json`: repository/ref provenance and aggregate metrics
  (`schema_version` 2).
- `gitcode_commits.jsonl`: one data-minimized row per included commit,
  including the commit's sorted top-level path list (`top_level_dirs`) so
  the core-path flag can be audited from this file alone.
- `gitcode_monthly.csv`: per-repository and combined monthly series. The
  final month (2026-07) covers only July 1–10 because of the author-date
  cutoff; treat it as a partial month when plotting.

Author-name and full-email fields are not included. Each record stores a
deterministic SHA-256 pseudonymous identity and a mutually exclusive domain
tier. Commit hashes and subjects are retained for audit, so the records
remain linkable to their public upstream history and are not anonymous.
Email-like strings in subjects receive best-effort redaction.

The snapshot measures public git activity. It does not contain source-code
blobs and does not establish performance, quality, deployment, or
employment.
