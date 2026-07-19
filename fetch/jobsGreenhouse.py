"""Greenhouse 職缺抓取：使用官方公開 Job Board API（無需金鑰）。

只要公司在 config 的 tier1 條目設定 `greenhouse: <board_token>`，就會抓該公司全部職缺
（含完整職缺內文，供技能關鍵詞統計）。
"""

import html
import re

import requests

BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
HEADERS = {"User-Agent": "martech-trend-agent (personal job research)"}


def stripHtml(raw):
    text = html.unescape(raw or "")
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalizeJob(raw, compName):
    location = (raw.get("location") or {}).get("name", "")
    return {
        "source": "greenhouse",
        "jobId": f"gh-{raw.get('id')}",
        "title": raw.get("title", ""),
        "company": raw.get("company_name", compName),
        "area": location,
        "salaryDesc": "",
        "salaryLow": 0,
        "salaryHigh": 0,
        "appearDate": (raw.get("first_published") or raw.get("updated_at") or "")[:10],
        "link": raw.get("absolute_url", ""),
        "matchedKeyword": f"company:{compName}",
        "trackedCompany": compName,
        "description": stripHtml(raw.get("content", "")),
    }


def fetchAll(config, logger):
    """回傳 (jobs, errors)。"""
    jobs, errors = [], []
    for comp in config["companies"]["tier1"]:
        token = comp.get("greenhouse")
        if not token:
            continue
        try:
            resp = requests.get(BOARD_URL.format(token=token), headers=HEADERS, timeout=30)
            resp.raise_for_status()
            raws = resp.json().get("jobs", [])
            for raw in raws:
                jobs.append(normalizeJob(raw, comp["name"]))
            logger(f"  Greenhouse [{comp['name']}] {len(raws)} 筆（官方 API，含內文）")
        except Exception as e:
            errors.append(f"greenhouse {comp['name']}: {e}")
            logger(f"  Greenhouse [{comp['name']}] 失敗：{e}")
    return jobs, errors
