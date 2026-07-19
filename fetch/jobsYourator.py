"""Yourator 職缺抓取：新創職缺板，台灣 martech 公司多數有刊登。

使用其前端搜尋 API（/api/v4/jobs，回應在 payload.jobs）。
職缺內文另抓公開職缺頁面（去除 HTML 標籤後供技能統計），總量有上限以示禮貌。
"""

import re
import time

import requests

SEARCH_URL = "https://www.yourator.co/api/v4/jobs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
}
REQUEST_INTERVAL_SEC = 1.0
MAX_DETAIL_TOTAL = 40  # 每次執行最多抓幾頁職缺內文


def searchJobs(term):
    resp = requests.get(SEARCH_URL, params={"term[]": term, "page": 1},
                        headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.json().get("payload", {}).get("jobs", [])


def fetchJobPageText(url):
    """抓公開職缺頁面並去標籤，失敗回空字串。"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", resp.text, flags=re.S)
        text = re.sub(r"<[^>]+>", " ", text)
        return re.sub(r"\s+", " ", text).strip()
    except Exception:
        return ""


def parseSalary(salaryText):
    """'NT$ 940,000 - 1,500,000 (年薪)' → 月薪 (low, high)；時薪/面議回 (0, 0)。"""
    if not salaryText or "時薪" in salaryText:
        return 0, 0
    nums = [int(n.replace(",", "")) for n in re.findall(r"[\d,]{4,}", salaryText)]
    if not nums:
        return 0, 0
    low, high = nums[0], nums[-1]
    if "年薪" in salaryText:
        low, high = low // 12, high // 12
    return low, high


def normalizeJob(raw, matchedKeyword):
    companyInfo = raw.get("company", {}) or {}
    path = raw.get("path", "")
    salaryLow, salaryHigh = parseSalary(raw.get("salary", "") or "")
    return {
        "source": "yourator",
        "jobId": f"ytor-{raw.get('id', path)}",
        "title": raw.get("name", ""),
        "company": companyInfo.get("brand", "") or companyInfo.get("name", ""),
        "area": raw.get("location", "") or "",
        "salaryDesc": raw.get("salary", "") or "",
        "salaryLow": salaryLow,
        "salaryHigh": salaryHigh,
        "appearDate": "",
        "link": f"https://www.yourator.co{path}" if path.startswith("/") else path,
        "matchedKeyword": matchedKeyword,
        "description": "",
    }


def fetchAll(config, logger):
    """Tier1 公司名搜尋（僱主過濾）＋產業關鍵詞搜尋。回傳 (jobs, errors)。"""
    jobs, errors, seen = [], [], set()
    detailBudget = MAX_DETAIL_TOTAL

    def addJobs(raws, matchedKeyword, trackedCompany):
        nonlocal detailBudget
        added = 0
        for raw in raws:
            job = normalizeJob(raw, matchedKeyword)
            if job["jobId"] in seen:
                continue
            seen.add(job["jobId"])
            job["trackedCompany"] = trackedCompany
            if detailBudget > 0:
                job["description"] = fetchJobPageText(job["link"])
                detailBudget -= 1
                time.sleep(REQUEST_INTERVAL_SEC)
            jobs.append(job)
            added += 1
        return added

    for comp in config["companies"]["tier1"]:
        if comp.get("greenhouse"):
            continue  # 已有官方 API 來源，避免重複計數
        try:
            raws = searchJobs(comp["aliases"][0])
            matched = []
            for raw in raws:
                companyName = ((raw.get("company", {}) or {}).get("brand", "") or
                               (raw.get("company", {}) or {}).get("name", ""))
                if any(a.lower() in companyName.lower() for a in comp["aliases"]):
                    matched.append(raw)
            added = addJobs(matched, f"company:{comp['name']}", comp["name"])
            logger(f"  Yourator [{comp['name']}] 命中 {added} 筆")
            time.sleep(REQUEST_INTERVAL_SEC)
        except Exception as e:
            errors.append(f"yourator {comp['name']}: {e}")
            logger(f"  Yourator [{comp['name']}] 失敗：{e}")

    for keyword in config.get("jobSearchKeywords", []):
        try:
            raws = searchJobs(keyword)
            added = addJobs(raws, f"industry:{keyword}", "")
            logger(f"  Yourator [產業:{keyword}] 新增 {added} 筆")
            time.sleep(REQUEST_INTERVAL_SEC)
        except Exception as e:
            errors.append(f"yourator industry {keyword}: {e}")
            logger(f"  Yourator [產業:{keyword}] 失敗：{e}")

    return jobs, errors
