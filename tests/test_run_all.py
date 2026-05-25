from experiments.run_all import run_all


def test_run_all_creates_three_metric_files(tmp_path):
    run_all(output_root=tmp_path, allow_download=False, methods=["dft"])
    assert (tmp_path / "multi_image" / "basic" / "metrics_basic_all.csv").exists()
    assert (tmp_path / "multi_image" / "strength" / "metrics_strength_all.csv").exists()
    assert (tmp_path / "multi_image" / "attacks" / "metrics_attacks_all.csv").exists()
