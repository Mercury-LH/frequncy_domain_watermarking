# 题目5：图像频域水印系统设计

## 背景与目标
本项目完成“信号与系统大作业—题目5：图像频域水印”。系统需要覆盖基础、进阶、挑战三类要求：在图像频域嵌入不可见数字水印并正确提取；分析嵌入强度对图像质量的影响；测试 JPEG 压缩、缩放、加噪等攻击后的水印提取能力；实现 DFT、DCT、DWT 三类频域水印算法，并支持盲水印提取。

设计目标是面向高分课程作业：代码模块化、算法可解释、实验可复现、结果便于写入报告和答辩 PPT。

## 总体方案
采用 A+ 架构：以清晰算法模块为主体，吸收研究型实验框架的关键能力。

- 每种算法提供统一 `embed()` / `extract()` 接口。
- 命令行入口支持单步演示。
- 实验脚本支持一键生成基础、强度、攻击实验结果。
- YAML 配置保存数据路径、算法参数、实验参数。
- 指标、攻击、可视化与算法实现解耦。

## 项目结构
```text
frequncy_domain_watermarking/
├── configs/
│   └── experiments.yaml
├── data/
│   ├── raw/
│   └── watermark/
├── docs/
│   └── superpowers/specs/2026-05-19-frequency-domain-watermark-design.md
├── experiments/
│   ├── run_basic.py
│   ├── run_strength.py
│   ├── run_attacks.py
│   └── run_all.py
├── outputs/
│   ├── basic/
│   ├── strength/
│   ├── attacks/
│   └── figures/
├── src/
│   └── watermarking/
│       ├── algorithms/
│       │   ├── base.py
│       │   ├── dft.py
│       │   ├── dct.py
│       │   └── dwt.py
│       ├── attacks.py
│       ├── metrics.py
│       ├── registry.py
│       ├── io_utils.py
│       └── visualization.py
├── tests/
├── main.py
├── README.md
└── requirements.txt
```

## 算法设计
### DFT 非盲水印
DFT 算法作为基础任务主线。流程为：对灰度图执行 `fft2` 和 `fftshift`，将二值水印映射为 `{-1, +1}`，在中频区域选择成对频率坐标嵌入水印信息，并保持共轭对称以保证逆变换后图像主要为实数。嵌入强度由 `alpha` 控制。

提取时需要原图参与：分别计算原图与含水印图频谱，在嵌入位置比较频域差值，还原水印 bit。该算法直接对应作业基础要求中的 DFT、频域特定位置嵌入、逆变换、不可见性验证和正确提取。

### DCT 盲水印
DCT 算法作为挑战任务主线。系统将图像分为 `8x8` 块，每个块执行 DCT，并使用一对中频系数 `(c1, c2)` 表示一个水印 bit。若 bit 为 1，则调整为 `c1 > c2 + delta`；若 bit 为 0，则调整为 `c2 > c1 + delta`。提取时只需要含水印图，通过比较对应 DCT 系数大小关系恢复 bit，不需要原始图像。

该方案与 JPEG 压缩场景联系紧密，适合解释频域中频系数、视觉不可见性和抗压缩能力之间的关系。

### DWT 盲/半盲水印
DWT 算法作为挑战增强。系统使用小波分解得到 `LL, LH, HL, HH` 子带，优先在 `HL` 或 `LH` 中频子带嵌入水印，以平衡不可见性与鲁棒性。基础实现采用系数关系或量化方式做盲提取；若在部分攻击下稳定性不足，保留半盲提取模式用于对照实验。

DWT 部分用于展示多分辨率频域分析能力，使挑战部分不仅有 DCT，还能比较不同变换域的特点。

## 进阶实验设计
### 嵌入强度影响
对每种算法设置强度扫描：

- DFT：`alpha = [2, 5, 10, 20, 40]`
- DCT：`delta = [2, 5, 10, 20, 40]`
- DWT：根据子带系数量级设置 `alpha = [0.01, 0.03, 0.05, 0.1]` 或等效范围

每组实验输出原图、含水印图、差异图、提取水印图和指标表。报告重点分析水印强度与图像质量、提取准确率之间的折中关系。

### 抗攻击能力
对含水印图像施加以下攻击：

- JPEG 压缩：quality `90, 70, 50, 30`
- 缩放攻击：scale `0.5, 0.75, 1.5` 后恢复原尺寸
- 高斯噪声：sigma `5, 10, 20`
- 可选扩展：裁剪、旋转、模糊

攻击后重新提取水印，并记录攻击后图像质量和水印恢复质量。

## 指标与输出
系统统一计算以下指标：

- `MSE`：图像均方误差
- `PSNR`：峰值信噪比，用于不可见性评价
- `SSIM`：结构相似度，用于视觉质量评价
- `NC`：归一化相关系数，用于水印恢复相似度
- `BER`：误码率，用于水印 bit 恢复准确性

实验输出包括：

```text
outputs/
├── basic/
├── strength/metrics_strength.csv
├── strength/strength_curves.png
├── attacks/metrics_attacks.csv
├── attacks/attack_comparison.png
└── figures/
```

## 命令行与配置
命令行用于单步演示：

```bash
python main.py embed --method dft --image data/raw/lena.png --watermark data/watermark/logo.png --output outputs/demo/dft_watermarked.png
python main.py extract --method dct --image outputs/demo/dct_watermarked.png --output outputs/demo/dct_extracted.png
python main.py attack --type jpeg --quality 50 --image outputs/demo/dct_watermarked.png --output outputs/demo/attacked.jpg
```

DFT 提取需要 `--original` 参数；DCT 和 DWT 默认支持不依赖原图的提取模式。所有入口支持 `--config configs/experiments.yaml` 加载默认参数。

配置文件保存数据路径、算法参数、攻击参数和输出路径，使实验可复现。

## 数据策略
系统优先自动下载公开数据集中的示例图像。若网络或站点不可访问，程序明确提示用户手动下载并放入 `data/raw/` 和 `data/watermark/`，不伪造下载成功。README 将说明推荐数据来源和手动放置路径。

## 测试策略
单元测试覆盖：

- `metrics`：简单数组下 MSE、PSNR、NC、BER 结果正确。
- `attacks`：攻击输出尺寸、类型、数值范围正确。
- `registry`：`dft`、`dct`、`dwt` 可正确实例化。

集成测试覆盖：

- 使用小尺寸合成图像完成 `embed -> extract`。
- DCT 盲水印不传原图也能提取。
- `run_basic.py` 能生成含水印图与提取水印图。
- `run_all.py` 能生成 CSV 和关键图表。

## 错误处理
- 输入图片不存在：报出缺失路径和建议放置位置。
- 数据下载失败：提示手动下载，不继续假设数据存在。
- 水印尺寸超过算法容量：报出当前容量和建议尺寸。
- DFT 提取缺少原图：提示必须提供 `--original`。
- DWT 依赖缺失：提示安装 `PyWavelets`，并在 `requirements.txt` 固定版本。

## 可读性要求
- 算法文件只包含算法逻辑，不写实验流程。
- 实验文件只调度算法、攻击、指标和可视化，不写频域细节。
- 公共返回结构统一，避免各算法返回不同格式。
- README 包含最快运行、三算法切换、一键实验、结果解释四部分。
- 代码命名保持直观，优先可读性，不做过度抽象。

## 范围边界
本项目不实现复杂插件系统、Web UI 或交互式可视化界面。重点是频域水印算法、可复现实验、质量指标和课程报告支撑材料。
