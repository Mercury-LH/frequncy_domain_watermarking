<div style="text-align:center; margin-top: 80px; margin-bottom: 80px;">

# 图像频域水印实现报告

第 5 题：图像频域水印  
信号与系统大作业

组员：侯治民、乔义杰、金灏、王师睿  
代码仓库：https://github.com/Mercury-LH/frequncy_domain_watermarking  
日期：2026 年 5 月

</div>

---

# 1 引言

## 1.1 数字水印的背景

随着数字图像、音频、视频等多媒体数据在网络中的大量传播，数字内容的版权保护、完整性验证和来源追踪变得越来越重要。数字水印技术就是在这种背景下产生的一类信息隐藏方法。它通过在原始媒体中嵌入某种标识信息，使得该信息在正常观看时不明显，但在需要时可以通过算法提取出来，用于证明版权、检测篡改或追踪传播来源。

图像数字水印通常需要同时满足以下几个目标：

- **不可见性**：水印嵌入后，含水印图像与原始图像在视觉上应尽量接近，不能明显破坏图像质量。
- **可提取性**：接收端或验证端能够从含水印图像中提取出嵌入的水印信息。
- **鲁棒性**：图像经过 JPEG 压缩、缩放、噪声干扰等常见处理后，水印仍尽量可以恢复。
- **安全性**：攻击者在不知道嵌入参数或嵌入规则的情况下，不容易去除或伪造水印。
- **可扩展性**：算法应能处理不同图像、不同水印尺寸，并能通过参数调整控制图像质量和水印强度。

本次大作业题目为“图像频域水印”。与直接修改像素的空间域方法相比，频域水印先将图像从空间域变换到频域或变换域，再对频率系数进行修改。由于图像压缩、滤波等操作本身也常在频域或变换域中体现，因此频域水印通常比简单空间域水印更适合分析不可见性与鲁棒性之间的关系。

## 1.2 频域水印的基本思想

图像可以看作二维离散信号。对于一幅灰度图像，像素矩阵可以表示为：

```text
I(x, y), 0 <= x < H, 0 <= y < W
```

其中 `H` 和 `W` 分别表示图像高度和宽度。频域水印的基本流程可以概括为：

```text
原始图像 I
→ 频域变换 T(I)
→ 修改特定频率系数
→ 逆变换 T^-1
→ 含水印图像 Iw
```

在频域中，低频系数通常对应图像整体亮度和大结构，高频系数通常对应边缘、纹理和噪声。若直接修改低频，水印鲁棒性可能较强，但图像容易出现明显失真；若只修改高频，水印更不容易被肉眼察觉，但容易被压缩或滤波破坏。因此很多频域水印方法会选择中频区域作为嵌入位置，在不可见性和鲁棒性之间取得折中。

本项目实现了三种典型变换域方法：

1. **DFT（Discrete Fourier Transform）**：直接对整幅图像做二维傅里叶变换，在频谱中频位置嵌入水印。
2. **DCT（Discrete Cosine Transform）**：将图像划分为多个 8×8 小块，在每个块的中频 DCT 系数中嵌入 bit，作为主要盲水印方案。
3. **DWT（Discrete Wavelet Transform）**：将图像分解为多个小波子带，在指定子带中嵌入水印，作为小波域扩展方法。

## 1.3 作业任务与目标

根据课堂 PPT/作业说明《20260428 信号与系统 大作业说明.pdf》，题目5“图像频域水印”的要求可分为基础、进阶和挑战三部分。

### 1.3.1 基础任务

基础任务要求：

- 对图像进行 DFT 或类似频域变换。
- 在频域特定位置嵌入不可见数字水印。
- 通过逆变换得到含水印图像。
- 从含水印图像中提取原始水印。
- 验证水印不可见性。

本项目通过 DFT 频域水印实现基础任务。DFT 方法在傅里叶频谱中选择中频位置对称嵌入水印，提取时利用原图和含水印图像的频谱差异恢复水印。

### 1.3.2 进阶任务

进阶任务要求：

- 分析嵌入强度对图像质量的影响。
- 测试水印在 JPEG 压缩、缩放、加噪等操作后的抗攻击能力。

本项目分别编写了强度实验脚本和抗攻击实验脚本。强度实验扫描不同嵌入参数，统计 PSNR、SSIM、BER 等指标；抗攻击实验模拟 JPEG 压缩、高斯噪声和缩放攻击，分析攻击后水印提取质量。

### 1.3.3 挑战任务

挑战任务要求：

- 尝试 DCT 或 DWT 域水印。
- 设计盲水印算法，使提取水印时不需要原始图像。

本项目实现了 DCT 盲水印算法。该算法通过 8×8 图像块中两个中频 DCT 系数的大小关系编码水印 bit，提取时只需要含水印图像，不需要原始图像。同时项目还实现了 DWT 小波域水印作为扩展方案。

## 1.4 本项目完成内容概述

| 层次 | 要求 | 完成情况 |
|---|---|---|
| 基础 | DFT 或类似频域变换 | 已实现 DFT、DCT、DWT 三种变换域方法 |
| 基础 | 频域嵌入不可见水印 | DFT 中频对称嵌入；DCT 中频系数对嵌入；DWT 子带嵌入 |
| 基础 | 逆变换得到含水印图像 | 分别使用 IDFT、IDCT、IDWT 重建 |
| 基础 | 提取原始水印 | DFT 非盲提取；DCT 盲提取；DWT 扩展提取 |
| 基础 | 不可见性验证 | 输出 MSE、PSNR、SSIM 指标 |
| 进阶 | 嵌入强度分析 | 输出强度-PSNR 和强度-BER 曲线 |
| 进阶 | 抗攻击测试 | 测试 JPEG、噪声、缩放攻击 |
| 挑战 | DCT/DWT 水印 | 已实现 DCT 和 DWT |
| 挑战 | 盲水印 | DCT 提取时不需要原图 |
| 扩展 | 多图实验 | 使用 4 张灰度图和 6 张彩色图 |
| 扩展 | 彩色图处理 | 增加 Y 通道频域水印接口，输出保留彩色 |

