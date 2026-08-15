继续补上适合直接交给 Agent 的组件规范。建议文件名：

```text
docs/tgqq/component-library.md
```

# TGQQ Component Library Specification

**Version:** v0.1
**Platform:** Telegram Web K / tweb
**Target:** Mobile Web / PWA
**Depends on:** `design-system.md`
**Scope:** TGQQ Core UI Components

---

# 1. Purpose

本文定义 TGQQ 的基础 UI Component Library。

目标不是建立一个通用 Web UI Framework，而是统一 TGQQ 高频界面的：

```text
结构
尺寸
状态
交互
数据边界
CSS 约束
Telegram integration boundary
```

第一阶段 Component Library 主要服务：

```text
Mobile Home Shell
Messages
Channels
Contacts
Dynamics
```

之后再扩展：

```text
Chat
Profile
Drawer
Settings
```

---

# 2. Component Architecture

推荐目录：

```text
src/tgqq/components/

├── PageContainer/
├── AccountHeader/
├── SearchBar/
├── BottomNavigation/
├── SegmentTabs/
├── ConversationRow/
├── ListRow/
├── SectionCard/
├── Avatar/
├── Badge/
├── EmptyState/
└── LoadingState/
```

每个组件原则上：

```text
ComponentName/
├── index.tsx
└── style.module.scss
```

如果当前 tweb convention 不使用这种组织方式，则遵循当前仓库惯例，但保持组件边界。

---

# 3. Component Ownership Rule

组件分三类。

## 3.1 Pure TGQQ Component

完全由 TGQQ 拥有。

例如：

```text
TqBottomNavigation
TqSegmentTabs
TqSectionCard
TqEmptyState
```

可以正常设计和迭代。

---

## 3.2 Telegram-backed TGQQ Component

视觉由 TGQQ 控制，数据来自 tweb。

例如：

```text
TqAccountHeader
TqConversationPresentation
TqAvatar
```

必须遵守：

```text
Telegram manager/state
        ↓
TGQQ display
```

组件不能成为 Telegram state owner。

---

## 3.3 Telegram Existing Component + TGQQ Skin

不应该重新实现。

例如：

```text
chat list dialog
chat bubble
chat input
story viewer
```

这类组件后续通过：

```text
TGQQ class
+
scoped SCSS
+
small presentation hook
```

实现。

---

# 4. Common Component Contract

所有 TGQQ Component 必须满足：

```text
No direct MTProto calls

No Telegram persistence ownership

No implicit global state mutation

No hardcoded TGQQ colors

No unnecessary upstream dependency

Accessible interaction

Mobile-first layout
```

---

# 5. Naming

React/Solid component：

```text
Tq<Component>
```

例如：

```text
TqSearchBar
TqBottomNavigation
TqSegmentTabs
```

CSS root：

```text
tq-<component>
```

例如：

```text
.tq-search-bar
.tq-bottom-navigation
```

CSS Modules 时可以简化内部命名。

---

# 6. TqPageContainer

## Purpose

TGQQ 主页面统一容器。

适用于：

```text
Messages
Channels
Contacts
Dynamics
```

---

## Structure

```text
TqPageContainer
│
├── Header?
├── Fixed/Static content?
├── Scroll Content
└── Bottom Navigation?
```

---

## Responsibilities

负责：

```text
page background
mobile safe-area
content height
header/content relationship
bottom navigation reserved space
```

不负责：

```text
Telegram navigation
scroll data
page business state
```

---

## Layout

概念：

```text
┌────────────────────────┐
│ Header                 │
├────────────────────────┤
│                        │
│ Content                │
│                        │
├────────────────────────┤
│ Bottom Navigation      │
└────────────────────────┘
```

必须避免：

```text
Bottom Nav 覆盖最后一个列表项
```

因此 content bottom inset 至少考虑：

```text
bottomNavigationHeight
+
safeAreaBottom
```

---

## Important

如果 Messages 使用 tweb 原 chat list：

```text
不要让 TqPageContainer
成为新的 vertical scroll owner。
```

---

# 7. TqBottomNavigation

## Purpose

TGQQ Mobile Home 一级导航。

固定 destinations：

```ts
type TqHomeTab =
  | 'messages'
  | 'channels'
  | 'contacts'
  | 'dynamics';
```

---

## Order

必须：

```text
消息
频道
联系人
动态
```

不得在 v0.x 任意重排。

