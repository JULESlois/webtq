# TGQQ Upstream Patch Ledger

## TW-UP-001

File:
src/pages/bootstrapIm.ts

Purpose:
Mount TGQQ mobile shell（在 `has-auth-pages` 移除后调用 `initTgqq()`，覆盖直接登录与 auth 登录两条路径）。

Type:
Yellow

Why upstream modification is necessary:
TGQQ Shell 需要稳定的挂载时机（IM 已就绪、auth 页已卸载）；`bootstrapIm()` 是唯一幂等汇聚点。

TGQQ fallback:
`tqFlags.shell = false` 时 `initTgqq()` 仍会创建隐藏的 `div.tq-shell`，但不加 `is-tgqq`/`tq-shell-on`，原 tweb UI 完全不受影响。

Risk:
Low

## TW-UP-002

File:
src/lang.ts

Purpose:
新增 TGQQ i18n 文案（Tab 标签 + 占位页文本，9 条）。

Type:
Yellow

Why upstream modification is necessary:
遵循仓库 lang 机制（`lang.ts` 为唯一源），不使用硬编码中文。

TGQQ fallback:
仅新增键，不修改任何既有键；flags OFF 时不被引用。

Risk:
Low

## TW-UP-003（自动生成，非手改）

File:
src/scripts/out/langPack.strings

Purpose:
lang watcher（`watch-lang.js`）在 dev server 启动时自动再生成，包含 TGQQ 新键。

Type:
Yellow（生成产物）

Why upstream modification is necessary:
仓库机制要求；未手改。

TGQQ fallback:
无。

Risk:
None

## TW-UP-004

File:
src/components/chat/chat.ts

Purpose:
Chat 容器增加 `is-tgqq-chat` class（`chat.ts:250`，与 `chat`/`tabs-tab` 同处一行）。

Type:
Yellow（一行）

Why upstream modification is necessary:
聊天页皮肤（topbar/bubbles/composer）需要稳定且精确的作用域锚点；body 上的 `tq-chat-*` 门控类负责 flag + mobile 开关，`is-tgqq-chat` 负责「当前在聊天页」这一事实本身。两者叠加后 CSS 不会泄漏到会话列表或其他页面。

TGQQ fallback:
`tqFlags.chatHeader/chatBubbles/chatComposer` 全部关闭时（或非移动端），body 上没有 `tq-chat-*` 类，`is-tgqq-chat` 不匹配任何 TGQQ 规则，原 tweb 聊天页完全不受影响。

Risk:
Low

## TW-UP-005（Round 2 修正记录）

Files:
- src/tgqq/config/flags.ts（dialogSkin/chatHeader/chatBubbles/chatComposer 本轮开启）
- src/tgqq/shell/index.tsx（皮肤门控：`tq-dialog-skin`/`tq-chat-header`/`tq-chat-bubbles`/`tq-chat-composer` 按 flag + `mediaSizes.isMobile` 切换）
- src/scss/style.scss（Round 1 曾把 TGQQ design scss @use 进主样式，Round 2 已还原，TGQQ CSS 全部收归 `src/tgqq/index.ts` 动态 chunk，消除重复打包）

Purpose:
修复 Round 1 的 flag 未门控问题：skin CSS 此前在 `body.is-tgqq` 下无条件生效（含桌面端），现在仅当对应 flag 开启且 `mediaSizes.isMobile`（<600px）为真时生效，与 §30 Mobile Only 一致。

Type:
Yellow

Risk:
Low

## TW-UP-006（Round 3 修正记录）

Files:
- src/tgqq/shell/index.tsx（skin 门控由 `flag && mediaSizes.isMobile` 放宽为 `flag`；新增 body class `tq-tablet` = `tqFlags.tablet && !isMobile`）
- src/tgqq/config/flags.ts（新增 `tablet: true`）
- src/tgqq/components/TqTablet.scss（新文件：平板左列主页 + 右侧聊天并排、shell 收进左栏、隐藏 folders sidebar、隐藏平板 topbar 返回键）
- src/tgqq/index.ts（引入 TqTablet.scss）
- src/tgqq/components/TqChatList.scss / TqChatBubble.scss / TqTopbar.scss（topbar 背景 `!important` 换肤、chatlist `--background` 驱动、气泡时间可见、在线状态灰色、搜索框胶囊圆角）

