# MemoHack 核心驱动规则 (MEMOHACK_CORE_RULES)

本规则是 MemoHack 系统的“行为芯片”，旨在确保 AI 代理始终遵循“显式状态管理”与“知识固化”工作流。

---

## 1. 基础行为准则 (The Law)
- **优先读取**：开启新会话或新任务时，必须优先读取 `00_MEMOHACK_BOOT.md` 以加载项目地图。
- **验证后固化**：仅记录已通过 `run_command` 或 `view_file` 物理验证的“事实”。
- **禁止猜测**：禁止将未经验证的猜测写入 `CURRENT_STATE` 或 `manual`。

---

## 2. 自动化固化流 (The Solidification Flow)

### 自动模式 (AUTO MODE)
- **触发**：当检测到 `manual.md` 中的 `MEMORY_MODE: AUTO` 时激活。
- **动作**：每当一个任务完成（如：修复了一个报错或实现了一个接口），AI 必须静默执行“微总结”，并追加到 `CURRENT_STATE.md`。
- **反馈**：无需征得用户许可，但需在对话结尾简述已更新内容。

### 进阶模式 (ADVANCED MODE)
- **触发**：当检测到 `manual.md` 中的 `MEMORY_MODE: ADVANCED` 时激活。
- **动作**：AI 执行“知识蒸馏”后，必须生成一个 **Artifact (Memory Patch)** 供用户批注。
- **反馈**：仅在用户在 Artifact 上确认/批注后，方可写入物理文件。

---

## 3. 记忆分类规范 (The 3-S Tags)
- **#MH-AUTH**: 鉴权逻辑、Token 管理
- **#MH-DB**: 数据库结构、SQL 范本
- **#MH-DEBUG**: 故障排除、日志搜索命令
- **#MH-UI**: 界面布局、CSS 设计系统

---

## 4. 特殊指令 (Special Ops)
- 当用户询问“现在进度到哪了？”，AI 必须同时引用 `CURRENT_STATE.md` 的内容进行回答。
- 当发生重复报错时，AI 必须查阅 `manual.md` 中的 `Redline` 区域以防止陷入循环。
