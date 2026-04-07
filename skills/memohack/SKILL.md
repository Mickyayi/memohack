# 🧠 MemoHack 固化引擎 Skill

## 1. 指令集 (Command Prompting)
本 Skill 旨在通过 `vibe_sync.py` 实现对话内容的物理固化。当 AI 完成任务或获得新知识时，必须调用此指令。

- **Checkpoint 固化**：执行 `python3 vibe_sync.py --type CHECKPOINT --content "你的成功路径摘要"`。
- **Redline (禁区) 记录**：执行 `python3 vibe_sync.py --type REDLINE --content "避坑指南"`。
- **技术手册更新**：执行 `python3 vibe_sync.py --type MANUAL --content "标题|具体内容"`。

## 2. 交互协议 (Interaction Protocol)

### [ADVANCED 模式]
1. AI 生成提议。
2. 调用脚本（无 `--confirm` 标志）生成 `/tmp/patch_preview.md`。
3. 将 Patch 内容以 Artifact 形式展示给用户。
4. 在用户回复 `Confirm` 后，再次调用脚本并附加 `--confirm` 参数。

### [AUTO 模式]
1. AI 将精简摘要传递给脚本。
2. 脚本静默执行原子写入。

## 3. 分类标准 (3-S Distillation)
- **Success (通过验证)**: 只有通过 `Exit 0` 或逻辑验证的路径才能进入 Checkpoint。
- **Standard (标准化)**: 使用绝对路径，不带任何含糊词。
- **Specific (特定参数)**: 记录具体配置及命令。

---
*Created by MemoHack Memory Engine v2.0*
