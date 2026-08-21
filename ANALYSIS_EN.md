# Public Commit Activity Around Huawei Ascend: A Narrow Replication and Extension of Heim (2026)

**Observation cutoffs:** the frozen commit snapshot remains July 10, 2026;
a separately pinned commit observation runs through the partial August 19,
2026 author-local cutoff. Kimi K3 status snapshots are dated August 5, August
8, and August 19, 2026.

## Answer first

This repository supports one bounded claim: substantial, Huawei-associated
engineering activity is visible in public software histories around the
Ascend stack, and some of that activity concerns adapting the stack to
newly released model architectures.

The evidence has three parts:

1. a fixed-window calibration against Lennart Heim's published counts;
2. an extension to the default-branch histories of three selected CANN
   repositories on GitCode; and
3. a classified set of launch-window Kimi K3 support PRs on GitHub.

These observations measure public repository activity. They do **not**
establish hardware performance, software quality, successful deployment,
Huawei's total engineering effort, GitCode's importance relative to GitHub,
or a causal response to export controls or model releases.

The August 19 GitHub observation contains 11,265 rows under eight declared
rules; the GitCode observation contains 8,283 commits from three selected
default-branch histories. Those totals are intentionally not combined or
used as a platform ratio: repository selection and contribution workflows
differ.

For both commit blocks, the cutoff compares the calendar date in each
commit's author timestamp and its own timezone. It is not a UTC-normalized
date, committer date, or retrieval date. A later moving ref can expose an
older-author-dated commit or drop a previously reachable commit, so the
August observation is a full recomputation rather than an append to July.

## 1. Fixed-window calibration against Heim

