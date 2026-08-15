可以。先把第一轮范围压得足够小。

我重新核对了当前 tweb `master`：仓库自己的 `AGENTS.md` 明确要求 coding agent 先遵循仓库内规则，UI 不得绕过 app managers 直接调用 MTProto，且未经明确要求不要自行 commit；当前 `package.json` 要求 Node `^22.18.0 || >=24.11.0`、pnpm `11.16.0`，提供 `start / build / typecheck / test / lint` 等脚本。

当前 `AppImManager` 顶层仍是 `CHATLIST / CHAT / PROFILE` 三种状态，所以 TGQQ 的“消息 / 频道 / 联系人 / 动态”不能替换这三个状态，而应该作为 **CHATLIST 内部的 Mobile Home Shell**。打开会话仍继续通过现有 `setPeer()` 进入 `CHAT`。 当前 dialogs 还已经存在独立的 `unreadAvatarBadge` DOM，并且列表点击最终复用 `appImManager.setPeer/setInnerPeer`，这对以后 QQ 化会话列表很有利。

下面这份可以直接交给 Agent。

---

# TGQQ × tweb 第一轮 Agent 工作指令

## 0. 任务背景

你正在开发 **TGQQ**。

TGQQ 是基于 Telegram Web K（tweb）的第三方 Telegram 客户端 UI 项目。

产品目标：

```text
Telegram protocol / state / messaging capability
+
current QQ Android core UX
```

本项目不是重新实现 Telegram，不修改 Telegram 协议语义。

核心原则：

```text
tweb owns Telegram state and behavior.

TGQQ owns mobile product shell
and presentation.
```

当前阶段优先级：

```text
1. 保持 Telegram 能力正确
2. 建立稳定 TGQQ integration boundary
3. 建立 TGQQ Design System
4. 打通 mobile shell
5. 最后才做 QQ pixel matching
```

---

# 1. 本轮唯一目标

第一轮只完成：

```text
A. 固定 tweb upstream baseline

B. 跑通本地开发 / typecheck / build

C. 调查当前实际源码架构

D. 建立 src/tgqq namespace

E. 建立 TGQQ Feature Flags

F. 建立 TGQQ Design System skeleton

G. 建立 Mobile Home Shell

H. 在 CHATLIST 状态中加入：
   消息 / 频道 / 联系人 / 动态
   四个 TGQQ Bottom Tabs

I. “消息”继续承载 tweb 原 chat list

J. 频道 / 联系人 / 动态
   第一轮允许使用简单 placeholder

K. 打开 Telegram 会话必须继续进入
   tweb 原 CHAT runtime

L. 输出下一轮 dialogs/chat hook 调查报告
```

本轮完成后预期：

```text
Launch
  ↓
TGQQ Mobile Home

消息 | 频道 | 联系人 | 动态
  │
  └─ 消息
       ↓
  existing Telegram chat list
       ↓
  tap dialog
       ↓
  existing tweb Chat
       ↓
  back
       ↓
  TGQQ Home
```

---

# 2. 本轮明确不做

禁止本轮实现：

```text
QQ-style message bubble

outgoing self avatar

QQ-style Chat Header

two-row Chat Composer

好友分组

特别关心

完整频道聚合

Stories 动态

Account Drawer

User Profile

Group Profile

Settings skin

PWA/TWA Android packaging
```

也禁止：

```text
重新写 message renderer

重新写 Telegram chat list state

重新写 ChatInput

重新写 MTProto

重新写 Telegram storage

重新写 account/auth system

重新写 upload/download

重新写 notification

重新写 call subsystem
```

特别是不要因为 Web 技术栈看起来容易，就创建：

```text
TqMessageManager
TqTelegramClient
TqMessageStore
TqChatEngine
```

这些都不应该存在。

---

# 3. 首先读取仓库自己的 Agent 指令

开始工作前：

```text
READ:
AGENTS.md
```

如果存在项目级或子目录级 Agent instructions：

```text
全部读取并遵循。
```

仓库自身指令优先于本工作指令中的代码风格示例。

特别注意：

```text
不要自行 commit
不要自行 push
不要删除用户已有工作
不要 reset 用户工作区
```

除非用户明确要求。

---

# 4. 所有实现必须基于当前 checkout

不要假定文档中的：

```text
类名
路径
API
DOM structure
CSS classname
```

一定和当前 checkout 完全一致。

