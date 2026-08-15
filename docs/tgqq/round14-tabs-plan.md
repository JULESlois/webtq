# Round 14 计划 — 四 Tab 页终审 + fixture↔真机页面对齐

- 日期：2026-08-15
- 前置：Round 13 聊天页改造（round13-chatpage-report.md）
- 目标：消息/频道/联系人/动态四 Tab 页与 QQ9 对照终审，并修复 fixture 与真机页面（src/tgqq/pages/*）的样式漂移

## 范围

### 1. fixture ↔ 真机页面对齐（fixture 必须以 src/tgqq/pages 为唯一视觉源）
- Contacts：分组标题 15px/600 → 13px/500（Contacts.module.scss §69）；行 padding 10px → 9px；字母索引条对齐（9px、right 2px、top 50%、#9a9a9a）。
- Dynamics：动态卡头像 44px → 42px（Dynamics.module.scss .cardAvatar）。
- Channels：已与 Channels.module.scss 一致（15px/600、118px 卡），无需改。
- 消息页：TqChatList.scss 驱动，Row 74px/头像 52px/选中 tint+左侧蓝条已验证存在。

### 2. codebuddy round14 评审（重点：布局模型说明）
- 平板/宽屏 = 左侧 360px 手机式主页（四 Tab 页面渲染在左列内）+ 右侧聊天窗；
  未选中聊天时右侧空白是**设计**，不是缺陷。
- 验证项：四 Tab 页特征（个人行/搜索框/列表/卡片/徽标/绿点/索引条/底部导航选中蓝）、
  手机消息页、平板回归。

## 验证
- fixture 对齐后 build/shoot → puppeteer（标题字号、头像 42/44、索引条几何、徽标/绿点存在）→
  codebuddy 终审 → 报告 round14-tabs-report.md。

## 实施进度（2026-08-15 03:5x）
- [x] Contacts fixture 对齐：分组标题 13px/500 灰、行 padding 9px（行高 62px）、
      索引条 9px/right 2px/top 50%/#9a9a9a
- [x] Dynamics fixture 对齐：卡头像 42px（`.tq-post-avatar`）
- [x] Channels / 消息页核对无需改（与 module/TqChatList.scss 一致）
- [x] build/shoot → puppeteer 自验（标题字号、行高、索引条几何、徽标/绿点、选中 tint+蓝条）
- [x] codebuddy round14 首轮：布局模型误读致全误报（已复核并记录）
- [x] codebuddy round14b 终审（prompt 注明左 360px 模型）：四 Tab PASS，
      3 项缺陷声明全部误报（详见报告 §3）
- [x] 报告 round14-tabs-report.md（含终审误报复核表）
- [ ] 下一步：聊天页改造续（用户指定，Round 15 范围）
