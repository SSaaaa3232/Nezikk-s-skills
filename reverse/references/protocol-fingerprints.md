# 协议指纹库

通过 URL 模式和请求/响应特征快速识别目标使用的认证和通信协议。

## 认证协议

### next-auth (Auth.js)

```
URL 模式:
  GET  /api/auth/csrf          → { "csrfToken": "xxx" }
  POST /api/auth/callback/*    → Set-Cookie: session-token
  GET  /api/auth/session       → { "user": {...} }
  POST /api/auth/signout

响应特征:
  - Set-Cookie: next-auth.csrf-token
  - Set-Cookie: next-auth.session-token (或 session-token)
  - callback 的 body 是 form-urlencoded (chain, message, signature, csrfToken, callbackUrl)
```

### SIWE (Sign-In with Ethereum)

```
URL 模式:
  GET/POST /api/siwe/nonce     → nonce
  POST /api/siwe/verify        → session

请求特征:
  - 签名消息包含: address, chainId, nonce, expiration, domain
  - 标准 SIWE 格式: "${domain} wants you to sign in..."
```

### 自定义钱包登录（本项目类似 SIWE 但非标准）

```
请求特征:
  - 签名消息格式为自定义模板（如 "Welcome to BANK OF AI !\n..."）
  - 可能有多个签名消息格式（登录用一套、claim 用另一套）
```

### OAuth / OIDC

```
URL 模式:
  GET  /api/auth/signin?callbackUrl=...  → 重定向到 Google/GitHub/...
  POST /api/auth/callback/oauth-provider  → Set-Cookie: session
```

---

## 通信协议

### tRPC

```
URL 模式:
  /trpc/<namespace>.<procedure>?batch=1    (batch 模式)
  /trpc/<namespace>.<procedure>?input=...   (vanilla 模式)

请求体特征 (batch 模式):
  {
    "0": { "json": { ... } }    ← JSON-RPC 风格，key 为数字索引
  }

响应体特征 (batch 模式):
  [{ "result": { "data": { "json": { ... } } } }]
```

### GraphQL

```
URL 模式:
  /graphql
  /api/graphql

请求体特征:
  { "query": "...", "variables": {...}, "operationName": "..." }

自检: POST /graphql { "query": "{ __schema { types { name } } }" }
```

### REST

```
URL 模式:
  /api/v1/resource
  /api/resource/:id

特征:
  - 标准 HTTP method (GET/POST/PUT/DELETE)
  - 响应通常为 JSON 或 HTML
```

### OpenAI 兼容

```
URL 模式:
  /v1/chat/completions
  /api/v1/chat/completions

请求头:
  Authorization: Bearer sk-...

请求体:
  { "model": "...", "messages": [...] }
```

---

## 自定义认证头

如果发现非标准的自定义认证头（如 `X-ainft-chat-auth`）：

1. 在 Sources 搜索该 header 名称
2. 追踪其值的构造方式（可能为 XOR + base64 或 AES 加密）
3. 回溯 key/secret 的来源

常见编码组合：
- `XOR(payload, key) → base64`
- `AES.encrypt(payload, key) → base64`
- `JWT token`（注意 . 分隔的三段式结构）