本工作指令描述的是目标和边界。

**当前 checkout 的源码才是实现事实源。**

如果实际 tweb 架构已经变化：

```text
先调查
→ 记录变化
→ 使用当前架构中的最小侵入方案
```

不要为了符合本文而恢复旧架构。

---

# 5. 记录 Upstream Baseline

修改任何代码以前，记录：

```bash
git status
git branch --show-current
git rev-parse HEAD
git remote -v
node --version
pnpm --version
```

如果仓库 `AGENTS.md` 要求 shell command 使用特定 wrapper，例如 `rtk`，严格遵循仓库要求。

新增：

```text
docs/tgqq/upstream-baseline.md
```

内容至少：

```markdown
# TGQQ tweb Upstream Baseline

Repository:
...

Branch:
...

Commit:
<full SHA>

Working tree before TGQQ changes:
clean / dirty

Node:
...

pnpm:
...

Date:
...

Notes:
...
```

如果初始 working tree 是 dirty：

```text
不要 reset
不要 checkout 覆盖
不要自动 stash
```

记录已有变化。

---

# 6. 验证真实 Toolchain

检查：

```text
package.json
pnpm-lock.yaml
AGENTS.md
README.md
```

确认：

```text
Node requirement
pnpm requirement
dev command
typecheck command
lint command
test command
production build command
preview workflow
```

不要根据记忆使用 npm/yarn。

不要自行升级：

```text
Node dependency
pnpm lockfile
Vite
Solid
TypeScript
```

本轮不是 dependency-upgrade PR。

---

# 7. 安装依赖

遵循当前仓库推荐方式。

优先保持 lockfile 不变。

如果：

```text
pnpm install
```

导致无关 lockfile 大规模变化：

先判断环境/版本是否不匹配。

不要直接接受无关 lockfile churn。

---

# 8. 先验证原始 tweb

在 TGQQ 修改前尽可能完成：

```text
typecheck
development start
production build
```

测试/预览方式严格按仓库 `AGENTS.md`。

如果授权预览必须通过：

```text
scripts/start-preview.sh
```

则使用该流程，不要绕过。

记录：

```text
BASELINE TYPECHECK:
PASS / FAIL

BASELINE BUILD:
PASS / FAIL

BASELINE PREVIEW:
PASS / FAIL
```

如果原始 upstream 本身失败：

```text
记录原始错误
```

不要把 upstream 原问题归因于 TGQQ。

---

# 9. 不伪造 Telegram Credentials

如果开发环境需要：

```text
API ID
API Hash
auth snapshot
.env.local
```

只使用仓库已有的合法开发配置或用户已经提供的环境。

不要：

```text
生成假 secret
提交真实 secret
把 credentials 写进代码
把 auth 数据加入 Git
```

---

# 10. Source Survey

在写 TGQQ Shell 之前，必须先阅读当前真实源码。

至少定位并检查：

```text
src/index.ts

src/lib/appImManager.ts
src/lib/appDialogsManager.ts
src/lib/rootScope.ts

src/lib/appManagers/**
src/lib/managers*

index.html

src/components/sidebarLeft/**
src/components/sidebarLeft/tabs/**

Contacts implementation

src/components/chat/chat*
src/components/chat/bubbles*
src/components/chat/input*

theme-related implementation
responsive/mobile detection
SCSS entry points
```

不要只搜索文件名。

要回答：

```text
谁拥有 state？

谁创建 DOM？

谁负责 navigation？

谁控制 mobile/desktop responsive state？

谁拥有 dialog click？

谁负责 chat list mount？

谁负责 CHATLIST → CHAT？

谁控制 back？

谁提供 account managers？

哪里最适合 mount TGQQ shell？
```

---

# 11. 必须确认顶层 Navigation

调查当前：

```text
APP_TABS
```

确认实际枚举和：

```text
selectTab
setPeer
setInnerPeer
```

行为。

预期设计原则是：

```text
tweb APP_TABS

CHATLIST
CHAT
PROFILE
```

继续保持。

TGQQ 不得变成：

```text
APP_TABS.MESSAGES
APP_TABS.CHANNELS
APP_TABS.CONTACTS
APP_TABS.DYNAMICS
```

---

# 12. TGQQ 四 Tab 的正确层级

TGQQ 四 Tab 属于：

```text
APP_TABS.CHATLIST
```

内部。

