import subprocess
import sys


def test_cli_help_runs():
    result = subprocess.run([sys.executable, "main.py", "--help"], text=True, capture_output=True, check=False)
    assert result.returncode == 0
    assert "embed" in result.stdout
    assert "extract" in result.stdout
    assert "attack" in result.stdout
