# TGQQ tweb Upstream Baseline

Repository:
https://github.com/morethanwords/tweb

Branch:
master

Commit:
e3730e10073c3fc02e1360e3513b70b176d6afec

Working tree before TGQQ changes:
clean

Node:
v24.14.1（Termux android-arm64 构建，`process.platform === 'android'`）

pnpm:
11.16.0（经 corepack 激活；`@pnpm/exe` 无 android-arm64 二进制，无法直接 npm 全局安装）

Date:
2026-08-12

Notes:
- 仓库 `AGENTS.md` 要求 shell 命令前缀 `rtk`，但当前环境未安装 `rtk`，本轮未使用（记录待补）。
- 仓库 `package.json` 要求 Node `^22.18.0 || >=24.11.0`、pnpm `11.16.0`，均满足。
- 仓库实际工具链与 AGENTS.md 描述有偏差：AGENTS.md 写 TypeScript 5.7 / Vite 5，实际 lockfile 为 typescript 7.0.2（原生 Go 编译器）与 vite 8.2.1（rolldown 驱动）。
- TypeScript 7 原生编译器没有 android-arm64 平台包，仓库自带 `pnpm typecheck` 在本机不可运行；本轮使用 `npx typescript@5.9 tsc --noEmit` 验证（不修改仓库依赖）。
- oxlint（android-arm64 原生包）启动即 panic（SIGABRT，oxc_allocator 线程池），`pnpm lint` 在本机不可运行。
- 上述均为环境/平台问题，非 TGQQ 修改引入。
