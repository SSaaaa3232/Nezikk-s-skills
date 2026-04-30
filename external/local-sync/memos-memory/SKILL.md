---
name: memos-memory
description: MemOS 记忆系统集成 - 用于存储和检索长期记忆、经验总结、技能进化。当用户提到"记住这个"、"我之前"、"搜索记忆"、"保存经验"、"学到了"等场景时触发。此 Skill 让 Claude 具备跨会话的记忆能力。
---

# MemOS Memory Skill

Claude Code 的 MemOS 记忆系统集成，实现长期记忆存储和检索。

## 核心功能

1. **记忆存储** - 将重要信息保存到 MemOS
2. **记忆检索** - 根据上下文搜索相关记忆
3. **经验总结** - 自动复盘并保存关键经验

## 配置要求

MemOS 服务必须运行在 `http://localhost:8000`。首次使用需要配置用户 ID。

## 使用方法

### 存储记忆
当用户说"记住..."时，调用存储脚本：
```bash
python3 ~/.claude/skills/memos-memory/scripts/store_memory.py --content "用户偏好使用中文交流" --user-id "claude-code-user"
```

### 搜索记忆
当用户说"我之前..."或需要查找历史信息时：
```bash
python3 ~/.claude/skills/memos-memory/scripts/search_memory.py --query "用户的交流偏好" --user-id "claude-code-user"
```

### 查看所有记忆
```bash
python3 ~/.claude/skills/memos-memory/scripts/search_memory.py --query "" --user-id "claude-code-user" --list-all
```

## 典型使用场景

1. **用户偏好** - "记住我喜欢用中文交流" → 存储到记忆
2. **项目上下文** - "这个项目使用 React" → 作为项目记忆存储
3. **经验总结** - "以后遇到 X 应该用 Y 方法" → 存储经验
4. **上下文恢复** - "我之前那个项目是怎么处理的？" → 搜索记忆

## 技术细节

- API Base: `http://localhost:8000`
- 存储端点: `POST /product/add`
- 搜索端点: `POST /product/search`
- 数据格式: JSON
- 用户隔离: 通过 user_id 字段

## 注意事项

- 仅存储用户明确要求记住的内容
- 搜索时优先检索最近的记忆
- 记忆会自动去重和摘要
