# 昇騰開源工程活動：Heim 復刻、GitCode 延伸與 Kimi K3 個案

**日期化截面：** 2026-07-10 commit 凍結快照完整保留；另有鎖定來源
SHA、截至 2026-08-19 部分日的 commit 觀察。Kimi K3 狀態快照日期為
2026-08-05、2026-08-08 與 2026-08-19。

## 技術摘要

本 repository 以三層可重現框架量測昇騰／CANN 周邊**公開可見的軟體
工程活動**：先以 Heim 的固定窗口統計作數量級校準，再量化 GitCode 上
三個 CANN 算子庫的 default-branch 活動，最後以 Kimi K3 發布窗口內
人工分類的 Ascend 支援 PR 集合作為具體個案。

它**不**量測硬體效能、生產就緒度、代碼品質、華為總工程投入、GitCode
相對 GitHub 的重要性，或出口管制與模型發布的因果效應。

2026-08-19 GitHub 觀察在八套已聲明規則下共有 11,265 筆列；GitCode
觀察則是三個選定 default-branch 歷史的 8,283 筆 commits。兩者的
repository 選樣與貢獻流程不同，刻意不加總、不相除，也不用來排列平台
規模。

兩個 commit 區塊都以 commit author timestamp 在其**自身時區**呈現的
日曆日期套用截止條件，不轉成 UTC，也不是 committer date 或抓取日期。
後一 moving ref 可能新曝露較早 author date 的 commit，也可能移除舊列；
因此 8 月觀察是全量重算，不是接續 7 月的 append。

## 一、Heim 的數量級可由公開 git 歷史獨立校準

