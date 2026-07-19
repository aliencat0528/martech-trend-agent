> 繼承根目錄共用規則（Claude Code 已自動載入，勿重複讀取 ../CLAUDE.md）

# martech-trend-agent

## 技術棧與指令

- Python 3.12＋venv（`.venv/`，不進 git）；依賴僅 requests / feedparser / pyyaml
- 執行：`.venv/bin/python run.py`（選項見 README）
- Lint：`.venv/bin/python -m py_compile run.py fetch/*.py analyze/*.py report/*.py`

## 與根規則的差異

- **資料快照要進 git**：`data/raw/YYYY-MM-DD/*.json` 是趨勢比較的基準，屬「程式產出的資料資產」，
  不適用「禁止手動修改自動生成資料檔」＝仍禁止手改，但由 pipeline 重新產生後 commit 是正常流程
- **抓取禮儀**：只用官方公開 API 或開放給前端的 JSON 端點；請求間隔 ≥1 秒；
  來源加 bot 防護（如 104 的 Cloudflare）就放棄該來源，**禁止加入任何繞過防護的依賴**（cloudscraper 等）

## 決策記錄

見 `prepare.md`（編號前綴 `MT-`）。
