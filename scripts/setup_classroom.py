"""Install the classroom environment into the active Python environment."""
import argparse
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-only", action="store_true", help="Install Python/dlt/dbt/Dagster; skip RAG and model download")
    args = parser.parse_args()
    if sys.version_info[:2] not in {(3, 11), (3, 12)}:
        raise SystemExit("Use Python 3.11 or 3.12 (the supplied Codespace uses 3.12).")
    (ROOT / ".dagster_home").mkdir(exist_ok=True)
    pip = [sys.executable, "-m", "pip", "install"]
    if not args.core_only:
        torch_args = ["torch==2.15.0"]
        if platform.system() in {"Linux", "Windows"}:
            torch_args += ["--index-url", "https://download.pytorch.org/whl/cpu"]
        run(*pip, *torch_args)
    requirements = "requirements-core.txt" if args.core_only else "requirements.txt"
    run(*pip, "-r", requirements)
    run(sys.executable, "scripts/generate_data.py")
    warmup = [sys.executable, "scripts/warmup.py"]
    if args.core_only:
        warmup.append("--core-only")
    run(*warmup)


if __name__ == "__main__":
    main()
