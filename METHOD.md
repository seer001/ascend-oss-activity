# Method and claim boundary

中文版：[METHOD_ZH.md](METHOD_ZH.md)

## Research question

Can public repository histories show sustained Ascend/CANN compatibility
work, including lower-level operator software, and does one recent model
launch offer a concrete example of that response pattern?

This is an **engineering-activity measurement** question. It is not a
hardware benchmark, deployment audit, employment census, or causal policy
evaluation.

## Three-block design

### A. Heim calibration

- Window: 2025-04-01 through 2026-03-31.
- Observations: the frozen 2026-07-10 output at the repository root and the
  separately pinned 2026-08-19 output under `data/github-2026-08-19/`. The
  window is fixed, but the reachable history can differ between observed
  refs.
- Reference: Lennart Heim's 2026-03-31 analysis
  ([X thread](https://x.com/ohlennart/status/2039001304169623576), primary
  source of the per-repository figures, read and preserved by this
  project's author on 2026-07-10;
  [LinkedIn cross-post](https://www.linkedin.com/posts/lennartheim_huawei-added-support-for-its-ascend-ai-chips-activity-7444771757829484544-Z4mn)).
- Sources: selected GitHub repository histories used to approximate the set
  in Heim's public analysis.
- Primary output: commit counts under the declared dedicated-repository or
  keyword/path candidate rule.
- Interpretation: order-of-magnitude calibration. A close count in one repo
  does not make every repository definition identical to Heim's unpublished
  implementation details.

Anchor readings:

- The most defensible point estimate is the `triton-ascend` subset authored
  from `huawei.com` or `hisilicon.com`: 301 commits in the frozen 2026-07-10
  output and 302 in the 2026-08-19 observation, against Heim's roughly 300.
  The full fixed-window total changes much more, from 1,528 to 2,011, because
  the later ref exposes backfilled upstream history. Note the
  repository-identity caution: `triton-lang/triton-ascend`
  (mined here) carries upstream Triton ancestry in its full history, so
  only the Huawei-domain subset is comparable, and a same-named repository
  exists under the `Ascend` organization. Counts from the two must not be
  conflated, and the full-history increase must not be described as work
  performed after July 10.
- The 2,685 `vllm-ascend` commits are about 11% above Heim's roughly 2,420
  and should be described as the same order of magnitude, not an exact
  match. The dedicated-repository rule counts every commit, including
  automation (for example, 47 dependabot commits appear in the mined
  `vllm-ascend` rows), matching the simplicity of Heim's headline count.
- The keyword/path candidate counts (SGLang, llama.cpp, PyTorch,
  lmdeploy, transformers) are rule-sensitive. SGLang (local 361 versus
  Heim's 210+) and llama.cpp (127 versus 93) land in the same order of
  magnitude; the strict message-only PyTorch rule finds 8 versus Heim's
  roughly 25 and is reported as a non-replication under this narrower
  rule, not as a correction of Heim.

Heim's aggregate 1.08-million-line estimate and 80–95% affiliation range
are retained as his reported baseline. This repository does not
independently validate those two figures: lines-of-code results depend
heavily on path and generated-file rules, while affiliation cannot be
reconstructed reliably from email domains alone.

### B. GitCode extension

- Repositories: `cann/ops-transformer`, `cann/ops-math`, `cann/catlass`.
- Ref: each repository's `master` default branch; the resolved commit SHA
  is stored in the output.
- Dated observations: the original cutoff is author-local date on or before
  2026-07-10. Its source refs were resolved on 2026-08-07 and locked by SHA;
  it is not a reconstruction of what each branch contained on July 10. A
  second live observation resolves new `master` SHAs and applies an inclusive
  2026-08-19 author-local cutoff. It is stored separately under
  `data/gitcode-2026-08-19/` and replays byte-identically from those SHAs.
- Partial period: retrieval occurred during August 19. The August 19 day and
  the August monthly bucket are therefore incomplete observations, even
  though the cutoff date is inclusive.
- Primary output: all default-branch commits through the cutoff.
- Supporting output: pseudonymous author identities, affiliation-domain
  tiers, monthly counts, per-commit top-level path lists, and
  non-merge/non-automation commits touching declared core implementation
  roots.

Selection: the three repositories are a purposive sample, chosen because
their stated purpose is operator/kernel implementation for the layers this
project asks about — transformer operators (`ops-transformer`),
mathematical operators (`ops-math`), and matrix-multiplication kernel
templates (`catlass`). They are not a census: on 2026-08-08 the public
CANN organization listed 75 repositories, including at least eleven other
`ops-*` operator libraries (`ops-nn`, `ops-tensor`, `ops-cv`, `ops-gnn`,
`ops-blas`, `ops-fft`, `ops-sparse`, `ops-rand`, `ops-solver`,
`ops-multimodal-fusion`, `ops-collections`) that this project does not
measure. The three-repository totals therefore understate organization
activity and support no organization-level claim.

Declared core roots:

| Repository | Core implementation roots |
|---|---|
| `ops-transformer` | `attention`, `common`, `experimental`, `ffn`, `gmm`, `mamba`, `mc2`, `mhc`, `moe`, `posembedding`, `torch_extension` |
| `ops-math` | `common`, `conversion`, `experimental`, `math`, `random` |
| `catlass` | `include`, `python`, `experimental` |

The core-path measure is a transparent proxy for implementation work. It
does not grade change size, difficulty, correctness, originality, or
performance. Each output row also stores the commit's top-level path list
(`top_level_dirs`), so the core-path flag can be audited from the
checked-in rows without recloning the repositories.

The frozen observation contains 6,889 commits, with 5,351 of 6,263 eligible
commits touching a core root (85.4%). The 2026-08-19 observation contains
8,283 commits, with 6,547 of 7,562 eligible commits touching a core root
(86.6%). Monthly counts through 2026-06 are unchanged between the two; July
becomes a complete 1,058-commit bucket under the later ref, while August has
790 commits through the partial August 19 retrieval. These numbers describe
only the three declared repositories.

### C. Kimi K3 bounded case

- Model event: Kimi K3 weights release on 2026-07-27 (vendor product
  history, accessed 2026-08-08). The hosted K3 service launched earlier in
  July; the adaptation clock uses the weights date because open-source
  execution requires the weights.
- Case set: 17 Ascend/NPU-targeted Kimi K3 pull requests, classified
  manually from the frozen 2026-07-26..2026-08-01 candidate window under
  the rule in [k3-adaptation/METHOD.md](k3-adaptation/METHOD.md).
- Status cutoffs: 2026-08-05, 2026-08-08, and 2026-08-19. The latest
  snapshot was retrieved at 2026-08-19T15:36:25Z and preserves the same 17
  manually classified cases.
- Output: per-PR timing, repository, state, merge status, and archived
  descriptions for the key exhibits.

Full-text search results remain discovery candidates; they are not counted as
adaptations without manual inspection. The 2026-08-19 search returned 629 raw
matches, a drifting discovery upper bound rather than an expanded cohort. The
fixed cases were 6 merged, 7 closed unmerged, and 4 open at that cutoff; see
[`k3-adaptation/snapshots/2026-08-19.json`](k3-adaptation/snapshots/2026-08-19.json).

## Metric definitions

### Total commits

Unique commit SHAs reachable from the declared ref whose author date is on
or before the cutoff. "Author date" means the calendar date in the commit's
author timestamp and its own timezone, not UTC conversion, committer date, or
retrieval date. This simple measure is retained for comparability with Heim's
public headline and the original repository analysis.

### Observed author identities

Unique SHA-256 values of the raw Git author name, a NUL separator, and the
lowercased author email. They are called identities—not people or
engineers—because spelling, case, whitespace, or email variants can split
one person, while shared or rewritten metadata can also occur.

Published rows on both platforms omit author-name and full-email fields.
Each row retains the public commit hash and subject, the email domain
(GitHub side), and deterministic hashes: `identity_hash` as above, plus a
`name_hash` on the GitHub side so that per-affiliation author counts remain
recomputable from the rows. These are linkable pseudonyms and data
minimization, not anonymization: a reader can consult the upstream public
Git history to recover the original metadata.

### GitHub-side affiliation tiers (`mine_commits.py`)

- `confirmed`: the author email domain is `huawei.com` or `hisilicon.com`
  (or a subdomain).
- `likely`: the domain is a recognized long-term partner domain
  (`h-partners.com`, `huawei-partners.com`, or a subdomain), **or** the
  same author name appears elsewhere in the mined set with a
  confirmed-domain address (cross-repository identity merge).
- `unknown`: everything else, including no-reply and personal addresses.

The identity-merge rule is a declared heuristic: it treats an author name
that has used a Huawei corporate address anywhere in the mined set as
likely-Huawei in repositories where the same name uses another address.
Common names can collide, so its contribution is quantified rather than
hidden: in the frozen 2026-07-10 output it upgrades 60 of 8,902 mined rows
(41 within the Heim window), and it does not affect the headline
`triton-ascend` anchor, which counts confirmed-domain commits only. In the
2026-08-19 full recomputation, one row already present in the old
`vllm-ascend` data changes from `unknown` to `likely` because a later selected
history supplies new confirmed-domain evidence for the same name. Tier labels
are therefore properties of a dated, jointly mined snapshot, not immutable
labels attached to a commit.

`unknown` is a floor artifact of email visibility, not a claim of
non-affiliation: `users.noreply.github.com` accounts for 23.4% of the frozen
rows and 23.6% of the 2026-08-19 rows (36.4% in `vllm-ascend` within the
fixed Heim window). See the domain-mix table in
[ANALYSIS_EN.md](ANALYSIS_EN.md).

### GitCode-side domain tiers (`mine_gitcode_activity.py`)

- `huawei`: `huawei.com`, `hisilicon.com` (or subdomains)
- `partner`: `h-partners.com`, `huawei-partners.com` (or subdomains)
- `automation`: `cann.team` addresses (the organization's CI identity), or
  an author name containing the standalone token `bot` or `robot`
  (matching whole tokens only, so human names that merely contain the
  letters "bot" are not swept in)
- `other`: all remaining and missing domains

Automation is classified first, even when an automation identity uses a
Huawei-domain address. Huawei and partner tiers are always reported
separately. Their sum is an observed corporate-domain share, not a complete
affiliation estimate. Private email or no observed corporate domain does
not establish non-affiliation.

### Core-path commits

Commits that are all of the following:

1. not merge commits;
2. not automation-authored under the rule above; and
3. touch at least one declared core implementation root.

This provides a more direct supporting signal than raw LOC. It is not used
to compare developer productivity across repositories or platforms.

## Reproducibility rules

- Missing repositories, a failed git command, an unexpected origin, a
  shallow clone, or an unresolved ref stops either pipeline; partial output
  is not treated as a successful snapshot.
- The analysis cutoff and resolved ref SHA are written to each current result;
  run metadata records retrieval time and the determinism check.
- Output ordering is deterministic for identical repositories, refs, and
  cutoff dates.
- GitHub and GitCode results stay in separate evidence blocks because their
  merge, bot, branch, and squash practices differ.
- Open-ended live counts are not silently substituted for a dated snapshot.
- `--replay-summary` reads the three resolved SHAs from the selected dated
  GitCode summary, so either pinned observation can be replayed without
  silently substituting today's `master`.
- The checked-in test suite discovers the frozen and dated commit snapshots
  and recomputes their aggregate statistics from their rows, so a manual data
  edit fails CI.

Because the filter uses author-local date, a live rerun from a later moving
branch can include an older-author-dated commit that became reachable only
after the earlier observation; history rewriting can also remove a previously
reachable row. Exact replay therefore uses checked-in SHAs. Live mode is a
full new observation, not an append or a reproduction of the frozen result.
The 2026-08-19 reconciliation demonstrates this directly: current
`triton-ascend` history adds 1,082 hashes dated no later than July 10 and drops
one formerly observed hash. Its fixed Heim-window total consequently changes
from 1,528 to 2,011 while the narrow confirmed-domain anchor moves only from
301 to 302.

The frozen root GitHub snapshot predates ref-SHA recording and therefore has a
known provenance limitation: it fixes the date and preserves per-commit rows,
but not the source ref SHA. The 2026-08-19 snapshot records every origin and
resolved `HEAD`; a second run against those pinned SHAs produced nine
byte-identical files. The two snapshots are retained side by side rather than
rewriting the older evidence.

The GitHub-side `--grep` candidate patterns use `\b` word boundaries,
which the GNU and BSD regex engines used by common git builds support;
on a git build without `\b` support the candidate counts would differ.

## Claim ladder

### Directly supported

- The selected repositories contain the reported number of publicly
  visible commits under the declared ref and cutoff.
- A reported share of those commits uses observed Huawei or partner email
  domains.
- A reported subset touches declared operator/library implementation
  roots.
- The 2026-08-19 selected GitHub rules yield 11,265 rows and the three
  selected GitCode histories yield 8,283 commits under their respective
  definitions. These are separate statements, not a combined or comparative
  platform total.
- The classified Kimi K3 case PRs appeared at the recorded times and had
  the recorded states at the snapshot cutoffs, including a support PR
  merged four days after the weights release.

### Reasonable descriptive inference

- The selected CANN repositories show sustained, organized public
  engineering activity in lower-level Ascend software outside Heim's
  GitHub frame.
- The Kimi K3 window shows a rapid public response whose same-day,
  minutes-apart timing is consistent with adaptation prepared before the
  public weights release.

### Not supported

- More commits or PRs mean better code, faster hardware, higher model
  quality, successful execution, or production readiness.
- The selected GitCode repositories represent all Huawei engineering
  activity or establish that GitCode is the overall "main theater."
- The GitHub and GitCode totals can be added, divided, or compared as if they
  were the same sampling frame or contribution unit.
- Corporate-domain metadata is a complete employee census.
- Kimi K3 establishes a general pattern across Chinese model releases.
- The identity of whoever prepared or coordinated the launch-window work.
- Export controls or another policy caused the observed timing or volume.

## Out of scope

This repository intentionally measures only the three evidence blocks
above. It does not attempt multi-model lifecycle analysis, CUDA/ROCm
control groups, hardware benchmarks, aggregate lines-of-code claims,
cross-platform totals, or performance adjudication; none of those are
needed to support its narrow descriptive claims.
