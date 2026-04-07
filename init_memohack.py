import os
import sys
import argparse
import shutil
import re
import json
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

## 2. 人机协同工作流 (ADVANCED 模式)
- **补丁预览**：在执行任何针对 `manual.md` 或 `CURRENT_STATE.md` 的写入操作前，必须通过 Artifact 生成预览补丁。
"""

# ==========================================
# 已知框架指纹库 (Framework Fingerprints)
# ==========================================

# Node.js 生态
NODE_FRAMEWORKS = {
    "next": "Next.js", "nuxt": "Nuxt.js", "react": "React",
    "vue": "Vue.js", "angular": "Angular", "svelte": "Svelte",
    "express": "Express", "fastify": "Fastify", "koa": "Koa",
    "nest": "NestJS", "hono": "Hono", "elysia": "Elysia",
    "prisma": "Prisma ORM", "sequelize": "Sequelize ORM",
    "mongoose": "Mongoose (MongoDB)", "typeorm": "TypeORM",
    "drizzle-orm": "Drizzle ORM",
    "tailwindcss": "TailwindCSS", "sass": "Sass/SCSS",
    "vite": "Vite", "webpack": "Webpack", "esbuild": "esbuild",
    "jest": "Jest", "vitest": "Vitest", "mocha": "Mocha",
    "socket.io": "Socket.IO", "redis": "Redis Client",
    "bull": "Bull (队列)", "bullmq": "BullMQ (队列)",
}

# Python 生态
PYTHON_FRAMEWORKS = {
    "django": "Django", "flask": "Flask", "fastapi": "FastAPI",
    "tornado": "Tornado", "sanic": "Sanic", "starlette": "Starlette",
    "sqlalchemy": "SQLAlchemy", "peewee": "Peewee ORM",
    "tortoise-orm": "Tortoise ORM", "alembic": "Alembic (迁移)",
    "celery": "Celery (异步任务)", "redis": "Redis",
    "pymongo": "PyMongo (MongoDB)", "psycopg2": "PostgreSQL Driver",
    "mysqlclient": "MySQL Driver", "pymysql": "PyMySQL",
    "pytest": "Pytest", "scrapy": "Scrapy (爬虫)",
    "pandas": "Pandas", "numpy": "NumPy",
    "tensorflow": "TensorFlow", "torch": "PyTorch",
    "gunicorn": "Gunicorn", "uvicorn": "Uvicorn",
}

# ==========================================
# 深度扫描引擎 (Deep Scan Engine)
# ==========================================

class MemohackInstaller:
    def __init__(self, target_dir, force_here=False):
        self.repo_root = os.path.dirname(os.path.abspath(__file__))

        current_abs = os.path.abspath(target_dir)
        if current_abs == self.repo_root and not force_here:
            parent_dir = os.path.abspath(os.path.join(current_abs, ".."))
            print("\n" + "!"*50)
            print(f"  检测到在工具目录运行。")
            print(f"  MemoHack 将自动为【父项目】初始化记忆引擎:")
            print(f"  👉 {parent_dir}")
            print("!"*50 + "\n")
            self.target_dir = parent_dir
        else:
            self.target_dir = current_abs

        # 项目画像数据容器
        self.portrait = {
            "project_name": os.path.basename(self.target_dir),
            "project_desc": "",
            "tech_stack": "Generic",
            "frameworks": [],
            "main_files": [],
            "dependencies": "",
            "infrastructure": "",
            "dir_tree": "",
            "commands": "",
            "git_history": "",
        }

    # ------------------------------------------
    # 第1层：README 描述提取
    # ------------------------------------------
    def _scan_readme(self):
        """从 README.md 中提取项目描述（前10行有效内容）"""
        for name in ["README.md", "readme.md", "Readme.md"]:
            readme_path = os.path.join(self.target_dir, name)
            if os.path.exists(readme_path):
                with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()

                # 提取非空、非标题装饰的有效行
                desc_lines = []
                for line in lines[:20]:
                    stripped = line.strip()
                    if not stripped:
                        continue
                    # 跳过徽章行 (badges)
                    if stripped.startswith('[![') or stripped.startswith('!['):
                        continue
                    desc_lines.append(stripped)
                    if len(desc_lines) >= 5:
                        break

                if desc_lines:
                    self.portrait["project_desc"] = "\n".join(desc_lines)
                    print(f"  [✓] README.md → 提取了 {len(desc_lines)} 行项目描述")
                return
        print(f"  [—] README.md → 未找到")

    # ------------------------------------------
    # 第2层：依赖与框架精确解析
    # ------------------------------------------
    def _scan_dependencies(self):
        """解析依赖清单并识别核心框架"""
        stacks = []
        frameworks = []
        dep_sections = []

        # --- Node.js ---
        pkg_path = os.path.join(self.target_dir, "package.json")
        if os.path.exists(pkg_path):
            stacks.append("Node.js")
            try:
                with open(pkg_path, 'r', encoding='utf-8') as f:
                    pkg = json.load(f)

                all_deps = {}
                all_deps.update(pkg.get("dependencies", {}))
                all_deps.update(pkg.get("devDependencies", {}))

                # 匹配框架指纹
                matched = []
                for key, label in NODE_FRAMEWORKS.items():
                    if any(key in dep_name for dep_name in all_deps):
                        matched.append(label)
                        frameworks.append(label)

                dep_lines = [f"  - `{k}`: {v}" for k, v in list(pkg.get("dependencies", {}).items())[:15]]
                section = "### Node.js (package.json)\n"
                if matched:
                    section += f"- **核心框架**: {', '.join(matched)}\n"
                section += f"- **依赖数量**: {len(all_deps)} 个\n"
                if dep_lines:
                    section += "- **主要依赖**:\n" + "\n".join(dep_lines) + "\n"
                dep_sections.append(section)
                print(f"  [✓] package.json → {len(all_deps)} 个依赖, 识别框架: {', '.join(matched) if matched else 'N/A'}")
            except Exception as e:
                print(f"  [!] package.json 解析失败: {e}")

        # --- Python ---
        req_path = os.path.join(self.target_dir, "requirements.txt")
        if os.path.exists(req_path):
            stacks.append("Python")
            with open(req_path, 'r', encoding='utf-8', errors='ignore') as f:
                req_lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]

            matched = []
            for key, label in PYTHON_FRAMEWORKS.items():
                if any(key in dep.lower().split('==')[0].split('>=')[0] for dep in req_lines):
                    matched.append(label)
                    frameworks.append(label)

            section = "### Python (requirements.txt)\n"
            if matched:
                section += f"- **核心框架**: {', '.join(matched)}\n"
            section += f"- **依赖数量**: {len(req_lines)} 个\n"
            dep_lines = [f"  - `{dep}`" for dep in req_lines[:15]]
            if dep_lines:
                section += "- **主要依赖**:\n" + "\n".join(dep_lines) + "\n"
            dep_sections.append(section)
            print(f"  [✓] requirements.txt → {len(req_lines)} 个依赖, 识别框架: {', '.join(matched) if matched else 'N/A'}")

        elif any(os.path.exists(os.path.join(self.target_dir, f)) for f in ['setup.py', 'pyproject.toml', 'Pipfile']):
            stacks.append("Python")
            dep_sections.append("### Python\n- 检测到 Python 项目（无 requirements.txt，请手动补充依赖信息）\n")
            print(f"  [✓] Python 项目 → 无 requirements.txt")

        # --- Go ---
        gomod_path = os.path.join(self.target_dir, "go.mod")
        if os.path.exists(gomod_path):
            stacks.append("Go")
            with open(gomod_path, 'r', encoding='utf-8') as f:
                go_content = f.read()
            go_deps = re.findall(r'^\t(\S+)', go_content, re.MULTILINE)
            section = "### Go (go.mod)\n"
            section += f"- **依赖数量**: {len(go_deps)} 个\n"
            dep_lines = [f"  - `{dep}`" for dep in go_deps[:10]]
            if dep_lines:
                section += "- **主要依赖**:\n" + "\n".join(dep_lines) + "\n"
            dep_sections.append(section)
            print(f"  [✓] go.mod → {len(go_deps)} 个依赖")

        # --- Rust ---
        cargo_path = os.path.join(self.target_dir, "Cargo.toml")
        if os.path.exists(cargo_path):
            stacks.append("Rust")
            dep_sections.append("### Rust (Cargo.toml)\n- 检测到 Rust 项目\n")
            print(f"  [✓] Cargo.toml → Rust 项目")

        # 补充：如果有 .py 文件但没被上面捕获
        if "Python" not in stacks:
            for root, _, files in os.walk(self.target_dir):
                if '.git' in root or 'node_modules' in root:
                    continue
                if any(f.endswith('.py') for f in files):
                    stacks.append("Python")
                    break

        self.portrait["tech_stack"] = " / ".join(stacks) if stacks else "Generic"
        self.portrait["frameworks"] = frameworks
        self.portrait["dependencies"] = "\n".join(dep_sections) if dep_sections else "未检测到依赖文件。"

    # ------------------------------------------
    # 第3层：基础设施探测
    # ------------------------------------------
    def _scan_infrastructure(self):
        """探测 Docker, 数据库, CI/CD, 环境变量"""
        infra = []

        # Docker
        compose_names = ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]
        for name in compose_names:
            compose_path = os.path.join(self.target_dir, name)
            if os.path.exists(compose_path):
                with open(compose_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                services = re.findall(r'^\s{2}(\w[\w-]*):', content, re.MULTILINE)
                # 探测数据库镜像
                dbs = []
                if 'mysql' in content.lower(): dbs.append("MySQL")
                if 'postgres' in content.lower(): dbs.append("PostgreSQL")
                if 'mongo' in content.lower(): dbs.append("MongoDB")
                if 'redis' in content.lower(): dbs.append("Redis")
                if 'mariadb' in content.lower(): dbs.append("MariaDB")

                section = f"### Docker ({name})\n"
                section += f"- **服务列表**: {', '.join(services[:10]) if services else 'N/A'}\n"
                if dbs:
                    section += f"- **数据库/缓存**: {', '.join(dbs)}\n"
                # 端口映射
                ports = re.findall(r'"?(\d+:\d+)"?', content)
                if ports:
                    section += f"- **端口映射**: {', '.join(ports[:8])}\n"
                infra.append(section)
                print(f"  [✓] {name} → 服务: {', '.join(services[:5])}, 数据库: {', '.join(dbs) if dbs else 'N/A'}")
                break

        if os.path.exists(os.path.join(self.target_dir, "Dockerfile")):
            if not any("Docker" in i for i in infra):
                infra.append("### Docker\n- 检测到 `Dockerfile`\n")
                print(f"  [✓] Dockerfile → 存在")

        # 环境变量
        for env_name in [".env.example", ".env.sample", ".env.template"]:
            env_path = os.path.join(self.target_dir, env_name)
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
                    env_lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]
                keys = [l.split('=')[0].strip() for l in env_lines if '=' in l]
                section = f"### 环境变量 ({env_name})\n"
                section += f"- **变量数量**: {len(keys)} 个\n"
                if keys:
                    section += "- **关键变量**: " + ", ".join([f"`{k}`" for k in keys[:12]]) + "\n"
                infra.append(section)
                print(f"  [✓] {env_name} → {len(keys)} 个环境变量")
                break

        # Nginx / Caddy
        for cfg_name in ["nginx.conf", "Caddyfile"]:
            cfg_path = os.path.join(self.target_dir, cfg_name)
            if os.path.exists(cfg_path):
                infra.append(f"### 反向代理\n- 检测到 `{cfg_name}`\n")
                print(f"  [✓] {cfg_name} → 反向代理配置")

        # CI/CD
        ci_paths = [
            (".github/workflows", "GitHub Actions"),
            (".gitlab-ci.yml", "GitLab CI"),
            ("Jenkinsfile", "Jenkins"),
        ]
        for ci_path, ci_name in ci_paths:
            full_path = os.path.join(self.target_dir, ci_path)
            if os.path.exists(full_path):
                infra.append(f"### CI/CD\n- 检测到 `{ci_name}`\n")
                print(f"  [✓] {ci_name} → CI/CD 配置")

        self.portrait["infrastructure"] = "\n".join(infra) if infra else "未检测到基础设施配置。"

    # ------------------------------------------
    # 第4层：目录结构树
    # ------------------------------------------
    def _scan_structure(self):
        """生成2层深度的目录结构树"""
        tree_lines = []
        base_depth = self.target_dir.count(os.sep)
        skip_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.venv',
                     '.agents', '.next', '.nuxt', 'dist', 'build', '.cache'}

        for root, dirs, files in os.walk(self.target_dir):
            # 过滤隐藏和无关目录
            dirs[:] = [d for d in sorted(dirs) if d not in skip_dirs and not d.startswith('.')]

            depth = root.count(os.sep) - base_depth
            if depth > 2:
                continue

            indent = "  " * depth
            dir_name = os.path.basename(root)
            if depth == 0:
                dir_name = self.portrait["project_name"] + "/"
            else:
                dir_name = dir_name + "/"

            tree_lines.append(f"{indent}{dir_name}")

            # 只在前两层显示文件
            if depth <= 1:
                for f in sorted(files)[:10]:
                    tree_lines.append(f"{indent}  {f}")
                remaining = len(files) - 10
                if remaining > 0:
                    tree_lines.append(f"{indent}  ... ({remaining} more files)")

        # 同时收集入口文件
        entry_patterns = ['main', 'app', 'index', 'server', 'start', 'manage']
        code_exts = ['py', 'js', 'ts', 'go', 'rs', 'jsx', 'tsx']
        main_files = []

        for root, dirs, files in os.walk(self.target_dir):
            if any(p in root for p in skip_dirs):
                continue
            depth = root.count(os.sep) - base_depth
            if depth > 2:
                continue
            for f in files:
                if f.split('.')[-1] in code_exts:
                    fname_lower = os.path.splitext(f)[0].lower()
                    if any(p in fname_lower for p in entry_patterns):
                        rel = os.path.relpath(os.path.join(root, f), self.target_dir)
                        main_files.append(rel)

        self.portrait["main_files"] = main_files
        self.portrait["dir_tree"] = "\n".join(tree_lines[:60])
        print(f"  [✓] 目录树 → {len(tree_lines)} 个节点, 入口文件: {len(main_files)} 个")

    # ------------------------------------------
    # 第5层：构建/运行命令提取
    # ------------------------------------------
    def _scan_commands(self):
        """从 package.json scripts 和 Makefile 中提取常用命令"""
        cmd_sections = []

        # package.json scripts
        pkg_path = os.path.join(self.target_dir, "package.json")
        if os.path.exists(pkg_path):
            try:
                with open(pkg_path, 'r', encoding='utf-8') as f:
                    pkg = json.load(f)
                scripts = pkg.get("scripts", {})
                if scripts:
                    section = "### npm scripts (package.json)\n"
                    for key, val in list(scripts.items())[:12]:
                        section += f"- `npm run {key}` → {val}\n"
                    cmd_sections.append(section)
                    print(f"  [✓] package.json scripts → {len(scripts)} 条命令")
            except:
                pass

        # Makefile
        make_path = os.path.join(self.target_dir, "Makefile")
        if os.path.exists(make_path):
            with open(make_path, 'r', encoding='utf-8', errors='ignore') as f:
                make_content = f.read()
            targets = re.findall(r'^([a-zA-Z_][\w-]*):', make_content, re.MULTILINE)
            if targets:
                section = "### Makefile\n"
                for t in targets[:10]:
                    section += f"- `make {t}`\n"
                cmd_sections.append(section)
                print(f"  [✓] Makefile → {len(targets)} 个 target")

        self.portrait["commands"] = "\n".join(cmd_sections) if cmd_sections else "未检测到构建命令。可手动补充 `npm run dev` 或 `python3 manage.py runserver` 等。"

    # ------------------------------------------
    # 第6层：Git 近期历史
    # ------------------------------------------
    def _scan_git_context(self):
        """获取最近5条 git commit 记录"""
        git_dir = os.path.join(self.target_dir, ".git")
        if not os.path.exists(git_dir):
            self.portrait["git_history"] = "未检测到 Git 仓库。"
            print(f"  [—] Git → 未找到 .git 目录")
            return

        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "--no-decorate", "-10"],
                capture_output=True, text=True, cwd=self.target_dir, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                history = "\n".join([f"- `{line}`" for line in lines])
                self.portrait["git_history"] = history
                print(f"  [✓] Git log → 最近 {len(lines)} 条提交")
            else:
                self.portrait["git_history"] = "Git 仓库为空或无提交历史。"
                print(f"  [—] Git → 无提交历史")
        except Exception as e:
            self.portrait["git_history"] = f"Git 历史获取失败: {e}"
            print(f"  [!] Git → 获取失败: {e}")

    # ------------------------------------------
    # 主扫描入口
    # ------------------------------------------
    def scan_project(self):
        """执行6层深度项目扫描"""
        print(f"\n{'='*50}")
        print(f"📊 深度扫描引擎启动 (Deep Scan Engine)")
        print(f"📍 目标路径: {self.target_dir}")
        print(f"{'='*50}")

        print(f"\n[1/6] 🔍 读取项目描述 (README)...")
        self._scan_readme()

        print(f"\n[2/6] 📦 解析依赖与框架 (Dependencies)...")
        self._scan_dependencies()

        print(f"\n[3/6] 🏭 探测基础设施 (Infrastructure)...")
        self._scan_infrastructure()

        print(f"\n[4/6] 📂 生成目录结构 (Structure)...")
        self._scan_structure()

        print(f"\n[5/6] ⚡ 提取构建命令 (Commands)...")
        self._scan_commands()

        print(f"\n[6/6] 📜 捕获近期历史 (Git Context)...")
        self._scan_git_context()

        # 输出最终画像
        print(f"\n{'='*50}")
        print(f"📊 项目画像报告 (Project Portrait)")
        print(f"{'='*50}")
        print(f"  项目名称 : {self.portrait['project_name']}")
        print(f"  项目描述 : {self.portrait['project_desc'][:80] if self.portrait['project_desc'] else 'N/A'}...")
        print(f"  技术栈   : {self.portrait['tech_stack']}")
        print(f"  核心框架 : {', '.join(self.portrait['frameworks']) if self.portrait['frameworks'] else 'N/A'}")
        print(f"  入口文件 : {', '.join(self.portrait['main_files'][:5]) if self.portrait['main_files'] else 'N/A'}")
        print(f"{'='*50}\n")

    # ------------------------------------------
    # 文件部署
    # ------------------------------------------
    def sync_skills(self, force=False):
        """同步技能模块"""
        source_skills = os.path.join(self.repo_root, "skills")
        target_skills = os.path.join(self.target_dir, "skills")

        if not os.path.exists(source_skills):
            print(f"[RE-ROUTE] 仓库目录下未发现 skills 文件夹")
            return False

        # 防止自拷自
        if os.path.abspath(source_skills) == os.path.abspath(target_skills):
            print(f"[SKIP] 源目录与目标目录相同，跳过 Skills 同步。")
            return True

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
        p = self.portrait

        mapping = {
            "{{PROJECT_PATH}}": self.target_dir,
            "{{PROJECT_NAME}}": p["project_name"],
            "{{PROJECT_DESC}}": p["project_desc"] if p["project_desc"] else "（初次扫描未检测到 README，请手动填写项目描述）",
            "{{NOW}}": now,
            "{{TECH_STACK}}": p["tech_stack"] if scan else "Generic",
            "{{FRAMEWORKS}}": ", ".join(p["frameworks"]) if p["frameworks"] else "未检测到",
            "{{MAIN_FILES}}": ", ".join(p["main_files"][:8]) if p["main_files"] else "未检测到",
            "{{DEPENDENCIES}}": p["dependencies"],
            "{{INFRASTRUCTURE}}": p["infrastructure"],
            "{{DIR_TREE}}": p["dir_tree"],
            "{{COMMANDS}}": p["commands"],
            "{{GIT_HISTORY}}": p["git_history"],
        }

        # 规则文件注入 (Workspace Level)
        rules_dir = os.path.join(self.target_dir, ".agents/rules")
        if not os.path.exists(rules_dir):
            os.makedirs(rules_dir)
        with open(os.path.join(rules_dir, "memohack.md"), 'w', encoding='utf-8') as f:
            f.write(GLOBAL_RULES)

        # 从 public 文件夹读取物理模板
        fnames = ["00_MEMOHACK_BOOT.md", "CURRENT_STATE.md", "manual.md"]
        for fname in fnames:
            source_path = os.path.join(self.repo_root, "public", fname)
            target_path = os.path.join(self.target_dir, fname)

            if os.path.exists(target_path) and not force:
                print(f"[SKIP] {fname} 已存在，跳过。（使用 --force 覆盖）")
                continue

            if not os.path.exists(source_path):
                print(f"[ERROR] 找不到公共模版: {source_path}")
                continue

            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 执行占位符注水
            for key, val in mapping.items():
                content = content.replace(key, val)

            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[DONE] {fname} → 已生成")

        # 自动部署 vibe_sync.py
        sync_src = os.path.join(self.repo_root, "skills", "memohack", "scripts", "vibe_sync.py")
        sync_dst_dir = os.path.join(self.target_dir, "skills", "memohack", "scripts")
        sync_dst = os.path.join(sync_dst_dir, "vibe_sync.py")
        if os.path.exists(sync_src) and not os.path.exists(sync_dst):
            os.makedirs(sync_dst_dir, exist_ok=True)
            shutil.copy2(sync_src, sync_dst)
            print(f"[DONE] vibe_sync.py → 已部署")
        elif os.path.exists(sync_dst):
            print(f"[SKIP] vibe_sync.py 已存在。")

    def setup_global(self):
        """激活全局记忆指令"""
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
    parser = argparse.ArgumentParser(description="MemoHack 深度扫描安装器 v3.0")
    parser.add_argument("path", nargs="?", default=os.getcwd(), help="指定安装的目标路径 (默认为当前目录)")
    parser.add_argument("--force", action="store_true", help="强制覆盖已有的 Skills 和模板文件")
    parser.add_argument("--here", action="store_true", help="强制在当前目录初始化，不触发智能寻址")
    parser.add_argument("--global_only", action="store_true", help="仅激活全局规则")

    args = parser.parse_args()
    installer = MemohackInstaller(args.path, force_here=args.here)

    if not args.global_only:
        print("🚀 [MEMOHACK v3.0] 深度扫描安装器启动...\n")
        installer.setup_global()
        installer.scan_project()
        installer.setup_workspace_files(scan=True, force=args.force)
        installer.sync_skills(force=args.force)
        print("\n✨ [SUCCESS] 项目记忆引擎初始化完成！")
        print(f"📁 记忆文件部署位置: {installer.target_dir}")
        print("📖 请查看 manual.md 获取完整的项目画像。")
        return

    if args.global_only:
        installer.setup_global()

if __name__ == "__main__":
    main()
