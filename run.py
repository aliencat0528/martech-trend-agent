"""Martech Trend Agent 主程式。

用法：
    .venv/bin/python run.py             # 完整執行：抓取 → 分析 → 報告
    .venv/bin/python run.py --no-jobs   # 跳過職缺（只更新新聞）
    .venv/bin/python run.py --no-news   # 跳過新聞
    .venv/bin/python run.py --reanalyze 2026-07-19   # 不抓取，重跑指定日期快照的分析與報告
"""

import argparse
import json
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from fetch import jobsGreenhouse, jobsYourator, newsRss  # noqa: E402
from analyze import stats as statsMod  # noqa: E402
from report import buildReport  # noqa: E402


def log(msg):
    print(msg, flush=True)


def loadJson(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def saveJson(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-jobs", action="store_true")
    parser.add_argument("--no-news", action="store_true")
    parser.add_argument("--reanalyze", metavar="DATE", help="重跑指定日期快照的分析")
    args = parser.parse_args()

    config = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
    runDate = args.reanalyze or time.strftime("%Y-%m-%d")
    snapDir = ROOT / "data" / "raw" / runDate
    snapDir.mkdir(parents=True, exist_ok=True)

    errors = []

    # ── 抓取 ──────────────────────────────────────────────
    if args.reanalyze:
        log(f"[reanalyze] 使用既有快照 {runDate}")
        jobs = loadJson(snapDir / "jobs.json", [])
        articles = loadJson(snapDir / "news.json", [])
    else:
        jobs = loadJson(snapDir / "jobs.json", [])  # 同日重跑：續用已抓的部分
        if not args.no_jobs:
            log("▶ 抓取 Greenhouse 職缺（官方 API）…")
            jGh, eGh = jobsGreenhouse.fetchAll(config, log)
            log("▶ 抓取 Yourator 職缺…")
            jYtor, eYtor = jobsYourator.fetchAll(config, log)
            seen = set()
            jobs = [j for j in jGh + jYtor
                    if not (j["jobId"] in seen or seen.add(j["jobId"]))]
            errors += eGh + eYtor
            saveJson(snapDir / "jobs.json", jobs)
        articles = loadJson(snapDir / "news.json", [])
        if not args.no_news:
            log("▶ 抓取新聞 RSS…")
            articles, eNews = newsRss.fetchAll(config, log)
            errors += eNews
            saveJson(snapDir / "news.json", articles)

    # ── 分析 ──────────────────────────────────────────────
    log("▶ 統計分析…")
    jobResult = statsMod.jobStats(jobs, config)
    newsResult = statsMod.newsStats(articles)
    prevDir = statsMod.previousSnapshotDir(ROOT / "data" / "raw", runDate)
    trendResult = statsMod.trendCompare(jobs, jobResult["skillFrequency"],
                                        newsResult["topicMentions"], prevDir)

    allStats = {"date": runDate, "jobs": jobResult, "news": newsResult,
                "trend": trendResult, "errors": errors}
    saveJson(snapDir / "stats.json", allStats)

    # ── 報告 ──────────────────────────────────────────────
    log("▶ 產生報告…")
    reportMd = buildReport.build(runDate, allStats, errors)
    reportsDir = ROOT / "reports"
    reportsDir.mkdir(exist_ok=True)
    (reportsDir / f"report-{runDate}.md").write_text(reportMd, encoding="utf-8")
    (reportsDir / "latest.md").write_text(reportMd, encoding="utf-8")

    log("")
    log(f"✅ 完成。職缺 {jobResult['totalJobs']} 筆、新聞 {newsResult['totalArticles']} 篇、"
        f"失敗來源 {len(errors)} 個")
    log(f"   報告：reports/report-{runDate}.md（latest.md 同步更新）")
    log(f"   快照：data/raw/{runDate}/")


if __name__ == "__main__":
    main()
