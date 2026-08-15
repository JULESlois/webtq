# Round 5 — 频道 / 联系人 / 动态 三个 Tab 页（完成）

> 范围：把 shell 底部四 tab 中三个占位页（EmptyState）替换为 QQ9 风格的完整页面；
> 同时落地 Round 4 终审提出的几处真实问题（附件"+"、动态 tab 红点、左列个人行）。

## 新增/修改

### 1. 三个 Tab 页组件（SolidJS + CSS Modules，mock 数据）

- `src/tgqq/pages/Channels/index.tsx` + `Channels.module.scss`
  - 头部：标题"频道" + 右上角个人头像圆 + 大圆角搜索胶囊（38px / 19px 圆角）。
  - 「推荐频道」横向滑动卡片（132px 白卡、渐变封面 + 名称 + 简介 + 关注数 + "+ 关注"按钮）。
  - 「行业频道 / 兴趣频道 / 常逛的小频道」三个分组列表（44px 圆角方块头像 + 名称 + 简介 + 关注数 + 关注按钮）。
- `src/tgqq/pages/Contacts/index.tsx` + `Contacts.module.scss`
  - 头部：标题 + 头像 + 搜索胶囊。
  - 分组：「新朋友 / 我的群聊 / 我的好友 / 多人聊天」，行 = 圆形头像 + 昵称 + 状态小字；
    在线好友头像右下角 11px 绿色在线点；新朋友带红色胶囊角标。
  - 右侧 A-Z 字母索引条（absolute，9px 宽，贴列右缘；列表行 `padding-inline-end: 26px` 让位）。
- `src/tgqq/pages/Dynamics/index.tsx` + `Dynamics.module.scss`
  - 头部：标题"动态" + 相机圆钮 + 头像 + 搜索胶囊。
  - 动态流卡片（白底 14px 圆角）：头像/昵称/时间 + 正文 + 图片区
    （1 张大图 / 3 图横排 / 9 宫格，6 组渐变照片占位）+ 点赞/评论/转发操作行。
- 三页均通过 `TqMobileShell.tsx` 既有 `Switch` 挂载，底部 tab 点击即切换。

### 2. Round 4 终审确认的修复

- **输入条附件按钮：回形针 → "+"**
  - `src/tgqq/design/chatInput.scss`：隐藏 `.attach-file .button-icon`，`::before` 渲染 `+`（26px，浅字重）。
  - fixture（tablet.html）同步换成 "+" 内联 SVG。
- **动态 tab 常驻橙红点**
  - `src/tgqq/components/BottomNavigation/index.tsx`：dynamics 项 icon 外包 `iconWrap`，新增 `i.dot`。
  - `BottomNavigation.module.scss` + `design/light.scss` / `dark.scss`：新 token `--tq-accent-orange: #ff6b35`。
- **左列头部个人行（QQ9：头像 + 昵称 + 绿点"手机在线·WiFi" + "+"）**
  - fixture（tablet/mobile/tab）直接换结构；
  - 真实应用：`index.html` 头部加 `.tgqq-profile` 行，`sidebarLeft/index.ts` 用
    `appUsersManager.getSelf()` 填充昵称/头像首字/在线状态，见 TW-UP-008。

### 3. i18n

- `src/lang.ts` + `src/scripts/out/langPack.strings` 新增 11 键
  （搜索占位 3 + 频道分组 5 + 联系人分组 3），见 TW-UP-009。

## Fixture 与验证

- 新 fixture `docs/tgqq/fixtures/tab.html`：`?tab=channels|contacts|dynamics` + `&mobile=1`，
  一个文件覆盖三个页面 + 手机全屏模式；底部 nav 用真实构建出的 module 类名（`_root_rma6i_1` 等）。
- `shoot.sh` 新增 4 张：`channels-tab` / `contacts-tab` / `dynamics-tab`（900x700 平板左列）
  + `dynamics-tab-mobile`（390x844）。
- Puppeteer 几何验证（900x700）：
  - shell 0,0 360x700；nav 0,644 360x56；三页头部/搜索/列表/卡片均在列内，无重叠。
  - 联系人索引条 x=348..357（列右缘），行文字至 344，不重叠。
  - tablet.html 回归：topbar 0..52 / viewport 52..630 / input 630..700 不变；搜索胶囊 36px。
- 排查记录：
  - `.main-search-sidebar-header` 改纵向 flex 后，`.input-search{flex:1}` 会把胶囊压到 24px
    （flex-basis:0 覆盖 height），已加 `.input-search{flex:none;width:100%}` 修复。
  - tab.html 曾因 `PHOTO_GRADS` 声明在 PAGES 字面量之后触发 TDZ 报错导致整页空白，已把常量前置。
- codebuddy 两轮评审：首轮 12 条问题 → 已修（搜索图标 18px、动态底部留白 32px、
  照片占位 6 组暖色渐变、联系人行右留白）；终轮仅剩设计意图项（横滑卡片露出下一张、
  平板右列留白、占位图为 fixture 限制——真实应用将渲染 Telegram 图片）。

## 已知边界

- 三页数据为 mock；后续可接 tweb 真实数据（频道/联系人/Stories）。
- 动态图片为渐变占位（chromium 无彩色 emoji/图片素材），真实 Telegram 图片会正常显示。
- 推荐频道横滑卡片"露边"是 QQ9 滚动暗示，非 bug。
- 平板 900px 下右列空白是设计意图（QQ 平板 = 左主页 + 右聊天，聊天未开时不占位）。
