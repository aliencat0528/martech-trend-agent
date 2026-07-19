# martech-trend-agent - MarTech 商業趨勢自動追蹤與統計分析

自動抓取 Appier 為首的 MarTech 公司職缺與產業新聞，統計分析後產出繁中趨勢報告，回答三個問題：**哪些公司在擴張、市場要我會什麼技能、產業風向往哪吹**。

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 功能特色 【必要】

- **職缺追蹤**：Greenhouse 官方 API（Appier 全球職缺含完整內文）＋ Yourator（台灣新創），僱主名稱過濾避免誤收
- **統計分析**：公司職缺數、職稱結構、技能關鍵詞需求頻率、薪資樣本、台灣可投遞清單
- **新聞聲量**：5 個 RSS 源（iThome／TechOrange／INSIDE／MarTech.org／MarketingDive），公司提及數與主題聲量
- **趨勢比較**：每次執行存日期快照，自動與上次比較（新增／消失職缺、技能需求升降）
- **報告自帶判讀指引**：每個統計節附「怎麼讀這個數字」

## 快速開始 【必要】

```bash
cd martech-trend-agent
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python run.py
# 預期：依序印出「▶ 抓取…」各來源筆數，最後
# ✅ 完成。職缺 N 筆、新聞 M 篇、失敗來源 0 個
#    報告：reports/report-YYYY-MM-DD.md（latest.md 同步更新）
```

## 使用方式 【必要】

| 指令 | 用途 |
|------|------|
| `.venv/bin/python run.py` | 完整執行：抓取 → 分析 → 報告（建議每週一次） |
| `.venv/bin/python run.py --no-jobs` | 只更新新聞 |
| `.venv/bin/python run.py --no-news` | 只更新職缺 |
| `.venv/bin/python run.py --reanalyze 2026-07-19` | 不重抓，用既有快照重跑分析（改完 config 後用） |

**加公司／技能／新聞源**：只改 `config.yaml`，不用動程式碼。公司若使用 Greenhouse 徵才，
在該公司條目加 `greenhouse: <board_token>` 可取得最完整資料。

**判讀方式**：報告每節下方有粗體「判讀」段落；整體原則見 `reports/latest.md` 文末限制說明。

## 專案結構 【必要】

```
martech-trend-agent/
├── config.yaml          # 公司清單、關鍵詞、RSS 來源（唯一需要編輯的檔案）
├── run.py               # 主程式：抓取 → 分析 → 報告
├── fetch/               # 抓取層（jobsGreenhouse / jobsYourator / newsRss）
├── analyze/stats.py     # 統計層（分類、頻率、趨勢比較）
├── report/buildReport.py# 報告層（繁中 markdown，含判讀指引）
├── data/raw/YYYY-MM-DD/ # 每次執行的原始快照（趨勢比較的基準）
└── reports/             # report-YYYY-MM-DD.md 與 latest.md
```

## 測試 【必要】

```bash
.venv/bin/python run.py --reanalyze <既有快照日期>   # 不打網路，驗證分析與報告層
```

## 版本歷史 【必要】

### v1.0.0 (2026-07-19)

- **首版 pipeline** — Greenhouse＋Yourator＋RSS 三源抓取、統計分析、繁中報告與趨勢快照

## 授權 【必要】

MIT License

---

## 資料來源限制（判讀前必讀）

- **104 / CakeResume 未納入**（有 bot 防護，本工具不做規避）：91APP、iKala 等主要在
  104 刊登的公司會顯示 0 筆，**0 筆 ≠ 沒在招**，投遞前請手動確認
- Appier 職缺為**全球**數字（官方 API），台灣部分看報告「1a 台灣職缺」節
- 技能頻率的分母是「有抓到內文」的職缺數，報告頂部有標示
- 職缺數受平台刊登行為影響，適合看**趨勢（週對週變化）**，不適合當公司招募全貌

## 相關文件

- README 更新觸發條件、版本規則 → `../.claude/specs/docs.md`
