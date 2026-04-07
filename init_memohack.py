import os
import sys
import argparse
import shutil
import re
from datetime import datetime

# ==========================================
# MemoHack 核心系统规则 (Global Rules)
# ==========================================

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
        print("[SCAN] 正在分析项目结构...")
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
        """同步技能模块"""
        source_skills = os.path.join(self.repo_root, "skills")
        target_skills = os.path.join(self.target_dir, "skills")
        
        if not os.path.exists(source_skills):
            print(f"[RE-ROUTE] 仓库目录下未发现 skills 文件夹")
            return False

        if os.path.exists(target_skills):
            if not force:
                print(f"[CONFLICT] 目标项目已存在 skills 文件夹。请使用 --force 参数强制覆盖。")
                return False
            else:
                shutil.rmtree(target_skills)

        shutil.copytree(source_skills, target_skills)
        print(f"[SUCCESS] Skills 全量同步成功")
        return True

    def setup_workspace_files(self, scan=False):
        """从 public 目录动态读取并创建记忆文件"""
        print(f"[INIT] 正在从 public 资产库初始化记忆文件...")
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        project_name = os.path.basename(self.target_dir)
        mapping = {
            "{{PROJECT_PATH}}": self.target_dir,
            "{{PROJECT_NAME}}": project_name,
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

        # 核心变动：从 public 文件夹读取物理模板
        fnames = ["00_MEMOHACK_BOOT.md", "CURRENT_STATE.md", "manual.md"]
        for fname in fnames:
            source_path = os.path.join(self.repo_root, "public", fname)
            target_path = os.path.join(self.target_dir, fname)

            if os.path.exists(target_path): 
                print(f"[SKIP] {fname} 已存在，跳过。")
                continue
            
            if not os.path.exists(source_path):
                print(f"[ERROR] 找不到公共模版: {source_path}")
                continue

            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 执行注水填充
            for key, val in mapping.items():
                content = content.replace(key, val)
            
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[DONE] 已由模版库创建 {fname}")

        # 自动部署 vibe_sync.py 到目标项目的 skills 目录
        sync_src = os.path.join(self.repo_root, "skills", "memohack", "scripts", "vibe_sync.py")
        sync_dst_dir = os.path.join(self.target_dir, "skills", "memohack", "scripts")
        sync_dst = os.path.join(sync_dst_dir, "vibe_sync.py")
        if os.path.exists(sync_src) and not os.path.exists(sync_dst):
            os.makedirs(sync_dst_dir, exist_ok=True)
            shutil.copy2(sync_src, sync_dst)
            print(f"[DONE] vibe_sync.py 已部署至 {sync_dst}")
        elif os.path.exists(sync_dst):
            print(f"[SKIP] vibe_sync.py 已存在，跳过。")

    def setup_global(self):
        """激活电脑全局潜意识"""
        global_path = os.path.expanduser("~/.gemini/GEMINI.md")
        if os.path.exists(global_path):
            with open(global_path, 'r') as f:
                if "MEMOHACK" in f.read():
                    print("[SKIP] 全局规则已激活。")
                    return
        
        with open(global_path, 'a', encoding='utf-8') as f:
            f.write(GLOBAL_RULES)
        print("[SUCCESS] 全局规则激活成功！")

def main():
    parser = argparse.ArgumentParser(description="MemoHack 仓库安装器 (Repo-based / Public-Assets)")
    parser.add_argument("--force", action="store_true", help="强制覆盖已有的 Skills")
    parser.add_argument("--global_only", action="store_true", help="仅激活全局规则")
    
    args = parser.parse_args()
    installer = MemohackInstaller(os.getcwd())

    # 全能一键模式
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and args.force):
        print("🚀 [MEMOHACK] 正在启动仓库级资产分发流程...")
        installer.setup_global()
        installer.scan_project()
        installer.setup_workspace_files(scan=True)
        installer.sync_skills(force=args.force)
        print("\n✨ [SUCCESS] 全部公共资产已从仓库同步部署完成！")
        return

    if args.global_only:
        installer.setup_global()

if __name__ == "__main__":
    main()
