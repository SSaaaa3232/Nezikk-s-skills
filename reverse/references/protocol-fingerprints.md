# 协议指纹库

通过 URL 模式和请求/响应特征快速识别目标使用的认证和通信协议。

**重要原则：先观察，后匹配。** 不要强行将目标套入已知指纹——如果找不到匹配，从零构建指纹。

---

## 通用识别方法论

当目标不在已知指纹库中时，按以下步骤从零识别：

### Step 1: URL 模式分类

观察 HAR/Network 中的所有 URL，按以下维度分类：

| 维度 | 观察点 | 示例 |
|------|--------|------|
| 路径结构 | `/api/v1/` vs `/trpc/` vs `/gateway/` | REST vs RPC vs 网关 |
| 参数风格 | `?batch=1` vs `?input=` vs 路径参数 `/user/123` | tRPC vs 自定义 RPC vs RESTful |
| 扩展名 | `.do` `.action` `.json` `.php` 无扩展名 | Java Struts / Spring / PHP / SPA |
| 子域名 | `api.` `gateway.` `m.` `h5.` | API 网关 / 移动端 / H5 |
| 版本号 | `/v1/` `/v2/` 或 URL 中无版本 | API 版本策略 |

### Step 2: 请求体格式分类

| 格式 | 特征 | 常见于 |
|------|------|--------|
| JSON | `Content-Type: application/json` | SPA、REST API |
| Form URL-Encoded | `key1=val1&key2=val2` | 传统 Web、OAuth |
| Multipart | `boundary=...` + 二进制数据 | 文件上传 |
| Protobuf/Binary | `Content-Type: application/x-protobuf` 或二进制 body | 移动端、高性能后端 |
| 加密体 | body 是单一 base64 字符串或乱码 | 自定义加密协议 |
| Query String 签名 | URL 末尾带 `&sign=xxx&ts=xxx` | 防篡改签名 |

### Step 3: 认证方式识别

遍历所有请求，提取认证相关的 Header 和 Cookie：

```
常见认证头:
  Authorization: Bearer <token>          → JWT 或 OAuth2
  Authorization: Basic <base64>           → HTTP Basic Auth
  X-Auth-Token: <token>                   → 自定义 token
  X-Signature: <hex>                      → HMAC 签名
  X-Request-Id / X-Trace-Id              → 链路追踪（非认证）

常见 Cookie:
  session=... / SESSION=...               → 服务端 Session
  jwt=... / token=...                     → JWT in Cookie
  JSESSIONID=...                          → Java Tomcat Session
  PHPSESSID=...                           → PHP Session
  .AspNetCore.Cookies=...                 → ASP.NET Session
```

### Step 4: 签名/加密模式识别

观察请求中的**重复出现的固定字段**：

```
如果多个请求都带:
  sign=xxx 或 signature=xxx              → 签名校验
  timestamp=xxx + nonce=xxx + sign=xxx   → 防重放签名
  token=xxx + encrypt=xxx                → 双层认证
  csrf=xxx / _csrf=xxx                   → CSRF 保护
  captcha=xxx / verify=xxx               → 验证码/人机校验
```

### Step 5: 构建自定义协议指纹

如果以上步骤都无法匹配已知指纹，输出：

```
## 自定义协议指纹

### URL 模式
- 基路径: /api/v2/
- 特征: 所有 POST 带 ?_t=<timestamp>&_s=<sign>

### 请求体格式
- Content-Type: application/x-www-form-urlencoded
- 所有请求包含: userId, timestamp, sign, data(可变的加密体)

### 认证流程
1. GET /api/v2/user/init → 返回 sessionId + publicKey
2. 后续请求: { data: RSA_encrypt(payload, publicKey), sign: MD5(sorted_params + salt) }

### 推测协议类型
- 自定义 RPC + RSA 加密 + MD5 签名
- 类似: 网易云 weapi / 拼多多 anti-content
```

---

## 已知认证协议

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
  - callback的body是form-urlencoded (chain, message, signature, csrfToken, callbackUrl)
```

### SIWE (Sign-In with Ethereum)

```
URL 模式:
  GET/POST /api/siwe/nonce     → nonce
  POST /api/siwe/verify        → session

请求特征:
  - 签名消息包含: address, chainId, nonce, expiration, domain
  - 标准SIWE格式: "${domain} wants you to sign in..."
```

### 自定义钱包登录

```
请求特征:
  - 签名消息格式为自定义模板（可能登录和业务使用不同格式）
  - 识别方法: 搜索 signMessage → 提取模板字符串 → 对比不同流程的格式差异
```

### JWT Token 认证

```
请求头:
  Authorization: Bearer eyJhbGciOi...

