"""Build a standalone planning dashboard from a checklist and its status file.

This tool assesses evidence tracking only. It does not query or validate VMware systems.
"""
import argparse
import csv
import html
from collections import Counter, defaultdict
from pathlib import Path

VALID_STATUSES = {"Not Started", "In Progress", "Complete", "Not Applicable", "Blocked"}
YES_VALUES = {"yes", "true", "1"}


def read_csv(path, required_columns):
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"File not found: {path}")
    try:
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise ValueError(f"CSV has no header: {path}")
            missing = set(required_columns) - set(reader.fieldnames)
            if missing:
                raise ValueError(f"CSV {path} is missing columns: {', '.join(sorted(missing))}")
            return list(reader)
    except OSError as exc:
        raise ValueError(f"Could not read {path}: {exc}") from exc


def load_checklist(checklist_path, status_path):
    checks = read_csv(checklist_path, ["phase", "check_id", "check", "required_evidence", "blocking_if_missing"])
    statuses = read_csv(status_path, ["check_id", "status", "evidence_reference", "completion_notes"])
    status_by_id = {}
    for item in statuses:
        check_id = (item.get("check_id") or "").strip()
        if not check_id:
            raise ValueError("Status CSV contains a row with an empty check_id")
        if check_id in status_by_id:
            raise ValueError(f"Duplicate status check_id: {check_id}")
        status = (item.get("status") or "").strip()
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{status}' for {check_id}; use: {', '.join(sorted(VALID_STATUSES))}")
        status_by_id[check_id] = item

    checklist_ids = [((c.get("check_id") or "").strip()) for c in checks]
    if any(not check_id for check_id in checklist_ids):
        raise ValueError("Checklist contains a row with an empty check_id")
    if len(set(checklist_ids)) != len(checklist_ids):
        raise ValueError("Checklist contains duplicate check_id values")
    extra_ids = set(status_by_id) - set(checklist_ids)
    if extra_ids:
        raise ValueError(f"Status CSV contains unknown check_id values: {', '.join(sorted(extra_ids))}")

    merged = []
    for check in checks:
        check_id = check["check_id"].strip()
        state = status_by_id.get(check_id, {})
        row = {**check, **state}
        row["check_id"] = check_id
        row["status"] = (state.get("status") or "Not Started").strip()
        row["evidence_reference"] = (state.get("evidence_reference") or "").strip()
        row["completion_notes"] = (state.get("completion_notes") or "").strip()
        row["blocking"] = (check.get("blocking_if_missing") or "").strip().lower() in YES_VALUES
        row["evidence_present"] = bool(row["evidence_reference"])
        merged.append(row)
    return merged


def summarize(rows):
    counts = Counter(row["status"] for row in rows)
    blockers = [r for r in rows if r["blocking"] and (r["status"] in {"Not Started", "Blocked"} or (r["status"] == "Complete" and not bool(r.get("evidence_reference"))))]
    needs_review = [r for r in rows if r["status"] == "In Progress" or (r["status"] == "Complete" and not bool(r.get("evidence_reference"))) or (r["status"] == "Not Applicable" and not r["completion_notes"])]
    # A GO is deliberately strict: every check is Complete with evidence, or N/A with rationale.
    all_resolved = all((r["status"] == "Complete" and bool(r.get("evidence_reference"))) or (r["status"] == "Not Applicable" and bool(r["completion_notes"])) for r in rows)
    if blockers:
        decision = "NO-GO"
    elif all_resolved:
        decision = "GO"
    else:
        decision = "REVIEW"
    return {
        "total": len(rows),
        "counts": {status: counts.get(status, 0) for status in sorted(VALID_STATUSES)},
        "blockers": blockers,
        "needs_review": needs_review,
        "decision": decision,
        "completed_with_evidence": sum(r["status"] == "Complete" and bool(r.get("evidence_reference")) for r in rows),
        "evidence_gaps": [r for r in rows if not bool(r.get("evidence_reference")) and r["status"] != "Not Applicable"],
    }


def _cell(value):
    return html.escape(str(value or ""), quote=True)


