"""Generate all synthetic readiness scenarios on Windows, macOS, or Linux."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = {
    "no-go": "NO-GO",
    "review": "REVIEW",
    "go": "GO",
}


def main():
    for name, expected in SCENARIOS.items():
        html_path = f"reports/scenarios/{name}.html"
        report_path = f"reports/scenarios/{name}.md"
        command = [
            sys.executable,
            "src/vcf_dashboard.py",
            "--status", f"data/scenarios/{name}.csv",
            "--html", html_path,
            "--report", report_path,
        ]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        print(result.stdout, end="")
        if result.returncode != 0:
            print(result.stderr, file=sys.stderr, end="")
            raise SystemExit(result.returncode)
        if f"Planning decision: {expected} " not in result.stdout:
            raise SystemExit(
                f"Scenario {name!r} did not produce expected decision {expected!r}. "
                f"Output was: {result.stdout.strip()}"
            )
    print("Generated NO-GO, REVIEW, and GO examples. Synthetic evidence only; not live VCF validation.")


if __name__ == "__main__":
    main()
