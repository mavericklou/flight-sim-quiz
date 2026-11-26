// 焯越模拟飞行理论题库 · 全站错题率统计服务
// 只存聚合数据：每道题的作答次数与答对次数；不收集 IP、账号或任何个人信息。

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

const QID_RE = /^q[0-9a-f]{12}$/;

function json(data, status = 200, extra = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8', ...CORS, ...extra },
  });
}

async function hashIP(ip) {
  if (!ip) return 'unknown';
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(ip));
  return Array.from(new Uint8Array(digest)).slice(0, 8).map((b) => b.toString(16).padStart(2, '0')).join('');
}

// 简单限流：同一 IP 每分钟最多 60 次上报事件
async function rateLimited(request, count, kv) {
  const ip = request.headers.get('CF-Connecting-IP') || '';
  const minute = Math.floor(Date.now() / 60000);
  const key = `rl:${await hashIP(ip)}:${minute}`;
  const raw = await kv.get(key);
  const used = raw ? parseInt(raw, 10) : 0;
  if (used + count > 60) return true;
  await kv.put(key, String(used + count), { expirationTtl: 120 });
  return false;
}

async function getStat(qid, kv) {
  const raw = await kv.get(`stat:${qid}`, 'text');
  if (!raw) return { a: 0, c: 0 };
  try {
    const s = JSON.parse(raw);
    return { a: Number(s.a) || 0, c: Number(s.c) || 0 };
  } catch (e) {
    return { a: 0, c: 0 };
  }
}

export default {
  async fetch(request, env) {
    const kv = env.STATS_KV;
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS });
    }

    if (url.pathname === '/health') {
      return json({ ok: true, service: 'zhuoyue-stats' });
    }

    if (request.method === 'POST' && url.pathname === '/api/stats') {
      let body;
      try {
        body = await request.json();
      } catch (e) {
        return json({ error: 'invalid json' }, 400);
      }
      const events = Array.isArray(body && body.events) ? body.events : [];
      if (!events.length || events.length > 200) return json({ error: 'invalid events' }, 400);
      const valid = events.filter((e) => e && QID_RE.test(e.qid) && typeof e.correct === 'boolean' && typeof e.id === 'string' && e.id.length <= 80);
      if (!valid.length) return json({ error: 'no valid events' }, 400);
      if (await rateLimited(request, valid.length, kv)) return json({ error: 'rate limited' }, 429);

      let processed = 0;
      for (const e of valid) {
        // 幂等：同一个作答事件只计一次（保留 30 天）
        const seen = await kv.get(`ev:${e.id}`);
        if (seen) continue;
        await kv.put(`ev:${e.id}`, '1', { expirationTtl: 60 * 60 * 24 * 30 });
        const stat = await getStat(e.qid, kv);
        stat.a += 1;
        if (e.correct) stat.c += 1;
        await kv.put(`stat:${e.qid}`, JSON.stringify(stat));
        processed++;
      }
      return json({ ok: true, processed });
    }

    if (request.method === 'GET' && url.pathname === '/api/stats') {
      const qids = (url.searchParams.get('qids') || '').split(',').filter((q) => QID_RE.test(q)).slice(0, 200);
      const out = {};
      for (const qid of qids) {
        const s = await getStat(qid, kv);
        if (s.a > 0) out[qid] = { a: s.a, c: s.c };
      }
      return json(out, 200, { 'Cache-Control': 'public, max-age=60' });
    }

    return json({ error: 'not found' }, 404);
  },
};