目标：

```text
APP_TABS.CHATLIST
    │
    └── TqMobileShell
          │
          ├── MESSAGES
          ├── CHANNELS
          ├── CONTACTS
          └── DYNAMICS
```

而：

```text
APP_TABS.CHAT
```

仍是 Telegram 真实聊天。

所以进入 Chat 时：

```text
TGQQ bottom nav must disappear
```

Back 后：

```text
return to CHATLIST
→ restore TGQQ home tab
```

---

# 13. 不修改 setPeer 语义

Telegram dialog click 后继续使用当前：

```text
appImManager.setPeer(...)
```

或当前源码对应能力。

不要增加：

```text
TqChatRouter
```

去取代它。

禁止复制：

```text
history navigation
chat stack
peer migration
forum/thread handling
```

---

# 14. 调查 Dialogs

检查：

```text
appDialogsManager
DialogElement
chat list DOM
dialog title
subtitle
timestamp
avatar
unread badge
avatar unread badge
mute
pin
mention
reaction badge
```

输出：

```text
docs/tgqq/dialogs-hook-plan.md
```

必须回答：

```text
1. 哪些 QQ 会话列表视觉可以纯 SCSS 完成？

2. 当前 unreadAvatarBadge 的 DOM 在哪里？

3. 如何做到：
      unread badge → avatar top-right
   而不重写 unread state？

4. title / subtitle / time DOM 结构是否足以实现 QQ layout？

5. 是否需要给 DialogElement
   添加一个单独 TGQQ class？

6. 哪些地方完全不需要改 TypeScript？
```

本轮：

```text
不要开始完整 Conversation List skin。
```

允许为 shell 集成增加必要的 wrapper/class。

---

# 15. 调查 Contacts

检查当前 Contacts 实现。

确认：

```text
联系人从哪个 manager 获取
Contacts update 监听哪个 event
怎样打开联系人 Chat/Profile
列表使用哪些现有组件
```

记录：

```text
TqContactsPage
```

下一轮应该如何读取 manager。

本轮 Contacts Tab 允许只显示：

```text
联系人

第一轮占位页面
```

如果真实联系人接入只需要非常少量、安全代码，也不要主动扩大范围。

**第一轮以 architecture validation 为目标。**

---

# 16. 调查 Chat，但不要改 Chat

必须阅读：

```text
Chat
ChatBubbles
ChatInput
```

输出：

```text
docs/tgqq/chat-hook-plan.md
```

至少回答以下问题。

### Chat Root

```text
聊天 root DOM 是谁建立的？

在哪个元素上增加
is-tgqq-chat
最安全？
```

### Header

```text
title DOM 来源
subtitle DOM 来源
typing 状态来源
back button
profile/menu action
```

### Bubbles

```text
incoming/outgoing class
bubble DOM
avatar DOM
grouped messages
date divider
message tail
reply block
reaction block
```

### Outgoing self avatar

必须调查：

```text
当前 outgoing bubble
是否已经有可利用 avatar DOM？
```

如果没有：

```text
下一轮怎样用 presentation-only decorator
实现 self avatar？
```

只写方案，不实施。

### Composer

确认：

```text
message input
send
emoji
attachment
voice/record
reply/edit
```

分别由哪个已有 DOM/对象负责。

必须回答：

```text
能否不复制任何实际 action button，
仅通过 CSS / DOM reorder，
实现：

Input + Send
----------------
Voice Gallery Camera File Emoji More
```

本轮禁止修改 ChatInput layout。

---

# 17. 建立 TGQQ Namespace

新增：

```text
src/tgqq/
```

第一轮只需要：

```text
src/tgqq/
├── config/
├── design/
├── shell/
├── components/
└── pages/
```

不要提前创建：

```text
metadata
profiles
drawer
chat
services
repository
domain
```

几十个空目录。

需要时再增加。

---

# 18. 路径 Alias

先检查当前 tsconfig/Vite alias。

如果：

```text
@/*
```

已经映射 `src/*`：

优先使用类似：

```ts
import ... from '@/tgqq/...';
```

不要为了 TGQQ 第一轮新增一堆：

```text
@tgqq-design
@tgqq-shell
@tgqq-components
```

除非当前项目本身有明确同类 convention。

降低构建配置改动。

---

# 19. Feature Flags

新增：

```text
src/tgqq/config/flags.ts
```

至少：

