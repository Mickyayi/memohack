# 📖 MemoHack 专家手册 (manual.md)
> **项目模式**: `MEMORY_MODE: ADVANCED` (默认为进阶模式，支持补丁预览)

---

## 🏗️ 项目架构全景 (System Map)
- **Backend**: Python-based sync scripts.
- **Rules Engine**: Antigravity Workspace Rules (.agents/rules).
- **Memory Storage**: Human-readable Markdown files.

---

## 📚 技术资产沉淀 (Knowledge Base)

### #MH-RULES: 规则加载逻辑
- 经验：Antigravity 会自动合并 `.agents/rules` 下的所有 Markdown 文件作为 Agent 的系统指令的一部分。
- 逻辑：通过在规则中定义 `AUTO` 模式，可以实现无感背景同步。

---

## 🩺 诊断与工具箱 (Diagnostic Toolbox)
- 权限检查：`ls -ld .agents/rules`
- 规则冲突排查：查看 IDE 输出面板中的 Agent 指令流。

- **2026-04-06 11:26** [#MH-DEBUG]: 高并发扣减模式|所有针对库存 stock 的原子操作必须由互斥锁 (Lock) 保护。已通过 50 线程压力测试验证成功。 [Status: OK]
