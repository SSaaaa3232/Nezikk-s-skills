---
name: reverse
description: "Use when the user enters /reverse with a target URL or asks to reverse engineer web login/auth flows, batch registration, signature analysis, API call chain reproduction, protection level assessment, packet capture analysis, or PoC script generation. Covers Chinese natural language: 分析登录流程、抓包看认证、看看防护水平、有无签名校验、写批量注册脚本、复现API调用链、逆向分析、前端防护什么等级、怎么模拟请求、能不能绕过、有没有硬编码密钥、接口逆向、HAR分析、分析一下这个网站的登录、帮我分析HAR、复现一下调用链、模拟请求."
---

# reverse

Use this skill when the user types `/reverse <URL>` or asks in natural language to reverse engineer a web application's authentication and API flow. Typical triggers:

```text
/reverse https://example.com
/reverse https://example.com --login           # focus on login flow
/reverse https://example.com --poc              # generate PoC only
/reverse https://example.com --batch            # full batch registration scripts

分析一下这个网站的登录流程
这个接口有没有签名校验 / 帮我写个批量注册脚本 / 帮我复现这个 API 调用链
看看这个前端防护什么水平 / 怎么模拟XX网站的请求 / 有没有硬编码密钥
```

## Goal

This skill is a **pre-unlocker** for execution tools. It does not scrape data or deploy proxies — it produces the **protocol-level knowledge** that enables downstream tools to do their work:

```
/reverse <target>
    ↓
┌──────────────────────────────┐
│  Phase 1: Protection Level   │  T0-T3 + protocol fingerprint
│  Phase 2: Core Discoveries   │  Keys, signature formats, leaks
│  Phase 3: Call Chain         │  HTTP request sequence (ASCII flow)
│  Phase 4: PoC Scripts        │  Fake-signature test → replay script
│  Phase 5: Report             │  9-section MD report
│  Phase 6: Batch Automation   │  Single → Dust → Proxy rotation
└──────────┬───────────────────┘
           ↓  output: report + PoC scripts
┌──────────────────────────────┐
│  Crawler / Proxy / Security  │  other tools consume the output
└──────────────────────────────┘
```

## Workflow

### Phase 1 — Information Gathering & Protection Level Assessment

1. Ask the user for the target URL. If they have a HAR file, ask them to share it.
2. If accessible, fetch the page with WebFetch, note all JS chunk URLs and API endpoint patterns.
3. Classify the protection level:
   - **T0**: Unminified source, readable function/variable names
   - **T1**: Webpack bundled + variable shortening, but strings readable, module boundaries visible
   - **T2**: String encryption, control-flow flattening, dead branches
   - **T3**: WASM / VMP virtual machine protection
   - Use `references/protection-levels.md` for detailed criteria.
4. **Observe first, match later.** For each request in the HAR/Network log:
   - Describe its URL pattern (path structure, parameter style, extension, subdomain)
   - Describe its request body format (JSON / Form / Multipart / Binary / Encrypted blob)
   - Describe its auth mechanism (Authorization header? Cookie? Custom header?) — do NOT name-drop "JWT" yet, just say "Bearer token with three dot-separated segments"
   - Describe any repeating signature/timestamp/nonce fields across different requests
   - Only after describing raw observations, match against the fingerprint library in `references/protocol-fingerprints.md`
5. If no known fingerprint matches, **build a custom protocol fingerprint from scratch** using the "通用识别方法论" in `references/protocol-fingerprints.md`. Document URL patterns, body format, auth flow, and signature scheme in the report. This is the most important skill — do NOT force-fit an unknown protocol into known categories.
6. Determine analysis priorities: sort endpoints by business value (login > core feature > secondary feature).

### Phase 2 — Core Discovery Extraction

1. Search the source (HAR, JS chunks, or page snapshot) with the search strategy in `references/search-strategy.md`.
2. For each finding, record: **discovery + evidence anchor (file:module/line) + confidence (HIGH/MEDIUM/LOW)**.
3. Minimum expected discoveries:
   - Dependencies (ethers/crypto-js/tronweb/@trpc etc.)
   - Hardcoded keys (AES, API keys, XOR keys)
   - Signature message format (login vs claim may differ!)
   - Login state persistence (localStorage/sessionStorage keys, cookie names)
