# TGQQ Round 4 Change Report（聊天页精修 + 列表重大 bug 修复）

基于 checkout：`e3730e10073c3fc02e1360e3513b70b176d6afec`（同 Round 1-3）。

## Round 4 目标

在 Round 3 平板结构之上完成聊天页与列表的精修：选中态、outgoing 头像、气泡细节、
输入条，以及修掉 codebuddy 评审反复误报背后的**真实渲染 bug**（列表文字被裁剪）。

## 重大 bug 修复（本轮的真正主角）

### 1. 会话列表文字/角标被裁剪成 2–4px 细条

- **现象**：左列昵称只有 2px 高、预览文字 4px、时间完全不渲染、未读角标只剩顶部
  4px 红条。此前多轮 codebuddy 评审把「裁剪后的文字条」误读为「正常小字」，本轮
  像素级分析（逐行颜色 dump）才坐实。
- **根因链**：
  1. tweb `.row-row { height: 1.375rem }` 把行内容器锁死 22px，并把
     row-title / row-subtitle 当 grid item 挤压到 2–4px 高；
  2. tweb `.row-title / .row-subtitle { overflow: hidden }` 把溢出文字裁掉；
  3. 时间字段被 tweb 动画规则 `body.animation-level-2 .dialog-subtitle-badge
     { transform: scale(0) }` 隐藏，等 JS 加 `.is-visible` 才显示（fixture 无 JS）。
- **修复**（`TqChatList.scss`）：
  - `.row-row { height: auto !important; display: block !important }`，
    `.row-title / .row-subtitle { height: auto !important }`；
  - `.dialog-subtitle-badge { transform: none !important; opacity: 1 !important }`。
- **验证**：puppeteer 几何（title 22px / subtitle 20px / time 22x22 / badge 18x18 圆）
  + 像素（昵称/预览/时间/badge 完整渲染）全部通过；codebuddy 最终确认 10 行四项完整。

### 2. 聊天区三段重叠（顶栏 / 消息区 / 输入条）

- **现象**：消息区 viewport 被 tweb 的 `--chat-padding-top/bottom` 相对偏移推挤，
  底部与输入条重叠 52px，最后一条消息被输入条遮住一半。
- **修复**（`fixture.css`，fixture 专用）：`.topbar` 回文档流
  （`position: relative !important`）、`.bubbles-viewport` 清掉 tweb 的
  `top/bottom` 偏移；消息流 `.bubbles` 用 `flex-direction: column;
  justify-content: flex-end` 钉在底部（内容溢出时最新消息优先可见）。
- **验证**：topbar 0..52 / viewport 52..750 / input 750..820，三段无重叠；
  date pill 与最后一条消息完整可见。

### 3. 日期分隔条（date pill）不渲染

- **根因**：tweb `.bubbles:not(.has-sticky-dates) .bubble.is-date
  { visibility: hidden }`，等 JS 加类才显示。
- **修复**（`TqChatBubble.scss`）：`.bubble.is-date { visibility: visible !important;
  opacity: 1 !important }`，底色 `--tq-surface-secondary` → `--tq-surface-tertiary`
  提升与聊天背景的对比。
- **验证**：像素确认灰底胶囊 + 深色文字「今天 14:12」渲染。

## 设计改动（QQ9 对齐）

### 选中态：整行蓝 → QQ9 浅蓝 tint + 左侧蓝条

- 原实现整行 `#1296DB` 蓝底白字，被 codebuddy 两次误读为「蓝色头卡」；
  QQ9 移动/平板选中行为**浅蓝底 + 深色文字**（平板另有左缘竖条）。
- 新样式（`TqChatList.scss` + `light.scss` 新 token `--tq-chatlist-active-bg: #e8f4ff`）：
  `box-shadow: inset 3px 0 0 var(--tq-accent-primary)` 左蓝条 +
  浅蓝底 + 文字回深色（逐一覆盖 tweb 的 active 白字 `!important`）。
- 验证：像素 `(232,244,255)` 底 + `#1296DB` 3px 左条。

### Outgoing 头像：私聊不显示、群聊才显示

