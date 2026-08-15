# Round 15 计划 — 聊天页输入区两行化（QQ9 快速操作栏）

- 日期：2026-08-15
- 前置：Round 14 四 Tab 终审 PASS（round14-tabs-report.md）
- 目标：实现 round1-instruction.md §62 明确的两行 composer 目标：
  ```
  Input + Send
  ----------------
  Voice Gallery Camera File Emoji More
  ```
  （QQ9 iPad/PC 式：上行输入+发送，下行快捷操作栏；chat-hook-plan.md 已论证
  CSS-only flex/grid 可行，但语音/相册/拍摄/文件四个快捷按钮需最小 renderer hook）

## 范围

### 1. renderer hook（TW-UP-013，最小 DOM 钩子，沿用 TW-UP-011/012 模式）
- `src/tgqq/config/flags.ts`：新增 `twoRowComposer: true`。
- `src/components/chat/input.ts`：`tqFlags.twoRowComposer && body.is-tgqq` 门控下，
  在 `newMessageWrapper` 注入 4 个快捷按钮（`createButtonIcon`，icon 名取自
  src/icons.ts：microphone_filled / image / camera / document）：
  - 语音：click → `setRecordingMediaType('voice')` + `recordingController.startActive()`
    （沿用 tweb 既有 mic 行为；权限/慢速模式错误由 ChatRecording 既有守卫处理）
  - 相册：click → `onAttachClick(false, true, true)`（照片/视频多选）
  - 拍摄：click → 同相册（web 文件选择器无 capture 语义，文档化为平台限制）
  - 文件：click → `onAttachClick(true)`（文档选择）
- 表情/更多：复用现有 `toggle-emoticons` 与 `attach-file`（+），仅 CSS 移入下行。
- 禁止：不重写任何 ChatInput 逻辑、不 reparent 录音控件、不动 attach/emoji 菜单行为。

### 2. CSS（src/tgqq/design/chatInput.scss）
- `.new-message-wrapper`（真机结构）与 `.chat-input-wrapper`（fixture 结构）双目标：
  - 上行：input（flex:1）+ send（右侧圆蓝钮）
  - 下行：语音/相册/拍摄/文件/表情/＋ 六个按钮等距分布（2.25rem 图标钮，
    灰 #5a5a5a，hover/active 蓝 #1296DB）
  - `voice-recording-panel` 跨两行（grid-column: 1/-1），录音态不破版
- 暗色模式同步。

### 3. fixture 重构（mobile-chat / group-chat / tablet）
- composer DOM 改为真机结构：`.rows-wrapper.chat-input-wrapper > .new-message-wrapper`
  内含 [快捷钮×4][＋][input][表情][send-container]（消除既有 fixture↔真机结构漂移）。

## 验证
- build/shoot（三张聊天 fixture + tablet）→ puppeteer computed-style + magick 像素：
  两行几何（上行高≈44px、下行≈40px）、六钮存在、hover 蓝、录音面板跨行、
  表情面板/附件面板回归（bottom 锚点仍正确）。
- codebuddy 识图终审 → 报告 round15-composer-report.md。

## 实施进度（2026-08-15 04:2x）
- [x] TW-UP-013：input.ts `constructTqQuickActions()`（语音/相册/拍摄/文件 4 钮，
      tqFlags.twoRowComposer 门控；语音→startActive()、相册/拍摄→onAttachClick(false,true,true)、
      文件→onAttachClick(true)；Stories composer 跳过）
- [x] chatInput.scss：`.new-message-wrapper` 6 列两行 grid（上行输入+发送、下行 6 钮），
      输入 `width:auto!important` 修复 tweb `width:1%` 挤压；录音面板跨行；暗色同步
- [x] fixture 三页（mobile-chat/group-chat/tablet）composer 重构为真机 DOM 结构
      （rows-wrapper > new-message-wrapper）+ 4 快捷钮；fixture.css plate 改 column
- [x] build/shoot → puppeteer 自验：plate 100px、grid 88px、输入 46px、发送 36px、
      6 钮 36px 均匀（mobile x=44..310 / tablet x=416..808）、hover 蓝 #1296DB、
      表情面板底缘 88px 锚定、附件面板贴底 217px
- [x] codebuddy round15 识图评审（6/6 PASS，结论见报告 §3）
- [x] 报告 round15-composer-report.md
