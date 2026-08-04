from __future__ import annotations

import csv
from html import escape
import json
from pathlib import Path
from typing import Any


def write_reports(report: dict[str, Any], output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "staffing-comparison.json"
    variants_path = output_dir / "staffing-summary.csv"
    runs_path = output_dir / "run-level-results.csv"
    html_path = output_dir / "staffing-report.html"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_variant_csv(report, variants_path)
    _write_runs_csv(report, runs_path)
    html_path.write_text(_render_html(report), encoding="utf-8")

    return {
        "json": json_path,
        "variantCsv": variants_path,
        "runCsv": runs_path,
        "html": html_path,
    }


def _write_variant_csv(report: dict[str, Any], path: Path) -> None:
    fields = [
        "serverCount",
        "runCount",
        "successRate",
        "meanP95WaitMinutes",
        "p95WaitCiLow",
        "p95WaitCiHigh",
        "meanMaximumQueueLength",
        "meanUtilisation",
        "utilisationCiLow",
        "utilisationCiHigh",
        "arrivalMeanWithinReferenceTolerance",
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for variant in report["variants"]:
            wait = variant["metrics"]["p95WaitMinutes"]
            queue = variant["metrics"]["maximumQueueLength"]
            utilisation = variant["metrics"]["overallUtilisation"]
            writer.writerow(
                {
                    "serverCount": variant["serverCount"],
                    "runCount": variant["runCount"],
                    "successRate": variant["successRate"],
                    "meanP95WaitMinutes": wait["mean"],
                    "p95WaitCiLow": wait["confidence_interval_95_low"],
                    "p95WaitCiHigh": wait["confidence_interval_95_high"],
                    "meanMaximumQueueLength": queue["mean"],
                    "meanUtilisation": utilisation["mean"],
                    "utilisationCiLow": utilisation["confidence_interval_95_low"],
                    "utilisationCiHigh": utilisation["confidence_interval_95_high"],
                    "arrivalMeanWithinReferenceTolerance": variant[
                        "arrivalMeanWithinReferenceTolerance"
                    ],
                }
            )


def _write_runs_csv(report: dict[str, Any], path: Path) -> None:
    records = report["runs"]
    if not records:
        raise ValueError("report contains no run records")
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def _render_html(report: dict[str, Any]) -> str:
    rows = []
    for variant in report["variants"]:
        wait = variant["metrics"]["p95WaitMinutes"]
        queue = variant["metrics"]["maximumQueueLength"]
        utilisation = variant["metrics"]["overallUtilisation"]
        rows.append(
            "<tr>"
            f"<td>{variant['serverCount']}</td>"
            f"<td>{variant['successRate']:.1%}</td>"
            f"<td>{wait['mean']:.2f}</td>"
            f"<td>{wait['confidence_interval_95_low']:.2f}–"
            f"{wait['confidence_interval_95_high']:.2f}</td>"
            f"<td>{queue['mean']:.2f}</td>"
            f"<td>{utilisation['mean']:.1%}</td>"
            f"<td>{'Yes' if variant['meetsRequiredSuccessRate'] else 'No'}</td>"
            "</tr>"
        )

    recommendation = report["recommendation"]
    selected = (
        str(recommendation["serverCount"])
        if recommendation["serverCount"] is not None
        else "None"
    )
    limitations = "".join(
        f"<li>{escape(item)}</li>" for item in report["limitations"]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>QueueForge Staffing Comparison</title>
<style>
:root {{ color-scheme: light; font-family: Inter, system-ui, sans-serif; }}
body {{ margin: 0; background: #f4f6f8; color: #17202a; }}
main {{ width: min(1080px, calc(100% - 40px)); margin: 48px auto; }}
header, section {{ background: white; border: 1px solid #dfe4ea; border-radius: 14px; padding: 28px; margin-bottom: 18px; }}
.eyebrow {{ text-transform: uppercase; letter-spacing: .12em; font-size: 12px; color: #506579; font-weight: 700; }}
h1 {{ margin: 8px 0 12px; font-size: 42px; }}
.notice {{ border-left: 4px solid #2b6f8e; padding-left: 16px; color: #455565; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ text-align: right; padding: 12px 10px; border-bottom: 1px solid #e7ebef; }}
th:first-child, td:first-child {{ text-align: left; }}
strong.metric {{ font-size: 34px; display: block; margin-top: 6px; }}
small {{ color: #687786; }}
</style>
</head>
<body>
<main>
<header>
<p class="eyebrow">Fictional service-centre experiment</p>
<h1>QueueForge staffing comparison</h1>
<p class="notice">This report is generated from synthetic assumptions and is not operational staffing advice.</p>
</header>
<section>
<p class="eyebrow">Decision output</p>
<strong class="metric">{escape(selected)} servers</strong>
<p>{escape(recommendation['statement'])}</p>
<small>Status: {escape(recommendation['status'])}</small>
</section>
<section>
<h2>Variant evidence</h2>
<table>
<thead><tr><th>Servers</th><th>Success rate</th><th>Mean run P95 wait</th><th>95% CI</th><th>Mean max queue</th><th>Mean utilisation</th><th>Target met</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
</section>
<section>
<h2>Limitations</h2>
<ul>{limitations}</ul>
</section>
</main>
</body>
</html>
"""
