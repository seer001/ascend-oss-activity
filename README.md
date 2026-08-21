# Ascend OSS Engineering Activity

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22040904.svg)](https://doi.org/10.5281/zenodo.22040904)

This repository measures **publicly visible engineering activity** around
Huawei Ascend and CANN. It independently calibrates the public GitHub
counts that Lennart Heim published on 2026-03-31
([X thread](https://x.com/ohlennart/status/2039001304169623576), with a
[LinkedIn cross-post](https://www.linkedin.com/posts/lennartheim_huawei-added-support-for-its-ascend-ai-chips-activity-7444771757829484544-Z4mn)),
extends the observation to three selected CANN repositories on GitCode, and
uses the Kimi K3 launch window as one bounded case.

It does **not** measure hardware performance, production readiness, code
quality, or the causal effect of export controls.

中文說明：[ANALYSIS.md](ANALYSIS.md) · English analysis:
[ANALYSIS_EN.md](ANALYSIS_EN.md) · Method: [English](METHOD.md) ·
[中文](METHOD_ZH.md)

## The argument this repository can support

1. **Heim's scale is independently recoverable.** In the same fixed window,
   this repository finds 2,685 `vllm-ascend` commits versus Heim's roughly
   2,420. For `triton-ascend`, the narrow Huawei-domain count is 301 in the
   frozen 2026-07-10 snapshot and 302 in the dated 2026-08-19 observation,
   close to Heim's roughly 300. The full fixed-window `triton-ascend` count
   moves from 1,528 to 2,011 because the later ref exposes backfilled upstream
   history; that full-history drift is not substituted for the narrow anchor.
2. **Heim's GitHub frame omits a large, lower-level public workstream.** The
   default-branch histories of three selected CANN operator repositories on
   GitCode contain 8,283 commits in the 2026-08-19 observation. After
   excluding merges and automation, 6,547 of 7,562 commits (86.6%) touch the
   declared core implementation roots. The frozen 2026-07-10 observation is
   retained separately at 6,889 commits.
3. **The Kimi K3 launch window shows fast, plausibly pre-coordinated
   adaptation activity.** On the weights-release day itself, the dedicated
   `vllm-ascend` repository received support proposals and a deployment
   guide (the guide merged within five minutes of filing); the core support
   proposal was merged four days after the release. Seventeen Ascend/NPU-
   targeted Kimi K3 pull requests are tracked with dated status snapshots.
   Activity is not evidence of correctness or performance.

The 2026-08-19 GitHub observation contains 11,265 rows across its eight
declared repository rules; the GitCode observation contains 8,283 commits
across three selected default-branch histories. These are different sampling
frames and workflows. The totals are reported as separate evidence blocks,
not added, divided, or used to rank platforms.

## Evidence blocks

| Block | Unit | Dated boundary | Intended use |
|---|---|---|---|
| Heim calibration | Git commits in selected GitHub repositories | Fixed author-date window 2025-04-01 through 2026-03-31; observed in the 2026-07-10 and 2026-08-19 snapshots | Check whether the published order of magnitude is recoverable, while exposing ref drift |
| GitHub dated observation | Rows matching the eight declared repository rules | Author-local date through 2026-08-19; exact source SHAs recorded | Extend the selected histories without overwriting the frozen baseline |
| GitCode extension | Default-branch commits in three selected CANN operator repositories | Frozen 2026-07-10 cutoff plus a separately pinned 2026-08-19 observation | Measure a lower-level workstream outside Heim's frame |
| Kimi K3 case | 17 manually classified Ascend/NPU-targeted PRs from a frozen launch window | PRs created 2026-07-26 through 2026-08-01; status snapshots 2026-08-05, 2026-08-08, and [2026-08-19](k3-adaptation/snapshots/2026-08-19.json) | Observe response timing and later states without treating proposals as deployments or raw search hits as new cases |

Both commit miners compare the commit's **author-local calendar date** with
the inclusive cutoff. Retrieval occurred during August 19, so the August 19
day and the August monthly buckets are partial observations. A later moving
ref can also make an older-author-dated commit newly reachable; dated live
observations are full recomputations, not append-only deltas.

## Repository map

| Path | Purpose |
|---|---|
| `mine_commits.py` | GitHub-side Heim calibration from local clones (pseudonymized rows) |
| `summary.json`, `raw_*.jsonl` | Frozen 2026-07-10 GitHub-side snapshot; rows carry email domains and deterministic identity hashes, not names or addresses |
| `data/github-2026-08-19/` | Pinned, data-minimized GitHub observation through the partial August 19 cutoff |
| `mine_gitcode_activity.py` | Deterministic GitCode default-branch activity measurement |
| `data/gitcode-2026-07-10/` | Data-minimized GitCode summary, per-commit records (with top-level path lists), and monthly series |
| `data/gitcode-2026-08-19/` | Pinned GitCode observation plus live-to-replay run metadata |
| `data/UPDATE-2026-08-19.md` | Hash-level reconciliation of the frozen and later commit observations |
| `k3-adaptation/` | Bounded Kimi K3 case: classified PR set, dated snapshots, archived PR descriptions |
| `METHOD.md` / `METHOD_ZH.md` | Scope, metric definitions, exclusions, and claim boundary |
| `tests/` | Unit tests plus regression checks that recompute the checked-in aggregates from the checked-in rows |
| `.github/workflows/ci.yml` | Compile, test, and data-consistency checks |

## Reproduce

Python 3.9+ is sufficient for the git-history scripts.

### 1. Heim calibration

Clone the eight declared repositories, preserving these directory names:

```bash
git clone https://github.com/vllm-project/vllm-ascend.git <repos_dir>/vllm-ascend
git clone https://github.com/triton-lang/triton-ascend.git <repos_dir>/triton-ascend
git clone --filter=blob:none --single-branch https://github.com/Ascend/pytorch.git <repos_dir>/torch_npu
git clone --filter=blob:none --single-branch https://github.com/sgl-project/sglang.git <repos_dir>/sglang
git clone --filter=blob:none --single-branch https://github.com/ggml-org/llama.cpp.git <repos_dir>/llama.cpp
git clone --filter=blob:none --single-branch https://github.com/InternLM/lmdeploy.git <repos_dir>/lmdeploy
git clone --filter=tree:0 --single-branch https://github.com/pytorch/pytorch.git <repos_dir>/pytorch
git clone --filter=tree:0 --single-branch https://github.com/huggingface/transformers.git <repos_dir>/transformers
```

For the new dated observation, run:

```bash
python3 mine_commits.py <repos_dir> data/github-2026-08-19 \
  --as-of 2026-08-19
```

The script validates each origin URL, rejects shallow clones, and writes
pseudonymized per-commit rows: author names and email addresses are
omitted; each row keeps the email domain plus deterministic SHA-256
identity/name hashes so that every aggregate in `summary.json` can be
recomputed from the rows (the checked-in test suite does exactly that).
The checked-in root `summary.json` and `raw_*.jsonl` remain the frozen
2026-07-10 output; they are not overwritten by the new snapshot. The new
summary records each exact `HEAD` SHA, and `RUN.json` records a byte-identical
rerun against those pinned refs. Because the old snapshot predates source-SHA
recording, its rows and checksums are preserved evidence but its then-current
ref cannot be reconstructed from metadata alone. See
[`data/UPDATE-2026-08-19.md`](data/UPDATE-2026-08-19.md) before interpreting
the difference as new work.

### 2. GitCode extension

```bash
git clone --filter=blob:none --no-checkout \
  https://gitcode.com/cann/ops-transformer.git <repos_dir>/ops-transformer
git clone --filter=blob:none --no-checkout \
  https://gitcode.com/cann/ops-math.git <repos_dir>/ops-math
git clone --filter=blob:none --no-checkout \
  https://gitcode.com/cann/catlass.git <repos_dir>/catlass

python3 mine_gitcode_activity.py <repos_dir> data/gitcode-2026-08-19 \
  --as-of 2026-08-19

python3 mine_gitcode_activity.py <repos_dir> <replay_out> \
  --as-of 2026-08-19 \
  --replay-summary data/gitcode-2026-08-19/gitcode_summary.json
```

This command fails if a repository is missing or its origin does not match
the declared public GitCode source, or if a clone is shallow. The replay
option traverses the three recorded SHAs rather than today's moving
`master`; omit it only when intentionally making a new live observation. The
checked-in 2026-08-19 live output and fixed-SHA replay are byte-identical. To
replay the preserved 2026-07-10 observation instead, use its dated summary and
the original cutoff. Author-name and full-email fields are omitted; the
auditable rows retain public commit metadata, each commit's top-level path
list, and
deterministic, linkable pseudonymous identity hashes. They are
data-minimized, not anonymous.

### 3. Kimi K3 case

The scripts in `k3-adaptation/` require an authenticated read-only `gh`
CLI. See [k3-adaptation/METHOD.md](k3-adaptation/METHOD.md) before
interpreting the raw full-text search counts. The fixed 17-PR cohort remains
unchanged in the [2026-08-19 status snapshot](k3-adaptation/snapshots/2026-08-19.json):
6 merged, 7 closed unmerged, and 4 open. Its 629 raw full-text matches are a
drifting discovery upper bound and do not expand the manually classified
cohort.

## What the evidence does not establish

- Commit or PR volume is not hardware speed, software quality, successful
  execution, or production deployment.
- A corporate email domain is a conservative observed attribution signal,
  not a complete employment census. Huawei and partner domains are separate.
- A PR title or model mention is a candidate, not automatically an
  adaptation.
- Same-day launch-window timing is consistent with pre-release coordination;
  it does not establish who prepared or directed the work.
- One Kimi case does not establish a general model-launch pattern.
- Temporal sequence does not establish that export controls or any policy
  caused the observed activity.

## Citing

See [CITATION.cff](CITATION.cff). Each release is archived on Zenodo:

| DOI | Resolves to | Use it when |
|---|---|---|
| [10.5281/zenodo.22040904](https://doi.org/10.5281/zenodo.22040904) | Concept record, always the latest version | Referring to this dataset in general |
| [10.5281/zenodo.22040905](https://doi.org/10.5281/zenodo.22040905) | Version 1.0.0 specifically | Citing figures you actually used, so a reader can retrieve the exact rows behind them |

Cite the **version** DOI in published work. The figures in this repository are
tied to dated snapshots, and a later version may revise them.

Social-media sources (the Heim thread) and vendor pages are cited with access
dates in the analysis documents; readers should rely on the dated snapshots
checked into this repository rather than on live pages.

## License and data note

Code is released under the [MIT License](LICENSE). Analysis text and the
snapshot data files are released under [CC BY 4.0](LICENSE-CONTENT.md).
Snapshot records are derived from public git and GitHub metadata; upstream
repository licenses continue to govern upstream code.
