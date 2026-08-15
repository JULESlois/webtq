# TGQQ Round 24：QQ9 设置页（通用 / 辅助功能）

> 目标：把 Telegram Web 的左栏头像/菜单入口接入 QQ9 设置页，还原参考图
> `docs/tgqq/ref/qq9-mobile2/004.jpg`（设置-通用）与 `005.jpg`（设置-辅助功能）。

## 交付内容

### React（真实皮肤）
- 新增 `src/tgqq/pages/Settings/index.tsx` + `Settings.module.scss`：
  - 通用屏（004）：模式选择卡（三列模式卡，普通模式选中）、夜间模式跟随系统、使用移动网络改善语音质量（含页底说明）、字体大小、存储空间/聊天记录设置/自动下载与保存、系统通知栏显示QQ图标/回车键发送消息/使用群文件在线预览服务（含说明）。
  - 辅助功能屏（005）：头像双击/撤回/语音视频通话/超级QQ秀（4 行）、表情推荐/怼图（2 行）、彩签设置/主页底部导航栏设置/语音消息自动转文本(SVIP)/更多功能设置（4 行）。
  - 导航头：56px 与页面同色，左返回箭头（`#313133`），标题 18px/500 居中。
  - 行高 45px、图标 22px、主文字 16px、分割线 `#e5e5e5` 0.5px 左缩进 50 右 16；开关 40×22（ON `#0099ff`、OFF `#e5e5e5`）；说明文字 13px 灰、位于卡片外的页面背景上。
  - 暗色全套：页面 `#1a1a1a`、卡片 `#2b2b2b`、文字 `#e5e5e5`、开关 ON `#4eb0f5` OFF `#3a3a3a`、分割线 `#373737`、SVIP 徽章深金 `#3a2f1e/#e0a94e`。
- `src/tgqq/shell/TqMobileShell.tsx`：注册 settings 页；设置页全屏（隐藏底部导航，pages 区域延伸到底）；onMount 向左栏个人卡片注入齿轮按钮（`.tq-profile-gear`）作为 QQ9 式入口（消息页头像行右侧，与「+」并列）。
- `src/tgqq/components/BottomNavigation/index.tsx`：`selected` 类型扩展支持 `'settings'`（导航项不新增）。

### Fixture 与截图
- `docs/tgqq/fixtures/tab.html`：新增 `PAGES.settings`（通用）与 `sub=accessibility`（辅助功能）两屏；左侧栏个人卡片加入齿轮入口；设置页全屏（隐藏底部导航）。
- `docs/tgqq/fixtures/mobile.html`：消息页头像行同样加入齿轮按钮（真实入口截图）。
- `docs/tgqq/fixtures/css/fixture.css`：镜像设置页样式（`.tq-settings-*`）。
- `docs/tgqq/fixtures/shoot.sh`：新增 10 张截图（mobile/tablet/long/dark × 通用/辅助功能）。
- 同步修复：CSS module 哈希变更后 fixture 中失效的 shell 类名（`_root_xi3m0_1` → `_root_10x2p_1`，涉及 tab/mobile/tablet.html）——否则平板端侧栏会盖住 shell 页面。

## 像素级还原验证（PIL 采样参考图 vs 截图）

参考图实测（纠正 codebuddy 误读）：
- 页面底色 `#F3F2F7`（与项目 token 一致），卡片纯白、圆角 12、卡距 12。
- 开关 ON 实测 `#0099FF`（codebuddy 报 `#00A0E9` 错误）；尺寸约 38×21（非 48×30）。
- 图标实测深灰 `#313133`（codebuddy 报 `#8E8E93` 错误）。
- 主文字 `#1B1C1E`，次要文字 `#908F94`，分割线 `#E5E5E5`。
- 行高实测约 44.5px；模式卡高约 96px、间隙 12、选中卡蓝描边+蓝底白勾单选钮（贴右下角）；说明文字在卡片外页面背景上。
- 004 标题经字形分析为「设置」（讠+置），codebuddy 报「通用」错误。
- SVIP 徽章为金色小字（参考图无橙色底），实现取浅金底深金字药丸。

截图验证：
- 10 张设置截图全部通过底色/卡片/开关/暗色像素断言；暗色与亮色均含正确 token 色值。
- 分割线实测 x 50..356（左 50 右 16）；底部导航在设置页已隐藏（底部 60px 纯页面底色）。

## codebuddy 终审

`codebuddy` 对比参考图与截图输出 `/tmp/cb_settings_review.md`：9 项清单 7 PASS、2 FAIL，3 个改进点（分割线缩进、SVIP 药丸圆角、设置页隐藏底栏）。已全部修复并经 PIL 复核；其两处文字/色值误读（标题、开关色）以像素实测为准。

## 待办

- 推送仍未完成：`origin` 为上游 `morethanwords/tweb`（无写权限）；gh 登录 `JULESlois` 无建仓/fork 权限。需用户提供可建仓的 PAT 或指定目标仓库后推送。
