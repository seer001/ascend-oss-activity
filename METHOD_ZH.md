# 方法與主張邊界

English version: [METHOD.md](METHOD.md)

## 研究問題

公開 repository 的版本歷史，能否顯示持續的昇騰／CANN 相容性工程，
包括較底層的算子軟體？而一次近期模型發布，是否能提供這類回應模式
的具體案例？

這是一個**工程活動量測**問題，不是硬體效能測試、部署稽核、員工普查或
政策因果評估。

## 三段式設計

### A. Heim 校準

- 統計期間：2025-04-01 至 2026-03-31。
- 觀察版本：repository 根目錄保留 2026-07-10 凍結輸出，另以
  `data/github-2026-08-19/` 保存鎖定來源 SHA 的 2026-08-19 輸出。統計
  窗口固定，但不同時點 ref 所能到達的歷史可能不同。
- 對照基準：Lennart Heim 2026-03-31 發布的分析
  （[X 討論串](https://x.com/ohlennart/status/2039001304169623576)為
  分 repo 數字的一手來源，本專案作者於 2026-07-10 親讀並留存；另有
  [LinkedIn 同步貼文](https://www.linkedin.com/posts/lennartheim_huawei-added-support-for-its-ascend-ai-chips-activity-7444771757829484544-Z4mn)）。
- 資料來源：選定的 GitHub repository 歷史，用來近似 Heim 公開分析
  所涵蓋的 repository 集合。
- 主要輸出：依已聲明的「專用 repository」或「關鍵字／路徑候選」規則統計
  commit 數。
- 解讀：進行數量級校準。某個 repository 的數字接近，不表示每個
  repository 的定義都與 Heim 未公開的實作細節完全相同。

各定錨的解讀：

- 最可靠的點估計，是 `triton-ascend` 中作者 email 來自 `huawei.com` 或
  `hisilicon.com` 的子集：2026-07-10 凍結輸出為 301 筆，2026-08-19
  觀察為 302 筆，均與 Heim 的約 300 筆接近。完整固定窗口總數則因後一
  ref 曝露回補的上游歷史，由 1,528 變為 2,011。須注意 repository
  身分：本專案挖掘的 `triton-lang/triton-ascend` 完整歷史
  含上游 Triton 譜系，因此只有華為網域子集可比較；`Ascend` 組織下
  另有同名 repository，兩者的計數不可混同；完整歷史的增加也不可描述
  成 7 月 10 日之後完成的工程活動。
- `vllm-ascend` 的 2,685 筆比 Heim 的約 2,420 筆高約 11%，應表述為
  同一數量級，而非精確一致。專用 repository 規則計入全部 commits，
  含自動化（例如挖掘所得列中有 47 筆 dependabot），與 Heim 主數字的
  簡單口徑一致。
- 關鍵字／路徑候選計數（SGLang、llama.cpp、PyTorch、lmdeploy、
  transformers）對規則敏感：SGLang（本地 361 對 Heim 210+）與
  llama.cpp（127 對 93）屬同一數量級；PyTorch 在從嚴的純訊息規則下
  得 8 筆、Heim 約 25 筆，如實報告為「此窄規則下未能復刻」，而非對
  Heim 的更正。

Heim 的 1.08M 行與 80–95% 歸屬區間保留為其自報基準。本專案不獨立
驗證這兩個數字：LOC 高度依賴路徑與生成檔規則，歸屬也無法僅靠 email
網域可靠重建。

### B. GitCode 延伸

- Repository 範圍：`cann/ops-transformer`、`cann/ops-math`、
  `cann/catlass`。
- Ref：各 repository 的 `master` 預設分支；解析後的 commit SHA 會寫入
  輸出。
- 日期化觀察：原始截止條件是 author-local date 不晚於 2026-07-10；
  來源 ref 於 2026-08-07 解析並以 SHA 鎖定，因此不是對各分支在 7 月
  10 日當天內容的還原。第二次 live 觀察解析新的 `master` SHA，套用
  2026-08-19（含）author-local 截止日，另存於
  `data/gitcode-2026-08-19/`，並能由這些 SHA 逐 byte 重播。
- 部分期間：抓取在 8 月 19 日尚未結束時完成，所以 8 月 19 日當天與
  8 月月度桶都只是部分觀察，即使截止日採含括口徑。
- 主要輸出：截至截止日（含），可由預設分支到達的全部 commits。
- 輔助輸出：假名化作者身分、作者信箱網域分層、月度數量、每筆 commit
  的頂層路徑清單，以及非 merge、非自動化且觸及已聲明核心實作目錄的
  commits。

選樣說明：三個 repository 是目的性樣本，入選理由是其專案宗旨直接就是
本研究關注層次的算子／kernel 實作——Transformer 算子
（`ops-transformer`）、數學算子（`ops-math`）、矩陣乘 kernel 模板
（`catlass`）。它們不是普查：2026-08-08 查閱時，CANN 公開組織列出
75 個 repository，其中至少還有十一個未被本專案量測的 `ops-*` 算子庫
（`ops-nn`、`ops-tensor`、`ops-cv`、`ops-gnn`、`ops-blas`、`ops-fft`、
`ops-sparse`、`ops-rand`、`ops-solver`、`ops-multimodal-fusion`、
`ops-collections`）。因此三庫合計低估組織活動量，且不支持任何
組織層級的主張。

已聲明的核心路徑：

| Repository | 核心實作路徑 |
|---|---|
| `ops-transformer` | `attention`, `common`, `experimental`, `ffn`, `gmm`, `mamba`, `mc2`, `mhc`, `moe`, `posembedding`, `torch_extension` |
| `ops-math` | `common`, `conversion`, `experimental`, `math`, `random` |
| `catlass` | `include`, `python`, `experimental` |

核心路徑指標是一個表徵實作工作的透明代理指標，不評分改動規模、難度、
正確性、原創性或效能。每筆輸出列另存該 commit 的頂層路徑清單
（`top_level_dirs`），讀者不必重新 clone 即可從版本庫內資料稽核
core-path 判定。

凍結觀察含 6,889 筆 commits，其中 6,263 筆 eligible commits 有 5,351
筆觸及核心路徑（85.4%）。2026-08-19 觀察含 8,283 筆 commits，其中
7,562 筆 eligible commits 有 6,547 筆觸及核心路徑（86.6%）。兩次觀察
在 2026-06 以前的月度數量不變；後一 ref 下，7 月成為 1,058 筆的完整
月度桶，8 月則是截至 8 月 19 日部分日的 790 筆。這些數字只描述三個
已聲明 repositories。

### C. Kimi K3 範圍限定案例

- 模型事件：Kimi K3 權重於 2026-07-27 發布（廠商產品歷程，2026-08-08
  查閱）。K3 託管服務較早於 7 月中旬上線；適配時鐘以權重日為準，
  因為開源執行以取得權重為前提。
- 個案集合：自凍結候選窗口（2026-07-26 至 2026-08-01 建立的 PR）
  人工分類出的 17 筆 Ascend／NPU 目標 Kimi K3 PR，規則見
  [k3-adaptation/METHOD.md](k3-adaptation/METHOD.md)。
- 狀態截止日：2026-08-05、2026-08-08 與 2026-08-19。最新快照抓取於
  2026-08-19T15:36:25Z，仍保留相同的 17 筆人工分類個案。
- 輸出：各 PR 的時間、repository、狀態、合併情形，以及關鍵 PR 的
  內文封存。

全文搜尋結果僅作為待查候選；未經人工檢視前，不會被計為適配事件。
2026-08-19 搜尋得到 629 筆 raw matches，這是會漂移的 discovery 上限，
不是擴大的 cohort。固定個案在該截止日為 6 筆 merged、7 筆 closed
unmerged、4 筆 open；見
[`k3-adaptation/snapshots/2026-08-19.json`](k3-adaptation/snapshots/2026-08-19.json)。

## 指標定義

### Commit 總數

從已聲明 ref 可到達、author date 不晚於截止日的唯一 commit SHA 數量。
這裡的 author date 是 commit author timestamp 在其自身時區所呈現的
日曆日期，不轉換為 UTC，也不是 committer date 或抓取日期。保留這個
簡單指標，是為了與 Heim 公開的主要數字維持可比性。

### 可觀察作者身分

將原始 Git author name、一個 NUL 分隔字元與小寫後的 author email 連接
計算 SHA-256，並以不重複的雜湊值作為可觀察作者身分。這些值被稱為
「身分」而不是「人」：姓名拼寫、大小寫、空白或 email 差異可能把同一人
分成多個身分，也可能出現共用或被改寫的 metadata。

兩個平台的公開列均不含 author name 或完整 email 欄位。每列保留公開
commit hash 與 subject、（GitHub 端）email 網域，以及確定性雜湊：
上述 `identity_hash`，GitHub 端另加 `name_hash`，使各歸屬層的作者數
可從公開列重算。這些是可連結的假名識別碼，屬於資料最小化而非匿名化：
讀者仍可查閱上游公開 Git 歷史找回原始 metadata。

### GitHub 端歸屬分層（`mine_commits.py`）

- `confirmed`：作者 email 網域為 `huawei.com` 或 `hisilicon.com`
  （含子網域）。
- `likely`：網域為已知長期合作商網域（`h-partners.com`、
  `huawei-partners.com`，含子網域），**或**同一作者姓名在挖掘集合的
  其他地方使用過 confirmed 網域信箱（跨 repository 身分合併）。
- `unknown`：其餘全部，含 no-reply 與個人信箱。

身分合併是一條已聲明的啟發式規則：凡在挖掘集合內任一處使用過華為
企業信箱的作者姓名，其在其他 repository 以別的信箱提交的 commits
視為 likely。常見姓名可能撞號，因此其影響量化揭露而非隱藏：它把
2026-07-10 凍結輸出的 8,902 筆挖掘列中 60 筆升級為 likely（Heim
窗口內 41 筆），且不影響只計 confirmed 網域的 `triton-ascend` 主定錨。
在 2026-08-19 全量重算中，一筆原已存在於舊 `vllm-ascend` 資料的列，
因後一批選定歷史提供同名作者的新 confirmed 網域證據，而由 `unknown`
變為 `likely`。因此 tier 標籤是「一次日期化聯合挖掘」的屬性，不是
永久附著在 commit 上的標籤。

`unknown` 是 email 能見度造成的下限假象，不是「非華為」的判定：
`users.noreply.github.com` 在凍結列占 23.4%，在 2026-08-19 列占 23.6%
（固定 Heim 窗口內的 `vllm-ascend` 為 36.4%）。網域組成表見
[ANALYSIS.md](ANALYSIS.md)。

### GitCode 端網域分層（`mine_gitcode_activity.py`）

- `huawei`：`huawei.com`、`hisilicon.com`（含子網域）
- `partner`：`h-partners.com`、`huawei-partners.com`（含子網域）
- `automation`：`cann.team` 信箱（組織 CI 身分），或 author name 含
  獨立 token `bot`／`robot`（只比對完整 token，因此僅僅包含字母
  “bot” 的人名不會被誤掃入）
- `other`：所有其餘網域與缺少網域的記錄

自動化優先分類，即使該身分使用華為網域信箱。Huawei 與 partner tier
始終分開報告；兩者之和是可觀察的企業網域占比，不是完整的組織隸屬
估計。使用私人 email 或未觀察到企業網域，不能據此判定作者不隸屬
華為或合作夥伴。

### 核心路徑 commits

同時符合以下條件的 commits：

1. 不是 merge commit；
2. 依上述規則判定，不是自動化作者；
3. 觸及至少一個已聲明的核心實作路徑。

相較於原始 LOC，這提供了更直接的輔助訊號。本指標不用來比較不同
repository 或平台的開發者生產力。

## 可重現規則

- 缺少 repository、git 指令失敗、origin 不符預期、shallow clone 或
  ref 無法解析，都會終止管線；部分輸出不會被視為成功快照。
- 現行結果會寫入分析截止日與解析後的 ref SHA；執行 metadata 另記錄
  抓取時間與確定性檢查。
- 在 repository、ref 與截止日相同時，輸出順序固定且可重現。
- GitHub 與 GitCode 結果保持為獨立證據區塊，因為兩平台的 merge、bot、
  branch 與 squash 做法不同。
- 不會在沒有聲明的情況下，用未設定固定終點的即時計數，取代具有明確
  截止日的快照。
- `--replay-summary` 會從所選日期化 GitCode summary 讀取三個已解析
  SHA，使任一鎖定觀察可精確重播，而不會暗中換成今日 `master`。
- 版本庫內測試會自動發現凍結與日期化 commit snapshots，並從公開列
  重算彙總統計；手動修改資料會使 CI 失敗。

由於篩選使用 author-local date，日後從仍會變動的 branch 即時重跑時，
可能納入一筆在較晚時點才變得可達、但 author date 較早的 commit；歷史
改寫也可能讓舊列消失。因此精確重播使用版本庫內記錄的 SHA；live mode
是一次全量新觀察，不是 append，也不是凍結結果的復刻。2026-08-19 對帳
直接呈現這項限制：現行 `triton-ascend` 歷史新增 1,082 個 author date
不晚於 7 月 10 日的 hashes，並移除一個舊 hash；固定 Heim 窗口總數因而
由 1,528 變為 2,011，但從嚴 confirmed-domain 定錨只由 301 變為 302。

根目錄的凍結 GitHub 快照產生於 ref SHA 記錄功能之前，因此存在已知的
來源可追溯性限制：它固定日期並保留每筆 commit 記錄，但沒有保留來源
ref SHA。2026-08-19 快照記錄每個 origin 與解析後的 `HEAD`；對這些固定
SHA 再跑一次得到九個逐 byte 相同的檔案。兩份快照並列保留，不回寫舊
證據。

GitHub 端 `--grep` 候選 pattern 使用 `\b` 字界，常見 git 建置的 GNU
與 BSD regex 引擎均支援；在不支援 `\b` 的 git 建置上，候選計數會
不同。

## 主張階梯

### 直接支持

- 在已聲明的 ref 與截止條件下，選定 repositories 包含報告的公開可見
  commit 數量。
- 可報告其中使用 Huawei 或 partner email 網域的 commit 占比。
- 報告所列的 commit 子集觸及已聲明的算子／函式庫實作路徑。
- 依各自定義，2026-08-19 的選定 GitHub 規則產生 11,265 筆列，三個
  選定 GitCode 歷史產生 8,283 筆 commits。這是兩個獨立陳述，不是
  合計或平台比較總數。
- 分類的 Kimi K3 個案 PR 在記錄的時點出現、在快照截止日呈現記錄的
  狀態，其中一筆支援 PR 於權重釋出後四天合併。

### 合理的描述性推論

- 在 Heim 的 GitHub 範圍之外，選定的 CANN repositories 顯示了持續、
  有組織且公開可見的昇騰底層軟體工程活動。
- Kimi K3 窗口顯示快速的公開回應；其同日、相隔數分鐘的時間分布，
  與「在權重公開前即已準備適配」的解釋一致。

### 不支持

- 較多 commits 或 PRs 代表較好的代碼、較快的硬體、較高的模型品質、
  成功執行或已具備生產環境條件。
- 選定的 GitCode repositories 代表華為全部工程活動，或足以確立
  GitCode 是整體的「主戰場」。
- 把 GitHub 與 GitCode 總數當成相同 sampling frame 或貢獻單位來加總、
  相除或比較。
- 企業網域 metadata 構成完整的員工普查。
- Kimi K3 足以建立中國廠商模型發布事件的一般模式。
- 發布窗口工作由誰準備或協調。
- 出口管制或其他政策造成觀察到的時點或數量。

## 範圍之外

本 repository 刻意只量測上述三個證據區塊，不進行多模型生命週期分析、
CUDA／ROCm 對照組、硬體 benchmark、總行數主張、跨平台加總或效能
判定；支持本 repository 的窄幅描述性主張並不需要它們。
