# Design

种子版（pre-implementation seed）。webapp 有真实代码后可用 `/impeccable document` 重新扫描生成。

## Theme

明亮学术纸感 × 北美大厂产品质感。像一篇排版精致的论文变成了网站：真灰白底、近黑墨字、墨绿主色、衬线大标题。冷静、精确、可信。唯一的浓烈时刻是叙事第 7 幕的整屏墨绿 Drenched 过渡段。

## Color

OKLCH 全程。策略：Restrained 为基底，叙事高潮一处 Drenched。

| Token | 值（基准，可微调） | 用途 |
|---|---|---|
| `--bg` | `oklch(0.97 0.003 170)` | 页面底色（真灰白，微偏品牌绿色相；禁奶油/米黄） |
| `--surface` | `oklch(0.995 0.002 170)` | 卡片/面板 |
| `--ink` | `oklch(0.22 0.01 170)` | 正文与标题 |
| `--ink-muted` | `oklch(0.45 0.015 170)` | 次要文字（对灰白底仍 ≥4.5:1） |
| `--brand` | `oklch(0.45 0.09 170)` | 墨绿主色：主按钮、当前选中、链接、数据高亮 |
| `--brand-deep` | `oklch(0.32 0.07 172)` | Drenched 段落底色、hover 深化 |
| `--line` | `oklch(0.90 0.004 170)` | 分隔线/描边 |
| 语义色 | 成功=brand；错误 `oklch(0.55 0.19 25)`；警告 `oklch(0.70 0.15 85)` | 状态反馈 |

对比度红线：正文 ≥4.5:1，大字 ≥3:1，placeholder 同 4.5:1。

## Typography

- **Display / 标题**：Noto Serif SC（中文）+ STIX Two Text（西文），weight 600–700
- **正文 / UI**：系统无衬线栈 `-apple-system, "PingFang SC", "Microsoft YaHei", system-ui, sans-serif`
- **数据 / 指标**：正文族的 tabular-nums，不为"技术感"引入 mono
- 桌面标题用 clamp() 流式缩放，上限 ≤5rem；正文行长 ≤72ch；h1–h3 加 `text-wrap: balance`

## Spacing & Layout

- 8px 基础网格；区块间距用 clamp() 流式呼吸，密集分组与大留白交替制造节奏
- 叙事段：左文右图两栏，右侧画面 sticky pinned；≤768px 退化为纵向静态分段
- 工具区：内容宽度上限 1120px；表单控件统一词汇表（同形状、同焦点环）
- z-index 语义梯度：dropdown < sticky < modal-backdrop < modal < toast < tooltip

## Components

每个交互组件必须齐 default / hover / focus / active / disabled / loading / error 七态。

- 主按钮：墨绿实心，白字；次按钮：墨色描边幽灵款
- 上传区：虚线描边 + 拖入高亮（brand 色）；加载用骨架屏不用居中 spinner
- 指标展示：论文表格式的精确排版（表格线极细），数字滚动计数出场
- 空状态：引导性文案 + 一键示例图入口，不出现"暂无数据"

## Motion

- 150–250ms，指数缓出（ease-out-quart/expo）；无弹跳
- 滚动叙事（GSAP ScrollTrigger）是全站唯一大型编排；其余动效仅表达状态变化
- `prefers-reduced-motion: reduce`：叙事呈现为静态分节，过渡改为交叉淡化

## Bans（本项目明确规避）

渐变文字 / 玻璃拟态 / 侧边彩条 / hero-metric 模板 / 同构卡片阵列 / 每节 uppercase eyebrow / 01·02·03 编号脚手架 / 奶油底色 / 杂志式 editorial 装腔 / 装饰性 mono 字体。
