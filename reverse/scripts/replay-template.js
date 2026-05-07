/**
 * 通用 HTTP 重放骨架
 *
 * 填入从 HAR/抓包还原的请求序列，快速验证调用链。
 * 每步自动打印请求/响应摘要，方便调试。
 *
 * 使用方法:
 *   1. 填入每个 step 的 URL / method / headers / body
 *   2. 填入 cookie/extract 逻辑
 *   3. node replay-template.js
 */

// ============================================================
// [REQUIRED] 填入目标 BASE URL
// ============================================================
const BASE_URL = 'https://CHANGE_ME';

// ============================================================
// [REQUIRED] 每个 step 是一个 async 函数，输入 context，返回更新后的 context
// ============================================================

async function step_getCsrfToken(ctx) {
  const res = await fetch(`${BASE_URL}/api/auth/csrf`, {
    headers: { 'Accept': 'application/json' }
  });
  const data = await res.json();
  ctx.csrfToken = data.csrfToken;
  ctx.csrfCookies = res.headers.getSetCookie?.() || [];
  console.log(`[CSRF] token: ${ctx.csrfToken?.slice(0, 20)}...`);
  return ctx;
}

async function step_login(ctx) {
  const formData = new URLSearchParams({
    chain: 'eth',
    message: ctx.loginMessage,
    signature: ctx.loginSignature,
    csrfToken: ctx.csrfToken,
    callbackUrl: `${BASE_URL}/chat`
  });

  const cookieHeader = ctx.csrfCookies.map(c => c.split(';')[0]).join('; ');

  const res = await fetch(`${BASE_URL}/api/auth/callback/metamask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Cookie': cookieHeader
    },
    body: formData.toString()
  });

  const setCookies = res.headers.getSetCookie?.() || [];
  ctx.sessionCookies = setCookies.map(c => c.split(';')[0]).join('; ');

  const hasSession = setCookies.some(c => c.includes('session-token'));
  console.log(`[Login] session: ${hasSession ? 'OK' : 'FAILED'}`);
  return ctx;
}

async function step_claim(ctx) {
  const body = {
    '0': {
      json: {
        address: ctx.address,
        chain: 'eth',
        encryptedToken: ctx.encryptedToken,
        message: ctx.claimMessage,
        signature: ctx.claimSignature,
        type: 'wallet',
        version: '2'
      }
    }
  };

  const res = await fetch(`${BASE_URL}/trpc/lambda/user.claimSignupBonus?batch=1`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Cookie': ctx.sessionCookies,
      'Referer': `${BASE_URL}/chat`,
      'Origin': BASE_URL,
      'Accept': '*/*'
    },
    body: JSON.stringify(body)
  });

  const text = await res.text();
  console.log(`[Claim] HTTP ${res.status} | ${text.slice(0, 200)}`);

  try {
    const data = JSON.parse(text);
    ctx.claimResult = data[0]?.result?.data?.json;
    ctx.claimSuccess = !!ctx.claimResult?.success;
  } catch {
    ctx.claimSuccess = false;
    ctx.claimError = text.slice(0, 200);
  }
  return ctx;
}

// ============================================================
// 主流程
// ============================================================

async function main() {
  const ctx = {
    // [REQUIRED] 在这里设置初始值
    address: '0xCHANGE_ME',
    loginMessage: 'CHANGE_ME',
    loginSignature: '0xCHANGE_ME',
    encryptedToken: 'CHANGE_ME',
    claimMessage: 'CHANGE_ME',
    claimSignature: '0xCHANGE_ME'
  };

  const steps = [
    { name: 'CSRF', fn: step_getCsrfToken },
    { name: 'Login', fn: step_login },
    { name: 'Claim', fn: step_claim },
    // 按需添加更多步骤
  ];

  for (const step of steps) {
    console.log(`\n--- ${step.name} ---`);
    try {
      ctx = await step.fn(ctx);
    } catch (err) {
      console.error(`[${step.name}] ERROR: ${err.message}`);
      break;
    }
  }

  console.log('\n=== Final Context ===');
  console.log(JSON.stringify({
    csrfToken: ctx.csrfToken,
    sessionCookies: ctx.sessionCookies,
    claimSuccess: ctx.claimSuccess,
    claimResult: ctx.claimResult,
    claimError: ctx.claimError
  }, null, 2));
}

main().catch(console.error);
