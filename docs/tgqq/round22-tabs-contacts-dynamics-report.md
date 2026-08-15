# TGQQ Round 22 — 审计修复 + 联系人页/动态页改造 + 聊天页微调报告

> 范围：修复 Round 21 终审 FAIL（暗色 Tab 下划线）+ codebuddy Round 22 四项审计（联系人/动态/频道/平板聊天）的全部高置信条目 + 聊天页 3 项微调。
> 自验：`/tmp/r22_verify.js` **26/26 PASS**；codebuddy 终审聚焦复核 5 项中 4 项 PASS，1 项（封面渐变）已按参考图实测修正。

---

## 1. Round 21 遗留 FAIL 修复（codebuddy 非误审）

| 项 | 修复前 | 修复后 |
|---|---|---|
| 暗色频道 Tab 选中下划线 | `#35A7E8`（fixture.css 硬编码） | `#1296DB`（fixture.css + `Channels.module.scss` 增 `html.night .tabActive` 覆盖） |
| 暗色联系人 Tab 选中下划线 | 无（本轮新增 Tab） | `#1296DB`（`Contacts.module.scss` 同款覆盖） |

像素复核：`tab-channels-dark.png` (25,125)=rgb(18,150,219) ✓；`channels-follow-dark.png` (72,124)=rgb(18,150,219) ✓；亮色不变 ✓。

---

## 2. codebuddy Round 22 四项审计结果（重试成功）

| 审计 | 结果文件 | 结论 |
|---|---|---|
| 联系人页 vs 010.jpg | `/tmp/cb_r22_contacts_result.md` | FAIL×5：二级 Tab 缺失、分组不可折叠无计数、头部形态错配、缺「新朋友/群通知」行、索引微调 |
| 动态页 vs 003.jpg | `/tmp/cb_r22_dynamics_result.md` | FAIL×7：缺渐变封面/等级/入口网格/功能卡，顶栏形态错配、搜索弱对比、动态图标应为旗帜 |
| 频道页暗色复核 | `/tmp/cb_r22_channels_result.md` | 唯一 HIGH FAIL = 暗色下划线（已修）；Tab 条位置条件 PASS（保留） |
| 平板+聊天页 | `/tmp/cb_r22_tablet_chat_result.md` | 106 PASS / 3 FAIL / 3 WARN：气泡色、时间戳 alpha、回复引用内边距 |

---

## 3. 联系人页改造（对照 010.jpg）

- **头部变体**：`TqTabHeader` 新增 props（`title`/`showStatus`/`addIcon`/`compact`）；联系人页 = 36px 头像 + 「联系人」标题 + 人形加号图标，无状态行（QQ9 联系人页与消息/频道页头部不同构，Round 21 统一顶栏对联系人页属错配，已纠正）。
- **快捷导航**：搜索下方新增「新朋友 [徽章1] ›」「群通知 ›」两行（44px 高，底部分割线）。
- **二级 Tab**：新增 `推荐/好友/分组/群聊/设备` 5 Tab，默认「分组」选中，`#1296db` + 22×3 下划线（复用 Channels Tab 模式）；好友/群聊 Tab 有真实数据，推荐/设备为空态。
- **可折叠分组 + 计数**：`特别关心 0/0`、`我的好友 3/6`、`我的群聊 3/3`、`多人聊天 2/2`；箭头 `#999`（展开旋转 90°）、计数 `#999` tabular-nums，点击整行折叠/展开。
- **A-Z 索引**：保留（010.jpg x≈600-720 确有竖排索引），字号 9→10.5px、行高 1.25→1.38。
- 文件：`src/tgqq/pages/Contacts/{index.tsx,Contacts.module.scss}`、`src/tgqq/components/TqTabHeader/{index.tsx,TqTabHeader.module.scss}`。

## 4. 动态页改造（对照 003.jpg）

