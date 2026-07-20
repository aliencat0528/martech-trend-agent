"""報告層：把 stats.json 轉成繁中 markdown 報告（含判讀指引）。

結構主軸：MarTech「應用趨勢」（新聞/文章）為主，職缺為次要（公司分析需求訊號）。
"""

import time


def bar(count, maxCount, width=20):
    filled = round(width * count / maxCount) if maxCount else 0
    return "█" * filled + "░" * (width - filled)


def rankTable(counterDict, header, topN=15):
    lines = [f"| {header} | 數量 | |", "|---|---|---|"]
    items = list(counterDict.items())[:topN]
    maxCount = items[0][1] if items else 1
    for name, count in items:
        lines.append(f"| {name} | {count} | `{bar(count, maxCount)}` |")
    return "\n".join(lines) if items else "（本次無資料）"


def fmtDate(ts):
    return time.strftime("%m/%d", time.localtime(ts)) if ts else "--"


def build(runDate, stats, errors):
    jobs = stats["jobs"]
    news = stats["news"]
    trend = stats["trend"]
    lines = []
    add = lines.append

    add(f"# MarTech 應用趨勢週報 · {runDate}")
    add("")
    add(f"> 產生時間：{time.strftime('%Y-%m-%d %H:%M')}　|　"
        f"相關文章 {news['totalArticles']} 篇　|　"
        f"職缺 {jobs['totalJobs']} 筆（含內文 {jobs['describedJobs']} 筆）")
    if errors:
        add(f"> ⚠️ 本次有 {len(errors)} 個來源抓取失敗（見文末），相關數字會偏低。")
    add("")

    # ── 主軸：應用趨勢 ────────────────────────────────────
    add("## 1. 應用主題聲量（近 30 天文章）")
    add("")
    add(rankTable(news["topicMentions"], "應用主題"))
    add("")
    add("**判讀**：這是本報告的主指標——每個主題有幾篇文章在談。單週的絕對值意義有限，"
        "要看**連續幾週的排序變化**：一個主題從中段爬升到前三（如 AI Agent應用），"
        "代表廠商開始把它產品化，通常 6–12 個月後反映在台灣的職缺與客戶需求上。"
        "產業媒體（MarTech.org、ChiefMartec）談概念，公司部落格（Appier/Insider Blog）"
        "談落地——後者出現＝已經在賣了。")
    add("")

    if news.get("topicArticles"):
        add("### 1a. 各主題代表文章（依時間新→舊）")
        add("")
        for topic, count in news["topicMentions"].items():
            arts = news["topicArticles"].get(topic, [])
            if not arts:
                continue
            add(f"**{topic}**（{count} 篇）")
            for a in arts:
                add(f"- {fmtDate(a['publishedTs'])} [{a['title']}]({a['link']})（{a['feed']}）")
            add("")
        add("**判讀**：判斷趨勢不要只看數字，點進標題掃一眼：談的是願景（想做）"
            "還是案例（做到了）？案例型文章多的主題才是真趨勢。")
        add("")

    add("## 2. 公司聲量（近 30 天被提及）")
    add("")
    add(rankTable(news["companyMentions"], "公司"))
    add("")
    if news["companyArticles"]:
        add("**追蹤公司相關文章**：")
        add("")
        for a in news["companyArticles"]:
            companies = "、".join(a["matchedCompanies"])
            add(f"- {fmtDate(a['publishedTs'])}【{companies}】"
                f"[{a['title']}]({a['link']})（{a['feed']}）")
        add("")
    add("**判讀**：聲量突然變高要點進文章看是好事（募資/新產品/大客戶）還是壞事。"
        "0 次很常見（RSS 只涵蓋近期），不代表公司沒動作；面試前一週再手動搜一次該公司新聞。")
    add("")

    # ── 次要：職缺＝公司分析需求訊號 ──────────────────────
    add("## 3. 職缺訊號（次要指標：公司在為哪些能力擴編）")
    add("")
    add("### 3a. 追蹤公司職缺數")
    add("")
    add(rankTable(jobs["byCompany"], "公司"))
    add("")
    add("### 3b. 技能關鍵詞需求（出現在幾筆職缺中）")
    add("")
    add(rankTable(jobs["skillFrequency"], "技能", topN=15))
    add("")
    add(f"**判讀**：職缺是「應用趨勢的落地驗證」——文章在談的主題若同步出現在職缺"
        f"（如 LLM / AI Agent 進技能榜前五），代表趨勢已經走到要人執行的階段。"
        f"技能分母是有內文的 {jobs['describedJobs']} 筆。"
        "職缺覆蓋限制：只含 Greenhouse（Appier 全球）與 Yourator，"
        "91APP/iKala 等主要在 104 刊登者會低估，0 筆 ≠ 沒在招。")
    add("")

    if jobs.get("taiwanJobs"):
        add("### 3c. 追蹤公司「台灣」職缺（可直接投遞清單）")
        add("")
        add("| 公司 | 職稱 | 類別 | 地點 |")
        add("|---|---|---|---|")
        for j in jobs["taiwanJobs"]:
            add(f"| {j['company']} | [{j['title']}]({j['link']}) | {j['role']} | {j['area']} |")
        add("")

    if jobs.get("salarySummary"):
        add("### 3d. 薪資樣本（僅含有公開薪資的職缺，月薪）")
        add("")
        add("| 職稱類別 | 樣本數 | 中位數下限 | 中位數上限 |")
        add("|---|---|---|---|")
        for s in jobs["salarySummary"]:
            add(f"| {s['role']} | {s['count']} | {s['medianLow']:,} | {s['medianHigh']:,} |")
        add("")
        add("**判讀**：樣本少時（<5）只當參考值，用途是知道行情帶與觀察薪資帶是否上移。")
        add("")

    # ── 趨勢比較 ──────────────────────────────────────────
    add("## 4. 趨勢變化（與上次快照比較）")
    add("")
    if not trend["hasBaseline"]:
        add("本次為**第一次執行（基準點）**，尚無比較對象。下次執行起，這裡會顯示："
            "主題聲量升降、新增/消失職缺、技能需求升降。建議每週跑一次。")
    else:
        add(f"比較基準：{trend['baselineDate']}")
        add("")
        if trend.get("topicDelta"):
            add("**應用主題聲量升降**（本報告最重要的趨勢訊號）：")
            for topic, diff in list(trend["topicDelta"].items())[:10]:
                sign = "+" if diff > 0 else ""
                add(f"- {topic}: {sign}{diff}")
            add("")
        add(f"- 新增職缺 **{trend['newCount']}** 筆、消失職缺 **{trend['removedCount']}** 筆")
        if trend["newJobs"]:
            add("")
            add("**新增職缺**（最多列 30 筆）：")
            for j in trend["newJobs"]:
                add(f"- [{j['title']}]({j['link']}) — {j['company']}")
        if trend["skillDelta"]:
            add("")
            add("**技能需求升降**：")
            for skill, diff in list(trend["skillDelta"].items())[:15]:
                sign = "+" if diff > 0 else ""
                add(f"- {skill}: {sign}{diff}")
        add("")
        add("**判讀**：主題聲量連續兩週以上上升＝真趨勢，單週跳動＝可能只是某事件洗版"
            "（點回 1a 的文章確認）。新增職缺是投遞時機訊號——刊登 7 天內投遞回覆率最高。")
    add("")

    if errors:
        add("## ⚠️ 本次抓取失敗的來源")
        add("")
        for e in errors:
            add(f"- {e}")
        add("")

    add("---")
    add("")
    add("*由 martech-trend-agent 自動產生。資料來源：公開 RSS（產業媒體＋公司部落格）、"
        "Greenhouse 官方 API、Yourator。數字受來源覆蓋範圍影響，僅供趨勢判讀。*")
    return "\n".join(lines)