特征:
  - token 以 eyJ 开头（base64url 编码的 {"alg"...}）
  - 三段式结构: header.payload.signature（. 分隔）
  - payload 解码后可看到: sub, iat, exp, aud 等字段

识别后的操作:
  1. 解码 payload → 了解 token 包含哪些字段
  2. 检查 exp → 判断 token 有效期
  3. 尝试修改 alg: none → 测试算法混淆漏洞
```

### OAuth / OIDC

```
URL 模式:
  GET  /api/auth/signin?callbackUrl=...  → 重定向到 Google/GitHub/...
  POST /api/auth/callback/oauth-provider → Set-Cookie: session
```

### 手机验证码登录

```
URL 模式:
  POST /api/sms/send          → 发送验证码（依赖手机号+可能的人机校验）
  POST /api/sms/verify        → 验证码校验 → 返回 token

特征:
  - 请求体通常包含: phone, captcha(图形验证码), smsCode
  - 可能有频率限制: 同一手机号 N 秒内只能发一次
```

### 第三方登录（微信/支付宝/微博）

```
URL 模式:
  GET  /api/oauth/wechat/authorize → 302 重定向到 open.weixin.qq.com
  GET  /api/oauth/wechat/callback?code=xxx → 服务端用 code 换 openid + token

特征:
  - 回调 URL 带 ?code= 参数（OAuth2 authorization code flow）
  - 返回: openid, unionid, access_token
```

---

## 已知通信协议

### tRPC

```
URL 模式:
  /trpc/<namespace>.<procedure>?batch=1    (batch模式)
  /trpc/<namespace>.<procedure>?input=...   (vanilla模式)

请求体特征 (batch模式):
  {
    "0": { "json": { ... } }    ← JSON-RPC风格，key为数字索引
  }

响应体特征 (batch模式):
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
  - 标准HTTP method (GET/POST/PUT/DELETE)
  - 响应通常为JSON或HTML
```

### JSON-RPC

```
URL 模式:
  /jsonrpc
  /api/rpc

请求体特征:
  { "jsonrpc": "2.0", "method": "...", "params": {...}, "id": 1 }
```

### gRPC-Web

```
URL 模式:
  /<package>.<Service>/<Method>

请求特征:
  - Content-Type: application/grpc-web+proto
  - 二进制body（base64编码传输）
```

### SOAP / XML-RPC

```
URL 模式:
  /services/<Service> 或 .wsdl结尾

请求体特征:
  Content-Type: text/xml
  <soap:Envelope>...</soap:Envelope>
```

### OpenAI 兼容 API

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

## 常见防爬/风控机制

### 基础反爬

```
特征:
  - 缺少User-Agent → 400
  - 缺少Referer → 403
  - 特定Header缺失 → 异常响应
```

### 参数签名（防篡改）

```
特征: URL或body中带 sign/token 参数
常见算法:
  - MD5(sorted_params + salt)
  - HMAC-SHA256(params, secret)
  - AES(body, key)

识别方法:
  1. 在Sources搜索 sign / signature / token 的构造逻辑
  2. 搜索 MD5 / sha256 / hmac / encrypt
  3. 找到salt/secret的来源（硬编码 or 服务端下发）
```

### 设备指纹/浏览器指纹

```
特征: 请求包含 canvasHash / webglFingerprint / deviceId 等字段
识别: 搜索 fingerprint / canvas / webgl / navigator 在JS中的使用
```

### 验证码/人机校验

```
特征:
  - 请求前触发图形验证码（滑块/点选/旋转）
  - 请求参数含 captchaToken / ticket / randstr
  - 常见服务商: 极验(geetest)、腾讯防水墙、Cloudflare Turnstile
```

### 加密通信体

```
特征: body 是单个加密字符串而非 JSON/Form
常见形式:
  - AES-encrypted JSON → base64
  - RSA-encrypted payload
  - 自定义序列化+加密

识别方法:
  1. 在Sources搜索 encrypt / CryptoJS / forge / JSEncrypt
  2. 找到加密入口函数和密钥
  3. 还原: 解密 → 结构化数据
```

---

## 自定义认证头

如果发现非标准的自定义认证头（如 `X-ainft-chat-auth`）：

1. 在Sources搜索该header名称
2. 追踪其值的构造方式（可能为XOR + base64或AES加密）
3. 回溯key/secret的来源（硬编码 or 动态生成）

常见编码组合：
- `XOR(payload, key) → base64`
- `AES.encrypt(payload, key) → base64`
- `JWT token`（注意 `.` 分隔的三段式结构）
- `HMAC(fields, secret) → hex`
