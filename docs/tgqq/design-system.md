下面是针对 **TGQQ × tweb** 新架构重写后的 Design System 文档。

目标不是单纯定义颜色，而是给 Agent 作为长期 UI 开发规范使用。它规定：

* TGQQ UI 层如何设计
* Telegram 原生 UI 与 TGQQ UI 的边界
* CSS Token 体系
* Component 规范
* 页面布局规范
* QQ 风格还原原则
* Dark-first 策略
* Mobile-first 约束
* 后续 Pixel Matching 的扩展方式

建议保存为：

```text
docs/tgqq/design-system.md
```

---

# TGQQ Design System Specification

Version: v0.1
Platform: Telegram Web K / tweb
Target: Mobile Web / PWA
Design Reference: QQ Android Core UI
Status: Active Development

---

# 1. Purpose

TGQQ Design System 是 TGQQ Presentation Layer 的统一设计规范。

目标：

```text
Telegram Web K
        +
TGQQ Design System
        ↓
QQ-style mobile Telegram experience
```

Design System 不负责：

* Telegram protocol
* Telegram state
* Message lifecycle
* Network
* Storage
* Authentication

Design System 只负责：

```text
Visual Language
+
Component Appearance
+
Layout Rules
+
Interaction Consistency
```

---

# 2. Core Design Philosophy

## Rule 1

Telegram owns behavior.

TGQQ owns appearance.

---

错误：

```
为了 QQ UI
修改 Telegram message state
```

正确：

```
Telegram state
      ↓
TGQQ component
      ↓
QQ presentation
```

---

## Rule 2

Prefer composition over replacement.

优先：

```
existing Telegram component
        +
TGQQ style layer
```

而不是：

```
replace Telegram component
```

---

例如：

Dialog:

```
Telegram Dialog State
        +
TGQQ Conversation Style
```

而不是：

```
TqDialogManager
重新实现聊天列表
```

---

# 3. Design System Architecture

目录：

```
src/tgqq/design/

├── tokens.scss

├── themes/
│   ├── dark.scss
│   └── light.scss

├── typography.scss

├── spacing.scss

├── radius.scss

├── shadows.scss

├── animation.scss

└── mixins.scss
```

---

# 4. CSS Variable Strategy

TGQQ 使用 CSS Custom Properties。

禁止：

```scss
color:#1a1a1a;
```

禁止：

```scss
background:#222;
```

所有颜色必须经过 Semantic Token。

---

正确：

```scss
background:
var(--tq-surface-primary);
```

---

# 5. Theme Root

TGQQ Theme 使用：

```css
.is-tgqq
```

作为 root scope。

示例：

```scss
.is-tgqq {

    --tq-surface-page:
        var(--theme-page);

}
```

禁止：

```scss
body {
    background:red;
}
```

因为会污染 Telegram 原 UI。

---

# 6. Theme Strategy

第一阶段：

```
Dark Theme
    ↓
Primary implementation
```

Light Theme：

```
Structure ready
Implementation later
```

原因：

QQ Reference 当前主要为 Dark Mobile UI。

---

# 7. Color System

## 7.1 Surface

页面背景：

```css
--tq-surface-page
```

用途：

```
App background
```

---

一级 Surface:

```css
--tq-surface-primary
```

用途：

```
Cards
Dialogs
Input background
```

---

二级 Surface:

```css
--tq-surface-secondary
```

用途：

```
Search
Secondary panels
Inactive areas
```

---

浮层：

```css
--tq-surface-overlay
```

用途：

```
Popup
Drawer
Modal
```

---

# 8. Text Colors

Primary:

```css
--tq-text-primary
```

用途：

```
Title
Username
Main message
```

---

Secondary:

```css
--tq-text-secondary
```

用途：

```
Preview
Timestamp
Description
```

---

Tertiary:

```css
--tq-text-tertiary
```

用途：

```
Hint
Placeholder
Disabled
```

---

Accent:

```css
--tq-text-accent
```

用途：

```
Links
Selected state
Important action
```

---

# 9. Accent System

Primary:

```css
--tq-accent-primary
```

用途：

```
Selected tab
Button
Online indicator
```

---

Danger:

```css
--tq-accent-danger
```

用途：

```
Delete
Error
Unread urgent
```

---

Online:

```css
--tq-accent-online
```

用途：

```
Online dot
Active status
```

---

# 10. QQ Style Color Direction

TGQQ 不复制 QQ 原始颜色值。

只复刻视觉语言：

特点：

```
Dark neutral background

High contrast text

Soft blue accent

Low saturation cards

Subtle separators

Rounded surfaces
```

---

禁止：

```
qqBlue
qqBlack
qqGray
```

命名。

必须：

```
accentPrimary
surfacePrimary
textSecondary
```

---

# 11. Spacing System

统一使用 4px 基础单位。

Scale:

