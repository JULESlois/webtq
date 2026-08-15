# Round 20 — 聊天页收尾：顶栏通话图标 + 已读双勾 + 单行输入区（报告）

- 日期：2026-08-15
- 前置：Round 19 头像/角标/搜索栏全 PASS（round19-avatars-badge-search-report.md）；Round 20 承接聊天页改造
- 循环：codebuddy 聊天页差距审计（`/tmp/cb_chataudit_out.txt`，参考 `group-chat-view.jpg`/`topbar_crop.jpg`/`tb_input.jpg`）→ 逐项像素核实 → 修复 → build/shoot → puppeteer 自验（`/tmp/verify20.js` 12 项全 PASS）→ 本报告

## 1. QQ9 参考规格（像素实测）

- **顶栏三图标**（`topbar_crop.jpg` 540×60 裁片）：电话 x410-430 灰 `rgb(67,67,67)`≈`#6c6c6c`、视频 x459-474 蓝 `rgb(46,165,233)`≈`#28a0de`、更多 x504-519 三圆点；手机/平板均显示。
- **已读标记**（`group-chat-view.jpg` 出站气泡）：时间旁蓝色双勾图标，无任何中文文字。
- **输入区**（`group-chat-view.jpg` 底栏 y768-843 + `tb_input.jpg`）：QQ9 空态为单行 **[表情😊] [输入框「发送消息」] [＋] [蓝色实心发送圆]** ——表情在最左（x29-46，黄 `rgb(255,213,79)`≈`#FFD54F`）、输入框占位文字左对齐（x70-129）、加号紧邻发送（x290-329 深色「+」）、发送为实心蓝圆 `rgb(17,150,219)`≈`#1296db`（x336-371，36px 级）；**无麦克风/图片/相机/文件图标**（语音与多媒体收进「+」菜单）。
- 胶囊底色 `#f7f8fa`、圆角胶囊、占位符灰字「发送消息」；暗色胶囊 `#2f2f2f` 级。

## 2. codebuddy 审计结论与逐项处置

审计 PASS 项：聊天背景纯色、顶栏布局/群名外置、气泡配色/圆角、输入胶囊、左侧表情等。
审计 FAIL 项处置：

| 审计项 | 结论 | 处置 |
| --- | --- | --- |
| #1 输入区 7 图标过多（麦克风/图片/相机/文件/表情/+/发送） | 属实 | 隐藏 voice/gallery/camera/file 4 个媒体键（QQ9 收进「+」菜单），并按参考把表情移到最左、加号移到发送旁，最终 **[表情][输入][＋][发送]** 4 元素单行 |
| #3 发送按钮应为蓝色实心圆 | **误报** | 像素核实 `btn-send` 本就是蓝 `rgb(18,150,219)` 36px 圆、白图标（audit 看的是旧截图），未改动 |
| #4 手机顶栏缺电话/视频图标 | 属实 | tweb 产品 CSS 在 `max-width:600px` 隐藏除菜单外全部 `chat-utils` 按钮（`_chatTopbar.scss` handhelds 规则）；TqTopbar.scss 增加手机端强制显示电话/视频的覆盖（见 3 节） |
| #5 已读标记出现「已读」中文 | 属实 | TqChatBubble.scss 改为 QQ9 双勾：`is-read` 时间状态蓝 `--tq-accent-primary` + 双勾字形，移除「已读」文字 |

## 3. 改动文件

### `src/tgqq/components/TqTopbar.scss`
- 新增 `@media (max-width: 600px)`：`.chat-utils > .btn-icon:has(.tgico-phone)` / `:has(.tgico-videochat)` 强制 `display: inline-flex`——抵消 tweb `_chatTopbar.scss` 的 handhelds 隐藏规则（真实 app 的 `ButtonIcon('phone'/'videochat')` 与 fixture 同为 `.btn-icon` + `.tgico-*` span，选择器两边通用）。
- 电话/视频/更多图标：隐藏 tgico 字形，用 CSS mask 注入 QQ9 风格实心图标——电话灰 `#6c6c6c`、视频蓝 `#28a0de`、更多三圆点；`html.night` 下电话 `--tq-text-secondary`、视频 `--tq-accent-primary`。
- 移动端返回箭头：QQ9 chevron-left mask 覆盖（沿用）。

### `src/tgqq/components/TqChatBubble.scss`
- 出站气泡时间状态：`&.is-read .time-sending-status` 蓝 `--tq-accent-primary` + 0.4px 描边加粗双勾；`&.is-sent` 无标记（QQ9：未读无勾、已读蓝双勾）；删除「已读」文字注入。

