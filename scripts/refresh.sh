#!/bin/bash
# martech-trend-agent 定期刷新（機械層）：抓取＋統計，完成後桌面通知。
# 由 launchd 每 3 天觸發（見 install-schedule.sh）。
# 分析與 email 不在這裡——見解需要模型在場，由 Claude 在 /martech-report 時產生。
set -euo pipefail

PROJ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJ"

PYBIN="/opt/homebrew/bin/python3"
if [ ! -x .venv/bin/python ]; then
  "$PYBIN" -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
fi

if .venv/bin/python run.py; then
  TITLE="MarTech 趨勢 · 資料就緒"
  MSG="資料已更新，開 Claude Code 執行 /martech-report 產生分析報告"
else
  TITLE="MarTech 趨勢 · 抓取異常"
  MSG="抓取失敗，請查看 scripts/refresh.log"
fi
/usr/bin/osascript -e "display notification \"$MSG\" with title \"$TITLE\" sound name \"Glass\"" || true
