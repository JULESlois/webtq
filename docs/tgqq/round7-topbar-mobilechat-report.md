# Round 7 — 顶栏图标 QQ9 化 + mobile-chat 手机聊天页 + 气泡/输入条细节（报告）

- 日期：2026-08-14
- 基线：`e3730e1`（未提交，工作区含 Round 1-6 改动）
- 范围：仅 `src/tgqq/**` + `docs/tgqq/fixtures/**`，**无上游 src/ 改动，不新增 TW-UP 条目**
- 循环：改 → `vite build` → `shoot.sh` 截图 → JPEG → codebuddy 识图 → puppeteer/magick 交叉验证 → 修复 → 本报告

## 1. 本轮完成项

### 1.1 顶栏三图标 QQ9 化（CSS-only，零 renderer 改动）
- `TqTopbar.scss` 追加：`.btn-icon .tgico-phone / .tgico-videochat / .btn-menu-toggle .tgico-more`
  字体隐藏（`font-size:0`）+ 20px CSS mask 实心图标：
  - 电话：实心听筒（Material 填充路径）
  - 视频：圆角摄像机（填充）
  - 更多：水平三点（三个实心圆）
- 颜色：`var(--tq-text-secondary)` → **本轮新增 `--tq-icon-primary` token**（light `#1f1f1f`、dark `#d6d6d6`），
  解决 codebuddy 指出的「实心但中灰 #5a5a5a」问题。
- `tablet.html` 原 emoji/SVG 按钮换为 `<span class="tgico tgico-phone/videochat/more">` 与真机同构。

### 1.2 新增 mobile-chat 手机聊天页 fixture
- 新文件 `docs/tgqq/fixtures/mobile-chat.html`（从 tablet.html 聊天区块抽取生成）；
  `shoot.sh` 增加 `mobile-chat:390x844`，截图共 9 张。
- `fixture.css` 追加：
  - `body:not(.tq-tablet) #column-center {opacity:1!important; transform:none!important}`（真机 JS 会显示，静态 fixture 需强制）
  - ≤599px 清 `--page-chats-padding`
  - 顶栏返回按钮 `position:static!important; order:-1`；`.chat-info` 覆盖 padding
    （高特异性 `body.is-tgqq.tq-chat-header:not(.tq-tablet) .topbar.has-avatar .chat-info{padding-inline-start:4px!important}`）
- 返回箭头：`tablet.html` 的 `←` 换成 `<span class="tgico tgico-left">`，`TqTopbar.scss` 加
  描边式 chevron mask（`M15 5l-7 7 7 7` stroke-width 2.6）。
- 头像统一 40px（`tablet.html` inline style 与 `TqTopbar.scss` 均 40px）。
- 移动端真机行为：`.topbar .btn-icon`（电话/视频）display:none，仅剩 ⋯（与 QQ9 手机一致）。

### 1.3 气泡圆角 8 → 14px
- `tokens.scss` `--tq-bubble-radius-incoming/outgoing: 14px`；fixture.css `.bubble-content border-radius:14px`。
- 逐角非对称规则（group-first/last）已在本轮前存在，本轮实测确认：见 §3。

### 1.4 输入条胶囊化
- `chatInput.scss` `.chat-input-wrapper` → `border-radius: var(--tq-radius-xl)`（20px）、
  `background:#f7f8fa; border:none`；dark 改 `#2f2f2f`；fixture.css 同步。
- 实测：`rgb(247,248,250)` / 20px ✓

### 1.5 回复块重设（复核确认在）
- `TqChatBubble.scss` `.reply{border-left:3px solid var(--tq-accent-primary); border-radius:6px;
  background:rgba(0,0,0,.06)}`；`.bubble.is-out .reply` 0.1；dark `rgba(255,255,255,.08)`。

### 1.6 shoot.sh 增加字体复制
- `cp dist/assets/fonts/* docs/tgqq/fixtures/css/assets/fonts/`（tgico 字体静态 fixture 需要）。

