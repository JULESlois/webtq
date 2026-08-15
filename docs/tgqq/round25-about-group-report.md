# TGQQ Round 25: 设置-关于QQ 页 + 联系人-分组 校准 + codebuddy 条目清零

日期：2026-08-15
基准：`f7d9f42`（Round 24 设置页）

## 本轮目标与结论

- 完成 `qq9-mobile2/` 盘点（codebuddy 全量 14 张 → `/tmp/cb_inventory2.md`），确定 Round 25 实现 002（设置-关于QQ）并校准 010（联系人-分组）。
- 新增完整「关于QQ」页面（React + fixture，浅色/暗色全套），设置页挂「关于QQ」入口行。
- 分组视图对齐参考：特别关心 0/0 折叠、我的好友 3/4（4 名成员、3 人在线）。
- codebuddy Round 24 审查 3 项：分割线缩进 34→50px（此前偏离审查要求）、SVIP 药丸、设置页隐藏底栏 —— 全部复核完成。
- codebuddy Round 25 终审 10 项：7 PASS + 3 FAIL，FAIL 项全部修复并复核。

## 新增：设置-关于QQ（002）

参考图实测（PIL 像素采样，纠正 codebuddy 误读处）：
- 整页背景 `#f0f4ff`（(240,244,255)）；hero 渐变：顶部粉 `#f3cdd9` → 中段暖粉 `#f1e4dc` → 底部淡蓝 `#eaf1ff`，垂直为主。
- hero 内只有居中「QQ9」三字标（空心渐变字：青 `#7ed7ff` → 蓝 `#4a9bff` → 紫 `#8b7bff`，字形 y≈230-253 逻辑），企鹅为极淡白色剪影（PIL 不可见，按 inventory 补半透明玻璃企鹅）。
- 卡片：左右边距 13，圆角 12，6 行（当前版本 V 9.0.0.14110 / 版本更新 已是最新版本 / 功能介绍 / 官网 / 帮助 / 反馈），行高 45，左小图标 14-16px，行 1-2 无 chevron（参考图实测），行 3-6 有 chevron。
- 底部 5 行居中灰字（基于 QNT徽标 QQNT 技术架构 / 服务协议|隐私政策 蓝链 / 客服热线 / Copyright / ICP 备案号 ›），锚定页面底部。

实现：
- `src/tgqq/pages/Settings/About.tsx` + `About.module.scss`：渐变 hero（返回箭头/企鹅/QQ9 字标）、卡片 6 行、底部 5 行；暗色渐变 `#35264a→#1e2a48`、卡片 `#2b2b2b`。
- `src/tgqq/pages/Settings/index.tsx`：内部 screen 状态（general/accessibility/about），设置页底部新增「关于QQ」入口行（info 图标 + chevron），点击进入关于页，返回回到设置。
- fixture：`tab.html` 新增 `SETTINGS_ABOUT` 模板 + `sub=about` 路由 + 设置页关于QQ行 + 6 个图标/企鹅/页脚同步；`fixture.css` 新增 `.tq-about-*` 全套（含暗色）。
- `shoot.sh`：新增 8 张截图（about-tab/mobile/long + 暗色 + contacts-group + 暗色）。

## 校准：联系人-分组（010）

- 我的好友分组：6 人 3/6 → 独立 `groupFriends` 4 人 3/4（与参考一致；好友 Tab 仍显示全部 6 人）。
- 特别关心默认折叠（0/0 空组），其余分组展开；fixture 同步。
- 搜索占位「搜索联系人」→「搜索」（`src/lang.ts`、`langPack.strings`、fixture 同步）。

## codebuddy 终审（`/tmp/cb_r25_review.md`）与修复

10 项核对：A1/A5/B6-B9/C10 PASS；A2（企鹅风格）、A3（当前版本行多余 chevron）、A4（footer 多余文字+分隔符）FAIL —— 全部修复：

1. 企鹅改为半透明白色剪影（移除眼睛/喙/围巾卡通细节，保留白色渐变+腹部高光+白点眼睛），React 与 fixture 同步。
2. 「当前版本」「版本更新」行移除 chevron（仅无 value 的导航行显示）。
3. footer 第一行去掉「，提供稳定高效的服务」；分隔符 `｜`→`|`；QNT 徽标保留金色六边形。
4. 搜索占位符改「搜索」。
5. 设置行分割线缩进 34→50px（Round 24 审查要求，PIL 复核：分割线从卡片左缘 50px 起、右缘 16px 止）。

## 验证

- `npx vite build` 通过（About.module.scss 哈希稳定，fixture 引用的 `_root_10x2p_1`/`_root_rma6i_1` 未变）。
- `shoot.sh` 61 张全出，无 FAIL；既有截图与上一版最大像素差 1/255（仅抗锯齿噪声，无实质变化）。
- PIL 复核：关于页卡片 6 行、行 1-2 无箭头行 3-6 有、页脚 5 行含蓝链、暗色渐变/卡片/文字正确；设置页关于QQ入口行在底部；分组页 3/4 计数与 4 行成员正确。
- 新增截图：`shots/about-{tab,mobile,long}[-dark].png`、`shots/contacts-group[-mobile][-dark].png`。

## 遗留

- 推送仍受阻：origin（morethanwords/tweb）无写权限 403。需用户提供可建仓的 PAT 或目标仓库。
- 下一轮建议：按用户方向进入聊天页改造；或实现 007/008/009（群成员去重/管理群）。
