#!/bin/bash
# 移除 launchd 排程。由你手動執行（碰 ~/Library/LaunchAgents/，Claude 不代跑）。
set -euo pipefail
LABEL="com.martech-trend-agent.refresh"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
launchctl unload "$PLIST" 2>/dev/null || true
rm -f "$PLIST"
echo "✅ 已移除 MarTech 排程（$LABEL）"