## 2. 验证矩阵

### 2.1 puppeteer computed-style（权威）
| 检测项 | 期望 | 实测 | 状态 |
|---|---|---|---|
| 入站气泡圆角（组首） | `4px 14px 14px 4px` | `4px 14px 14px 4px` | ✅ |
| 出站气泡圆角（组首） | `14px 4px 4px 14px` | `14px 4px 4px 14px` | ✅ |
| 顶栏四图标色（改后） | 近黑 | `rgb(31,31,31)` = #1f1f1f | ✅ |
| 回复块左边框 | 3px 蓝 #1296DB | `3px solid rgb(18,150,219)` | ✅ |
| 回复块圆角/背景 | 6px / rgba(0,0,0,.06) | 一致 | ✅ |
| 顶栏头像 | 40px | x412 y6 40x40 | ✅ |
| 状态行绿点 | 8px #00D66C | 8px `rgb(0,214,108)` | ✅ |

### 2.2 magick 像素（渲染层）
| 检测项 | 实测 | 状态 |
|---|---|---|
| tablet-mid 顶栏右侧深色像素 | 186（三簇图标，实心） | ✅ |
| mobile-chat 头像右下绿点 | 9px #00D66C（含 2px 白边，核心绿像素 x97-101/y41-45） | ✅ |
| mobile-chat 状态行绿点 | #00D66C（x128-136 簇，codebuddy 误读为此点） | ✅ |

### 2.3 codebuddy 三轮评审
- round7c（首轮）：严重缺陷 0；确认三图标/手机聊天页/气泡蓝白/按钮 PASS。
- round7e（终轮）：确认气泡圆角 + 胶囊输入条自然；误报项经交叉验证排除。
- round7f（本轮重试，`/tmp/cb_round7f_out.txt`）：仅 D2 属实，其余全为误报，详见 §3。

## 3. codebuddy round7f 结论澄清（交叉验证）

| # | codebuddy 说法 | 判定 | 证据 |
|---|---|---|---|
| D1 | 气泡圆角未逐角非对称（接收全 4 / 发送全 14） | ❌ 误报 | puppeteer 实测 `in=4px 14px 14px 4px`、`out=14px 4px 4px 14px`，与 QQ9 完全一致；它只读了单行压缩 CSS |
| D2 | 顶栏图标实心但中灰 #585858 | ✅ 属实（轻微） | puppeteer 实测 `rgb(90,90,90)`；**已修复**：新增 `--tq-icon-primary`（#1f1f1f），实测 `rgb(31,31,31)` |
| D3 | 绿点不在头像右下角（x128-135 处） | ❌ 误报 | 头像右下绿点实测存在（9px 半溢出+白边）；x128-136 是状态行「手机在线」绿点 |
| D4 | 回复块蓝条取色不统一（#1D91CE vs #1296db） | ❌ 误报 | 取样点为 JPEG 抗锯齿边缘；computed style = `#1296DB` = `--tq-accent-primary` 精确值 |

## 4. 剩余风格差异（非缺陷，后续可选）
- 超宽屏（xwide）聊天区左侧大量留白 → 可做最大宽度居中策略。
- 顶栏图标笔画偏细 → 后续可将 mask 图标 stroke/填充加粗（本轮已实心+加深）。
- channels 卡右缘截断 → 设计渐隐（mask-image），早前已定。
- 动态页九宫格为渐变占位 → fixture 数据空态，等真实图源。
- 整体密度低于 QQ9（间距/字号）→ 风格差异，逐项微调。

## 5. 环境备注
- `pnpm run typecheck` 本次失败：TypeScript 7.0.2 native 缺 `@typescript/typescript-android-arm64`
  平台包（环境问题，非代码问题）；改用 `npx vite build` 直接构建，产物正常。
- codebuddy 命令：`cd /data/data/com.termux/files/home/tg-web && codebuddy -y -p "$(cat /tmp/xxx.txt)"`，
  单轮约 25 分钟；JPEG 可读。
