# TGQQ Chat Hook Plan（第一轮调查输出，未实施）

基于当前 checkout：`e3730e10073c3fc02e1360e3513b70b176d6afec`。
本轮 Chat 零视觉改动；以下为下一轮方案分级。

## Chat Root

- 建立者：`Chat` 类（`src/components/chat/chat.ts`），由 `AppImManager` 实例化（`appImManager.ts:2945`），容器 `div.chat.tabs-tab` 挂到 `#column-center`。
- `is-tgqq-chat` class：最安全加在 chat.ts `:250` `this.container.classList.add('chat', 'tabs-tab')` 处（一行，flags `chatHeader/chatBubbles` 门控），或挂在 `#column-center` 上由 CSS 派生。
- 分类：**small DOM hook**（低风险）。

## Chat Header（topbar）

- 来源：`src/components/chat/topbar.ts`（title/subtitle/typing/back/profile action 均在其中）。
- title DOM：topbar 内 peer title；subtitle：typing 状态/在线状态；back button / menu action 均存在。
- 方案：**CSS only**（布局/间距/字号）+ 可选 class hook（`is-tgqq-chat` 后代）覆盖颜色与安全区。
- 风险：低。不做 DOM reparent。

## Bubble

- 来源：`src/components/chat/bubbles.ts`（`ChatBubbles`）。
- 类名：`is-out` / `is-outgoing` / `is-in`；bubble 元素由 `getBubble(fullMid)` 管理；grouped messages、date divider、reply block、reaction block 均在现有 bubble DOM 内。
- 方案：**CSS + class hook**（`is-tgqq-chat .is-out` 等），不重写 renderer。
- 风险：中（bubble 动画/测量依赖既有 DOM 结构；下一轮先做静态视觉，动画后置）。

## Own Avatar（outgoing self avatar）

- 调查结论（需下一轮验证细节）：bubble renderer 知道 `isOut`（`bubbles.ts:935/2752`），但 outgoing bubble 当前**没有 self avatar DOM**。
- 群聊 outgoing 有 sender 信息；私聊无头像位。
- 方案：presentation-only decorator —— 在 `is-tgqq-chat` 作用域下，通过 CSS 在 bubble 行首插入固定尺寸占位（或由 `bubbles.ts` 在渲染 `is-out` 时 append 一个 `avatar` 装饰节点，最小 DOM hook）。
- 风险：中-高（grouped bubble 需要判断组首/组中，避免每行都插头像）；**下一轮单独处理，本轮只记录**。

## Time Divider

- 现有 date divider 已存在（`dateBubble.ts`）。
- 方案：**CSS only**（居中胶囊样式）。
- 风险：低。

## Composer 特别分析（`src/components/chat/input.ts`）

- 根 class：`chat-input`；`inputContainer` 承载输入区；控件 class `chat-input-control`。
- 两行结构：`inputContainer` 内已有 rows 体系（`rowsWrapperWrapper` 等），**CSS flex-direction/换行即可形成两行**，无需复制 DOM。
- Send / Emoji / voice / attach 均为现有按钮控件（`chat-input-control`、`btn-record-cancel` 等），可经 CSS order/flex 移动位置。
- 风险点：
  - voice recording 控件（`btnRecord` 相关）动画/状态依赖 `inputContainer` 父结构 —— 移动可能破坏录音态（高）。
  - 附件菜单（attach）与 send menu 是 popup/浮层，reparent 风险高 —— 保持原位，只做视觉排列。
  - Gallery/Camera/File 快捷入口：已有 attach 行为可调用（`chat-input-control` 按钮 + 现有 menu），下一轮优先复用。
- 结论：composer 两行布局 **CSS-only 可行**；但 voice/attach 相关控件**禁止 reparent**（状态依赖父 DOM），下一轮以 flex order 为主。

## 禁止重写（absolutely must not be rewritten）

- `bubbles.ts` message renderer、`input.ts` ChatInput 逻辑、`chat.ts` 生命周期、MTProto/message storage。

# Round 2 实施记录（2026-08-14）

## 已完成

- Chat root：`chat.ts:250` 增加 `is-tgqq-chat`（TW-UP-004）。
- Chat Header：`TqTopbar.module.scss` 激活（`tq-chat-header`），`.chat` 的 `--chat-topbar-height` 同步为 52px。
- Bubble：`TqChatBubble.module.scss` 激活（`tq-chat-bubbles`），扁平灰底 + 白/绿气泡 + 无 tail + 日期胶囊。
- Composer：`chatInput.scss` 激活（`tq-chat-composer`），单行 QQ 重绘（plate/send/attach/emoji/reply）。
- 皮肤门控：`tq-*` body class 按 flag + `mediaSizes.isMobile` 切换；桌面不生效。

## 仍推迟（与 Round 1 判断一致）

- two-row composer：录音态依赖父 DOM，CSS-only 两行风险高 → 待专项。
- outgoing self avatar：grouped 组首判断 → `chatOwnAvatar: false`。
- bubble 动画、回复/转发手势视觉。