```ts
export const tqFlags = {
  shell: true,

  messages: true,
  channels: true,
  contacts: true,
  dynamics: true,

  dialogSkin: false,

  chatHeader: false,
  chatBubbles: false,
  chatOwnAvatar: false,
  chatComposer: false,

  drawer: false,
  metadata: false
};
```

具体命名按 repo style 调整。

要求：

```text
CHAT-* 本轮全部 false
```

---

# 20. Flags 不做复杂配置系统

本轮不要加入：

```text
remote config
query-string feature config
IndexedDB config
Settings UI
实验平台
```

只需要一个集中配置入口。

下一轮 Debug Tool 再扩。

---

# 21. TGQQ Root Class

当：

```text
tqFlags.shell === true
```

时，在一个稳定、最上层但不污染 Telegram state 的容器增加：

```text
is-tgqq
```

或：

```text
tq-shell-enabled
```

这样的 root class。

具体挂：

```text
body
#page-chats
TGQQ shell root
```

哪一个最合理，要根据实际源码调查决定。

优先原则：

```text
作用域足够明确
+
不影响 auth/login pages
+
不影响其他原 Telegram 页面
```

---

# 22. Design System Skeleton

新增例如：

```text
src/tgqq/design/tokens.scss
src/tgqq/design/dark.scss
src/tgqq/design/light.scss
```

必要时再增加：

```text
typography.scss
```

第一轮不要过度拆文件。

---

# 23. Design Token 使用 CSS Variables

例如：

```scss
.is-tgqq {
  --tq-surface-page: ...;
  --tq-surface-primary: ...;
  --tq-surface-secondary: ...;

  --tq-text-primary: ...;
  --tq-text-secondary: ...;
  --tq-text-tertiary: ...;

  --tq-accent-primary: ...;
  --tq-accent-danger: ...;
  --tq-accent-online: ...;

  --tq-radius-sm: ...;
  --tq-radius-md: ...;
  --tq-radius-lg: ...;

  --tq-space-xs: ...;
  --tq-space-sm: ...;
  --tq-space-md: ...;
  --tq-space-lg: ...;
}
```

这只是结构示意。

值不要宣称是 QQ 精确值。

---

# 24. Design System 第一轮基准

我们当前主要参考：

```text
QQ Android Dark Core UI
```

因此：

```text
Dark = first working implementation
Light = structural placeholder
```

但必须保留 Light 的扩展路径。

不要写：

```text
color: #xxxxxx
```

散布 TGQQ Component。

全部使用 semantic variables。

---

# 25. TGQQ CSS 必须 Scoped

禁止：

```scss
.chatlist-chat {
  ...
}
```

作为 TGQQ 全局修改。

优先：

```scss
.is-tgqq .chatlist-chat {
  ...
}
```

或者更低成本、更轻量的专用 class。

如果使用 Solid Component：

优先 `.module.scss`，遵循仓库 convention。

---

# 26. 不写重型 CSS selector

避免：

```scss
.is-tgqq
  .foo
  > .bar
  div:not(...)
  span:nth-child(...)
```

依赖复杂 DOM 偶然结构。

如果需要稳定 styling：

```text
加一个明确 presentation class
```

通常比深层 selector 更好。

---

# 27. Mobile Shell

新增：

```text
TqMobileShell
```

具体 `.tsx` / imperative implementation 根据现有 mount architecture 决定。

如果用 Solid：

```text
遵循当前 tweb Solid.js 写法
```

不要使用 React API/mental model。

---

# 28. Mobile Shell 状态

定义内部：

```text
MESSAGES
CHANNELS
CONTACTS
DYNAMICS
```

这个状态：

```text
只属于 TGQQ Home
```

绝不能与：

```text
APP_TABS
```

混淆。

建议命名：

```text
TqHomeTab
```

而不是：

```text
APP_TABS extension
```

---

# 29. 默认 Tab

默认：

```text
MESSAGES
```

第一轮切换其他 tab 后再回：

应保持用户选中的：

```text
TqHomeTab
```

至少在当前页面生命周期中。

无需第一轮持久化 IndexedDB。

---

# 30. Mobile Only

第一轮 TGQQ Shell 只针对 mobile。

桌面宽屏：

```text
保持原 tweb UI
```

不要做：

```text
QQ PC 风格
```

也不要让 Bottom Navigation 出现在 desktop 三栏界面。

