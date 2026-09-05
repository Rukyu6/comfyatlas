import os
import json

print("=== 1. 编写企业级安全防护模块: src/lib/security.js ===")
os.makedirs("src/lib", exist_ok=True)

security_lib = '''// 企业级安全防护库 - 防火墙与数据清洗
const rateLimitMap = new Map();

// 清理超过 1 分钟的陈旧限流记录（防内存泄漏）
setInterval(() => {
  const now = Date.now();
  for (const [key, record] of rateLimitMap.entries()) {
    if (now - record.startTime > 60000) {
      rateLimitMap.delete(key);
    }
  }
}, 60000);

/**
 * IP 滑动窗口限流校验
 * @param {string} ip 客户端 IP
 * @param {number} limit 允许的最大频次
 * @param {number} windowMs 窗口时间 (毫秒)
 */
export function checkRateLimit(ip, limit = 60, windowMs = 60000) {
  const now = Date.now();
  const record = rateLimitMap.get(ip) || { count: 0, startTime: now };

  if (now - record.startTime > windowMs) {
    record.count = 1;
    record.startTime = now;
    rateLimitMap.set(ip, record);
    return { allowed: true, remaining: limit - 1 };
  }

  record.count += 1;
  rateLimitMap.set(ip, record);

  if (record.count > limit) {
    return { allowed: false, remaining: 0 };
  }
  return { allowed: true, remaining: limit - record.count };
}

// 恶意扫描路径黑名单
export const BLACKLIST_PATHS = [
  /\\/\\.env/i,
  /\\/\\.git/i,
  /\\/wp-login\\.php/i,
  /\\/wp-admin/i,
  /\\/phpmyadmin/i,
  /\\/eval-stdin\\.php/i,
  /\\/actuator/i,
  /\\/cgi-bin/i,
  /\\/solr/i,
  /\\/console/i,
  /\\/autodiscover/i
];

// 常见黑客扫描器与攻击工具指纹
export const MALICIOUS_BOTS = [
  /sqlmap/i,
  /nikto/i,
  /dirbuster/i,
  /acunetix/i,
  /havij/i,
  /masscan/i,
  /nmap/i,
  /zgrab/i,
  /python-requests/i // 限制直接脚本裸爬敏感 API
];

/**
 * 递归清洗危险脚本与 XSS 攻击 Payload
 */
export function sanitizeInput(data) {
  if (typeof data === 'string') {
    return data
      .replace(/<script\\b[^<]*(?:(?!<\\/script>)<[^<]*)*<\\/script>/gi, '')
      .replace(/javascript:/gi, '')
      .replace(/onload\\s*=/gi, '')
      .replace(/onerror\\s*=/gi, '')
      .replace(/[<>]/g, (tag) => ({ '<': '&lt;', '>': '&gt;' }[tag] || tag));
  }
  if (Array.isArray(data)) {
    return data.map(sanitizeInput);
  }
  if (data !== null && typeof data === 'object') {
    const cleaned = {};
    for (const key of Object.keys(data)) {
      cleaned[key] = sanitizeInput(data[key]);
    }
    return cleaned;
  }
  return data;
}
'''
with open("src/lib/security.js", "w", encoding="utf-8") as f:
    f.write(security_lib)
print("✓ 已生成: src/lib/security.js")

print("\n=== 2. 创建/升级全局中间件: src/middleware.js ===")
middleware_code = '''import { checkRateLimit, BLACKLIST_PATHS, MALICIOUS_BOTS } from './lib/security.js';

export async function onRequest(context, next) {
  const { request, url } = context;
  const clientIp = request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip') || '127.0.0.1';
  const userAgent = request.headers.get('user-agent') || '';
  const pathname = url.pathname;

  // 1. 防御恶意漏洞探测扫描 (直接 403 阻断)
  for (const pattern of BLACKLIST_PATHS) {
    if (pattern.test(pathname)) {
      console.warn(`[Security Alert] Blocked suspicious probe: ${pathname} from IP: ${clientIp}`);
      return new Response(JSON.stringify({ error: 'Access Denied: Security violation detected.' }), {
        status: 403,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }

  // 2. 拦截黑客扫描工具 User-Agent (仅针对 API 与敏感路径)
  if (pathname.startsWith('/api/') || pathname.startsWith('/admin')) {
    for (const botPattern of MALICIOUS_BOTS) {
      if (botPattern.test(userAgent)) {
        console.warn(`[Security Alert] Blocked malicious scanner UA: ${userAgent} from IP: ${clientIp}`);
        return new Response(JSON.stringify({ error: 'Forbidden: Automated scanner blocked.' }), {
          status: 403,
          headers: { 'Content-Type': 'application/json' }
        });
      }
    }
  }

  // 3. 动态滑动窗口接口限流 (防 CC 与刷单爆破)
  if (pathname.startsWith('/api/')) {
    // 支付验证、订单派发与密码验证：高密防护 (每分钟限 15 次)
    const isSensitiveApi = pathname.includes('payment') || pathname.includes('order') || pathname.includes('notify') || pathname.includes('auth');
    const limit = isSensitiveApi ? 15 : 60;
    
    const rateCheck = checkRateLimit(clientIp + ':' + (isSensitiveApi ? 'strict' : 'general'), limit);
    if (!rateCheck.allowed) {
      console.warn(`[Security Alert] Rate limit exceeded for IP: ${clientIp} on: ${pathname}`);
      return new Response(JSON.stringify({
        error: '请求过于频繁，触发安全保护，请稍候再试。',
        code: 'RATE_LIMIT_EXCEEDED'
      }), {
        status: 429,
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          'Retry-After': '60'
        }
      });
    }
  }

  // 4. 执行业务逻辑
  const response = await next();

  // 5. 注入现代安全防护响应头 (防 XSS / 防点击劫持 / 防嗅探)
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-XSS-Protection', '1; mode=block');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload');
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');

  return response;
}
'''
with open("src/middleware.js", "w", encoding="utf-8") as f:
    f.write(middleware_code)
print("✓ 已生成/更新: src/middleware.js")

print("\n=== 3. 升级 Edge 部署安全策略: vercel.json ===")
vercel_config = {
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" }
      ]
    },
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "no-store, no-cache, must-revalidate, proxy-revalidate" },
        { "key": "Pragma", "value": "no-cache" }
      ]
    }
  ]
}
with open("vercel.json", "w", encoding="utf-8") as f:
    json.dump(vercel_config, f, indent=2, ensure_ascii=False)
print("✓ 已生成边缘防御配置文件: vercel.json")

print("\n=== 4. 验证系统构建与防御网生效 ===")
