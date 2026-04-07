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
    def __init__(self, target_dir, force_here=False):
        # 核心：定位仓库自身的根目录
        self.repo_root = os.path.dirname(os.path.abspath(__file__))
        
        # 智能寻址：如果在工具目录内运行，且没指定强制当前目录，则尝试初始化父目录
        current_abs = os.path.abspath(target_dir)
        if current_abs == self.repo_root and not force_here:
            parent_dir = os.path.abspath(os.path.join(current_abs, ".."))
            print("\n" + "!"*40)
            print(f"检测到在工具目录运行。为了更好的记忆体验，")
            print(f"MemoHack 将自动将目标设定为【父项目根目录】:")
            print(f"👉 {parent_dir}")
            print("!"*40 + "\n")
            self.target_dir = parent_dir
        else:
            self.target_dir = current_abs
            
        self.tech_stack = "Unknown"
        self.main_files = []

    def scan_project(self):
        """深度扫描目标项目画像 (Depth=2)"""
        print(f"[SCAN] 正在分析项目结构: {self.target_dir}")
        
        all_files = []
        # 递归扫描最多 2 层深度
        base_depth = self.target_dir.count(os.sep)
        for root, dirs, files in os.walk(self.target_dir):
            # 排除干扰项
            if any(p in root for p in ['.git', '__pycache__', 'node_modules', 'venv', '.agents']):
                continue
                
            depth = root.count(os.sep) - base_depth
            if depth > 2:
                continue
            
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), self.target_dir)
                all_files.append(rel_path)

        # 识别技术栈
        stacks = []
        if any(f.endswith('package.json') for f in all_files): stacks.append("Node.js")
        if any(f.endswith('.py') for f in all_files): stacks.append("Python")
        if any(f.endswith('go.mod') for f in all_files): stacks.append("Go")
        if any(f.endswith('Cargo.toml') for f in all_files): stacks.append("Rust")
        self.tech_stack = " / ".join(stacks) if stacks else "Generic"

        # 识别入口文件
        entry_patterns = ['main', 'app', 'index', 'server', 'start']
        candidates = [f for f in all_files if f.split('.')[-1] in ['py', 'js', 'go', 'ts', 'rs']]
        
        for f in candidates:
            fname = os.path.basename(f).lower()
            if any(p in fname for p in entry_patterns):
                self.main_files.append(f)
        
        # 兜底：如果没找到 main，取前三个代码文件
        if not self.main_files and candidates:
            self.main_files = candidates[:3]

        # 打印项目画像
        print("\n" + "="*30)
        print("📊 项目画像报告 (Project Portrait)")
        print("="*30)
        print(f"📍 目标路径 : {self.target_dir}")
        print(f"🛠️ 技术栈   : {self.tech_stack}")
        print(f"🚀 入口文件 : {', '.join(self.main_files) if self.main_files else 'None'}")
        print("="*30 + "\n")

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

    def setup_workspace_files(self, scan=False, force=False):
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

            if os.path.exists(target_path) and not force: 
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
            print(f"[DONE] {'覆盖' if force and os.path.exists(target_path) else '创建'}了 {fname}")

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
    parser.add_argument("path", nargs="?", default=os.getcwd(), help="指定安装的目标路径 (默认为当前目录)")
    parser.add_argument("--force", action="store_true", help="强制覆盖已有的 Skills 或模板")
    parser.add_argument("--here", action="store_true", help="强制在当前工具目录下初始化记忆文件，不触发智能寻址")
    parser.add_argument("--global_only", action="store_true", help="仅激活全局规则")
    
    args = parser.parse_args()
    installer = MemohackInstaller(args.path, force_here=args.here)

    # 全能一键模式
    if not args.global_only:
        print("🚀 [MEMOHACK] 正在启动仓库级资产分发流程...")
        installer.setup_global()
        installer.scan_project()
        installer.setup_workspace_files(scan=True, force=args.force)
        # 这里的 force 对 sync_skills 生效
        installer.sync_skills(force=args.force)
        print("\n✨ [SUCCESS] 全部公共资产已从仓库同步部署完成！")
        return

    if args.global_only:
        installer.setup_global()

if __name__ == "__main__":
    main()