```
4
8
12
16
20
24
32
40
48
64
```

Token:

```css
--tq-space-xs

--tq-space-sm

--tq-space-md

--tq-space-lg

--tq-space-xl
```

---

# 12. Layout Grid

Mobile 基准：

```
360px ~ 430px viewport
```

主要参考：

```
390px width device
```

---

页面水平 Padding：

默认：

```
16px
```

Dense List:

```
12px
```

Card:

```
16px
```

---

# 13. Radius System

TGQQ 使用明显圆角。

Token:

```css
--tq-radius-sm
```

用途：

```
small button
badge
```

---

```css
--tq-radius-md
```

用途：

```
card
search
input
```

---

```css
--tq-radius-lg
```

用途：

```
bubble
large container
drawer
```

---

默认：

```
Bubble:
18~22px

Card:
16px

Input:
20px+
```

---

# 14. Typography

TGQQ 不直接指定 font-family。

继承 tweb。

只定义：

```
size
weight
line-height
color
```

---

## Title

用途：

```
Page title
Conversation name
```

规格：

```
18px
600
```

---

## Body

用途：

```
Message
Description
```

规格：

```
15-16px
400
```

---

## Caption

用途：

```
Timestamp
Hint
Metadata
```

规格：

```
12-13px
400
```

---

# 15. Icon Rules

图标原则：

```
simple
outline
rounded
```

避免：

```
heavy filled icon
```

---

Icon size:

Small:

```
16px
```

Normal:

```
20px
```

Navigation:

```
24px
```

Large:

```
32px
```

---

# 16. Component Principles

所有 TGQQ Component：

必须：

```
visual only
+
small state
```

禁止：

Component 内：

```
direct MTProto call

direct network

message mutation
```

---

# 17. Component Naming

统一：

```
Tq<ComponentName>
```

例如：

```
TqSearchBar

TqBottomNavigation

TqConversationRow

TqAccountHeader
```

---

禁止：

```
QQSearch

QQCell

QQView
```

因为 TGQQ 是产品名，不是 QQ 官方组件。

---

# 18. Navigation Design

Mobile Bottom Navigation:

```
消息
频道
联系人
动态
```

固定：

```
height:
56~64px
```

---

Structure:

```
[TAB]

icon

label

badge(optional)
```

---

Selected:

```
accentPrimary
```

---

Inactive:

```
textSecondary
```

---

# 19. Page Layout

标准：

```
Page

├── Header

├── Content

└── Bottom Navigation
```

---

禁止：

```
每个页面自己定义 padding
```

必须：

```
TqPageContainer
```

统一。

---

# 20. Header Design

统一：

```
height:
56px
```

结构：

```
Avatar

Title

Actions
```

---

Header 不负责：

```
navigation state
Telegram peer state
```

只负责展示。

---

# 21. Search Bar

QQ 风格：

特点：

```
rounded pill

dark surface

low contrast

full width
```

规格：

```
height:
40-44px
```

---

结构：

```
icon

placeholder

optional action
```

---

# 22. Conversation Row

未来替换 Telegram Dialog appearance。

目标：

```
Avatar

Name

Last message

Time

Badge
```

结构：

```
┌─────────────────┐
│ ○ Name     10:30│
│   Preview    [5]│
└─────────────────┘
```

---

Spacing:

```
height:
72px
```

---

Avatar:

```
48px
```

---

# 23. Avatar System

Sizes:

```
Small:
32

Normal:
48

Large:
80

Profile:
96+
```

---

状态：

```
online dot

badge

special marker
```

全部使用 decorator。

不要修改 avatar source。

---

# 24. Badge System

Unread Badge:

```
circle

high contrast

small
```

位置：

未来目标：

```
Avatar top-right
```

而不是：

```
row end
```

---

但是实现时：

优先：

```
existing Telegram unread state
+
CSS reposition
```

---

# 25. Card System

TGQQ 使用轻卡片。

用途：

```
Profile section

Contact group

Settings item
```

规格：

```
surface-primary

radius-lg

16px padding
```

---

# 26. Drawer Design

未来：

```
Avatar

Account

Menu

Settings
```

宽度：

Mobile:

```
80% viewport
```

最大：

```
320px
```

---

# 27. Chat UI Design Direction

Chat 不属于第一轮 Design System 实现。

但定义目标。

---

## Bubble

Incoming:

```
surface-primary
```

Outgoing:

```
accent related surface
```

---

Radius:

```
18-22px
```

---

禁止：

```
强 Telegram bubble tail
```

目标：

```
QQ-style clean bubble
```

---

# 28. Chat Avatar

目标：

```
Incoming:

avatar + bubble


Outgoing:

bubble + self avatar
```

---

实现原则：

```
presentation decorator
```

不要：

```
replace message renderer
```

---

# 29. Composer Design

目标：

```
Input Row

+

Quick Action Row
```

