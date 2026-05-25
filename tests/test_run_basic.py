from experiments.run_basic import run_basic


def test_run_basic_creates_outputs(tmp_path):
    output_root = tmp_path / "outputs"
    rows = run_basic(output_root=output_root, allow_download=False, methods=["dft", "dct"])
    assert len(rows) == 20
    assert (output_root / "multi_image" / "basic" / "metrics_basic_all.csv").exists()
    assert (output_root / "multi_image" / "basic" / "boat_gray" / "metrics_basic.csv").exists()
    assert any((output_root / "multi_image" / "basic" / "house_color").glob("*_watermarked.png"))
    assert {row["source_type"] for row in rows} == {"gray", "color"}
    assert {"image_name", "image_path", "source_type"}.issubset(rows[0])