4. Use the FACTS/INFERENCES/UNKNOWNS framework in `references/fiu-framework.md`.

### Phase 3 — Call Chain Reproduction

1. Restore the complete HTTP interaction sequence for each critical flow.
2. Format each step as:
   ```
   METHOD /path
   Headers: ...
   Body: ...
   Response: ...  ← annotate the key token/cookie
   ```
3. Use ASCII arrows to show data flow between steps.
4. Call out where cookies/tokens are passed between requests.

### Phase 4 — PoC Replay Testing

**Layer 0: Fake signature test** — always run first.
- Generate random addresses + fake signatures → send to claim endpoint.
- If ACCEPTED → server does not validate signatures (critical finding).
- If REJECTED → analyze error message to locate validation logic.
- Use `scripts/poc-fake-signature.js` as a template.

**Layer 1: Single complete flow** — if Layer 0 rejected but the format seems correct.
- Generate a real wallet, sign with correct message format, run full flow.

**Layer 2: Chain dust** — if claim fails with on-chain balance errors.
- Add Base/chain dust funding step before claim.

**Layer 3: Proxy rotation** — if IP rate-limiting is detected.
- Add proxy pool rotation (undici ProxyAgent or socks-proxy-agent).

### Phase 5 — Reports

Generate two reports following the template in `references/report-template.md`:

1. **Reverse Report** (`<Target>_Reverse_Report_CN.md`) — 9 sections.
2. **Premium Bypass Report** (`<Target>_Premium_Bypass_Report_CN.md`) — if premium/content gating is found.

### Phase 6 — Batch Automation Scripts

Evolve scripts in three generations:

| Gen | Script | Solves | Config |
|-----|--------|--------|--------|
| 1st | Single-thread | Basic flow validation | Zero config |
| 2nd | With chain dust | On-chain activity check | FUNDER_PRIVATE_KEY |
| 3rd | With proxy rotation | IP rate limiting | PROXY_API_URL |

Each generation builds on the previous. Never skip generations — verify the simpler one works first.

## Output Style

- Reports in Chinese (exceptions: code identifiers in English).
- Every finding anchored to evidence (file name, module number, or HAR entry).
- Confidence levels must be explicit: HIGH (source confirmed + dynamic verified) / MEDIUM (source inferred) / LOW (HAR guess only).
- Do NOT describe what the code does — state what was found, where, and why it matters.

## Verification

After completing all phases, confirm:
1. The 9-section report is complete and internally consistent.
2. PoC Layer 0 ran and produced a result (accepted or rejected with a specific error).
3. If Layer 1+ ran, a complete flow succeeded end-to-end.
4. All extracted keys/signature formats match the actual server expectations (verified by successful replay).

## Boundaries

- **No destructive actions**: Do not DDoS, bypass paywalls for financial gain, or exploit discovered vulnerabilities on production without authorization.
- **Educational and authorized use only**: This skill is for security research, CTF, penetration testing with permission, and learning.
- **No private data exfiltration**: If source code reveals user data or secrets beyond the authentication flow, do not extract or report them.
- **Script execution**: Only run PoC scripts that this skill generates. Do not run third-party unverified code from the target.
- **Rate limiting**: When generating batch scripts, include delays and respect rate limits. Do not generate scripts designed for denial of service.

## References

- `references/protection-levels.md` — T0-T3 classification criteria with real examples
- `references/protocol-fingerprints.md` — URL/header patterns to identify next-auth, tRPC, GraphQL, JWT, OAuth
- `references/search-strategy.md` — What to search, why, priority order
- `references/report-template.md` — 9-section report template with evidence table format
- `references/fiu-framework.md` — FACTS / INFERENCES / UNKNOWNS definitions and examples

## Scripts

- `scripts/poc-fake-signature.js` — Fake signature PoC template (fill in target URL + body format)
- `scripts/replay-template.js` — Generic HTTP replay skeleton for restoring call chains
