import os
import sys
import argparse
import re
import shutil
from datetime import datetime

# 基础配置文件定义
BOOT_FILE = "00_MEMOHACK_BOOT.md"
STATE_FILE = "CURRENT_STATE.md"
MANUAL_FILE = "manual.md"
PATCH_FILE = "/tmp/memohack_patch.md"

# 锚点定义 (强容错正则匹配)
ANCHORS = {
    "CHECKPOINT": r"## .*Checkpoints",
    "REDLINE": r"## .*Redline",
    "MANUAL": r"## .*技术沉淀"
}

def get_config_mode():
    """读取 manual.md 检查内存模式 (AUTO/ADVANCED)"""
    mode = "ADVANCED"
    if os.path.exists(MANUAL_FILE):
        with open(MANUAL_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            if "MEMORY_MODE: AUTO" in content:
                mode = "AUTO"
    return mode

def generate_entry(target_type, content):
    """根据类型生成 3-S 标准条目"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    tag = "#MH-BOOT" if target_type == "CHECKPOINT" else "#MH-DEBUG"
    return f"- **{now}** [{tag}]: {content} [Status: OK]\n"

def smart_insert(file_path, anchor_regex, new_entry):
    """智能插队逻辑：在锚点标题下方插入"""
    if not os.path.exists(file_path):
        return False, f"文件 {file_path} 不存在"

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    found = False
    new_lines = []
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        if re.search(anchor_regex, line):
            # 在标题行之后插入新条目
            new_lines.append(new_entry)
            found = True
    
    if not found:
        # 如果没找到锚点，则追加到末尾
        new_lines.append(f"\n{new_entry}")

    # 原子写入流程
    temp_path = file_path + ".tmp"
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    # 备份并替换
    shutil.move(temp_path, file_path)
    return True, "同步成功"

def create_patch(target_type, content):
    """预览模式：生成补丁文件"""
    entry = generate_entry(target_type, content)
    target_file = STATE_FILE if target_type in ["CHECKPOINT", "REDLINE"] else MANUAL_FILE
    
    patch_content = f"### 🛡️ MemoHack 提议补丁\n"
    patch_content += f"**目标文件**: `{target_file}`\n"
    patch_content += f"**插入位置**: `{ANCHORS.get(target_type, 'End of file')}`\n\n"
    patch_content += "#### [即将写入的内容]\n"
    patch_content += entry
    patch_content += "\n---\n*请在对话框回复 'Confirm' 进行合入。*"

    with open(PATCH_FILE, 'w', encoding='utf-8') as f:
        f.write(patch_content)
    
    # 打印给 AI 代理捕获
    print(f"\n[MEMOHACK_PATCH_START]\n{patch_content}\n[MEMOHACK_PATCH_END]")

def main():
    parser = argparse.ArgumentParser(description="MemoHack 精准固化引擎 (SmartAnchor)")
    parser.add_argument("--type", choices=["CHECKPOINT", "REDLINE", "MANUAL"], required=True)
    parser.add_argument("--content", required=True)
    parser.add_argument("--confirm", action="store_true")

    args = parser.parse_args()
    mode = get_config_mode()

    if mode == "ADVANCED" and not args.confirm:
        create_patch(args.type, args.content)
        return

    # 执行合入逻辑
    target_file = STATE_FILE if args.type in ["CHECKPOINT", "REDLINE"] else MANUAL_FILE
    anchor = ANCHORS.get(args.type, "")
    entry = generate_entry(args.type, args.content)
    
    success, msg = smart_insert(target_file, anchor, entry)
    if success:
        print(f"[SUCCESS] {msg}: {target_file}")
    else:
        print(f"[ERROR] {msg}")

if __name__ == "__main__":
    main()
