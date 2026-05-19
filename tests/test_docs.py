from pathlib import Path


def test_readme_contains_required_submission_sections():
    text = Path("README.md").read_text(encoding="utf-8")
    required = ["快速开始", "算法说明", "进阶实验", "抗攻击能力", "一键运行", "结果输出"]
    for phrase in required:
        assert phrase in text