---

## Structure

```text
TqBottomNavigation
│
├── Item: Messages
├── Item: Channels
├── Item: Contacts
└── Item: Dynamics
```

单项：

```text
Icon
Badge?
Label
```

---

## Props

建议：

```ts
interface TqBottomNavigationProps {
  selected: TqHomeTab;
  onSelect: (tab: TqHomeTab) => void;

  messagesBadge?: string | number;
}
```

不要把：

```text
Telegram unread calculation
```

放在组件内部。

---

## States

```text
default
selected
pressed
disabled
badged
```

Alpha 不需要 disabled，但组件结构可以支持。

---

## Selected

使用：

```text
--tq-accent-primary
```

---

## Unselected

使用：

```text
--tq-text-secondary
```

---

## Interaction

点击非当前 Tab：

```text
切换 TGQQ Home content
```

点击当前 Tab：

第一阶段允许：

```text
no-op
```

之后增加：

```text
scroll to top
```

不要为了第一轮强行访问 Telegram list internals。

---

## Visibility Rule

只显示于：

```text
mobile
+
tweb CHATLIST state
+
TGQQ shell enabled
```

以下状态隐藏：

```text
Chat
Profile
Login/Auth
Desktop
Fullscreen viewer
```

---

## Accessibility

每个 item 使用：

```text
button
```

或等价语义。

必须提供：

```text
aria-label
aria-current / selected state
```

---

# 8. TqAccountHeader

## Purpose

QQ 当前移动首页常见的账号/Header 结构。

Messages 目标：

```text
Avatar  Display Name             +
        Status
```

Contacts：

```text
Avatar  联系人                  +
```

因此组件支持 Variant。

---

## Variants

```ts
type TqAccountHeaderVariant =
  | 'identity'
  | 'page';
```

---

## Identity Variant

```text
Avatar
Display Name
Subtitle
Trailing Action
```

---

## Page Variant

```text
Avatar
Page Title
Trailing Action
```

---

## Props

概念：

```ts
interface TqAccountHeaderProps {
  variant: 'identity' | 'page';

  avatarPeerId?: PeerId;

  title: string;
  subtitle?: string;

  onAvatarClick?: () => void;
  onActionClick?: () => void;
}
```

实际类型根据 tweb 当前 TypeScript 类型调整。

---

## Data Ownership

组件不能：

```text
自己找当前 Telegram 用户
```

调用方提供：

```text
title
subtitle
peer/avatar source
```

或者通过一个薄 TGQQ account bridge 获取。

---

## Avatar Click

未来：

```text
Account Drawer
```

第一轮：

可以调用现有 tweb profile/sidebar 行为。

---

## Trailing Action

Messages：

```text
+
```

Contacts：

```text
Add
```

但第一轮可以只实现 visual placeholder。

---

# 9. TqSearchBar

## Purpose

统一 QQ-style 搜索入口。

---

## Idle State

目标：

```text
╭────────────────────────╮
│        搜索            │
╰────────────────────────╯
```

特点：

```text
rounded
full-width
surface-secondary
centered icon + placeholder
```

---

## Focused State

长期：

```text
Back | Input              Cancel
```

但第一阶段可以只提供：

```text
clickable search entry
```

然后交给现有 tweb Search。

---

## Props

建议：

```ts
interface TqSearchBarProps {
  placeholder?: string;

  value?: string;

  mode?: 'entry' | 'input';

  onClick?: () => void;
  onInput?: (value: string) => void;
}
```

---

## Rules

禁止组件内部直接：

```text
search Telegram
```

它只是：

```text
presentation + input
```

---

# 10. TqSegmentTabs

## Purpose

用于联系人页：

```text
分组
好友
群聊
频道
机器人
设备
```

也可以被其他 TGQQ 二级页面复用。

---

## Structure

```text
Scrollable horizontal tab list
```

---

## Props

```ts
interface TqSegmentItem<T extends string> {
  id: T;
  label: string;
  badge?: string | number;
}

interface TqSegmentTabsProps<T extends string> {
  items: TqSegmentItem<T>[];
  selected: T;
  onSelect: (id: T) => void;
}
```

---

## Selected Visual

```text
primary text
+
accent underline
```

---

## Unselected

```text
secondary/primary text
```

---

## Overflow

必须支持：

```text
horizontal scrolling
```

禁止为了塞入 6 个 Tab：

