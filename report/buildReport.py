"""報告層：把 stats.json 轉成繁中 markdown 報告（含判讀指引）。"""

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


def build(runDate, stats, errors):
    jobs = stats["jobs"]
    news = stats["news"]
    trend = stats["trend"]
    lines = []
    add = lines.append

    add(f"# MarTech 趨勢週報 · {runDate}")
    add("")
    add(f"> 產生時間：{time.strftime('%Y-%m-%d %H:%M')}　|　"
        f"職缺 {jobs['totalJobs']} 筆（含內文 {jobs['describedJobs']} 筆）　|　"
        f"相關新聞 {news['totalArticles']} 篇")
    if errors:
        add(f"> ⚠️ 本次有 {len(errors)} 個來源抓取失敗（見文末），相關數字會偏低。")
    add("")

    add("## 1. 追蹤公司職缺數（Tier 1 台灣）")
    add("")
    add(rankTable(jobs["byCompany"], "公司"))
    add("")
    add("**判讀**：職缺數是公司擴張的領先指標。連續數週增加＝業務成長或新產品線；"
        "歸零或驟減要注意（凍編或轉向）。**0 筆 ≠ 沒在招**——本工具只覆蓋 Greenhouse 與 "
        "Yourator，91APP/iKala 等主要在 104/CakeResume 刊登的公司請手動確認。"
        "Appier 的數字是全球職缺（官方 API），台灣部分見下一節。")
    add("")

    if jobs.get("taiwanJobs"):
        add("### 1a. 追蹤公司「台灣」職缺（可直接投遞清單）")
        add("")
        add("| 公司 | 職稱 | 類別 | 地點 |")
        add("|---|---|---|---|")
        for j in jobs["taiwanJobs"]:
            add(f"| {j['company']} | [{j['title']}]({j['link']}) | {j['role']} | {j['area']} |")
        add("")
        add("**判讀**：這是本報告最可直接行動的一節——你的投遞池。"
            "「數據分析／技術顧問」類優先看；行銷/客戶成功類若含 data 字眼也值得點開。")
        add("")

    add("## 2. 職稱結構（整體市場，含產業關鍵詞搜尋）")
    add("")
    add(rankTable(jobs["byRole"], "職稱類別"))
    add("")
    add("**判讀**：「數據分析＋技術顧問/TSE」的佔比是你的可投遞池。"
        "若「數據科學/ML」遠多於「數據分析」，代表該市場偏研發、對 DA 新人較不利。")
    add("")

    add("## 3. 技能關鍵詞需求（出現在幾筆職缺中）")
    add("")
    add(rankTable(jobs["skillFrequency"], "技能", topN=20))
    add("")
    add(f"**判讀**：分母是有抓到內文的 {jobs['describedJobs']} 筆職缺。"
        "排前面的是硬門檻（SQL/Python 通常穩居前列＝你的 30 天計畫方向正確）；"
        "注意 LLM / AI Agent 的排名變化——它爬得越快，你作品集的 agent 主軸越加分。")
    add("")

    if jobs.get("salarySummary"):
        add("### 薪資樣本（僅含有公開薪資的職缺，月薪）")
        add("")
        add("| 職稱類別 | 樣本數 | 中位數下限 | 中位數上限 |")
        add("|---|---|---|---|")
        for s in jobs["salarySummary"]:
            add(f"| {s['role']} | {s['count']} | {s['medianLow']:,} | {s['medianHigh']:,} |")
        add("")
        add("**判讀**：樣本少時（<5）只當參考值。用途是談薪前知道行情帶，"
            "以及觀察同類職缺薪資帶是否隨時間上移。")
        add("")

    add("## 4. 新聞聲量")
    add("")
    add("### 公司被提及次數（近 30 天）")
    add("")
    add(rankTable(news["companyMentions"], "公司"))
    add("")
    add("### 主題聲量")
    add("")
    add(rankTable(news["topicMentions"], "主題"))
    add("")
    add("**判讀**：主題聲量看產業風向（AI Agent、CDP 誰在升）；"
        "公司聲量突然變高要點進下方文章看是好事（募資/新產品）還是壞事。"
        "面試前一週掃一次「該公司的文章」是最低成本的功課。")
    add("")

    if news["companyArticles"]:
        add("### 追蹤公司相關文章")
        add("")
        for a in news["companyArticles"]:
            dateStr = time.strftime("%m/%d", time.localtime(a["publishedTs"])) \
                if a["publishedTs"] else "--"
            companies = "、".join(a["matchedCompanies"])
            add(f"- {dateStr}【{companies}】[{a['title']}]({a['link']})（{a['feed']}）")
        add("")

    add("## 5. 趨勢變化（與上次快照比較）")
    add("")
    if not trend["hasBaseline"]:
        add("本次為**第一次執行（基準點）**，尚無比較對象。下次執行起，"
            "這裡會顯示：新增/消失的職缺、技能關鍵詞需求升降。建議每週跑一次。")
    else:
        add(f"比較基準：{trend['baselineDate']}")
        add("")
        add(f"- 新增職缺 **{trend['newCount']}** 筆、消失職缺 **{trend['removedCount']}** 筆")
        if trend["newJobs"]:
            add("")
            add("**新增職缺**（最多列 30 筆）：")
            for j in trend["newJobs"]:
                add(f"- [{j['title']}]({j['link']}) — {j['company']}")
        if trend["skillDelta"]:
            add("")
            add("**技能需求升降**（與上次相比）：")
            for skill, diff in list(trend["skillDelta"].items())[:15]:
                sign = "+" if diff > 0 else ""
                add(f"- {skill}: {sign}{diff}")
        add("")
        add("**判讀**：「消失的職缺」= 已補齊或撤掉，出現過的職缺類型代表該公司會再開；"
            "新增職缺是投遞時機訊號——刊登 7 天內投遞回覆率最高。")
    add("")

    if errors:
        add("## ⚠️ 本次抓取失敗的來源")
        add("")
        for e in errors:
            add(f"- {e}")
        add("")

    add("---")
    add("")
    add("*由 martech-trend-agent 自動產生。資料來源：Greenhouse 官方 API、Yourator、公開 RSS。"
        "職缺數受平台刊登行為影響，僅供趨勢判讀，非公司實際招募全貌。*")
    return "\n".join(lines)
