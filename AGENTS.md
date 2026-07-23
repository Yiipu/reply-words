# reply-words — 词库

纯 GitHub 托管：静态前端 + Issue Form 投稿 + GitHub Discussions 投票，无后端服务。

## 运行

本地直接用浏览器打开 `index.html`，或起个静态服务器（如 `python3 -m http.server`）。无构建步骤、无依赖。

## 部署

GitHub Pages（`main` 分支根目录）。访问地址：https://yiipu.github.io/reply-words/

## 架构

- **`index.html`** — 单页前端，全部内联（无构建步骤）
- **`community.json`** — 社区词库，唯一数据源；由 Actions 读写、commit 提交
- **`.github/ISSUE_TEMPLATE/submit-word.yml`** — 投稿表单（text / category / mode）
- **`.github/workflows/submit.yml`** — 监听 `word-submission` label 的 issue，硬校验 → 创建 Discussion → 写入 `community.json` → 关闭 issue
- **`.github/workflows/fade-out.yml`** — 每日定时，读取各 Discussion 的 👍/👎 reaction 计数，衰减比例 >1.5 的词从 `community.json` 移除

## 数据流

1. **投稿**：用户点「向社区投稿」→ 跳转 GitHub Issue Form → 提交 issue → `submit.yml` 校验通过后为该词创建一条 Discussion（分类 `Announcements`），把 `{text, discussion: <number>}` 写入 `community.json` 并 commit
2. **展示**：前端 `fetch('community.json')`（同目录静态文件），社区词以 20% 概率混合展示
3. **投票**：展示社区词时懒加载 giscus，`data-mapping="number"` `data-term="<discussion>"` 精确指向对应 Discussion，用户登陆 GitHub 后点 reaction（👍/👎）
4. **衰减**：`fade-out.yml` 每日读取 reaction 计数，套用与旧版 `run_fade_out()` 相同的 `差评 > 好评×1.5` 逻辑，移除词条

## 概念

- 两个**模式**: `ok`(👌) / `no`(😈)
- 两个**类别**: `leader`(对领导) / `colleague`(对同事)
- 前端个人词库存储在 `localStorage`（key: `reply-words-data-v2`），可通过编辑弹窗修改
- 默认词库硬编码在 `index.html` 的 JS 数组中
- 词条 ID = GitHub Discussion 的 `number`（创建后永不变），不再有自增数据库 ID

## 常量（改仓库名/账号时需同步）

`index.html`、`.github/workflows/*.yml` 里都硬编码了：
- repo: `Yiipu/reply-words`
- repositoryId: `R_kgDOTg3sHQ`
- Discussion category: `Announcements` / `DIC_kwDOTg3sHc4DBxyQ`

## 未完成

- **`paw_check`** 语义审核（原 stub）尚未搬进 `submit.yml`，当前只有硬校验（长度/类别/模式/查重），待接 programasweights.com PAW
- giscus 目前只做了基础配置（reactions-enabled + 明暗主题跟随），细节样式待后续调整

## 风格

- commit message 用中文、加前缀