```text
把文字压到极小字号
```

---

# 11. TqAvatar

## Purpose

统一 TGQQ 页面里的头像外观。

但它不应该重新实现 Telegram Avatar loading。

---

## Principle

正确：

```text
existing tweb avatar renderer
+
TGQQ wrapper/decorator
```

错误：

```text
自己 fetch Telegram avatar
```

---

## Sizes

语义：

```text
xs
sm
md
lg
profile
```

不要页面直接：

```text
width: 47px
height: 47px
```

---

## Decoration Slots

允许：

```text
online indicator
unread badge
future special marker
```

---

## Shape

默认：

```text
circle
```

第一阶段不实现：

```text
头像框
VIP frame
animated decoration
```

---

# 12. TqBadge

## Variants

```text
unread
dot
count
status
```

---

## Count

规则：

```text
1–99
99+
```

不要出现：

```text
1037
```

导致 layout 变形。

---

## Unread Badge

QQ Messages Reference 目标：

```text
Avatar top-right
```

但注意：

> Telegram unread state 仍由 tweb 提供。

所以如果现有 `unreadAvatarBadge` 可以使用：

优先对其 styling/reposition，

而不是新建第二个 TGQQ Badge state。

---

# 13. TqConversationRow

这个组件需要特别说明。

## v0.1 Status

**Design Component：Defined**

**Runtime replacement：Not yet required**

当前 Alpha 应优先：

```text
existing tweb DialogElement
+
TGQQ styles
```

而不是把它替换成 `TqConversationRow.tsx`。

---

## Target Visual

```text
      [Unread]
Avatar     Title                 Time
           Preview
```

---

## Information

必须支持：

```text
Avatar
Title
Preview
Timestamp
Unread
Muted
Pinned
Typing
Draft
```

---

## State Ownership

全部：

```text
tweb
```

TGQQ 只决定布局与 style。

---

## Layout

概念：

```text
ConversationRow
│
├── AvatarSlot
│   ├── Avatar
│   └── UnreadBadge
│
└── Content
    ├── Header
    │   ├── Title
    │   └── Time
    │
    └── Preview
```

---

## Separator

默认：

```text
none
```

或者极弱。

当前 QQ Core UI 主要依赖：

```text
spacing
alignment
typography
```

区分 row。

---

## Future Decision

只有当现有 Dialog DOM 无法满足以下要求时：

```text
avatar badge
title/time grid
preview structure
```

才考虑真正实现：

```text
TqConversationRow
```

在 Agent 第一轮不要提前替换。

---

# 14. TqListRow

## Purpose

通用 QQ-style 列表行。

用于未来：

```text
Drawer
Profile
Settings
Devices
```

---

## Structure

```text
Leading      Content           Trailing
Icon/Avatar  Title             Value
             Subtitle?         Chevron?
```

---

## Props

概念：

```ts
interface TqListRowProps {
  title: string;

  subtitle?: string;

  leading?: JSX.Element;

  trailing?: JSX.Element;

  onClick?: () => void;
}
```

---

## Rule

整行可点击时：

不要再让内部每个 child 都有互相冲突的 click handler。

---

# 15. TqSectionCard

## Purpose

QQ 当前 Settings/Profile 大量使用 rounded grouped card。

---

## Structure

```text
╭─────────────────────────╮
│ Row                     │
│─────────────────────────│
│ Row                     │
│─────────────────────────│
│ Row                     │
╰─────────────────────────╯
```

---

## Props

可以简单：

```text
children
```

不要把 SectionCard 设计成一个拥有几十个业务字段的组件。

---

## Styling

```text
surface-primary
radius-lg
overflow hidden
```

内部 separator：

```text
subtle
inset
```

---

# 16. TqEmptyState

## Purpose

统一：

```text
Channels empty
Contacts empty
Dynamics empty
Search no results
```

---

## Structure

```text
Optional illustration/icon

Title

Description

Optional primary action
```

---

## Example

Channels：

```text
还没有加入频道

加入 Telegram 频道后，
它们会显示在这里。
```

第一轮 placeholder 不应伪造 Telegram 数据。

---

# 17. TqLoadingState

Telegram 客户端本身大部分时候有缓存。

因此：

```text
Loading State
```

不应该成为大面积常态。

---

## Usage

只在：

```text
第一次真正没有可显示数据
```

时使用。

有 cache：

```text
立即显示 cache
```

---

## Style

