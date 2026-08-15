# Round 19 — 默认头像 + 未读角标 + 搜索栏居中（报告）

- 日期：2026-08-15
- 前置：Round 18 底部导航/频道 Tab/右窗空状态全 PASS（round18-nav-empty-channel-tabs-report.md）
- 循环：codebuddy 规格提取（`/tmp/cb_round19_out.txt`）→ 实施 → build/shoot → puppeteer 自验（27 项）→ 搜索条居中修复 + codebuddy 三轮终审（`/tmp/cb_final19_out.txt`、`/tmp/cb_final19b_out.txt`、`/tmp/cb_final19c_out.txt`）→ 本报告

## 1. QQ9 参考规格（来自 `qq9-mobile2/000.jpg`/`010.jpg` 像素分析）

- **默认头像**：浅灰圆底 `rgb(243,242,247)` + 深灰人形 `rgb(144,144,146)`；圆形直径 99px（720 宽图，2 倍缩放 ≈ 手机屏 52px）；人形居圆内上部（头 y≈19-42%、肩 y≈50-67%），无描边。暗色：圆底 `rgb(86,83,100)` + 白色人形。
- **未读角标**：鲜红 `rgb(254,71,53)`，紧凑圆角气泡（16px 高、白字 10px/500），钉在头像右上角并凸出重叠；列表行无数字角标，只有 Tab 红点。
- **搜索栏**：无边框浅底胶囊、大圆角（约 20px），「放大镜 + 搜索」整体水平居中。
- **顶栏/底栏/列表**：顶栏淡蓝 `rgb(240,244,255)`（暗色 `rgb(43,61,99)`）；列表区/页面与底栏同灰 `rgb(243,242,247)`；列表行本身为白色卡片（参考图 row1 裁片：行区白、行外灰）。
- **Tab 角标**：底部「动态」Tab 右上角纯红点 `rgb(254,71,53)`，无数字。

## 2. 改动文件

### 设计变量 `src/tgqq/design/light.scss` / `dark.scss`
- 新增 `--tq-avatar-bg`/`--tq-avatar-fg`/`--tq-search-bg`/`--tq-header-bg`；浅色 `--tq-surface-page` 由 `#f5f5f5` 校准为 `#f3f2f7`（= 参考 列表区/底栏 243,242,247）；`--tq-accent-orange` 与 `--tq-badge-bg` 统一为 QQ 红 `#fe4735`（亮/暗同值，修复角标偏粉）。

### 组件样式 `src/tgqq/components/TqChatList.scss`
- `.dialog-avatar`：浅灰圆底 + `::before` data-URI SVG 人形（浅色深灰/暗色白），覆盖真实照片头像的 `.avatar-gradient::before` 分支；`.row-row`/`.row-subtitle` 置 `position:static !important`（tweb 全局 relative 会让角标锚到文本列而非头像）。
- `.badge.unread`：绝对定位贴头像右上角（16px 高、10px 字号、500 字重、`--tq-badge-bg`）。
- `.input-search`：胶囊底 `--tq-search-bg`；新增 `.sidebar-header .input-search` 结构修复——占位符/图标从绝对定位拉回流内，输入框绝对覆盖胶囊（透明底），使「放大镜+文字」整体居中（QQ9 规格）。
- `.chatlist-container`：`background: var(--tq-surface-page) !important`——tweb 的 `#column-left #chatlist-container` 特异性更高会把列表容器刷白，导致平板列表区看不到 QQ 灰底；强制后白色行卡下方的灰底在行间/行下可见。

### 夹具 `docs/tgqq/fixtures/css/fixture.css`
- `.input-search`：白底圆角 20px、`justify-content:center`、`::before` 注入放大镜 SVG、隐藏原 emoji 图标、`.input-search-placeholder` 置 static。
- `.badge.unread`/`.tq-badge`：`#fe4735`；body 底色 `#f3f2f7`；`.tq-nav-dot` 红点 `#fe4735` 无描边；`.tgqq-profile-avatar` 红色径向渐变。