---

# 2 系统结构与实验环境

## 2.1 项目目录结构

项目采用模块化结构组织代码，使算法实现、实验流程、指标计算和可视化输出相互独立。整体目录如下：

```text
frequncy_domain_watermarking/
├── configs/
│   └── experiments.yaml          # 数据集、算法参数和实验参数
├── data/
│   ├── images/                   # BSD 彩色图像
│   ├── misc/                     # USC-SIPI 灰度和彩色图像
│   ├── raw/                      # 可选原始图像目录
│   └── watermark/
│       └── logo.png              # HJQ 水印图
├── docs/
│   ├── manual/                   # 使用手册 Markdown/PDF
│   ├── final_report.md           # 本报告源文件
│   └── final_report.pdf          # 本报告 PDF
├── experiments/
│   ├── common.py                 # 实验公共工具
│   ├── run_basic.py              # 基础实验
│   ├── run_strength.py           # 强度实验
│   ├── run_attacks.py            # 抗攻击实验
│   └── run_all.py                # 一键运行全部实验
├── outputs/
│   └── multi_image/              # 多图实验输出结果
├── src/
│   └── watermarking/
│       ├── algorithms/
│       │   ├── base.py           # 抽象基类与公共转换函数
│       │   ├── dft.py            # DFT 水印算法
│       │   ├── dct.py            # DCT 盲水印算法
│       │   └── dwt.py            # DWT 水印算法
│       ├── attacks.py            # JPEG、缩放、噪声等攻击
│       ├── io_utils.py           # 图像读写、Y 通道处理
│       ├── metrics.py            # 图像质量和水印质量指标
│       ├── registry.py           # 算法注册表
│       └── visualization.py      # 图像与曲线可视化
├── tests/                        # pytest 自动化测试
├── main.py                       # 命令行接口
├── README.md
├── requirements.txt
└── pyproject.toml
```

这种结构的优点是：

- 算法之间相互独立，DFT、DCT、DWT 可以单独测试和替换。
- 实验脚本不直接依赖某个具体算法类，而是通过注册表创建算法对象。
- 指标计算和图像保存独立封装，方便在不同实验中复用。
- 配置文件集中管理实验参数，便于修改数据集、嵌入强度和攻击强度。

## 2.2 运行环境与依赖

项目主要使用 Python 实现，依赖如下：

| 依赖 | 作用 |
|---|---|
| numpy | 矩阵计算、FFT、数值处理 |
| opencv-python | 图像读写、DCT、颜色空间转换 |
| scipy | 科学计算辅助 |
| scikit-image | SSIM 指标计算 |
| matplotlib | 绘制对比图、频谱图和曲线 |
| PyWavelets | DWT 小波变换 |
| PyYAML | 读取实验配置文件 |
| pandas | 保存和处理 CSV 指标数据 |
| requests | 自动下载示例图像 |
| pytest | 自动化测试 |

安装依赖命令：

```bash
python3 -m pip install -r requirements.txt
```

运行全部测试命令：

```bash
python3 -m pytest -v
```

## 2.3 实验配置文件

所有实验的核心参数写在 `configs/experiments.yaml` 中。配置文件中同时保留单图字段和多图列表，既兼容单次命令行使用，也支持批量实验。

```yaml
dataset:
  image: data/misc/boat.512.tiff
  watermark: data/watermark/logo.png
  image_size: [512, 512]
  images:
    - name: boat_gray
      path: data/misc/boat.512.tiff
      source_type: gray
    - name: gray21_gray
      path: data/misc/gray21.512.tiff
      source_type: gray
    - name: house_color
      path: data/misc/house.tiff
      source_type: color
    - name: bsd_color
      path: data/images/test/101085.jpg
      source_type: color
```

算法参数示例：

```yaml
methods:
  dft:
    alpha: 10.0
    watermark_size: [64, 64]
    radius_ratio: 0.28
  dct:
    delta: 12.0
    block_size: 8
    watermark_size: [32, 32]
    coeff_pair: [[3, 4], [4, 3]]
  dwt:
    alpha: 0.05
    wavelet: haar
    subband: hl
    watermark_size: [64, 64]
```

实验参数示例：

```yaml
experiments:
  methods: [dft, dct, dwt]
  strengths:
    dft: [2, 5, 10, 20, 40]
    dct: [2, 5, 10, 20, 40]
    dwt: [0.01, 0.03, 0.05, 0.1]
  jpeg_qualities: [90, 70, 50, 30]
  noise_sigmas: [5, 10, 20]
  scale_factors: [0.5, 0.75, 1.5]
```

## 2.4 数据集与水印图

本实验使用 10 张测试图像，包括 4 张灰度图和 6 张彩色图。

| 类型 | 数量 | 图像名称 |
|---|---:|---|
| 灰度图 | 4 | `boat_gray`、`gray21_gray`、`texture_gray`、`pattern_gray` |
| 彩色图 | 6 | `house_color`、`airplane_color`、`bsd_color`、`bsd_landscape_color`、`bsd_train_color`、`bsd_texture_color` |

水印图为 `data/watermark/logo.png`，内容为 `HJQ`。在实验中，水印会根据不同算法的容量被缩放和二值化。例如 DFT 和 DWT 默认使用 `64×64` 水印，DCT 默认使用 `32×32` 水印，因为 DCT 每个 8×8 块通常只嵌入一个 bit。

---

# 3 基础任务：DFT 频域水印

## 3.1 任务问题

基础任务要求在图像频域中嵌入不可见水印，并能从含水印图像中提取出原始水印。这里选择二维 DFT 作为基础算法。对于二维图像 `f(x, y)`，其二维离散傅里叶变换可以写为：

```text
F(u, v) = Σx Σy f(x, y) · exp(-j2π(ux/M + vy/N))
```

逆变换为：

```text
f(x, y) = 1/(MN) · Σu Σv F(u, v) · exp(j2π(ux/M + vy/N))
```

在实现中，使用 `np.fft.fft2` 计算二维 DFT，使用 `np.fft.ifft2` 进行逆变换。为了便于选择频谱中心附近的中频区域，还使用 `np.fft.fftshift` 将低频移动到频谱中心。

