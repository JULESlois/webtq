# Round 18 — 底部导航图标重绘 + 频道页 Tab + 平板右窗空状态（报告）

- 日期：2026-08-15
- 前置：Round 17 聊天页状态全 PASS（round17-chat-states-report.md）；本轮基于 codebuddy 全量差距审计（`/tmp/cb_gapaudit_out.txt`）TOP10 清单实施
- 循环：差距审计 → 图标重绘 → 频道 Tab/关注页 → 空状态 → build/shoot → puppeteer 自验（21 项）→ codebuddy 两轮终审 → 本报告

## 1. 本轮完成项（对应审计 TOP10 #1/#6/#9）

### 1.1 底部 4 Tab 图标重绘为 QQ9 线性轻图标
- `src/tgqq/components/BottomNavigation/index.tsx` 内嵌 `TqNavIcon`（1.5px stroke 线性）：`消息`=气泡、`频道`=#、`联系人`=人形、`动态`=时钟；替换旧填充图标（扬声器/星形）。
- 语义来源：codebuddy 审计对 `qq9-mobile2/001` 的判定（消息=气泡、频道=#、联系人=人形、动态=时钟）。
- fixture 同步：`mobile.html`/`tablet.html` 全量替换 4 个旧填充 SVG；`tab.html` 补齐 消息/联系人 2 个（频道/动态上轮已同步）。

