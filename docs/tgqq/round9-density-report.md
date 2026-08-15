# Round 9 — 密度校准：会话列表 / 气泡 / 字号（报告）

- 日期：2026-08-15
- 基线：Round 8 完成态（未提交，工作区含 Round 1-8 改动）
- 循环：改 token → `vite build` → `shoot.sh`（11 张）→ puppeteer 实测 → codebuddy 评审 → 本报告
- 背景：多轮 codebuddy 反馈整体密度低于 QQ9（列表项间距、气泡间距、字号偏小、行高偏松，"松散感"）

## 1. 本轮改动

### 1.1 密度 token（`src/tgqq/design/tokens.scss`）
| Token | 改前 | 改后 | 理由（对照 QQ9 移动端） |
|---|---|---|---|
| `--tq-chatlist-item-height` | 68px | **74px** | QQ9 会话行更高更饱满 |
| `--tq-chatlist-avatar-size` | 48px | **52px** | QQ9 移动端头像较大 |
| `--tq-bubble-padding-v` | 8px | **10px** | 气泡更饱满 |
| `--tq-bubble-padding-h` | 12px | **14px** | 同上 |
| `--tq-font-size-md` | 15px | **16px** | QQ9 聊天气泡正文 16px 档 |
| `--tq-line-height-normal` | 1.5 | **1.4** | 行高收紧，消除松散感 |

### 1.2 会话列表头像贴左（`src/tgqq/components/TqChatList.scss`）
- 发现 tweb 残留 `.row-with-padding` 的 **72px 左内边距**（`!important`），
  把头像推到 x=88，行内大片空白（松散感主要来源之一）。
- 修复：`.chatlist-chat { padding-inline-start: var(--tq-chatlist-padding) !important }` →
  头像贴左（页面 16px 边距 + 行 12px 内边距 = 头像 x=28 手机 / x=12 平板）。

### 1.3 fixture 同步
- `mobile.html` / `tablet.html`：20 处内联 `width:48px;height:48px` 移除，
  头像尺寸改由 `--tq-chatlist-avatar-size` 单一来源控制（避免两边失同步）。
- `fixture.css`：搜索框 `.input-search` 36 → **40px**。

## 2. 改前后实测数值（puppeteer computed-style，390x844 / 900x700）

| 检测项 | 改前 | 改后 | 目标（QQ9 近似） |
|---|---|---|---|
| 会话行高 | 68px | **74px** | ~72-76px ✅ |
| 会话头像 | 48px | **52px** | 52px ✅ |
| 头像位置（手机） | x=88（72px 残留缩进） | **x=28**（16 边距+12 内边距） | 贴左 ✅ |
| 标题字号/行高 | 17px / 22.1px | 17px / 22.1px | 17px ✅ |
| 副标题字号 | 13px | 13px | 13px ✅ |
| 搜索框 | 36px | **40px** | ~40px ✅ |
| 气泡正文 | 15px / 行高 22.5px | **16px / 22.4px** | 16px ✅ |
| 气泡内边距 | 8px 12px | **10px 14px** | ✅ |
| 单行气泡高 | 86px | **90px** | ✅ |
| 组内气泡间距 | 4px | 4px（保持） | QQ9 紧凑 ✅ |
| 日期胶囊 | 43px / 11px | 43px / 11px | 保持 |

## 3. 回归检查（puppeteer + magick）
- 群聊头像 40px、底边与组末气泡齐平（g1: 187=187；g2: 377=377）✅
- 入站 46px / 出站 46px 缩进、tq-own 右缘 16px ✅
- 出站 #A6E3FF、入站 #FFFFFF、回复块 3px 蓝条 ✅
- 渐变头像渲染正常（magick 采样到 #12B7F5→#1296DB 渐变像素）✅
- 平板列表头像 x=12、行高 74px ✅

## 4. codebuddy round9 评审（`/tmp/cb_round9_out.txt`）

**总体结论：密度校准基本达标，无严重缺陷。** 行高 74px、头像 52/40px、字号 17/13/16、
行高 1.4、出站 #A6E3FF、群头像底对齐、入出站 46px 对称——全部 PASS。

codebuddy 提出 5 个轻微项，逐一核实/修复：
| # | codebuddy 反馈 | 核实结果 | 处理 |
|---|---|---|---|
| ① | 气泡水平内边距 ≈23px（偏大） | ✅ 属实：tweb `.message` 自带 `margin:4px 8px 5px`，把文字从 14px 推到 23px | **已修**：`TqChatBubble.scss` 文本消息 `.message{margin:0}`，文字距气泡缘 = 14px padding + 1px 边框 = 15px |
| ② | 竖向内边距不均（上 16/下 9） | ✅ 同因（.message 上 4px/下 5px margin） | **已修**（同上），现上 11px / 下 ≈15px（含时间行）均匀 |
| ③ | 搜索框 ≈35px < 40px | ❌ 误报：puppeteer 实测 `.input-search` 恰好 40px（codebuddy 量的是内部图标区） | 无需改 |
| ④ | 行高 77-78px 漂移 | ❌ 误报：puppeteer 实测行距精确 74px（122/196/270/344/418），codebuddy 扫描的是头像顶部噪声 | 无需改 |
| ⑤ | 回复块 3px 蓝条无法验证 | ❌ 误报：group-chat.html 有回复块，magick 实测 x=85-87 三列像素为 #1296DB 蓝条（y=430） | 无需改 |

## 5. 修复后复验（vite build → shoot.sh 11 张 → puppeteer/magick）
- 消息气泡：padding `10px 14px`，文字实际偏移 15px/11px（= padding + 1px 边框）✅
- 气泡宽 174→158px（去掉 .message 外距后更紧致）✅
- 群聊头像底对齐保持（g1: 232=232；g2: 404=404）✅
- 回复块 3px 蓝条像素确认 ✅

## 6. 遗留/后续
- 下一轮（Round 10）：聊天页「+」附件面板 QQ9 化（计划见 `round10-attach-panel-plan.md`）
- 长尾：动态页真实图占位、出站自头像真机验证、顶栏图标描边、sendername 间距

## 5. 遗留/后续
- 下一轮（Round 10）：聊天页「+」附件面板 QQ9 化（计划见 `round10-attach-panel-plan.md`）
- 长尾：动态页真实图占位、出站自头像真机验证、顶栏图标描边、sendername 间距
