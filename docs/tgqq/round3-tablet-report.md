# TGQQ Round 3 Change Report（平板结构 + 皮肤修复）

基于 checkout：`e3730e10073c3fc02e1360e3513b70b176d6afec`（同 Round 1/2）。

## Round 3 目标

按 `round3-tablet-plan.md`：宽屏（≥600px）改为 **QQ 平板结构** —— 左侧一列呈现
类手机主页（会话列表 + 底部四 tab），右侧为独立聊天窗。皮肤门控从 `isMobile` 放宽到
全部宽度（<600px 保持手机形态，≥600px 为平板形态，桌面三栏由本方案定义）。

## 实现

### 平板结构（新）

- `src/tgqq/components/TqTablet.scss`（新文件，`src/tgqq/index.ts` 引入）：
  - `.tq-shell` 固定定位到左列 footprint（`width: var(--left-column-visual-width)`），
    底部导航视觉上收进左栏底部，宽度与左栏一致。
  - 600–925px（tweb floating drawer 区间）：`#column-left` 拉回文档流
    （`position: relative; transform/opacity none !important`），
    `#column-center` 用 `inset-inline-start: var(--left-column-visual-width)` 并排，
    替代原 translateX 滑入滑出；隐藏 folders sidebar。
  - >925px（tweb docked 区间）：列布局沿用 tweb 原生，仅套皮肤 + 隐藏 folders
    sidebar 视觉侵入 + 平板下隐藏 topbar 返回键。
- `src/tgqq/config/flags.ts`：新增 `tablet: true` 开关。
- `src/tgqq/shell/index.tsx`：
  - skin 门控从 `flag && isMobile` 放宽为 `flag`（is-tgqq 即生效）。
  - 新增 body class `tq-tablet`（`tqFlags.tablet && !mediaSizes.isMobile`，
    在 `changeScreen / resize / tab_changing` 时同步）。

### 本轮发现并修复的真实皮肤 bug

- **topbar 背景被 tweb 压掉**：tweb `.topbar { background: var(--surface-color) !important }`
  会盖掉 QQ 皮肤 → `TqTopbar.scss` 改为 `background: var(--tq-surface-primary) !important`
  （主规则 / search-top-active / dark 三处）。
- **chatlist 行背景**：tweb 用 `background: var(--background) !important` 机制 →
  `TqChatList.scss` 改为驱动 `--background` 自定义属性（默认白 / hover 浅灰 / active 蓝）。
- **气泡时间被 tweb 隐藏**：`.bubble .time` 默认 `display: none` →
  `TqChatBubble.scss` 改为 `visibility: visible !important`。
- **在线状态文字**：tweb 青色 `#1296db` → `--tq-text-secondary` 灰（QQ9 顶栏风格）。
- **搜索框圆角**：`--tq-radius-sm` → `--tq-radius-xl`（QQ 胶囊）。
- **`.bubbles` 计数器 inset**：tweb `#column-center .bubbles`（ID 特异性）在 docked
  区间写对称 counter-inset，宽屏聊天区右侧出现 ~180px 灰边 →
  `TqTablet.scss` 用 `inset-inline: 0 !important` 强制撑满右栏。
- **气泡呼吸空间**：`--chat-bubbles-padding: 1rem`（tweb 原生机制，≥600px 默认 0px），
  聊天内容距右栏左右各 16px，避免贴边。

## 验证

- `tsc 5.9.3 --noEmit`：通过。
- `vite build`：通过，`dist/tgqq-*.css` 含全部 `tq-tablet` 规则。
- fixture 几何（chromium headless + puppeteer，`docs/tgqq/fixtures/`）：

  | 窗口 | #column-left | #column-center | .bubbles | 结果 |
  |---|---|---|---|---|
  | 900x700 | 360 | 360..900 (540) | 360..900 (540) | ✅ 并排 |
  | 1180x820 | 360 | 360..1180 (820) | 360..1180 (820) | ✅ 占满右栏 |
  | 1440x820 | 360 | 360..1440 (1080) | 360..1440 (1080) | ✅ 占满右栏 |

- 像素抽查（magick）：左列 active 会话行整行 `#1296DB` 蓝底白字，正确渲染。
- codebuddy 读图评审 4 张截图（mobile/tablet-mid/tablet-wide/tablet-xwide）：
  - 无错位 / 重叠 / 缺失 / 空白异常；顶栏、气泡左右配色、圆角、时间戳、双勾、
    回复引用、输入条（表情/加号/蓝色发送）全部正常。
  - 评审误报 1 条（“选中态缺失”）：实测 active 行蓝底白字已渲染，属评审幻觉。
  - 其余建议（气泡阴影、输入条居中、在线状态绿色等）与既有 QQ9 设计决策冲突，
    维持现状不采纳（QQ9 为扁平白气泡 + 1px 描边、顶栏灰色在线状态、输入条全宽）。

## 已知（后续轮）

- 平板下频道/联系人/动态三 tab 的右侧联动二级页内容 → 后续轮。
- two-row composer、outgoing self avatar → Yellow，沿用 Round 2 结论。
- `bubbles.ts` / `input.ts` renderer、MTProto / storage / auth、`updateColumnWidths.ts`
  逻辑一律未动（Red）。

## 文件清单

New:
- src/tgqq/components/TqTablet.scss
- docs/tgqq/round3-tablet-plan.md
- docs/tgqq/round3-tablet-report.md（本文件）
- docs/tgqq/fixtures/（tablet.html / mobile.html / css / shoot.sh / shots/）

Modified:
- src/tgqq/shell/index.tsx（皮肤门控放宽 + `tq-tablet`）
- src/tgqq/config/flags.ts（`tablet: true`）
- src/tgqq/index.ts（引入 TqTablet.scss）
- src/tgqq/components/TqChatList.scss / TqChatBubble.scss / TqTopbar.scss（上述皮肤 bug 修复）
- docs/tgqq/upstream-patches.md（TW-UP-006，见下）

上游改动（累计 Round 1-3，全部 Yellow）：
- src/pages/bootstrapIm.ts（TW-UP-001）
- src/lang.ts + src/scripts/out/langPack.strings（TW-UP-002/003）
- src/components/chat/chat.ts（TW-UP-004）
