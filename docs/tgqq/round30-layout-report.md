# TGQQ Round 30: 布局完善 — 真机参考入库 / 气泡改版 / 列表扁平化 / 底导 3Tab / 动态页顶栏

日期：2026-08-17
基准：`52ccc30`（Round 29，已推送）

## 流程

1. 联网搜索到两批**新的真实参考**并入库：
   - `docs/tgqq/ref/qq9-mobile3/`：QQ 9.1.65 内测版真机截图 11 张（vgover.com 体验报告，2025-04）：消息列表整屏 / 会话行细节 / 搜索页 / 聊天输入面板 / 个人抽屉 / 设置 / 动态页。
   - `docs/tgqq/ref/qq9-official/`：腾讯 ISUX 官方 QQ9 设计复盘图 5 张（uisdc.com/qq-9）：图标库 / Light+Dark 列表层级稿 / 聊天页 Before-After / 多端分栏 / 视觉板。
   - 另取 QQ 9.0.0 iOS 发布文 7 张截图（163.com），其中聊天页 `076e5855` 与消息列表 `395c10fc` 成为本轮**气泡与背景色的决定性证据**。
2. codebuddy（hy3）两轮评审：`/tmp/cb_r30_review.md`（12 条修复清单）+ `/tmp/cb_r30_final.md`（回归终审，全部 PASS）。
3. 每条反馈先用 PIL 像素探针对照真机/官方图核实，再落地；误报不采纳（如「气泡应为 #1FA1FF」被真机 9.0.0 实测 #4596F4 推翻；「暗色应 #0F0F12」被官方稿实测 ≈#1C1D1F 推翻；「聊天顶栏返回箭头多余」无真机依据，保留）。

## 关键像素事实（探针实测，均为真机/官方稿读数）

| 项目 | 旧值（推测） | 真机/官方实测 | 处置 |
|---|---|---|---|
| 出站气泡背景 | `#95ecff` 浅青+黑字 | QQ9.0.0 聊天页实测 `#4596F4`（69,150,244），白字，无渐变 | 已改 `--tq-bubble-outgoing-bg:#4596f4`、文字白、时间戳 rgba(255,255,255,.75)；气泡内链接/回复/转发/引用同步改白系 |
| 消息列表背景 | `#f3f2f7` 暖灰 | 9.0.0 与 9.1.65 均为 `#F0F4FF`（240,244,255）冷浅蓝 | 已改 `--tq-surface-page:#f0f4ff`；会话行改扁平（去白卡、去分隔线）；隐藏行内 ✓✓ 已读对勾（QQ 列表不显示） |
| 底部导航条 | 跟随页面色 | 9.1.65 底导 `#F3F2F7`（与列表略暖） | 新增 `--tq-nav-bg:#f3f2f7`（暗色 `#17181b`），导航独立用色 |
| 聊天区背景 | `#f0f4f8` 冷蓝 | 9.0.0 聊天页 `#EDECF1` 中性浅灰 | 已改 `--tq-chat-page:#edecf1` |
| 底导 Tab 数 | 4 Tab（含频道） | 9.1.65 真机 = 3 Tab（消息/联系人/动态，均分；选中=蓝图标+蓝字；动态右上红点） | 已改 3 Tab；「频道」改为联系人页「我的频道」入口行（蓝色渐变井号图标），点按进入频道页 |
| 平板左列宽 | 固定 400px（900 宽时 44%） | 官方多端稿侧栏 ≈30% | 已改 `clamp(340px, 38vw, 400px)`（900→342 / 1180→400 / 1440→400） |
| 暗色头部 | `#2b3d63` 蓝条 | 官方 Dark 稿头部与页面同色 | 已改 `--tq-header-bg:#1a1a1a`；暗色活动行改为 `rgba(78,176,245,.16)` |
| 动态页顶栏 | 头像+「我」+Lv | 9.1.65 真机：左「动态」标题 + 右铃铛/设置 | 已改；并补「分享此刻天空」天气 banner + 「亲密空间」行（真机同位置） |

## 改动文件

- `src/tgqq/design/light.scss` / `dark.scss`：页面/导航/聊天区/气泡色板 + 暗色头部与活动行。
- `src/tgqq/components/TqChatList.scss`：行扁平化、去分隔线、隐藏已读对勾。
- `src/tgqq/components/TqChatBubble.scss`：出站蓝泡内的链接/回复/转发/引用文字改白系。
- `src/tgqq/components/BottomNavigation/index.tsx`：3 Tab（消息/联系人/动态）。
- `src/tgqq/components/BottomNavigation/BottomNavigation.module.scss`：导航条独立背景色。
- `src/tgqq/components/TqSidebar.scss`：导航背景引用 `--tq-nav-bg`。
- `src/tgqq/components/TqTablet.scss`：左列 `clamp(340px,38vw,400px)`。
- `src/tgqq/shell/TqMobileShell.tsx`：联系人页接入频道入口回调。
- `src/tgqq/pages/Contacts/index.tsx` + `.module.scss`：新增「我的频道」入口行。
- `src/tgqq/pages/Dynamics/index.tsx` + `.module.scss`：动态顶栏（标题+铃铛+设置）、天气 banner、亲密空间行。
- `docs/tgqq/fixtures/`：mobile/tablet/tab 三件 fixture 的导航同步为 3 Tab（scoped 类名随构建更新为 `_1j3bc_*`）、联系人「我的频道」行、动态页新模块、fixture.css 新增样式并修复硬编码 `body` 背景（改跟随 `--tq-surface-page`）；61 张截图重拍。
- `docs/tgqq/ref/qq9-mobile3/`、`docs/tgqq/ref/qq9-official/`：新参考图 + README 说明。

## 验证

- 61 张截图全部重拍（无 FAIL）。
- PIL 探针：列表行 `(240,244,255)` 扁平、导航 `(243,242,247)`、气泡中位 `(69,150,244)` 与真机一致、暗色头部 `(26,26,26)` 无蓝条、平板左列 342px 起右窗 `#EDECF1`。
- codebuddy 回归终审 7 项全 PASS，未发现改坏项。

## 说明（有意保留的偏差）

- 手机顶栏右侧保留齿轮（设置入口，QQ 真机为抽屉内入口；无抽屉前保留）。
- 聊天页保留返回箭头与 电话/视频/更多 按钮（9.0.0 iOS 仅汉堡，但 Android 版与官方稿均有通话入口，保留）。
- 频道不再是底导 Tab：QQ 真机频道在左抽屉；本项目以联系人页入口替代，下一轮可考虑左抽屉。
