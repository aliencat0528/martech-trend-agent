# Changelog

格式依循 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)。

## [Unreleased]

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
