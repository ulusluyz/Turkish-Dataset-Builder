import os
import json
from typing import Dict, Any

def generate_reports(
    final_dir: str,
    stats: Dict[str, Any],
    config: Dict[str, Any]
) -> None:
    """Generates dataset_report.json, quality_report.json, duplicate_report.json, dataset_report.html, and processing_log.txt."""
    reports_dir = os.path.join(final_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # Save dataset_report.json
    with open(os.path.join(reports_dir, "dataset_report.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    # Save quality_report.json
    quality_summary = {
        "accepted_documents": stats.get("accepted_documents", 0),
        "rejected_documents": stats.get("rejected_documents", 0),
        "too_short": stats.get("too_short", 0),
        "spam": stats.get("spam", 0),
        "non_turkish": stats.get("non_turkish", 0)
    }
    with open(os.path.join(reports_dir, "quality_report.json"), "w", encoding="utf-8") as f:
        json.dump(quality_summary, f, indent=2, ensure_ascii=False)

    # Save duplicate_report.json
    dup_summary = {
        "exact_duplicates": stats.get("exact_duplicates", 0),
        "near_duplicates": stats.get("near_duplicates", 0)
    }
    with open(os.path.join(reports_dir, "duplicate_report.json"), "w", encoding="utf-8") as f:
        json.dump(dup_summary, f, indent=2, ensure_ascii=False)

    # Save processing_log.txt
    with open(os.path.join(reports_dir, "processing_log.txt"), "w", encoding="utf-8") as f:
        f.write(f"Pipeline processing completed.\nStatus: {stats.get('status')}\nProcessed Docs: {stats.get('processed_documents')}\n")

    # Save HTML report
    report_html_path = os.path.join(reports_dir, "dataset_report.html")
    html_content = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>NEXT LLM Dataset Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; background: #f8f9fa; color: #212529; }}
        .card {{ background: white; padding: 24px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 24px; }}
        h1 {{ color: #0d6efd; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
        th {{ background: #e9ecef; }}
        .badge-success {{ color: #198754; font-weight: bold; }}
        .badge-danger {{ color: #dc3545; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>NEXT LLM Corpus Quality & Dataset Report</h1>
    <div class="card">
        <h2>Summary Statistics</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Discovered Files</td><td>{stats.get('discovered_files', 0)}</td></tr>
            <tr><td>Processed Documents</td><td>{stats.get('processed_documents', 0)}</td></tr>
            <tr><td>Accepted Documents</td><td class="badge-success">{stats.get('accepted_documents', 0)}</td></tr>
            <tr><td>Rejected Documents</td><td class="badge-danger">{stats.get('rejected_documents', 0)}</td></tr>
            <tr><td>Exact Duplicates Filtered</td><td>{stats.get('exact_duplicates', 0)}</td></tr>
            <tr><td>Near Duplicates Filtered</td><td>{stats.get('near_duplicates', 0)}</td></tr>
            <tr><td>Train Documents</td><td>{stats.get('train_documents', 0)}</td></tr>
            <tr><td>Validation Documents</td><td>{stats.get('validation_documents', 0)}</td></tr>
            <tr><td>Test Documents</td><td>{stats.get('test_documents', 0)}</td></tr>
        </table>
    </div>
</body>
</html>
"""
    with open(report_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Save README_DATASET.md
    readme_path = os.path.join(final_dir, "README_DATASET.md")
    readme_content = f"""# NEXT LLM Final Clean Corpus

## Dataset Summary
- **Discovered Files:** {stats.get('discovered_files', 0)}
- **Processed Documents:** {stats.get('processed_documents', 0)}
- **Accepted Documents:** {stats.get('accepted_documents', 0)}
- **Rejected Documents:** {stats.get('rejected_documents', 0)}
- **Train Documents:** {stats.get('train_documents', 0)}
- **Validation Documents:** {stats.get('validation_documents', 0)}
- **Test Documents:** {stats.get('test_documents', 0)}

## Shards & Manifest
Check `manifest/manifest.json` and `manifest/SHA256SUMS` for cryptographic integrity verification.
"""
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