避免：

```text
巨大 spinner 居中整屏
```

优先：

```text
轻量 skeleton
```

但 Alpha 可以先只使用现有 tweb loading indicator。

---

# 18. TqIconButton

建议作为 Shared Component。

---

## Purpose

用于：

```text
Back
Add
More
Camera
Search
```

---

## Required

```text
minimum touch target
aria-label
pressed feedback
```

Icon 本身不能成为 click target 的唯一边界。

---

# 19. TqPrimaryButton

未来 Profile / Empty State / Composer 可使用。

---

## Variants

```text
primary
secondary
danger
```

Primary：

```text
accent-primary surface
high contrast text
```

---

# 20. TqPageTitle

如果多个新页面需要：

```text
频道
联系人
动态
```

不要每页自己定义一套字号和 margin。

可以抽：

```text
TqPageTitle
```

但：

> 如果 `TqAccountHeader` 已经能覆盖当前场景，就不要为了组件数量而继续拆分。

---

# 21. TqHomeShell

虽然属于 Shell，不是普通 Component，但需要定义边界。

---

## Structure

```text
TqHomeShell
│
├── HomeContent
│   ├── Messages
│   ├── Channels
│   ├── Contacts
│   └── Dynamics
│
└── TqBottomNavigation
```

---

## State

只拥有：

```text
selectedHomeTab
```

不拥有：

```text
Telegram current peer
current chat
profile navigation
dialog state
```

---

## Messages Content

必须 mount/contain：

```text
original tweb chat list
```

---

## Other Tabs Alpha

允许：

```text
TqEmptyState / placeholder
```

---

# 22. TqMessagesPage

## v0.1

职责：

```text
optional AccountHeader
optional SearchBar
existing chat list
```

不要创建 conversation data store。

---

## Preferred Structure

```text
TqMessagesPage
│
├── TqAccountHeader
├── TqSearchBar
└── TelegramChatListSlot
```

---

## TelegramChatListSlot

这不是重新渲染。

只是：

```text
existing DOM mount location
```

---

# 23. TqContactsPage

## Long-term Structure

```text
TqContactsPage
│
├── TqAccountHeader
├── TqSearchBar
├── TqSegmentTabs
└── SegmentContent
```

---

## Segment IDs

```ts
type TqContactsSegment =
  | 'groups'
  | 'friends'
  | 'groupChats'
  | 'channels'
  | 'bots'
  | 'devices';
```

---

## Alpha

允许：

```text
placeholder
```

第一轮不要加入假 Telegram 联系人。

---

# 24. TqChannelsPage

长期：

```text
TqAccountHeader
TqSearchBar
Channel list
```

数据：

```text
Telegram broadcast channels
```

---

## Alpha

```text
Title
Placeholder
```

---

# 25. TqDynamicsPage

长期：

```text
Telegram Stories
```

第一版不做 QQ Space。

---

## Alpha

```text
Title
Placeholder
```

---

# 26. Component CSS Rules

每个 TGQQ Component 必须：

```text
使用 Design Tokens
```

例如正确：

```scss
.root {
  background: var(--tq-surface-page);
  color: var(--tq-text-primary);
  padding-inline: var(--tq-space-md);
}
```

错误：

```scss
.root {
  background: #121212;
  color: white;
  padding: 16px;
}
```

---

# 27. Spacing Exceptions

不是每一个 `4px` 都必须做成一个新的 CSS Variable。

允许：

```text
局部微调
```

但高频语义值必须使用 Token。

判断标准：

> 如果同一个数值/含义会在多个组件复用，就应该成为 Design Token。

---

# 28. Component Variants

禁止为了细微差异复制：

```text
TqMessagesHeader
TqContactsHeader
TqChannelsHeader
```

如果本质结构相同。

优先：

```text
TqAccountHeader
+
variant
```

但也不要形成：

```text
variant="messages-contacts-channels-drawer-compact-large-special..."
```

如果差异已经很大，就拆组件。

---

# 29. Props Boundary

组件 Props 应表达：

```text
presentation requirement
```

而不是暴露 Telegram 全部内部对象。

不推荐：

```ts
<TqHeader managers={managers} rootScope={rootScope} ... />
```

推荐：

```ts
<TqHeader
  title={title}
  subtitle={subtitle}
  avatar={...}
/>
```

Telegram manager access 集中在 page/bridge 层。

---

# 30. Bridge vs Component

