"""Verify Dashboard Royale downloads and CSV/Parquet parity. Requires duckdb."""
import hashlib
import json
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def main():
    manifest = json.loads((DATA / "manifest.json").read_text())
    listed = {entry["path"] for entry in manifest["files"]}
    actual = {str(path.relative_to(DATA)) for path in DATA.rglob("*")
              if path.suffix in {".gz", ".parquet"}}
    assert listed == actual, "Manifest and data file list differ"
    con = duckdb.connect()
    tables = 0
    for entry in manifest["files"]:
        path = DATA / entry["path"]
        assert path.stat().st_size == entry["bytes"], f"Size mismatch: {path}"
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        assert digest == entry["sha256"], f"Checksum mismatch: {path}"
        if path.suffix != ".parquet":
            continue
        parquet = con.read_parquet(str(path))
        assert parquet.count("*").fetchall()[0][0] == entry["rows"], f"Row count: {path}"
        csv = con.read_csv(str(path.with_suffix(".csv.gz")),
                           columns=dict(zip(parquet.columns, map(str, parquet.types))),
                           header=True)
        parquet.create_view("parquet_rows", replace=True)
        csv.create_view("csv_rows", replace=True)
        for left, right in [("parquet_rows", "csv_rows"), ("csv_rows", "parquet_rows")]:
            difference = con.sql(f"(SELECT * FROM {left} EXCEPT ALL SELECT * FROM {right}) LIMIT 1")
            assert difference.fetchall() == [], f"Format mismatch: {path}"
        assert csv.count("*").fetchall()[0][0] == entry["rows"], f"CSV row count: {path}"
        tables += 1
    print(f"PASS: {len(listed)} checksums and sizes; {tables} row counts and format comparisons")


if __name__ == "__main__":
    main()