## 3.2 原理分析

DFT 频域水印的核心思想是将二值水印映射为频谱中的微小扰动。设水印 bit 为 `0/1`，先将其转换为符号：

```text
bit = 1 → +1
bit = 0 → -1
```

然后在频谱中选取一组中频位置 `(u, v)`，按如下方式修改：

```text
F'(u, v) = F(u, v) + α · s
```

其中 `α` 是嵌入强度，`s` 是由水印 bit 转换得到的 `+1/-1` 符号。为了保证逆变换后结果主要为实数，需要在频谱的对称位置同时嵌入相同扰动。

本项目的 DFT 算法属于非盲水印算法。提取时需要原始图像，先计算含水印图像和原图的差值，再对差值做 DFT：

```text
D = FFT(Iw - I)
```

如果某个嵌入位置的差值频谱实部为正，则恢复 bit 为 1；否则恢复 bit 为 0。

## 3.3 算法设计与实现

DFT 水印嵌入流程：

```text
1. 读取原始图像并转换为灰度亮度矩阵。
2. 将水印缩放并二值化。
3. 对原始图像执行二维 FFT。
4. 将频谱中心移动到图像中心。
5. 选择中频嵌入位置。
6. 将水印 bit 映射为 +1/-1 并写入频谱。
7. 在对称频率位置同步写入，保持频谱对称性。
8. 执行逆 FFT 得到含水印图像。
```

核心代码如下：

```python
def embed(self, image: np.ndarray, watermark: np.ndarray) -> WatermarkResult:
    host = ensure_grayscale_float(image)
    bits = watermark_to_bits(watermark)
    signs = bits.astype(np.float64) * 2 - 1
    spectrum = np.fft.fftshift(np.fft.fft2(host))
    positions = self._positions(host.shape, bits.shape)
    flat_signs = signs.ravel()
    height, width = host.shape
    strength = self.alpha * height * width / 32.0
    for idx, (y, x) in enumerate(positions):
        spectrum[y, x] += strength * flat_signs[idx]
        spectrum[(height - y) % height, (width - x) % width] += strength * flat_signs[idx]
    watermarked = np.fft.ifft2(np.fft.ifftshift(spectrum)).real
    return WatermarkResult(
        image=normalize_uint8(watermarked),
        watermark=np.where(bits > 0, 255, 0).astype(np.uint8),
        metadata={"method": self.method_name, "alpha": self.alpha, "blind": False},
    )
```

DFT 水印提取代码如下：

```python
def extract(self, image, watermark_shape, original_image=None):
    if original_image is None:
        raise ValueError("DFT extraction requires original_image because this is a non-blind baseline.")
    watermarked = ensure_grayscale_float(image)
    original = ensure_grayscale_float(original_image)
    difference = np.fft.fftshift(np.fft.fft2(watermarked - original))
    positions = self._positions(watermarked.shape, watermark_shape)
    bits = np.array(
        [1 if difference[y, x].real >= 0 else 0 for y, x in positions],
        dtype=np.uint8,
    )
    watermark = (bits.reshape(watermark_shape) * 255).astype(np.uint8)
    return ExtractionResult(watermark=watermark, metadata={"method": self.method_name, "blind": False})
```

## 3.4 运行结果与分析

灰度图 `boat_gray` 上的 DFT 结果如下。图中依次展示原图、含水印图、差异图、原始水印和提取水印。

![Figure 1: boat_gray DFT 对比结果](../outputs/multi_image/basic/boat_gray/dft_comparison.png)

对应频谱图如下：

![Figure 2: boat_gray DFT 频谱图](../outputs/multi_image/basic/boat_gray/dft_spectrum.png)

另一张灰度图 `gray21_gray` 的 DFT 结果如下：

![Figure 3: gray21_gray DFT 对比结果](../outputs/multi_image/basic/gray21_gray/dft_comparison.png)

彩色图 `house_color` 通过 Y 通道进行 DFT 水印处理，输出仍保持彩色：

![Figure 4: house_color DFT 对比结果](../outputs/multi_image/basic/house_color/dft_comparison.png)

从图中可以看到，含水印图像和原图整体接近，差异图主要显示水印嵌入带来的细微变化。DFT 提取出的水印能够看到 `HJQ` 结构，说明基础任务中的频域嵌入和提取流程已经实现。

---

# 4 挑战任务一：DCT 盲水印算法

## 4.1 任务问题

挑战任务要求尝试 DCT 或 DWT 域水印，并设计盲水印算法。盲水印的关键要求是：提取水印时不依赖原始图像。为了满足这一点，本项目将 DCT 作为主要盲水印算法。

DCT 广泛用于图像压缩，尤其是 JPEG 标准。图像被划分为 8×8 小块后，每个块可以通过 DCT 转换为 64 个频率系数。左上角对应低频，右下角对应高频，中间区域为中频。

## 4.2 原理分析

二维 DCT 可表示为：

```text
C(u, v) = α(u)α(v) Σx Σy f(x, y)
          cos((2x+1)uπ/2N) cos((2y+1)vπ/2N)
```

其中 `C(u, v)` 为 DCT 系数。DCT 盲水印的关键不是记录某个绝对系数值，而是记录两个系数之间的相对大小关系。设选择两个中频系数 `c1` 和 `c2`：

```text
bit = 1: c1 > c2
bit = 0: c1 < c2
```

提取时，只需要对含水印图像重新分块并执行 DCT，再比较同一对系数大小即可恢复 bit。这种方法不需要原始图像，因此属于盲水印算法。

## 4.3 算法设计与实现

DCT 盲水印嵌入流程：

```text
1. 将图像转换为灰度或 Y 通道亮度矩阵。
2. 将图像按 8×8 分块。
3. 对每个块执行 DCT。
4. 取两个中频系数 c1=(3,4), c2=(4,3)。
5. 若要嵌入 bit=1，则调整为 c1 > c2。
6. 若要嵌入 bit=0，则调整为 c1 < c2。
7. 对修改后的块执行 IDCT。
8. 拼接所有块得到含水印图像。
```

