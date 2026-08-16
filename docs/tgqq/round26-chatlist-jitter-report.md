# TGQQ Round 26: 聊天列表错位/抖动根因分析与修复

日期：2026-08-16
基准：`fdd05f3`（Round 25 关于QQ + 分组校准，用户已推送）

## 结论

聊天列表"严重错位/抖动"已修复，验证方式：
- puppeteer 真实 DOM 页面（`a.row...chatlist-chat.chatlist-chat-bigger.row-big` + `row-title-row`/`row-subtitle-row`/`row-media-bigger`）：10 行全部恒定 74px；增删未读徽章、hover 均不改变行高。
- fixture 截图像素采样：mobile/tablet 明暗 4 张，分隔线间距全部精确 74px（195,269,343,417,491,565,639,713,787 / 179,253,327,401,475,549,623）。

## 根因（均为"fixture 与真实 tweb DOM 不一致"导致的假象）

真实聊天行 DOM（`Row` + `DialogElement`，`src/components/row.ts` + `src/lib/appDialogsManager.ts`）：

```
a.row.no-wrap.row-with-padding...chatlist-chat.chatlist-chat-bigger.row-big
├─ div.row-row.row-subtitle-row.dialog-subtitle.has-multiple-badges   （先入 DOM）
│    ├─ div.row-subtitle > span.user-last-message
│    └─ 徽章：dialog-subtitle-badge badge badge-22 {dialog-subtitle-badge-unread
│       | mention mention-badge dialog-subtitle-badge-mention | reaction-badge
│       | poll-vote-badge | dialog-subtitle-badge-pinned}（avatar-badge 挂 li 上）
├─ div.row-row.row-title-row.dialog-title（order 翻转后视觉在上）
│    ├─ div.row-title.user-title > span.peer-title [+ span.dialog-muted-icon]
│    └─ div.row-title.row-title-right.dialog-title-details > message-status + message-time
└─ canvas.dialog-avatar.row-media.row-media-bigger（绝对定位）
```

旧覆盖是按 fixture 简化结构（单个 `.row-row` 包 title+subtitle）写的，与真实结构错位：

1. **文字被头像压住**：上游 `.chatlist-chat.row-with-padding{padding-inline-start:4.5rem!important}`（72px）特异性 (0,2,0)!important 压过旧的 12px 覆盖；同时头像按上游 `.row-media-bigger` 绝对定位在 9px/54px。结果文字列从 12px 起，直接叠在头像上。
2. **行结构纵向堆叠**：旧 `.row-row{display:block!important}` 把真实行的 `.row-row.row-title-row`/`.row-row.row-subtitle-row` 变成块级堆叠 → 时间掉到标题下方、字号 16px（上游 `.chatlist-chat .row-title{font-size:16px!important}` 压住 12px 覆盖）。
3. **徽章撑高行 → 抖动**：真实未读徽章类名是 `.dialog-subtitle-badge-unread`（不是 `.badge.unread`），旧的 `.badge.unread` 规则完全不匹配；徽章留在副标题流内（`.dialog-subtitle-badge{display:block!important}`），有未读/提及/置顶的行 74→95px，增删徽章时整列跳动。
4. **垂直内边距被清零**：上游 `.row.no-wrap{padding-top/bottom:0!important}`，QQ9 的 12px 节奏丢失。
5. **徽章被动画隐藏**：上游 `body.animation-level-2 .dialog-subtitle-badge{transform:scale(0)}` 直到 JS 加 `.is-visible`；覆盖层未包含 `.dialog-subtitle-badge` 时徽章不可见。

## 修复（src/tgqq/components/TqChatList.scss + tokens.scss）

- 行结构按真实 DOM 重写并整体收进 `.chatlist-chat` 作用域：
  - `.row-title-row`/`.row-subtitle-row` → `display:flex!important`、align-items:center；标题行 space-between；副标题行 gap + margin-top 4px。
  - `.user-title` flex:1 + ellipsis + `font-size:17px!important`；`.row-subtitle` flex:1 + `13px!important`；`.dialog-title-details` `11px!important` 右对齐。
- 文本列偏移：`.chatlist-chat.row-with-padding{padding-inline-start:76px!important}`（=12+52+12，新增 token `--tq-chatlist-gap:12px`）；`.chatlist-chat.no-wrap` 恢复上下 12px。
- 头像：`.chatlist-chat .dialog-avatar` → `position:absolute!important; top:50%; translateY(-50%); inset-inline-start:12px!important; 52×52!important`（压上游 `.row-media-bigger` 54px@9px）。
- 徽章全部绝对定位到头像右上角（`top:8px; left:calc(12px+52px-10px)`），从流内移除：
  `.dialog-subtitle-badge-unread / .mention-badge / .dialog-subtitle-badge-mention / .reaction-badge / .dialog-subtitle-badge-reaction / .poll-vote-badge / .dialog-subtitle-badge-pollvote / .dialog-subtitle-badge-pinned`；`avatar-badge` 左上；统一 `transform:none!important; opacity:1!important` 防 scale(0) 隐藏。
- 修正裸 `.mention`（会命中消息气泡内 @提及）→ `.mention-badge`/`.dialog-subtitle-badge-mention`（codebuddy F2）。

## codebuddy 审查（Round 26）

审查报告：`/tmp/codebuddy_chatlist_report.txt`。结论 中等偏上，阻塞项 F2/F3，全部修复：

- F1 标题字号未覆盖 !important → 已加（R1）
- F2 裸 `.mention` 外溢破坏气泡 @提及 → 全部徽章规则收进 `.chatlist-chat`，裸类改专属类（R2/R3）
- F3 置顶徽章仍在流内会抖动 → 加入绝对定位清单（R4）
- F4 `.badge.unread` 死代码 → 移除裸选择器（R3）
- F5 avatar-badge 缺 position:absolute!important → 已补（R5）
- F7 列表类泄漏到其它区域 → 行结构规则整体收进 `.chatlist-chat`（R6）

## Fixture 同步

- `mobile.html`/`tablet.html`：聊天行改为真实 DOM（subtitle 行先入 DOM、`dialog-title`/`dialog-subtitle has-multiple-badges`、`dialog-avatar row-media row-media-bigger`），并补充 pinned(📌)、mention(@)、avatar-badge 三类用例（R7）。
- `fixture.css`：删除按旧简化 DOM 手写的 chatlist cosmetics（`flex-direction:row`、`.badge.unread` 等），改由 tgqq.css 统一驱动。
- 截图：mobile/tablet 明暗 + 空态等 chatlist 相关图已重拍；与聊天列表无关的截图（channels/dynamics/voice 等）字节级无变化，未纳入本次提交。

## 验证数据

- 真实 DOM 页（/tmp/qqtest/real-list.html，内联 dist css）：10 行高度 `[74×10]`；badge 增删前后与 hover 后仍 `[74×10]`。
- badge 位置（tablet）：unread (54, row+8, 16×16)；mention (54, row+8, 18×18)；avatar-badge (52, row+6, 26×26)；pinned (14, row+6, 22×22)。
- 截图分隔线间距：mobile 8 个 74px 间隙、tablet 6 个 74px 间隙（明/暗一致）。
