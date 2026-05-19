# 图像频域水印

本项目实现信号与系统大作业题目5：图像频域水印。系统支持 DFT、DCT、DWT 三种频域水印算法，覆盖基础嵌入/提取、嵌入强度分析和 JPEG 压缩、缩放、加噪等抗攻击能力测试。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python experiments/run_all.py
```

如果公开数据下载失败，程序会生成可运行的示例图像和水印；也可以手动将测试图放入 `data/raw/`，将水印图放入 `data/watermark/`。

## 一键运行

```bash
python experiments/run_basic.py
python experiments/run_strength.py
python experiments/run_attacks.py
python experiments/run_all.py
```

## 命令行演示

```bash
python main.py embed --method dft --image data/raw/lena.png --watermark data/watermark/logo.png --output outputs/demo/dft_watermarked.png
python main.py extract --method dft --image outputs/demo/dft_watermarked.png --original data/raw/lena.png --output outputs/demo/dft_extracted.png
python main.py attack --type jpeg --quality 50 --image outputs/demo/dft_watermarked.png --output outputs/demo/dft_jpeg50.png
```

## 算法说明

- DFT：非盲水印算法，在傅里叶频谱中频区域嵌入水印，提取时需要原始图像。
- DCT：盲水印算法，以 `8x8` 图像块中频 DCT 系数对的大小关系表示水印 bit。
- DWT：小波域水印算法，在 `LH/HL/HH` 子带中嵌入水印，展示多分辨率频域方法。

## 进阶实验

`experiments/run_strength.py` 会扫描不同嵌入强度，输出 PSNR、SSIM、MSE、NC、BER 指标和曲线，用于分析水印强度对图像质量与提取准确率的影响。

## 抗攻击能力

`experiments/run_attacks.py` 会测试 JPEG 压缩、缩放和高斯噪声攻击。攻击后重新提取水印，并统计图像质量与水印恢复质量。

## 结果输出

结果默认保存在 `outputs/`：

- `outputs/basic/`：基础嵌入、提取和对比图。
- `outputs/strength/`：强度实验 CSV 和曲线图。
- `outputs/attacks/`：抗攻击实验 CSV 和对比图。

## 依赖

所有依赖及版本见 `requirements.txt`。
