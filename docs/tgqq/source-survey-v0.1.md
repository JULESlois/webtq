# TGQQ Source Survey v0.1

Current checkout SHA:
e3730e10073c3fc02e1360e3513b70b176d6afec

## App bootstrap

- 入口 `index.html` → `src/index.ts`（模块入口）。
- `src/index.ts`：初始化账号/auth 流程；已登录时 `bootstrapIm()`（`src/pages/bootstrapIm.ts`）显示 `#page-chats` 并启动 IM。
- `bootstrapIm()` 是登录成功与直接登录两条路径的汇聚点（幂等），也是 TGQQ 挂载点。
- 样式入口：`src/materialize.scss` + `src/scss/style.scss`。

## Top-level navigation

- `APP_TABS` 枚举（`src/lib/appImManager.ts:198`）：`CHATLIST / CHAT / PROFILE`。
- `AppImManager.selectTab(id)`（`:2874`）切换；`document.body.classList.toggle('is-left-column-shown', id === CHATLIST)`。
- `selectTab` 内调用 `(window as any).onImTabChange?.(id)` 钩子，并 dispatch `tab_changing` 事件。
- `setPeer() / setInnerPeer()`（`src/lib/appImManager.ts`）保持原语义，TGQQ 不新增 chat router。

## CHATLIST owner

- `AppImManager`（`src/lib/appImManager.ts`），列容器 `columnEl = #column-center`。
- 左侧聊天列 `#column-left`（sidebar-left），由 `appSidebarLeft`（`src/components/sidebarLeft/index.ts`）管理。

## Chat list owner

- `AppDialogsManager`（`src/lib/appDialogsManager.ts`），`chatsContainer = #chatlist-container`。
- 每个 filter 一个 `Scrollable`，容器类 `tabs-tab chatlist-parts folders-scrollable` —— 聊天列表的 scroll owner。
- 列表项由 `DialogElement` 创建：`li.chatlist-chat.chatlist-chat-<avatarSize>`。

## Dialog element owner

- `DialogElement`（同文件 `:366` 起）：容器 `.row-big/.row-small`；元素含 avatar（`dom.listEl`）、subtitle 行（`.dialog-subtitle`，`dom.subtitleEl`）、时间 `.message-time`、详情 `.dialog-title-details`。
- 未读角标两类：subtitle 角标 `dialog-subtitle-badge-unread`；头像角标 `avatar-badge`（`dom.unreadAvatarBadge`，挂在 avatar 元素内，`createUnreadAvatarBadge` `:486`）。
- pinned / mentions / reactions badge 均挂到 `subtitleEl`。

## Dialog click flow

- 列表点击 → `DialogElement` 内部 handler → `appImManager.setPeer(...)` → `CHAT`（未改动，见 dialogs-hook-plan）。
- TGQQ 不做 interception，不改点击语义。

## Mobile/desktop responsive owner

- `src/helpers/mediaSizes.ts`：`ScreenSize`（mobile=600 边界）、`mediaSizes.isMobile`、`changeScreen` / `resize` 事件。
- `AppImManager` 内部大量使用 `mediaSizes.activeScreen === ScreenSize.mobile`。

## Contacts source

- 联系人实现在 `src/components/sidebarLeft/tabs/contacts.tsx`（Solid tab），数据经 `appContactsManager`（`src/lib/appManagers/appContactsManager.ts`）等 managers。
- 本轮未接入，仅占位（见 1.md §15）。

## Chat owner

- `Chat` 类（`src/components/chat/chat.ts`），由 `AppImManager` 实例化（`:2945`），容器 `div.chat.tabs-tab` 挂到 `#column-center`。

## Bubble owner

- `src/components/chat/bubbles.ts`（`ChatBubbles`）；bubble class：`is-out` / `is-outgoing` / `is-in`。
- 本轮零修改。

## Composer owner

- `ChatInput`（`src/components/chat/input.ts`），根 class `chat-input`，`inputContainer` 承载 rows/controls（`chat-input-control`）。
- 本轮零修改，仅输出调查（chat-hook-plan）。

## Theme owner

- `src/helpers/themeController.ts`：`document.documentElement.classList.toggle('night', isNight)` —— 深色主题类 `html.night`。
- TGQQ design tokens 在 `.is-tgqq` 上定义，深色用 `html.night .is-tgqq` 覆盖。

## Safe TGQQ mount point

- `body.is-tgqq`（作用域根，flags 开启时由 `initTgqq()` 添加）。
- Shell 根 `div.tq-shell` 挂到 `#page-chats` 末尾（登录页不存在该容器，天然隔离）。
- 显示条件：`tqFlags.shell && mediaSizes.isMobile && body.is-left-column-shown`（= CHATLIST）。
- 生命周期：`initTgqq()` 在 `bootstrapIm()` 内 `has-auth-pages` 移除后调用；监听 `tab_changing` + `changeScreen` + `resize`。

## Expected next-round hook points

- DialogElement 增加 TGQQ class（一行，flags 门控）→ 会话列表 skin。
- `avatar-badge` 纯 CSS 重定位 → 未读角标右上。
- Chat 容器 `is-tgqq-chat` class + topbar（`src/components/chat/topbar.ts`）→ 聊天头。
- `chat-input` 控件 DOM reorder（CSS only）→ 两行 composer。
- `bubbles.ts` outgoing bubble 装饰（presentation-only）→ 自己头像。

## Files that should remain untouched (Red)

- `src/lib/mtproto/**`、`src/lib/mainWorker/**`、`src/lib/storages/**`、`src/lib/apiManager*`、auth（`src/pages/mountAuthFlow.tsx` 等）、`src/components/chat/bubbles.ts`、`src/components/chat/input.ts`、calls/media pipeline。

## Green / Yellow / Red 分类

### Green（本轮新增）
- `src/tgqq/**`（全部）。

### Yellow（最小侵入）
- `src/pages/bootstrapIm.ts`：mount 调用（1 行 + import）。
- `src/lang.ts`：TGQQ i18n 键。
- `src/scripts/out/langPack.strings`：由 lang watcher 自动再生成（非手改）。

### Red（本轮不碰）
- MTProto、message semantics、storage、auth、worker internals、upload/download、calls（与上文 Red 文件一致）。
