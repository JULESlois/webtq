# TGQQ Round 29: 布局完善 — 平板导航胶囊 / 平板头部精简 / 通讯录邀请卡 / 暗色硬编码修复

日期：2026-08-16
基准：`7c9746a`（Round 28，已推送）

## 流程

- 用 codebuddy（hy3，视觉模型）对 Round 28 后的关键截图做两轮布局审计：
  - 第一轮（`/tmp/cb_round29_review.md`）：手机消息列表 / 平板主页 / Tab 页 / 暗色。
  - 第二轮（`/tmp/cb_round29b_chat_review.md`）：聊天页（顶栏 / 气泡 / 日期 / 输入区 / 面板）。
- 每一条 codebuddy 反馈都先用 PIL 像素探针对照 QQ9 参考图核实，再落地；误报不采纳。

## 核实结论（关键：codebuddy 两处误报被探针推翻）

| # | codebuddy 反馈 | 像素探针核实 | 处置 |
|---|---|---|---|
| 1 | 手机底导选中态应为「灰下划线+深字」，当前蓝色过重 | **误报**：qq9_000_full.png 底导选中 Tab 图标+文字均为 QQ 蓝 `#0099FF`，无灰下划线 | 不改（现状正确） |
| 2 | 平板底导选中态缺蓝色胶囊 | **属实**：qq9-tablet/001.png 选中 Tab 有浅蓝圆角矩形 `#46B5FA`（30px 宽）包图标 | 已修（见下） |
| 3 | 平板左栏头部应为极简状态条（无头像/昵称） | **属实**：ref 左栏顶部只有状态文本+右侧图标+搜索胶囊 | 已修（见下） |
| 4 | 消息页缺「通讯录好友在用QQ」邀请卡 | **属实**：qq9_000_full.png y226-320 全宽白卡（通讯录图标+一行灰字） | fixture 已加（真实应用注入留待产品决策） |
| 5 | 连续出站气泡组内圆角未压平 | **误报**：CSS 的 `.is-group-middle` 规则早已存在（`:not(.is-group-first):not(.is-group-last)` 4px）；问题是 fixture 没有成组气泡 | fixture 补齐成组气泡（见下） |
| 6 | 出站气泡链接/回复副标题硬编码颜色，暗色可读性差 | **属实**：`#0066cc` / `rgba(0,0,0,0.6)` 无暗色覆盖 | 已修（见下） |

## 改动

### 1. 平板底导选中态胶囊（`src/tgqq/components/BottomNavigation/BottomNavigation.module.scss`）
- 平板（`body.is-tgqq.tq-tablet`）下选中 Tab 的 `.iconWrap`：30×30、圆角 9px、
  背景 `var(--tq-nav-capsule, #46b5fa)`（与 QQ9 参考逐像素一致 `#46B5FA`）、图标白色；
  暗色 `html.night` 下 `#3b95d2`。
- 手机保持蓝图标+蓝文字（探针确认与 QQ9 一致，不加胶囊）。
- 注意：CSS Modules 的 `:global(...) &` 写法会丢作用域（编译后无 body 前缀，会漏到手机），
  已改为顶层 `:global(body.is-tgqq.tq-tablet) .itemSelected .iconWrap`，编译产物已核实。

### 2. 平板左栏头部精简（`src/tgqq/components/TqTablet.scss`）
- `tq-tablet` 下隐藏 `.tgqq-profile-avatar` / `.tgqq-profile-name`；
  保留在线状态文本（12px）+ 右侧 ⊕/齿轮 + 下方搜索胶囊，与 QQ9 平板头部一致。

### 3. 通讯录邀请卡（fixture：`docs/tgqq/fixtures/{mobile,tablet}.html` + `css/fixture.css`）
- 搜索胶囊与会话列表之间插入 `.tq-invite-row`：全宽白卡 92px，通讯录 SVG 图标 +
  「看看手机通讯录里哪些人在用QQ」，随列表滚动（QQ9 语义）。
- 说明：这是 QQ 专属促销元素，真实应用注入需要产品决策（Telegram 语境文案/功能），
  本轮只落在 fixture 作为视觉基准；真实应用与 fixture 的这一差异已在此明示。

### 4. 聊天页 fixture 补齐成组气泡（`docs/tgqq/fixtures/mobile-chat.html`）
- 入站组 2→3 条（首/中/尾），新增一条 `is-in is-grouped` 中间气泡；
- 出站两条孤立气泡改为一个 3 气泡组（`is-group-first` → `is-grouped` 中间 → `is-group-last`）。
- 像素核实：中间气泡右上角为 4px 压平（右边缘 4 行内 370→373 收口），与真实 app 分组一致。

### 5. 暗色硬编码修复（`src/tgqq/components/TqChatBubble.scss`）
- `.bubble.is-out .reply-subtitle` / `.forward`：亮色 `rgba(0,0,0,0.6)` 保留，
  新增 `html.night` 覆盖 `rgba(255,255,255,0.55)`；
- `.bubble.is-out .bubble-content a`：亮色 `#0066cc` 保留，新增 `html.night` 覆盖 `#4cb3f7`。

### 6. 语音录制条最小宽度（`src/tgqq/design/chatInput.scss`）
- `.voice-recording-pill` 补 `min-width: 9rem`，避免波形区在窄屏被压挤。

## 验证

- `vite build` 通过（typecheck 因 TS7 android-arm64 原生二进制缺失跳过，沿用前轮做法）。
- `shoot.sh` 重拍 61 张截图（亮/暗全部成功），`css/tgqq.css`、`css/tweb.css` 从 dist 同步。
- 像素探针（全部通过）：
  - tablet-mid.png 底导选中胶囊：蓝色块 x35-64（30px）、色值 `#46B5FA`，与 QQ9 参考一致；
  - tablet-mid.png 头部：无红色头像像素（avatar 已隐藏）、状态文本在；
  - mobile.png：搜索胶囊下方白卡 y106-198（92px）+ 图标 y141-162，手机底导无胶囊（20px 蓝图标仅字形）；
  - mobile-chat.png 成组气泡中间条右上角 4px 压平确认。
- fixture HTML 结构校验：mobile.html 无错；tablet/mobile-chat 的 3 处结构提示为 HEAD 既有问题，非本轮引入。

## 已知 / 后续

- 聊天页第二轮审计因多数 `qq9-chat` 参考图实为营销图，仅能对照结构；无官方像素坐标，
  建议后续补拍真实 QQ9 聊天页高清截图再对齐细节（顶栏留白、输入区宽度）。
- 频道页参考图（qq9-mobile2/001.jpg 实为消息页）同样缺失，频道内容保真留待高清参考。
- 邀请卡真实应用注入待产品决策（Telegram 语义文案 + DOM 注入稳定性）。
