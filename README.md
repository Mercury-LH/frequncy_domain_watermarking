---
title: Invisible Watermark Studio
emoji: 🌊
colorFrom: green
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# 图像频域水印

本项目实现信号与系统大作业题目5：图像频域水印。系统支持 DFT、DCT、DWT 三种频域水印算法，覆盖基础嵌入/提取、嵌入强度分析和 JPEG 压缩、缩放、加噪等抗攻击能力测试。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=.:src python3 experiments/run_all.py
```

默认实验会使用多张测试图，包含 `data/misc/` 中的灰度图和 `data/misc/`、`data/images/test/` 中的彩色图；灰度图直接进行频域水印处理，彩色图会通过 YCrCb 颜色空间的 Y 通道接口保留彩色外观。也可以手动将测试图放入 `data/raw/` 或在 `configs/experiments.yaml` 中继续添加图片。

## 一键运行

```bash
PYTHONPATH=.:src python3 experiments/run_basic.py
PYTHONPATH=.:src python3 experiments/run_strength.py
PYTHONPATH=.:src python3 experiments/run_attacks.py
PYTHONPATH=.:src python3 experiments/run_all.py
```

## 命令行演示

```bash
PYTHONPATH=.:src python3 main.py embed --method dft --image data/misc/boat.512.tiff --watermark data/watermark/logo.png --output outputs/demo/dft_watermarked.png
PYTHONPATH=.:src python3 main.py extract --method dft --image outputs/demo/dft_watermarked.png --original data/misc/boat.512.tiff --output outputs/demo/dft_extracted.png
PYTHONPATH=.:src python3 main.py attack --type jpeg --quality 50 --image outputs/demo/dft_watermarked.png --output outputs/demo/dft_jpeg50.png
```

彩色图像建议使用 Y 通道接口，例如：

```bash
PYTHONPATH=.:src python3 main.py embed --method dct --color-y --image data/images/test/101085.jpg --watermark data/watermark/logo.png --output outputs/demo/bsd_color_y_dct_watermarked.png
PYTHONPATH=.:src python3 main.py extract --method dct --color-y --image outputs/demo/bsd_color_y_dct_watermarked.png --output outputs/demo/bsd_color_y_dct_extracted.png
```

## 算法说明

- DFT：非盲水印算法，在傅里叶频谱中频区域嵌入水印，提取时需要原始图像。
- DCT：盲水印算法，以 `8x8` 图像块中频 DCT 系数对的大小关系表示水印 bit。
- DWT：小波域水印算法，在 `LH/HL/HH` 子带中嵌入水印，展示多分辨率频域方法。
- 彩色 Y 通道接口：彩色图像转换到 YCrCb 空间，仅在亮度通道 Y 上执行 DFT/DCT/DWT 水印处理，再与色度通道合成为彩色含水印图。

## 进阶实验

`experiments/run_strength.py` 会扫描不同嵌入强度，输出 PSNR、SSIM、MSE、NC、BER 指标和曲线，用于分析水印强度对图像质量与提取准确率的影响。

## 抗攻击能力

`experiments/run_attacks.py` 会测试 JPEG 压缩、缩放和高斯噪声攻击。攻击后重新提取水印，并统计图像质量与水印恢复质量。

## 结果输出

结果默认保存在 `outputs/multi_image/`，旧的 `outputs/basic/`、`outputs/strength/`、`outputs/attacks/` 不会被脚本主动删除：

- `outputs/multi_image/basic/<image_name>/`：每张图的基础嵌入、提取、频谱和对比图。
- `outputs/multi_image/basic/metrics_basic_all.csv`：所有图片的基础实验汇总指标。
- `outputs/multi_image/strength/<image_name>/`：每张图的强度实验 CSV 和曲线图。
- `outputs/multi_image/strength/metrics_strength_all.csv`：所有图片的强度实验汇总指标。
- `outputs/multi_image/attacks/<image_name>/`：每张图的抗攻击结果、CSV 和曲线图。
- `outputs/multi_image/attacks/metrics_attacks_all.csv`：所有图片的抗攻击实验汇总指标。

## 依赖

所有依赖及版本见 `requirements.txt`。
