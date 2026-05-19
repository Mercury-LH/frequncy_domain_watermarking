from experiments.run_attacks import run_attacks


def test_run_attacks_creates_metrics(tmp_path):
    rows = run_attacks(output_root=tmp_path, allow_download=False, methods=["dct"], jpeg_qualities=[80], noise_sigmas=[5], scale_factors=[0.75])
    assert len(rows) == 3
    assert (tmp_path / "attacks" / "metrics_attacks.csv").exists()
    assert (tmp_path / "attacks" / "attack_ber.png").exists()
