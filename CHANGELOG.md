# Changelog

格式依循 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)。

## [Unreleased]

## [1.0.0] - 2026-07-19

### Added
- 抓取層：Greenhouse 官方 Job Board API（Appier，含職缺內文）、Yourator 搜尋 API（台灣新創，僱主過濾）、5 個新聞 RSS 源
- 統計層：公司職缺數、職稱分類、技能關鍵詞頻率、薪資樣本中位數、台灣可投遞清單、跨快照趨勢比較
- 報告層：繁中 markdown 週報（每節附判讀指引），`reports/latest.md` 同步更新
- `--no-jobs` / `--no-news` / `--reanalyze` 執行選項

### Removed
- 104 抓取模組——端點有 Cloudflare bot 防護，不做規避，改以 Greenhouse＋Yourator 為職缺來源
