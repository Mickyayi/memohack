# 🛠️ MemoHack 安装与部署指南

本指南旨在帮助您在几秒钟内为任何项目开启“数字记忆”能力。

## 1. 环境激活 (Environment Activation)

MemoHack 采用 **仓库中心化 (Repo-based)** 安装模式。这意味着您只需要克隆一次仓库，就可以为无限个项目提供记忆支持。

### 一键安装指令
在您的 **目标项目根目录** 下运行：
```bash
python3 /path/to/MemoHack/init_memohack.py
```
*(请将 `/path/to/MemoHack` 替换为您本地克隆该仓库的真实路径)*

## 2. 自动化安装内容 (What's installed?)

运行上述脚本后，MemoHack 将自动完成以下部署：

- **全局指令 (`~/.gemini/GEMINI.md`)**: 植入 AI 固化协议，确保 AI 保持“引导优先”的习惯。
- **项目引导 (`00_MEMOHACK_BOOT.md`)**: 为 AI 提供项目的快速索引。
- **状态快照 (`CURRENT_STATE.md`)**: 记录实时的开发进度、Checkpoint 和 Redline。
- **技术手册 (`manual.md`)**: 存放已验证的代码模式与环境配置。
- **固化引擎 (`skills/memohack/`)**: 部署 `vibe_sync.py`，赋予 AI 原子化写入记忆的能力。

## 3. 进行版本更新 (Version Syncing)

如果您更新了 MemoHack 仓库中的 `vibe_sync.py` 或规则：
只需要在项目目录中再次运行安装脚本，并附加 `--force` 参数：
```bash
python3 /path/to/MemoHack/init_memohack.py --force
```

---
*Powered by MemoHack Memory Engine v2.0*
