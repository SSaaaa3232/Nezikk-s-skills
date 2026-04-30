# External Skills

这里放从其他仓库下载或 fork 过来的第三方 skills。

## Directory Rule

按来源仓库分层：

```text
external/
  <github-owner>/
    <repo-name>/
      SOURCE.md
      <skill-name>/
        SKILL.md
```

例子：

```text
external/
  KKKKhazix/
    khazix-skills/
      SOURCE.md
      neat-freak/
        SKILL.md
```

## Source Metadata

每个外部来源仓库都要保留一个 `SOURCE.md`，记录：

- 原始仓库地址
- 导入时间
- 导入 commit
- license
- 是否做过本地修改

可以复制 [`SOURCE.template.md`](./SOURCE.template.md) 作为模板。

## Linking

不要把同一个 skill 复制到 Claude 和 Codex 两份目录里。统一保留在这个仓库，然后软链接：

```bash
./scripts/link-skill.sh external/KKKKhazix/khazix-skills/neat-freak
```

脚本会创建：

```text
~/.agents/skills/neat-freak -> /Users/saaaaa/Desktop/Nezikk-s-skills/external/KKKKhazix/khazix-skills/neat-freak
~/.claude/skills/neat-freak -> /Users/saaaaa/Desktop/Nezikk-s-skills/external/KKKKhazix/khazix-skills/neat-freak
```
