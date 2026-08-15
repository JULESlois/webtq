# TGQQ Round 3 工作指令：平板结构（左侧手机主页 + 右侧聊天窗）

## 0. 背景与目标

Round 1 完成 mobile shell 与 design system 骨架；Round 2 修复了 skin 摇树问题并开启
聊天页（topbar/bubbles/composer）皮肤，但全部门控在 `mediaSizes.isMobile`（<600px）。

QQ 9 安卓平板模式（8.9.15+，参见 IT之家 https://www.ithome.com/0/648/309.htm）：
屏幕超宽后 **左侧为手机界面同款主页（消息/频道/联系人/动态 四 tab + 底部导航），
右侧为独立聊天窗**。手机版底部导航四 tab 为：消息 / 频道 / 联系人 / 动态。

### 本轮唯一目标

把 `≥600px` 的宽屏改为 **QQ 平板结构**：

1. 左侧一列呈现类手机主页：会话列表（`#column-left` 原生内容）+ 底部四 tab 导航。
2. 右侧为独立聊天窗：tweb `#column-center` 原位保留，套用 Round 2 的
   `tq-chat-header / tq-chat-bubbles / tq-chat-composer` 皮肤。
3. 皮肤门控从 `isMobile` 放宽到 **全部非大屏桌面三栏**（即所有宽度生效，
   `<600px` 保持手机形态，`≥600px` 为平板形态）。这是有意扩展，文档明示。

### 不做（本轮）

- `bubbles.ts` renderer / `input.ts` 逻辑 / MTProto / storage / auth 一律不碰（Red）。
- two-row composer、outgoing self avatar 仍缓做（Yellow，沿用 Round 2 结论）。
- 平板下右侧资料栏（`#column-right`）、会话文件夹侧栏（folders sidebar）只做
  CSS 隐藏，不做逻辑删除。
- 频道/联系人/动态三页在平板左侧的完整内容填充（QQ 平板右侧联动二级页）→ 后续轮。

## 1. 实现方案

### 1.1 状态门控（`src/tgqq/shell/index.tsx`）

- `updateSkinState()`：skin class 由 `flag && isMobile` 改为 `flag`（is-tgqq 即生效）。
- 新增 body class `tq-tablet`：`mediaSizes.isMobile === false`（≥600px）时加上，
  并在 `changeScreen / resize / tab_changing` 时同步。
- `<600px` 维持现状：全屏 shell + 底部导航盖在会话列表下；进入聊天全屏。

### 1.2 平板左侧主页（`TqTablet.scss` 新文件，`src/tgqq/index.ts` 引入）

目标：底部导航视觉上落在 `#column-left` 底部，宽度与左栏一致。

- `.tq-shell`（shell 根节点）在 `body.is-tgqq.tq-tablet` 下：
  - `position: fixed; inset-block: var(--page-chats-padding);`
  - `inset-inline-start: var(--page-chats-padding);`
  - `width: var(--left-column-visual-width);`（JS 已写 :root，360px 默认）
  - 这样 shell 恰好覆盖左栏 footprint（含 16px 页面 padding）。
- `.tq-shell .pages` 不变（abs inset 0 0 nav-height 0），覆盖左栏内部区域。
- 导航条 `.tq-bottom-nav` 沿用现有 `.root` 底部实现，宽度自动等于 shell 宽度。
- 左栏内容底部补白已存在（`tq-shell-on` 规则），平板下同样生效。

### 1.3 平板 600–925px 抽屉改并排（`TqTablet.scss`）

tweb 该区间 `#column-left` 是 floating drawer（absolute，默认 translate 出屏），
`#column-center` 在 `is-left-column-shown` 时 translateX(26.5625rem)。TGQQ 平板下改为：

```css
body.is-tgqq.tq-tablet #column-left {
  position: relative;            /* 回到文档流，与右侧聊天并排 */
  transform: none !important;    /* 无视 drawer 的显隐 transform */
  opacity: 1 !important;
  margin-inline-start: 0;
  border-radius: 0;
  box-shadow: none;
}
body.is-tgqq.tq-tablet #column-center {
  inset-inline-start: calc(var(--left-column-visual-width) + var(--page-chats-padding));
  inset-inline-end: var(--page-chats-padding);
  transform: none !important;
}
```

