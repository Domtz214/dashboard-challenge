"""Check organizer release evidence. Run verify_data.py separately first."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def check(root=ROOT):
    manifest_path = root / "data/manifest.json"
    manifest = json.loads(manifest_path.read_text())
    release = json.loads((root / "reference/release.json").read_text())
    errors = []
    if not re.fullmatch(r"[1-9]\d*\.\d+\.\d+", manifest["version"]):
        errors.append("Dataset version must be a final semantic version after calibration approval.")

    def evidence(path):
        if not isinstance(path, str) or not path:
            return False
        resolved = (root / path).resolve()
        return (resolved.is_relative_to(root.resolve()) and resolved.is_file()
                and resolved.stat().st_size > 0)

    calibration = release["calibration"]
    if not calibration.get("approved_by") or not evidence(calibration.get("report_path")):
        errors.append("Record calibration approver and a report with targets, results and acceptance rationale.")
    digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    if calibration.get("manifest_sha256") != digest:
        errors.append("Calibration approval must bind to the exact final manifest SHA-256.")
    # Derive required publishers from shipped tables, rather than trusting config keys.
    required = set()
    for entry in manifest["files"]:
        path = entry["path"]
        if not path.startswith("4_context/real_sources/"):
            continue
        table = Path(path).name
        if table.startswith(("city_visitation_", "visitor_profile_")):
            required.add("LVCVA")
        elif table.startswith("benchmark_"):
            required.add("Missouri Gaming Commission")
        elif table.startswith("weather_"):
            required.add("NOAA")
        else:
            errors.append(f"Unrecognized third-party table needs a publisher review: {path}")
    for publisher in sorted(required):
        permission = release["source_permissions"].get(publisher, {})
        if not evidence(permission.get("evidence_path")):
            errors.append(f"Record redistribution terms or permission evidence for {publisher}.")
    if not evidence("LICENSE"):
        errors.append("Original project distribution license is missing.")
    return errors


if __name__ == "__main__":
    failures = check()
    for failure in failures:
        print(f"BLOCKED: {failure}")
    if failures:
        sys.exit(1)
    print("PASS: release evidence is present; organizers must review its substance before publication.")
