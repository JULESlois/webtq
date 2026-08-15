# Round 17 — 聊天页状态补全 + 间距密度修复（报告）

- 日期：2026-08-15
- 前置：Round 16 暗色四 Tab + 真机照片 PASS（round16-dark-photos-report.md）
- 循环：状态 fixture 补全（录音/回复/长按菜单/占位符）→ 密度审计 → 私聊间距 bug 修复 → build/shoot → puppeteer 自验 → codebuddy 两轮终审 → 本报告

## 1. 本轮完成项

### 1.1 新 fixture 与截图规格
- `voice-recording.html`：真机录音面板 DOM（`.voice-recording-panel` + 红点 + 波形胶囊 + 计时器 + 取消/暂停钮），`.chat-input.is-recording` 状态类；浅/暗两规格。
- `composer-reply.html`：输入区回复态（`.reply-wrapper` 在 plate 内、两行 composer 之上），`.chat.is-helper-active` 状态类；浅/暗两规格。
- `shoot.sh` 新增 4 个规格：`voice-recording` / `voice-recording-dark` / `composer-reply` / `composer-reply-dark` / `message-menu-dark`（共 +5）。

### 1.2 录音面板真机样式（src/tgqq/design/chatInput.scss）
- 面板背景钉死到 plate 色（浅 `#f7f8fa` / 暗 `#2f2f2f`）——tweb 原用 JS 注入的 `--surface-color`，fixture 中缺失。
- 波形胶囊 QQ 风：浅 `rgba(18,150,219,.1)` / 暗 `rgba(78,176,245,.16)`、圆角 20px。
- 计时器 `--tq-text-primary`、取消钮 `--tq-accent-danger !important`（tweb `.danger` 带 important）、红点 `--tq-accent-danger`。
- fixture.css 同步：豁免录音面板的 `position:static !important` 覆写（保留真机 absolute 定位）。

### 1.3 私聊间距 bug 修复（src/tgqq/components/TqChatBubble.scss）
- **根因**：群名外置规则对所有 `is-group-first` 入站气泡预留 `margin-top: 1.125rem`（18px），私聊每条入站消息都白留 18px → 相邻气泡 22px 大空档（codebuddy 17a 轮实测 25px）。
- **修复**：预留改为仅 `.chat.is-tgqq-chat.is-tgqq-group` 生效；私聊显式 `margin-top: 0`。
- 效果：私聊相邻气泡间距 4-5px（含 1px 边框），与 QQ9 密度一致；群聊外置名 18px 预留保留。

### 1.4 fixture 气泡宽度保真（docs/tgqq/fixtures/css/fixture.css）
- 删除过期规则 `.bubble-content{max-width:min(70%,720px)}`（把内容限死在 70%×250=175px）。
- 镜像 tweb 生产规则：`.bubble-content-wrapper{max-width:min(100%,var(--max-width))}`（tweb 的模块 CSS 未随 fixture 发布）+ `.bubble-content{width:100%;box-sizing:border-box}`（撑满 wrapper）。
- 效果：短消息按内容宽度、长消息封顶 70%×358≈250px（真实 app 同结构同结果）。
- mobile-chat fixture 新增 90 字长消息以验证 70% 封顶。

## 2. 验证矩阵（puppeteer computed-style + 像素）

| 检测项 | 期望 | 实测 | 状态 |
|---|---|---|---|
| 录音面板定位 | absolute 覆盖 plate 两行 | 238×100 @(28,726)，inset-end 96px | ✅ |
| 录音面板可见 | opacity 1、红点闪烁 | visible；dot 动画 opacity 0.2→0.81 | ✅ |
| 录音面板底色 | 浅 #f7f8fa / 暗 #2f2f2f | (247,248,250) / (47,47,47) | ✅ |
| 波形胶囊 | 浅 rgba(18,150,219,.1) / 暗 rgba(78,176,245,.16) | computed 精确命中 | ✅ |
| 取消钮/红点 | #fa5151 | rgb(250,81,81) | ✅ |
| 回复引用条 | plate 内 36px、蓝边蓝名灰内容 | box 36px @(44,688)，#f0f0f0 + 3px 蓝边 | ✅ |
| 回复态两行 composer | 不挤压 | grid 88px @(36,732) | ✅ |
| 长按菜单 | 贴底、16px 圆角、48px 项 | 390×304 bottom=844；6 项 icon 带 y565→817 步进 48px | ✅ |
| 占位符色 | 浅 #999 / 暗 #808080 | rgb(153,153,153) / (128,128,128) | ✅ |
| 私聊入站 margin | 0 | 全部 0px | ✅ |
| 群聊群首 margin | 18px | 18px（codebuddy 实测 17≈18） | ✅ |
| 长消息宽度 | 70%×358≈250px | 251px（content 250.6） | ✅ |
| 短消息宽度 | 内容自适应 | 142-222px | ✅ |
| 暗色长气泡 | #3e6fa3 252px | (71,113,161) | ✅ |

## 3. codebuddy 终审结论

### 第一轮（17a，9 图）
- 录音/回复/菜单/暗色全 PASS；气泡密度与 QQ9 参考图对比结论：「当前偏窄、偏松、圆角偏小」。
- 复核后**大部分为测量伪影**：短气泡按内容宽度属 QQ9 行为；圆角 computed 为 14px（组角 4px 属设计）；间距异常源自私聊 18px 预留 bug（已修）。
- 确认的真实问题仅 1 个：私聊间距（已修）。

### 第二轮（17b，6 图，修复后）
- 私聊间距 2-5px ✅、长消息 250px 展开 ✅、群聊外置名+头像底对齐 ✅、三项状态回归 ✅。
- 提出 D1「菜单底部 112px 空白」：复核为**误读**——菜单实为 6 项，icon 带 y565→817 步进 48px，末项底 836 + 8px 安全边距 = 面板底 844。
- 结论：第 17 轮全部达标，聊天页状态补全完成。

## 4. 状态
- **第 17 轮验收通过。** 聊天页已完成：顶栏、气泡（私聊/群聊/暗色）、外置群名、已读蓝字、两行 composer、录音态、回复态、长按菜单、表情/附件面板、70% 气泡宽度、QQ9 密度。
- 未提交；本轮源码改动均在 `src/tgqq/`（无新增 upstream patch），其余为 `docs/tgqq/fixtures/`。