使用 tweb 当前真实的 mobile/responsive 机制。

不要另外发明：

```ts
window.innerWidth < 700
```

除非当前 repo 本身就是这样抽象的。

---

# 31. Bottom Navigation

实现：

```text
消息
频道
联系人
动态
```

结构：

```text
icon
label
optional badge
```

第一轮 icon 可以使用：

```text
现有 tweb icon
```

或非常简单的 TGQQ-owned icon placeholder。

不要复制 QQ 原始资源。

---

# 32. Bottom Navigation 状态

实现：

```text
normal
selected
pressed
```

消息：

如果能低风险复用现有总 unread badge：

```text
可以显示
```

如果需要自己计算：

```text
本轮不要实现
```

不允许为了一个 badge 新建 unread aggregation。

---

# 33. Bottom Navigation 生命周期

只在：

```text
APP_TABS.CHATLIST
+
mobile
```

显示。

以下情况必须隐藏：

```text
CHAT
PROFILE
auth/login
desktop
modal/fullscreen states where inappropriate
```

不要简单：

```css
position: fixed
```

然后让它永远覆盖所有页面。

---

# 34. Messages Tab

MESSAGES 必须继续承载：

```text
existing tweb chat list
```

不创建自己的：

```text
TqDialogsStore
TqConversation[]
TqMessagePreview
```

第一轮只负责把现有列表放进 TGQQ Shell 的 Messages content area。

---

# 35. 不 clone chatlist DOM

严禁：

```text
复制 #chatlist-container
cloneNode
```

或把 dialogs 重渲染成第二份。

必须保证只有一套真实 dialogs UI/state owner。

---

# 36. 消息点击行为

必须继续使用现有：

```text
DialogElement click
→ tweb navigation
→ setPeer(...)
→ CHAT
```

不要 interception 后自己导航。

如果为 Shell 移动 DOM 破坏了现有 event delegation：

应修复 mount/container 结构，

而不是重新实现点击 handler。

---

# 37. Search 第一轮

不要重写 Telegram 搜索。

如果现有 Search entry 很容易放入 TGQQ Messages 页面：

```text
复用。
```

否则第一轮可以：

```text
保留原有搜索入口
```

而不做到 QQ Search Bar。

QQ-style `TqSearchBar` 放下一轮。

---

# 38. CHANNELS 第一轮

内容：

```text
频道
```

和简单 empty/placeholder。

例如：

```text
频道页将在下一阶段接入 Telegram Broadcast Channels
```

不要实现假数据。

---

# 39. CONTACTS 第一轮

内容：

```text
联系人
```

和简单 placeholder。

可以预留以后 Segments：

```text
分组
好友
群聊
频道
机器人
设备
```

但不要显示假的成员数量。

---

# 40. DYNAMICS 第一轮

内容：

```text
动态
```

简单 placeholder。

不要第一轮接 Stories。

---

# 41. Header

第一轮 Messages Header 可以保持 tweb 原实现。

如果 Shell 不提供 Header 会导致布局明显不可用：

允许实现一个非常基础的：

```text
Account Avatar
Page title/account name
Add
```

但：

```text
不要实现 Drawer
不要实现 QQ status system
```

Avatar 暂时可以保持原 Telegram 行为。

---

# 42. Shell Layout

第一轮核心是验证：

```text
content area
+
bottom navigation
+
safe viewport sizing
```

特别注意：

```text
mobile browser dynamic viewport
safe-area-inset-bottom
keyboard
existing chatlist scroll
```

不要写死：

```text
height: 100vh
```

如果 repo 已经有更安全的 viewport abstraction/CSS variables。

优先复用现有方式。

---

# 43. Bottom Safe Area

需要考虑：

```css
env(safe-area-inset-bottom)
```

但优先查看 tweb 现有 safe area 实现。

不要重复定义冲突变量。

---

# 44. Scroll Owner

Messages 页面：

```text
existing Telegram chat list
```

仍是 scroll owner。

不要包一层：

```css
overflow-y: auto
```

导致：

```text
nested scrolling
```

Channels/Contacts/Dynamics placeholder 可以有自己的普通 content area。

---

# 45. Chat 本轮零视觉改动

TGQQ Shell 完成后：

```text
打开 chat
```

应看到：

```text
原始 tweb Chat
```

这是本轮的正确结果。

