"""Audit SEO metadata from an exported page inventory CSV.

Usage:
    python -m seo_audit.audit examples/pages.csv -o audit-results.csv

This tool audits *provided* page metadata. It does not crawl websites.
"""

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

REQUIRED_COLUMNS = ("url", "status_code", "title", "meta_description", "h1", "canonical", "indexability")
OUTPUT_COLUMNS = ("url", "issue", "severity", "detail")


def is_valid_url(value):
    parts = urlsplit(value.strip())
    return parts.scheme in ("http", "https") and bool(parts.netloc)


def check_row(row):
    """Return (issue, severity, detail) tuples for one CSV row."""
    issues = []
    url = row["url"].strip()
    title = row["title"].strip()
    desc = row["meta_description"].strip()
    h1 = row["h1"].strip()
    canonical = row["canonical"].strip()
    indexability = row["indexability"].strip().lower()
    status_raw = row["status_code"].strip()

    if not is_valid_url(url):
        issues.append(("Invalid URL", "High", "Expected an absolute HTTP(S) URL"))
    try:
        status = int(status_raw)
        if status != 200:
            issues.append(("Non-200 status", "High", f"HTTP {status}"))
    except ValueError:
        issues.append(("Invalid status code", "High", f"Received: {status_raw!r}"))

    # Metadata warnings apply to HTML inventory rows supplied in the CSV.
    if not title:
        issues.append(("Missing title", "High", "No title provided"))
    elif len(title) < 30 or len(title) > 60:
        issues.append(("Title length", "Medium", f"{len(title)} characters (guide: 30-60)"))
    if not desc:
        issues.append(("Missing meta description", "Medium", "No description provided"))
    elif len(desc) < 120 or len(desc) > 160:
        issues.append(("Description length", "Low", f"{len(desc)} characters (guide: 120-160)"))
    if not h1:
        issues.append(("Missing H1", "Medium", "No H1 provided"))
    if canonical and not is_valid_url(canonical):
        issues.append(("Invalid canonical", "High", "Canonical must be an absolute HTTP(S) URL"))
    if indexability in ("noindex", "non-indexable", "non-indexable (noindex)"):
        issues.append(("Page marked non-indexable", "Review", "Check whether intentional"))
    return issues


def audit(rows):
    """Return issue rows including duplicate metadata findings."""
    materialized = list(rows)
    counts = {
        field: Counter(r[field].strip().casefold() for r in materialized if r[field].strip())
        for field in ("title", "meta_description")
    }
    findings = []
    for row in materialized:
        url = row["url"].strip()
        for issue, severity, detail in check_row(row):
            findings.append(dict(url=url, issue=issue, severity=severity, detail=detail))
        for field, issue in (("title", "Duplicate title"), ("meta_description", "Duplicate meta description")):
            value = row[field].strip()
            if value and counts[field][value.casefold()] > 1:
                findings.append(dict(url=url, issue=issue, severity="Medium", detail=f"Shared by {counts[field][value.casefold()]} rows"))
    return findings


def run(input_path, output_path):
    with open(input_path, encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None:
            raise ValueError("Input CSV is empty")
        missing = [field for field in REQUIRED_COLUMNS if field not in reader.fieldnames]
        if missing:
            raise ValueError("Missing columns: " + ", ".join(missing))
        rows = list(reader)
    results = audit(rows)
    with open(output_path, "w", encoding="utf-8", newline="") as dest:
        writer = csv.DictWriter(dest, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(results)
    return len(rows), len(results)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Audit SEO metadata in a page inventory CSV")
    parser.add_argument("input", type=Path, help="Input CSV with the documented columns")
    parser.add_argument("-o", "--output", type=Path, default=Path("audit-results.csv"), help="Output issues CSV")
    args = parser.parse_args(argv)
    try:
        pages, issues = run(args.input, args.output)
    except (OSError, ValueError, csv.Error) as exc:
        parser.error(str(exc))
    print(f"Audited {pages} pages; found {issues} issues. Saved to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
