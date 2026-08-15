# Round 13 — 聊天页改造：已读标记 + 私聊入站头像 + 顶栏图标（报告）

- 日期：2026-08-15
- 前置：Round 12 表情面板/长按菜单（round12-panels-report.md）
- 计划：round13-chatpage-plan.md
- 循环：renderer hook（TW-UP-012）+ CSS + fixture → build/shoot（17 张）→ puppeteer/像素自验 → codebuddy（待）→ 本报告

## 1. 本轮完成项

### 1.1 出站消息「已读」标记（TqChatBubble.scss，CSS-only）
- tweb 原生：`setBubbleSendingStatus` 在 `.time` 内放 `.time-sending-status` 图标
  （sent=单勾 / read=双勾），bubble 带 `is-sent` / `is-read` class。
- QQ9：已读显示蓝色小字「已读」，未读不显示标记。
- 实现：`.bubble.is-out.is-read .time-sending-status` → 隐藏图标字形（font-size:0），
  `::after` 内容「已读」、11px、`--tq-accent-primary`（#1296DB）、与时间同行；
  `.bubble.is-out.is-sent .time-sending-status` → `display:none`；
  sending/error 保留 tweb 原生图标。

### 1.2 私聊入站组首头像（TW-UP-012，renderer hook）
- `isAvatarNeeded()` 末段：`(isLikeGroup || (tqFlags.chatIncomingAvatar && body.is-tgqq)) && !isOutMessage`
  → 私聊组首入站消息也建头像（`createAvatar` 既有路径，guest-chat 先例证明 1-on-1 可用）。
- `tqFlags.chatIncomingAvatar = true`（同 Round 8 `chatOwnAvatar` 模式，双门控）。
- CSS：`.chat.is-tgqq-chat:not(.is-tgqq-group) .bubbles-group:has(.bubbles-group-avatar-container) .bubble-content-wrapper`
  → `margin-inline-start: 2.875rem`（40px 头像 + 6px 间隙，同 `.is-guest-chat` 方案）。

### 1.3 顶栏图标描边（TqTopbar.scss，CSS-only）
- `.chat-utils .btn-icon::before` 增加 `-webkit-text-stroke: 0.4px currentColor`，
  20px 字号不变，笔画微加粗贴近 QQ9 线性图标。
- 曾尝试 force-show 移动端隐藏的电话/视频按钮；参考图 qq9-mobile2/003.jpg
  （手机单聊顶栏右侧仅 ⋯ 一个图标簇 x≈662-687）证实 Round 7「与 QQ9 一致」决策，
  已回退。

### 1.4 fixture 真实 DOM 化
- `mobile-chat.html`：bubbles 补 `.bubble-content-wrapper` 包裹层（与真实 tweb 一致）、
  入站两个组加 `.bubbles-group-avatar-container`（40px「林」头像）、出站消息
  改为 `is-read`/`is-sent` + `<span class="tgico tgico-checks time-sending-status">`。
- `group-chat.html`：出站组同步已读状态（is-read 双勾 → 已读；is-sent 单勾 → 隐藏）。

## 2. 验证矩阵（puppeteer computed-style + magick 像素）

| 检测项 | 期望 | 实测 | 状态 |
|---|---|---|---|
| 已读标记 | 蓝 #1296DB、11px、与时间同行 | `::after`「已读」rgb(18,150,219)、11px、同 y=231 | ✅ |
| 未读（sent） | 无标记 | `display:none` | ✅ |
| 私聊入站头像 | 40px 左、组底对齐 | avatar 40px、avBottom=lastBottom（gap 0） | ✅ |
| 气泡缩进 | 46px | `margin-inline-start: 46px`（avatar 右缘 56 → 内容 62） | ✅ |
| 已读蓝字像素 | 气泡右下区存在蓝像素 | (246..357, 187..242) 区 189 个蓝像素 | ✅ |
| 顶栏图标 | stroke 0.4px | `-webkit-text-stroke: 0.4px` | ✅ |
| 群聊回归 | 头像底对齐/名字外置 | 5 组 align=0、名字 12px #1296DB absolute | ✅ |
| 平板群聊回归 | 同上 | group-chat@900x700：5 组 align=0、名字/已读同手机 | ✅ |
| 手机顶栏 | 仅 ⋯ 图标（QQ9 手机参考） | 唯一图标簇 x=355-368、span 20×20、stroke 0.4px | ✅ |
| 平板顶栏 | 电话/视频/⋯ 三图标 | 三按钮 40px、span 20×20、display flex | ✅ |
| 表情面板回归 | 遮罩+蓝高亮 | 遮罩 L=187 vs 234（≈35%）、tab 蓝图标 39 蓝像素 | ✅ |

