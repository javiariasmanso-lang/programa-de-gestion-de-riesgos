"""Export report data to JSON or CSV."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List


def _flatten_for_csv(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    rows = []
    def _add(prefix: str, obj: Any):
        if isinstance(obj, dict):
            for key, value in obj.items():
                _add(f"{prefix}{key}." if prefix else f"{key}.", value)
        elif isinstance(obj, list):
            for idx, value in enumerate(obj, start=1):
                _add(f"{prefix}{idx}.", value)
        else:
            rows.append({"metric": prefix[:-1] if prefix.endswith(".") else prefix, "value": str(obj)})
    _add("", payload)
    return rows


def export_payload(
    payload: Dict[str, Any], output_format: str, output_path: Path
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "json":
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    elif output_format == "csv":
        rows = _flatten_for_csv(payload)
        with output_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["metric", "value"])
            writer.writeheader()
            writer.writerows(rows)
    else:
        raise ValueError("Formato de salida no soportado.")
    return output_path
