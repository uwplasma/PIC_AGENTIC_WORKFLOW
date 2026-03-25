from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Iterable

import numpy as np


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def to_serializable(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): to_serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_serializable(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def atomic_write_text(path: Path, text: str) -> None:
    ensure_directory(path.parent)
    with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(text)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(to_serializable(payload), indent=2, sort_keys=True) + "\n")


def replace_marked_section(text: str, marker_start: str, marker_end: str, section_lines: list[str]) -> str:
    start_index = text.find(marker_start)
    end_index = text.find(marker_end)
    if start_index == -1 or end_index == -1 or end_index < start_index:
        raise ValueError(f"Could not locate README markers '{marker_start}' and '{marker_end}'")
    start_index += len(marker_start)
    replacement = "\n\n" + "\n".join(section_lines).rstrip() + "\n\n"
    return text[:start_index] + replacement + text[end_index:]


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    ensure_directory(path.parent)
    with NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: to_serializable(row.get(key, "")) for key in fieldnames})
        temp_path = Path(handle.name)
    temp_path.replace(path)