- **渐变封面**：176px 高 `linear-gradient(160deg,#df81f9→#b6b0ff)`（左上实测 rgb(218,134,249)≈参考 010/003 的 (223,129,249)，右下 (184,174,255)≈(184,182,255)，R 通道跨封面下降 34，对比度可见）；含 64px 白环头像、18px 名字、副文、「Lv.3」半透白徽章、「开启我的动态空间 ›」行动条、右上 ≡ 菜单。
- **搜索浮条**：白底 `#fff` + `#ebebeb` 边框，上移压封面 19px（QQ9 白色搜索浮于彩色头部语义）。
- **入口图标网格**：8 项 4 列（好友动态/相册/收藏/文件/小世界/厘米秀/游戏/小程序），48px 渐变圆角图标 + 11px 标签。
- **功能卡片**：2×2 白卡（直播/小游戏/小程序中心/我的收藏），圆角 14、标题 15/600、子文 12、右侧 ⊕。
- **照片流保留**：新增「好友动态」区块标题，原 PostCard feed 置于 hub 之下（QQ9 动态页 = hub + 下方好友动态二级视图）。
- **底部导航**：动态图标 时钟→旗帜（`BottomNavigation` + fixture）。
- **强调色**：新增 `--tq-accent-dynamics`（light `#bb6bff` / dark `#c98aff`），封面头像使用。
- 暗色：封面 `#6a3fb0→#4a5bd0`，卡片/入口网格 `#2b2b2b`，文字浅色。
- 文件：`src/tgqq/pages/Dynamics/{index.tsx,Dynamics.module.scss}`、`src/tgqq/components/BottomNavigation/index.tsx`、`src/tgqq/design/{light,dark}.scss`。

## 5. 聊天页微调（对照 QQ9 聊天页）

| 项 | 修复 | 文件 |
|---|---|---|
| 发出气泡背景 | `#a6e3ff` → `#95ecff` | `src/tgqq/design/light.scss` |
| 发出时间戳 alpha | 0.55 → 0.45 | 同上 |
| 回复引用栏内边距 | `--tq-space-xs`(4px) → `--tq-space-sm`(8px) | `src/tgqq/design/chatInput.scss` |
| 表情面板超高兜底 | 新增 `max-height: 60vh`（W2 建议） | `src/tgqq/components/TqEmojiPanel.scss` |

已确认进 dist：`#95ecff`、meta `#00000073`(=0.45α)、`max-height:60vh`、space-sm。

## 6. Fixture 同步与修复

- `docs/tgqq/fixtures/tab.html`：联系人页（紧凑头部+快捷导航+5 Tab+折叠分组+计数+索引）、动态页（封面+浮条+入口网格+功能卡+feed 标题）、底部导航旗帜图标。
- `docs/tgqq/fixtures/css/fixture.css`：新增全部新模块样式 + 暗色覆盖（quicknav/分组头/入口网格/功能卡 → `#2b2b2b`，文字 `#e5e5e5`）。
- **修复既有 bug**：`tab.html` 频道「已关注」模板引用 `followRow()` 但函数从未定义（Round 21 遗留，导致整个 PAGES 脚本抛错页面空白），已补定义。
- 暗色联系人/动态卡片白底问题（终审 F）已修复：`html.night` 下 quicknav/分组头/entries/feature 卡均 `#2b2b2b`。

## 7. 验证

- `/tmp/r22_verify.js`：26/26 PASS（暗色下划线×3、联系人 11 项、动态 10 项、导航旗帜）。
- 像素抽样：暗色下划线 rgb(18,150,219) ✓；封面渐变与 003.jpg 对照在 ±15 内 ✓；搜索浮条 #fff ✓；计数/箭头 #999 ✓；暗色卡片 #2b2b2b ✓。
- codebuddy 终审 `/tmp/cb_final22_out.md`：10 PASS / 5 FAIL；聚焦复核 `/tmp/cb_final22b_out.md`：4 PASS / 1 FAIL；FAIL（封面渐变）已按 PIL 实测修正（`/tmp/cb_final22c_out.md` 因进程中断未产出，以本报告 PIL 数据为准）。终审中「计数偏浅/搜索条非白/桌面无 feed」三项经精确坐标复核为采样点误读（分别落在索引区/封面上方/右侧空态列），PIL 实测均符合规格。

## 8. 涉及文件清单

- `src/tgqq/pages/Contacts/index.tsx`、`Contacts.module.scss`
- `src/tgqq/pages/Dynamics/index.tsx`、`Dynamics.module.scss`
- `src/tgqq/pages/Channels/Channels.module.scss`（暗色 Tab 覆盖）
- `src/tgqq/components/TqTabHeader/index.tsx`、`TqTabHeader.module.scss`
- `src/tgqq/components/BottomNavigation/index.tsx`（旗帜图标）
- `src/tgqq/design/light.scss`、`dark.scss`、`chatInput.scss`
- `src/tgqq/components/TqEmojiPanel.scss`
- `docs/tgqq/fixtures/tab.html`、`css/fixture.css`

## 9. 下一步建议（Round 23）

- 聊天页主窗口（气泡/输入栏）已条件通过，可做更细的平板右窗视觉打磨（qq9-tablet 细节）。
- 联系人「推荐/设备」Tab 空态可补 QQ9 风格的推荐联系人/设备卡片。
- 动态 hub 的「互动标识」「关系挂件」两块（003.jpg y480-760）可作为下一轮扩展。
