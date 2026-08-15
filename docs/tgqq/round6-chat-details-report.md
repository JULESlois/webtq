# Round 6 报告：聊天页细节修正（气泡配色 / 发送按钮 / 宽屏适配）

## 背景

Round 5 完成后，codebuddy 对 8 张 fixture 截图做了两轮评审。首轮出现工具权限问题（Bash/Read 被拒），
重试后（`codebuddy -y`）拿到有效结果。评审确认上一轮遗留项：频道推荐卡片横向裁剪、顶栏在线状态缺失；
同时指出发送方气泡为 Telegram 风格绿色（微信风），与 QQ9 蓝色气泡不符。

## 本轮改动（全部 CSS/fixture，零 renderer/TS 改动）

### 1. 频道推荐卡片裁剪修复

- `Channels.module.scss` + fixture：卡片 `flex: 0 0 118px; min-width: 0`（原先 132px + `min-width:auto`
  会把第 1 张卡撑到 129px 挤出容器）。
- 右侧边缘用 `mask-image: linear-gradient(90deg, #000 94%, transparent 100%)` 做 QQ9 式渐隐，
  第 3 张卡标题完整可读、第 4 张露头提示可滑动。
- 联系人页 A-Z 索引字号 9px → 11px。

### 2. 顶栏在线状态（QQ9 特征）

- 事实核对（web + 真机 DOM）：QQ 好友聊天顶栏在名字下方显示绿点 + 「手机在线 · WiFi」，
  状态行左对齐；头像右下角另有一个绿点。tweb 私聊已有 `span.online`、群聊无 → 纯 CSS 门控即可。
- `TqTopbar.scss`：`.bottom .online` 字号 0 + `::before` 8px 绿点（`--tq-accent-online` #00d66c）
  + `::after` 状态文案（13px）；`.topbar:has(.person .bottom .online) .person-avatar::after`
  = 头像右下 9px 绿点 + 2px 页面色描边。
- fixture `tablet.html` 顶栏 person 结构重构为与真机 DOM 一致；`fixture.css` 补 person/content 列布局。
- 验证：puppeteer computed style + magick 像素统计（顶栏裁剪区恰好 45 个 #00D66C 像素）。

### 3. 发送方气泡：微信绿 → QQ 蓝（核心修正）

- 事实核对（web 多源）：QQ 默认气泡「发送方自己看到蓝色、接收方看到白色」；绿色是微信特征。
  参考图无法提供精确色号，采用 QQ 经典默认气泡蓝。
- `light.scss`：`--tq-bubble-outgoing-bg: #95ec69` → `#a6e3ff`（浅蓝 + 黑字）。
- `dark.scss`：`#7cb342` → `#3e6fa3`（暗色 QQ 蓝 + 白字）。
- 尾巴/圆角规则引用同一 token，自动跟随，无额外改动。
- 验证：tablet-wide.png 直方图 19,560 px 精确 #A6E3FF，绿色像素仅剩在线绿点。

### 4. 发送按钮：纸飞机 → 圆形蓝底白色上箭头

- tweb 真机 `.btn-send` 默认图标是 Telegram logo（`Icon('logo','send')`）；fixture 里是 SVG 箭头。
- `chatInput.scss`：按钮改圆形（`border-radius: 50%`、36×36）、隐藏 `.btn-send-icon-send` 与全部 svg、
  用 `::before` + CSS mask（内联 SVG 上箭头）绘制白箭头——**不需要改 input.ts**。
- 修正过程中发现两处坑：`position: relative` 被未知高特异规则覆盖 → 加 `!important`；
  fixture 的 SVG 与 mask 箭头叠加 → 统一隐藏 svg。
- 验证：36×36 像素图白点渲染出居中上箭头（三角 rows12-18 + 竖杆 rows19-22）。

### 5. 宽屏气泡宽度与细节对比度

- `--tq-bubble-max-width: min(70%, 540px)` → `min(70%, 720px)`（token + fixture.css 同步），
  超宽屏不再窄成一条；codebuddy 的「xwide 右侧 300px 留白」实为短消息内容宽度，QQ 同款行为。
- 引用块：左色条 2px→3px、圆角 4→6px、底色加深（浅色 0.06 / 外发 0.10 / 暗色 rgba(255,255,255,.08)）。
- 顶栏头像 36px → 40px（与 52px 顶栏更协调）。
- 气泡时间/状态 meta 对比度微升（light 0.5→0.55，dark 0.6→0.68）。

## 验证

- `tsc --noEmit`：通过。
- `vite build`：通过（0 error）。
- puppeteer 实测（fixture 1440×900）：
  - `.bubble-content` `max-width: min(70%, 720px)`；发送方气泡 `rgb(166,227,255)`、圆角 `8px 4px 4px 8px`；
  - `.btn-send` 36×36、`border-radius: 50%`、`position: relative`、`::before` 18×18 mask 箭头；
  - 引用块 `border-left: 3px solid #1296db` + 灰底 + 6px 圆角。
- codebuddy 终审（8 张 JPEG，`-y` 模式）确认：
  - 发送方 #A6E3FF 浅蓝 ✅ / 接收方纯白 ✅ / 无绿色气泡 ✅；
  - 圆形蓝色发送按钮 + 白色上箭头 ✅（非纸飞机）；
  - 顶栏双绿点（名字下 + 头像右下）✅；引用块左色条+灰底+圆角 ✅；
  - 频道/联系人/动态三页布局无溢出，索引条正常；
  - 剩余项：超宽屏留白（设计取舍）、顶栏电话/视频/更多图标仍是 Telegram 线性风格（后续轮）、
    动态页图片为渐变色占位（fixture 数据层）、平板 700px 高截图偏矮（截图选择）。

## 已知（后续轮）

- 顶栏右侧电话/视频/更多图标 → QQ9 圆润图标（需替换 tweb 图标，Red/Yellow）。
- 私聊 incoming 对方头像（组首）需 renderer hook（bubbles.ts createAvatar，Red）。
- 群聊 outgoing 真实照片头像（当前渐变圆占位，Red）。
- 输入条「+」按钮为 CSS 注入，`input.ts` 原生行为未动（Yellow）。
- mobile fixture 目前只有消息列表页，聊天页用 tablet fixture 覆盖；移动端聊天页后续补拍。

## 文件清单

Modified（src/tgqq，CSS-only）:
- src/tgqq/design/light.scss（气泡蓝 #a6e3ff、meta 对比度）
- src/tgqq/design/dark.scss（暗色气泡蓝 #3e6fa3、meta 对比度）
- src/tgqq/design/tokens.scss（气泡最大宽度 720px）
- src/tgqq/design/chatInput.scss（圆形发送按钮 + mask 上箭头、引用块对比度）
- src/tgqq/components/TqTopbar.scss（在线绿点 + 状态行 + 头像绿点、头像 40px）
- src/tgqq/components/TqChatBubble.scss（引用块、暗色引用）
- src/tgqq/pages/Channels/Channels.module.scss（卡片 118px + 渐隐）

Modified（docs fixture）:
- docs/tgqq/fixtures/tablet.html（顶栏 person 结构、发送按钮 SVG）
- docs/tgqq/fixtures/css/fixture.css（bubble max-width、圆形按钮、隐藏 svg）
- docs/tgqq/fixtures/shots/（8 张 PNG + JPG 重新生成）

New:
- docs/tgqq/round6-chat-details-report.md（本文件）

上游改动：本轮 **无** src/ 新改动（仅 src/tgqq/**），不新增 TW-UP 条目。
