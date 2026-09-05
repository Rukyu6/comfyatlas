import { checkRateLimit, BLACKLIST_PATHS, MALICIOUS_BOTS } from './lib/security.js';

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
