from experiments.run_strength import run_strength


def test_run_strength_creates_metrics(tmp_path):
    rows = run_strength(output_root=tmp_path, allow_download=False, methods=["dft"], strengths={"dft": [5, 10]})
    assert len(rows) == 2
    assert (tmp_path / "strength" / "metrics_strength.csv").exists()
    assert (tmp_path / "strength" / "strength_psnr.png").exists()