### 1.2 频道页顶部 Tab（推荐/关注）+ 关注态联动
- `src/tgqq/pages/Channels/index.tsx`：新增 `createSignal<'recommend'|'follow'>` 选中态；`Channel` 数据加 `id`；`followedIds` 集合提升到页面级，卡片/行内「+ 关注/已关注」与关注页实时联动（关注后在「关注」Tab 出现，可取消）。
- Tab 条样式（`Channels.module.scss`）：15px 文字、选中蓝 `--tq-accent-primary`(#1296db) 加粗 + 底部 22px 蓝色小横线，未选中灰。
- 「关注」Tab：有关注 → 已关注列表（行式复用 `ChannelRow`）；无关注 → 空状态（72px 虚线圆 + 「还没有关注的频道」+ 引导文案）。
- 语言包：`lang.ts` + `langPack.strings` 新增 `Tgqq.Channels.Recommend/Follow/FollowEmpty/FollowEmptySub`。

### 1.3 平板右窗空状态（纯 CSS，审计 TOP10 #9）
- `src/tgqq/components/TqTablet.scss`：`#column-center:not(:has(.chat.active))` 时显示占位——`::before` 载入 data-URI SVG（浅灰蓝 QQ 企鹅 + 左右两个聊天气泡轮廓，气泡内三点/两横线），`::after` 显示「选择会话开始聊天」（`--tq-text-tertiary`）。
- 亮/暗双套 SVG（暗色 `html.night` 分支），参考 `qq9-tablet/001.png`：右窗近白底、顶部居中低对比浅灰单色企鹅 + 气泡；首轮终审后按参考图把企鹅改为单色浅灰（去橙嘴/脚）、整体对比度再压低（像素均值差 55→14.6，参考图约 6.5，处于"清晰可辨但柔和"区间）。
- 有激活聊天时（`.chat.active` 存在）规则不生效，右窗正常显示聊天。

### 1.4 fixture 补全与交互修复
- `tablet.html` 支持 `?empty=1`（JS 移除 `.chat`，真实触发 `:has` 空状态规则，验证的是生产 CSS）。
- `tab.html` 频道页模板加 Tab 条 + 双面板；`?follow=1` 展示已关注列表，否则空状态；Tab 点击切换、关注按钮点击态。
- `fixture.css`：`.tq-tabs/.tq-tab/.tq-tab-active`（含 dark）、`.tq-follow-empty*`、`.tq-tab-panel[hidden]/.tq-follow-empty[hidden]/.tq-follow-list[hidden]` 显示覆盖。
- 交互修复：`.tq-pages` 补 `pointer-events:auto`（此前 fixture 页面不可点击，真实 app 无此问题）。
- `shoot.sh` 新增 6 规格：`tablet-empty`/`tablet-empty-wide`/`tablet-empty-dark`/`channels-follow`/`channels-follow-dark`（+`tablet-empty` 暗色并入）。

## 2. 验证矩阵（puppeteer computed-style + 像素采样）

| 检测项 | 期望 | 实测 | 状态 |
|---|---|---|---|
| 空状态触发条件 | `?empty=1` 时无 `.chat` | chatCount=0，`::before` 为 data:image/svg+xml | ✅ |
| 空状态文案 | 「选择会话开始聊天」 | `::after` content 命中 | ✅ |
| 有聊天时无空状态 | `.chat.active` 存在 → `::after` none | 命中 | ✅ |
| 空状态定位 | 右窗水平居中、偏上 | 900px: 中心 x=629(窗心630)；1180px: 769.5(窗心770) | ✅ |
| 空状态 SVG | 亮/暗两套 | 亮 `#f5f5f5` 底、暗 `#1a1a1a` 底均渲染 | ✅ |
| 空状态对比度 | 柔和（贴参考图） | 像素均值差 14.6（参考 6.5，改前 55） | ✅ |
| 4 Tab 图标 | 线性 stroke、fill=none、1.5px | mobile/tablet/tab 三 fixture 全命中 | ✅ |
| 图标可见性 | 4 个图标均在底部渲染 | mobile 4 槽 diff 219-290px；tablet 4 槽 187-319px | ✅ |
| 频道 Tab 条 | 2 Tab、选中蓝 #1296db+22px 下划线 | 色值/宽度精确命中 | ✅ |
| 面板切换 | 推荐↔关注互斥显示 | hidden 状态互斥，点击切换生效 | ✅ |
| 关注页 | 只显示已关注列表 | 空状态 display:none、列表 block；「已关注」蓝底白字 ×2 | ✅ |
| 关注空状态 | 无关注时虚线圆+文案 | display:flex、列表 none | ✅ |
| 暗色 Tab | 选中 #35a7e8 | rgb(53,167,232) | ✅ |
| 聊天回归 | tablet-mid 右窗正常聊天 | 顶栏/气泡/输入区齐全，无空状态 | ✅ |

## 3. codebuddy 终审结论

### 第一轮（18a，7 图）
- A 底部 4 Tab 图标 PASS（语义/线宽/选中蓝 #1296db 全部符合）
- B 频道 Tab 条 PASS（y≈120 处双 Tab、选中蓝色加粗+短蓝线）
- C 关注页 **FAIL**：`channels-follow.png` 同时出现空状态与已关注列表
- D 空状态 PASS（亮/暗一致，风格贴近参考）
- E 激活聊天无空状态 PASS
- 附加建议：企鹅对比度可再压低（已采纳）、频道 Tab 页右窗空状态系 fixture 无聊天所致（符合预期）

### 第二轮（18b，3 图，修复后）
- **C 修复 PASS**：根因 = fixture `.tq-follow-empty` 的 `display:flex` 覆盖了 `hidden` 属性（源码用 Solid `Show` 不存在此问题）；补 `[hidden]` 显式覆盖后，关注页仅剩已关注列表。
- **D 微调 PASS**：企鹅单色浅灰、无橙嘴/脚、柔和可辨。
- 结论：**第 18 轮全部通过**。

## 4. 记账

- 本轮源码改动：`src/tgqq/components/BottomNavigation/index.tsx`（图标）、`src/tgqq/pages/Channels/index.tsx`+`Channels.module.scss`（Tab/关注）、`src/tgqq/components/TqTablet.scss`（空状态）、`src/lang.ts`+`src/scripts/out/langPack.strings`（4 键）——均在 `src/tgqq/` 私有目录，无 upstream 补丁。
- fixture：`docs/tgqq/fixtures/{mobile,tablet,tab}.html`、`css/fixture.css`、`shoot.sh`、`shots/*`（42 PNG+JPG 重生成）。
- 未提交（延续此前各轮惯例：`src/tgqq/`、`docs/tgqq/` 为私有工作区；`src/components/chat/*`、`sidebarLeft`、`lang.ts`、`bootstrapIm.ts` 等前几轮已审改动仍未提交）。
- 审计 TOP10 剩余开放项：真实头像/默认灰头像 fallback（#4）、顶栏搜索形态微调（#7/#10）、未读角标收敛（#8）——留待后续轮次。
