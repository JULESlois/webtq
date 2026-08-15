# Round 13 计划 — 聊天页改造：已读标记 + 私聊入站头像 + 顶栏图标

- 日期：2026-08-15
- 前置：Round 12 表情面板/长按菜单完成（报告见 round12-panels-report.md）
- 目标：聊天页三处 QQ9 细节（均为多轮「遗留/后续」清单中的长尾项）

## 范围

### 1. 出站消息「已读」标记（CSS-only，低风险）
- 现状：tweb 在 `.time` 内放 `.time-sending-status` 图标（sent=单勾 checks=双勾），
  气泡 class `is-sent` / `is-read`；QQ9 出站气泡底部是「已读」蓝色小字（已读时），未读不显示勾。
- 方案（TqChatBubble.scss）：
  - `.bubble.is-out.is-read .time-sending-status`：隐藏图标字形（font-size:0），
    `::after` 内容「已读」，10px、`--tq-accent-primary` 蓝、与时间同排；
  - `.bubble.is-out.is-sent .time-sending-status`：`display:none`（QQ9 未读不显示标记）；
  - sending/error 保持 tweb 原生图标。
- fixture：`mobile-chat.html` / `group-chat.html` 改为真实 tweb DOM
  （bubble 加 `is-read`/`is-sent`，`.time` 内加 `<span class="tgico tgico-checks time-sending-status">`）。

### 2. 私聊入站组首头像（renderer hook，TW-UP-012，Yellow 两行）
- 现状：`isAvatarNeeded()` 只给群聊入站（`isLikeGroup && !isOutMessage`）建头像，
  私聊完全不渲染头像；QQ9 单聊在组首显示对方头像（40px、左、底对齐）。
- 方案：`bubbles.ts` `isAvatarNeeded()` 末行改为
  `(this.chat.isLikeGroup || (tqFlags.chatIncomingAvatar && document.body.classList.contains('is-tgqq'))) && !this.chat.isOutMessage(message)`；
  新增 flag `tqFlags.chatIncomingAvatar = true`（同 Round 8 `chatOwnAvatar` 模式）。
- 私有聊天非 TGQQ 皮肤下行为不变（body.is-tgqq 不存在）。
- CSS：`.bubbles-group-avatar` 已通用（40px 左底对齐），私聊沿用；
  可能需给私聊入站 `.bubble-content-wrapper` 加 `margin-inline-start` 腾出头像位
  （群聊原生 CSS 已处理，先验证再定）。
- fixture：`mobile-chat.html` 入站组首加 `.bubbles-group-avatar-container` 头像节点。

### 3. 顶栏图标描边复核（CSS-only，低风险）
- 现状：Round 7 已把 `.chat-utils .btn-icon::before` 设 20px 实心深色；
  评审遗留「笔画偏细」。QQ9 手机聊天顶栏为粗线性图标。
- 参考图核对（qq9-mobile2/003.jpg 手机单聊）：顶栏右侧仅「⋯」一个图标
  （x≈662-687, y≈89-111 唯一深色簇）→ Round 7「电话/视频移动端隐藏（display:none，
  与 QQ9 一致）」决策正确，**不** force-show 通话按钮。
- 方案：`.chat-utils .btn-icon::before` 加 `-webkit-text-stroke: 0.4px` 微加粗
  （对 ⋯ 与平板/桌面三图标均生效），像素验证无改善则回退。

## 验证
- fixture + build/shoot → puppeteer（已读文字色/字号、私聊头像几何、图标 stroke）→
  codebuddy 识图评审 → 报告 round13-chatpage-report.md。
- 回归：群聊（头像底对齐、名字外置）、平板聊天窗。

## 备注
- 已读「已读」文案走 CSS content，不引入 lang 机制（与既有 `::after` 在线状态一致）；
  后续如需 i18n 再改 renderer。
- two-row composer（录音态依赖父 DOM）仍推迟。

## 实施进度（2026-08-15 02:3x）
- [x] TW-UP-012：`bubbles.ts isAvatarNeeded()` 放宽 + `tqFlags.chatIncomingAvatar`
- [x] TqChatBubble.scss：已读「已读」蓝字 / sent 隐藏 / 私聊入站头像列缩进（46px，` :has()` 门控）
- [x] TqTopbar.scss：`.chat-utils .btn-icon::before` 加 `-webkit-text-stroke: 0.4px`；
  曾尝试 force-show 电话/视频按钮，被 qq9-mobile2/003 参考图与 Round 7 决策否决（已回退）
- [x] fixture：mobile-chat.html 重写为真实 tweb DOM（`.bubble-content-wrapper`、
  `.bubbles-group-avatar-container`、`is-read/is-sent` + `.time-sending-status`）；
  group-chat.html 同步已读状态
- [x] 自验（puppeteer + 像素）：已读 #1296DB 11px 与时间同行、sent 隐藏、
  头像 40px 底对齐（align=0）、缩进 46px、顶栏 stroke 0.4px；
  群聊回归：头像底对齐、名字 12px 蓝外置、已读状态正常
- [x] codebuddy round13 + round13b 识图评审（结论 PASS，见报告 §3/§3b）
- [x] 报告 round13-chatpage-report.md