核心代码如下：

```python
def embed(self, image: np.ndarray, watermark: np.ndarray) -> WatermarkResult:
    host = ensure_grayscale_float(image).copy()
    bits = watermark_to_bits(watermark).ravel()
    if bits.size > self._capacity(host.shape):
        raise ValueError(f"Watermark has {bits.size} bits but DCT capacity is {self._capacity(host.shape)} bits.")
    c1, c2 = self.coeff_pair
    for bit, (y, x, block) in zip(bits, self._iter_blocks(host)):
        dct_block = cv2.dct(block.astype(np.float32))
        a = dct_block[c1]
        b = dct_block[c2]
        midpoint = (a + b) / 2.0
        if bit == 1:
            dct_block[c1] = midpoint + self.delta / 2.0
            dct_block[c2] = midpoint - self.delta / 2.0
        else:
            dct_block[c1] = midpoint - self.delta / 2.0
            dct_block[c2] = midpoint + self.delta / 2.0
        host[y : y + self.block_size, x : x + self.block_size] = cv2.idct(dct_block)
    return WatermarkResult(
        image=normalize_uint8(host),
        watermark=(bits.reshape(watermark.shape) * 255).astype(np.uint8),
        metadata={"method": self.method_name, "delta": self.delta, "blind": True},
    )
```

提取流程更简单，只比较两个系数大小：

```python
def extract(self, image: np.ndarray, watermark_shape: tuple[int, int], original_image=None):
    host = ensure_grayscale_float(image)
    total_bits = int(np.prod(watermark_shape))
    c1, c2 = self.coeff_pair
    bits: list[int] = []
    for _, _, block in self._iter_blocks(host):
        dct_block = cv2.dct(block.astype(np.float32))
        bits.append(1 if dct_block[c1] > dct_block[c2] else 0)
        if len(bits) == total_bits:
            break
    watermark = (np.array(bits, dtype=np.uint8).reshape(watermark_shape) * 255).astype(np.uint8)
    return ExtractionResult(watermark=watermark, metadata={"method": self.method_name, "blind": True})
```

## 4.4 运行结果与分析

灰度图 `boat_gray` 的 DCT 盲水印结果如下：

![Figure 5: boat_gray DCT 盲水印结果](../outputs/multi_image/basic/boat_gray/dct_comparison.png)

对应 DCT 频谱可视化如下：

![Figure 6: boat_gray DCT 频谱图](../outputs/multi_image/basic/boat_gray/dct_spectrum.png)

彩色图 `house_color` 的 DCT 盲水印结果如下：

![Figure 7: house_color DCT 盲水印结果](../outputs/multi_image/basic/house_color/dct_comparison.png)

BSD 彩色图 `bsd_color` 的 DCT 盲水印结果如下：

![Figure 8: bsd_color DCT 盲水印结果](../outputs/multi_image/basic/bsd_color/dct_comparison.png)

从实验图可以看到，DCT 方法的差异图整体较弱，含水印图与原图肉眼接近；同时提取水印中 `HJQ` 字样比较清楚。基础实验中 DCT 方法平均 PSNR 达到约 `47.541 dB`，平均 BER 约为 `0.0014`，说明它在不可见性和水印恢复准确率之间表现较好。

---

# 5 挑战任务二：DWT 小波域扩展

## 5.1 原理分析

DWT（离散小波变换）是一种多分辨率分析方法。对图像进行一级二维小波分解后，可以得到四个子带：

| 子带 | 含义 |
|---|---|
| LL | 低频近似部分，包含图像主要结构 |
| LH | 水平方向细节 |
| HL | 垂直方向细节 |
| HH | 对角高频细节 |

DWT 水印的思想是在某个细节子带中叠加水印信息。相比 DFT，DWT 同时具有频率局部性和空间局部性；相比 DCT，DWT 不依赖固定 8×8 分块，适合展示多尺度频域水印方法。

## 5.2 算法流程

```text
原始图像
→ 一级 DWT 分解
→ 得到 LL、LH、HL、HH 子带
→ 在指定子带中嵌入水印
→ IDWT 重建图像
→ 得到含水印图像
```

DWT 嵌入的关键步骤是将水印二值化为 `+1/-1` 符号，再叠加到指定子带的前若干位置中。默认配置中使用 `haar` 小波和 `HL` 子带。

## 5.3 实验结果

灰度图 `boat_gray` 的 DWT 结果如下：

![Figure 9: boat_gray DWT 水印结果](../outputs/multi_image/basic/boat_gray/dwt_comparison.png)

彩色图 `airplane_color` 的 DWT 结果如下：

![Figure 10: airplane_color DWT 水印结果](../outputs/multi_image/basic/airplane_color/dwt_comparison.png)

BSD 纹理图 `bsd_texture_color` 的 DWT 结果如下：

![Figure 11: bsd_texture_color DWT 水印结果](../outputs/multi_image/basic/bsd_texture_color/dwt_comparison.png)

DWT 方法在当前实验中主要用于展示小波域水印思想。由于默认嵌入强度较低，图像失真很小，因此 PSNR 和 SSIM 指标较高。报告中将 DWT 作为挑战部分的扩展算法，而将 DCT 作为主要盲水印算法。

---

# 6 彩色图像 Y 通道水印接口

## 6.1 问题来源

在初始实验中，如果直接用 OpenCV 的灰度读取方式处理彩色图，输出图像会丢失颜色。这虽然可以完成频域水印算法验证，但不利于展示真实彩色图像场景。为了让彩色图像输出仍保持彩色，本项目增加了 Y 通道频域水印接口。

## 6.2 原理分析

RGB 图像可以转换到 YCrCb 颜色空间，其中：

- `Y` 表示亮度信息。
- `Cr` 和 `Cb` 表示色度信息。

人眼对亮度变化更敏感，但大多数图像结构也主要体现在亮度通道中。因此，在 Y 通道嵌入水印可以保持算法的二维矩阵处理方式，同时保留彩色图像的色度信息。

Y 通道处理流程如下：