def build_markdown(rows, summary):
    lines = [
        "# VCF Lifecycle Readiness Dashboard Report", "",
        "> **Synthetic portfolio example.** This report tracks supplied planning evidence only. It does not validate live VCF health, compatibility, supported upgrade paths, or upgrade eligibility.", "",
        f"- **Planning decision:** {summary['decision']}",
        f"- **Checks in checklist:** {summary['total']}",
        f"- **Complete with evidence:** {summary['completed_with_evidence']}",
        f"- **Blocking items:** {len(summary['blockers'])}",
        f"- **Items requiring review:** {len(summary['needs_review'])}", "",
        "## Status counts", "", "| Status | Count |", "|---|---:|"
    ]
    for status, count in summary["counts"].items():
        lines.append(f"| {status} | {count} |")
    lines += ["", "## Checklist details", "", "| Phase | ID | Check | Blocking if missing | Status | Evidence reference | Notes |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        vals = [r.get("phase"), r.get("check_id"), r.get("check"), "Yes" if r["blocking"] else "No", r.get("status"), r.get("evidence_reference") or "MISSING", r.get("completion_notes")]
        lines.append("| " + " | ".join(str(v or "").replace("|", "\\|").replace("\n", " ") for v in vals) + " |")
    lines += ["", "## Decision rules", "", "- **NO-GO:** at least one blocking check is Not Started or Blocked, or marked Complete without an evidence reference.", "- **GO:** every check is Complete with an evidence reference, or Not Applicable with a written rationale.", "- **REVIEW:** no blocking condition above, but some work is in progress, incomplete, or lacks adequate evidence.", "", "## Important limitation", "", "A GO means the evidence-tracking rules were satisfied in this checklist only. It is not authorization to upgrade and is not proof of VCF compatibility or infrastructure health. Verify current, release-specific Broadcom guidance and perform supported technical prechecks before any real change.", ""]
    return "\n".join(lines)


def build_html(rows, summary, markdown_report):
    data_rows = []
    for r in rows:
        data_rows.append({k: r.get(k, "") for k in ("phase", "check_id", "check", "required_evidence", "status", "evidence_reference", "completion_notes", "blocking")})
    payload = __import__("json").dumps(data_rows, ensure_ascii=False).replace("</", "<\\/")
    counts = summary["counts"]
    metrics = [
        ("Total checks", summary["total"]),
        ("Complete + evidence", summary["completed_with_evidence"]),
        ("Blocking items", len(summary["blockers"])),
        ("Needs review", len(summary["needs_review"])),
    ]
    cards = "".join(f'<div class="metric"><span>{_cell(label)}</span><strong>{value}</strong></div>' for label, value in metrics)
    decision_class = summary["decision"].lower().replace("-", "")
    markdown_json = __import__("json").dumps(markdown_report, ensure_ascii=False).replace("</", "<\\/")
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>VCF Lifecycle Readiness Dashboard</title>
<style>
:root{{font-family:Inter,Segoe UI,Arial,sans-serif;color:#182230;background:#f4f7fb}}*{{box-sizing:border-box}}body{{margin:0}}header{{background:#12243a;color:white;padding:28px clamp(18px,4vw,52px)}}header p{{color:#d3dfed;max-width:900px;line-height:1.5}}main{{max-width:1400px;margin:auto;padding:24px clamp(12px,3vw,36px) 48px}}.banner{{border:1px solid #d7e0eb;background:white;padding:16px 18px;border-radius:12px;margin-bottom:18px;line-height:1.5}}.decision{{display:inline-block;padding:7px 12px;border-radius:8px;font-weight:800;letter-spacing:.04em;background:#fce7e7;color:#8b1e1e}}.decision.go{{background:#dcfce7;color:#166534}}.decision.review{{background:#fef3c7;color:#92400e}}.metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:18px 0}}.metric{{background:white;border:1px solid #dbe3ed;border-radius:12px;padding:18px}}.metric span{{display:block;color:#536276;font-size:13px}}.metric strong{{display:block;font-size:30px;margin-top:8px}}.toolbar{{display:flex;gap:10px;flex-wrap:wrap;margin:16px 0}}input,select,button{{font:inherit;padding:10px 12px;border:1px solid #c8d3e0;border-radius:8px;background:white}}input{{min-width:230px;flex:1}}button{{cursor:pointer;background:#173b63;color:white;border-color:#173b63}}.table-wrap{{overflow:auto;background:white;border:1px solid #dbe3ed;border-radius:12px}}table{{width:100%;border-collapse:collapse;min-width:950px}}th,td{{text-align:left;padding:12px;border-bottom:1px solid #e7edf4;vertical-align:top;font-size:13px}}th{{background:#edf3f9;position:sticky;top:0}}.pill{{display:inline-block;padding:4px 8px;border-radius:99px;font-size:12px;font-weight:700;background:#e5e7eb}}.pill.complete{{background:#dcfce7;color:#166534}}.pill.blocked,.pill.notstarted{{background:#fee2e2;color:#991b1b}}.pill.inprogress{{background:#fef3c7;color:#92400e}}.pill.notapplicable{{background:#e0e7ff;color:#3730a3}}.foot{{color:#596779;font-size:13px;line-height:1.6;margin-top:18px}}@media(max-width:760px){{.metrics{{grid-template-columns:repeat(2,minmax(0,1fr))}}header{{padding:22px 18px}}}}@media(max-width:400px){{.metrics{{grid-template-columns:1fr 1fr}}.metric strong{{font-size:24px}}}}
</style></head><body>
<header><h1>VCF Lifecycle Readiness Dashboard</h1><p>Checklist-driven planning evidence tracker · VCF 9.x planning context · Synthetic portfolio data only</p></header>
<main><div class="banner"><strong>Planning decision</strong> <span class="decision {decision_class}">{_cell(summary['decision'])}</span><p>This is a decision about checklist evidence only—not a live VCF compatibility, health, or upgrade-readiness result.</p></div>
<section class="metrics">{cards}</section>
<div class="toolbar"><input id="search" type="search" placeholder="Search checks, evidence, notes…" aria-label="Search checklist"><select id="phase"><option value="">All phases</option></select><select id="status"><option value="">All statuses</option></select><button id="download">Download Markdown report</button></div>
<div class="table-wrap"><table><thead><tr><th>Phase</th><th>Check ID</th><th>Readiness check</th><th>Status</th><th>Blocking?</th><th>Evidence reference</th><th>Notes</th></tr></thead><tbody id="rows"></tbody></table></div>
<p class="foot"><strong>Decision rules:</strong> NO-GO if a blocking check is Not Started or Blocked, or marked Complete without an evidence reference. GO only if every check is Complete with evidence or Not Applicable with a written rationale. Otherwise REVIEW. Confirm current release-specific Broadcom guidance and perform technical prechecks before any real change.</p></main>
<script>
const checks={payload}; const report={markdown_json};
const tbody=document.getElementById('rows'), search=document.getElementById('search'), phase=document.getElementById('phase'), status=document.getElementById('status');
const unique=(key)=>[...new Set(checks.map(x=>x[key]).filter(Boolean))].sort();
unique('phase').forEach(v=>phase.add(new Option(v,v))); unique('status').forEach(v=>status.add(new Option(v,v)));
function cls(s){{return s.toLowerCase().replace(/[^a-z]/g,'')}}
function render(){{const q=search.value.toLowerCase(); const list=checks.filter(r=>(!phase.value||r.phase===phase.value)&&(!status.value||r.status===status.value)&&Object.values(r).join(' ').toLowerCase().includes(q));tbody.innerHTML=list.map(r=>`<tr><td>${{esc(r.phase)}}</td><td>${{esc(r.check_id)}}</td><td><strong>${{esc(r.check)}}</strong><br><small>Evidence expected: ${{esc(r.required_evidence)}}</small></td><td><span class="pill ${{cls(r.status||'Not Started')}}">${{esc(r.status||'Not Started')}}</span></td><td>${{String(r.blocking)==='true'?'Yes':'No'}}</td><td>${{esc(r.evidence_reference||'MISSING')}}</td><td>${{esc(r.completion_notes||'')}}</td></tr>`).join('');}}
function esc(s){{return String(s??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]))}}
[search,phase,status].forEach(el=>el.addEventListener('input',render));document.getElementById('download').addEventListener('click',()=>{{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([report],{{type:'text/markdown;charset=utf-8'}}));a.download='vcf-readiness-dashboard-report.md';a.click();URL.revokeObjectURL(a.href)}});render();
</script></body></html>'''


def main():
    parser = argparse.ArgumentParser(description="Generate a standalone VCF planning-readiness dashboard and Markdown report.")
    parser.add_argument("--checklist", default="docs/vcf9-readiness-checklist.csv", help="Checklist definition CSV")
    parser.add_argument("--status", default="data/checklist_status.csv", help="Per-check status/evidence CSV")
    parser.add_argument("--html", default="reports/readiness-dashboard.html", help="Output standalone HTML dashboard")
    parser.add_argument("--report", default="reports/readiness-dashboard-report.md", help="Output Markdown report")
    args = parser.parse_args()
    try:
        rows = load_checklist(args.checklist, args.status)
    except ValueError as exc:
        parser.error(str(exc))
    summary = summarize(rows)
    report = build_markdown(rows, summary)
    dashboard = build_html(rows, summary, report)
    for path, content in ((args.html, dashboard), (args.report, report)):
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
        print(f"Wrote {output}")
    print(f"Planning decision: {summary['decision']} (evidence tracking only; not a live VCF validation).")

if __name__ == "__main__":
    main()
