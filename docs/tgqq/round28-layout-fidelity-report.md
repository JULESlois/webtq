# TGQQ Round 28: 布局保真修复（手机列表贴边 / 高度链 / 滚动留白 / 平板左栏 400px）

日期：2026-08-16
基准：`0e57384`（Round 27b，已推送）

## 结论

本轮没有改产品逻辑，全部是**布局与 fixture 保真**问题：

1. **真实应用**：QQ9 平板模式左栏从 360px 加宽到 400px（列、底部导航、聊天窗偏移三处
   用同一 `--left-column-visual-width`，body 作用域统一覆盖，几何探针确认一致）。
2. **fixture 修正**（此前截图与真实应用不符的假象，全部经几何探针验证）：
   - 手机端 `--page-chats-padding` 归零：真实应用 JS 在 handheld 下写 0
     （`PAGE_CHATS_PADDING_ROOT_HANDHELD`），fixture 硬编码 16px 导致列表内缩 16px；
     修正后 QQ 手机消息列表全宽贴边。
   - 左栏高度链：真实应用靠 `#column-left > .sidebar-slider > .item-main >
     .sidebar-content > #chatlist-container` 的 flex 链把列表收口到视口内；fixture
     省略中间层，`max-height:100%` 直接对整列解析 → 列表溢出视口 100px+，最后一行
     被固定底导航遮挡。fixture 补 `flex:1 1 auto; min-height:0` + 列高 100%。
   - 滚动行为：tweb 的自定义滚动类（`.scrollable.scrollable-y`）由 JS 挂到列表滚动
     容器；fixture 静态页缺失 → `.folders-scrollable` 需补 `position:absolute;
     inset:0; overflow-y:auto`。配合 tgqq 已有规则
     `folders-scrollable{padding-bottom:calc(var(--tq-nav-height)+...)}`，
     滚动到底时最后一行完整浮出底导航上方。
   - 重新跑 `shoot.sh`：`css/tgqq.css`、`css/tweb.css` 从新 dist 同步，40 张关键截图
     重拍。

## 验证（puppeteer 几何探针，全部通过）

- mobile 390x844 / 360x800：`#column-left` 高 = 视口，`#chatlist-container`
  bottom = 视口底，body 无溢出；滚动到底最后一行 bottom = 导航 top（744/788），
  无遮挡。
- tablet 640/900/1200/1440：左栏与 shell 恒为 400px，`#column-center` 从 x=400 起；
  列表滚动到底同样清出导航。
- 移动聊天页（mobile-chat）几何无变化（本轮不涉及），截图基线未变。

## 文件清单

- `src/tgqq/components/TqTablet.scss`：平板左栏 400px（真实应用唯一改动）
- `docs/tgqq/fixtures/css/fixture.css`：手机 padding 0、列高链、滚动容器、列宽 400
- `docs/tgqq/fixtures/css/{tgqq,tweb}.css`：从 dist 重新同步
- `docs/tgqq/fixtures/shots/*.png`：40 张截图刷新

## 风险

- 平板列宽变更影响 600-640px 极窄段（聊天窗 240px），几何探针确认顶栏/气泡/输入区
  无重叠；如需更保守可回落 380px。
- fixture 改动只影响预览；真实应用相关行为（手机 padding、列表滚动留白）原本已正确，
  本轮将其在 fixture 中如实呈现。
