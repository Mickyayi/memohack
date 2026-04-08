import os
import sys
import argparse
import shutil
import subprocess
from datetime import datetime

# ==========================================
# MemoHack 核心系统规则 (Global Rules)
# ==========================================

GLOBAL_RULES = """
# MEMOHACK 记忆引擎指令 (MEMOHACK_V2)

## 1. 显式状态管理规范
- **引导优先**：开启新会话或新任务时，必须通过 `list_dir` 寻找并读取 `00_MEMOHACK_BOOT.md`。
- **验证后记录**：仅在终端操作成功 (Exit 0) 或代码逻辑验证无误后，方可更新 `CURRENT_STATE.md`。
- **蒸馏原则**：遵循 3-S 原子化准则（Success, Standard, Specific），将碎片信息脱水后写入手动手册。

## 2. manual.md 核心资产保护协议（最高优先级）

`manual.md` 是项目最核心的知识资产，承载所有经过验证的技术坐标，供下一个 AI 会话直接使用。

**严禁以下行为**：
- ❌ 未经用户明确确认（回复 'Confirm'），直接写入 `manual.md`
- ❌ 写入叙述型、感悟型内容（"我们发现..."、"经过讨论..."）
- ❌ 重复已存在的内容（每次写入前必须先 `cat manual.md` 比对）
- ❌ 在同一条命令中连续写入多条记录而不暂停确认

**必须遵守**：
- ✅ 写入前生成补丁预览 Artifact，等待用户回复 'Confirm'
- ✅ 每条入库内容必须是"坐标型"：包含路径/命令/字段名/数值
- ✅ 质量检验：**"下一个 AI 读到这条，能否在10秒内知道如何操作？"**
- ✅ 使用 `#MH-TAG` 标签确保 grep 可寻址

## 3. 人机协同工作流 (ADVANCED 模式)
- **补丁预览**：在执行任何针对 `manual.md` 或 `CURRENT_STATE.md` 的写入操作前，必须通过 Artifact 生成预览补丁，等待用户批注或回复 'Confirm'。
- **严禁后台黑盒操作**：特别是当知识冲突时，必须显式征询用户意见。
- **主动审计**：若 `manual.md` 包含 `[PENDING AI SCAN]`，请立即调用 `memohack-expert-scan` 技能进行深度审计。

## 4. 标签与搜索 (MH-Tags)
所有记录必须携带分类标签，确保全局 `grep` 可瞬间寻址：
- `#MH-ARCH`：架构决策、系统设计、数据流向
- `#MH-DB`：数据库坐标（表名、字段、连接信息）
- `#MH-AUTH`：认证、权限、密钥相关
- `#MH-DEBUG`：已修复的 Bug、禁区、踩坑记录
- `#MH-INFRA`：部署、Docker、服务器、端口
- `#MH-BOOT`：项目初始化与引导逻辑

## 5. 考古蒸馏触发协议
当用户在 active 对话框发送 `/distill` 时：
1. 读取 `cat manual.md` 作为比对基准
2. 从 Context Window 提炼候选坐标（只取坐标型内容）
3. 逐条比对：标注 [NEW] / [UPDATE] / [SKIP]
4. 输出补丁预览 Artifact，等待 'Confirm'
5. 用户确认后调用 `vibe_sync.py --confirm` 写入
- **Skill 路径**：`skills/retroactive-distill/SKILL.md`
"""

class MemohackInstaller:
    def __init__(self, target_dir, force_here=False):
        # 核心：定位仓库自身的根目录
        self.repo_root = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))
        
        has_explicit_path = False
        if len(sys.argv) > 1:
            for arg in sys.argv[1:]:
                if not arg.startswith('-'):
                    has_explicit_path = True
                    break

        current_abs = os.path.realpath(os.path.abspath(target_dir))
        
        if current_abs == self.repo_root and not force_here and not has_explicit_path:
            parent_dir = os.path.dirname(current_abs)
            self.target_dir = parent_dir
            print(f"\n[SMART] 自动切换至父目录: {parent_dir}")
        else:
            self.target_dir = current_abs
            print(f"\n[TARGET] 锁定目录: {self.target_dir}")

    def sync_skills(self, force=False):
        """同步技能模块 (包含 SKILL.md 大脑)"""
        source_skills = os.path.join(self.repo_root, "skills")
        target_skills = os.path.join(self.target_dir, "skills")

        if not os.path.exists(source_skills):
            return False

        if os.path.abspath(source_skills) == os.path.abspath(target_skills):
            return True

        if os.path.exists(target_skills) and force:
            shutil.rmtree(target_skills)
        elif os.path.exists(target_skills):
            print("[SKIP] Skills 目录已存在")
            return True

        shutil.copytree(source_skills, target_skills)
        print(f"[SUCCESS] Skills (AI 专家大脑) 已部署至: {target_skills}")
        return True

    def setup_workspace_files(self, force=False):
        """创建基础记忆文件骨架 (带 AI 触发钩子)"""
        print(f"[INIT] 正在注入专家级记忆骨架...")
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        mapping = {
            "{{PROJECT_NAME}}": os.path.basename(self.target_dir),
            "{{NOW}}": now,
            "{{PROJECT_PATH}}": self.target_dir
        }

        # 1. 注入 .agents 规则 (让 AI 认识并开启主动审计)
        rules_dir = os.path.join(self.target_dir, ".agents/rules")
        os.makedirs(rules_dir, exist_ok=True)
        with open(os.path.join(rules_dir, "memohack.md"), 'w', encoding='utf-8') as f:
            f.write(GLOBAL_RULES)

        # 2. 部署核心文件
        fnames = ["00_MEMOHACK_BOOT.md", "CURRENT_STATE.md", "manual.md"]
        for fname in fnames:
            source_path = os.path.join(self.repo_root, "public", fname)
            target_path = os.path.join(self.target_dir, fname)

            if os.path.exists(target_path) and not force:
                continue

            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()

            for key, val in mapping.items():
                content = content.replace(key, val)

            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[DONE] {fname} → 已生成 (DRAFT)")

def main():
    parser = argparse.ArgumentParser(description="MemoHack 专家级初始化工具 v3.0 (Skill-Driven)")
    parser.add_argument("path", nargs="?", default=os.getcwd(), help="目标路径")
    parser.add_argument("--force", action="store_true", help="强制覆盖")
    parser.add_argument("--here", action="store_true", help="强制当前目录")

    args = parser.parse_args()
    installer = MemohackInstaller(args.path, force_here=args.here)
    
    # 物理部署
    if installer.sync_skills(force=args.force):
        installer.setup_workspace_files(force=args.force)
        
    print(f"\n{'='*50}")
    print("✨ [SUCCESS] MemoHack 骨架已搭好，大脑 (Skill) 已就位！")
    print(f"{'='*50}")
    print("👉 下一步：请在此目录的 AI 会话中说：")
    print("   '请执行 memohack-expert-scan 完善项目画像'")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    main()