### `src/tgqq/design/chatInput.scss`
- 单行 grid（6 列）：`[表情 col1] [输入 col2-3] [＋ col5] [发送 col6]`；`tq-quick-voice/gallery/camera/file` 全部 `display:none`（QQ9 多媒体收进「+」菜单；语音录制仍可经 tweb 变体发送键/长按流程）。
- 输入容器 `width:auto !important` 修复 grid 下 tweb `width:1%` 塌陷；按钮统一 36px 圆形、hover 蓝。

### 夹具 `docs/tgqq/fixtures/`
- `mobile-chat.html` / `group-chat.html`：顶栏 `chat-utils` 增加 电话（`title=语音通话`）+ 视频（`title=视频通话`）按钮（与真实 `ButtonIcon` 结构一致）；输入区保留 `.attach-file`/`.toggle-emoticons`/`.tq-quick-*`/`.btn-send`。
- `fixture.css`：`.btn-icon` 基础样式、`#f7f8fa` 胶囊、蓝发送圆等（沿用上轮）；颜色/形状主规则由构建产物 `tgqq.css`（来自上述 scss）提供。

## 4. 验证结果

### puppeteer computed-style 自验（`/tmp/verify20.js`）—— 12/12 PASS
- 顶栏：手机端电话可见（灰 `rgb(108,108,108)`）、视频可见（蓝 `rgb(40,160,222)`）、更多可见；暗色电话 `rgb(179,179,179)`、视频 `rgb(78,176,245)`。
- 已读：`is-read` 时间状态 蓝 `rgb(18,150,219)` 19px 双勾字形、`::after` 无内容（无「已读」文字）；暗色蓝 `rgb(78,176,245)`。
- 输入区：voice/gallery/camera/file 均 `display:none`；可见元素 x 序 `emoji(43.7) < input(89.3) < attach(257) < send(318)` 单行递增；发送 36px 蓝圆。
- 与参考几何对照：表情左（参考 x29-46 / 实现 x44-80）、占位文字左对齐（参考 x70-129 / 实现 x97-157）、加号紧邻发送（参考 x290-329 / 实现 x257-293）、发送圆右端（参考 x336-371 / 实现 x318-354）——排列模式一致。

### 像素复核
- `mobile-chat.png` 顶栏裁片：电话(灰)/视频(蓝)/更多(三圆点) 三图标在列，群聊同构。
- 参考图输入区逐像素分析：仅 表情黄 `(255,213,79)` 与 发送蓝 `(17,150,219)` 两个饱和色块 + 深色「+」字形；tb_input（暗色）同构 [表情][输入][发送]。
- 暗色 `mobile-chat-dark.png`：胶囊 `#2f2f2f`、发送蓝 `(78,176,245)`、表情黄 `(255,213,79)`。
+
+### codebuddy 终审（`/tmp/cb_final20_out.txt`）—— 4/4 全部 PASS
+- A 顶栏：手机/平板三图标（电话灰、视频蓝、更多三点）与 `topbar_crop.jpg` 同构，暗色电话/视频色值吻合；返回箭头/头像/标题位置一致。
+- B 已读：出站气泡时间旁蓝色双勾、无任何中文；未读消息无标记；暗色亮蓝双勾。
+- C 输入区：`[表情][输入框 发送消息 左对齐][＋][蓝色实心发送圆]` 与参考几何一致；voice/gallery/camera/file 均 `display:none`；胶囊浅色 `#f7f8fa` / 暗色 `#2f2f2f`；回复态布局不受影响。
+- D 暗色体系：顶栏/气泡/胶囊/发送键/表情/双勾全组件同构，仅色板切换。

## 5. 记账

- 本轮源码改动：`src/tgqq/components/TqTopbar.scss`、`src/tgqq/components/TqChatBubble.scss`、`src/tgqq/design/chatInput.scss`（均在 `src/tgqq/` 私有目录），无 upstream 补丁；夹具 `docs/tgqq/fixtures/mobile-chat.html`、`group-chat.html`、`css/fixture.css`。
- `shots/*` 42 张重新生成（`bash docs/tgqq/fixtures/shoot.sh`）。
- 未提交（延续惯例）。
- 遗留开放项：真实 app 内 `:has()` 选择器与 morphing 发送键在真实会话中需复验；「+」菜单内的语音/多媒体入口（QQ9 样式面板）留待后续轮次；群聊顶栏视频按钮为「发起群通话」语义（与 QQ9 群聊一致）。
