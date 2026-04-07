import os
import sys
import argparse
import shutil
import re
from datetime import datetime

# ==========================================
# MemoHack 核心模板库 (The Atomic Templates)
# ==========================================

BOOT_TEMPLATE = """# 🚀 MemoHack 项目引导 (Bootloader)
> **状态：已激活** | [项目地址]({{PROJECT_PATH}})

---

## 📍 核心索引 (Linguistic Pointers)
- **实时执行状态** -> [CURRENT_STATE.md](file:///{{PROJECT_PATH}}/CURRENT_STATE.md)
- **技术资产沉淀** -> [manual.md](file:///{{PROJECT_PATH}}/manual.md)

---

## 🏷️ 知识 Tag 索引 (MH-Tags)
- `#MH-BOOT`: 项目初始化与引导逻辑
- `#MH-TECH`: 核心技术栈与架构模式
- `#MH-DEBUG`: 故障排查与 Redline 记录
"""

STATE_TEMPLATE = """# 🕒 MemoHack 实时快照 (CURRENT_STATE)
> 更新时间：{{NOW}}

---

## 🎯 当前目标 (Current Goal)
- [ ] 完成项目扫描与初始化

---

## 📍 验证路径点 (Checkpoints)
- **{{NOW}}** [#MH-BOOT]: 通过 `init_memohack.py` 完成仓库级一键安装 [Status: OK]

---

## 🚨 禁区 (Redlines)
- **禁止项**: 严禁在没有物理验证的情况下记录 Checkpoint。
"""

MANUAL_TEMPLATE = """# 📚 MemoHack 技术手册 (manual.md)
> **MEMORY_MODE**: ADVANCED

---

## 🛠️ 环境配置 (Environment)
- **技术栈**: {{TECH_STACK}}
- **主入口**: {{MAIN_FILES}}

---

## 📚 技术沉淀 (Knowledge Base)
- (此处存放已验证的最佳实践)

---

## 📋 业务逻辑地图 (Business Logic)
- (描述核心业务流程)
"""

GLOBAL_RULES = """
# MEMOHACK 记忆引擎指令 (MEMOHACK_V2)

## 1. 显式状态管理规范
- **引导优先**：开启新会话或新任务时，必须通过 `list_dir` 寻找并读取 `00_MEMOHACK_BOOT.md`。
- **验证后记录**：仅在终端操作成功 (Exit 0) 或代码逻辑验证无误后，方可更新 `CURRENT_STATE.md`。

## 2. 人机协同工作流 (ADVANCED 模式)
- **补丁预览**：在执行任何针对 `manual.md` 或 `CURRENT_STATE.md` 的写入操作前，必须通过 Artifact 生成预览补丁。
"""

class MemohackInstaller:
    def __init__(self, target_dir):
        self.target_dir = os.path.abspath(target_dir)
        # 核心：定位仓库自身的根目录
        self.repo_root = os.path.dirname(os.path.abspath(__file__))
        self.tech_stack = "Unknown"
        self.main_files = []

    def scan_project(self):
        """扫描目标项目画像"""
        print("[SCAN] 正在分析目标项目结构...")
        files = [f for f in os.listdir(self.target_dir) if os.path.isfile(os.path.join(self.target_dir, f))]
        
        stacks = []
        if 'package.json' in files: stacks.append("Node.js")
        if any(f.endswith('.py') for f in files): stacks.append("Python")
        if 'go.mod' in files: stacks.append("Go")
        self.tech_stack = " / ".join(stacks) if stacks else "Generic"

        candidates = [f for f in files if f.split('.')[-1] in ['py', 'js', 'go', 'ts']]
        for f in candidates:
            if any(p in f for p in ['main', 'app', 'index', 'start', 'server']):
                self.main_files.append(f)
        if not self.main_files and candidates:
            self.main_files = candidates[:3]

    def sync_skills(self, force=False):
        """核心重构：从仓库物理复制 Skills 文件夹"""
        print("[SKILL] 正在从仓库同步 Skills 模块...")
        source_skills = os.path.join(self.repo_root, "skills")
        target_skills = os.path.join(self.target_dir, "skills")
        
        if not os.path.exists(source_skills):
            print(f"[RE-ROUTE] 仓库目录下未发现 skills 文件夹: {source_skills}")
            return False

        # 如果目标目录已存在
        if os.path.exists(target_skills):
            if not force:
                print(f"[CONFLICT] 目标项目已存在 skills 文件夹。请使用 --force 参数强制覆盖。")
                return False
            else:
                print("[FORCE] 正在覆盖旧的 Skills 模块...")
                shutil.rmtree(target_skills)

        # 全量物理复制 (保持目录结构不变)
        try:
            shutil.copytree(source_skills, target_skills)
            print(f"[SUCCESS] Skills 全量同步成功: {target_skills}")
            return True
        except Exception as e:
            print(f"[ERROR] 同步失败: {str(e)}")
            return False

    def setup_workspace_files(self, scan=False):
        """创建基础记忆文件结构"""
        print(f"[INIT] 正在初始化基础记忆文件: {self.target_dir}")
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        mapping = {
            "{{PROJECT_PATH}}": self.target_dir,
            "{{NOW}}": now,
            "{{TECH_STACK}}": self.tech_stack if scan else "Generic",
            "{{MAIN_FILES}}": ", ".join(self.main_files) if scan else "Manual detection"
        }

        # 规则文件注入 (Workspace Level)
        rules_dir = os.path.join(self.target_dir, ".agents/rules")
        if not os.path.exists(rules_dir):
            os.makedirs(rules_dir)
        with open(os.path.join(rules_dir, "memohack.md"), 'w', encoding='utf-8') as f:
            f.write(GLOBAL_RULES)

        files_to_create = {
            "00_MEMOHACK_BOOT.md": BOOT_TEMPLATE,
            "CURRENT_STATE.md": STATE_TEMPLATE,
            "manual.md": MANUAL_TEMPLATE
        }

        for fname, template in files_to_create.items():
            fpath = os.path.join(self.target_dir, fname)
            if os.path.exists(fpath): continue
            content = template
            for key, val in mapping.items():
                content = content.replace(key, val)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[DONE] 已创建 {fname}")

    def setup_global(self):
        """激活电脑全局潜意识"""
        global_path = os.path.expanduser("~/.gemini/GEMINI.md")
        if not os.path.exists(os.path.dirname(global_path)):
            os.makedirs(os.path.dirname(global_path))
        if os.path.exists(global_path):
            with open(global_path, 'r') as f:
                if "MEMOHACK" in f.read():
                    print("[SKIP] 全局规则已激活。")
                    return
            shutil.copy(global_path, global_path + ".bak")
        
        with open(global_path, 'a', encoding='utf-8') as f:
            f.write(GLOBAL_RULES)
        print("[SUCCESS] 全局规则激活成功！")

def main():
    parser = argparse.ArgumentParser(description="MemoHack 社区版仓库安装器 (Repo-based)")
    parser.add_argument("--force", action="store_true", help="强制覆盖已有的 Skills")
    parser.add_argument("--global_only", action="store_true", help="仅激活全局规则")
    
    args = parser.parse_args()
    installer = MemohackInstaller(os.getcwd())

    # 全能一键模式
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and args.force):
        print("🚀 [MEMOHACK] 正在启动仓库中心化全量安装流程...")
        installer.setup_global()
        installer.scan_project()
        installer.setup_workspace_files(scan=True)
        installer.sync_skills(force=args.force)
        print("\n✨ [SUCCESS] 全部模块已从仓库同步部署完成！")
        return

    if args.global_only:
        installer.setup_global()

if __name__ == "__main__":
    main()