- QQ9 规范：私聊自己消息右侧**无**头像；群聊每条右侧有自己头像。
- CSS-only 无法区分单聊/群聊 → `chat.ts` 增加
  `this.container.classList.toggle('is-tgqq-group', isLikeGroup)`（TW-UP-007），
  `TqChatBubble.scss` 头像规则门控到 `.chat.is-tgqq-chat.is-tgqq-group`。
- 头像仍是渐变圆占位（真实照片需 renderer hook，Red 待办）；单聊下不再出现
  「占位符感」的重复圆。

### 气泡细节（QQ9 特征）

- **小尾巴**：组首气泡加 5px 平角三角（incoming 左上白、outgoing 右上绿），
  替代 tweb 的 Telegram 风格 SVG tail（继续 `display:none`）。
- **圆角方向**：组首/组尾的「尖角」由 8px 收成 4px（`--tq-radius-xs`），
  指向发送者一侧，符合 QQ9 气泡方向感。
- **最大宽度**：`--tq-bubble-max-width: min(70%, 540px)`，宽屏不再无限伸展
  （QQ9 平板贴边对齐，不做居中）。

### 其他

- 聊天背景 `--tq-chat-page: #ededed` → `#f0f4f8`（QQ9 蓝灰）。
- fixture：列表补到 10 行、消息补到 8 条；底部导航四 tab、视频通话、输入条
  （表情/附件/发送）emoji 全部换内联 SVG（chromium 无彩色 emoji 字体，
  📹 曾渲染成打印图标）。

## 验证

- `tsc 5.9.3 --noEmit`：通过。
- `vite build`：通过。
- fixture 几何（puppeteer，`docs/tgqq/fixtures/`）：

  | 项目 | 结果 |
  |---|---|
  | 左列 10 行（title/sub/time/badge） | 22/20/22x22/18x18 全部正常 |
  | 选中行 | 浅蓝底 + 3px 左蓝条 + 深色文字 |
  | 聊天三段（topbar/viewport/input） | 0..52 / 52..750 / 750..820 无重叠 |
  | 气泡 | 组首尾巴（白/绿三角）、尖角 4px、max-width min(70%,540px) |
  | 日期 pill | 常显，灰底 + 深色文字 |

- codebuddy 读图评审 4 张截图（三轮迭代）：
  - 第一轮：确认选中态/头像/图标/背景/气泡宽度修复生效；
    误报「预览文字方块化」（实为裁剪 bug 的 AI 幻觉，本轮已根除）。
  - 第二轮：确认列表四项完整、聊天三段无重叠；
    误报「日期条缺失」（实为 visibility:hidden，本轮已修）。
  - 最终：完成度 ~90%，剩余仅「在线」字色、宽屏留白等可推迟项。

## 已知（后续轮）

- 私聊 incoming 对方头像：QQ9 单聊在组首显示对方头像，tweb 私聊无头像渲染 →
  需 renderer hook（bubbles.ts 私聊 createAvatar），Red 待办。
- 输入条「+」按钮：需改 `input.ts` renderer，Yellow 待办。
- 群聊 outgoing 头像：真实照片需 renderer hook，Red 待办。
- 平板四 tab 右侧二级页（频道/联系人/动态）→ 后续轮。

## 文件清单

Modified:
- src/components/chat/chat.ts（`is-tgqq-group` class，TW-UP-007）
- src/tgqq/components/TqChatList.scss（选中态、row 高度解锁、时间常显）
- src/tgqq/components/TqChatBubble.scss（头像门控、尾巴、圆角、date 常显）
- src/tgqq/design/light.scss（`--tq-chatlist-active-bg`、聊天背景）
- src/tgqq/design/tokens.scss（气泡最大宽度）
- docs/tgqq/fixtures/（tablet.html / mobile.html / fixture.css / shoot.sh / shots/）
- docs/tgqq/upstream-patches.md（TW-UP-007）

New:
- docs/tgqq/round4-chat-report.md（本文件）

上游改动（累计 Round 1-4，全部 Yellow）：
- src/pages/bootstrapIm.ts（TW-UP-001）
- src/lang.ts + src/scripts/out/langPack.strings（TW-UP-002/003）
- src/components/chat/chat.ts（TW-UP-004：is-tgqq-chat；TW-UP-007：is-tgqq-group）
