# Changelog

格式依循 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)。

## [Unreleased]

### Added
- **2026-08-13 第 6 期資料快照**：職缺 145 筆（Greenhouse 88＋Yourator 57）、新聞 66 篇，
  失敗來源 0 個。機械層報告 `reports/report-2026-08-13.md`，`latest.md` 同步。
- **第 6 期分析** `reports/analysis-2026-08-13.md`
- **`reports/artifact-2026-08-13.html` 進 git**——先前各期的 artifact 只存在雲端，
  repo 裡沒有副本，等於**無法重現任何一期的頁面**。本期起改為與下游
  `martech-job-radar` 一致，把產出的 HTML 一併收進版控

### Changed
- **修正一個講了四期的框架**：「研發重心從資料移到 AI」不成立。
  同一期 Appier 台北新開 `Senior Digital Advertising Data Analyst`（08/10 刊登，
  六期以來第一個新開分析職），而初階 AI 研究職連兩期缺席。
  真正一致的分界是**年資**（資深在開、初階在收），不是職能

### Notes
- **上期的觀察項有一條被推翻**：「實習類整體在收」不成立，本期 Appier 實習 6 → 8。
  但回升的兩筆是 `Account Operations Intern`（營運端，且刊登日為 2021／2025 的舊缺重新上架），
  AI 研究類實習仍然一個都沒有。修正為「收的是 AI 研究類實習，不是實習整體」
- **主題聲量的跨期禁令證據更強**：本期重疊 **5／66**，且間隔從 5 天縮到 3 天
  重疊率並未變高——重疊取決於 feed 長度而非時間間隔。`topicDelta` 本期一律不判讀
- **新增一條職缺判讀規則**（累積至兩條）：異動要依序濾掉 ① 非追蹤公司
  ② 刊登日遠早於本期者（重新上架非新編制，本期 2 筆）。
  原擬的第三條「換城市／換頁造成的一增一減」**當日撤回**——查明那是下游
  `martech-job-radar` 整併鍵的 bug（無職缺編號時退回比職稱），不是真實現象。
  本專案以 `jobId` 為鍵，不受影響
- 本次刷新是由下游 `martech-job-radar` 的第 3 期報告觸發的：
  下游讀的是本專案的**工作區**，先前工作區停在 `docs/version-stamp-third`，
  最新快照是 08-10。先刷新本專案再跑下游，下游才不會觸發新鮮度警告

## [1.2.1] - 2026-08-10

### Added
- `docs/ARCHITECTURE.md`：四層管線圖、模組職責、識別鍵與跨期比較是否成立、對下游的六欄契約
- README 新增判讀限制：**主題聲量不可跨期比較**（見下方 Notes）

### Fixed
- **RSS 抓取無逾時上限**：`feedparser.parse()` 不吃 timeout 參數，來源掛住連線會讓程序永不結束；
  排程情境下 launchd 不會在前次仍在跑時啟動新的一次，等於**靜默停擺且無任何錯誤訊息**。
  於 `run.py` 入口設 `socket.setdefaulttimeout(30)`（requests 自帶的 20/30 秒更短，優先生效）
- `scripts/refresh.log` 加入 `.gitignore`——排程一跑就產生，本專案 commit 流程用 `git add -A`，
  否則會被一起提交進版控

### Notes
- **查出主題聲量的測量方式不支援跨期比較**（2026-08-10 第 5 期分析）：
  `fetch/newsRss.py` 只讀 feed 當下的 `entries`，`maxAgeDays` 只能剔除舊文、無法找回已滑出
  feed 的文章，也沒有跨期累積儲存。實測相鄰兩期文章重疊數為 9、13、4、6（分母 31～66），
  能跨期存活的幾乎只有低頻源的舊文。因此 `stats.json` 的 `topicDelta` 是兩批幾乎不相交樣本
  之間的差，**不是趨勢**。
- 要修得把新聞改成累積式儲存（`data/news-store.json`，每期併入新抓到的、依 `maxAgeDays` 過期），
  這會讓歷史五期快照無法直接沿用，**屬於需要先立一筆 MT 決策的改動**，本版不動程式碼，
  只把限制寫進 README 與 `docs/ARCHITECTURE.md`
- 職缺面不受影響：差集以 `jobId` 為鍵，同 id 改標題不會製造假異動（本期實測 `gh-6820898`）

## [1.2.0] - 2026-07-20

### Added
- **分析層**：`/martech-report` 指令（`.claude/commands/martech-report.md`）——Claude 讀完資料
  親自撰寫「分析專區」（跨來源見解、對求職的意涵），非模板；產出 `reports/analysis-*.md`
- 首份分析專區 `reports/analysis-2026-07-20.md`
- **半自動排程**：`scripts/refresh.sh`（機械層刷新＋桌面通知）、`install-schedule.sh` /
  `uninstall-schedule.sh`（macOS launchd，每 3 天）
- 視覺化 artifact 新增分析專區（三大重點＋見解卡）
- **通知落點**：Notion 母 page「MarTech 趨勢報告」，每期一個子 page（含見解＋artifact 連結）

### Changed
- README 使用方式改為「機械層／分析層」兩層架構，新增定期更新（半自動）說明

### Notes
- 通知原訂用 Email，但 Gmail 連接器只能建草稿且授權範圍不足，改用 Notion（見 MT-003）

## [1.1.0] - 2026-07-20

### Changed
- **主軸修正**：報告改為「應用趨勢（新聞/文章）為主、職缺為次」的結構（MT-002）
- 應用主題分類 8 → 12 類（新增 對話式商務／零售媒體／行銷自動化／個人化推薦 等）
- 趨勢比較新增「主題聲量升降」，為報告最重要的趨勢訊號

### Added
- 新聞源 5 → 9：ChiefMartec、MarTech Series、Appier Blog、Insider Blog
- feed 選項 `keepAll`（純 MarTech 源不經關鍵詞過濾）、`company`（公司部落格自動掛標記）、
  `maxAgeDays`（低頻高價值源放寬時間窗）
- 報告新增「各主題代表文章」節（1a），趨勢判斷不只看數字

## [1.0.0] - 2026-07-19

### Added
- 抓取層：Greenhouse 官方 Job Board API（Appier，含職缺內文）、Yourator 搜尋 API（台灣新創，僱主過濾）、5 個新聞 RSS 源
- 統計層：公司職缺數、職稱分類、技能關鍵詞頻率、薪資樣本中位數、台灣可投遞清單、跨快照趨勢比較
- 報告層：繁中 markdown 週報（每節附判讀指引），`reports/latest.md` 同步更新
- `--no-jobs` / `--no-news` / `--reanalyze` 執行選項

### Removed
- 104 抓取模組——端點有 Cloudflare bot 防護，不做規避，改以 Greenhouse＋Yourator 為職缺來源
