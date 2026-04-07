# 🧠 MemoHack: AI 记忆引擎 v2.0

> **告别 AI 上下文碎片感，让 Vibe Coding 拥有持久“肌肉记忆”。**

---

## 🌟 核心理念 (Why MemoHack?)
Antigravity 是一款强大的 IDE，但 AI 在不同对话间容易产生记忆丢失。MemoHack 通过“物理状态化”与“智能蒸馏”技术，将 AI 的成功路径与排障经验固化在项目中，实现知识的零损耗传递。

## 🚀 仓库级一键启动 (Repo-based Sync)

1. **下载或克隆** 本仓库。
2. 在您的 **新项目根目录** 下，调用本仓库中的脚本即可完成同步：
```bash
python3 /path/to/MemoHack/init_memohack.py
```
**这一条指令将自动完成：**
1. **全局激活**：植入或更新您的系统规则。
2. **智能扫描**：分析当前项目的技术画像。
3. **记忆注水**：生成具备业务背景的初始化 MD 文件集。
- **智能扫描**：自动识别 Python/Node/Go 技术栈。
- **模板填充**：自动生成带项目画像的 `manual.md`, `CURRENT_STATE.md` 和 `00_BOOT`。

## 🛠️ 日常交互流程 (The Workflow)

### 1- 极速对齐 (Linguistic Pointers)
AI 每次开启任务，都会优先阅读 `00_MEMOHACK_BOOT.md`，瞬间从项目海量文件中找回业务逻辑主线。

### 2- 成功即固化 (Distillation)
通过 `vibe_sync.py` 脚本，将成功的 Terminal 指令与修复代码一键生成补丁。
```bash
python3 skills/memohack/scripts/vibe_sync.py --type CHECKPOINT --content "修复高并发超卖逻辑"
```

## 🏷️ 知识管理规范 (MH-Tags)
- `#MH-TECH`: 核心架构沉淀
- `#MH-DEBUG`: 踩坑与避障经验
- `#MH-BOOT`: 初始化引导逻辑

---
*Inspired by the Vibe Coding community. Made for Antigravity IDE.*
