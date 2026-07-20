"""新聞抓取：讀取 config 內的 RSS 來源，保留「命中追蹤公司或 martech 主題」的文章。"""

import calendar
import time

import feedparser


def entryTimestamp(entry):
    for key in ("published_parsed", "updated_parsed"):
        parsed = entry.get(key)
        if parsed:
            return calendar.timegm(parsed)
    return 0


def matchTerms(text, terms):
    lowered = text.lower()
    return [t for t in terms if t.lower() in lowered]


def fetchAll(config, logger, maxAgeDays=30):
    """回傳 (articles, errors)。文章帶 matchedCompanies / matchedTopics 標記。"""
    articles, errors = [], []

    allCompanies = config["companies"]["tier1"] + config["companies"]["tier2"]
    topicMap = config.get("newsTopics", {})

    for feed in config.get("newsFeeds", []):
        cutoff = time.time() - feed.get("maxAgeDays", maxAgeDays) * 86400
        try:
            parsed = feedparser.parse(feed["url"])
            if parsed.bozo and not parsed.entries:
                raise RuntimeError(f"feed 解析失敗：{parsed.bozo_exception}")
            kept = 0
            for entry in parsed.entries:
                ts = entryTimestamp(entry)
                if ts and ts < cutoff:
                    continue
                text = " ".join([
                    entry.get("title", ""),
                    entry.get("summary", ""),
                ])
                matchedCompanies = [c["name"] for c in allCompanies
                                    if matchTerms(text, c["aliases"])]
                matchedTopics = [topic for topic, terms in topicMap.items()
                                 if matchTerms(text, terms)]
                feedCompany = feed.get("company")
                if feedCompany and feedCompany not in matchedCompanies:
                    matchedCompanies.append(feedCompany)
                if not feed.get("keepAll") and not matchedCompanies and not matchedTopics:
                    continue
                articles.append({
                    "feed": feed["name"],
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "publishedTs": ts,
                    "summary": entry.get("summary", "")[:500],
                    "matchedCompanies": matchedCompanies,
                    "matchedTopics": matchedTopics,
                })
                kept += 1
            logger(f"  RSS [{feed['name']}] 共 {len(parsed.entries)} 篇，留下 {kept} 篇")
        except Exception as e:
            errors.append(f"rss {feed['name']}: {e}")
            logger(f"  RSS [{feed['name']}] 失敗：{e}")

    return articles, errors
