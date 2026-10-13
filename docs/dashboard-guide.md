# Checklist Dashboard Guide

## Purpose

`src/vcf_dashboard.py` merges the checklist definition in `docs/vcf9-readiness-checklist.csv` with the progress/evidence state in `data/checklist_status.csv`. It writes a standalone HTML dashboard and a Markdown report. It uses Python's standard library only.

## Run

From the repository root:

```powershell
python src/vcf_dashboard.py
```

Optional paths:

```powershell
python src/vcf_dashboard.py `
  --checklist docs/vcf9-readiness-checklist.csv `
  --status data/checklist_status.csv `
  --html reports/readiness-dashboard.html `
  --report reports/readiness-dashboard-report.md
```

Open `reports/readiness-dashboard.html` in a browser. The page is self-contained and supports searching, phase/status filters, and downloading the Markdown report.

## Status file

`data/checklist_status.csv` requires these columns:

- `check_id`: must match a checklist ID exactly.
- `status`: `Not Started`, `In Progress`, `Complete`, `Not Applicable`, or `Blocked`.
- `evidence_reference`: a sanitized record/reference identifier, not a secret or restricted document.
- `completion_notes`: rationale or a short note. `Not Applicable` requires a written rationale for the dashboard to consider that check resolved.

Unknown IDs, duplicate IDs, missing required columns, and invalid status values cause a clear validation error. Checklist IDs without a status row are treated as `Not Started`.

## Decision semantics

- **NO-GO:** any blocking check is `Not Started` or `Blocked`, or is marked `Complete` without an evidence reference.
- **GO:** every check is `Complete` with an evidence reference, or `Not Applicable` with a written rationale.
- **REVIEW:** remaining work exists but no blocking condition above is detected.

These labels describe evidence-tracking rules only. `GO` is not a vendor-supported upgrade-path determination, live health result, compatibility check, or authorization to execute a change. Use current release-specific vendor guidance and supported technical prechecks before real operations.

## Sample data warning

The included status file intentionally contains incomplete items and fictional evidence IDs; the expected sample decision is `NO-GO`. Replace the sample state with approved, sanitized project evidence only when using the toolkit for a real planning workflow. Never commit sensitive production details to a public repository.
