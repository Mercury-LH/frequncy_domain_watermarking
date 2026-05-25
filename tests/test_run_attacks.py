from experiments.run_attacks import run_attacks


def test_run_attacks_creates_metrics(tmp_path):
    rows = run_attacks(output_root=tmp_path, allow_download=False, methods=["dct"], jpeg_qualities=[80], noise_sigmas=[5], scale_factors=[0.75])
    assert len(rows) == 30
    assert (tmp_path / "multi_image" / "attacks" / "metrics_attacks_all.csv").exists()
    assert (tmp_path / "multi_image" / "attacks" / "boat_gray" / "metrics_attacks.csv").exists()
    assert (tmp_path / "multi_image" / "attacks" / "house_color" / "attack_ber.png").exists()
    assert {row["source_type"] for row in rows} == {"gray", "color"}
