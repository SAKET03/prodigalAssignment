"""
Call Analysis Dashboard
Interactive visualization for analyzing overtalk and silence metrics in call logs
"""

import subprocess
import sys
from pathlib import Path


def run_streamlit_app():
    """Run the Streamlit app with auto-reload enabled"""
    app_path = Path(__file__).parent / "main.py"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.fileWatcherType",
            "auto",
            "--server.runOnSave",
            "true",
            "--server.allowRunOnSave",
            "true",
        ]
    )


def main():
    run_streamlit_app()


if __name__ == "__main__":
    main()