正确：

```text
TqAccountSource
      ↓
TqMessagesPage
      ↓
TqAccountHeader
```

错误：

```text
TqAccountHeader
      ↓
rootScope.managers
```

保持组件可测试。

---

# 31. Solid State Rules

如果使用 Solid：

优先：

```text
signals
memos
store APIs already used by tweb
```

不要把 React Pattern 硬搬过来。

尤其禁止：

```text
React-style useEffect mental model
```

如果仓库有现成 helper，则遵循项目风格。

---

# 32. Cleanup

任何 Component 创建：

```text
listener
subscription
event handler
```

必须在 disposal 时清理。

尤其：

```text
rootScope listener
manager listener
window event
ResizeObserver
```

不要制造页面切换后残留 listener。

---

# 33. Telegram DOM Adapter Rule

对于现有 tweb DOM：

如果只需要 styling：

```text
class hook
```

优先。

例如：

```text
tq-dialog
tq-chat
tq-composer
```

禁止因为想让组件体系“统一”就把 Telegram DOM 包装成几层无意义 wrapper。

---

# 34. DOM Reparent Rule

原则：

```text
不 reparent Telegram stateful DOM
除非源码调查证明安全。
```

特别是：

```text
ChatInput
ChatBubbles
chat list
```

这些都可能依赖父级：

```text
layout
animation
event delegation
scroll
```

第一轮 Shell 应尽量通过：

```text
container insertion
layout integration
```

而不是任意移动核心 DOM。

---

# 35. Animation API

共享组件应通过 Token：

```text
--tq-motion-fast
--tq-motion-normal
```

不要：

```scss
transition: all 0.37s ease-in-out;
```

---

推荐只 transition：

```text
color
background-color
opacity
transform
```

避免：

```text
transition: all
```

---

# 36. Reduced Motion

尊重：

```css
prefers-reduced-motion
```

TGQQ 动画不是功能必需条件。

---

# 37. Safe Areas

所有底部固定组件，尤其：

```text
TqBottomNavigation
```

必须考虑：

```text
safe-area-inset-bottom
```

但优先复用 tweb 当前 safe-area abstraction。

---

# 38. Keyboard Interaction

未来 Composer 打开软键盘时：

```text
TqBottomNavigation
```

已经因为处于 CHAT 页面而消失，因此不会与 Chat keyboard 冲突。

Home Search 输入键盘时：

Bottom Navigation 是否隐藏待实际 QQ Reference 确认。

Alpha：

```text
保持显示
```

除非造成 viewport 问题。

---

# 39. Z-index

不要随便：

```scss
z-index: 999999;
```

必须调查 tweb 当前 layering system。

TGQQ overlay/drawer 后续应使用统一层级 Token。

---

# 40. Component Testing

纯 TGQQ Components 推荐至少覆盖：

```text
render
selected state
click
disabled if applicable
accessibility labels
```

特别：

```text
TqBottomNavigation
TqSegmentTabs
```

值得做单元/UI 测试。

---

# 41. Visual Test

第一轮最值得固定：

```text
TqBottomNavigation
TqSearchBar
TqAccountHeader
```

因为它们后续将成为很多页面的视觉基线。

---

# 42. Reference Accuracy Levels

以后 Component 文档中允许标：

```text
Reference A
```

当前 QQ 实机明确。

```text
Reference B
```

结构确认，尺寸待校准。

```text
Reference C
```

推断，需要补图。

例如目前：

```text
Bottom Navigation structure: A
Dark visual direction: A
Exact tab height: B
Exact font size: B
Exact accent RGB: B
```

Agent 不得把 B/C 值描述成：

```text
QQ 精确参数
```

---

# 43. Alpha Component Set

第一轮真正要求 Agent 实现的只有：

```text
TqHomeShell

TqBottomNavigation

基础 TqPageContainer

基础 Design Tokens
```

根据实际 integration 需要，可增加：

```text
TqEmptyState
```

---

以下允许只定义接口/暂不实现：

```text
TqAccountHeader
TqSearchBar
TqSegmentTabs
```

---

以下本轮不实现：

```text
TqConversationRow runtime replacement
TqDrawer
TqProfileHeader
TqChatComposer
TqMessageBubble
```

---

# 44. 第二轮 Component Set

预计：

```text
TqAccountHeader
TqSearchBar
Conversation styling
TqSegmentTabs
Contacts page components
```

