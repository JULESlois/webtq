# TGQQ Round 2 Change Report（修复 + 聊天页改造）

基于 checkout：`e3730e10073c3fc02e1360e3513b70b176d6afec`（同 Round 1）。

## Round 2 目标

1. 修复 Round 1 遗留问题：flags 未门控、skin CSS 桌面泄漏、design scss 重复打包、未定义变量。
2. 按 `chat-hook-plan.md` 进入聊天页改造：chat header / bubbles / composer 皮肤化（CSS-only，零 renderer 重写）。

## 修复项

- **flag 门控**：`tqFlags` 现在真正生效。`shell/index.tsx` 按 `flag && mediaSizes.isMobile` 切换 body class：
  - `tq-dialog-skin` ← `dialogSkin`
  - `tq-chat-header` ← `chatHeader`
  - `tq-chat-bubbles` ← `chatBubbles`
  - `tq-chat-composer` ← `chatComposer`
  - 对应 4 个 skin scss 的根选择器全部改为 `body.is-tgqq.tq-*`。
- **Mobile Only**：所有 skin 仅在 <600px（`mediaSizes.isMobile`，tweb 原生断点）生效；桌面保持原 tweb UI。
- **CSS 去重**：还原 `src/scss/style.scss`（移除 4 个 @use），TGQQ 全部 CSS 收归 `src/tgqq/index.ts` 动态 chunk。
- **未定义变量**：`TqMobileShell.module.scss` 的 `--tq-bg-primary` → `--tq-surface-page`。
- **新 token**：`--tq-chat-page`（QQ 聊天页底色 light #ededed / dark #191919）、`--tq-bubble-incoming-meta` / `--tq-bubble-outgoing-meta`（气泡内时间/状态色，双主题可用）。

## 聊天页改造（本轮开启）

- `chat.ts`：chat 容器加 `is-tgqq-chat`（TW-UP-004），作为聊天页作用域锚点。
- `TqTopbar.scss`：`.chat { --chat-topbar-height: var(--tq-topbar-height) }`，顶部栏 52px 与气泡区 padding 保持同步；其余 QQ 头部样式沿用 Round 1 草稿。
- `TqChatBubble.scss`：`.bubbles-inner` 背景改用 `--tq-chat-page`（扁平灰底，盖住 wallpaper）；outgoing 时间/状态改用 meta token；气泡圆角/组角/无 tail/日期胶囊沿用 Round 1 草稿。
- `chatInput.scss`：composer 单行 QQ 重绘（白底圆角 plate、QQ 蓝 send、回复/提及样式），门控到 `tq-chat-composer`。
- `dialogSkin` 一并开启：会话列表 QQ 皮肤 + 未读角标等（Round 1 已写好但未生效的 CSS 现在激活）。

## 明确不做（按 chat-hook-plan 风险分级）

- **two-row composer**：`chat-input-control` 为 absolute 定位且 voice recording 状态依赖父 DOM，reparent/改 flow 风险高 → 本轮保持单行重绘，后续单独处理。
- **outgoing self avatar**：grouped bubble 需要组首/组中判断，风险中-高 → `chatOwnAvatar: false`，下一轮单独处理。
- 动画（bubble 出入场、composer 过渡）：本轮只做静态视觉。

## Round 1 遗留的隐藏问题（本轮发现并修复）

- **三个皮肤 .module.scss 从未生效**：`TqChatList/TqChatBubble/TqTopbar` 内容全部是 `:global(...)` 规则、没有任何导出的 local class，rolldown 将其视为无副作用模块直接摇树，产物 CSS 里根本没有这些规则（此前 typecheck/build 都通过，但皮肤是死的）。
- 修复：转为普通 `Tq*.scss` 并剥离 `:global()` 包装（机械转换），由 `src/tgqq/index.ts` 副作用引入；同时修正了 7 处被写反的 `:global(.bubble.is-out) &` 选择器（编译成 `bubble.is-out body...` 死规则），改为 `.bubble.is-out .reply` 等正确后代选择器。

## 验证

- `tsc 5.9.3 --noEmit`（需 `NODE_OPTIONS=--max-old-space-size=6144`）：通过。
- `pnpm build`：通过，dist 生成 `tgqq-*.js/css` chunk。
- 人工预览：必须用 <600px 宽度（浏览器设备模拟或窄窗口），桌面宽屏按设计保持原 tweb UI。

## 文件清单

Modified:
- src/components/chat/chat.ts
- src/tgqq/config/flags.ts
- src/tgqq/shell/index.tsx
- src/tgqq/shell/TqMobileShell.module.scss
- src/tgqq/design/light.scss / dark.scss / chatInput.scss
- src/tgqq/index.ts（皮肤 scss 引入更新）
- src/tgqq/components/TqChatList.scss / TqChatBubble.scss / TqTopbar.scss（.module.scss 转普通 scss，修复摇树）

Reverted:
- src/scss/style.scss（Round 1 的 4 个 @use 移除）

Docs:
- docs/tgqq/upstream-patches.md（TW-UP-004/005）
- docs/tgqq/round2-chat-report.md（本文件）
