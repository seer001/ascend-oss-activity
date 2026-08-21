# Case study：Kimi K3 launch-window 個案集合

**English summary.** Seventeen manually classified Ascend/NPU-targeted
Kimi K3 pull requests from the frozen 2026-07-26..2026-08-01 window. On the
weights-release day itself (2026-07-27 UTC), `vllm-ascend` received four
Kimi K3 PRs within 21 minutes, two of which (a deployment guide and a
docs fix) were merged the same hour; the core support PR #12950 was merged
on 2026-07-31. SGLang's two `[NPU]` PRs (#32544 same day, #32604 next UTC
day, explicitly naming 910C/CANN/PyPTO) remained open through 2026-08-19.
As of 2026-08-19: 6 merged, 7 closed unmerged, 4 open. The evidence shows
fast, plausibly pre-coordinated public adaptation activity; it does not
show correctness, performance, or who directed the work.

## 案例定位

觀察對象是凍結窗口內人工分類的 17 筆 Ascend／NPU 目標 Kimi K3 PR
（選取規則見 [METHOD.md](METHOD.md)）。個案觀察「支援活動何時出現、
在窗口內的公開結局」，不驗證適配完成度或效能。

## 時間線（UTC）

| 時間 | 公開事件 | 可觀察意義 |
|---|---|---|
| 2026-07-27 | [Kimi 官方產品歷程](https://www.kimi.com/help/agent/agent-overview)（2026-08-08 查閱）記錄完整權重開放 | T0：開源適配時鐘起點 |
| 2026-07-27 15:17 | `vllm-ascend` [#12950](https://github.com/vllm-project/vllm-ascend/pull/12950)、[#12951](https://github.com/vllm-project/vllm-ascend/pull/12951) 建立 | T0 當日即出現可執行支援提案 |
| 2026-07-27 15:19 → 15:24 | [#12952](https://github.com/vllm-project/vllm-ascend/pull/12952) 部署指南建立，**五分鐘後合併** | 內容含 ModelScope W4A8 權重、Atlas 800 A3、DP4/TP16/EP64 與十六節點 PD 分離配置；與「預先準備」解釋一致 |
| 2026-07-27 15:29 | SGLang [#32544](https://github.com/sgl-project/sglang/pull/32544)（`[NPU][Kimi] Support Kimi-K3 on NPU`）建立 | 第二個框架同日出現 NPU 支援提案 |
| 2026-07-27 15:38 → 15:57 | [#12953](https://github.com/vllm-project/vllm-ascend/pull/12953) 建立並於十九分鐘內合併 | 部署文件持續修正 |
| 2026-07-28 03:21 | SGLang [#32604](https://github.com/sgl-project/sglang/pull/32604)（`[NPU] Day0 Support Kimi-K3 on 910C`）建立 | 內文指明 910C、CANN、PyPTO 與 3× Atlas 800I A3＝48× 910C 測試叢集 |
| 2026-07-29–08-01 | `vllm-ascend` 持續出現部署指南與功能 PR（#13036–#13323） | 窗口內活動不止於首日 |
| 2026-07-31 03:10 | **#12950 合併** | 核心支援提案於權重日後四天進入代碼庫 |
| 2026-08-05 | 第一次狀態快照 | #32604 仍 `OPEN`、`updatedAt` 停在送件當日 |
| 2026-08-08 | 第二次狀態快照（17 筆全量） | 5 合併、4 未合併關閉、8 開啟；#13225、#13277 於快照當日仍有更新 |
| 2026-08-19 | 第三次狀態快照（同一 17 筆 cohort） | 6 合併、7 未合併關閉、4 開啟；#13225、#13286 於快照當日更新 |

## 個案表（狀態截至 2026-08-19）

| PR | 標題要旨 | 類型 | 建立（UTC） | 狀態 |
|---|---|---|---|---|
| vllm-ascend #12950 | Support Kimi K3 on Ascend (v0.26.0rc) | 支援 | 07-27 15:17 | **MERGED**（07-31） |
| vllm-ascend #12951 | Support Kimi K3 (v0.23.0) | 支援 | 07-27 15:17 | CLOSED 未合併 |
| vllm-ascend #12952 | Kimi-K3 deployment guide | 部署文件 | 07-27 15:19 | **MERGED**（07-27 15:24） |
| vllm-ascend #12953 | Fix openEuler image tag | 部署文件 | 07-27 15:38 | **MERGED**（07-27 15:57） |
| vllm-ascend #13036 | A2 deploy guide | 部署文件 | 07-29 01:42 | CLOSED 未合併 |
| vllm-ascend #13037 | A2 deployment guide | 部署文件 | 07-29 01:56 | **MERGED**（07-29） |
| vllm-ascend #13041 | Update deployment configuration | 部署文件 | 07-29 03:01 | CLOSED 未合併 |
| vllm-ascend #13065 | Kimi DSpark GQA | 功能 | 07-29 07:56 | CLOSED 未合併（08-11） |
| vllm-ascend #13071 | test Kimi3 mla dspark | 測試 | 07-29 08:57 | CLOSED 未合併 |
| vllm-ascend #13143 | Update deployment configurations | 部署文件 | 07-30 03:53 | **MERGED**（07-30） |
| vllm-ascend #13225 | Kimi K3 MLA C8 support on A3 | 功能 | 07-31 01:39 | OPEN（08-19 更新） |
| vllm-ascend #13277 | MLA DSpark speculative decoding | 功能 | 07-31 09:29 | **MERGED**（08-12） |
| vllm-ascend #13286 | A5 C8 quantization | 功能 | 07-31 10:48 | OPEN（08-19 更新） |
| vllm-ascend #13315 | DSpark 三算子精度調查（WIP） | 調查 | 08-01 02:49 | CLOSED 未合併（08-12） |
| vllm-ascend #13323 | Fuse KDA RMSNorm and sigmoid gate | 效能 | 08-01 10:29 | CLOSED 未合併（08-13） |
| sglang #32544 | Support Kimi-K3 on NPU | 支援 | 07-27 15:29 | OPEN（最後更新 07-27 21:14） |
| sglang #32604 | Day0 Support Kimi-K3 on 910C | 支援 | 07-28 03:21 | OPEN（`updatedAt` 停在送件當日） |

類型欄為依標題與內文的人工判讀，僅供閱讀輔助；狀態欄一律以
[`snapshots/2026-08-19.json`](snapshots/2026-08-19.json) 為準。

## 可以說

- Kimi K3 權重釋出**當日**，兩個公開推論框架即出現 Ascend／NPU 目標的
  支援提案；`vllm-ascend` 的部署指南在送件五分鐘後合併。
- 核心支援提案 #12950 於權重日後四天（2026-07-31）合併。
- 截至 2026-08-19，17 筆個案中 6 筆已合併、4 筆仍開啟；其中
  兩筆功能 PR 在快照當日更新。
- 同日、相隔數分鐘且附完整部署配置的時間分布，與「權重公開前已預先
  準備適配」的解釋一致（見 METHOD 競爭解釋節）。
- #32604 的內文（已封存）明確指向 910C、CANN 與 PyPTO，提供 CANN
  軟體棧被用於新模型適配的具體公開例證。

## 不可以說

- Kimi K3 已在 910C／Ascend 上「完成」適配——合併只代表維護者接受
  變更，不是正確性或效能證明。
- 任何吞吐量、延遲、精度、穩定性或成本表現。
- 提交者代表華為或 Moonshot，或該工作由誰主導、協調。
- 單一模型的發布窗口足以證明生態的普遍反應速度。
- 全文搜尋命中（08-05 的 290 筆、08-08 的 373 筆、08-19 的
  629 筆）是適配 PR 數。

## 資料來源

- [`snapshots/2026-08-05.json`](snapshots/2026-08-05.json)：第一截止日
  的候選數與 #32604 狀態。
- [`snapshots/2026-08-08.json`](snapshots/2026-08-08.json)：第二截止日
  的候選數與 17 筆個案狀態。
- [`snapshots/2026-08-19.json`](snapshots/2026-08-19.json)：同一 17 筆個案
  的第三次狀態快照，含 UTC 實際抓取時間。
- [`snapshots/pr-bodies-2026-08-08.json`](snapshots/pr-bodies-2026-08-08.json)：
  #32544、#32604、#12950、#12952 的公開內文封存（email 樣式已遮蔽）。
- [`snapshots/authors-2026-07-26_2026-08-01-run2026-08-05.json`](snapshots/authors-2026-07-26_2026-08-01-run2026-08-05.json)：
  候選窗口的彙總作者網域稽核；不進入核心推論。
- 各 PR 的 GitHub 頁面為原始公開物件；本文一律以版本庫內的日期化
  快照為準，不以之後的頁面狀態回填舊結論。