Lennart Heim 於 2026-03-31 發布的分析指出，前十二個月華為系貢獻者為
vLLM、Triton、SGLang、llama.cpp、PyTorch 等專案加入約 3,000 個
commits、1.08M 行代碼，並估計 80–95% 來自華為員工（分 repo 數字的
一手來源為 [X 討論串](https://x.com/ohlennart/status/2039001304169623576)，
本專案作者於 2026-07-10 親讀並留存；另有
[LinkedIn 同步貼文](https://www.linkedin.com/posts/lennartheim_huawei-added-support-for-its-ascend-ai-chips-activity-7444771757829484544-Z4mn)）。

本專案以 2025-04-01 至 2026-03-31 為固定窗口，從本地完整 git 歷史
重新計數：

| Repo／口徑 | Heim | 2026-07-10／2026-08-19 觀察 | 解讀 |
|---|---:|---:|---|
| `vllm-ascend` 全部 commits | 約 2,420 | 2,685／2,685 | 高約 11%，屬同一數量級；簡單口徑連自動化一併計入（窗口內含 32 筆 dependabot） |
| `triton-ascend` 華為企業網域作者 commits | 約 300 | 301／302 | 即使完整歷史大幅漂移，保守網域口徑仍接近 Heim 的數字 |
| SGLang Ascend/CANN/NPU 訊息或路徑命中 | 210+ | 361／361 | candidate 計數，同一數量級；不等於 361 個人工確認適配事件 |
| llama.cpp CANN/Ascend 訊息或路徑命中 | 93 | 127／127 | 同一數量級，仍受 keyword 規則影響 |
| PyTorch Ascend/NPU commit-message 命中 | 約 25 | 8／8 | 從嚴的純訊息口徑下未能復刻；如實報告為分歧，非對 Heim 的更正 |

這是校準，不是宣稱 Heim 分析的每個環節都被精確復刻。`vllm-ascend`
的差距可能來自 ref 快照、merge 處理或收錄規則差異。`triton-ascend`
方面，本專案挖掘的 `triton-lang/triton-ascend` default branch 含上游
Triton 譜系。兩次日期化觀察之間，現行 ref 新增 1,082 個 author date
不晚於 7 月 10 日的可達 hashes，並移除一個舊 hash；完整固定窗口總數
因而由 1,528 變為 2,011，但華為企業網域子集只由 301 變為 302。舊快照
沒有記錄來源 SHA，不能把這些回補列定時為 7 月 10 日之後完成的工程。
`Ascend` 組織下另有同名 repository，兩者計數也不可混同。

Heim 的 1.08M 行與 80–95% 歸屬區間保留為其自報基準；本專案不獨立
驗證（LOC 高度依賴路徑與生成檔規則，歸屬無法僅靠 email 網域重建）。

### GitHub email metadata 能歸屬什麼、不能歸屬什麼

2026-08-19 GitHub 觀察的全部 11,265 筆列（author-local date 自
2025-04-01 至截止日）之作者信箱網域組成：

| 網域 | 筆數 | 占比 |
|---|---:|---:|
| `users.noreply.github.com` | 2,656 | 23.6% |
| `huawei.com` | 2,242 | 19.9% |
| `gmail.com` | 1,736 | 15.4% |
| `163.com` | 1,518 | 13.5% |
| `qq.com` | 1,395 | 12.4% |
| `openai.com` | 517 | 4.6% |
| `h-partners.com` | 285 | 2.5% |
| `outlook.com` | 211 | 1.9% |

近四分之一的 GitHub 端 commits 以 no-reply 隱藏信箱，其餘以個人信箱
為大宗；Heim 窗口內 `vllm-ascend` 的 no-reply 占比達 36.4%。因此
GitHub 端的企業網域占比是**下限**——這是本專案保守網域口徑（例如
`vllm-ascend` 窗口內華為＋合作商網域僅 9.5%）遠低於 Heim 80–95%
估計的主因：Heim 使用了 email 網域以外的歸屬訊號。同一量測在 GitCode
算子庫得到高企業網域占比（下節），主要因為該處貢獻者以工作信箱
提交。兩平台的占比不可互相比較，兩者也都不是員工普查。
凍結快照的 8,902 筆網域表仍可由根目錄資料重算，並未被覆寫。

## 二、三個 GitCode 算子庫補上 Heim 未觀察的底層工作流

Heim 的範圍在 GitHub。本專案另選 [GitCode 公開 CANN 組織](https://gitcode.com/cann)
的三個 repository。三庫是目的性樣本：其專案宗旨直接就是 Transformer
算子、數學算子與矩陣乘 kernel 模板。它們不是普查——2026-08-08 查閱
時，該組織列出 75 個公開 repository，其中至少還有十一個本專案未量測
的 `ops-*` 算子庫；因此三庫合計低估組織活動量，不支持任何組織層級
主張。

凍結觀察取 2026-08-07 解析並固定的 `master` SHA，再以 author-local date
篩選至 2026-07-10。第二次 live 觀察解析新 `master` SHA，採 2026-08-19
（含）author-local 截止日。抓取在 8 月 19 日當天完成，所以該日與 8 月
月度桶都只是部分觀察；兩者也都不是對截止日收盤 branch 內容的還原。

| Repo | 08-19 author-date range | Commits 07-10→08-19 | 作者身分* 07-10→08-19 | 華為 tier 07-10→08-19 | 合作商 tier 07-10→08-19 | 自動化 tier 07-10→08-19 | 核心路徑／eligible** 07-10→08-19 |
|---|---|---:|---:|---:|---:|---:|---:|
| `cann/ops-transformer` | 2025-09-28–2026-08-19 | 4,377→5,264 | 505→558 | 3,282→3,965 | 746→860 | 306→357 | 3,698／4,071（90.8%）→4,482／4,907（91.3%） |
| `cann/ops-math` | 2025-09-25–2026-08-19 | 2,040→2,501 | 323→360 | 1,208→1,541 | 417→455 | 275→318 | 1,433／1,758（81.5%）→1,819／2,176（83.6%） |
| `cann/catlass` | 2025-01-22–2026-08-19 | 472→518 | 80→85 | 285→311 | 81→83 | 37→38 | 220／434（50.7%）→246／479（51.4%） |

\*「作者身分」是 author name 與 email 的去識別組合，不是工程師人數、
FTE 或彼此去重後的跨 repository 人數。

\** eligible 指非 merge、非自動化的 commits；核心路徑依
[METHOD_ZH.md](METHOD_ZH.md) 事先列出的實作目錄判定。每筆公開列另存
該 commit 的頂層路徑清單，讀者可直接從版本庫內資料稽核判定，無須
重新 clone。

三庫在凍結觀察合計 6,889 筆 default-branch commits，2026-08-19 觀察
為 8,283 筆。這些數字的用途是證明 Heim 的 GitHub sampling frame 外，
存在一個規模可觀察、企業網域參與度高的 CANN 算子工程工作流。它
**不能**被寫成「GitCode 是主戰場」或「華為總投入是 Heim 的 N 倍」：
不同平台的 merge、bot、squash 與分支流程不同，三個目的性 repo 也不是
任一平台的隨機樣本。

2026-08-19 觀察的 7,562 筆 eligible commits 中，6,547 筆（86.6%）
觸及預先聲明的核心實作目錄；凍結觀察則為 5,351／6,263（85.4%）。
兩次觀察在 2026-06 以前的彙總月度數量相同；後一 ref 下，7 月是完整
1,058 筆，8 月則為截至部分 8 月 19 日的 790 筆。這是對「底層軟體
活動」較直接的輔助指標；路徑占比不衡量改動難度、正確性、原創性或
效能。

## 三、Kimi K3 發布窗口：人工分類的個案集合

[Kimi 官方產品歷程](https://www.kimi.com/help/agent/agent-overview)
（2026-08-08 查閱）記錄 Kimi K3 完整權重於 **2026-07-27** 開放。自
凍結候選窗口（2026-07-26 至 2026-08-01 建立的 PR）人工分類出 17 筆
Ascend／NPU 目標的 Kimi K3 PR：15 筆在 Ascend 專用的
`vllm-project/vllm-ascend`，2 筆為 `sgl-project/sglang` 的 `[NPU]`
標記 PR。

最新的 [2026-08-19 快照](k3-adaptation/snapshots/2026-08-19.json)抓取於
2026-08-19T15:36:25Z，保留同一組固定 17 PR cohort；該截止日為 6 筆
merged、7 筆 closed unmerged、4 筆 open。629 筆 raw search hits 是會
漂移的 discovery 上限，不是 629 個適配事件，也沒有擴大人工分類個案集。

關鍵觀察（全部凍結於
[`k3-adaptation/snapshots/`](k3-adaptation/snapshots/) 的日期化快照）：

- **當日叢集**：權重釋出當日 15:17–15:38 UTC，`vllm-ascend` 出現四筆
  Kimi K3 PR——兩筆支援提案、一筆部署指南（#12952，送件五分鐘後
  合併，內容含 ModelScope W4A8 權重、Atlas 800 A3 映像與多節點部署
  配置）、一筆十九分鐘內合併的文件修正。SGLang 同日出現 #32544
  （`[NPU][Kimi] Support Kimi-K3 on NPU`）。
- **四天內合併**：核心提案 #12950（`Support Kimi K3 on Ascend`）於
  2026-07-31 合併。
- **910C 明示例證**：次一 UTC 日的 #32604（`[NPU] Day0 Support
  Kimi-K3 on 910C`）內文指明 Ascend 910C、CANN、PyPTO tile DSL 與
  3× Atlas 800I A3＝48× 910C 測試叢集（內文已封存於快照）；截至
  2026-08-19，它與另一筆 SGLang 個案都仍開啟，且 #32604 的公開
  metadata 仍未見送件日後的更新。
- **cohort 不變、狀態續變**：相較 8 月 8 日，`vllm-ascend` #13277 由
  open 轉為 merged；#13065、#13315、#13323 由 open 轉為 closed
  unmerged。仍 open 的 #13225 與 #13286 在 8 月 19 日有更新。兩個
  repositories 的固定個案合計因此為 6 merged、7 closed unmerged、4 open。

同日、相隔數分鐘且附完整部署配置的時間分布，與「權重公開前已預先
準備適配」的解釋一致。公開 metadata 無法顯示誰準備或協調該工作；
合併只代表維護者接受代碼，不是正確性或效能驗證；單一發布窗口也
不構成一般模式。

`k3-adaptation/` 的全文搜尋命中（2026-08-05 合計 290、2026-08-08 為
373、2026-08-19 為 629）只是會漂移的 discovery 上限；它不會自動
擴大固定 17 PR cohort。197 筆窗口候選主要用於彙總網域稽核。這些搜尋
數都不作 headline，只用來保留候選集合與查核軌跡。

## 四、指標與主張邊界

本專案只使用三個核心證據單位：

1. 固定窗口、固定 repository／ref 的 commit 計數，用於 Heim 數量級
   校準。
2. 三個指定 GitCode 算子庫的 default-branch 活動、網域分層與核心路徑
   commits，用於觀察 Heim 範圍外的底層工作流。
3. 一組人工分類、附日期化狀態快照的 Kimi K3 發布窗口 PR，用於描述
   回應時間與窗口內結局。

刻意不納入 headline 的項目包括：無法由 checked-in pipeline 重建的
彙總 LOC、GitCode 組織頁即時顯示的總 PR／下載數、硬體 benchmark、
跨模型存活分析、政策因果與跨平台效率比較。

完整定義與排除規則見 [METHOD_ZH.md](METHOD_ZH.md)。

## 五、重現

### GitHub／Heim 校準

```bash
python3 mine_commits.py <repos_dir> data/github-2026-08-19 \
  --as-of 2026-08-19
```

根目錄 `summary.json` 與 `raw_*.jsonl` 仍是 2026-07-10 凍結快照；它
產生於來源 SHA 記錄功能之前，因此無法只靠 metadata 還原當時 ref。
2026-08-19 summary 則記錄八個來源 SHA，對這些 refs 全量再跑一次得到
九個逐 byte 相同的檔案。兩份輸出的 hash-level 差異見
[`data/UPDATE-2026-08-19.md`](data/UPDATE-2026-08-19.md)。公開列不含
作者姓名或完整 email，所有彙總可自列重算。

### GitCode 延伸

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

管線會驗證 origin、拒絕 shallow clone、fail fast，並以已記錄 SHA
精確重播。省略 `--replay-summary` 才會以當前 `master` 建立新觀察；
本次 live 輸出與固定 SHA replay 三檔逐 byte 相同。舊觀察仍保留於
`data/gitcode-2026-07-10/`，可用其 summary 與原截止日重播。
輸出不含作者姓名或完整 email 欄位，但保留公開 commit metadata、每筆
commit 的頂層路徑清單與可連結的雜湊身分以供查核；這是資料最小化，
不是匿名化。

### Kimi K3 個案

詳見 [k3-adaptation/README.md](k3-adaptation/README.md) 與
[k3-adaptation/METHOD.md](k3-adaptation/METHOD.md)。相關查詢需要已
登入、唯讀使用的 `gh` CLI；最新狀態見
[`k3-adaptation/snapshots/2026-08-19.json`](k3-adaptation/snapshots/2026-08-19.json)。
