---
name: agent-browser
description: "Automates browser interactions for web testing, form filling, screenshots, and data extraction. Use when: (1) Need to automate web testing, (2) Fill out forms programmatically, (3) Extract data from websites, (4) Take screenshots of web pages, (5) Record browser interactions."
---

# agent-browser 工具完整文档

浏览器自动化工具,用于自动化浏览器交互,支持网页测试、表单填写、截图和数据提取。

## 核心工作流

1. **导航**: `agent-browser open <url>`
2. **快照**: `agent-browser snapshot -i` (获取可交互元素及引用如 @e1, @e2)
3. **交互**: 使用快照中的引用进行操作
4. **重快照**: 导航后或 DOM 重大变化时重新快照

## 主要命令类别

| 类别 | 功能 |
|------|------|
| **导航** | open, back, forward, reload, close |
| **快照** | snapshot, snapshot -i, snapshot -c |
| **交互** | click, fill, type, press, select, scroll, drag, upload |
| **获取信息** | get text/html/value/attr, get title/url/count/box/styles |
| **状态检查** | is visible/enabled/checked |
| **截图/PDF** | screenshot, screenshot --full, pdf |
| **录制** | record start, record stop |
| **等待** | wait element/text/url/load/fn |
| **鼠标控制** | mouse move/down/up/wheel |
| **语义定位** | find role/text/label/placeholder/alt/title/testid |
| **浏览器设置** | set viewport/device/geo/offline/headers/credentials/media |
| **网络** | network route/unroute/requests |
| **标签页/窗口** | tab new/close/switch, window new |
| **调试** | console, errors, highlight, trace, record |

## 常用示例

```bash
# 打开网页并交互
agent-browser open https://example.com/form
agent-browser snapshot -i
agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password"
agent-browser click @e3

# 带状态的认证
agent-browser state save auth.json  # 保存登录状态
agent-browser state load auth.json   # 加载登录状态
```

## 全局选项

- `--session <name>`: 隔离浏览器会话
- `--json`: JSON 输出
- `--headed`: 显示浏览器窗口
- `--proxy <url>`: 代理服务器
- `--cdp <port>`: Chrome DevTools 协议连接

## 环境变量

- `AGENT_BROWSER_SESSION`: 默认会话名
- `AGENT_BROWSER_EXECUTABLE_PATH`: 自定义浏览器路径
- `AGENT_BROWSER_PROVIDER`: 云浏览器提供商
