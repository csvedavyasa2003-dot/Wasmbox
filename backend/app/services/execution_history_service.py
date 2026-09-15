import json
from pathlib import Path
from threading import Lock
from typing import Any


class ExecutionHistoryService:
    def __init__(self) -> None:
        self.history_path = (
            Path(__file__).resolve().parents[2] / "logs" / "execution_history.jsonl"
        )
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def record(self, entry: dict[str, Any]) -> None:
        with self._lock:
            with self.history_path.open("a", encoding="utf-8") as file:
                file.write(json.dumps(entry) + "\n")

    def get_history(self) -> list[dict[str, Any]]:
        if not self.history_path.exists():
            return []

        records = []
        with self.history_path.open("r", encoding="utf-8") as file:
            for line in file:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        return records

    def get_metrics(self) -> dict[str, Any]:
        records = self.get_history()
        successful = [
            record
            for record in records
            if record.get("status") == "success"
        ]

        execution_times = [
            record["execution_time_ms"]
            for record in successful
            if isinstance(record.get("execution_time_ms"), (int, float))
        ]

        return {
            "total_runs": len(records),
            "successful_runs": len(successful),
            "failed_runs": len(records) - len(successful),
            "average_execution_time_ms": round(
                sum(execution_times) / len(execution_times),
                2,
            ) if execution_times else 0,
        }


execution_history_service = ExecutionHistoryService()
