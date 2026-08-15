# Round 16 — 暗色四 Tab + 动态真机照片 + 页面交互（报告）

- 日期：2026-08-15
- 前置：Round 15 两行 composer（round15-composer-plan.md）；Round 14 四 Tab 浅色 PASS
- 循环：token 修复 → 四 Tab 暗色审计 → 动态照片接入 → 交互补全 → build/shoot → puppeteer 自验 → codebuddy 终审 → 本报告

## 1. 本轮完成项

### 1.1 暗色 token bug 修复（src/tgqq/design/dark.scss:15-16）
- 原 `--tq-text-quaternary:` 缺值、`#5a5a5a` 被注释吞掉 → 暗色四 Tab 部分禁用文字/图标回退到错误颜色。
- 修复后：light `--tq-text-quaternary:#cccccc`、`--tq-icon-primary:#1f1f1f`；dark `--tq-text-quaternary:#5a5a5a`、`--tq-icon-primary:#d6d6d6`。

### 1.2 四 Tab 暗色全覆盖审计
- Channels / Contacts / Dynamics 三页 + PageContainer 底色/文字全部 token 化（`--tq-surface-*` / `--tq-text-*`）。
- 硬编码 `#fff` 仅保留渐变头像/徽标文字（设计内）。
- 链路：`src/tgqq/index.ts` 引入 `dark.scss`，`html.night .is-tgqq` 门控生效。

### 1.3 动态页真机照片（src/tgqq/assets/photos/）
- 12 张真机照片 `docs/tgqq/fixtures/imgs/photo01..12.jpg` → `src/tgqq/assets/photos/`，Vite import + `<img>`。
- `.imgCell`：`object-fit:cover` + `overflow:hidden`，3 图/4 图网格、1 图宽幅（16:9）。
- Post 数据 `imgStart`：沈亦舟=3、林晚晴=0、陈默=4、产品讨论组=0，与 fixture 映射一致。
- 打包产物 `dist/photo01-BdMHM84-.jpg` 等 12 张 ✅。

### 1.4 暗色 fixture 支持
- 8 个 fixture 头部插 `night` class 注入脚本（`?dark=1` 生效）。
- `shoot.sh` 新增 10 个 `*-dark` 截图规格。
- `fixture.css` 追加 `html.night` 覆盖块（profile、输入条、composer plate、nav、tq-page、search、card、list、row、post、follow、online-dot 等，全部 token + 回退值）。

### 1.5 真机交互补全（此前三页按钮全静态）
- Channels：`createSignal` 关注切换，`ChannelRow` + 新 `RecommendCard` 复用，`.followBtnActive`（蓝底白字）。
- Dynamics：抽 `PostCard`，点赞切换 `.actionBtnActive`（蓝）+ 计数 +1。
- fixture 同步交互行为（`.tq-follow` 点击切换「+ 关注/已关注」、`.tq-post-actions button` 点赞切换），供后续交互截图/验证。

## 2. 验证矩阵（puppeteer computed-style + magick/Pillow 像素）

### 2.1 交互（fixture 与真机同构）
| 检测项 | 期望 | 实测 | 状态 |
|---|---|---|---|
| 平板频道页布局 | shell 在左 360px 列 | shell @(0,0) 360×700；右窗 540×700 | ✅ |
| 关注初始态 | 「+ 关注」蓝描边透明底 | rgb(18,150,219)/transparent | ✅ |
| 关注点击 | 「已关注」蓝底白字 | rgb(18,150,219) 底 + #fff 字，可回切 | ✅ |
| 点赞初始态 | 灰计数 | rgb(138,138,138)「35」 | ✅ |
| 点赞点击 | 蓝 + 计数+1 | rgb(18,150,219)「36」+ active class | ✅ |
| 手机动态页 | shell 全宽 390 | 390×844 @(0,0) | ✅ |

### 2.2 暗色 token（computed-style 精确值）
| 检测项 | 期望 | 实测 | 状态 |
|---|---|---|---|
| 三 Tab 页面底 | #1a1a1a | rgb(26,26,26) | ✅ |
| 卡片/列表 | #2b2b2b | rgb(43,43,43) | ✅ |
| 搜索条 | #373737 | rgb(55,55,55) | ✅ |
| 主文字 | #e5e5e5 | rgb(229,229,229) | ✅ |
| 次文字 | #b3b3b3 | rgb(179,179,179) | ✅ |
| 导航选中 | #4eb0f5 | rgb(78,176,245) | ✅ |
| 关注钮 active | #4eb0f5 底白字 | rgb(78,176,245)/#fff | ✅ |
| 聊天页气泡区 | #191919 | rgb(25,25,25) | ✅ |
| 自己气泡 | #3e6fa3 | rgb(62,111,163) | ✅ |
| 对方气泡 | #373737 | rgb(55,55,55) | ✅ |
| 顶栏 | #2b2b2b | rgb(43,43,43) | ✅ |
| 浅色版 | 无暗色渗入 | 全浅 token | ✅ |

### 2.3 照片真实性（Pillow 局部方差）
- 照片单元 std=6~9（真实影像纹理）；产品讨论组帖 std=0（0 图，符合）。
- 3 图（沈亦舟）/ 1 图宽幅（林晚晴）/ 4 图网格（陈默）结构全部成立。
- 手机/平板暗色文字可读。

## 3. codebuddy 终审结论（8 张图全 PASS）

- 逐项 PASS，无严重缺陷；布局模型（左 360px 主页 + 右聊天窗）严格遵守；
  暗色 token 在四 Tab 与手机/平板/聊天窗四处均精确命中（JPEG 偏差 ≤3）。
- codebuddy 提出 2 个「轻微项」，复核后均为**误读，非缺陷**：
  1. 「首卡红色角标过大」→ 实为首卡品牌渐变封面（#ff7a59→#ff3d68，腾讯新闻），
     PNG 采样 (255,109,92)/(255,77,100) 确认为封面渐变，非角标。
  2. 「陈默帖点赞按钮红色」→ 红色像素位于 4 图网格照片内容区（photo05/08 橙红渐变），
     点赞 footer 实际为灰色 (138,138,138)（第 2.1 节点击前采样）。

## 4. 状态

- **第 16 轮验收通过，可进入聊天页改造（Round 17）。**
- 未提交；改动均在 `src/tgqq/` 私有目录 + `docs/tgqq/fixtures/`（本轮无新增 upstream patch）。
