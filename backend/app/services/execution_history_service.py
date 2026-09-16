import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ExecutionHistoryService:
    def __init__(self):
        self.logs_directory = Path("backend/logs")
        self.logs_directory.mkdir(parents=True, exist_ok=True)

        self.history_path = self.logs_directory / "execution_history.jsonl"

    def record(self, entry: dict[str, Any]) -> None:
        self.logs_directory.mkdir(parents=True, exist_ok=True)

        with self.history_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(entry, default=str) + "\n")

    def get_history(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self.history_path.exists():
            return []

        entries = []

        with self.history_path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if line:
                    entries.append(json.loads(line))

        return entries[-limit:][::-1]

    def get_metrics(self) -> dict[str, Any]:
        history = self.get_history(limit=10000)

        total_runs = len(history)
        successful_runs = sum(
            1 for entry in history if entry.get("status") == "success"
        )
        failed_runs = total_runs - successful_runs

        execution_times = [
            entry["execution_time_ms"]
            for entry in history
            if entry.get("status") == "success"
            and isinstance(entry.get("execution_time_ms"), (int, float))
        ]

        average_execution_time_ms = (
            sum(execution_times) / len(execution_times)
            if execution_times
            else 0
        )

        return {
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "average_execution_time_ms": round(
                average_execution_time_ms,
                2,
            ),
        }


execution_history_service = ExecutionHistoryService()