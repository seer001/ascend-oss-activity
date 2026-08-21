# 方法與證據邊界

**English summary.** This case study measures launch-window response
activity, not adaptation completeness or performance. Candidates come from
a raw full-text PR search (`Kimi-K3`) in three repositories over a frozen
creation window (2026-07-26..2026-08-01, 197 candidates). A candidate
qualifies as a case PR when its public title or description names both the
Kimi K3 model and an Ascend/NPU execution target; every Kimi K3 PR in the
Ascend-dedicated `vllm-project/vllm-ascend` repository qualifies by
construction, and in `sgl-project/sglang` the two `[NPU]`-tagged Kimi K3
PRs qualify. That yields 17 case PRs. Statuses were frozen on 2026-08-05,
2026-08-08, and 2026-08-19; PR descriptions for the four key exhibits are archived with
emails redacted. Full-text hit counts are discovery upper bounds only. The
author-domain audit ships as aggregates without per-PR author identities.

## 研究問題

本資料集不評估 Kimi K3 在華為硬體上的完成度或效能，也不嘗試計算
「適配 PR 總量」。它只回答一個 launch-window 問題：

> Kimi K3 權重釋出後，公開程式碼社群中針對 Ascend／NPU 的支援活動
> 多快出現？在觀察窗口內，這些活動的公開狀態如何演變？

分析單位是人工分類後的 17 筆個案 PR，而不是全文搜尋命中的 PR 母體。
搜尋與作者網域稽核都只是輔助層。

## 基準日

[Kimi 官方產品歷程](https://www.kimi.com/help/agent/agent-overview)
（2026-08-08 查閱）記錄 Kimi K3 完整權重於 **2026-07-27** 開放。個案
以權重日為 T0：開源框架的適配必須以取得權重為前提；Kimi K3 託管服務
較早（7 月中旬）上線一事，不影響開源適配的時鐘起點。

## 個案選取規則

候選集合：三個 repository（`vllm-project/vllm`、`sgl-project/sglang`、
`vllm-project/vllm-ascend`）中，建立時間落在 2026-07-26 至 2026-08-01
的 `Kimi-K3` 全文搜尋命中，共 197 筆（凍結於 2026-08-05 快照）。

納入條件（依公開標題與內文判讀）：

1. 明確指向 Kimi K3 模型；且
2. 明確指向 Ascend／NPU 執行目標。

依此規則：

- `vllm-project/vllm-ascend` 是 Ascend 專用適配 repository，其窗口內
  全部 15 筆 Kimi K3 PR 依定義納入；
- `sgl-project/sglang` 納入 2 筆 `[NPU]` 標記 PR（#32544、#32604）；
- `vllm-project/vllm` 的命中均未同時滿足兩條件（K3 的一般模型支援
  不指向特定硬體），不納入。

共 17 筆。個案分類與截止狀態見 [CASE_STUDY.md](CASE_STUDY.md)。

## 觀察欄位與快照

每筆個案 PR 保存 `title`、`state`、`createdAt`、`mergedAt`、
`updatedAt`、`closedAt`，凍結於：

- `snapshots/2026-08-05.json`：全文候選數與 #32604 狀態（第一截止日）。
- `snapshots/2026-08-08.json`：全文候選數與 17 筆個案 PR 的完整狀態
  （第二截止日）。
- `snapshots/2026-08-19.json`：同一 17 筆個案 PR 的第三次狀態
  快照，含 UTC 實際抓取時間。
- `snapshots/pr-bodies-2026-08-08.json`：#32544、#32604、#12950、#12952
  的公開內文（email 樣式字串已遮蔽），供技術主張（910C、CANN、PyPTO、
  Atlas 叢集、W4A8 等）查核。

時間一律以 UTC 解讀。「當日」指與權重日同一 UTC 日曆日；由於權重開放
的精確時刻未被封存，本資料不支持「N 小時內」的表述。

「inactive」操作化為：截至快照日，`updatedAt` 仍停在 PR 建立當日。
這只描述 GitHub 公開 metadata，不能排除未反映在該欄位的私下活動。

## 證據層級

1. **核心：人工分類的 launch-window 個案集合（17 筆）。** 支持
   「支援活動快速出現且部分已合併」。
2. **輔助：全文搜尋候選池。** 只用來界定候選集合；不衡量適配量。
   原始命中會隨 GitHub 索引變動（2026-08-05 合計 290、2026-08-08 為
   373、2026-08-19 為 629），故一律附執行日期，且不以新命中擴大
   或重新解釋固定 cohort。
3. **附錄：作者網域稽核。** 只在彙總層級檢查公開 git metadata 的網域
   訊號；不推定組織主導，也不否定未公開的隸屬關係。

這個分層避免把「出現提案」、「合併程式碼」、「成功運行」與「效能
驗證」混成同一件事：本資料只觀察前兩者。

## 競爭解釋

權重日當日 15:17–15:38 的四筆 PR（其中部署指南五分鐘內合併）以及
「Day0」的分支命名，與「權重公開前已取得早期存取並預先準備適配」的
解釋一致。公開 metadata 無法分辨這種準備是由模型方、硬體方或社群
發起；本個案據此只陳述時間分布，不推定協調者。

## 可重現流程

### 1. 候選發現與個案狀態

```bash
bash snapshot_k3_prs.sh
```

腳本對三個 repository 執行 `gh search prs "Kimi-K3" --limit 300`（輸出
含 `limit_reached` 旗標），再抓取 17 筆個案 PR 的狀態欄位，寫入日期化
JSON。搜尋為全文比對，命中僅為 candidate upper bound。

### 2. 人工分類

對候選逐筆判讀標題與內文，套用上述兩條納入條件。分類結果與依據
記錄於 [CASE_STUDY.md](CASE_STUDY.md) 的個案表。

### 3. 作者網域稽核（附錄）

```bash
python3 audit_k3_pr_authors.py --window 2026-07-26..2026-08-01
```

輸出為資料最小化的彙總：逐筆 PR 只保留公開工作 metadata（編號、
建立時間、標題），作者 login 與逐筆 email 網域不發布；網域只進入
單一彙總直方圖。2026-08-05 快照含 197 筆候選（vLLM 99、SGLang 81、
vLLM Ascend 17）、2 筆 Moonshot 網域旗標與 2 名 MoonshotAI 公開組織
成員數。commit email 可自行設定；公開組織成員資格為選擇性揭露；
沒有公司網域不能證明作者與該公司無關。此稽核不回答誰審查、協調、
測試或主導工作，不作為正文主結論。

## 整體限制

- 權重釋出日以 Kimi 官方產品歷程為一手來源，引用時註明查閱日期；
  該頁面未被本資料集封存。
- PR 標題與內文表示提交者提出的支援目標，不等於維護者接受該主張；
  已合併也只表示維護者接受該變更進入代碼庫。
- 所有狀態欄位只描述截止日狀態；後續可能改變。
- `updatedAt` 未變只支持「公開 metadata 未見後續更新」，不能證明沒有
  任何工程活動。
- 本資料未保存可重跑的模型輸出、測試紀錄或 benchmark，不能判斷運行
  成功、正確性或效能。
- 單一模型的發布窗口不能推出華為、各框架社群或整個生態的普遍反應
  速度。