```text
RGB 彩色图像
→ 转换到 YCrCb
→ 提取 Y 亮度通道
→ 在 Y 通道执行 DFT/DCT/DWT 水印
→ 用修改后的 Y 替换原 Y
→ 保留原 Cr/Cb 通道
→ 转回 RGB 彩色图像
```

## 6.3 代码实现

图像读取和 Y 通道替换代码如下：

```python
def read_color(path: str | Path) -> np.ndarray:
    image_path = Path(path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}. Put the file there or run demo data preparation.")
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Failed to read image as color: {image_path}.")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def luminance_channel(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)[:, :, 0]


def replace_luminance(image: np.ndarray, luminance: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return luminance
    ycrcb = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
    ycrcb[:, :, 0] = np.clip(luminance, 0, 255).astype(np.uint8)
    return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB)
```

命令行使用示例：

```bash
PYTHONPATH=.:src python3 main.py embed \
  --method dct \
  --color-y \
  --image data/images/test/101085.jpg \
  --watermark data/watermark/logo.png \
  --output outputs/demo/bsd_color_y_dct_watermarked.png
```

## 6.4 彩色实验结果

`house_color` 上的 DCT 结果如下：

![Figure 12: house_color 彩色 Y 通道 DCT 结果](../outputs/multi_image/basic/house_color/dct_comparison.png)

`bsd_train_color` 上的 DFT 结果如下：

![Figure 13: bsd_train_color 彩色 Y 通道 DFT 结果](../outputs/multi_image/basic/bsd_train_color/dft_comparison.png)

`bsd_landscape_color` 上的 DWT 结果如下：

![Figure 14: bsd_landscape_color 彩色 Y 通道 DWT 结果](../outputs/multi_image/basic/bsd_landscape_color/dwt_comparison.png)

从这些结果可以看出，彩色图像经过水印处理后仍保留颜色，说明 Y 通道接口解决了彩色图被灰度化的问题。

---

# 7 评价指标设计

## 7.1 图像质量指标

为了验证水印不可见性，本项目使用 MSE、PSNR 和 SSIM 三个指标。

### 7.1.1 MSE

MSE 表示原图和含水印图像之间的均方误差：

```text
MSE = 1/(MN) · Σx Σy [I(x,y) - Iw(x,y)]²
```

MSE 越小，说明两幅图像越接近。

### 7.1.2 PSNR

PSNR 表示峰值信噪比：

```text
PSNR = 10 · log10(MAX² / MSE)
```

其中 `MAX=255`。PSNR 越高，说明图像失真越小。一般情况下：

| PSNR | 图像质量说明 |
|---|---|
| > 40 dB | 失真很小 |
| 30-40 dB | 质量较好 |
| 20-30 dB | 有一定失真 |
| < 20 dB | 失真较明显 |

### 7.1.3 SSIM

SSIM 衡量结构相似性，范围通常在 0 到 1 之间，越接近 1 表示图像结构越相似。

## 7.2 水印质量指标

水印提取质量通过 NC 和 BER 衡量。

### 7.2.1 NC

NC 是归一化相关系数，用于衡量原始水印和提取水印之间的相关程度：

```text
NC = <W, W'> / (||W|| · ||W'||)
```

NC 越接近 1，表示提取水印越接近原水印。

### 7.2.2 BER

BER 表示 bit 错误率：

```text
BER = 错误 bit 数 / 总 bit 数
```

BER 越低，说明水印提取越准确。

## 7.3 指标计算代码

```python
def mse(reference: np.ndarray, candidate: np.ndarray) -> float:
    ref, cand = _same_shape(reference, candidate)
    return float(np.mean((ref - cand) ** 2))


def psnr(reference: np.ndarray, candidate: np.ndarray, data_range: float = 255.0) -> float:
    error = mse(reference, candidate)
    if error == 0:
        return math.inf
    return float(10 * math.log10((data_range**2) / error))


def bit_error_rate(reference: np.ndarray, candidate: np.ndarray) -> float:
    ref, cand = _same_shape(_bits(reference), _bits(candidate))
    return float(np.mean(ref != cand))
```

---

# 8 基础实验结果汇总

## 8.1 输出目录

基础实验输出目录为：

```text
outputs/multi_image/basic/
├── boat_gray/
├── gray21_gray/
├── texture_gray/
├── pattern_gray/
├── house_color/
├── airplane_color/
├── bsd_color/
├── bsd_landscape_color/
├── bsd_train_color/
└── bsd_texture_color/
```

每张图像目录中包含：

```text
dft_watermarked.png
dft_extracted.png
dft_comparison.png
dft_spectrum.png

dct_watermarked.png
dct_extracted.png
dct_comparison.png
dct_spectrum.png

dwt_watermarked.png
dwt_extracted.png
dwt_comparison.png
dwt_spectrum.png

metrics_basic.csv
```

## 8.2 平均指标

基础实验的聚合指标文件为：

```text
outputs/multi_image/basic/metrics_basic_all.csv
```

三种算法的平均指标如下：

| method | mse | psnr | ssim | nc | ber |
| --- | --- | --- | --- | --- | --- |
| dct | 1.6081 | 47.541 | 0.9957 | 0.9973 | 0.0014 |
| dft | 261.8546 | 24.1322 | 0.7517 | 0.9236 | 0.0382 |
| dwt | 0.03 | inf | 0.9999 | 1.0 | 0.0 |

## 8.3 多图实验结果展示

灰度纹理图 DFT 结果：

![Figure 15: texture_gray DFT 结果](../outputs/multi_image/basic/texture_gray/dft_comparison.png)

灰度 pattern 图 DCT 结果：

![Figure 16: pattern_gray DCT 结果](../outputs/multi_image/basic/pattern_gray/dct_comparison.png)

彩色 airplane 图 DCT 结果：

![Figure 17: airplane_color DCT 结果](../outputs/multi_image/basic/airplane_color/dct_comparison.png)

BSD train 彩色图 DCT 结果：

![Figure 18: bsd_train_color DCT 结果](../outputs/multi_image/basic/bsd_train_color/dct_comparison.png)