---

# 45. 第三轮 Component Set

Chat：

```text
TqChatHeader presentation
TqMessageBubble skin
TqChatTimeDivider skin
TqComposer presentation
```

这些优先是：

```text
styles/hooks
```

而不是完全独立 Component。

---

# 46. Out of Scope

TGQQ Core Component Library v0.x 不包含：

```text
QQ VIP badge

QQ level icon

QQ Show

Wallet

Gift

Avatar decorations

Dynamic bubble themes

Pet

Custom font marketplace

Commercial banners

Game center
```

---

# 47. Agent Rule: Do Not Overbuild

如果一个需求现在只需要：

```text
20 行简单 Solid component
```

不要变成：

```text
BaseComponent
ComponentFactory
UIRegistry
RendererAdapter
ThemeAwareAbstract...
```

TGQQ 需要的是：

```text
清晰
薄
可维护
```

而不是 framework。

---

# 48. Agent Rule: No Premature Generic Design

例如现在只有 Bottom Navigation。

不要创建：

```text
UniversalNavigationEngine
```

直接：

```text
TqBottomNavigation
```

即可。

等真正出现第二种 navigation pattern 再抽象。

---

# 49. Agent Rule: Prefer Existing tweb Utility

遇到：

```text
Ripple
Icon
Avatar
Localization
Responsive
Peer title
```

先检查 tweb 是否已有工具。

优先复用。

不要在 `src/tgqq` 重新实现：

```text
TqRipple
TqTelegramAvatarLoader
TqLocalizationEngine
```

---

# 50. Agent Rule: TGQQ Component Must Survive Fallback

当：

```text
tqFlags.shell = false
```

TGQQ Components 应不再参与主 UI。

不能：

```text
Shell disabled
但 TGQQ global CSS 仍改变 tweb
```

这就是 scoped CSS 的实际验收标准。

---

# 51. 第一轮组件开发验收

完成第一轮时：

```text
TqHomeShell

TqBottomNavigation

TqPageContainer

TqEmptyState（如需要）
```

应满足：

```text
mobile only

dark theme usable

semantic tokens

safe area correct

messages tab contains real tweb chat list

placeholder tabs render normally

no nested scrolling

chat navigation unaffected

fallback unaffected
```

---

# 52. Recommended Initial Skeleton

可参考，但 Agent 应根据真实仓库风格调整：

```text
src/tgqq/

├── config/
│   └── flags.ts

├── design/
│   ├── tokens.scss
│   ├── dark.scss
│   └── light.scss

├── components/
│   ├── PageContainer/
│   ├── BottomNavigation/
│   └── EmptyState/

├── shell/
│   └── TqMobileShell.tsx

└── pages/
    ├── Channels/
    ├── Contacts/
    └── Dynamics/
```

Messages 在第一轮可能不需要新建完整 component：

```text
现有 Telegram chatlist
```

就是其核心内容。

---

# 53. Component Definition of Done

一个 TGQQ Component 只有满足：

```text
[ ] 使用 semantic tokens

[ ] scoped styles

[ ] 不直接调用 MTProto

[ ] 不拥有 Telegram core state

[ ] mobile layout 正常

[ ] accessibility 基本完整

[ ] 无明显 magic color

[ ] 无无意义 abstraction

[ ] feature off 不污染 tweb

[ ] listener/disposable 正确清理
```

才算完成。

---

# 54. Design Review Order

Agent 调 UI 时按：

```text
1. Structure

2. Geometry

3. Alignment

4. Spacing

5. Typography

6. Colors

7. Icons

8. Motion
```

不要先花时间：

```text
调一个蓝色 RGB
```

而页面结构还不正确。

---

# 55. 当前组件体系总结

TGQQ 的 Component Library 应最终形成：

```text
                 TqDesignSystem
                       │
        ┌──────────────┼───────────────┐
        │              │               │
    Containers       Controls       Presentations
        │              │               │
 PageContainer      SearchBar      Conversation
 SectionCard        SegmentTabs    AccountHeader
                    BottomNav      Avatar/Badge
```

再往上：

```text
TqHomeShell
│
├── Messages
├── Channels
├── Contacts
└── Dynamics
```

复杂 Telegram Runtime 则保持在 TGQQ Component Library 之外：

```text
Telegram Chatlist
Telegram Chat
Telegram Bubbles
Telegram ChatInput
Telegram Stories
```