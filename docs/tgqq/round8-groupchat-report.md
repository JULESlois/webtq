# Round 8 — 群聊聊天页改造：消息头像 QQ9 化 + 超宽屏居中（报告）

- 日期：2026-08-14
- 基线：`e3730e1`（未提交，工作区含 Round 1-7 改动）
- 上游改动：`bubbles.ts` / `bubbleGroups.ts`（TW-UP-010，见 `upstream-patches.md`）
- 循环：改 → `vite build` → `shoot.sh`（11 张）→ puppeteer/magick 验证 → codebuddy 评审 → 本报告

## 1. 本轮完成项

### 1.1 群聊入站头像 QQ9 化（CSS）
- tweb 原生为群聊入站消息组渲染 `bubbles-group-avatar`（40px，底部对齐，sticky）。
- 修正 `TqChatBubble.scss`：头像 32px → **40px**（QQ9 群聊头像尺寸）；`position: static`
  取消 sticky（QQ9 头像随消息组滚动）；`margin-bottom: var(--tq-bubble-margin)` 抵消
  组容器含末条气泡 margin 的 4px 偏差，使头像底边与最后一条气泡底边精确齐平。

### 1.2 群聊出站自头像（renderer hook，TW-UP-010）
- `bubbles.ts isAvatarNeeded()`：群聊 outgoing 消息且 `tqFlags.chatOwnAvatar &&
  body.is-tgqq` 时返回 true → 出站消息组也创建头像（走与入站完全相同的
  `createAvatar`/`avatarNew` 路径，头像即本人）。
- `bubbleGroups.ts createAvatar()`：outgoing 时给头像节点加 `tq-own` class。
- `flags.ts`：`chatOwnAvatar: false → true`。
- CSS：`.bubbles-group-avatar.tq-own { margin-inline-start: auto }` 右侧定位；
  出站气泡 `.bubble-content-wrapper` `margin-inline-end: 2.875rem`（46px）预留头像位。
- 移除 Round 2 的 CSS `::after` 渐变占位（真头像取代）。
- 私聊不受影响：`isLikeGroup=false` 无头像、无缩进。

### 1.3 超宽屏聊天区居中
- `TqTablet.scss`：`#column-center { --chat-width: min(100%, 53rem) }`（848px 上限）。
- 窄于 848px 的列不受影响（tablet-mid/wide 不变），xwide 下聊天内容居中不再贴右。

### 1.4 群聊 fixture
- 新文件 `group-chat.html`（手机 390px + 900px 宽两种截图），真实 tweb DOM：
  `.bubbles-inner.is-chat` + `.bubble > .bubble-content-wrapper > .bubble-content`、
  `bubbles-group-avatar-container > .bubbles-group-avatar.user-avatar(.tq-own) > .avatar`。
- 内容：陈默 3 条（含名字/回复块）、我 2 条（tq-own）、周子昂 1 条（回复我）、我 1 条、陈默 1 条。
- 顶栏：群头像「产」+「产品讨论组」+「128 人」（无在线绿点，区别于私聊）。
- `shoot.sh` 新增 `group-chat` / `group-chat-tablet`，共 11 张截图。

## 2. 验证矩阵（puppeteer computed-style + magick 像素）

| 检测项 | 期望 | 实测 | 状态 |
|---|---|---|---|
| 入站头像尺寸 | 40px | `40px/40px`（inner avatar），`position: static` | ✅ |
| 入站气泡缩进 | 46px | `margin-inline-start: 46px`，气泡 x62（头像 x16-56） | ✅ |
| 出站气泡缩进 | 46px | `margin-inline-end: 46px`，气泡右缘 x328（头像 x334-374） | ✅ |
| 头像底边 vs 气泡底边 | 齐平 | g1: 206=206；g2: 388=388（精确） | ✅ |
| tq-own 右侧定位 | 右缘 | 头像 x334-374 = 16px 右边距 | ✅ |
| 发送者名字 | QQ 蓝 | `rgb(18,150,219)` = #1296DB | ✅ |
| 头像渲染 | 渐变圆 | magick 各头像位采样到 #FF8B4E 渐变像素 | ✅ |
| xwide 居中 | 内容居中 | 蓝气泡 x531-1310（中心 920.5，视口 1440） | ✅ |

## 3. codebuddy round8 评审结论（`/tmp/cb_round8_out.txt`）

**全部 PASS，无严重缺陷。** 逐项：
- 9 个头像全部 40px 圆形、与组末气泡底边对齐（差值 ≤1px）、与气泡无重叠；
- 入站/出站缩进 46px（气泡距屏幕边缘 62px = 16px 页边距 + 46px），左右基本对称；
- 群顶栏头像 40px + 群名 + 「128 人」，无在线绿点（区别于私聊）；
- 出站 #A6E3FF / 入站 #FFFFFF 精确匹配；回复块 3px 蓝条确认。

codebuddy 提示的轻微项（出站侧间距窄 2-3px、头像 39×39 圆角 1px 差）经核实为
JPEG 取整/抗锯齿误差：puppeteer 实测两侧 `margin-inline` 均为精确 46px、头像 CSS
均为 40×40。「第一组只见 2 条」为 fixture 底部锚定 + 首条消息在折叠线上方，非缺陷。

## 4. 环境备注
- `pnpm run typecheck` 依旧失败：TypeScript 7.0.2 native 缺少
  `@typescript/typescript-android-arm64` 平台包（环境问题）；`vite build` 正常，
  TW-UP-010 的改动为纯增量（import + 条件返回 + classList.add），已通过构建。

## 5. 下一轮候选
- 群聊气泡内 sender 名与消息间距微调、消息密度（间距/字号）整体收紧；
- 出站自头像真机跑通验证（需真实账号，fixture 已验证 DOM/CSS 路径）；
- 私聊「+」附件面板（真机行为验证，input.ts 未改）。
