// 企业级安全防护库 - 防火墙与数据清洗
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
  /\/\.env/i,
  /\/\.git/i,
  /\/wp-login\.php/i,
  /\/wp-admin/i,
  /\/phpmyadmin/i,
  /\/eval-stdin\.php/i,
  /\/actuator/i,
  /\/cgi-bin/i,
  /\/solr/i,
  /\/console/i,
  /\/autodiscover/i
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
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/javascript:/gi, '')
      .replace(/onload\s*=/gi, '')
      .replace(/onerror\s*=/gi, '')
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
