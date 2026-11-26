// 焯越模拟飞行理论题库 · 统计模块
// 本地：localStorage 累计每人自己的作答记录
// 全员：Cloudflare Worker 只存聚合值（题号 + 作答次数 + 答对次数），不含个人信息
(function () {
  'use strict';

  var API = 'https://zhuoyue-stats.maverick-lou.workers.dev';
  var LKEY = 'zhuoyue_stats_v1';
  var QKEY = 'zhuoyue_stats_queue_v1';
  var CKEY = 'zhuoyue_global_stats_v1';
  var CACHE_MS = 10 * 60 * 1000;
  var cache = null;

  function read(key, fallback) {
    try { return JSON.parse(localStorage.getItem(key) || 'null') || fallback; } catch (e) { return fallback; }
  }
  function write(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) {}
  }

  function uid() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return 'e' + Date.now().toString(36) + Math.random().toString(36).slice(2, 10);
  }

  var Stats = {
    local: function () { return read(LKEY, {}); },

    // 记录一次判定（只应在首次判定时调用）
    record: function (qid, correct) {
      if (!qid) return;
      var data = this.local();
      if (!data[qid]) data[qid] = { a: 0, c: 0 };
      data[qid].a += 1;
      if (correct) data[qid].c += 1;
      write(LKEY, data);
      var queue = read(QKEY, []);
      queue.push({ id: uid(), qid: qid, correct: !!correct });
      write(QKEY, queue);
      this.renderUI();
      this.flush();
    },

    // 把待上报事件发送到 Worker；失败则保留在本地队列，下次再试
    flush: function () {
      var queue = read(QKEY, []);
      if (!queue.length) return;
      var batch = queue.slice(0, 200);
      var body = JSON.stringify({ events: batch });
      fetch(API + '/api/stats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: body,
        keepalive: true
      }).then(function (r) {
        if (!r.ok) throw new Error('bad status');
        var left = read(QKEY, []).slice(batch.length);
        write(QKEY, left);
      }).catch(function () { /* 保留队列，等待下次重试 */ });
    },

    // 批量拉取全员聚合数据，缓存 10 分钟
    global: function (qids) {
      qids = (qids || []).filter(Boolean);
      if (!qids.length) return Promise.resolve({});
      if (cache && Date.now() - cache.ts < CACHE_MS) return Promise.resolve(cache.data);
      try {
        var saved = JSON.parse(sessionStorage.getItem(CKEY) || 'null');
        if (saved && Date.now() - saved.ts < CACHE_MS) {
          cache = saved;
          return Promise.resolve(saved.data);
        }
      } catch (e) {}
      return fetch(API + '/api/stats?qids=' + encodeURIComponent(qids.join(',')), { cache: 'no-store' })
        .then(function (r) { return r.ok ? r.json() : {}; })
        .then(function (data) {
          cache = { ts: Date.now(), data: data || {} };
          try { sessionStorage.setItem(CKEY, JSON.stringify(cache)); } catch (e) {}
          return cache.data;
        })
        .catch(function () { return {}; });
    },

    globalData: function () { return (cache && cache.data) || {}; },

    rate: function (s) {
      if (!s || !s.a) return '--';
      return Math.round(s.c / s.a * 100) + '%';
    },

    renderUI: function () {
      var local = this.local();
      var global = (cache && cache.data) || {};
      document.querySelectorAll('.q-stat[data-qid]').forEach(function (el) {
        var qid = el.getAttribute('data-qid');
        var l = local[qid], g = global[qid];
        var parts = [];
        if (l && l.a) parts.push('我的 ' + Math.round(l.c / l.a * 100) + '%（' + l.c + '/' + l.a + '）');
        if (g && g.a) parts.push('全员 ' + Math.round(g.c / g.a * 100) + '%（n=' + g.a + '）');
        el.textContent = parts.join(' · ');
      });
      var box = document.getElementById('local-stats');
      if (box) {
        var a = 0, c = 0;
        Object.keys(local).forEach(function (k) { a += local[k].a; c += local[k].c; });
        box.innerHTML = a
          ? '本机累计作答 <strong>' + a + '</strong> 题次，答对 <strong>' + c + '</strong> 题次，本地正确率 <strong>' + Math.round(c / a * 100) + '%</strong>。'
          : '本机暂无作答记录。完成任意复习或考试后，这里会显示你自己的累计正确率。';
      }
    },

    init: function () {
      var ids = [];
      document.querySelectorAll('[data-qid]').forEach(function (el) {
        var qid = el.getAttribute('data-qid');
        if (qid && ids.indexOf(qid) < 0) ids.push(qid);
      });
      this.renderUI();
      var self = this;
      this.global(ids).then(function () {
        self.renderUI();
        if (typeof window.onStatsReady === 'function') window.onStatsReady();
      });
      this.flush();
    }
  };

  window.Stats = Stats;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { Stats.init(); });
  } else {
    Stats.init();
  }
})();