Purpose:
Round 2 的皮肤仅 <600px（`isMobile`）生效；Round 3 按 QQ 平板方案把门控放宽到全部宽度，并实现 ≥600px 的平板结构（左列类手机主页 + 右列独立聊天窗）。

Type:
Yellow

TGQQ fallback:
`tqFlags.tablet = false` 时 body 无 `tq-tablet` 类，平板规则全部不生效；skin class 仍按各自 flag 门控，全关则回到原 tweb UI。

Risk:
Low-Medium（`#column-center` 在 600–925px 区间用 `inset-inline-start` 替代原生 translateX 定位，已用 fixture 几何验证并排；`updateColumnWidths.ts` 逻辑未改动）

## TW-UP-007（Round 4 修正记录）

Files:
- src/components/chat/chat.ts（`isLikeGroup` 赋值后新增
  `this.container.classList.toggle('is-tgqq-group', isLikeGroup)`）

Purpose:
QQ 皮肤需要区分私聊/群聊来显示 outgoing 消息右侧头像（QQ9：私聊无、群聊每条有）。
Bubble 上没有群聊标记（群聊 outgoing 也不渲染 `.name`），CSS-only 无法判断；
用容器 class 暴露群聊事实。

Type:
Yellow（一行）

TGQQ fallback:
非 TGQQ 皮肤下该 class 无任何样式匹配；`tqFlags.chatBubbles = false` 时 TGQQ
CSS 不加载，同样无影响。

Risk:
Low（class 名与既有 `is-tgqq-chat` 同域，无 JS 行为变化）

## TW-UP-008（Round 5）

Files:
- src/index.html（`sidebar-header main-search-sidebar-header` 内新增 `.tgqq-profile` 行：
  avatar / name / status(绿点+文字) / "+" 按钮）
- src/components/sidebarLeft/index.ts（`init()` 中填充 profile 行：`appUsersManager.getSelf()`
  → 昵称（first+last name）、头像首字、在线状态文案；监听 `user_update` 刷新）

Purpose:
QQ9 左列顶部是「头像 + 昵称 + 绿点"手机在线·WiFi" + 右侧 +」个人行，而 tweb 只有汉堡图标。
fixture 已按目标结构渲染，这里给真实应用补上同构的 DOM 与数据填充。

Type:
Yellow

TGQQ fallback:
`.tgqq-profile` 无 TGQQ 皮肤时无样式、无点击行为（"+"/头像不接线，仅占位）；
`getSelf()` 未就绪时保留空态，不影响 tweb 原有汉堡/搜索逻辑（burger 仍保留为第二行）。

Risk:
Low（新增 DOM + 只读数据填充，无既有行为变更）

## TW-UP-009（Round 5）

File:
- src/lang.ts（新增 11 条 TGQQ 键：搜索占位 3 + 频道分组 5 + 联系人分组 3）
- src/scripts/out/langPack.strings（同键中文翻译）

Purpose:
三个新 tab 页的分组标题与搜索占位走仓库 lang 机制，不硬编码中文。

Type:
Yellow（仅新增键）

TGQQ fallback:
仅新增键；flags OFF 时不被引用。

Risk:
None

## TW-UP-010（Round 8：群聊消息头像 renderer hook）

Files:
- src/components/chat/bubbles.ts（`isAvatarNeeded()` 末尾：群聊且消息为
  outgoing 时，若 `tqFlags.chatOwnAvatar && body.is-tgqq` 则返回 true——
  即给出站消息组也创建头像；新增 `import {tqFlags} from '@/tgqq/config/flags'`）
- src/components/chat/bubbleGroups.ts（`createAvatar()`：消息为 outgoing 时
  给头像节点加 `tq-own` class）

Purpose:
QQ9 群聊：入站消息组左侧显示发送者头像（tweb 原生已有），出站消息组右侧
也要显示自己的头像。tweb 原生 `isAvatarNeeded` 只给入站消息建头像
（`isLikeGroup && !isOutMessage`），本钩子补齐出站侧；`tq-own` class 供
TGQQ CSS 定位到右侧并预留缩进。私聊不受影响（`isLikeGroup` 为 false）。

Type:
Yellow（两处小改；DOM 结构与 tweb 原生头像一致，仅多一个 class）

TGQQ fallback:
非 TGQQ 皮肤下 `body.is-tgqq` 不存在 → 行为与原生完全一致；
`tqFlags.chatOwnAvatar = false` 同样关闭。

