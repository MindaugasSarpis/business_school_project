#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

from chatbot.utils.logging_config import configure_logging

Logger = configure_logging()


def run_tests() -> None:
    """Run all tests for the project-rag project."""
    # Check if virtual environment exists
    venv_path = Path(".venv")
    if not venv_path.exists():
        Logger.error(
            "Virtual environment not found. Please run 'python setup.py' first."
        )
        sys.exit(1)

    # Get the correct Python executable from the virtual environment
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        python_path = venv_path / "bin" / "python"

    if not python_path.exists():
        Logger.error(
            f"Python executable not found at {python_path}. Running setup again..."
        )
        subprocess.run([sys.executable, "setup.py"], check=True)

    # Run the tests
    Logger.info("Running tests...")
    result = subprocess.run(
        [str(python_path), "-m", "poetry", "run", "pytest", "-s", "tests/", "-v"],
        check=False,
    )

    if result.returncode == 0:
        Logger.info("\n✅ All tests passed!")
    else:
        Logger.error("\n❌ Some tests failed.")
        sys.exit(result.returncode)


if __name__ == "__main__":
    run_tests()
