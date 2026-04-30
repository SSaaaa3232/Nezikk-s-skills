---
name: image
description: 整理 Obsidian vault 中散落的图片文件。当用户输入 `/image` 时触发。自动将 GIF、SVG、PNG、JPG/JPEG、WEBP 文件移动到 image 文件夹，并更新所有 Markdown 文件中的引用路径。
---

# image

## 触发方式
用户输入 `/image`

## 功能
扫描 Obsidian vault，将散落在各处的图片文件（GIF、SVG、PNG、JPG/JPEG、WEBP）统一移动到 `image/` 文件夹，同时更新所有 Markdown 文件中的相关引用，确保链接不会断裂。

## 规则
- 跳过已在 `image/` 文件夹内的文件
- 跳过 `.obsidian`、`.claude`、`.claudian` 等隐藏目录
- 如果目标路径已存在同名文件，自动加数字后缀避免覆盖（如 `foo_1.png`）
- 同时更新 Wikilink（`![[file.png]]`）和 Markdown（`![alt](path/file.png)`）两种引用格式

## 执行步骤

用以下 Python 脚本完成全部操作，直接用 Bash 执行：

```python
import os, re, shutil

VAULT = '/Users/saaaaa/Obsidian-Template'
IMAGE_DIR = os.path.join(VAULT, 'image')
EXTS = {'.gif', '.svg', '.png', '.jpg', '.jpeg', '.webp'}
SKIP_DIRS = {'.obsidian', '.claude', '.claudian', 'image'}

os.makedirs(IMAGE_DIR, exist_ok=True)

# 1. 收集需要移动的图片文件
to_move = []  # [(old_abs, filename)]
for root, dirs, files in os.walk(VAULT):
    # 跳过隐藏/目标目录
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
    for fname in files:
        if os.path.splitext(fname)[1].lower() in EXTS:
            to_move.append((os.path.join(root, fname), fname))

if not to_move:
    print('✓ 没有需要移动的图片文件，vault 已整洁！')
    exit(0)

# 2. 移动文件，处理同名冲突，记录映射 {old_abs: new_abs}
moved = {}
for old_abs, fname in to_move:
    name, ext = os.path.splitext(fname)
    new_abs = os.path.join(IMAGE_DIR, fname)
    counter = 1
    while os.path.exists(new_abs):
        new_abs = os.path.join(IMAGE_DIR, f'{name}_{counter}{ext}')
        counter += 1
    shutil.move(old_abs, new_abs)
    moved[old_abs] = new_abs

# 3. 更新所有 Markdown 文件中的引用
updated_files = 0
updated_refs = 0

for root, dirs, files in os.walk(VAULT):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    for fname in files:
        if not fname.endswith('.md'):
            continue
        md_path = os.path.join(root, fname)
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            continue

        new_content = content
        for old_abs, new_abs in moved.items():
            old_name = os.path.basename(old_abs)
            new_name = os.path.basename(new_abs)
            old_rel = os.path.relpath(old_abs, VAULT)
            new_rel = os.path.relpath(new_abs, VAULT)

            # 替换 Markdown 链接中的相对路径（各种写法）
            for old_path in [old_rel, old_rel.replace('\\', '/'), old_name]:
                escaped = re.escape(old_path)
                # ![alt](path) 格式
                new_content, n1 = re.subn(
                    r'(!\[[^\]]*\]\()' + escaped + r'(\))',
                    r'\g<1>' + new_rel.replace('\\', '/') + r'\2',
                    new_content
                )
                # [text](path) 格式
                new_content, n2 = re.subn(
                    r'(\[[^\]]*\]\()' + escaped + r'(\))',
                    r'\g<1>' + new_rel.replace('\\', '/') + r'\2',
                    new_content
                )
                updated_refs += n1 + n2

            # 替换 Wikilink ![[filename]] 格式（Obsidian 只用文件名匹配，名字变了才需更新）
            if old_name != new_name:
                new_content, n3 = re.subn(
                    r'(!\[\[)' + re.escape(old_name) + r'(\]\])',
                    r'\g<1>' + new_name + r'\2',
                    new_content
                )
                updated_refs += n3

        if new_content != content:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            updated_files += 1

# 4. 汇报结果
print(f'✓ 移动了 {len(moved)} 个图片文件到 image/ 文件夹')
for old_abs, new_abs in moved.items():
    old_rel = os.path.relpath(old_abs, VAULT)
    new_rel = os.path.relpath(new_abs, VAULT)
    print(f'  {old_rel}  →  {new_rel}')
print(f'✓ 更新了 {updated_files} 个 Markdown 文件，共 {updated_refs} 处引用')
```

将上述脚本保存为临时文件后执行，或直接用 `python3 -c` 运行。执行完毕后告知用户移动了哪些文件、更新了几处引用。