Risk:
Low-Medium（出站组头像走与入站完全相同的 `createAvatar`/`avatarNew` 路径，
头像加载、删除重建（`deleteMessagesByIds` 同条件）与选择动画逻辑天然一致；
CSS 负责右侧定位与 46px 缩进，JS 不动布局）

## TW-UP-011（Round 10：附件菜单标记 class）

Files:
- src/components/chat/input.ts（`ButtonMenuToggle` 的 `onOpen` 回调：
  菜单元素创建后加 `tq-attach-menu` class）

Purpose:
QQ9 附件面板：点「+」后弹出的 `.btn-menu`（tweb 下拉列表）改造成底部
4×2 网格面板。菜单挂在 overlay root（body 层），CSS 无法可靠地区分它和
其他 `.btn-menu`（消息右键菜单等），故给附件菜单打上标记 class，
TGQQ CSS 只对 `.btn-menu.tq-attach-menu` 生效。

Type:
Green（一行 DOM class；不改结构、不动布局）

TGQQ fallback:
非 TGQQ 皮肤下无对应 CSS 规则 → 行为与原生完全一致（多一个无样式 class）。

Risk:
None（class 不影响任何原生选择器/行为）

## TW-UP-012（Round 13：私聊入站组首头像）

Files:
- src/components/chat/bubbles.ts（`isAvatarNeeded()` 末段：群聊条件放宽为
  `isLikeGroup || (tqFlags.chatIncomingAvatar && body.is-tgqq)`，
  私聊且非出站时也返回 true——即私聊组首消息显示对方头像）
- src/tgqq/config/flags.ts（新增 `chatIncomingAvatar: true`）

Purpose:
QQ9 单聊：入站消息组首显示对方头像（40px、左侧、与组底对齐），tweb 原生
私聊完全不渲染头像（`isAvatarNeeded` 仅 `isLikeGroup && !isOutMessage`）。
与 Round 8 `chatOwnAvatar` 同一模式：flag + body.is-tgqq 双重门控。

Type:
Yellow（一处逻辑条件放宽 + 一个 flag）

TGQQ fallback:
非 TGQQ 皮肤下 `body.is-tgqq` 不存在 → 与原生一致；
`tqFlags.chatIncomingAvatar = false` 同样关闭。

Risk:
Low-Medium（与 Round 8 相同路径：`createAvatar`/`avatarNew` 对私聊可用，
guest-chat 先例已证明 1-on-1 头像渲染没问题；CSS 缩进沿用
`.is-guest-chat` 的 46px 方案，仅作用于含头像容器的组）

## TW-UP-013（Round 15：两行 composer 快捷按钮）
Files:
- src/components/chat/input.ts（新增 `constructTqQuickActions()`：`tqFlags.twoRowComposer
  && body.is-tgqq` 门控下向 `newMessageWrapper` 追加 4 个 `tq-quick-btn` 按钮——
  语音 → `recordingController.setRecordingMediaType('voice')+startActive()`；
  相册/拍摄 → `onAttachClick(false,true,true)`；文件 → `onAttachClick(true)`。
  全部复用既有公开方法，零逻辑重写、零 reparent）
- src/tgqq/config/flags.ts（新增 `twoRowComposer: true`）
- src/tgqq/design/chatInput.scss（`.new-message-wrapper` 两行 6 列 grid：
  上行 input(1/6)+send(6/6)，下行 语音/相册/拍摄/文件/表情/＋；输入容器
  `width:auto!important` 覆盖 tweb flex 用 `width:1%`；录音面板 `grid-column:1/-1`）

Purpose:
QQ9 两行输入区（round1-instruction §62 目标：Input+Send / Voice Gallery Camera
File Emoji More）。聊天窗输入区从单行升级为双行，快捷操作常驻可见。

Type:
Yellow（一个 renderer 小钩子 + 纯 CSS + flags；无行为重写）

TGQQ fallback:
非 TGQQ 皮肤 / flag=false → 不注入按钮，`.new-message-wrapper` 无 grid 覆盖，
保持 tweb 原生单行（chatInput.scss 规则带 `body.is-tgqq.tq-chat-composer` 前缀）。

Risk:
Low-Medium（录音/附件行为均走既有入口；grid 仅作用于 TGQQ 作用域；
fixture 三页已按真机 DOM 重构并自验两行几何）
