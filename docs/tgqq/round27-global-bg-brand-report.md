# TGQQ Round 27: 全局背景去 Telegram 化 + 站点品牌（标题/图标/清单）

日期：2026-08-16
基准：`7e4a2bc`（Round 26 聊天列表错位修复，已推送）

## 结论

- 全局 Telegram 壁纸层已从**所有视图**移除：登录页、聊天列表、聊天页、平板双栏一律换为 QQ9 扁平底色（浅色 `#f3f2f7` 页面 / `#f0f4f8` 聊天区，深色 `#1a1a1a` / `#191919`）。
- 站点品牌改为 WebQQ：`<title>`、各 `meta`（application-name / og / twitter / 移动端标题）、favicon 全套（16/32/180/192/512 + SVG）、`site.webmanifest` 运行时重写（name / short_name / icons / theme_color / background_color）。
- 验证（puppeteer 真实 dist 登录页）：
  - `html` 带 `tq-app`，`document.title === 'WebQQ'`；
  - body 背景 `rgb(243,242,247)`；body 首子元素壁纸层被标记 `tq-bg-layer` 且 `display:none`（含 canvas，识别准确）；
  - 图标链接全部指向 qq-icon 资源（16/32 由 vite 内联为 data URI，180/192/512 为产物文件，alternate icon → SVG）；
  - `#manifest` href 已变为 blob URL（重写后的清单）；
  - 登录页截图像素统计：QQ 灰白占绝对主导，无 Telegram 蓝紫渐变残留。

## 背景层识别与隐藏机制

Telegram 壁纸层来源：`src/components/chat/bubbles/chatBackground.tsx` 的 `appChatBackground`
单例——`src/index.ts` 启动即 `attach()`，把一个**无 id/无 class 的裸 div** 插为
`body` 首子元素，Solid 再渲染渐变/图案 canvas 进去（登录页也挂）。

处理：
- `src/tgqq/boot.ts`（新模块，`src/index.ts` 顶部一行 import，见 TW-UP-014）：
  - 模块求值即给 `<html>` 加 `tq-app`，并注册 MutationObserver + 定时重扫；
  - 识别规则：body 直接子元素 ∧ 无 id ∧ 无 class ∧ 含 `<canvas>` → 打上 `tq-bg-layer`；
  - 内联 `<ChatBackground>`（壁纸预览、passcode 锁屏——后者挂 overlay root 且有 class）不受影响。
- `src/tgqq/design/TqGlobal.scss`：`html.tq-app body` 底色 = `--tq-surface-page`；
  `html.tq-app body > .tq-bg-layer { display:none !important }`；登录页所需的
  少量 surface token 也在此定义（完整 `.is-tgqq` 令牌集登录后照常接管）。

## 品牌注入

- 标题：`WebQQ`；同步 `application-name` / `mobile-web-app-title` /
  `apple-mobile-web-app-title` / `og:*` / `twitter:*` / description。
- 图标：新建 `src/tgqq/assets/qq-icon.svg`（QQ 蓝渐变圆角方块 + 白色企鹅，
  与现有 QQ 蓝 `#12b7f5→#1296db` 一致），`rsvg-convert` 生成 16/32/180/192/512
  PNG；`boot.ts` 按 `sizes` 替换全部 icon 链接（apple-touch → 180 PNG）。
- 清单：DOMContentLoaded 后（等上游 `setManifest` 先指好目标）fetch
  `site.webmanifest` → 改品牌字段与图标 → blob URL 重设；fetch 失败（本地
  `copyPublicDir:false` 构建无 public 文件）时兜底自建清单。
- 未读徽标 favicon 恢复链路不受影响：`uiNotificationsManager` 在登录后才构造，
  其捕获的 faviconElements 已是我们替换后的 QQ 链接。

## 文件清单

- 新增 `src/tgqq/boot.ts`、`src/tgqq/design/TqGlobal.scss`、
  `src/tgqq/assets/qq-icon.svg` + `qq-icon-{16,32,180,192,512}.png`
- 上游一行：`src/index.ts`（`import '@/tgqq/boot';`）
- 文档：`docs/tgqq/upstream-patches.md`（TW-UP-014）

## 风险

- 识别规则严格（body 直接子元素 + 裸 div + canvas），tweb 其余 body 级容器均有
  id/class；多账户/主题切换不重建该层（attach 幂等），标记一次即永久隐藏。
- 深色模式经 `html.night.tq-app` 同规则覆盖，与 `.is-tgqq` 夜间令牌一致。
