---
name: justdo
description: Use when the user enters /justdo followed by a folder name to create that folder under the Desktop 项目 directory
---

# justdo

Use this skill when the user enters `/justdo <文件夹名字>` and wants a matching folder created under the Desktop project directory.

## Workflow

1. Parse the text after `/justdo` as the target folder name.
   - Trim leading and trailing spaces.
   - Trim matching quotes, including ASCII quotes and Chinese quotes.
   - Treat the remaining text as the `文件夹名字`.
   - Stop and ask for a valid name if it is empty, contains `/`, starts with `.`, or is `.` / `..`.

2. Use this base directory:

```text
/Users/saaaaa/Desktop/项目
```

3. Create the base directory if needed:

```bash
mkdir -p "/Users/saaaaa/Desktop/项目"
```

4. Create the target folder:

```bash
mkdir "/Users/saaaaa/Desktop/项目/<文件夹名字>"
```

5. Safety behavior:
   - If `/Users/saaaaa/Desktop/项目/<文件夹名字>` already exists, stop and report `目标文件夹已存在`.
   - 不要覆盖, rename, delete, or merge an existing folder unless the user explicitly asks for that.
   - Do not create the folder outside `/Users/saaaaa/Desktop/项目`.

6. Report the final absolute path after creation.