BSD texture 彩色图 DFT 结果：

![Figure 19: bsd_texture_color DFT 结果](../outputs/multi_image/basic/bsd_texture_color/dft_comparison.png)

从多图实验可以看到，不同图像纹理复杂程度会影响水印效果。纹理较复杂的图像中，水印扰动更容易被图像本身的纹理掩盖；平滑区域较多的图像中，差异图可能更明显。彩色图通过 Y 通道嵌入后，整体颜色仍然保留。

---

# 9 进阶任务一：嵌入强度实验

## 9.1 任务问题

嵌入强度是水印算法中最重要的参数之一。强度过低时，水印对图像影响小，但提取时容易出错；强度过高时，水印更容易提取，但图像失真也会增加。因此，需要通过实验分析强度对图像质量和提取准确率的影响。

## 9.2 实验设计

强度实验对三种算法分别设置不同扫描范围：

```yaml
strengths:
  dft: [2, 5, 10, 20, 40]
  dct: [2, 5, 10, 20, 40]
  dwt: [0.01, 0.03, 0.05, 0.1]
```

运行脚本：

```bash
PYTHONPATH=.:src python3 experiments/run_strength.py
```

核心实验代码如下：

```python
for method in selected_methods:
    for value in sweep[method]:
        params = dict(config["methods"][method])
        watermark_size = tuple(params.pop("watermark_size"))
        params[_strength_key(method)] = value
        watermark = prepare_watermark(watermark_source, watermark_size)
        watermarker = create_watermarker(method, **params)
        embedded = watermarker.embed(image, watermark)
        extracted = watermarker.extract(
            embedded.image,
            watermark.shape,
            original_image=image if method == "dft" else None,
        )
```

## 9.3 总体曲线

强度与 PSNR 的关系如下：

![Figure 20: 所有图像强度-PSNR 曲线](../outputs/multi_image/strength/strength_psnr_all.png)

强度与 BER 的关系如下：

![Figure 21: 所有图像强度-BER 曲线](../outputs/multi_image/strength/strength_ber_all.png)

## 9.4 单图曲线展示

`boat_gray` 强度实验：

![Figure 22: boat_gray 强度-PSNR 曲线](../outputs/multi_image/strength/boat_gray/strength_psnr.png)

![Figure 23: boat_gray 强度-BER 曲线](../outputs/multi_image/strength/boat_gray/strength_ber.png)

`house_color` 强度实验：

![Figure 24: house_color 强度-PSNR 曲线](../outputs/multi_image/strength/house_color/strength_psnr.png)

![Figure 25: house_color 强度-BER 曲线](../outputs/multi_image/strength/house_color/strength_ber.png)

## 9.5 数据分析

DFT 强度实验平均结果：

| strength | psnr | ber |
| --- | --- | --- |
| 2.0 | 35.053 | 0.0365 |
| 5.0 | 28.9068 | 0.0365 |
| 10.0 | 24.1322 | 0.0382 |
| 20.0 | 19.6326 | 0.0506 |
| 40.0 | 15.6902 | 0.1127 |

DCT 强度实验平均结果：

| strength | psnr | ber |
| --- | --- | --- |
| 2.0 | inf | 0.1482 |
| 5.0 | 49.7319 | 0.0036 |
| 10.0 | 48.1555 | 0.0017 |
| 20.0 | 45.2405 | 0.0012 |
| 40.0 | 40.7824 | 0.0007 |

可以看到 DCT 方法最符合预期规律：当 `delta=2` 时，图像几乎没有失真，但 BER 较高；当 `delta` 提高到 5 或 10 时，BER 快速下降，而 PSNR 仍保持较高；当 `delta=40` 时，BER 进一步降低，但 PSNR 下降到约 40.78 dB。综合考虑不可见性和提取准确率，默认 `delta=12` 是较合理的折中。

---

# 10 进阶任务二：抗攻击实验

## 10.1 任务问题

图像在实际传播中常常会经历压缩、缩放、加噪等处理。抗攻击实验的目标是观察水印在这些处理后是否仍能被提取。

本项目测试三类攻击：

| 攻击类型 | 参数 | 含义 |
|---|---|---|
| JPEG | 90、70、50、30 | 质量因子越低，压缩越强 |
| noise | 5、10、20 | 高斯噪声标准差越大，噪声越强 |
| resize | 0.5、0.75、1.5 | 先缩放再恢复原尺寸 |

## 10.2 攻击代码实现

攻击实验会先嵌入水印，再对含水印图像施加攻击，最后从攻击后的图像中提取水印。

```python
attacks = []
attacks += [("jpeg", q, jpeg_compress(embedded.image, q)) for q in qualities]
attacks += [("noise", s, gaussian_noise(embedded.image, s)) for s in sigmas]
attacks += [("resize", s, resize_attack(embedded.image, s)) for s in scales]
for attack_name, level, attacked in attacks:
    extracted = watermarker.extract(
        attacked,
        watermark.shape,
        original_image=image if method == "dft" else None,
    )
```

## 10.3 总体攻击结果

所有图像的 BER 曲线如下：

![Figure 26: 所有图像抗攻击 BER 曲线](../outputs/multi_image/attacks/attack_ber_all.png)

`boat_gray` 单图攻击结果：

![Figure 27: boat_gray 抗攻击 BER 曲线](../outputs/multi_image/attacks/boat_gray/attack_ber.png)

`house_color` 单图攻击结果：

![Figure 28: house_color 抗攻击 BER 曲线](../outputs/multi_image/attacks/house_color/attack_ber.png)

## 10.4 攻击图像示例

JPEG 质量为 30 的攻击图像示例：

![Figure 29: boat_gray DFT JPEG 30 攻击](../outputs/multi_image/attacks/boat_gray/dft_jpeg_30_attacked.png)

高斯噪声 sigma=20 的攻击图像示例：

![Figure 30: boat_gray DFT noise 20 攻击](../outputs/multi_image/attacks/boat_gray/dft_noise_20_attacked.png)

缩放比例 0.5 的攻击图像示例：

