import argparse, json
from pathlib import Path

EVIDENCE = {
    "owner": "Assigned owner",
    "maintenance_window": "Maintenance window",
    "backup_evidence": "Backup / recovery evidence",
    "health_check_evidence": "Pre-change health-check evidence",
    "compatibility_reference": "Compatibility / release reference",
    "rollback_plan": "Rollback / recovery plan",
    "change_approval": "Change approval status",
}

def load_inventory(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Inventory root must be an object")
    for key, expected in (("environment", dict), ("components", list), ("change_records", list)):
        if key not in data or not isinstance(data[key], expected):
            raise ValueError(f"Missing or invalid top-level field: {key}")
    return data

def assess_change(change):
    missing = [label for key, label in EVIDENCE.items() if not str(change.get(key, "")).strip()]
    if not str(change.get("owner", "")).strip() or not str(change.get("rollback_plan", "")).strip():
        status = "BLOCKED"
    elif missing or str(change.get("change_approval", "")).lower() not in ("approved", "approved with conditions"):
        status = "REVIEW"
    else:
        status = "READY"
    return {"status": status, "missing_evidence": missing}

def build_report(data):
    env = data["environment"]
    out = [
        f"# Lifecycle Readiness Report — {env.get('name', 'Unnamed environment')}", "",
        "> **Synthetic portfolio lab.** Checks planning evidence only; does not validate real VCF compatibility or execute changes.", "",
        "## Environment summary", "",
        f"- **Type:** {env.get('environment_type', 'Not supplied')}",
        f"- **VCF release:** {env.get('vcf_release', 'Not supplied')}",
        f"- **Data classification:** {env.get('data_classification', 'Not supplied')}",
        f"- **Components:** {len(data['components'])}",
        f"- **Change records:** {len(data['change_records'])}", "",
        "## Component inventory", "",
        "| Component | Role | Version | Owner |", "|---|---|---|---|"
    ]
    for c in data["components"]:
        vals = [str(c.get(k, "Not supplied")).replace("|", "\\|") for k in ("name", "role", "version", "owner")]
        out.append("| " + " | ".join(vals) + " |")
    out += ["", "## Change readiness", ""]
    statuses = []
    for c in data["change_records"]:
        result = assess_change(c); statuses.append(result["status"])
        out += [f"### {c.get('id', 'Missing ID')} — {c.get('title', 'Untitled')}", "",
                f"- **Target:** {c.get('target', 'Not supplied')}",
                f"- **Status:** **{result['status']}**",
                f"- **Owner:** {c.get('owner') or 'MISSING'}",
                f"- **Maintenance window:** {c.get('maintenance_window') or 'MISSING'}",
                f"- **Approval:** {c.get('change_approval') or 'MISSING'}"]
        out.append("- **Evidence gaps:** " + ("; ".join(result["missing_evidence"]) if result["missing_evidence"] else "None detected by basic rules.") )
        out.append("")
    overall = "BLOCKED" if "BLOCKED" in statuses else "REVIEW" if "REVIEW" in statuses or not statuses else "READY"
    out += ["## Overall planning status", "", f"**{overall}**", "",
            "## Before any real change", "",
            "1. Confirm exact deployed VCF and component versions.",
            "2. Validate upgrade path and interoperability using current official Broadcom documentation.",
            "3. Confirm health, backups, capacity, maintenance window, dependencies, and recovery procedures.",
            "4. Obtain required change approvals.",
            "5. Use only the supported workflow for the deployed release.", "",
            "## Limitations", "",
            "- Status is planning-evidence completeness, not proof of technical readiness.",
            "- No connection is made to SDDC Manager, vCenter, NSX, ESXi, or production systems.",
            "- Example versions and evidence must never authorize a real change.", ""]
    return "\n".join(out)

def main():
    parser = argparse.ArgumentParser(description="Generate a VCF lifecycle planning evidence report.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        report = build_report(load_inventory(args.input))
    except ValueError as exc:
        parser.error(str(exc))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(report, encoding="utf-8")
    print(f"Report written to {args.output} (planning evidence only; not a compatibility check).")

if __name__ == "__main__":
    main()
