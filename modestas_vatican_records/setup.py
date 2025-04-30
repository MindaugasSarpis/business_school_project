#!/usr/bin/env python3
import logging
import subprocess
import sys
import venv
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s",
)
Logger = logging.getLogger(__name__)


def setup_environment() -> None:
    """Set up the project environment and install dependencies."""
    Logger.info("Setting up project-rag environment...")

    # Create virtual environment if it doesn't exist
    venv_path = Path(".venv")
    if not venv_path.exists():
        Logger.info("Creating virtual environment...")
        venv.create(".venv", with_pip=True)

    # Get the correct Python executable from the virtual environment
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python.exe"
        pip_path = venv_path / "Scripts" / "pip.exe"
    else:
        python_path = venv_path / "bin" / "python"
        pip_path = venv_path / "bin" / "pip"

    Logger.info("Installing Poetry in the virtual environment...")
    subprocess.run([str(pip_path), "install", "poetry"], check=True)

    Logger.info("Configuring Poetry...")
    subprocess.run(
        [str(python_path), "-m", "poetry", "config", "virtualenvs.in-project", "true"],
        check=True,
    )

    Logger.info("Installing dependencies...")
    subprocess.run([str(python_path), "-m", "poetry", "install"], check=True)

    # Create .env file in tests directory if it doesn't exist
    env_example_path = Path("tests/.env.example")
    env_path = Path("tests/.env")
    if env_example_path.exists() and not env_path.exists():
        Logger.info("Creating .env file in tests directory from .env.example...")
        env_content = env_example_path.read_text()
        env_path.write_text(env_content)
        Logger.info(
            "Created .env file. Please edit tests/.env to add your Gemini API key."
        )

    Logger.info("\nSetup complete! You can now run the project with:")
    Logger.info("  python main.py")
    Logger.info("Or run tests with:")
    Logger.info("  python test.py")


if __name__ == "__main__":
    setup_environment()
