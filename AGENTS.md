# reply-words — 词库

## 运行

```sh
make install   # 创建 venv + pip install flask
make run       # 启动 http://0.0.0.0:8799
```

## 架构

- **`backend/app.py`** — Flask 单文件服务，端口 8799，提供 API 和静态文件
- **`backend/db.py`** — SQLite 封装，`community.db` 在项目根目录，启动时自动建表
- **`static/index.html`** — 单页前端，全部内联（无构建步骤）
- **`backend/community.json`** — 从 DB 导出的社区词缓存，被 `.gitignore`，由 `db.py:rebuild_community_json()` 自动生成

## API

| 路由 | 说明 |
|------|------|
| `POST /api/submit` | 投稿 `{text, category, mode}`, 硬校验 → PAW(stub) → 入库 |
| `GET /api/community-words` | 社区词列表（ETag 缓存）, 返回 `{id, text}` 对象 |
| `POST /api/feedback` | 评价 `{word_id, vote}` (1=有用, -1=没用) |
| `POST /api/fade-out` | 执行衰减：差评 > 好评×1.5 的词设为 inactive |

## 概念

- 两个**模式**: `ok`(👌) / `no`(😈)
- 两个**类别**: `leader`(对领导) / `colleague`(对同事)
- 前端词库存储在 `localStorage`（key: `reply-words-data-v2`），可通过编辑弹窗修改
- 默认词库硬编码在 `index.html:528-587` 的 JS 数组中
- 社区词以 20% 概率混合展示，带有 👍/👎 评价按钮

## 未完成

- **`paw_check()`** (`app.py:48`) 是 stub 始终返回 True，待接 programasweights.com PAW
- **投稿 UI** — `POST /api/submit` 后端已就绪但前端无投稿入口

## 风格

- commit message 用中文、加前缀
