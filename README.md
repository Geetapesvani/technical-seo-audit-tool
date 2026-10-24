# Technical SEO Audit Tool

A small, **working Python tool** that checks exported website page metadata and produces an actionable CSV of SEO issues. Useful for demonstrating an SEO automation workflow in a technical SEO portfolio.

**Scope:** This is a CSV-based audit, **not a website crawler**. It only reviews the fields you supply. It does not connect to Google Search Console, validate live page HTML, or check real-time indexation.

## Checks included

- HTTP status code (reported from the CSV)
- Missing or unusually short/long page titles
- Duplicate page titles (case-insensitive)
- Missing or unusually short/long meta descriptions
- Duplicate meta descriptions (case-insensitive)
- Missing H1
- Invalid canonical URL format (when a canonical is provided)
- Pages marked noindex or non-indexable, flagged for **review**, not automatically labeled errors
- Invalid page URL format

Title and description length thresholds are **editorial guidelines**, not Google ranking factors or hard Google limits. Search snippets can be rewritten or truncated dynamically.

## How to run

Requires **Python 3.9+**. No additional packages needed.

1. Download the repository and open a terminal inside its folder.
2. Run the sample audit:

```bash
python -m seo_audit.audit examples/pages.csv -o audit-results.csv
```

3. Open `audit-results.csv` in Excel or Google Sheets. Each row records the URL, issue, severity, and details.

### Input CSV columns

`url,status_code,title,meta_description,h1,canonical,indexability`

You can export or manually prepare an inventory from your crawler or spreadsheet. Keep all seven headers. Values may be blank where the audit should check for missing fields. Avoid sharing real client information without permission.

### Run automated tests

```bash
python -m unittest discover -s tests -v
```

## Example output

| url | issue | severity | detail |
| --- | --- | --- | --- |
| https://example.com/old-page | Non-200 status | High | HTTP 404 |
| https://example.com/old-page | Missing title | High | No title provided |

## Limitations

- A flagged length is a suggestion rather than a guarantee of SEO impact.
- Duplicate detection compares the supplied inventory only.
- Redirect chains, JavaScript rendering, actual robots directives, crawlability, and Google indexing require other tools.
- The example URLs belong to `example.com` and are placeholders, not real client data.

## Portfolio description

“Built a lightweight Python-based technical SEO audit utility that analyzes website inventory exports for metadata, status, H1, canonical formatting, and indexability review flags, then exports prioritized findings to CSV.”

## License

MIT. See [LICENSE](LICENSE).