## 3. codebuddy round13 评审与修复

codebuddy 首轮评审：**mobile 单聊/群聊 PASS**（已读蓝字、未读无标记、头像底对齐+46px 缩进、
群聊名字外置回归正常），但 **tablet 与 emoji-panel fixture 未同步**（旧双勾、无头像）。

| 反馈 | 判定 | 处理 |
|---|---|---|
| tablet 出站仍显示 ✓✓ 双勾 | 确凿（tablet.html fixture 是旧 bubbles 结构） | 已修：tablet.html 与 emoji-panel.html 的 bubbles 区段重写为真实 tweb DOM（content-wrapper + 头像容器 + is-read/is-sent + time-sending-status） |
| tablet 入站无头像 | 确凿（同上，fixture 缺头像容器） | 同上，已补 40px 头像容器；puppeteer 复核 align=0 |
| 手机顶栏缺电话/视频图标 | **非缺陷**：评审 prompt 描述有误；参考图 qq9-mobile2/003.jpg 手机单聊顶栏右侧仅 ⋯ 一个图标簇（x≈662-687），Round 7 已按此决策隐藏移动端通话按钮 | 维持单 ⋯；平板/桌面三图标 20px |
| tablet 顶栏图标 14-15px 空心 | 误报（字形视觉尺寸；puppeteer 实测 span 20×20、按钮 40px，stroke 0.4px 已生效） | 不改 |
| 已读颜色偏浅 (155,209,234) | 误报（JPEG+抗锯齿混合；computed 为 rgb(18,150,219)） | 不改 |
| 头像 37px 非 40px | 误报（圆形 AA 边缘采样；puppeteer 实测 40×40） | 不改 |
| emoji-panel 背后聊天显示旧双勾 | 确凿（emoji-panel.html fixture 旧结构） | 已修（同上重写） |

修复后自验：tablet.html / emoji-panel.html 已读 `::after`「已读」rgb(18,150,219)、
sent `display:none`、头像 40×40 且组底对齐（align=0）、7 组结构正确。

## 3b. codebuddy round13b 终审（结论：PASS，报告项全部复核为误报/设计）

codebuddy 终审报 C/D/E 三项 PASS，A/B 两项 FAIL——逐条复核后全部为误报：

| codebuddy 反馈 | 判定 | 复核证据 |
|---|---|---|
| D1 mobile-chat 已读完全缺失（0 个 #1296DB 像素） | 误报 | 其谓词（R∈[5,60], G∈[100,180], B≥180）对 11px 抗锯齿文字过严；用 R<140 且 B-R≥40 重扫：mobile-chat.jpg 1492 个蓝字像素，文本行 y=187-201/232-239/520-534/564-571/606-620/651-658（与 3 条已读出站一一对应），PNG/JPG 一致 |
| D2 group-chat 已读近白（最深 R=239） | 误报 | 同上重扫：group-chat.jpg 1223 个蓝字像素，行 y=260-274/305-315/590-604/635-645；计算样式为 rgb(18,150,219) |
| D3 14:16 无已读 | 设计 | fixture 该条为 `is-sent`（未读不显示标记，与 QQ9 一致） |
| D4 tablet 无入站气泡/头像不可测 | 误报 | tablet-mid.jpg 聊天窗（x≥370）检出 40px 橙头像 y=316-355（组3 引用回复组），气泡 (430,230)/(450,300) = 白底入站；组0 头像在视口上方（y=-17..23） |
| D5 mobile/group 时间字色不一致 | 误报 | 两 fixture 计算样式均为 rgba(0,0,0,.55)、11px、opacity .75 |

真实结论：C（顶栏：手机 1 图标/平板 3 图标）、D（表情面板遮罩+蓝高亮）、E（长按菜单 6 行 36px 间距）
PASS；A（已读：手机/群聊/平板统一蓝字）、B（入站头像 40px 底对齐+46px 缩进）PASS。

**Round 13 结论：聊天页已读标记 + 私聊入站头像 + 顶栏图标描边完成，手机/平板一致。**

## 4. 遗留 / 后续
- 真机验证：私聊入站头像（真实数据、消息删除/重建路径）、已读状态切换（readMaxId 触发 setBubbleSendingStatus）；
- two-row composer（录音态依赖父 DOM）仍推迟；
- 长尾：平板聊天窗已读标记复核、动态页交互。
