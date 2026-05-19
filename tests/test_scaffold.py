from pathlib import Path


def test_project_scaffold_files_exist():
    expected = [
        Path("requirements.txt"),
        Path("pyproject.toml"),
        Path("configs/experiments.yaml"),
        Path("src/watermarking/__init__.py"),
        Path("src/watermarking/algorithms/__init__.py"),
    ]
    missing = [str(path) for path in expected if not path.exists()]
    assert missing == []
