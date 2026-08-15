# Round 10 — 聊天页改造：QQ9「+」附件底部面板（报告）

- 日期：2026-08-15
- 前置：Round 9 密度校准完成（round9-density-report.md）
- 循环：renderer hook（TW-UP-011）→ CSS 底部面板 → fixture → build/shoot（13 张）→ 自验 → codebuddy → 本报告

## 1. 本轮完成项

### 1.1 renderer 标记（TW-UP-011）
- `input.ts`：附件菜单（`.btn-menu`）创建后加 `tq-attach-menu` class（`onOpen` 回调里）。
- 用途：QQ9 皮肤只改附件菜单，不误伤消息右键等其他 `.btn-menu`。

### 1.2 QQ9 附件底部面板（`src/tgqq/design/chatInput.scss`）
- 手机（<601px）：`position:fixed` 贴底全宽，顶部圆角 16px，白底，
  `box-shadow: 0 0 0 100vmax rgba(0,0,0,.35)` 全屏遮罩（点遮罩=点页面，
  走 tweb 外部点击关闭逻辑）；面板 `z-index:1060`。
- 平板/桌面（≥601px）：居中浮层 `width:26rem`，四角 16px 圆角，底部 1.25rem。
- 网格：`flex-wrap` + 每项 25% 宽 = **4 列 × N 行**；图标 52px 圆形
  浅色底（8 色循环：#E8F2FF 蓝 / #FFF1E6 橙 / #EAF7EF 绿 / #F3EDFF 紫 /
  #FFECEF 红 / #E6F7FA 青 / #FFF8E1 黄 / #F0F4F8 灰），图标色深色同系；
  标签 11px 灰、间距 8px。
- 暗色模式：面板 #2F2F2F，遮罩 0.55。

### 1.3 fixture 与截图
- 新 `attach-panel.html`（基于 mobile-chat.html + `.btn-menu.top-right.tq-attach-menu.active`，
  8 项：相册/拍摄/文件/位置/红包/转账/语音通话/视频通话，inline SVG 图标）。
- `shoot.sh` 新增 `attach-panel`（390x844）与 `attach-panel-tablet`（900x700），共 13 张。

## 2. 验证矩阵（puppeteer computed-style + magick 像素）

| 检测项 | 期望 | 实测 | 状态 |
|---|---|---|---|
| 手机面板位置/尺寸 | 贴底全宽 | x0 y630 w390 h214，radius 16/16/0/0 | ✅ |
| 平板面板 | 居中 26rem | x242 y462 w416，radius 16 | ✅ |
| 4 列布局 | 每列 25% | 手机列宽 92px / 平板 98px，行距 89px | ✅ |
| 图标 | 52px 圆形 | 52×52，8 色 pastel 逐个核对 | ✅ |
| 标签 | 11px 灰 | 11px #5A5A5A | ✅ |
| 全屏遮罩 | 0.35 暗化 | 顶区 240→155（0.65x）；面板区保持 255 不透明 | ✅ |
| 面板不透明度 | 打开态 | `.active` 类 → opacity 1（tweb 原生 `.btn-menu` 默认 opacity 0） | ✅ |
| 暗色模式 | 面板 #2F2F2F | 规则就位（未截图） | ✅ |

## 3. codebuddy round10 评审（`/tmp/cb_round10_out.txt`）

**总体结论：面板符合 QQ9 底部弹出特征，全部核心项 PASS。** 手机贴底全宽
（x0-389 y630-843、顶角圆角 16px）、平板居中 416px、4×2 网格列距差 ≤1px、
图标 52px、遮罩压暗 ≈35%、面板纯白不透明——全部 PASS；无面板聊天页回归 PASS。

codebuddy 提出 4 个轻微项，核实/处理：
| # | codebuddy 反馈 | 核实 | 处理 |
|---|---|---|---|
| ① | 语音/视频图标底色过浅（与白面板边界不清） | ✅ 属实（#FFF8E1/#F0F4F8 过浅） | **已修**：加深为 #FFE9B8 / #E2EAF3，magick 实测 (255,234,187)/(227,236,245) |
| ② | 标签 9-10px < 11px | ⚠️ 部分属实（原 11px 偏小） | **已修**：标签统一 12px（puppeteer 验证 8 项全部 12px） |
| ③ | 图标色相映射建议（相册蓝/拍摄橙/文件绿/位置紫/红包红/转账青/语音黄/视频灰） | ✅ 当前 nth-child 映射已与建议一致 | 无需改 |
| ④ | 气泡文字 13-14px < 16px | ❌ 误报：codebuddy 量的是字形帽高；puppeteer 实测 font-size 16px / line-height 22.4px | 无需改 |

## 5. 已知限制 / 后续
- 遮罩为 box-shadow 扩散（无独立遮罩元素），点击遮罩落在页面上，
  由 tweb 外部点击关闭逻辑处理；若真机上发现关闭失效，再加 renderer 遮罩 div。
- 附件面板真机行为（按钮点击弹出/关闭、bot 附加项追加）需真机账号验证。
- 长尾：动态页真实图占位、出站自头像真机验证、顶栏图标描边、sendername 间距。

## 5. 已知限制 / 后续
- 遮罩为 box-shadow 扩散（无独立遮罩元素），点击遮罩落在页面上，
  由 tweb 外部点击关闭逻辑处理；若真机上发现关闭失效，再加 renderer 遮罩 div。
- 长尾：动态页真实图占位、出站自头像真机验证、顶栏图标描边、sendername 间距。
