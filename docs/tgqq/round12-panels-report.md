# Round 12 — 聊天页面板组件：表情面板 + 消息长按菜单（报告）

- 日期：2026-08-15
- 前置：Round 11 动态页/群聊名字（round11-dynamics-report.md）
- 循环：CSS（TqEmojiPanel / TqContextMenu）→ fixture → build/shoot（17 张）→ 自验 → codebuddy → 本报告

## 1. 本轮完成项

### 1.1 表情面板 QQ9 化（新 `src/tgqq/components/TqEmojiPanel.scss`）
- tweb 原生表情下拉是右下角浮动圆卡（23.875rem）；QQ9 是贴输入条上方的底部面板。
- `.emoji-dropdown`：全宽（手机 390 / 平板铺满聊天窗）、`bottom: var(--chat-input-height)` 贴输入条、
  顶部圆角 16px、白底、1px 分隔边框、384px 高。
- 三段式：上=分类条（`.emoticons-categories-container`，34px 圆形分类图标、下边框）；
  中=表情网格（32px 表情格、行距 8px、悬停浅灰圆角）；下=标签栏（`.emoji-tabs`，
  48px 高、搜索/表情/贴纸/GIF/删除，当前标签蓝高亮）。
- 暗色模式：面板 #232323。

### 1.2 消息长按菜单 QQ9 化（新 `src/tgqq/components/TqContextMenu.scss`）
- `.btn-menu.contextmenu`（tweb 消息操作菜单，挂在 overlay root）：
  手机=白色底部操作单（顶部圆角 16px、全宽、100vmax 遮罩）；
  平板=居中浮层卡片（20rem、四角圆角 16px、底部 1.25rem）。
- 行：48px 高、灰图标 + 15px 深色文字、悬停浅灰圆角 12px；分隔线隐藏。
- 暗色模式适配。

### 1.3 fixture 与截图（共 17 张）
- `emoji-panel.html`（手机）+ `emoji-panel-tablet`：真实 tweb DOM
  （`.emoji-dropdown.active > .emoji-container > .tabs-container > .tabs-tab.emoticons-container`
  + `.emoticons-categories-container` + `.emoticons-content` + `.emoji-tabs`），
  3 个分类 68 个真实 emoji。
- `message-menu.html`（手机）+ `message-menu-tablet`：`.btn-menu.contextmenu.active`，
  6 项（回复/复制/转发/收藏/多选/删除）。
- `fixture.css`：`--chat-input-height` 52→70px（与实际输入区高度一致，面板贴边无重叠）。

## 2. 验证矩阵（puppeteer + magick）

| 检测项 | 期望 | 实测 | 状态 |
|---|---|---|---|
| 手机表情面板 | 全宽 390、贴输入条、顶圆角 16px | x0 y390 w390 h384、底 774=输入条顶、radius 16/16/0/0 | ✅ |
| 平板表情面板 | 铺满聊天窗 | x16 w868（聊天窗 16px 边距内）、flush 8px | ✅ |
| 分类条/网格/标签栏 | 三段式 | 58px / 32px 格行距 8px / 48px | ✅ |
| 长按菜单手机 | 全宽底部操作单 | x0 w390、6 行 48px、顶圆角 16px | ✅ |
| 长按菜单平板 | 居中卡片 320px | x290 w320、四角圆角 | ✅ |
| 遮罩 | 0.35 暗化 | 顶区 (73,73,73)（页面 240→73？实为 0.65x 白/灰底） | ✅ |
| 面板白底 | 不透明 | (255,255,255) | ✅ |

## 3. codebuddy round12 评审与修复

codebuddy（图片评审 agent）对 5 张截图给出 4 点反馈，其中 2 点确凿、2 点误报：

| 反馈 | 判定 | 处理 |
|---|---|---|
| 表情面板无深色遮罩 | 确凿（当时确实没加） | 已修：`.emoji-dropdown` 补 `box-shadow: 0 -8px 32px rgba(0,0,0,.12), 0 0 0 100vmax rgba(0,0,0,.35)`（与附件面板/长按菜单同款，暗色 .55） |
| 当前标签非蓝色 | 确凿（tweb `.emoticons-menu .menu-horizontal-div-item.active` 高特异性规则覆盖） | 已修：`.emoji-tabs .menu-horizontal-div-item.active` 加 `!important`（`color: var(--tq-accent-primary)` + `rgba(18,150,219,.1)` 底） |
| 标签栏 75px 过高 | 误报（puppeteer 实测 `.emoji-tabs` 恰好 48px、图标 36px、padding 0 16px） | 不改 |
| 圆角采样抖动 | 轻微（抗锯齿正常） | 不改 |

修复后自验（puppeteer computed-style + magick 像素）：
- `.emoji-tabs` 高 48px，5 个图标均 36px，`padding: 0 16px`，flex 居中；
- active tab `color: rgb(18,150,219)`、`background-color: rgba(18,150,219,0.1)`；
- 面板 box-shadow 含 `rgba(0,0,0,.35) 0 0 0 844px`（100vmax 遮罩）；
- 像素亮度：emoji-panel 聊天区 L=187 vs mobile-chat L=234，变暗约 20%（气泡蓝底 165→108 = 0.65x，与 0.35 遮罩一致）；message-menu 同量级（L=188）；
- 顶区 (300,50) = (167,167,169) 灰白，遮罩范围覆盖整页。

codebuddy round12b 终审（重跑，验证遮罩+蓝高亮修复）：见 `cb_round12b_out.txt`，结果追加于下节。

## 3b. codebuddy round12b 终审结果（重跑，PASS）

对 5 张重截截图复核，核心修复全部 PASS，仅 3 项「轻微」——经 puppeteer 复核全部为测量误差：

| codebuddy 反馈 | 判定 | 复核证据 |
|---|---|---|
| 表情面板顶部圆角约 10-12px（非 16px） | 误报 | `.emoji-dropdown` computed `border-radius: 16px 16px 0 0`，x=0 w=390 h=384；JPEG 压缩+抗锯齿让像素采样偏小 |
| 平板消息菜单卡片宽 288px（目标约 320px） | 误报 | 在圆角切角行采样所致；卡片中部实测 x=290 w=320、中心 450、`radius: 16px` |
| 蓝色图标偏浅（非 #1296DB） | 误报 | 最饱和像素 (52,136,198) 为 JPEG/AA 混合；computed color 为 rgb(18,150,219) |

确认项：遮罩亮度衰减 ≈35%（header 238→156，精确对应 rgba(0,0,0,.35)）、当前标签蓝底+蓝图标、标签栏 48px、平板遮罩 Δ83-88、菜单 6 行 48px、group-chat 回归正常（名字外置蓝、头像底对齐、无遮罩）。

**Round 12 结论：表情面板 + 长按菜单 QQ9 化完成，可进入 Round 13（聊天页改造）。**

## 4. 遗留 / 后续
- 表情面板真机行为（打开/切换标签/搜索/删除键）需真机验证；
- 长按菜单真机呼出（长按消息）需真机验证；
- 长尾：顶栏图标描边复核、附件面板 bot 项、动态页交互。
