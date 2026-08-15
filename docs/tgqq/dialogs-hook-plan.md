# TGQQ Dialogs Hook Plan（第一轮调查输出，未实施）

基于当前 checkout：`e3730e10073c3fc02e1360e3513b70b176d6afec`。

## 1. QQ 会话列表视觉可以纯 SCSS 完成的部分

- 行高、内边距、间距（avatar/title/subtitle/time 之间的 4px 网格）。
- title / subtitle / time 的字号、字重、颜色（semantic tokens）。
- 头像圆角、边框。
- 分隔线（1px，`--tq-surface-secondary`）。
- 点击态、按压反馈、行背景。
- 未读角标重定位（见 §3）。
- 结论：**绝大多数布局与视觉可纯 SCSS 完成**，通过 `body.is-tgqq .chatlist-chat` 作用域（flags `dialogSkin` 门控）。

## 2. unreadAvatarBadge 的 DOM 在哪里

- `DialogElement.dom.unreadAvatarBadge`（`src/lib/appDialogsManager.ts:486` `createUnreadAvatarBadge()`）。
- DOM：`div.dialog-subtitle-badge.badge.badge-<size>.avatar-badge`，**append 到头像元素 `dom.listEl` 内部**。
- 条件创建由现有 unread state 驱动，无需重写。

## 3. unread badge → 头像右上（不重写 unread state）

- 头像元素是角标的父容器：只需 CSS 使头像元素 `position: relative`（或依赖现有 relative），并把 `.avatar-badge` 定位到 `top/right`（负偏移到头像右上角）。
- 现状 `.avatar-badge` 已存在于 DOM 且与 unread count 同步 —— 本轮/下一轮 **零 TS 改动** 即可实现视觉重定位。
- 风险：`.avatar-badge` 目前在 tweb 中可能已有默认定位（需在实施时核对，避免影响现有桌面端）；用 `body.is-tgqq` 作用域隔离。

## 4. title / subtitle / time DOM 是否足以实现 QQ layout

- 是。`DialogElement` 提供：
  - title（peer 名）
  - `.dialog-title-details`（右侧时间/状态区）
  - `.dialog-subtitle`（`dom.subtitleEl`，含预览 + 各种 badge）
  - `.message-time`
- QQ 会话行（标题+时间 一行，预览 一行）可完全由这些现有节点的 CSS 重排实现。

## 5. 是否需要给 DialogElement 添加 TGQQ class

- 推荐：需要（一行，flags 门控）。
- 位置：`appDialogsManager.ts:366` `li.classList.add('chatlist-chat', ...)` 追加 `is-tgqq-chatlist-item`（仅 `tqFlags.dialogSkin` 为 true 时）。
- 目的：避免深层 selector，提供稳定 presentation hook（符合 1.md §26）。
- 替代：若不想动 TS，可先用 `body.is-tgqq .chatlist-chat` 完成 90%；class hook 留给需要区分状态（pin/mute/mention）时再加。

## 6. 完全不需要改 TypeScript 的地方

- 未读角标重定位、预览/时间布局、分隔线、间距、行内 icon 配色 —— 全部 CSS。
- 需要 TS 的地方仅：`is-tgqq-chatlist-item` class hook（可选）、未来“会话置顶/分组”等新数据语义（下一轮 Metadata，本轮禁止）。

## 结论

- 下一轮 QQ Conversation 列表：**SCSS-first**；只加 1 个 class hook；不重写 `DialogElement`、不复制 chat list DOM、不动 unread state。