- `#column-center` 用 `inset-inline-*` 重新定位替代 translateX，聊天紧贴左栏。
- `--chat-width` 在浮动区间由 JS 设为 `vw-2*padding`，超出实际宽度时
  `.bubbles-inner / .topbar / .chat-input` 的 `max-width` 不会撑破父容器
  （`max-width` 仅上限，`width:100%` 受父容器约束）——fixture 截图验证。
- `--left-column-width`（layout 宽度）在浮动区间 = 360，与 visual 一致。

### 1.4 平板 >925px（tweb docked 区间）

tweb 此处左栏本就在文档流中、聊天本就在其右侧，无需改列布局：
- 皮肤自动生效（1.1）。
- shell 底部导航落在左栏底部（1.2）。
- 隐藏 folders sidebar 与右侧资料栏的视觉侵入：
  `body.is-tgqq.tq-tablet body.has-folders-sidebar ...`（具体选择器实现时核对
  `src/scss/partials/_foldersSidebar.scss` 的 DOM 结构）。
- 聊天 topbar 的返回按钮（`.sidebar-close-button`）在平板下隐藏：
  `body.is-tgqq.tq-tablet .topbar .sidebar-close-button { display: none !important }`。

### 1.5 会话列表内顶部区域（沿用 Round 1 的 dialogSkin）

左栏顶部搜索框、会话条目等继续使用 `tq-dialog-skin`（Round 1 草稿，Round 2 已激活）。
本轮若截图发现顶部搜索框与 QQ 胶囊差异过大，作为视觉微调项处理，不扩 scope。

## 2. 验证（无 Telegram seed，必须静态 fixture）

1. `NODE_OPTIONS=--max-old-space-size=6144 node /root/.npm/_npx/.../tsc --noEmit -p tsconfig.json`
2. `./node_modules/.bin/vite build`（约 21s），确认 `dist/tgqq-*.css` 含
   `tq-tablet` 相关选择器。
3. fixture HTML（`docs/tgqq/fixtures/`）：
   - 引入 `dist/index-*.css` + `dist/tgqq-*.css`（真实产物），外加一小段
     fixture 结构 CSS（复刻三栏布局关键规则 + CSS 变量），不引 app JS。
   - DOM 复刻 tweb 类名：`.page-chats > #main-columns > #column-left/#column-center`、
     `.chatlist-chat`、`.topbar`、`.bubble.is-out`、`.chat-input` 等。
   - 三档窗口：390x844（手机）、900x700（平板中档 600-925）、1180x820（平板宽）。
   - chromium headless `--screenshot --window-size=WxH --hide-scrollbars file://...`。
4. codebuddy（`codebuddy -p`，支持读图）对比 QQ9 参考图
   （`docs/tgqq/ref/qq9-mobile2/`、`qq9-chat/`）逐项核对：左栏主页、底部导航、
   聊天 topbar、气泡、输入区；按反馈迭代。

## 3. 风险分级

### Green（本轮做）
- skin 门控放宽（all widths）
- `tq-tablet` 平板布局（600-925 并排、>925 沿用 docked）
- 底部导航收进左栏
- 平板下隐藏 topbar 返回按钮

### Yellow（记录，本轮不做）
- 平板下非消息 tab 的右侧联动二级页
- two-row composer、outgoing self avatar
- 平板下 folders sidebar / 右侧资料栏的完整替代页

### Red（禁止）
- `bubbles.ts` / `input.ts` / MTProto / storage / auth / langPack 语义改动
- 重排 `chat-input-control` 的 absolute 定位
- 改动 tweb 列宽 JS（`updateColumnWidths.ts`）

## 4. 交付物

- `src/tgqq/shell/index.tsx`（门控 + tq-tablet）
- `src/tgqq/components/TqTablet.scss`（平板布局，新增）
- `src/tgqq/config/flags.ts`（如需新 flag）
- `docs/tgqq/fixtures/*.html` + 截图
- `docs/tgqq/round3-tablet-report.md`（收尾报告）
- `docs/tgqq/upstream-patches.md` 更新