结构：

```
┌───────────────┐
│ Input     Send│
├───────────────┤
│Voice Gallery +│
└───────────────┘
```

---

禁止：

重新实现：

```
send logic

voice recording

emoji picker

upload
```

---

# 30. Animation

原则：

```
fast
subtle
natural
```

Duration:

```
100ms
150ms
200ms
300ms
```

---

禁止：

```
large bounce

oversized transition
```

---

# 31. Interaction States

所有 Interactive Component 必须考虑：

```
default

hover(optional)

pressed

selected

disabled

loading
```

---

Mobile 重点：

```
pressed
selected
```

---

# 32. Dark Mode Rules

Dark UI 禁止：

纯黑：

```
#000000
```

除非特殊场景。

推荐：

```
near black
```

---

层级通过：

```
surface difference
```

而不是：

```
大量 border
```

---

# 33. Separator

默认：

弱分割。

Token:

```css
--tq-border-subtle
```

禁止：

明显：

```
1px bright line
```

---

# 34. Shadow

Dark mode:

少用 shadow。

优先：

```
surface contrast
```

Overlay:

允许：

```
soft shadow
```

---

# 35. Responsive Rules

Mobile:

```
primary
```

Tablet:

```
adapt
```

Desktop:

```
fallback to tweb layout
```

---

TGQQ 不强制：

```
desktop QQ layout
```

---

# 36. Accessibility

所有按钮：

必须：

```
semantic button

aria-label

keyboard support
```

---

所有 icon-only button：

必须：

```
accessible name
```

---

# 37. Performance Rules

禁止：

组件 render 中：

```
network request

large calculation

manager query
```

---

避免：

```
deep DOM selector

heavy animation

large shadow
```

---

# 38. Telegram Integration Boundary

TGQQ Component 可以：

读取：

```
Telegram manager state
```

不可以：

修改：

```
Telegram core state
```

---

允许：

```
display username

display avatar

display message preview
```

---

禁止：

```
change message send flow
```

---

# 39. Feature Flag Compatibility

所有大型 TGQQ UI：

必须支持：

```
enabled
disabled
```

例如：

```
tgqq-chat-skin=false
```

可以恢复：

```
original tweb style
```

---

# 40. Development Workflow

新增 Component：

顺序：

```
1. Define token

2. Create component

3. Add scoped style

4. Test mobile viewport

5. Compare QQ reference

6. Optimize
```

---

禁止：

```
先写大量 CSS
再补 token
```

---

# 41. Pixel Matching Workflow

QQ Reference 校准：

顺序：

```
Layout
↓
Spacing
↓
Typography
↓
Color
↓
Icon
↓
Animation
```

不要：

先调颜色。

---

# 42. Screenshot Review

每个重要页面：

保存：

```
reference/

qq/

tgqq/
```

比较：

```
Structure

Spacing

Alignment

Hierarchy
```

不是单纯 Pixel Diff。

---

# 43. Current Alpha Scope

Design System v0.1 服务：

必须支持：

```
Mobile Shell

Bottom Navigation

Messages Container

Contacts Placeholder

Channels Placeholder

Dynamics Placeholder
```

---

暂不要求：

```
Chat Bubble

Composer

Profile

Drawer

Metadata UI
```

---

# 44. Final Principles

TGQQ Design System 最终遵循：

```
1.
Telegram owns capability.

2.
TGQQ owns visual language.

3.
Use semantic tokens.

4.
Avoid global CSS pollution.

5.
Prefer composition over replacement.

6.
Reuse Telegram state.

7.
Keep upstream modifications small.

8.
Mobile first.

9.
Dark first.

10.
Pixel matching happens after architecture stability.
```

---

# 45. Agent Implementation Checklist

实现 Design System 时：

```
[ ] src/tgqq/design created

[ ] CSS variables introduced

[ ] Dark theme tokens added

[ ] Light theme structure prepared

[ ] Typography tokens added

[ ] Spacing tokens added

[ ] Radius tokens added

[ ] Component naming follows Tq prefix

[ ] TGQQ CSS scoped

[ ] No Telegram core logic changed

[ ] No hardcoded colors in components

[ ] No hardcoded spacing in components

[ ] Mobile viewport tested
```

---

这份文档应该和上一份 **《TGQQ × tweb 第一轮 Agent 工作指令》** 一起交给 Agent。

二者职责分离：

* **Work Instruction**：告诉 Agent 做什么、改哪里、不改哪里。
* **Design System**：告诉 Agent 所有 UI 代码应该长什么样。

下一步建议继续补一份：

**《TGQQ Component Library Specification.md》**

专门定义：

* TqBottomNavigation
* TqSearchBar
* TqConversationRow
* TqAccountHeader
* TqSegmentTabs
* TqSectionCard

因为 Agent 开始写 UI 时，最容易失控的就是组件边界。