![Figure 31: boat_gray DFT resize 0.5 攻击](../outputs/multi_image/attacks/boat_gray/dft_resize_0.5_attacked.png)

彩色图 JPEG 攻击示例：

![Figure 32: bsd_color DCT JPEG 30 攻击](../outputs/multi_image/attacks/bsd_color/dct_jpeg_30_attacked.png)

彩色图噪声攻击示例：

![Figure 33: bsd_color DCT noise 20 攻击](../outputs/multi_image/attacks/bsd_color/dct_noise_20_attacked.png)

## 10.5 数据分析

JPEG 攻击平均结果：

| attack | level | method | ber | nc |
| --- | --- | --- | --- | --- |
| jpeg | 30.0 | dct | 0.372 | 0.2561 |
| jpeg | 30.0 | dft | 0.0469 | 0.9061 |
| jpeg | 50.0 | dct | 0.3971 | 0.2059 |
| jpeg | 50.0 | dft | 0.0406 | 0.9188 |
| jpeg | 70.0 | dct | 0.3793 | 0.2414 |
| jpeg | 70.0 | dft | 0.0389 | 0.9223 |
| jpeg | 90.0 | dct | 0.0071 | 0.9857 |
| jpeg | 90.0 | dft | 0.0383 | 0.9235 |

噪声攻击平均结果：

| attack | level | method | ber | nc |
| --- | --- | --- | --- | --- |
| noise | 5.0 | dct | 0.0552 | 0.8896 |
| noise | 5.0 | dft | 0.0384 | 0.9232 |
| noise | 10.0 | dct | 0.2134 | 0.5732 |
| noise | 10.0 | dft | 0.0404 | 0.9192 |
| noise | 20.0 | dct | 0.3478 | 0.3045 |
| noise | 20.0 | dft | 0.0576 | 0.8849 |

缩放攻击平均结果：

| attack | level | method | ber | nc |
| --- | --- | --- | --- | --- |
| resize | 0.5 | dct | 0.3816 | 0.2367 |
| resize | 0.5 | dft | 0.1672 | 0.6655 |
| resize | 0.75 | dct | 0.0542 | 0.8916 |
| resize | 0.75 | dft | 0.0553 | 0.8894 |
| resize | 1.5 | dct | 0.0118 | 0.9764 |
| resize | 1.5 | dft | 0.039 | 0.922 |

实验结果说明，DCT 盲水印对轻度 JPEG 和轻度缩放较稳定，但对强压缩、强噪声和 0.5 倍缩放更敏感。这是因为 DCT 方法依赖固定 8×8 分块和固定系数对，一旦攻击改变局部块的频率结构，系数大小关系就可能被破坏。DFT 非盲方法在部分攻击下表现较稳定，但它需要原图参与提取，因此适用场景不同。

---

# 11 命令行接口与实验脚本

## 11.1 命令行接口

项目提供 `main.py`，支持嵌入、提取和攻击三类命令。

### 11.1.1 嵌入水印

```bash
PYTHONPATH=.:src python3 main.py embed \
  --method dft \
  --image data/misc/boat.512.tiff \
  --watermark data/watermark/logo.png \
  --output outputs/demo/boat_dft_watermarked.png
```

### 11.1.2 提取水印

DFT 是非盲算法，需要原图：

```bash
PYTHONPATH=.:src python3 main.py extract \
  --method dft \
  --image outputs/demo/boat_dft_watermarked.png \
  --original data/misc/boat.512.tiff \
  --output outputs/demo/boat_dft_extracted.png
```

DCT 是盲水印算法，不需要原图：

```bash
PYTHONPATH=.:src python3 main.py extract \
  --method dct \
  --image outputs/demo/boat_dct_watermarked.png \
  --output outputs/demo/boat_dct_extracted.png
```

### 11.1.3 攻击图像

```bash
PYTHONPATH=.:src python3 main.py attack \
  --type jpeg \
  --quality 50 \
  --image outputs/demo/boat_dft_watermarked.png \
  --output outputs/demo/boat_dft_jpeg50.png
```

## 11.2 实验脚本

完整实验建议使用脚本运行：

```bash
PYTHONPATH=.:src python3 experiments/run_all.py
```

该命令会依次执行：

```text
run_basic.py
run_strength.py
run_attacks.py
```

输出保存在：

```text
outputs/multi_image/
```

## 11.3 自动化测试

项目包含 26 个自动化测试，覆盖：

- DFT 嵌入与提取。
- DCT 盲水印嵌入与提取。
- DWT 嵌入与提取。
- JPEG、resize、noise 攻击函数。
- MSE、PSNR、SSIM、NC、BER 指标。
- CLI 是否可运行。
- 实验脚本是否生成 CSV 和图像。
- README 是否包含必要说明。

测试命令：

```bash
python3 -m pytest -v
```

---

# 12 结果讨论

## 12.1 三种算法对比

| 算法 | 是否盲提取 | 优点 | 缺点 | 适用定位 |
|---|---|---|---|---|
| DFT | 否 | 频域思想直观，抗部分攻击效果较好 | 提取需要原图，失真相对明显 | 基础任务与非盲基线 |
| DCT | 是 | 不需要原图，图像质量高，解释性强 | 对强压缩、强噪声、几何变换敏感 | 挑战任务核心算法 |
| DWT | 扩展方法 | 多分辨率分析，扰动较弱 | 当前实现更偏展示扩展思路 | 挑战部分补充算法 |

## 12.2 不可见性分析

从基础实验平均指标看，DCT 的 PSNR 约为 `47.541 dB`，SSIM 约为 `0.9957`，说明含水印图像和原图非常接近。DFT 的 PSNR 较低，说明当前频谱嵌入强度下图像扰动更明显，但它可以较好展示傅里叶域水印的基本机制。

## 12.3 鲁棒性分析

鲁棒性实验表明，水印算法没有绝对最优，而是取决于攻击类型和是否允许使用原图。DCT 盲水印在轻度 JPEG 和轻度缩放下表现较好，但强攻击会破坏 DCT 系数关系。DFT 方法需要原图，但在 JPEG 和噪声下 BER 较低。实际应用中可以根据需求选择：若验证端可获得原图，可以使用非盲方法；若验证端不能获得原图，则应选择 DCT 盲水印，并进一步加入纠错编码或同步机制。