On March 31, 2026, Lennart Heim reported roughly 3,000 commits and 1.08
million lines of code for Ascend support across several open-source AI
frameworks during the preceding twelve months, attributing about 80–95% of
the relevant contributions to Huawei-affiliated engineers
([X thread](https://x.com/ohlennart/status/2039001304169623576), the
primary source of the per-repository figures, read and preserved by this
project's author on 2026-07-10; a
[LinkedIn cross-post](https://www.linkedin.com/posts/lennartheim_huawei-added-support-for-its-ascend-ai-chips-activity-7444771757829484544-Z4mn)
summarizes the same analysis).

For calibration, we apply an inclusive author-date window corresponding to
Heim's period, **2025-04-01 through 2026-03-31**, and inspect local git
histories with [`mine_commits.py`](mine_commits.py):

| Repository and counting rule | Heim | 2026-07-10 / 2026-08-19 observation | Reading |
|---|---:|---:|---|
| [`vllm-ascend`](https://github.com/vllm-project/vllm-ascend), all commits in the dedicated adaptation repository | ~2,420 | 2,685 / 2,685 | Same order; local count about 11% higher. The simple rule counts automation too (32 dependabot commits in the window) |
| [`triton-ascend`](https://github.com/triton-lang/triton-ascend), commits authored with a Huawei corporate domain | ~300 | 301 / 302 | Near numerical agreement under this narrower attribution rule despite large full-history drift |
| [`sglang`](https://github.com/sgl-project/sglang), Ascend/CANN/NPU message-or-path candidates | 210+ | 361 / 361 | Same order; candidate counts are rule-sensitive and are not 361 confirmed adaptation events |
| [`llama.cpp`](https://github.com/ggml-org/llama.cpp), CANN/Ascend message-or-path candidates | 93 | 127 / 127 | Same order, still rule-sensitive |
| [`pytorch`](https://github.com/pytorch/pytorch), Ascend/NPU commit-message candidates | ~25 | 8 / 8 | Not replicated under this stricter message-only rule; reported as a divergence, not a correction of Heim |

This is a calibration, not a claim that every element of Heim's analysis has
been exactly reproduced. The `vllm-ascend` gap can arise from ref snapshots,
merge handling, or repository-specific inclusion rules. For
`triton-ascend`, the mined `triton-lang/triton-ascend` default branch carries
upstream Triton ancestry. Between the dated observations, 1,082 hashes with
author dates no later than July 10 become newly reachable and one formerly
observed hash disappears. Its full fixed-window count consequently changes
from 1,528 to 2,011, but the recognized Huawei-domain subset changes only
from 301 to 302. The old snapshot did not record its source SHA, so the
backfilled rows cannot be timed as engineering performed after July 10. A
same-named repository also exists under the `Ascend` GitHub organization;
counts from the two repositories must not be conflated.

Heim's aggregate 1.08-million-line estimate and 80–95% affiliation range
are retained as his reported baseline. This repository does not
independently validate those two figures: lines-of-code results depend
heavily on path and generated-file rules, while affiliation cannot be
reconstructed reliably from email domains alone.

### What the GitHub email metadata can and cannot attribute

Observed author-email domains across all 11,265 rows in the 2026-08-19
GitHub observation (author-local dates from 2025-04-01 through the cutoff):

| Domain | Rows | Share |
|---|---:|---:|
| `users.noreply.github.com` | 2,656 | 23.6% |
| `huawei.com` | 2,242 | 19.9% |
| `gmail.com` | 1,736 | 15.4% |
| `163.com` | 1,518 | 13.5% |
| `qq.com` | 1,395 | 12.4% |
| `openai.com` | 517 | 4.6% |
| `h-partners.com` | 285 | 2.5% |
| `outlook.com` | 211 | 1.9% |

Nearly a quarter of GitHub-side commits hide their address behind GitHub
no-reply, and personal-mail domains dominate the rest; within the Heim
window, 36.4% of `vllm-ascend` commits use no-reply addresses. GitHub-side
corporate-domain shares are therefore **floors**, and this is the main
reason our conservative domain-only attribution (for example, 9.5% of
`vllm-ascend` window commits from Huawei or partner domains) sits far below
Heim's 80–95% estimate, which used additional attribution signals beyond
email domains. The same measurement on the GitCode operator repositories
yields high corporate-domain shares (next section) largely because
contributors there commit with work addresses. Domain shares must not be
compared across platforms, and neither number is an employment census. The
frozen 8,902-row domain table remains recoverable from the root snapshot; it
has not been overwritten.

## 2. Extension to three selected GitCode/CANN histories

Heim's comparison focused on GitHub projects. We extend the observation set
to three repositories in the public
[CANN organization on GitCode](https://gitcode.com/cann). The three are a
purposive sample chosen for their stated purpose — transformer operators,
math operators, and matmul kernel templates. They are not a census: on
2026-08-08 the organization listed 75 public repositories, including at
least eleven other `ops-*` operator libraries that this project does not
measure, so these totals understate organization activity and support no
organization-level claim.

The frozen source refs were resolved and locked on **2026-08-07**, then
filtered to author-local dates on or before **2026-07-10**. A second live
observation resolved new `master` SHAs and applied an inclusive
**2026-08-19** author-local cutoff. Retrieval occurred during August 19, so
that day and the August bucket are partial. Neither observation reconstructs
what the branches contained at the end of its cutoff day:

| Selected repository | Included author dates in 08-19 observation | Commits 07-10 -> 08-19 | Huawei + partner tiers* 07-10 -> 08-19 | Core-path commits / eligible** 07-10 -> 08-19 |
|---|---|---:|---:|---:|
| [`ops-transformer`](https://gitcode.com/cann/ops-transformer) | 2025-09-28–2026-08-19 | 4,377 -> 5,264 | 4,028 (92.0%) -> 4,825 (91.7%) | 3,698 / 4,071 (90.8%) -> 4,482 / 4,907 (91.3%) |
| [`ops-math`](https://gitcode.com/cann/ops-math) | 2025-09-25–2026-08-19 | 2,040 -> 2,501 | 1,625 (79.7%) -> 1,996 (79.8%) | 1,433 / 1,758 (81.5%) -> 1,819 / 2,176 (83.6%) |
| [`catlass`](https://gitcode.com/cann/catlass) | 2025-01-22–2026-08-19 | 472 -> 518 | 366 (77.5%) -> 394 (76.1%) | 220 / 434 (50.7%) -> 246 / 479 (51.4%) |

\* Automation is classified first and reported separately, even when an
automation identity uses a Huawei-domain address.

\** Eligible means non-merge and non-automation. Core paths are the
declared operator/library implementation roots in [`METHOD.md`](METHOD.md);
each published row stores the commit's top-level path list, so this flag is
auditable from the checked-in data without recloning.

The tier share is the fraction of all commits assigned to a recognized
Huawei-family domain (`huawei.com` or `hisilicon.com`) or an identified
partner domain (`h-partners.com` or `huawei-partners.com`) after automation
is separated. It is an attribution proxy, not a verified employee census.

Corporate-domain matching is a narrow observed attribution proxy for
Huawei- or partner-associated authorship in public metadata. Affiliated
contributors may use personal or no-reply addresses and therefore fall
outside the numerator. Conversely, partner-domain authors should not be
relabeled as Huawei employees, and git author metadata is self-reported.

The defensible inference is limited: these three selected CANN repositories
contain sustained default-branch activity. In the 2026-08-19 observation,
6,547 of 7,562 non-merge, non-automation commits (86.6%) touch declared core
implementation roots, compared with 5,351 of 6,263 (85.4%) in the frozen
observation. Aggregate monthly counts through 2026-06 are unchanged; July
becomes a complete 1,058-commit bucket under the later ref, while August
contains 790 commits through the partial August 19 cutoff. That is direct
path-level evidence of
operator/library work, not a grade of difficulty, correctness, originality,
or performance.

The table does not show that:

- the three repositories represent all of CANN or Huawei's software work;
- GitCode is the principal venue for that work;
- their commit counts can be added to Heim's GitHub total as one comparable
  measure; or
- more commits imply more unique code, engineering hours, quality, or
  performance.

Platform workflows are not comparable. Default-branch histories can differ
in imported ancestry, merge policy, squash behavior, bot use, and review
workflow. A GitCode commit and a GitHub pull request are also different
units. For that reason, this repository reports the three histories
separately and makes no cross-platform multiplier claim.

## 3. Kimi K3 launch window: a classified case set

[Kimi's official product history](https://www.kimi.com/help/agent/agent-overview)
(accessed 2026-08-08) records the full Kimi K3 weights becoming available
on **2026-07-27**. From a frozen candidate window (PRs created 2026-07-26
through 2026-08-01), 17 pull requests were manually classified as
Ascend/NPU-targeted Kimi K3 work: 15 in the dedicated
`vllm-project/vllm-ascend` repository and 2 `[NPU]`-tagged PRs in
`sgl-project/sglang`.

The [2026-08-19 snapshot](k3-adaptation/snapshots/2026-08-19.json), retrieved
at 2026-08-19T15:36:25Z, preserves the same fixed 17-PR cohort. It records 6
merged, 7 closed unmerged, and 4 open cases. The 629 raw search hits are a
drifting discovery upper bound, not 629 adaptations and not an expansion of
the manually classified set.

Key observations, all frozen in dated snapshots under
[`k3-adaptation/snapshots/`](k3-adaptation/snapshots/):

- **Same-day cluster.** On the release day itself, `vllm-ascend` received
  four Kimi K3 PRs between 15:17 and 15:38 UTC — two support proposals, a
  deployment guide
  ([#12952](https://github.com/vllm-project/vllm-ascend/pull/12952), merged
  five minutes after filing, describing ModelScope W4A8 weights, Atlas 800
  A3 images, and multi-node deployment layouts), and a documentation fix
  merged within nineteen minutes. SGLang received
  [#32544](https://github.com/sgl-project/sglang/pull/32544) (`[NPU][Kimi]
  Support Kimi-K3 on NPU`) the same day.
- **Merged support within four days.** The core proposal
  [#12950](https://github.com/vllm-project/vllm-ascend/pull/12950)
  (`Support Kimi K3 on Ascend`) was merged on 2026-07-31.
- **An explicit 910C exhibit.** On the next UTC day,
  [#32604](https://github.com/sgl-project/sglang/pull/32604) (`[NPU] Day0
  Support Kimi-K3 on 910C`) named Ascend 910C, the CANN stack, the PyPTO
  tile DSL, and a 3× Atlas 800I A3 = 48× 910C test cluster; its
  description is archived in the snapshots. It and the other SGLang case PR
  remained open as of 2026-08-19; #32604 still showed no public metadata
  update after its filing day.
- **Later states without cohort expansion.** Relative to August 8,
  `vllm-ascend` #13277 moved from open to merged, while #13065, #13315, and
  #13323 moved from open to closed unmerged. The remaining open cases #13225
  and #13286 were updated on August 19. Across both repositories the fixed set
  therefore stood at 6 merged, 7 closed unmerged, and 4 open.

The same-day, minutes-apart timing with complete deployment configurations
is consistent with adaptation prepared before the public weights release.
Public metadata cannot show who prepared or coordinated that work, and
merges show maintainer acceptance of code, not verified correctness or
performance. One launch window does not establish a general pattern.

## What this evidence can support in an article

A technically cautious formulation is:

> Public repository histories show a large and concentrated body of
> Ascend-related engineering activity. Fixed-window counts for
> `vllm-ascend` and Huawei-domain commits in `triton-ascend` are close to
> Heim's published anchors; three selected CANN operator histories add
> direct path-level evidence from GitCode; and when Kimi K3's weights were
> released, Ascend-targeted support PRs — including a deployment guide —
> appeared in public inference frameworks the same day, with a core
> support proposal merged within four days.

The key word is **activity**. The repository measures visible engineering
actions—commits and pull requests—rather than the resulting system's
capability or commercial success.

## Reproducing the observations

### GitHub calibration

Clone the relevant repositories at the intended refs (commands in
[`README.md`](README.md)), then run:

```bash
python3 mine_commits.py <repos_dir> data/github-2026-08-19 \
  --as-of 2026-08-19
```

The script uses Python's standard library, validates origins, rejects
shallow clones, and writes pseudonymized per-commit rows plus aggregate
results in `summary.json`. Every aggregate is recomputable from the rows. The
root 2026-07-10 output remains frozen; because it predates ref-SHA recording,
its exact then-current source history cannot be recovered from metadata. The
dated 2026-08-19 summary records all eight source SHAs, and a full second run
against those refs produced nine byte-identical files. See the checked-in
[`reconciliation note`](data/UPDATE-2026-08-19.md) for hash-level drift.

### GitCode extension

Clone the three repositories listed in [`README.md`](README.md), then run:

```bash
python3 mine_gitcode_activity.py <repos_dir> data/gitcode-2026-08-19 \
  --as-of 2026-08-19

python3 mine_gitcode_activity.py <repos_dir> <replay_out> \
  --as-of 2026-08-19 \
  --replay-summary data/gitcode-2026-08-19/gitcode_summary.json
```

The script validates each public origin, rejects shallow clones, and fails
on missing inputs. Replay mode traverses the recorded SHAs; omitting the
replay option intentionally creates a new observation from today's
`master`. It writes data-minimized commit rows (including per-commit
top-level path lists), a summary, and a monthly CSV. Author-name and
full-email fields are omitted, but the retained public commit metadata and
deterministic identity hashes remain linkable and are not anonymous. The live
2026-08-19 output and replay are byte-identical. The original observation
remains in [`data/gitcode-2026-07-10/`](data/gitcode-2026-07-10/); replay it
with its own summary and cutoff.

### Kimi K3 snapshots

With an authenticated GitHub CLI:

```bash
bash k3-adaptation/snapshot_k3_prs.sh
python3 k3-adaptation/audit_k3_pr_authors.py --window 2026-07-26..2026-08-01
```

Search results drift as GitHub indexes and updates pull requests (total raw
matches: 290 on 2026-08-05, 373 on 2026-08-08, and 629 on 2026-08-19). These
are discovery upper bounds; the manually classified cohort remains the same
17 PRs. Cite the dated snapshots for historical statements.

## Claim boundary

The repository is an auditable record of selected public software activity.
It should not be used by itself to infer Ascend performance, compatibility
completion, market position, organizational priority, or the cause of the
observed work.
