# Round 10 计划 — 聊天页改造：QQ9 附件面板（「+」底部弹层）

- 日期：2026-08-14
- 前置：Round 9 密度校准完成（报告见 round9-density-report.md）
- 目标：tweb 的「+」附件菜单（`.btn-menu` 下拉列表）改造成 QQ9 样式底部面板

## 现状（tweb 原始行为）
- `src/components/chat/input.ts`：`attachMenuButtons` = 图片/文档/编辑/礼物/投票/日程…
- `ButtonMenuToggle({container: this.attachMenu, direction: 'top-right'})` 生成 `.btn-menu.top-right`，
  挂到 `getOverlayRoot()`（body 层），`positionMenuTrigger` 按按钮定位 → 下拉列表（图标+文字行）。
- 现有 QQ9 化：按钮本体已是「+」字符（`chatInput.scss .attach-file::before`）。

## 改造方案
1. **renderer hook（TW-UP-011）**：`input.ts` 中菜单元素创建后加标记类 `tq-attach-menu`，
   避免误伤其他 `.btn-menu`（消息右键菜单等）。
2. **CSS（chatInput.scss 新增块）**：
   - `.btn-menu.tq-attach-menu`：`position: fixed; left: 0; right: 0; bottom: 0;`
     圆角顶部 16px、白色底 `--tq-surface-primary`、阴影上浮、最大宽 640px 居中；
   - `.btn-menu-item` 改为 4 列网格（`grid-template-columns: repeat(4, 1fr)`），
     图标 52px 圆形浅色底（各功能不同色，参考 QQ9：#F0F7FF 蓝 / #FFF3E3 橙 / #E8F7EE 绿…），
     文字 12px 灰色居中；两行 = 8 个功能位；
   - 面板头部可加「常用」标题或关闭把手（CSS 伪元素，尽量不动 renderer）。
   - 手机全宽贴底；平板（tq-tablet）居中浮层 400px。
3. **fixture**：`mobile-chat.html` / `group-chat.html` 增加 `.btn-menu.tq-attach-menu` 静态 DOM
   （照片/拍摄/文件/语音通话/视频通话/位置/红包/转账），用于 shoot.sh 截图评审。
4. **验证**：puppeteer computed-style + magick 像素（面板位置、列数、图标底色、文字行高）；
   codebuddy 识图评审。

## 验收标准（对照 QQ9）
- 点「+」→ 底部弹层，顶部圆角、轻微上浮阴影、背景遮罩半透明；
- 4 列 x 2 行图标：圆底彩色 icon + 12px 标签，间距均匀；
- 点空白/遮罩关闭；与输入条、表情面板互斥（沿用 onOpen 里 emoticonsDropdown.toggle(false)）。

## 备注
- 若 CSS-only 无法完成（如遮罩层、动画），再考虑 renderer 小改（加遮罩 div）。
- 出站自头像真机验证、顶栏图标描边粗细等长尾项排在 Round 10 之后。
