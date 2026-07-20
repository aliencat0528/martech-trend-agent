# Prepare — martech-trend-agent 決策記錄

> 記錄規則繼承根 `prepare.md`，只寫本專案差異。編號前綴 `MT-`。

## 決策日誌

### MT-002 · 2026-07-20 · 主軸修正：應用趨勢為主、職缺為次
- **決策**（用戶指示）：報告主軸＝新聞/文章的應用趨勢判斷；職缺降為次要節（公司需求訊號）
- **落地**：新聞源 5→9（加 ChiefMartec/MarTech Series/Appier Blog/Insider Blog）、
  主題分類 8→12 類、每主題附代表文章、趨勢比較新增主題聲量升降；
  feed 支援 `keepAll`（純 MarTech 源全收）與 `maxAgeDays`（低頻源放寬時間窗）

### MT-001 · 2026-07-19 · 職缺來源選擇
- **決策**：職缺來源＝Greenhouse 官方 API（Appier）＋ Yourator；104 不納入
- **理由**：104 搜尋端點已上 Cloudflare bot 防護（實測 403／挑戰頁），規避防護不做；
  Greenhouse 為官方公開 API 且含完整內文，資料品質反而更好
- **代價**：91APP／iKala 等只在 104 刊登的公司職缺數會是 0，報告已標注此限制
- **關聯**：← D-001（本專案為求職資訊基礎設施，服務 Appier 投遞主線）

### MT-000 · 2026-07-19 · 專案建立
- 生活線作品「Martech 情報 pipeline」落地為本專案；範圍：台灣職缺＋國際新聞、
  手動執行為主、報告 markdown＋HTML artifact（三項均經用戶確認）
