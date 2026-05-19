from experiments.run_all import run_all


def test_run_all_creates_three_metric_files(tmp_path):
    run_all(output_root=tmp_path, allow_download=False, methods=["dft"])
    assert (tmp_path / "basic" / "metrics_basic.csv").exists()
    assert (tmp_path / "strength" / "metrics_strength.csv").exists()
    assert (tmp_path / "attacks" / "metrics_attacks.csv").exists()
