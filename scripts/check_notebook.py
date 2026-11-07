"""Execute the course notebook in a fresh IPython process and save evidence.

Run with the project's Python environment. This checks notebook code and data,
not the Cursor interface or a running Dagster web server.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notebook", type=Path, default=ROOT / "ETL_Course_Lab_HE.ipynb")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "notebook-ci-output")
    parser.add_argument("--require-python", default="3.13.12")
    args = parser.parse_args()
    source = args.notebook.resolve()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)

    # These settings apply before notebook imports and to all child commands.
    os.environ.update({
        "DBT_SEND_ANONYMOUS_USAGE_STATS": "false",
        "HF_HUB_DISABLE_TELEMETRY": "1",
        "PYTHONUTF8": "1",
        "PYTHONIOENCODING": "utf-8",
        "TOKENIZERS_PARALLELISM": "false",
        "GITHUB_OFFLINE": "1",
        "FAKE_EMBEDDINGS": "0",
    })
    import nbformat
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.utils.capture import capture_output

    original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    notebook = nbformat.read(source, as_version=4)
    nbformat.validate(notebook)
    executed_path = output / f"{source.stem}.executed.ipynb"
    if executed_path == source:
        raise ValueError("The output notebook must differ from the input notebook.")
    notebook.metadata.setdefault("etl_lab", {}).pop("validation", None)
    for cell in notebook.cells:
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None
            cell.metadata.pop("etl_validation_seconds", None)

    os.chdir(ROOT)
    shell = InteractiveShell.instance()
    started = time.perf_counter()
    total_cells = sum(cell.cell_type == "code" for cell in notebook.cells)
    attempted = passed = 0
    cell_results = []
    error = None
    official_result = None
    try:
        if platform.python_version() != args.require_python:
            raise RuntimeError(
                f"Expected Python {args.require_python}; got {platform.python_version()} "
                f"from {sys.executable}"
            )
        for index, cell in enumerate(notebook.cells):
            if cell.cell_type != "code":
                continue
            attempted += 1
            cell.execution_count = attempted
            tick = time.perf_counter()
            with capture_output(stdout=True, stderr=True, display=True) as captured:
                result = shell.run_cell(cell.source, store_history=True, silent=False)
            if captured.stdout:
                cell.outputs.append(nbformat.v4.new_output("stream", name="stdout", text=captured.stdout))
            if captured.stderr:
                cell.outputs.append(nbformat.v4.new_output("stream", name="stderr", text=captured.stderr))
            for rich in captured.outputs:
                cell.outputs.append(nbformat.v4.new_output("display_data", data=rich.data, metadata=rich.metadata))
            duration = round(time.perf_counter() - tick, 2)
            cell.metadata["etl_validation_seconds"] = duration
            cell_error = result.error_before_exec or result.error_in_exec
            cell_results.append({"cell": index + 1, "passed": cell_error is None, "seconds": duration})
            print(f"Cell {index + 1}/{len(notebook.cells)}: {'FAIL' if cell_error else 'PASS'} ({duration}s)", flush=True)
            if cell_error:
                cell.outputs.append(nbformat.v4.new_output(
                    "error", ename=type(cell_error).__name__, evalue=str(cell_error),
                    traceback=traceback.format_exception(cell_error),
                ))
                print(captured.stdout, captured.stderr, flush=True)
                raise cell_error
            passed += 1
            nbformat.write(notebook, executed_path)

        checks = shell.user_ns.get("CHECKS", {})
        if not checks or not all(checks.values()):
            raise AssertionError("The notebook did not finish with all its checks passing.")
        embedder = shell.user_ns.get("embedder")
        if embedder is None or getattr(embedder, "fake", True):
            raise AssertionError("The notebook must use the real embedding model.")
        matches = re.findall(r"\b(\d+)/(\d+)\b", shell.user_ns.get("exercise_output", ""))
        official_result = tuple(map(int, matches[-1])) if matches else None
        if official_result != (18, 18):
            raise AssertionError(f"Expected the official exercise checker to pass 18/18; got {official_result}.")
    except BaseException as exc:
        error = exc
        traceback.print_exc()
    finally:
        unchanged = hashlib.sha256(source.read_bytes()).hexdigest() == original_hash
        if not unchanged and error is None:
            error = AssertionError("The input notebook changed during validation.")
        checks = shell.user_ns.get("CHECKS", {})
        embedder = shell.user_ns.get("embedder")
        summary = {
            "success": error is None and passed == total_cells,
            "method": "Code cells executed in order in a fresh IPython process",
            "python": platform.python_version(),
            "required_python": args.require_python,
            "platform": platform.system(),
            "machine": platform.machine(),
            "commit": os.getenv("GITHUB_SHA"),
            "input_notebook_sha256": original_hash,
            "input_notebook_unchanged": unchanged,
            "code_cells_total": total_cells,
            "code_cells_attempted": attempted,
            "code_cells_passed": passed,
            "notebook_checks_total": len(checks),
            "notebook_checks_passed": sum(bool(value) for value in checks.values()),
            "official_exercise_checks": f"{official_result[0]}/{official_result[1]}" if official_result else None,
            "real_embeddings": embedder is not None and not getattr(embedder, "fake", True),
            "embedding": getattr(embedder, "signature", None),
            "cursor_ui_tested": False,
            "dagster_web_ui_tested": False,
            "elapsed_seconds": round(time.perf_counter() - started, 2),
            "cells": cell_results,
            "error": f"{type(error).__name__}: {error}" if error else None,
        }
        final_table = shell.user_ns.get("final_summary")
        if final_table is not None:
            summary["observed_results"] = final_table.to_dict(orient="records")
        notebook.metadata.setdefault("etl_lab", {})["validation"] = summary
        nbformat.validate(notebook)
        nbformat.write(notebook, executed_path)
        (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

        # Save logs and compact exports, not virtual environments/model weights.
        lab_root = shell.user_ns.get("LAB_ROOT")
        if lab_root is not None:
            for directory in ("logs", "exports"):
                source_directory = Path(lab_root) / directory
                if source_directory.is_dir():
                    shutil.copytree(source_directory, output / directory, dirs_exist_ok=True)

        lines = [
            "# Notebook execution trial", "",
            f"Outcome: **{'PASS' if summary['success'] else 'FAIL'}**", "",
            f"Python: `{summary['python']}`; platform: `{summary['platform']} {summary['machine']}`.", "",
            "Code cells are executed in a fresh IPython process; a successful trial requires real embeddings.",
            "The Cursor interface and the Dagster web interface are not covered by this run.", "",
            "| Check | Observed |", "|---|---|",
            f"| Code cells passed | {passed}/{total_cells} |",
            f"| Notebook checks passed | {summary['notebook_checks_passed']}/{len(checks)} |",
            f"| Official exercise checks | {summary['official_exercise_checks'] or 'Not reached'} |",
            f"| Real embedding model | {summary['real_embeddings']} |",
            f"| Input notebook unchanged | {unchanged} |",
            f"| Duration in seconds | {summary['elapsed_seconds']} |",
        ]
        if error:
            lines += ["", "## Failure", "", "```text", summary["error"], "```"]
        lines += ["", "The executed notebook, per-stage logs, CSV files and HTML report are saved in the run artifact."]
        (output / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0 if summary["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
