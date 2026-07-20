#!/bin/bash
# 安裝 launchd 排程：每 3 天執行 refresh.sh（抓取＋桌面通知）。
# 本腳本會寫入 ~/Library/LaunchAgents/（專案資料夾外），故由你手動執行，Claude 不代跑。
# 安裝時自動綁定「當前所在的專案路徑」——在哪個 checkout 跑，就綁哪個。
# 建議先 merge PR #9、在主 checkout 執行，避免綁到臨時 worktree 路徑。
set -euo pipefail

PROJ="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="com.martech-trend-agent.refresh"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

# 先確認 venv 存在，否則排程首次跑會慢
if [ ! -x "$PROJ/.venv/bin/python" ]; then
  echo "⚠ 尚未建立 .venv，請先執行：cd \"$PROJ\" && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
fi

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$PROJ/scripts/refresh.sh</string>
  </array>
  <key>StartInterval</key><integer>259200</integer>
  <key>RunAtLoad</key><false/>
  <key>StandardOutPath</key><string>$PROJ/scripts/refresh.log</string>
  <key>StandardErrorPath</key><string>$PROJ/scripts/refresh.log</string>
</dict>
</plist>
EOF

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "✅ 已安裝排程：每 3 天執行一次 refresh.sh"
echo "   plist：$PLIST"
echo "   綁定專案：$PROJ"
echo "   立即測試：launchctl start $LABEL"
echo "   移除：bash scripts/uninstall-schedule.sh"
