from __future__ import annotations

from pathlib import Path

from experiments.run_attacks import run_attacks
from experiments.run_basic import run_basic
from experiments.run_strength import run_strength


def run_all(output_root: str | Path = "outputs", allow_download: bool = True, methods: list[str] | None = None) -> None:
    run_basic(output_root=output_root, allow_download=allow_download, methods=methods)
    run_strength(output_root=output_root, allow_download=allow_download, methods=methods)
    run_attacks(output_root=output_root, allow_download=allow_download, methods=methods)


if __name__ == "__main__":
    run_all()