## 12.4 参数选择分析

DCT 的 `delta` 是最重要参数。根据强度实验，`delta` 太小会导致 BER 较高，`delta` 太大则会降低 PSNR。默认值 `12.0` 在本项目中能够兼顾图像质量和提取准确性。

DFT 的 `alpha` 控制频谱扰动强度。实验中可以看到，随着 `alpha` 增大，PSNR 明显下降，说明 DFT 对强度较敏感。

DWT 的 `alpha` 控制小波子带扰动。当前默认较小，用于保证不可见性和展示扩展方法。

---

# 13 总结与展望

本项目围绕“图像频域水印”完成了完整的课程大作业实现。基础部分使用 DFT 完成频域嵌入、逆变换和水印提取；进阶部分完成嵌入强度扫描和抗攻击实验；挑战部分实现 DCT 盲水印，并扩展 DWT 小波域方法和彩色图 Y 通道水印接口。项目还提供了命令行工具、批量实验脚本、配置文件、自动化测试、详细手册和最终报告。

实验结果表明，DCT 盲水印在默认参数下具有较好的不可见性和提取准确率，适合作为本项目的主要挑战算法。DFT 方法虽然需要原图，但更直观地体现了傅里叶频域水印思想。DWT 方法展示了小波域多分辨率分析的可能性。彩色 Y 通道接口使算法能够处理真实彩色图像，并保持输出图像的颜色。

仍可改进的方向包括：

1. 在 DCT 水印中加入纠错编码，降低攻击后的 BER。
2. 使用伪随机位置嵌入，提高安全性。
3. 使用重复嵌入或多数投票，提高鲁棒性。
4. 引入 DWT-DCT-SVD 混合水印算法，提高对压缩和噪声的稳定性。
5. 针对缩放、裁剪等几何攻击加入同步模板或特征点对齐。
6. 将实验结果进一步导出为 PPT 图表，方便答辩展示。

---

# 14 小组分工与工作量说明

本项目由 侯治民、乔义杰、金灏、王师睿 共同完成。由于本项目需要完成算法实现、实验设计、数据处理、报告撰写和代码仓库维护等多项工作，整体分工按照“核心开发者承担更多实现与集成工作，其他组员分别负责实验、测试、文档和结果分析”的方式组织。其中侯治民承担主要代码实现、系统集成和最终交付工作，工作量占比最高。

| 组员 | 主要负责内容 | 工作量占比 |
|---|---|---:|
| 侯治民 | 需求分析；整体架构设计；DFT/DCT/DWT 算法实现；彩色图 Y 通道接口；CLI 与实验脚本集成；GitHub 仓库维护；最终报告统稿与 PDF 生成 | 45% |
| 乔义杰 | 数据集整理；灰度图和彩色图样本筛选；基础实验运行；基础对比图、频谱图和水印提取结果检查 | 20% |
| 金灏 | 进阶实验设计与结果整理；嵌入强度实验；JPEG、噪声、缩放攻击实验；CSV 指标统计和曲线图检查 | 20% |
| 王师睿 | README 和使用手册整理；测试用例检查；报告文字校对；答辩材料和运行说明整理 | 15% |

具体工作包括：

- 阅读课程 PPT/作业说明，拆解基础、进阶、挑战三部分要求。
- 设计模块化代码架构，拆分算法、指标、攻击、可视化和实验脚本。
- 实现 DFT 频域非盲水印算法。
- 实现 DCT 分块盲水印算法。
- 实现 DWT 小波域扩展水印算法。
- 实现彩色图 Y 通道频域水印接口。
- 准备 USC-SIPI 和 BSD 灰度/彩色图像数据。
- 设计并生成 HJQ 二值水印。
- 完成基础实验、强度实验和抗攻击实验。
- 输出多图对比图、频谱图、强度曲线和攻击曲线。
- 编写 CLI 接口和 YAML 配置系统。
- 编写自动化测试并验证主要功能。
- 编写 README、详细使用手册和最终报告。
- 将代码和报告上传到 GitHub 仓库，仓库地址为：https://github.com/Mercury-LH/frequncy_domain_watermarking

---

# 附录 A：主要运行命令汇总

```bash
# 安装依赖
python3 -m pip install -r requirements.txt

# 运行测试
python3 -m pytest -v

# 一键运行全部实验
PYTHONPATH=.:src python3 experiments/run_all.py

# 基础实验
PYTHONPATH=.:src python3 experiments/run_basic.py

# 强度实验
PYTHONPATH=.:src python3 experiments/run_strength.py

# 抗攻击实验
PYTHONPATH=.:src python3 experiments/run_attacks.py

# DCT 盲水印嵌入
PYTHONPATH=.:src python3 main.py embed \
  --method dct \
  --image data/misc/boat.512.tiff \
  --watermark data/watermark/logo.png \
  --output outputs/demo/boat_dct_watermarked.png

# DCT 盲水印提取
PYTHONPATH=.:src python3 main.py extract \
  --method dct \
  --image outputs/demo/boat_dct_watermarked.png \
  --output outputs/demo/boat_dct_extracted.png
```

# 附录 B：输出文件说明

```text
outputs/multi_image/basic/metrics_basic_all.csv
outputs/multi_image/strength/metrics_strength_all.csv
outputs/multi_image/attacks/metrics_attacks_all.csv
outputs/multi_image/strength/strength_psnr_all.png
outputs/multi_image/strength/strength_ber_all.png
outputs/multi_image/attacks/attack_ber_all.png
```

其中：

- `metrics_basic_all.csv`：基础实验指标汇总。
- `metrics_strength_all.csv`：嵌入强度实验指标汇总。
- `metrics_attacks_all.csv`：抗攻击实验指标汇总。
- `strength_psnr_all.png`：强度与 PSNR 曲线。
- `strength_ber_all.png`：强度与 BER 曲线。
- `attack_ber_all.png`：不同攻击下 BER 曲线。
