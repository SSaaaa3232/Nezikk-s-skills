---
name: git-down
description: 同步 GitHub star 列表到 Obsidian。当用户输入 `/git down` 时触发。自动拉取 GitHub 上所有 starred 仓库，按用户的 GitHub Lists 分类整理，生成 Markdown 文件保存到 Obsidian vault。每次执行都覆盖写入，保持文件与 GitHub 最新状态同步。
---

# git-down

## 触发方式
用户输入 `/git down`

## 功能
从 GitHub 拉取用户全部 starred 仓库，按 GitHub Lists 分类整理，覆盖写入 `/Users/saaaaa/Obsidian-Template/GitHub Stars.md`。

## 输出格式

文件标题为 `# GitHub Stars`，每个 List 对应一个二级标题（保留原始 emoji），内容用表格展示：

```markdown
# GitHub Stars

## 🔥 分类名

| 项目 | 描述 |
|------|------|
| [owner/repo](https://github.com/owner/repo) | |

## 未分类

| 项目 | 描述 |
|------|------|
| [owner/repo](https://github.com/owner/repo) | |
```

规则：
- 描述列**优先保留现有文件中用户已填写的内容**，没有则留空
- 不属于任何 List 的 star 放入「未分类」组，排在最后
- 覆盖写入，不追加

## 执行步骤

用以下 Python 脚本完成全部操作，直接用 Bash 执行：

```python
import subprocess, json, sys, re, os

output_path = '/Users/saaaaa/Obsidian-Template/清单/GitHub Stars.md'

# 0. 读取现有文件，提取用户已填写的描述 {repo: desc}
existing_descs = {}
if os.path.exists(output_path):
    with open(output_path, 'r') as f:
        for line in f:
            # 匹配表格行: | [owner/repo](url) | 描述内容 |
            m = re.match(r'\|\s*\[([^\]]+)\]\(https://github\.com/[^\)]+\)\s*\|\s*(.*?)\s*\|', line)
            if m:
                repo, desc = m.group(1), m.group(2).strip()
                if desc:
                    existing_descs[repo] = desc

# 1. 获取所有 Lists 及其仓库
result = subprocess.run(
    ['gh', 'api', 'graphql', '-f', 'query={ viewer { lists(first:50) { nodes { name items(first:100) { nodes { ... on Repository { nameWithOwner } } } } } } }'],
    capture_output=True, text=True
)
data = json.loads(result.stdout)
lists = data['data']['viewer']['lists']['nodes']

# 2. 获取全部 starred 仓库
result2 = subprocess.run(
    ['gh', 'api', 'user/starred', '--paginate', '--jq', '.[].full_name'],
    capture_output=True, text=True
)
all_starred = set(line.strip() for line in result2.stdout.strip().splitlines() if line.strip())

# 3. 统计已分类的
categorized = set()
for lst in lists:
    if lst is None:
        continue
    for node in lst['items']['nodes']:
        if node and 'nameWithOwner' in node:
            categorized.add(node['nameWithOwner'])

uncategorized = all_starred - categorized

# 4. 生成 Markdown（描述优先用现有内容）
lines = ['# GitHub Stars\n']

for lst in lists:
    repos = [n['nameWithOwner'] for n in lst['items']['nodes'] if 'nameWithOwner' in n]
    if not repos:
        continue
    lines.append(f"\n## {lst['name']}\n")
    lines.append('| 项目 | 描述 |')
    lines.append('|------|------|')
    for repo in repos:
        desc = existing_descs.get(repo, '')
        lines.append(f'| [{repo}](https://github.com/{repo}) | {desc} |')

if uncategorized:
    lines.append('\n## 未分类\n')
    lines.append('| 项目 | 描述 |')
    lines.append('|------|------|')
    for repo in sorted(uncategorized):
        desc = existing_descs.get(repo, '')
        lines.append(f'| [{repo}](https://github.com/{repo}) | {desc} |')

# 5. 写入文件
with open(output_path, 'w') as f:
    f.write('\n'.join(lines) + '\n')

preserved = sum(1 for r in existing_descs if r in all_starred)
print(f'✓ 已写入 {output_path}')
print(f'  分类: {len(lists)} 个，总计: {len(all_starred)} 个 star，未分类: {len(uncategorized)} 个')
print(f'  已保留用户描述: {preserved} 条')
```

将上述脚本保存为临时文件后执行，或直接用 `python3 -c` 运行。执行完毕后告知用户写入结果（几个分类、几个 star、几个未分类、保留了几条描述）。