## 3. 验证结果

### puppeteer computed-style 自验（`/tmp/verify19.js`）—— 27/27 PASS
- 头像：浅色底 `rgb(243,242,247)`、文字透明、人形 SVG 在（top 8%/width 58%）；暗色底 `rgb(86,83,100)` + 白人形；平板同规格。
- 角标：绝对定位 `left:54px` 贴头像右上（badge x=70, avatar 右端 x=80，重叠 10px），16×16、10px/500；亮暗色值均 `rgb(254,71,53)`。
- 搜索：胶囊白/`rgb(55,55,55)`、`justify-content:center`、放大镜 SVG、组中心与胶囊中心偏差 <2px。
- 页面/底栏：body 与 nav 均 `rgb(243,242,247)`；顶栏 `rgb(240,244,255)`（暗 `rgb(43,61,99)`）；Tab 红点 `rgb(254,71,53)`。

### 像素复核（`shots/mobile.png`/`mobile-dark.png`/`tablet-mid.png`/`tablet-dark.png`）
- 搜索组中心：mobile 211.0 / 211.0（±0.0）、tablet 188.0 / 187.5（+0.5），四张全居中。
- 角标核心像素 `(254,71,53)` 亮暗精确命中；nav `(243,242,247)`、暗 nav `(26,26,26)`。
- 人形 bbox：x44-68 y143-168（头 19-42%、肩 50-67%、水平中心 54%）——与 QQ9 参考形态一致。

### codebuddy 终审（三轮）
- 第一轮（`/tmp/cb_final19_out.txt`）：A 默认头像 PASS、C 搜索栏 PASS、E Tab 红点 PASS；B 角标 FAIL（实测 `(250,81,81)`/`(255,107,107)` 偏粉，规格 `(254,71,53)`）；D FAIL（误将列表行白色当"列表底色"，且底栏 `#f5f5f5` 与参考 `(243,242,247)` 差 2-3）。
- 修复：`--tq-badge-bg` 亮/暗统一 `#fe4735`；`--tq-surface-page` 校准 `#f3f2f7`（= 参考列表区/底栏 `(243,242,247)`）；补充参考图证据（行=白卡、列表区/底栏=灰）。
- 第二轮（`/tmp/cb_final19b_out.txt`）：B/D 复核通过，但出现两处与实测矛盾的误报——A 头像翻案 FAIL（与第一轮字节级证据自相矛盾）、C tablet 搜索"胶囊 x20-324 中心 172"（实测 `getBoundingClientRect` 为 x20-355 中心 187.5，content bbox x165-211 中心 188.0，偏差 0.5px）；B 声称"列表行应无数字角标"（与 QQ9 官方头像角标数字气泡 UI 及 010 规格"白字"矛盾，属参考图缺行导致的误读）。
- 修复：`.chatlist-container` 强制灰底（见 2 节）；对每项用 DOM 几何 + 像素复核后，保留实测结论。
- 第三轮（`/tmp/cb_final19c_out.txt`，附精确几何）：**A/B/C/D 全部 PASS**——搜索组中心 mobile 0px / tablet 0.5px 偏差、角标红 `(254,71,53)` 白字 16px 钉位正确、无未读行干净、行外灰底可见、暗色体系一致。**Round 19 终审全部通过**。

## 4. 记账

- 本轮源码改动均在 `src/tgqq/` 私有目录（`design/light.scss`、`design/dark.scss`、`components/TqChatList.scss`），无 upstream 补丁；fixture 改动在 `docs/tgqq/fixtures/css/fixture.css`。
- `shots/*` 42 张 PNG/JPG 重新生成（`bash docs/tgqq/fixtures/shoot.sh`）。
- 未提交（延续惯例：`src/tgqq/`、`docs/tgqq/` 为私有工作区）。
- 遗留开放项：真实 app 侧 `sidebar-header .input-search` 结构修复需在真实会话中复验（fixture 无输入框，本轮回流式结构已同步）；聊天页（chat page）改造留待下一轮。
