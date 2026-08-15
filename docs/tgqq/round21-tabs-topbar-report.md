# Round 21 — 频道/联系人/动态三页顶栏 QQ9 同构改造（报告）

- 日期：2026-08-15
- 前置：Round 20 聊天页收尾全 PASS（round20-chat-page-report.md）；本轮为全页面横向对照审计
- 循环：codebuddy 横向审计（`/tmp/cb_round21_result.md`，参考 `qq9_000_full.png`/`qq9_001_full.png`/`qq9-mobile2/*`）→ 逐项像素/参考图复核（纠出 2 条误报）→ 修复 → build/shoot → puppeteer 自验（`/tmp/r21_verify.js` 33/33 PASS）→ codebuddy 终审（`/tmp/cb_final21_out.md`）→ 本报告

## 1. QQ9 参考规格（像素实测 + 官方更新帖）

- **权威文字规格**（yooqur.com/thread/522802-1.html，QQ9 官方更新帖）：QQ9 新版频道页「上方头像和搜索框会和消息页高度一致，且最右边还有个 ⊕」。
- **消息页顶栏**（`qq9_000_full.png` 720×1600）：头像+名字+在线状态（左，红底人像 ~40px）+ 右侧图标行 + 搜索胶囊其下；**无页面大标题**。
- **频道页顶栏**（`qq9_001_full.png`）：与消息页同高同构——头像+名字/状态 左、右侧图标行含 ⊕、搜索胶囊其下；内容区为空态/加载态。
- **联系人页**（`qq9-mobile2/010.jpg`）：头像+名字 左 + 右侧图标 + 搜索胶囊；内容区含联系人分组与**右侧 A-Z 索引条**（逐像素复核：x≈645-685 全程存在竖排字母索引，非新增元素）。
- **动态页**（`qq9-mobile2/003.jpg`）：头像左 + 右侧图标；内容为动态 hub（本轮未改动态内容，见遗留）。

## 2. codebuddy 审计结论与逐项处置（TOP8）

审计 PASS：三页内容区（频道卡片/联系人分组/动态 feed）、暗色、底部导航。

| 审计项 | 结论 | 处置 |
| --- | --- | --- |
| #1 三页顶栏结构错误：`[标题左+头像右]` vs QQ9 `[头像+状态左+右侧功能图标]`，且无标题文字 | **属实（致命）** | 新建共享组件 `TqTabHeader`：`[40px 红底头像 + 名字「我」+ 绿点「手机在线 · WiFi」] + [右侧 32px ⊕ 添加钮] + 搜索胶囊`，三页统一替换旧 `[标题+头像]` 头部；几何与消息页侧栏个人行一致（y10-50 / y58-96） |
| #2 三页均缺失最右 ⊕ 图标 | **属实** | TqTabHeader 右侧 32px 圆形 ⊕（浅色 `#f0f0f0` / 暗色 `#373737`，与消息页 `.tgqq-profile-add` 同构）；动态页原相机+头像一并收敛为 ⊕ |
| #3 频道页「推荐/关注」Tab 条占用规范顶栏高度 | 部分属实 | Tab 条移出 `<header>`，置于搜索胶囊下方、内容区上方（y106-140）；功能保留（推荐/关注双面板联动不受影响） |
| #4 搜索胶囊独立下沉、未与头像行同构同高 | **属实** | 新头部 gap 8px + padding 10/16/8，与消息页 `main-search-sidebar-header` 同构；搜索胶囊 y58-96 38px 圆角 |
| #5 联系人页缺二级 Tab（推荐/好友/分组/群聊/设备） | **误报** | 参考 `qq9-mobile2/010.jpg` 内容区逐像素复核：搜索胶囊下直接是联系人分组行，未见二级 Tab 条 |
| #6 联系人分组可折叠+计数 | 证据不足 | 参考图仅能确认分组标题行，折叠态/计数文案无法从像素可靠判读；留待高清参考 |
| #7 动态页内容形态应为 hub（非照片流） | 证据冲突 | `qq9-mobile2/003` 为 QQ9 新版动态 hub；但 `qq9-mobile/003-004` 为照片 feed（Round 11 依据），两版并存；hub 内标签文字无法像素判读，本轮保留照片流，留待高清参考再改 |
| #8 联系人 A-Z 索引条为新增非参考元素 | **误报** | 复核 `qq9-mobile2/010.jpg`：右侧 x≈645-685 全程存在竖排字母索引，QQ9 联系人页确有索引条，予以保留 |

## 3. 改动文件

