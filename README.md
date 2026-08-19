# martech-trend-agent - MarTech 應用趨勢自動追蹤與統計分析

自動抓取 MarTech 產業新聞／文章判斷**應用趨勢**（主軸），輔以 Appier 為首的公司職缺作為
落地驗證訊號（次要），統計分析後產出繁中趨勢報告。回答三個問題：
**產業風向往哪吹、哪些應用已從概念走到落地、公司在為哪些能力擴編**。

![Version](https://img.shields.io/badge/version-1.2.1-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 功能特色
- **應用趨勢（主軸）**：9 個 RSS 源（iThome／TechOrange／INSIDE／MarTech.org／MarketingDive
  ／ChiefMartec／MarTech Series／Appier Blog／Insider Blog），12 類應用主題聲量＋每主題代表文章；
  純 MarTech 源可設 `keepAll` 全收、公司部落格自動掛公司標記
- **職缺訊號（次要）**：Greenhouse 官方 API（Appier 全球含內文）＋ Yourator（台灣新創），
  職稱結構、技能關鍵詞頻率、台灣可投遞清單、薪資樣本
- **趨勢比較**：每次執行存日期快照，自動與上次比較（新增／消失職缺、技能升降、主題聲量升降）。
  ⚠️ 職缺面以 `jobId` 為鍵、跨期成立；**主題聲量面不成立**，見「資料來源限制」第一條
- **報告自帶判讀指引**：每個統計節附「怎麼讀這個數字」

## 快速開始
```bash
cd martech-trend-agent
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python run.py
# 預期：依序印出「▶ 抓取…」各來源筆數，最後
# ✅ 完成。職缺 N 筆、新聞 M 篇、失敗來源 0 個
#    報告：reports/report-YYYY-MM-DD.md（latest.md 同步更新）
```

## 使用方式
本工具分兩層：**機械層**（Python 抓取＋統計，可排程自動跑）與**分析層**（Claude 讀完
資料撰寫見解，需模型在場）。

### 機械層（純資料）

| 指令 | 用途 |
|------|------|
| `.venv/bin/python run.py` | 完整執行：抓取 → 統計 → 產出 stats.json 與機械報告 |
| `.venv/bin/python run.py --no-jobs` | 只更新新聞 |
| `.venv/bin/python run.py --no-news` | 只更新職缺 |
| `.venv/bin/python run.py --reanalyze 2026-07-19` | 不重抓，用既有快照重跑統計（改完 config 後用） |

### 分析層（見解＋通知，在 Claude Code 內）

在 Claude Code 打 **`/martech-report`** —— 一鍵跑完整流程：抓取 → Claude 撰寫分析專區
（跨來源見解、對求職的意涵）→ 更新視覺化 artifact → 在 Notion 母 page 下建當期子 page → commit。
見解由 Claude 親自寫，非模板。

### 定期更新（半自動，每 3 天）

macOS launchd 排程每 3 天自動跑機械層並桌面通知，你再打 `/martech-report` 產生分析：

```bash
bash scripts/install-schedule.sh     # 安裝（首次；建議 merge 後在主 checkout 執行）
launchctl start com.martech-trend-agent.refresh   # 立即測試一次
bash scripts/uninstall-schedule.sh   # 移除
```

通知落點：Notion 母 page「MarTech 趨勢報告」，每期一個子 page（含見解＋artifact 連結）。

> 為何不是全自動：見解需要模型在場，本機無法定時喚醒模型，故採「機械層自動抓＋你觸發分析」
> 的半自動。（Gmail 連接器授權範圍不支援寫入，故通知改用 Notion。）

**加公司／技能／新聞源**：只改 `config.yaml`，不用動程式碼。公司若使用 Greenhouse 徵才，
在該公司條目加 `greenhouse: <board_token>` 可取得最完整資料。

**判讀方式**：先讀 `reports/analysis-<日期>.md`（見解）→ 再看 `report-<日期>.md`（統計數字）。

## 專案結構
```
martech-trend-agent/
├── config.yaml          # 公司清單、關鍵詞、RSS 來源（唯一需要編輯的檔案）
├── run.py               # 主程式：抓取 → 分析 → 報告
├── fetch/               # 抓取層（jobsGreenhouse / jobsYourator / newsRss）
├── analyze/stats.py     # 統計層（分類、頻率、趨勢比較）
├── report/buildReport.py# 報告層（繁中 markdown，含判讀指引）
├── scripts/             # refresh.sh（排程刷新）＋ install/uninstall-schedule.sh
├── docs/ARCHITECTURE.md # 四層管線圖、模組職責、識別鍵、對下游的契約
├── data/raw/YYYY-MM-DD/ # 每次執行的原始快照（趨勢比較的基準）
└── reports/             # analysis-*.md（Claude 見解）、report-*.md（機械統計）、latest.md
```

模組職責與資料流見 `docs/ARCHITECTURE.md`。
分析層流程定義在 `../.claude/commands/martech-report.md`（`/martech-report` 指令）。

## 對外契約：`data/raw/<日期>/jobs.json`

⚠️ **這個檔案有下游在讀，欄位改動需通知下游。**

姊妹專案 [`martech-job-radar`](https://github.com/aliencat0528/martech-job-radar)
（求職情報彙整）**唯讀取用**本檔，藉此不必重寫 Greenhouse 與 Yourator 兩支已跑過多期、
坑都補好的 fetcher。它不 import 本專案的模組、也不改 `config.yaml`——
所以本專案內部怎麼重構都不會弄壞它，**只要下列欄位不變**（← 根 `prepare.md` D-018）：

| 欄位 | 意義 | 為什麼下游需要它 |
|------|------|-----------------|
| `company` | 公司名 | 跨管道去重鍵的一半 |
| `title` | 職稱 | 去重鍵的另一半 |
| `area` | 地點 | 篩台灣職缺 |
| `link` | 職缺網址 | 報告要能點回原始頁面 |
| `appearDate` | **首次刊登日**（Greenhouse `first_published`） | 分辨「掛了三年的常駐缺」與「上週新開的缺」——下游最倚重的一欄 |
| `source` | 來源管道 | 報告標示職缺從哪個平台取得 |

**要改這些欄位時**：先在 `martech-job-radar` 開一個 issue 或直接改它的
`companies.yaml` 內 `trendAgentContractFields`，兩邊一起改再合併。
新增欄位不受此限（下游只讀它認得的欄位，多的會忽略）。

## 測試
```bash
.venv/bin/python run.py --reanalyze <既有快照日期>   # 不打網路，驗證分析與報告層
```

## 版本歷史
### v1.2.1 (2026-08-10)

- **查出主題聲量不能跨期比較** — 新聞是每期重抓 feed 當下內容，相鄰兩期文章重疊只有 4～6 篇；
  限制寫進 README 與新增的 `docs/ARCHITECTURE.md`，程式未動（修法需先立決策）
- RSS 抓取補上逾時上限（`socket.setdefaulttimeout(30)`），避免排程情境靜默停擺

### v1.2.0 (2026-07-20)

- **分析層＋半自動排程** — `/martech-report` 由 Claude 撰寫見解、`scripts/` launchd 每 3 天刷新

### v1.1.0 (2026-07-20)

- **主軸修正** — 應用趨勢為主、職缺為次；新聞源 5→9、主題 8→12 類

### v1.0.0 (2026-07-19)

- **首版 pipeline** — Greenhouse＋Yourator＋RSS 三源抓取、統計分析、繁中報告與趨勢快照

## 授權
MIT License

---

## 資料來源限制（判讀前必讀）

- **主題聲量不可跨期比較（最重要的一條）**：新聞抓取只讀 RSS feed **當下**的內容，
  多數源一次只回 10 篇，且沒有跨期累積儲存——`maxAgeDays` 只能剔除舊文、無法找回已滑出 feed 的。
  實測相鄰兩期文章重疊數為 9、13、4、6、5、14（分母 31～66），能跨期存活的幾乎只有低頻源的舊文。
  因此報告第 1 節與第 4 節的 `topicDelta` 是**兩批幾乎不相交樣本之間的差，不是趨勢**。
  在抓取方式改成累積式之前，那張表只能當期閱讀。修法與影響見 `docs/ARCHITECTURE.md`
  - **2026-08-19 補**：重疊數看似上升到 14／60，但**拆開後全部來自慢速源**
    （Insider Blog 10、Appier Blog 3、ChiefMartec 1）；iThome／TechOrange／INSIDE／
    MarTech.org／MarTech Series／MarketingDive 六個快速源，**六期以來重疊一直是 0**。
    重疊率取決於慢速源這期剛好在不在窗內，與時間間隔無關
  - **「連兩期同向才算趨勢」不適用於新聞面**（2026-08-19 新增）：該規則預設樣本連續，
    快速源期期不相交時，兩期同向只是兩次獨立抽樣剛好同號。此規則只在職缺面有效
- **主題分類是純子字串比對，中文會誤命中**（2026-08-19 查出根因）：關鍵詞 `個資`
  會在「修補 58 **個資**安漏洞」裡命中——量詞「個」黏上「資安」的「資」。
  2026-08-19 那期「隱私/法規」9 篇裡有 5 篇是這樣進來的。
  同型的還有 `第三方`（第三方外掛）與 `上市`（新車上市）。修法待決策，見 `prepare.md` 文末
- **職缺面不受上述限制**：差集以 `jobId` 為鍵，同一職缺改標題不會產生假的新增／消失
  （2026-08-10 實測 `gh-6820898` 確認）。但 Yourator 產業關鍵詞會撈進非追蹤公司，
  看異動前要先濾掉它們
- **104 / CakeResume 未納入**（有 bot 防護，本工具不做規避）：91APP、iKala 等主要在
  104 刊登的公司會顯示 0 筆，**0 筆 ≠ 沒在招**，投遞前請手動確認
- Appier 職缺為**全球**數字（官方 API），台灣部分看報告「1a 台灣職缺」節
- 技能頻率的分母是「有抓到內文」的職缺數，報告頂部有標示
- 職缺數受平台刊登行為影響，適合看**趨勢（週對週變化）**，不適合當公司招募全貌

## 相關文件

- 架構圖、模組職責、對下游的欄位契約 → `docs/ARCHITECTURE.md`
- 版本變更明細 → `CHANGELOG.md`
- 決策記錄（`MT-` 系列）→ `prepare.md`
- README 更新觸發條件、版本規則 → `../.claude/specs/docs.md`
