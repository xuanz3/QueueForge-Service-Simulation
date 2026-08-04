from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import tempfile
from typing import Any


class EngineExecutionError(RuntimeError):
    pass


def run_engine(
    *,
    engine_path: Path,
    scenario: dict[str, Any],
    seed: int,
    server_count: int,
) -> dict[str, Any]:
    run_input = deepcopy(scenario)
    run_input["simulation"]["seed"] = seed
    run_input["queue"]["serverCount"] = server_count

    with tempfile.TemporaryDirectory(prefix="queueforge-") as temp_dir:
        temp = Path(temp_dir)
        input_path = temp / "input.json"
        output_path = temp / "output.json"
        input_path.write_text(json.dumps(run_input, separators=(",", ":")), encoding="utf-8")

        completed = subprocess.run(
            [
                str(engine_path),
                "--input",
                str(input_path),
                "--output",
                str(output_path),
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )

        if completed.returncode != 0:
            raise EngineExecutionError(
                f"engine returned {completed.returncode}: {completed.stderr.strip()}"
            )

        try:
            result = json.loads(output_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise EngineExecutionError(f"engine output is not valid JSON: {error}") from error

    _validate_result(result, seed=seed)
    return result


def _validate_result(result: dict[str, Any], *, seed: int) -> None:
    if result.get("schemaVersion") != "1.0":
        raise EngineExecutionError("unexpected result schema version")
    if result.get("seed") != seed:
        raise EngineExecutionError("engine result seed does not match the requested seed")

    invariants = result.get("invariants", {})
    required = ["accountingBalanced", "chronologyValid", "utilisationWithinRange"]
    if not all(invariants.get(name) is True for name in required):
        raise EngineExecutionError(f"engine invariant failed: {invariants}")

    metrics = result.get("metrics")
    if not isinstance(metrics, dict):
        raise EngineExecutionError("engine result is missing metrics")