### 新增 `src/tgqq/components/TqTabHeader/`（index.tsx + TqTabHeader.module.scss）
- 共享 QQ9 顶栏：个人行（40px 红底人像 + 名字 + 绿点状态 + 32px ⊕ 添加钮）+ 搜索胶囊；CSS token 化（`--tq-surface-secondary`/`--tq-text-*`/`--tq-accent-online`），浅/暗自动适配；几何与消息页侧栏个人行一致。

### `src/tgqq/pages/{Channels,Contacts,Dynamics}/index.tsx`
- 三页顶栏统一替换为 `<TqTabHeader searchPlaceholder={...}/>`（占位符沿用 `Tgqq.Channels.Search` 等 i18n 键）；删除原 `[h1 标题 + 头像]` 头部。
- Channels：「推荐/关注」Tab 条移出 header 到内容区上方（功能不变）。
- Dynamics：原 `headerActions`（相机按钮 + 头像）删除，收敛为 ⊕。

### `src/tgqq/pages/{Channels,Contacts,Dynamics}/*.module.scss`
- 删除废弃的 `.header/.headerRow/.title/.avatar/.search/.searchIcon/.headerActions/.iconBtn` 样式（约 60 行/页）。

### 夹具 `docs/tgqq/fixtures/tab.html` + `css/fixture.css`
- 三页头部替换为 `.tgqq-profile` 个人行（复用消息页 fixture 组件样式）+ `.tq-search`；Tab 条移到 header 外。
- `.tq-page-header` padding 12/16/10→10/16/8、gap 10→8，与消息页同构。

## 4. 验证结果

### puppeteer computed-style + 几何自验（`/tmp/r21_verify.js`）—— 33/33 PASS
- 三页（channels/follow/contacts/dynamics）：无 `.tq-page-title`、无旧 `.tq-page-avatar`；个人行 y10 h40、头像 40×40、⊕ 32×32（x312 y14）、搜索胶囊 y58 h38 圆角；频道/关注页 Tab 条 y106 在 header 外。
- 暗色：名字 `rgb(229,229,229)`、状态 `rgb(179,179,179)`。

### 像素复核（PIL）
- 三页浅色：头像红底 `#FDDAD8` 中心、⊕ 圆钮 `#F0F0F0` + 深色 `+`（30 暗像素）、搜索胶囊 `#F0F1F5`、绿点 `#00D66C`；暗色：背景 `#1A1A1A`、搜索 `#373737`、⊕ 背景 `#373737`。
- 顶栏纵向几何与消息页一致（头像 y10-50、搜索 y58-96，同一套 padding/gap）。

### codebuddy 终审（`/tmp/cb_final21_out.md`）
- A 三页顶栏结构 PASS（头像+状态左、⊕ 右、搜索其下、无大标题）；B 头像 40px/⊕ 32px/搜索 38px 圆角 PASS；C Tab 条位置/浅色选中蓝 PASS；D 暗色同构 PASS；E 内容不回归 PASS；F 底部导航 PASS。
- 唯一 FAIL：暗色频道 Tab 选中下划线 `#35A7E8` 未符合终审 prompt 中写的 `#1296DB`——**误报**：本项目设计系统在暗色下统一提亮主色（`src/tgqq/design/dark.scss` `--tq-accent-primary: #4eb0f5`；fixture 暗色 Tab 自 Round 18 起即批准为 `#35a7e8`），与 QQ9 暗色提亮惯例一致；终审 prompt 未写明暗色变体所致，代码无需改动。

## 5. 记账

- 本轮源码改动：新增 `src/tgqq/components/TqTabHeader/*`；修改 `src/tgqq/pages/{Channels,Contacts,Dynamics}/index.tsx` + 3 个 module.scss——均在 `src/tgqq/` 私有目录，无 upstream 补丁。
- fixture：`docs/tgqq/fixtures/tab.html`、`css/fixture.css`、`shoot.sh`（无新增规格）、`shots/*`（42 PNG 重生成）。
- 未提交（延续惯例：`src/tgqq/`、`docs/tgqq/` 为私有工作区）。

## 6. 遗留 / 后续
- 联系人页二级 Tab/可折叠分组计数（#5/#6）：需更高清 QQ9 参考图确认后实施。
- 动态页 hub 化（#7）：QQ9 新旧两版并存（hub vs 照片流），需确认目标版本后改造。
- 真实 app 顶栏个人行数据：目前硬编码「我 / 手机在线 · WiFi」，后续可接 tweb 当前账号数据（与侧栏个人行一致）。
