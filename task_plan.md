# 图像频域水印大作业计划

## 目标
完成“题目5：图像频域水印”大作业：实现不可见数字水印嵌入与提取，验证基础 DFT 方案，并扩展抗攻击测试；最终提交答辩 PPT、大作业报告、可直接运行的代码、README 和 requirements.txt。

## 当前状态
- 项目目录已初始化为 Git 仓库。
- 已读取作业说明 PDF。
- 数据目录 `data/` 当前未发现文件。

## 任务范围
### 必做基础
- 对图像进行 DFT 等频域变换。
- 在频域特定位置嵌入不可见水印。
- 通过逆变换得到含水印图像。
- 验证视觉不可见性。
- 从含水印图像中正确提取原始水印。

### 进阶分析
- 分析不同嵌入强度对图像质量的影响。
- 测试 JPEG 压缩、缩放、加噪后的水印提取能力。

### 挑战方向
- 可选实现 DCT 或 DWT 域嵌入。
- 可选设计盲水印算法，即提取时不依赖原始图像。

## 推荐技术路线
1. 先实现 DFT 非盲水印基础版本，保证能嵌入、恢复、提取。
2. 加入图像质量指标：PSNR、SSIM、MSE、NC/BER 等。
3. 做参数实验：不同嵌入强度 alpha 与不同水印尺寸。
4. 做攻击实验：JPEG、缩放、高斯噪声。
5. 如果时间允许，实现 DCT 盲水印作为加分模块。
6. 整理可复现实验脚本、输出图表、报告和 PPT。

## 阶段计划
| 阶段 | 状态 | 内容 | 产出 |
|---|---|---|---|
| Phase 1 | complete | 阅读作业要求，初始化本地 Git 仓库 | `.git/`、规划文件 |
| Phase 2 | complete | 搭建 Python 项目结构 | `src/`、`experiments/`、`outputs/`、`README.md`、`requirements.txt` |
| Phase 3 | complete | 准备数据集与示例图像 | 原图、水印图、数据说明 |
| Phase 4 | complete | 实现 DFT 水印嵌入与提取 | 可运行基础算法 |
| Phase 5 | complete | 实现质量评估与可视化 | PSNR/SSIM/NC/BER、频谱图、对比图 |
| Phase 6 | complete | 实现攻击测试 | JPEG、缩放、加噪实验结果 |
| Phase 7 | complete | 可选 DCT/DWT 或盲水印增强 | 加分算法模块 |
| Phase 8 | pending | 编写报告、PPT、最终打包 | 报告、答辩 PPT、提交压缩包 |

## 建议项目结构
```text
frequncy_domain_watermarking/
├── data/
│   ├── raw/                 # 原始测试图像
│   └── watermark/           # 水印图像或二值水印
├── src/
│   ├── dft_watermark.py     # DFT 嵌入/提取
│   ├── attacks.py           # JPEG/缩放/加噪攻击
│   ├── metrics.py           # 图像质量与提取质量指标
│   └── utils.py             # 图像读写、预处理、可视化辅助
├── experiments/
│   ├── run_basic.py         # 基础实验
│   ├── run_strength.py      # 嵌入强度实验
│   └── run_attacks.py       # 抗攻击实验
├── outputs/                 # 实验输出图像和表格
├── report/                  # 报告与 PPT 草稿
├── requirements.txt
└── README.md
```

## 错误记录
| 错误 | 尝试 | 处理 |
|---|---|---|
| 暂无 | - | - |

## 待确认
- GitHub 远程仓库名称、可见性（public/private）和是否使用 GitHub CLI 创建远程仓库。
- 小组人数、组号、组长姓名，用于最终提交命名与报告分工。
