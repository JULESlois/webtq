# TGQQ Round 23 — 动态页下半部（搭子/互动标识/幸运字符/新奇物种/DNA）+ 联系人推荐/设备 Tab 报告

> 范围：对照 QQ9 Mobile2 `003.jpg` 下半部实现动态 Hub 的 6 个新模块；补齐联系人页「推荐/设备」Tab 内容。
> 验证：fixture DOM 自验 **12/12 PASS**；codebuddy 视觉复审（light + dark 全模块）**10/10 PASS**；构建 `vite build` 通过。

---

## 1. 动态页下半部（003.jpg img y580–1600 精读实现）

### 1.1 搭子入口卡片（Block 1）
- **单张淡紫渐变卡**（非白卡、非 4 张独立卡）：`linear-gradient(135deg,#f1eaff→#e9ecff)`。
  - 以 PIL 采样参考图证实：卡片区 y284–377 全行呈连续浅紫渐变 rgb(244,237,255)→(242,246,255)，列间隙无底色露出 → codebuddy 首轮「4 张独立淡紫卡」与精读「白卡」均不准确，按采样修正。
- 4 列等宽：梦搭子/王者搭子/学习搭子/运动搭子；标题 14px/600、副标题 11px `#999`。
- 底部 **36px 深紫圆形加号按钮** `#b7b5fe`（参考实测 rgb≈(183,181,254)）+ 白色 `+`。
- 暗色：卡 `#3d3a55→#333a52`、按钮 `#6b6fd0`。

### 1.2 互动标识卡（Block 2）
- 白卡 14px 圆角；头行「互动标识」15px/600 + 计数「3/23」13px `#999` + 右侧 `›`。
- 4 个 52px 圆图标，**flex 左对齐、10px 间隙**（采样参考图标中心 55/117/180/241，间距 62px，与标题左对齐，非 grid 均分）：
  1. 紫青渐变吉他 + 右下红底白字 Q badge（`#fa5151`）
  2. 青蓝渐变水滴（`#4ecdc4→#44a8b3`）
  3. 黄底多色花瓣花（粉 `#ffb3d1`/白瓣 + 杏黄心，参考实测含粉/黄混合色）
  4. 浅灰占位「20个 / 待点亮」10px `#bbb`
- 暗色：卡 `#2b2b2b`，占位格 `#373737`。

### 1.3 幸运字符卡（Block 4）
- 分节标题「我们的幸运物种」13px `#999`，左 16px。
- 白卡 12px 圆角 flex 行：左 **48×48 黑金「X」符文方块**（底 `#2a1810`、金边 `#c4a35a`、金 X 2.6 描边）+ 中列「幸运字符」15px/600 + 「抽取专属字符」12px `#999` + 右「开启 〉」`#1296db`。

### 1.4 新奇物种卡（Block 5）
- 分节标题「新奇物种」同规格。
- 白卡 flex 行：左 48×48 粉蓝渐变底 Q 版双角色 SVG（粉 `#ff9ecb` + 蓝 `#7ec8ff` 圆脸 + 微笑）+「解锁聊天新玩法」/「我是超级可爱的新奇物种」+ 右「去养成 〉」`#1296db`。

### 1.5 「我们的DNA」分节 + 分割线（Block 6）
- 分节标题 + 1px `--tq-border-light` 分割线（左右 16px）。

## 2. 联系人页推荐/设备 Tab 补齐

- **推荐**：分节标题「推荐联系人」+ 3 行推荐卡片（渐变头像 + 名字 + 推荐来源说明 + 右侧「添加」胶囊按钮 `#1296db`）。
- **设备**：分节标题「我的设备」+ 3 行（圆形灰底设备图标 SVG：手机/电脑/平板 + 名称 + 状态/上次登录 + 右侧 `›`）。
- 空态分支移除；默认 Tab 仍为「分组」。
- fixture `tab.html` 支持 `ctab=recommend|device` 参数渲染对应视图（含暗色）。

## 3. 修正记录（PIL 采样 vs codebuddy 分歧）

| 争议项 | codebuddy 说法 | PIL 采样结论 | 处理 |
|---|---|---|---|
| 搭子卡容器 | 精读：白卡；视觉复审：4 张独立渐变卡 | 单张淡紫渐变卡（y284–377 连续渐变） | 单卡渐变 ✓ |
| 加号按钮 | 精读：灰底黑+ | 深紫底白+（rgb≈183,181,254） | `#b7b5fe` 白+ ✓ |
| 幸运字符/新奇物种卡 | 视觉复审：卡外有卡名+分割线 | 卡上方灰字为分节标题，卡内中列即标题 | 保持卡内标题 ✓ |
| 图标行对齐 | 视觉复审：grid 左对齐 FAIL | 参考图标中心 55/117/180/241 左对齐、间距 62px | flex+10px gap ✓ |

## 4. 验证

- **构建**：`npx vite build` 通过，dist 含新样式类（`partners`/`badges`/`assetCard`/`sectionLabel`/`dnaDivider`）。
- **DOM 自验**（`/tmp/r23_dom_check.js`，puppeteer，900×700 + 390 宽）：dynamics/dynamics-mobile 的 `.tq-partners/.tq-badges/.tq-asset-card×2/.tq-dna`、contacts-recommend `.tq-add-btn×3`、contacts-device `.tq-device-icon×3/.tq-row-arrow×3` **12/12 PASS**。
- **codebuddy 视觉复审**（`dynamics-long.png` 390×1400 + dark，对照 003.jpg）：封面/搜索/入口/功能卡/搭子卡/互动标识/分节标题/幸运字符/新奇物种/DNA/feed **10/10 模块 PASS**，暗色专项全 PASS；仅 2 项非阻塞观察（图标素材已按参考改进、`〉` 字符在 headless 截图字体回退属环境问题）。
- 截图：`docs/tgqq/fixtures/shots/dynamics-long.png`、`dynamics-long-dark.png`、`contacts-recommend.png`、`contacts-device.png` 等。

## 5. 变更文件

- `src/tgqq/pages/Dynamics/index.tsx`、`src/tgqq/pages/Dynamics/Dynamics.module.scss`
- `src/tgqq/pages/Contacts/index.tsx`、`src/tgqq/pages/Contacts/Contacts.module.scss`
- `docs/tgqq/fixtures/tab.html`、`docs/tgqq/fixtures/css/fixture.css`、`docs/tgqq/fixtures/shoot.sh`
- 报告：`docs/tgqq/round23-dynamics-lower-contacts-report.md`
