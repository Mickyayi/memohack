# 🧠 MemoHack: 专家级项目初始化 (memohack-expert-scan)

## 🎯 技能概述 (Skill Overview)
本技能旨在将一个“草率”的初始扫描提升为“专家级”的项目画像。当你（AI）发现 `manual.md` 处于 `DRAFT` 状态或包含 `[PENDING AI SCAN]` 标识时，应主动调用此技能。

---

## 🛠️ 深度审计流程 (6-Layer Audit SOP)

请严格按照以下层级执行 `IDE` 工具调用，并将分析结果整合：

### 1️⃣ 这是什么 (The Vision)
- **行为**：使用 `read_file` 读取根目录的 `README.md`。
- **目标**：提取前 10-20 行，总结项目的核心目标、愿景和主要功能。

### 2️⃣ 用了什么 (The Stack)
- **行为**：使用 `list_dir` 搜索根目录及第二层子目录（如 `crmeb/`, `app/`, `backend/`）。
- **目标**：找到并读取 `package.json`, `composer.json`, `requirements.txt`, `go.mod`, `Cargo.toml`。
- **深度分析**：
    - 不只是列出语言，而是识别具体的框架（如：Node.js -> **NestJS**, PHP -> **Laravel/ThinkPHP**, JS -> **Uni-app**）。
    - 记录核心 ORM 或状态管理库。

### 3️⃣ 基础设施 (Infrastructure)
- **行为**：专项猎取配置文件。
    - 搜索 `docker-compose.yml`, `Dockerfile`。
    - 搜索 `.env.example`, `.env.sample`。
    - 搜索 `nginx.conf`, `Caddyfile`。
- **目标**：提取数据库类型（MySQL/Redis/Mongo）、端口映射关系、以及开发时必须配置的环境变量清单。

### 4️⃣ 代码组织 (Structure)
- **行为**：使用 `list_dir` 生成深度为 2 的分层目录树名。
- **目标**：区分“逻辑模块”。例如：`crmeb/` 是核心后台，`template/` 是前端模板。

### 5️⃣ 怎么跑 (Commands)
- **行为**：解析 `package.json` 的 `scripts` 或 `Makefile`。
- **目标**：记录 `npm run dev`, `php think run`, `make build` 等核心启动命令。

### 6️⃣ 最近在忙什么 (Git Context)
- **行为**：运行 `run_command` 指令：`git log --oneline -5`。
- **目标**：从最新的 5 次 Commit 中捕捉当前开发的重点方向和紧急热点。

---

## 📥 知识入库 (Hardening)

分析完成后，请调用以下命令将成果永久固化：

```bash
python3 skills/memohack/scripts/vibe_sync.py --type MANUAL --content "你的专家审计报告全文" --confirm
```

> [!IMPORTANT]
> **补丁预览原则**：在写入 `manual.md` 前，必须通过 Artifact 展示你总结的 1-6 层画像补丁，并等待用户回复 'Confirm'。

---
*MemoHack Skill v3.0 | 专家模式已就绪*
