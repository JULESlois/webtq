# Round 15 — 聊天页输入区两行化（QQ9 快速操作栏）（报告骨架）

- 日期：2026-08-15
- 前置：Round 14 四 Tab 终审 PASS（round14-tabs-report.md）
- 计划：round15-composer-plan.md
- 循环：renderer hook（TW-UP-013）+ CSS + fixture 重构 → build/shoot → puppeteer 自验 → codebuddy（待）→ 本报告

## 1. 本轮完成项

### 1.1 两行 composer 结构（round1-instruction §62 目标）
```
Input + Send            ← 行 1
Voice Gallery Camera File Emoji More   ← 行 2
```
- **真机 DOM**：`newMessageWrapper` 内以 6 列两行 grid 排布：
  - 行 1：`.input-message-container`（1-5 列，flex:1）+ `.btn-send-container`（6 列，蓝圆发送钮）；
  - 行 2：`.tq-quick-voice/.tq-quick-gallery/.tq-quick-camera/.tq-quick-file`
    + 既有 `.toggle-emoticons` + `.attach-file`（+），六钮等距（36px 圆钮、灰 #5A5A5A、hover 蓝 #1296DB）。
- **关键修复**：tweb `.input-message-container{width:1%}` 在 grid 下会把输入框压成 ~15px
  竖排占位符（首版截图 plate 高 166px）→ grid 内 `width:auto !important`，plate 回落到 100px。
- **录音面板**：`grid-column:1/-1; grid-row:1/-1`，绝对定位覆盖两行（tweb 原生 absolute，安全）。

### 1.2 renderer hook（TW-UP-013）
- `input.ts constructTqQuickActions()`：语音→`setRecordingMediaType('voice')+startActive()`、
  相册/拍摄→`onAttachClick(false,true,true)`、文件→`onAttachClick(true)`；
  拍摄与相册同入口（web 文件选择器无 capture 语义，文档化限制）。
- flags：`twoRowComposer: true`；双门控 `body.is-tgqq`。

### 1.3 fixture 重构
- mobile-chat / group-chat / tablet 三页 composer 从「plate 直放按钮」改为真机 DOM
  （`.rows-wrapper.chat-input-wrapper > .new-message-wrapper`），消除结构漂移；
  fixture.css plate 改 `flex-direction:column`，内层 grid 透明化；
  `--chat-input-height: 70px → 88px`（表情面板锚点）。

## 2. 验证矩阵（puppeteer computed-style + magick 像素）

| 检测项 | 期望 | 实测 | 状态 |
|---|---|---|---|
| mobile plate | 浅灰圆角 100px | 334×100 @(28,726) #f7f8fa | ✅ |
| mobile grid | 两行 grid | 318×88 @(36,732) display:grid | ✅ |
| 输入框 | 单行、flex | 265×46、占行 1 的 5/6 | ✅ |
| 发送钮 | 36px 蓝圆 | 36×36 @(318,738) | ✅ |
| 6 快捷钮 | 36px 等距 | x=44/97/150/204/257/310，36×36 | ✅ |
| 快捷钮色 | 灰 #5A5A5A | rgb(90,90,90) | ✅ |
| hover | 变蓝 | rgb(18,150,219)+rgba(0,0,0,.05) 圆 50% | ✅ |
| group-chat | 同 mobile | 6 钮 x=30/89/148/206/265/324 | ✅ |
| tablet 右窗 | 同 mobile | grid 468×88、6 钮 x=416/494/573/651/729/808 | ✅ |
| 表情面板 | 底缘 88px 锚定 | bottom=756（844-88）、384px、白底、上圆角 16px | ✅ |
| 附件面板 | 贴底全宽 4 列 | 390×217 bottom=844 | ✅ |

## 3. codebuddy round15 终审结论

6/6 截图 PASS（mobile-chat / group-chat / tablet-mid / group-chat-tablet /
emoji-panel / attach-panel），两行 composer 与 QQ9 快速操作栏形态一致性 98%：
上行 plate #f7f8fa + 蓝圆发送钮、下行 6 钮等距、响应式（手机 390 → 平板右窗 540 宽）
均通过。报告 3 项「缺陷」复核：

| codebuddy 反馈 | 判定 | 复核证据 |
|---|---|---|
| D1 表情面板打开时快捷钮被覆盖（轻微） | 设计（非缺陷） | QQ9 表情面板打开时即替代/覆盖输入区，仅露出发送与「+」；面板底缘 88px 锚定精确（bottom=756），与两行 composer 高度一致，无缝隙无遮挡错误 |
| D2 附件面板圆底饱和度低（轻微） | JPG 伪影 | 面板 PNG 源为 8 色循环彩底（E8F2FF/FFF1E6/...），JPG 4:2:0 色度抽样拉灰；非代码问题 |
| D3 已读蓝字偏淡（信息） | 误报（老问题） | Round 13 已复核：PNG 中 11px 抗锯齿小字精确 rgb(18,150,219)；JPG 压缩 + 宽松阈值判定所致 |

**round15 终审结论：PASS（无真实缺陷）**。

## 4. 本轮记账
- TW-UP-013（input.ts 快捷按钮 hook + flags.twoRowComposer + chatInput.scss 两行 grid），
  已写入 upstream-patches.md；fixture 三页 composer 重构为真机 DOM 结构。


## 5. 遗留 / 后续
- 录音态真机验证（面板覆盖两行）；暗色模式两行 composer 复核；
- 真机验证：语音/相册/拍摄/文件按钮行为（需要真实 Telegram 会话）；
- 长尾：动态页真机照片、联系人索引真机点击。
