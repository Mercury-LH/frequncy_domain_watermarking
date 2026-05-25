from experiments.run_strength import run_strength


def test_run_strength_creates_metrics(tmp_path):
    rows = run_strength(output_root=tmp_path, allow_download=False, methods=["dft"], strengths={"dft": [5, 10]})
    assert len(rows) == 20
    assert (tmp_path / "multi_image" / "strength" / "metrics_strength_all.csv").exists()
    assert (tmp_path / "multi_image" / "strength" / "boat_gray" / "metrics_strength.csv").exists()
    assert (tmp_path / "multi_image" / "strength" / "house_color" / "strength_psnr.png").exists()
    assert {row["source_type"] for row in rows} == {"gray", "color"}
