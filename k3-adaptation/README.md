# Kimi K3 launch-window case

This directory answers one bounded question: **after the Kimi K3 weights
release, how quickly did Ascend/NPU-targeted support activity appear in
public inference-framework repositories, and what happened to that activity
inside the observation window?**

[Kimi's official product history](https://www.kimi.com/help/agent/agent-overview)
(accessed 2026-08-08) records the full K3 weights becoming available on
**2026-07-27**. The adaptation clock in this case uses the weights date:
open-source frameworks cannot execute a model before its weights exist,
even though the hosted Kimi K3 service launched earlier in July.

From a frozen candidate window (PRs created 2026-07-26 through 2026-08-01,
197 full-text candidates), 17 pull requests were manually classified as
Ascend/NPU-targeted Kimi K3 work: 15 in `vllm-project/vllm-ascend` (a
dedicated Ascend adaptation repository) and 2 NPU-tagged PRs in
`sgl-project/sglang`. Status snapshots were taken on 2026-08-05,
2026-08-08, and 2026-08-19.

Observed facts, all reproducible from the checked-in snapshots:

- **On the release day itself** (2026-07-27 UTC), `vllm-ascend` received a
  cluster of four Kimi K3 PRs between 15:17 and 15:38 UTC — executable
  support proposals ([#12950](https://github.com/vllm-project/vllm-ascend/pull/12950),
  [#12951](https://github.com/vllm-project/vllm-ascend/pull/12951)), a
  deployment guide ([#12952](https://github.com/vllm-project/vllm-ascend/pull/12952),
  merged five minutes after filing), and a follow-up documentation fix
  ([#12953](https://github.com/vllm-project/vllm-ascend/pull/12953), merged
  within nineteen minutes). SGLang received
  [#32544](https://github.com/sgl-project/sglang/pull/32544)
  (`[NPU][Kimi] Support Kimi-K3 on NPU`) the same day at 15:29 UTC.
- **On the next UTC day**, SGLang received
  [#32604](https://github.com/sgl-project/sglang/pull/32604)
  (`[NPU] Day0 Support Kimi-K3 on 910C`), whose description names Ascend
  910C, the CANN stack, the PyPTO tile DSL, and a 3× Atlas 800I A3 = 48×
  910C test cluster. The description is archived in
  [`snapshots/pr-bodies-2026-08-08.json`](snapshots/pr-bodies-2026-08-08.json).
- **The core support proposal was merged within four days.** #12950 was
  merged on 2026-07-31. As of 2026-08-19, the full 17-PR cohort contained
  6 merged, 7 closed-unmerged, and 4 open PRs. Two open `vllm-ascend` PRs
  were updated on the snapshot day itself.
- **Both SGLang NPU PRs remained open.** #32604 showed no public metadata
  update after its filing day, as of 2026-08-19.

The narrow statements this evidence can support:

> Ascend-targeted Kimi K3 support activity appeared in public inference
> frameworks on the release day itself, including a deployment guide merged
> within minutes and a support proposal merged within four days. The
> same-day, minutes-apart timing is consistent with adaptation work prepared
> before the public weights release.

It does **not** establish that the merged code runs the model correctly or
at any performance level, that Huawei or Moonshot directed the work, or
that one launch generalizes to a broader pattern.

## Directory contents

- [`CASE_STUDY.md`](CASE_STUDY.md): timeline, observation fields, and the
  can-say / cannot-say boundary (中文, with English summary).
- [`METHOD.md`](METHOD.md): candidate discovery, classification rule,
  evidence tiers, and reproduction steps (中文, with English summary).
- `snapshots/2026-08-05.json`: frozen discovery counts and the #32604
  status at the first cutoff.
- `snapshots/2026-08-08.json`: discovery counts plus status for all 17
  classified case PRs at the second cutoff.
- `snapshots/2026-08-19.json`: the same fixed 17-PR cohort at the current
  point-in-time cutoff; it also records the UTC retrieval timestamp.
- `snapshots/pr-bodies-2026-08-08.json`: archived public descriptions of
  the four key PRs (email-like strings redacted).
- `snapshots/authors-2026-07-26_2026-08-01-run2026-08-05.json`:
  data-minimized author-domain audit of the candidate window (aggregate
  histogram; no per-PR author identities).
- `snapshot_k3_prs.sh`: reruns candidate discovery and case-PR status.
- `audit_k3_pr_authors.py`: reruns the window-bounded author-domain audit.

Raw full-text search counts are discovery upper bounds, not adaptation
counts; they also drift as the search index updates (290 total raw matches
on 2026-08-05, 373 on 2026-08-08, and 629 on 2026-08-19 for the same
query), which is why every number here carries a snapshot date. These
counts never expand or reinterpret the fixed cohort.

---

# Kimi K3 發布窗口個案（中文）

本目錄回答一個有限問題：**Kimi K3 權重釋出後，公開推論框架中針對
Ascend／NPU 的支援活動多快出現？在觀察窗口內，這些活動的結局是什麼？**

[Kimi 官方產品歷程](https://www.kimi.com/help/agent/agent-overview)
（2026-08-08 查閱）記錄完整權重於 **2026-07-27** 開放。本個案以權重日
作為適配時鐘起點：開源框架必須取得權重才能執行模型，即使 Kimi K3 的
託管服務更早在 7 月中旬上線。

自凍結候選窗口（2026-07-26 至 2026-08-01 建立的 PR，全文候選 197 筆）
人工分類出 17 筆 Ascend／NPU 目標的 Kimi K3 PR：15 筆在
`vllm-project/vllm-ascend`（Ascend 專用適配 repository），2 筆為
`sgl-project/sglang` 的 NPU 標記 PR。狀態快照日期為 2026-08-05、
2026-08-08 與 2026-08-19。

可自版本庫內快照重現的觀察事實：

- **權重釋出當日**（2026-07-27 UTC），`vllm-ascend` 於 15:17–15:38 UTC
  間出現四筆 Kimi K3 PR——可執行支援提案（#12950、#12951）、部署指南
  （#12952，送件五分鐘後合併）、文件修正（#12953，十九分鐘內合併）。
  SGLang 同日 15:29 UTC 出現 #32544（`[NPU][Kimi] Support Kimi-K3 on
  NPU`）。
- **次一 UTC 日**，SGLang 出現 #32604（`[NPU] Day0 Support Kimi-K3 on
  910C`），內文指明 Ascend 910C、CANN、PyPTO tile DSL 與 3× Atlas 800I
  A3＝48× 910C 測試叢集；內文已封存於
  `snapshots/pr-bodies-2026-08-08.json`。
- **核心支援提案四天內合併**：#12950 於 2026-07-31 合併。截至
  2026-08-19，完整 17 筆 cohort 為 6 筆已合併、7 筆未合併關閉、
  4 筆仍開啟；兩筆開啟中的 `vllm-ascend` PR 在快照當日更新。
- **SGLang 兩筆 NPU PR 均仍開啟**；#32604 截至 2026-08-19 的公開
  metadata 仍未顯示送件日後的更新。

本證據可支持的窄幅表述：

> Kimi K3 權重釋出當日，公開推論框架即出現 Ascend 目標的支援活動，
> 包括數分鐘內合併的部署指南與四天內合併的支援提案；同日、相隔數分鐘
> 的時間分布，與「在權重公開前即已準備適配工作」的解釋一致。

它**不能**證明已合併代碼能正確或以任何效能水準執行模型、華為或
Moonshot 主導該工作，或單一發布事件足以推出普遍模式。

全文搜尋數是 discovery 上限而非適配數量，且會隨索引變動（同一查詢
2026-08-05 合計 290 筆、2026-08-08 為 373 筆、2026-08-19 為 629 筆）。
該數字不會擴大或重新解釋固定 cohort，本目錄所有數字一律附快照日期。