不要因为觉得“不像 QQ”就顺手改：

```text
bubble
input
header
background
```

下一轮单独处理。

---

# 46. Profile 同样保留原 tweb

如果打开 Telegram Profile：

```text
原始 tweb Profile
```

即可。

TGQQ Profile 属于后续 Beta。

---

# 47. Telegram Managers 规则

TGQQ UI 本轮原则上甚至不需要直接访问 MTProto。

如果需要数据：

```text
只能使用现有 app managers。
```

严禁 TGQQ Component：

```ts
rootScope.managers.apiManager.invokeApi(...)
```

或类似 raw API 调用。

如果当前 manager 没有能力：

```text
不要为了 placeholder 页面新增协议调用。
```

记录下一轮需求。

---

# 48. 不修改 Network / Storage Core

本轮禁止修改：

```text
MTProto
main worker
SharedWorker protocol
Service Worker networking
auth
API connection
message manager semantics
dialogs storage semantics
IndexedDB Telegram schema
media pipeline
call pipeline
```

除非 upstream 原始构建问题要求修复，并且需要单独报告。

---

# 49. Green / Yellow / Red 分类

完成 Source Survey 后，在：

```text
docs/tgqq/source-survey-v0.1.md
```

明确分类。

## Green

目标：

```text
src/tgqq/**
```

---

## Yellow

可能包括：

```text
app bootstrap
AppImManager
chatlist mount/container
appDialogsManager presentation hook
```

只能进行：

```text
mount
class
container
presentation hook
```

---

## Red

至少：

```text
MTProto
Telegram message semantics
storage
auth
worker internals
upload/download pipeline
calls
```

TGQQ 第一轮不得触碰。

---

# 50. Upstream Patch Ledger

新增：

```text
docs/tgqq/upstream-patches.md
```

每修改一个：

```text
src/** 非 tgqq 文件
index.html
core SCSS
```

都登记。

格式：

```markdown
## TW-UP-001

File:
...

Purpose:
Mount TGQQ mobile shell.

Type:
Yellow

Why upstream modification is necessary:
...

TGQQ fallback:
...

Risk:
Low / Medium / High
```

---

# 51. 目标 Patch Surface

第一轮应尽量做到：

```text
绝大部分新增文件：
src/tgqq/**

现有 tweb 修改：
1~几个集中 integration points
```

如果最终需要修改：

```text
20 个 tweb 核心文件
```

才能 mount 一个 Shell：

说明方案有问题。

重新分析。

---

# 52. 禁止顺手 Refactor Upstream

不要做：

```text
rename
cleanup
format unrelated files
move components
convert imperative code to Solid
convert classes to hooks
```

即使觉得 upstream 代码“不漂亮”。

本项目目标是：

```text
可维护 downstream
```

而不是重构 tweb。

---

# 53. i18n

新增用户可见文本：

```text
消息
频道
联系人
动态
```

优先遵循 tweb 当前国际化机制。

不要：

```tsx
<span>联系人</span>
```

直接硬编码，除非第一轮确实需要短期 prototype，且在报告中明确 TODO。

最好第一轮就走正确 lang mechanism。

修改语言资源时严格遵循 repo `AGENTS.md`，不要手改生成文件。

---

# 54. Accessibility

Bottom Navigation 至少：

```text
button semantics
accessible name
selected state
```

触控面积可用。

不要只做：

```text
<div onclick>
```

没有语义。

---

# 55. 第一轮 Tests

完成后至少运行当前仓库适用的：

```text
typecheck
lint relevant files / lint
production build
```

如果完整 test suite 时间合理：

```text
pnpm test
```

如果 upstream 本身有已知失败：

精确记录。

不要隐瞒。

---

# 56. 手工 Smoke Test

至少验证移动 viewport：

```text
1. 打开已登录 tweb

2. 默认看到 TGQQ Home

3. 默认 Tab = 消息

4. Telegram 原 chat list 正常

5. 列表可以滚动

6. 点击真实 dialog

7. 正确进入 Telegram Chat

8. Bottom Navigation 消失

9. Chat 可以加载历史消息

10. Back

11. 返回 TGQQ Home

12. Bottom Navigation 恢复

13. 切换 频道

14. 切换 联系人

15. 切换 动态

16. 回到 消息

17. Telegram chat list 没有重建/丢失明显状态

18. Desktop viewport 仍可使用原 tweb
```

---

