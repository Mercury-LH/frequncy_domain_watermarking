from experiments.run_basic import run_basic


def test_run_basic_creates_outputs(tmp_path):
    output_root = tmp_path / "outputs"
    rows = run_basic(output_root=output_root, allow_download=False, methods=["dft", "dct"])
    assert len(rows) == 2
    assert (output_root / "basic" / "metrics_basic.csv").exists()
    assert any((output_root / "basic").glob("*_watermarked.png"))
