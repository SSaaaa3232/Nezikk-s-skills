---
name: git-create
description: Use when the user enters /git-create to create a GitHub repository for a local project folder and connect that folder as the local Git repository
---

# git-create

Use this skill when the user enters `/git-create` and wants a local project folder connected to a newly created GitHub repository.

## Workflow

1. 确认本地项目文件夹。
   - Ask the user which folder should be set as the GitHub local repository.
   - If the current working directory appears to be the target project, still ask the user to confirm that exact path.
   - Do not run `git init`, create a repository, or change remotes until the user confirms the folder.

2. 确认 GitHub 仓库名。
   - 默认使用项目文件夹名 as the suggested repository name.
   - Ask the user to confirm or edit the GitHub repository name before creation.
   - Default visibility is private: 默认创建 private.
   - If the user explicitly asks for a public repository, use public visibility instead.

3. Check required tools and local Git state.
   - Run `gh auth status` and stop with the exact error if GitHub CLI is not authenticated.
   - Run `git status --short --branch` in the confirmed folder.
   - If the folder is not a Git repository, run `git init` there.
   - If the repository has no commits, create an initial commit after reviewing `git status --short`.

4. Handle existing remotes safely.
   - Run `git remote -v`.
   - If there is an 已有 remote, report it and 让用户确认 whether to keep it, add a different remote name, or replace it.
   - 不要覆盖 an existing `origin` unless the user explicitly approves replacing it.

5. Create the GitHub repository and connect it to the local folder.
   - Use GitHub CLI from the confirmed project folder:

```bash
gh repo create <repo-name> --private --source . --remote origin
```

   - For a public repository, use:

```bash
gh repo create <repo-name> --public --source . --remote origin
```

   - If the local default branch is not `main`, either rename it with `git branch -M main` or explain the current branch and ask before changing it.

6. Commit and push.
   - Run `git status --short`.
   - If there are uncommitted project files, ask before staging broad changes.
   - For a new repository with no commits, run:

```bash
git add .
git commit -m "Initial commit"
git push -u origin main
```

   - For an existing local repository with commits, push the confirmed branch:

```bash
git push -u origin main
```

7. Report the result.
   - GitHub repository URL.
   - Confirmed local folder path.
   - Remote name and URL.
   - Current branch.
   - Push result.

## Safety Rules

- Never create the GitHub repository until the user confirms both the local folder and repository name.
- Never overwrite an existing remote without explicit user approval.
- Do not make a public repository unless the user explicitly requested public visibility.
- If `gh repo create` or `git push -u origin main` fails, stop and report the command and error output.
