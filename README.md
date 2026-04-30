<div align="center">

# 🧰 Nezikk's Skills

#### 我自己常用的一些 AI 技能，都放在这里

[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](./LICENSE)
[![Skills](https://img.shields.io/badge/Skills-8-10B981?style=for-the-badge)](#-skills)
[![Tests](https://img.shields.io/badge/Tests-unittest-F59E0B?style=for-the-badge)](#-测试)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-8B5CF6?style=for-the-badge)](https://agentskills.io)

![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-D97706?style=flat-square&logo=anthropic&logoColor=white)
![Codex](https://img.shields.io/badge/Codex-Skill-10B981?style=flat-square&logo=openai&logoColor=white)
![OpenCode](https://img.shields.io/badge/OpenCode-Skill-3B82F6?style=flat-square)
![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-8B5CF6?style=flat-square)

</div>

这些 skill 都是为我自己的工作流做的。能自动化的就自动化，能少问一次就少问一次，尽量把重复操作收进 Agent 的工具箱里。

- **Skills** — Agent 能直接加载的结构化指令集，遵循 [Agent Skills](https://agentskills.io) 开放标准
- **Automation** — 有些 skill 会调用仓库里的脚本或 CLI，把固定流程跑完整
- **Personal Workflow** — 以我本地的 Claude Code / Codex 使用习惯为主，开源出来方便复用和改造
- **Single Source** — Claude 和 Codex 可以各自保留入口目录，但软链接到这个仓库里的同一份 `SKILL.md`

---

## 🗂️ 仓库分层

这个仓库会同时管理两类 skill：

```text
Nezikk-s-skills/
  nskill/                         # 我自己写的 skill
  git-create/
  justdo/
  docx-creater/
  synbio-academic-translator/
  feishu-yang/

  external/                       # 从别人仓库下载或 fork 的 skill
    <github-owner>/
      <repo-name>/
        SOURCE.md                 # 来源、commit、license、本地修改记录
        <skill-name>/
          SKILL.md

  scripts/
    link-skill.sh                 # 同时链接到 Claude 和 Codex
```

核心规则：

- 自己写的 skill 放在仓库根目录，方便作为主展示内容维护
- 别人的 skill 放进 `external/<github-owner>/<repo-name>/`
- 每个外部来源仓库必须带 `SOURCE.md`，标注原始仓库、导入 commit、license 和本地修改情况
- Claude 和 Codex 各自保留默认 skill 目录，但目录项用软链接指向本仓库里的同一份 skill

这样修改一次 `SKILL.md`，Claude 和 Codex 读到的就是同一份内容。

---

## 📋 目录

### My Skills

| 名字 | 一句话 | 文件 |
|---|---|---|
| 🧩 [**nskill**](#-nskill) | 输入 `/nskill <name>`，自动创建同名 skill 文件夹并发布到这个仓库 | [SKILL.md](./nskill/SKILL.md) |
| 📦 [**skill-down**](#-skill-down) | 输入 `/skill-down npx skills add ... --skill ...`，把外部 skill 导入本仓库并同步到 Claude/Codex | [SKILL.md](./skill-down/SKILL.md) |
| 🐙 [**git-create**](#-git-create) | 输入 `/git-create`，把本地项目接到一个新的 GitHub 仓库 | [SKILL.md](./git-create/SKILL.md) |
| 📁 [**justdo**](#-justdo) | 输入 `/justdo <文件夹名字>`，在桌面项目目录下创建新文件夹 | [SKILL.md](./justdo/SKILL.md) |
| 🧬 [**synbio-academic-translator**](#-synbio-academic-translator) | 面向合成生物学论文的中英翻译、润色和术语统一 | [SKILL.md](./synbio-academic-translator/SKILL.md) |
| 📄 [**docx-creater**](#-docx-creater) | 生成、整理和格式化 `.docx` 文档 | [SKILL.md](./docx-creater/SKILL.md) |
| 📥 [**download-yang**](#-download-yang) | 从杨的飞书消息里列出近期文件，确认后下载 | [SKILL.md](./feishu-yang/download-yang/SKILL.md) |
| 📤 [**send-yang**](#-send-yang) | 把本地文件上传并发送到杨的飞书会话 | [SKILL.md](./feishu-yang/send-yang/SKILL.md) |

### External Skills

外部 skill 统一放在 [`external/`](./external/)，并在来源目录中保留 `SOURCE.md`。

| 名字 | 来源 | 文件 |
|---|---|---|
| 🧹 [**neat-freak**](./external/KKKKhazix/khazix-skills/neat-freak/SKILL.md) | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) | [SOURCE.md](./external/KKKKhazix/khazix-skills/SOURCE.md) |
| 🔭 [**hv-analysis**](./external/KKKKhazix/khazix-skills/hv-analysis/SKILL.md) | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) | [SOURCE.md](./external/KKKKhazix/khazix-skills/SOURCE.md) |
| ✍️ [**khazix-writer**](./external/KKKKhazix/khazix-skills/khazix-writer/SKILL.md) | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) | [SOURCE.md](./external/KKKKhazix/khazix-skills/SOURCE.md) |

---

## 📦 安装方式

推荐方式是把这个仓库作为唯一真实存储位置，然后把同一个 skill 同时软链接到 Codex 和 Claude：

```bash
./scripts/link-skill.sh nskill
./scripts/link-skill.sh synbio-academic-translator
```

脚本会创建：

```text
~/.agents/skills/<skill-name> -> /Users/saaaaa/Desktop/Nezikk-s-skills/<skill-name>
~/.claude/skills/<skill-name> -> /Users/saaaaa/Desktop/Nezikk-s-skills/<skill-name>
```

外部 skill 也一样：

```bash
./scripts/link-skill.sh external/KKKKhazix/khazix-skills/neat-freak
```

如果要把当前 Claude / Codex 里已经安装的非系统 skill 全部收进本仓库，并把两个入口目录改成软链接：

```bash
python3 scripts/sync_installed_skills.py        # dry-run
python3 scripts/sync_installed_skills.py --apply
```

脚本会跳过 Codex 系统内置的 `~/.codex/skills/.system/`，把同步前的入口备份到：

```text
/Users/saaaaa/Desktop/Nezikk-s-skills-entry-backups/
```

如果要手动软链接：

```bash
ln -s "/Users/saaaaa/Desktop/Nezikk-s-skills/nskill" "$HOME/.agents/skills/nskill"
ln -s "/Users/saaaaa/Desktop/Nezikk-s-skills/nskill" "$HOME/.claude/skills/nskill"
```

`download-yang` 和 `send-yang` 依赖共享 CLI，需要和 `feishu-yang/feishu-yang-automation` 一起复制：

```bash
./scripts/link-skill.sh feishu-yang/download-yang
./scripts/link-skill.sh feishu-yang/send-yang
```

---

## ✨ Skills

<a id="-skills"></a>

<table>
<tr><td>

### 🧩 nskill

> *"想加一个新 skill，就让 Agent 自己把文件夹、模板、测试和发布流程走完。"*

输入 `/nskill <name>` 后，它会在 `Nezikk-s-skills` 仓库里创建同名 skill 文件夹，并写入最小可用的 `SKILL.md` 模板。

**适合**

- 想快速开一个新 skill
- 不想手动记 `SKILL.md` frontmatter 格式
- 创建完以后顺手跑测试、提交、推送

**它会做什么**

- 解析 `/nskill` 后面的目标名称
- 防止覆盖已有 skill 文件夹
- 创建最小 `SKILL.md`
- 运行仓库测试
- `git commit` 后推送到远端

→ [SKILL.md](./nskill/SKILL.md)

</td></tr>
</table>

<table>
<tr><td>

### 📦 skill-down

> *"别人仓库里的 skill 不直接散装到各个 CLI，而是先进入我的仓库，标注来源，再统一软链接出去。"*

输入 `/skill-down` 后面接一段 `npx skills add ... --skill ...` 命令，它会把外部 skill 导入这个仓库的 `external/` 分层目录，并同步给 Claude 和 Codex。

**适合**

- 下载别人开源的 skill，但想统一放进自己的 Git 仓库管理
- 保留原始仓库、导入 commit、license 和本地修改记录
- 避免 Claude 和 Codex 各自复制一份，导致以后内容分叉

**典型用法**

```bash
/skill-down npx skills add https://github.com/op7418/guizang-ppt-skill --skill guizang-ppt-skill
```

**它会做什么**

- clone 外部 GitHub 仓库
- 找到指定 skill 的 `SKILL.md`
- 保存到 `external/<github-owner>/<repo-name>/<skill-name>/`
- 自动生成 `SOURCE.md`
- 软链接到 `~/.agents/skills/` 和 `~/.claude/skills/`

→ [SKILL.md](./skill-down/SKILL.md) · [import_external_skill.py](./scripts/import_external_skill.py)

</td></tr>
</table>

<table>
<tr><td>

### 🐙 git-create

> *"本地项目已经写好了，剩下的 GitHub 建仓库、接 remote、推 main，就别手动点来点去了。"*

输入 `/git-create` 后，它会引导确认本地项目目录和 GitHub 仓库名，然后用 GitHub CLI 创建仓库并连接本地 Git remote。

**适合**

- 本地已经有项目文件夹，但还没有 GitHub 仓库
- 想默认创建 private 仓库
- 想避免误覆盖已有 remote

**它会特别小心的地方**

- 创建仓库前必须确认目录和仓库名
- 默认 private，除非你明确要求 public
- 已有 remote 时不会直接覆盖
- 推送失败会停下来报告错误

→ [SKILL.md](./git-create/SKILL.md)

</td></tr>
</table>

<table>
<tr><td>

### 📁 justdo

> *"想到一个项目名，直接 `/justdo`，文件夹就落到固定的项目目录里。"*

输入 `/justdo <文件夹名字>` 后，它会在 `/Users/saaaaa/Desktop/项目` 下面创建对应文件夹。

**适合**

- 快速开一个新的本地项目目录
- 保持项目都集中在同一个桌面目录
- 避免因为路径写错创建到奇怪的位置

**安全规则**

- 不允许创建到项目目录之外
- 文件夹已存在时会停下，不覆盖、不合并、不重命名
- 空名称、`/`、`.`、`..` 这类不合法名称会被拒绝

→ [SKILL.md](./justdo/SKILL.md)

</td></tr>
</table>

<table>
<tr><td>

### 🧬 synbio-academic-translator

> *"中文实验和论文思路可以直说，但英文稿要像合成生物学论文里该有的样子。"*

这是面向合成生物学、代谢工程、分子生物学和微生物工程写作的中英学术翻译 skill。默认先忠实翻译，再按论文表达重写，并统一术语。

**适合**

- 中文论文段落翻译成英文
- 摘要、引言、结果、方法、讨论、图注润色
- 合成生物学相关术语统一
- `.docx` 文稿段落提取后翻译

**不做什么**

- 不替你编数据
- 不把相关性写成机制结论
- 不擅自扩大战果或改写实验事实

**包含**

- 合成生物学术语参考表
- `.docx` 段落提取脚本
- 面向工程型生物论文的表达规则

→ [SKILL.md](./synbio-academic-translator/SKILL.md) · [terminology.md](./synbio-academic-translator/references/terminology.md) · [extract_docx_paragraphs.py](./synbio-academic-translator/scripts/extract_docx_paragraphs.py)

</td></tr>
</table>

<table>
<tr><td>

### 📄 docx-creater

> *"内容写完以后，剩下的标题、编号、行距、字体和 Word 文件生成，让 Agent 按规则收尾。"*

这个 skill 用来创建、整理和格式化 `.docx` 文档。它会先确认格式要求，再生成或更新 Word 文件。

**适合**

- 把已有内容导出成 `.docx`
- 按指定格式整理标题、正文、编号和行距
- 处理论文里基因斜体、蛋白正体、上下标等细节
- 用 `/docx-create` 触发 Word 文档生成流程

**它会先问清楚**

- 输出文件名和目录
- 标题、字号、字体、行距、段距
- 是否覆盖已有文件
- 是否需要保留原文档结构

→ [SKILL.md](./docx-creater/SKILL.md)

</td></tr>
</table>

<table>
<tr><td>

### 📥 download-yang

> *"先列出杨最近发过来的文件，选中哪个再下哪个，不靠猜 message_id。"*

这个 skill 会调用共享飞书 CLI，列出杨近期发来的文件候选项，让你按序号确认后再下载。

**适合**

- 从固定飞书会话里找最近文件
- 下载前先看文件名、消息 ID 和时间
- 避免误下不相关文件

**需要环境变量**

- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `FEISHU_YANG_CHAT_ID`

它依赖共享脚本：[`feishu_yang_cli.py`](./feishu-yang/feishu-yang-automation/scripts/feishu_yang_cli.py)

→ [SKILL.md](./feishu-yang/download-yang/SKILL.md)

</td></tr>
</table>

<table>
<tr><td>

### 📤 send-yang

> *"给出本地文件路径，它会通过共享 CLI 上传并发送到杨的飞书会话。"*

这个 skill 用来把本地文件发送到配置好的杨飞书聊天里。没有路径时会先问路径，路径不存在时不会继续发送。

**适合**

- 把本地文档、结果文件、资料包发到固定飞书会话
- 避免重复手动打开飞书上传
- 复用同一套飞书 API 配置

**需要环境变量**

- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `FEISHU_YANG_CHAT_ID`

它依赖共享脚本：[`feishu_yang_cli.py`](./feishu-yang/feishu-yang-automation/scripts/feishu_yang_cli.py)

→ [SKILL.md](./feishu-yang/send-yang/SKILL.md)

</td></tr>
</table>

---

## 🧪 测试

这个仓库带了一些针对脚本和 skill 行为的单元测试：

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

当前覆盖：

- `tests/test_nskill_skill.py`
- `tests/test_git_create_skill.py`
- `tests/test_justdo_skill.py`
- `tests/test_extract_docx_paragraphs.py`
- `tests/test_feishu_yang_cli.py`

---

## 🌟 关于

这是我的个人 AI skill 仓库。它不追求做成通用平台，更像是把我每天真的会用到的固定动作整理成可复用的工具。

如果你要直接用，建议先读对应的 `SKILL.md`，尤其是带本地路径、飞书环境变量、GitHub CLI 的 skill。很多规则是按我的本机工作流写的，你可以 fork 后改成自己的路径和习惯。

外部 skill 会保留原始来源记录；如果我做了本地修改，也会写在对应的 `SOURCE.md` 里，避免混淆原作者版本和本仓库版本。

---

<div align="center">

[MIT License](./LICENSE) · 自由使用 / 修改 / 再分发

Made by [@SSaaaa3232](https://github.com/SSaaaa3232)

</div>