# 57. Telegram 功能 Smoke Test

如果环境允许：

```text
打开私聊
发送普通文字
收到消息
返回列表
未读/预览仍正常
```

本轮没有改 Chat，因此若这一步坏掉：

必须优先检查 Shell/Navigation integration。

---

# 58. Account / Auth Smoke

至少确认：

```text
登录流程没有被 TGQQ Shell 注入影响
```

TGQQ Shell：

```text
只应该在主聊天应用已经进入正确状态后 mount
```

不要让登录页底部出现：

```text
消息 / 频道 / 联系人 / 动态
```

---

# 59. 第一轮 Source Survey 文档

新增：

```text
docs/tgqq/source-survey-v0.1.md
```

至少包含：

```text
Current checkout SHA

App bootstrap

Top-level navigation

CHATLIST owner

Chat list owner

Dialog element owner

Dialog click flow

Mobile/desktop responsive owner

Contacts source

Chat owner

Bubble owner

Composer owner

Theme owner

Safe TGQQ mount point

Expected next-round hook points

Files that should remain untouched
```

---

# 60. 第一轮必须输出 dialogs-hook-plan

文件：

```text
docs/tgqq/dialogs-hook-plan.md
```

为下一轮回答：

```text
QQ Conversation layout
该怎样利用现有 DOM？

未读 Badge 如何放头像右上？

哪些只用 SCSS？

哪些需要 class hook？

哪些 absolutely must not be rewritten？
```

---

# 61. 第一轮必须输出 chat-hook-plan

文件：

```text
docs/tgqq/chat-hook-plan.md
```

为下一阶段回答：

```text
Chat Header
Bubble
Own Avatar
Time Divider
Composer
```

每项标：

```text
CSS only

CSS + class hook

small DOM hook

high risk / defer
```

---

# 62. 特别分析 Composer

虽然本轮不修改，但调查必须足够深入。

必须回答：

```text
现有输入 DOM 是否可以通过 layout CSS
形成两行结构？

现有 Send button 能否移动？

现有 Emoji button 能否移动？

现有 voice recording control 能否移动？

Gallery/Camera/File shortcut
是否已有可调用现有行为？

哪些控件不能随意 reparent，
因为状态/animation 依赖父 DOM？
```

这是下一轮是否顺利的关键。

---

# 63. 特别分析 outgoing avatar

必须确认：

```text
当前 bubble renderer
如何知道 peerId / senderId？

是否已经渲染头像？

群聊和私聊差异？

outgoing message 的 sender avatar
有没有现成 DOM？

如果没有，
在哪里插入 presentation-only avatar
对 grouped bubble 风险最小？
```

本轮只记录。

---

# 64. 不做 Metadata

第一轮不要创建：

```text
IndexedDB TGQQ Metadata
```

因为：

```text
好友分组
特别关心
```

尚未进入本轮。

避免同时验证：

```text
Shell integration
+
new persistence layer
```

---

# 65. 不做 TWA

不要加入：

```text
Android
Bubblewrap
assetlinks.json
TWA manifest
```

本轮只验证：

```text
Browser / PWA web client architecture
```

Android packaging 是 TGQQ Web Alpha 稳定后的独立阶段。

---

# 66. Git 行为

除非用户明确要求：

```text
不要 commit
不要 push
不要 force checkout
不要 rebase 用户分支
```

最终保留 working tree 供用户 review。

---

# 67. 不要删除原 tweb Shell

TGQQ Shell 必须是：

```text
可关闭的 presentation mode
```

而不是：

```text
永久删除 sidebar
永久删除原 chatlist layout
```

Feature Flag OFF：

```text
应尽可能恢复 upstream tweb 原运行方式。
```

---

# 68. Fallback 验证

必须手工测试：

```text
tqFlags.shell = false
```

然后：

```text
原 tweb 主界面仍能进入
Chat 仍正常
```

如果 TGQQ shell OFF 后原 UI 已经损坏：

第一轮架构不合格。

---

# 69. 最终 Change Report

完成后必须输出：

## Baseline

```text
SHA:
Branch:
Node:
pnpm:
```

## Baseline status

```text
typecheck before:
build before:
preview before:
```

## Architecture findings

```text
App shell:
Navigation:
Dialogs:
Contacts:
Chat:
Composer:
Theme:
```

## Added files

完整列出：

```text
src/tgqq/**
