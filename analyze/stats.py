"""統計層：把原始快照變成統計結果（公司職缺數、職稱分類、技能頻率、主題聲量、趨勢比較）。"""

import json
import re
from collections import Counter
from pathlib import Path


def classifyRole(title, roleCategories):
    lowered = title.lower()
    for category, terms in roleCategories.items():
        if any(t.lower() in lowered for t in terms):
            return category
    return "其他"


def countSkills(texts, skillKeywords):
    """統計技能關鍵詞在幾筆文本中出現（每筆最多算一次，避免單篇灌水）。"""
    counter = Counter()
    for text in texts:
        lowered = text.lower()
        for skill in skillKeywords:
            pattern = re.escape(skill.lower())
            # 英文短詞（如 R、Git）要求詞邊界，中文詞直接子字串比對
            if re.fullmatch(r"[a-z0-9 .+#/]+", skill.lower()):
                if re.search(rf"(?<![a-z0-9]){pattern}(?![a-z0-9])", lowered):
                    counter[skill] += 1
            elif skill.lower() in lowered:
                counter[skill] += 1
    return counter


TAIWAN_AREA_TERMS = ["台北", "臺北", "taipei", "taiwan", "新北", "台灣"]


def jobStats(jobs, config):
    roleCategories = config["roleCategories"]
    companyCounter = Counter({c["name"]: 0 for c in config["companies"]["tier1"]})
    roleCounter = Counter()
    companyRoles = {}
    salaryRows = []
    taiwanJobs = []

    for job in jobs:
        role = classifyRole(job["title"], roleCategories)
        job["roleCategory"] = role
        roleCounter[role] += 1
        tracked = job.get("trackedCompany", "")
        if tracked:
            companyCounter[tracked] += 1
            companyRoles.setdefault(tracked, Counter())[role] += 1
            area = job.get("area", "").lower()
            if any(t in area for t in TAIWAN_AREA_TERMS):
                taiwanJobs.append({"company": tracked, "title": job["title"],
                                   "role": role, "area": job["area"], "link": job["link"]})
        if job.get("salaryLow", 0) >= 20000 and job.get("salaryHigh", 0) >= job["salaryLow"]:
            salaryRows.append({
                "company": tracked or job["company"], "role": role,
                "low": job["salaryLow"],
                "high": min(job["salaryHigh"], job["salaryLow"] * 3),  # 排除灌水上限
            })

    texts = [f"{j['title']} {j.get('description', '')}" for j in jobs]
    skillCounter = countSkills(texts, config["skillKeywords"])
    describedCount = sum(1 for j in jobs if j.get("description"))

    salaryByRole = {}
    for row in salaryRows:
        salaryByRole.setdefault(row["role"], []).append(row)
    salarySummary = []
    for role, rows in sorted(salaryByRole.items(), key=lambda kv: -len(kv[1])):
        lows = sorted(r["low"] for r in rows)
        highs = sorted(r["high"] for r in rows)
        salarySummary.append({
            "role": role, "count": len(rows),
            "medianLow": lows[len(lows) // 2], "medianHigh": highs[len(highs) // 2],
        })

    return {
        "totalJobs": len(jobs),
        "describedJobs": describedCount,
        "byCompany": dict(companyCounter.most_common()),
        "byRole": dict(roleCounter.most_common()),
        "companyRoles": {c: dict(r.most_common()) for c, r in companyRoles.items()},
        "skillFrequency": dict(skillCounter.most_common()),
        "salarySamples": salaryRows,
        "salarySummary": salarySummary,
        "taiwanJobs": taiwanJobs,
    }


def newsStats(articles):
    companyCounter = Counter()
    topicCounter = Counter()
    for article in articles:
        for c in article["matchedCompanies"]:
            companyCounter[c] += 1
        for t in article["matchedTopics"]:
            topicCounter[t] += 1
    topArticles = sorted(
        [a for a in articles if a["matchedCompanies"]],
        key=lambda a: a["publishedTs"], reverse=True)[:20]

    # 每個主題挑最新的代表文章（應用趨勢的證據，不只給數字）
    topicArticles = {}
    for topic in topicCounter:
        matched = sorted([a for a in articles if topic in a["matchedTopics"]],
                         key=lambda a: a["publishedTs"], reverse=True)
        topicArticles[topic] = [
            {"title": a["title"], "link": a["link"], "feed": a["feed"],
             "publishedTs": a["publishedTs"]}
            for a in matched[:3]]

    return {
        "totalArticles": len(articles),
        "companyMentions": dict(companyCounter.most_common()),
        "topicMentions": dict(topicCounter.most_common()),
        "companyArticles": topArticles,
        "topicArticles": topicArticles,
    }


def previousSnapshotDir(rawRoot, currentDate):
    """找出比本次早的最近一次快照目錄，沒有則回 None。"""
    dirs = sorted(d.name for d in Path(rawRoot).iterdir()
                  if d.is_dir() and d.name < currentDate)
    return Path(rawRoot) / dirs[-1] if dirs else None


def trendCompare(currentJobs, currentSkillFreq, currentTopicMentions, prevDir):
    """與上一次快照比較：主題聲量升降、職缺增減、技能關鍵詞升降。"""
    if prevDir is None or not (prevDir / "jobs.json").exists():
        return {"hasBaseline": False}

    prevJobs = json.loads((prevDir / "jobs.json").read_text(encoding="utf-8"))
    prevStats = {}
    statsPath = prevDir / "stats.json"
    if statsPath.exists():
        prevStats = json.loads(statsPath.read_text(encoding="utf-8"))

    currentIds = {j["jobId"]: j for j in currentJobs}
    prevIds = {j["jobId"]: j for j in prevJobs}
    newJobs = [j for jid, j in currentIds.items() if jid not in prevIds]
    removedJobs = [j for jid, j in prevIds.items() if jid not in currentIds]

    skillDelta = {}
    prevSkills = prevStats.get("jobs", {}).get("skillFrequency", {})
    for skill, count in currentSkillFreq.items():
        diff = count - prevSkills.get(skill, 0)
        if diff != 0:
            skillDelta[skill] = diff

    topicDelta = {}
    prevTopics = prevStats.get("news", {}).get("topicMentions", {})
    for topic in set(currentTopicMentions) | set(prevTopics):
        diff = currentTopicMentions.get(topic, 0) - prevTopics.get(topic, 0)
        if diff != 0:
            topicDelta[topic] = diff

    return {
        "topicDelta": dict(sorted(topicDelta.items(), key=lambda kv: -abs(kv[1]))),
        "hasBaseline": True,
        "baselineDate": prevDir.name,
        "newJobs": [{"title": j["title"], "company": j["company"], "link": j["link"]}
                    for j in newJobs][:30],
        "removedJobs": [{"title": j["title"], "company": j["company"]}
                        for j in removedJobs][:30],
        "newCount": len(newJobs),
        "removedCount": len(removedJobs),
        "skillDelta": dict(sorted(skillDelta.items(), key=lambda kv: -abs(kv[1]))),
    }
