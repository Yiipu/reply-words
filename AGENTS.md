# reply-words — 词库

纯 GitHub 托管：静态前端 + Issue Form 投稿 + GitHub Discussions 投票，无后端服务。

## 运行与部署

- 本地开发：直接用浏览器打开 `index.html`，或 `python3 -m http.server <port>`
- 无构建步骤、无依赖（纯静态 HTML）
- 部署：`deploy.yml`（仅 `index.html` 变更时触发 + `workflow_dispatch` 手动）→ GitHub Pages（Source 设为 "GitHub Actions"）→ https://yiipu.github.io/reply-words/

## 架构

单页应用，全部内联在 `index.html`（CSS + JS 均不分离）。数据分三层：

| 层 | 存储位置 | 读写方式 |
|---|---|---|
| 默认词库 | `index.html` 内 JS 常量 `DEFAULT_*` | 硬编码，只读 |
| 个人词库 | `localStorage`（key: `reply-words-data-v2`） | 前端编辑弹窗读写 |
| 社区词库 | Gist `community.json` | GitHub Actions 写入，前端 `fetch()` 读取 |

## 概念

- **模式**（mode）：`ok`（👌 浅色主题） / `no`（😈 暗色主题）
- **类别**（category）：`leader`（对领导，深绿按钮） / `colleague`（对同事，浅绿按钮）
- 词条选取逻辑：避开最近 5 条历史，随机抽取；社区词以可配置概率（默认 20%）混入
- 社区词展示时懒加载 giscus 组件，按 Discussion `number` 映射到对应投票

## 数据流（社区词生命周期）

1. **投稿**：用户 → Issue Form（`submit-word.yml`）→ `submit.yml` 校验（长度≤50/类别/模式/查重）→ GraphQL 创建 Discussion → Gist 乐观锁写入 `community.json`（失败重试 3 次）
2. **展示**：前端 `fetch(community.json)`（成功写入 `localStorage` 缓存 5min TTL，失败时降级）→ 按 `communityMixRate` 概率混入 → 懒加载 giscus 投票
3. **衰减**：`fade-out.yml`（每日 UTC 18:00）→ 批量 GraphQL 拉取 Discussion 👍/👎 → `total ≥ 10 && 👎 > 👍 × 1.5` 则移除并关闭 Discussion → Gist 乐观锁写回

## 硬编码常量（改仓库名/账号时需同步）

分布在 `index.html`、`.github/workflows/*.yml` 中：
- repo: `Yiipu/reply-words`
- repositoryId: `R_kgDOTg3sHQ`
- Discussion category: `Announcements` / `DIC_kwDOTg3sHc4DBxyQ`
- Gist ID: `fb0670351105898b40e2d23a0dae3cd7`
