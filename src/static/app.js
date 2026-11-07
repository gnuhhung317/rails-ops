/*
 * CompressorGuard v3.0 — Operations Command Console (vanilla SPA, zero build)
 *
 * Product invariants enforced by this module:
 *  1. ZERO HARDCODED TELEMETRY — every rendered value comes from a JSON response.
 *  2. "The Dashboard Does Not Trigger Telemetry" — the UI is a pure consumer.
 *     It polls GET endpoints only; the server-side background stream worker pumps
 *     samples into MongoDB. No setInterval -> POST /demo/tick pattern exists here.
 *  3. All simulation controls live inside the Replay Studio drawer (Shift + S).
 *  4. Human-in-the-loop buttons are enabled strictly by real API state, and
 *     ActionGuard renders FAIL + denial_reason when is_permitted === false.
 */
'use strict';

/* ══════════════════════════════ runtime config (no domain data) ══════════════════════════════ */
const CFG = {
  pollMs: 1500,
  requestTimeoutMs: 20000,
  samplingIntervalSeconds: 10,
  gapBreakSeconds: 30,
  detectionWindowSeconds: 1200,
  timeframeLimits: { '5m': 30, '15m': 90, '1h': 360, '6h': 500, 'all': 500 },
  timeframeLabels: { '5m': '5 phút', '15m': '15 phút', '1h': '1 giờ', '6h': '6 giờ', 'all': 'Bộ đệm tối đa' },
  api: {
    operations: '/api/operations',
    incident: '/api/incident',
    evidence: '/api/evidence',
    events: '/api/case/events',
    guard: '/api/action/guard-status',
    recovery: '/api/recovery',
    window: '/api/telemetry/window',
    analytics: '/api/telemetry/analytics',
    scenarios: '/api/scenarios',
    validation: '/api/validation-reference'
  },
  pillBase: 'LIVE SIMULATION · HISTORICAL DATA'
};

const S = {
  view: 'fleet',
  wbFocus: 'changed',
  timeframe: '15m',
  operator: 'DISPATCHER-0941',
  shading: true,
  thresholds: true,
  degraded: false,
  lastGoodPoll: 0,
  engineering: false,
  data: {
    operations: null, incident: null, evidence: null, events: [],
    guard: null, recovery: null, window: null, analytics: null,
    scenarios: null, validation: null, simStatus: null
  },
  lastAction: null,
  charts: {},
  pollCount: 0
};

/* ══════════════════════════════ tiny DOM helpers ══════════════════════════════ */
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
const DASH = '—';

function txt(value) {
  if (value === null || value === undefined || value === '') return DASH;
  return String(value);
}

/*
 * The engine speaks English. These are the recurring tokens the console renders;
 * anything not in the glossary falls through untouched rather than being guessed,
 * so an unknown backend value is always visible verbatim instead of mistranslated.
 */
const GLOSSARY = {
  HEALTHY: 'Tốt',
  DEGRADING: 'Suy giảm',
  CRITICAL: 'Nghiêm trọng',
  NOMINAL: 'Bình thường',
  NONE: 'Chưa có',
  LOW: 'Thấp',
  MEDIUM: 'Vừa',
  HIGH: 'Cao',
  ACKNOWLEDGED: 'Đã xác nhận',
  UNACKNOWLEDGED: 'Chưa xác nhận',
  DISPATCHED: 'Đã phát',
  CORROBORATED: 'AI xác nhận',
  TRIGGERED: 'Kích hoạt',
  NORMAL: 'Trong ngưỡng',
  PASS: 'ĐẠT',
  FAIL: 'KHÔNG ĐẠT',
  AVAILABLE: 'SẴN SÀNG',
  'NOT AVAILABLE': 'CHƯA SẴN SÀNG',
  WITHIN_BASELINE: 'Trong baseline',
  SUPPRESSED_TRANSIENT: 'Nhiễu thoáng qua đã chặn',
  'Active case required in DETECTED or INVESTIGATING state.': 'Cần ca mở ở giai đoạn Phát hiện hoặc Đang điều tra.',
  'Mitigation not recommended by DecisionEngine.': 'DecisionEngine chưa khuyến nghị can thiệp.',
  'Conflicting active cases detected on asset.': 'Tài sản đang có ca mở xung đột.',
  'Brake reservoir pressure below safe threshold (< 7.0 bar or LPS tripped).': 'Áp phanh bình chứa dưới ngưỡng an toàn (< 7.0 bar hoặc LPS đã kích).',
  'Post-maintenance historical stream segment unavailable.': 'Chưa có phân đoạn luồng sau bảo trì.',
  'Case is active and confirmed (DETECTED / INVESTIGATING)': 'Ca đang mở và đã xác nhận (DETECTED / INVESTIGATING)',
  'DecisionEngine recommends mitigation (Physics + ML Corroboration)': 'DecisionEngine khuyến nghị can thiệp (vật lý + AI)',
  'No conflicting active cases on asset': 'Không có ca mở xung đột trên tài sản',
  'Main brake reservoir safe for depot routing (TP3 >= 7.0 bar, LPS == 0)': 'Bình phanh chính an toàn cho điều độ (TP3 ≥ 7.0 bar, LPS = 0)',
  'Post-maintenance commissioning stream segment available': 'Có phân đoạn luồng chạy thử sau bảo trì',
  'Transient excursion (< 3 consecutive LOADED cycles); suppressed to prevent alert fatigue.': 'Nhiễu thoáng qua dưới 3 kỳ LOADED — đã chặn.'
};

function vlabel(value) {
  const key = String(value === null || value === undefined ? '' : value).trim();
  return GLOSSARY[key] !== undefined ? GLOSSARY[key] : txt(key);
}

/* Backend prose is data, not UI copy: translate the known finite set, leave the rest verbatim. */
const MESSAGE_VI = {
  'Discharge Valve Pressure': 'Áp suất van xả',
  'Compressor Oil Temperature': 'Nhiệt độ dầu máy nén',
  'Temporal Persistence Tracking': 'Độ bền bước nhảy theo thời gian',
  'Multivariate Isolation Forest': 'Isolation Forest đa biến',
  'Low Pressure Switch': 'Công tắc áp thấp',
  'Baseline state.': 'Trạng thái nền.',
  'Multiple anomaly signals detected with ongoing persistence tracking.': 'Nhiều tín hiệu bất thường; đang theo dõi độ bền.',
  'Transient anomaly excursion(s) detected. Accumulating telemetry evidence.': 'Có nhiễu thoáng qua; đang gom bằng chứng.',
  'Confirmed severe step degradation in DV_pressure with thermal stress drift.': 'Suy giảm bước nhảy nghiêm trọng ở DV_pressure kèm trôi nhiệt.',
  'Confirmed severe step degradation corroborated by Isolation Forest.': 'Suy giảm bước nhảy nghiêm trọng, AI xác nhận.',
  'Physical step degradation corroborated by multivariate Isolation Forest (5 LOADED features). Safe Mode recommended.': 'Vật lý suy giảm bước nhảy, Isolation Forest xác nhận (5 đặc trưng LOADED). Khuyến nghị chế độ an toàn.',
  'Low Pressure Switch (LPS=1) reactive threshold breached. Line pressure < 7.0 bar.': 'Công tắc áp thấp (LPS=1) đã kích hoạt. Áp đường < 7.0 bar.',
  'Insufficient temporal persistence (1/3 LOADED cycles); suppressed to prevent alert fatigue.': 'Độ bền bước nhảy chưa đủ (1/3 kỳ LOADED) — đã chặn.',
  'Confirmed degradation detected': 'Đã xác nhận suy giảm',
  'Severe step degradation in DV_pressure with thermal drift sustained across loaded observations. Case opened.': 'Suy giảm bước nhảy ở DV_pressure kéo qua các kỳ LOADED. Đã mở vụ việc.',
  'Operational Policy Evaluation: Open Case': 'Đánh giá chính sách: mở vụ việc',
  'DecisionEngine evaluated multi-sensor evidence. Confirmed persistent degradation; opened case and recommended elevated monitoring.': 'DecisionEngine đánh giá bằng chứng đa cảm biến, xác nhận suy giảm bền; mở vụ việc và giám sát chặt.',
  'Multivariate Isolation Forest Corroboration': 'AI xác nhận (Isolation Forest)',
  'Isolation Forest exceeded threshold (score > 0.35) on 5 LOADED features. Mitigation recommended.': 'Isolation Forest vượt ngưỡng (điểm > 0.35) trên 5 đặc trưng LOADED. Khuyến nghị can thiệp.',
  'Operational Policy Evaluation: Mitigation Recommended': 'Đánh giá chính sách: khuyến nghị can thiệp',
  'DecisionEngine corroborated anomaly with Isolation Forest. Recommended EXECUTE_MITIGATION under ActionGuard.': 'DecisionEngine xác nhận bất thường bằng Isolation Forest; khuyến nghị can thiệp qua ActionGuard.',
  'Early Excursion Telemetry Observation': 'Quan sát nhiễu áp đầu kỳ',
  'Unmitigated Historical LPS Breach Reference': 'Tham chiếu LPS lịch sử không can thiệp',
  'Conventional low pressure switch breach observed in historical baseline without early intervention.': 'LPS quy ước đã kích hoạt trong dữ liệu lịch sử, không có cảnh báo sớm.',
  'Safe Mode Simulated Intervention': 'Can thiệp chế độ an toàn',
  'ActionGuard validated 5 criteria. Branching stream to post-maintenance historical segment.': 'ActionGuard đạt 5 tiêu chí. Chuyển luồng sang phân đoạn sau bảo trì.',
  'Recovery Criteria Verified (5/5 healthy LOADED observations)': 'Nghiệm thu đạt (5/5 kỳ LOADED khỏe)',
  'Discharge valve pressure < 0.05 bar and oil temp < 67°C verified across 5 consecutive loaded observations.': 'Áp van xả < 0.05 bar, dầu < 67 °C đạt trên 5 kỳ LOADED liên tiếp.',
  'Case Signed Off & Closed': 'Đã chốt và đóng vụ việc',
  'Operator Shift / Diagnostic Note': 'Ghi chú vận hành / chẩn đoán',
  'Case Closed as False Positive (Operator Override)': 'Đóng vụ việc: dương tính giả (operator bỏ qua)'
};

const MESSAGE_RX = [
  [/^Case Acknowledged \((.+)\)$/, (m) => `Đã xác nhận vụ việc (${m[1]})`],
  [/^Maintenance Work Order Dispatched \((.+)\)$/, (m) => `Đã phát lệnh công tác (${m[1]})`],
  [/^Playbook (.+) dispatched to (.+) \((.+)\): ([\s\S]*)$/, (m) => `Playbook ${m[1]} → ${m[2]} (${m[3]}): ${m[4]}`],
  [/^Discharge valve transient pressure excursion observed \(([^)]+)\) at ([^.]+)\..*$/, (m) => `Nhiễu áp van xả thoáng qua (${m[1]}) lúc ${m[2]} — độ bền chưa đủ, chưa mở vụ việc.`],
  [/^Operator (\S+) acknowledged operational case with priority (\S+)\. ?([\s\S]*)$/, (m) => `${m[1]} xác nhận vụ việc, ưu tiên ${m[2]}. ${m[3]}`],
  [/^Operator (\S+) marked case as false positive\. Reason: ?([\s\S]*)$/, (m) => `${m[1]} đánh dấu dương tính giả. Lý do: ${m[2]}`],
  [/^Operator (\S+) signed off incident\. Asset (\S+) released back to HEALTHY service\. Notes: ?([\s\S]*)$/, (m) => `${m[1]} chốt vụ việc. ${m[2]} trở lại trạng thái Tốt. Ghi chú: ${m[3]}`]
];

function mtxt(value) {
  const key = String(value === null || value === undefined ? '' : value).trim();
  if (!key) return key;
  if (MESSAGE_VI[key] !== undefined) return MESSAGE_VI[key];
  for (let i = 0; i < MESSAGE_RX.length; i += 1) {
    const m = key.match(MESSAGE_RX[i][0]);
    if (m) return MESSAGE_RX[i][1](m);
  }
  return vlabel(key);
}

function bind(name, text, tone) {
  const nodes = $$(`[data-bind="${name}"]`);
  nodes.forEach((n) => {
    n.textContent = txt(text);
    if (tone !== undefined) {
      if (tone === null) n.removeAttribute('data-tone'); else n.setAttribute('data-tone', tone);
    }
  });
  return nodes.length;
}

function kpi(name, value, tone) {
  const node = $(`[data-kpi="${name}"]`);
  if (node) {
    node.textContent = txt(value);
    if (tone === null) node.removeAttribute('data-tone'); else if (tone) node.setAttribute('data-tone', tone);
    const card = node.closest('.kpi-card');
    if (card) { if (tone) card.setAttribute('data-tone', tone); else card.removeAttribute('data-tone'); }
  }
  return node;
}

function kpiNote(name, value) {
  const node = $(`[data-kpi-note="${name}"]`);
  if (node) node.textContent = txt(value);
  return node;
}

function el(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
}

function clear(node) { while (node && node.firstChild) node.removeChild(node.firstChild); return node; }

function badge(label, tone) {
  const b = el('span', `badge ${tone || 'idle'}`, label);
  return b;
}

function num(value, digits) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return DASH;
  const n = Number(value);
  return n.toFixed(digits === undefined ? (Math.abs(n) >= 100 ? 1 : 3) : digits);
}

function signed(value, digits) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return DASH;
  const n = Number(value);
  return `${n >= 0 ? '+' : '−'}${Math.abs(n).toFixed(digits === undefined ? 2 : digits)}`;
}

/* The API prefixes the elapsed warning with '+'; the hero label already carries the sign. */
function stripPlus(value) {
  if (value === null || value === undefined || value === '') return DASH;
  return String(value).replace(/^\+/, '');
}

function clockOf(iso) {
  if (!iso) return DASH;
  const s = String(iso);
  const m = s.match(/T(\d{2}:\d{2}:\d{2})/);
  if (m) return m[1];
  return s;
}

function utcOf(iso) {
  if (!iso) return DASH;
  return String(iso).replace('T', ' ').replace(/Z$/, '');
}

const STATUS_TONE = {
  CRITICAL: 'crit', SEVERE: 'crit', LPS_TRIGGER: 'crit', BREACH: 'crit', FAIL: 'crit',
  ELEVATED: 'warn', TRIGGERED: 'warn', WARNING: 'warn', PENDING: 'warn', AWAITING_CORROBORATION: 'warn',
  CONFIRMED: 'ok', PASS: 'ok', HEALTHY: 'ok', NORMAL: 'ok', VERIFIED: 'ok',
  CORROBORATED: 'info', OBSERVING: 'info', INVESTIGATING: 'info', MITIGATING: 'info', VERIFYING_RECOVERY: 'info'
};
const tone = (value) => STATUS_TONE[String(value || '').toUpperCase()] || 'idle';

const PHASE_LABEL = {
  NONE: 'Giám sát',
  DETECTED: 'Phát hiện',
  INVESTIGATING: 'Đang điều tra',
  MITIGATING: 'Đang xử lý',
  VERIFYING_RECOVERY: 'Đang nghiệm thu',
  RESOLVED: 'Đã khắc phục'
};
const phaseLabel = (value) => PHASE_LABEL[String(value || 'NONE').toUpperCase()] || txt(value);

/* UI = f(state): a control or a status lamp only exists once the lifecycle really needs it. */
const PHASE_VISIBILITY = {
  NONE: { steps: [], guard: false, recovery: false },
  DETECTED: { steps: [1], guard: true, recovery: false },
  INVESTIGATING: { steps: [2, 3], guard: true, recovery: false },
  MITIGATING: { steps: [4], guard: true, recovery: false },
  VERIFYING_RECOVERY: { steps: [5], guard: false, recovery: true },
  RESOLVED: { steps: [], guard: false, recovery: true }
};
const PHASE_FOCUS = {
  NONE: 'changed', DETECTED: 'changed', INVESTIGATING: 'changed',
  MITIGATING: 'guard', VERIFYING_RECOVERY: 'recovery', RESOLVED: 'recovery'
};
const recoveryPhase = (state) => ['MITIGATING', 'VERIFYING_RECOVERY', 'RESOLVED'].includes(state);

/* ══════════════════════════════ transport ══════════════════════════════ */
async function request(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), CFG.requestTimeoutMs);
  let res;
  let raw;
  try {
    res = await fetch(path, {
      method: options.method || 'GET',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: options.body ? JSON.stringify(options.body) : undefined,
      signal: controller.signal,
      cache: 'no-store'
    });
    raw = await res.text();
  } catch (netErr) {
    // Transport-level failure only: the API link itself is unhealthy.
    setConnection(false);
    clearTimeout(timer);
    throw netErr;
  }
  clearTimeout(timer);
  let payload = null;
  try { payload = raw ? JSON.parse(raw) : null; } catch (_) { payload = { rawError: raw }; }
  if (!res.ok) {
    // HTTP-level rejection (409 ActionGuard gate, 400 validation, 500) means the
    // link is alive — the engine honestly refused the request. Never mark it degraded.
    const err = new Error(extractError(payload) || `HTTP ${res.status}`);
    err.status = res.status;
    err.payload = payload;
    throw err;
  }
  setConnection(true);
  return payload;
}

function extractError(payload) {
  if (!payload) return null;
  const d = payload.detail !== undefined ? payload.detail : payload.error;
  if (typeof d === 'string') return d;
  if (Array.isArray(d) && d.length) {
    const first = d[0];
    return (first && (first.msg || first.message)) || JSON.stringify(first);
  }
  if (typeof payload.rawError === 'string') return payload.rawError.slice(0, 200);
  return null;
}

function setConnection(online) {
  const box = $('#conn-indicator');
  const label = $('#conn-text');
  if (!box) return;
  const wasDegraded = S.degraded;
  S.degraded = !online;
  box.setAttribute('data-state', online ? 'online' : 'degraded');
  if (label) label.textContent = online ? 'API BÌNH THƯỜNG' : 'API GIÁN ĐOẠN';
  const pill = $('#stream-pill');
  if (pill) pill.setAttribute('data-stale', online ? 'false' : 'true');
  if (!online && !wasDegraded) toast('warn', 'Gián đoạn luồng đọc', 'Lần đọc thành công: ' + formatPollAge());
}

function formatPollAge() {
  if (!S.lastGoodPoll) return 'chưa đọc thành công';
  const secs = Math.max(0, Math.round((Date.now() - S.lastGoodPoll) / 1000));
  return `${new Date(S.lastGoodPoll).toISOString().replace('T', ' ').slice(0, 19)} UTC (${secs}s trước)`;
}

/* ══════════════════════════════ toasts ══════════════════════════════ */
function toast(kind, title, detail, ttl) {
  const stack = $('#toast-stack');
  if (!stack) return;
  const tones = { ok: 'ok', error: 'error', warn: 'warn', info: 'info' };
  const node = el('div', 'toast');
  node.setAttribute('data-tone', tones[kind] || 'info');
  node.appendChild(el('b', null, title));
  if (detail) node.appendChild(el('span', 'mono', detail));
  stack.appendChild(node);
  const life = ttl || (kind === 'error' ? 9000 : 4800);
  setTimeout(() => {
    node.classList.add('leaving');
    setTimeout(() => node.remove(), 260);
  }, life);
  while (stack.children.length > 5) stack.removeChild(stack.firstChild);
}

/* ══════════════════════════════ data acquisition ══════════════════════════════ */
async function refreshAllData() {
  const limit = CFG.timeframeLimits[S.timeframe] || 90;
  const jobs = {
    operations: request(CFG.api.operations),
    incident: request(CFG.api.incident),
    evidence: request(CFG.api.evidence),
    guard: request(CFG.api.guard),
    recovery: request(CFG.api.recovery),
    window: request(`${CFG.api.window}?limit=${limit}`),
    analytics: request(CFG.api.analytics),
    events: request(CFG.api.events),
    simStatus: request('/demo/status')
  };
  if (S.pollCount % 8 === 0 || !S.data.scenarios) jobs.scenarios = request(CFG.api.scenarios);
  if (S.pollCount % 40 === 0 || !S.data.validation) jobs.validation = request(CFG.api.validation);

  const names = Object.keys(jobs);
  const results = await Promise.allSettled(names.map((n) => jobs[n]));
  let ok = 0;
  const failed = [];
  results.forEach((r, i) => {
    const name = names[i];
    if (r.status === 'fulfilled') {
      if (name !== 'validation' || r.value) S.data[name] = r.value;
      ok += 1;
    } else {
      failed.push(`${name}: ${r.error && r.error.message ? r.error.message : r.error}`);
    }
  });

  if (ok > 0) {
    S.lastGoodPoll = Date.now();
    if (S.degraded && ok === names.length) setConnection(true);
  }
  if (failed.length === names.length && names.length) {
    toast('error', 'Mất kết nối API', failed[0], 8000);
  }

  S.pollCount += 1;
  render();
}

/* ══════════════════════════════ derived helpers ══════════════════════════════ */
function chronologicalPoints() {
  const pts = (S.data.window && Array.isArray(S.data.window.points)) ? S.data.window.points : [];
  return pts.slice().reverse();
}

function latestPoint() {
  const pts = (S.data.window && Array.isArray(S.data.window.points)) ? S.data.window.points : [];
  return pts.length ? pts[0] : null;
}

function isLoaded(value) { return String(value || '').toUpperCase() === 'LOADED'; }
function regimeLabel(value) { return isLoaded(value) ? 'LOADED' : 'UNLOADED'; }

function evidenceCardByCode(fragment) {
  const pack = (S.data.evidence && S.data.evidence.evidence_pack) || [];
  return pack.find((c) => String(c.code || '').toUpperCase().includes(fragment)) || null;
}

function evidenceCardBySensor(sensor) {
  const pack = (S.data.evidence && S.data.evidence.evidence_pack) || [];
  return pack.find((c) => c.provenance && c.provenance.sensor === sensor) || null;
}

function statsFor(key) {
  const pts = chronologicalPoints().filter((p) => isLoaded(p.regime) && typeof p[key] === 'number');
  if (!pts.length) return null;
  const vals = pts.map((p) => p[key]);
  const mean = vals.reduce((a, b) => a + b, 0) / vals.length;
  const variance = vals.reduce((a, b) => a + (b - mean) * (b - mean), 0) / vals.length;
  return { mean, std: Math.sqrt(variance), n: vals.length, min: Math.min(...vals), max: Math.max(...vals) };
}

function hasActiveCase() {
  const inc = S.data.incident;
  const ops = S.data.operations;
  if (ops && ops.operations_summary && ops.operations_summary.active_cases_count > 0) return true;
  return Boolean(inc && inc.incident_id);
}

function activeCaseId() {
  const inc = S.data.incident;
  if (inc && inc.incident_id) return inc.incident_id;
  const ops = S.data.operations;
  if (ops && ops.active_case && ops.active_case.incident_id) return ops.active_case.incident_id;
  return null;
}

function guardCheck(id) {
  const list = (S.data.guard && Array.isArray(S.data.guard.checklist)) ? S.data.guard.checklist : [];
  return list.find((c) => c.id === id) || null;
}

function closeable() {
  return Boolean(S.data.recovery && S.data.recovery.is_verified);
}

/* ══════════════════════════════ causal gating (ADR-008) ══════════════════════════════ */
/* Every event_time in this replay is a naive Lisbon timestamp; comparing them as UTC
   keeps the ordering self-consistent without inventing an offset. */
function tsMs(value) {
  if (!value) return null;
  const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})/);
  if (!m) return null;
  return Date.UTC(+m[1], +m[2] - 1, +m[3], +m[4], +m[5], +m[6]);
}

function eventNowMs() {
  const sim = S.data.simStatus;
  const fromSim = sim && sim.current_event_time ? tsMs(sim.current_event_time) : null;
  if (fromSim !== null) return fromSim;
  const point = latestPoint();
  return point ? tsMs(point.timestamp) : null;
}

/* Milestone clocks are read from the active scenario catalog, never hardcoded here. */
function milestoneMs(fragment) {
  const catalog = S.data.scenarios;
  if (!catalog) return null;
  const active = (catalog.scenarios || []).find((s) => s.scenario_id === catalog.active_scenario_id);
  const milestones = (active && active.milestones) || {};
  const key = Object.keys(milestones).find((k) => k.toLowerCase().includes(fragment));
  return key ? tsMs(milestones[key]) : null;
}

/* The counterfactual benchmark (lead time, LPS breach stamp, anything derived from it)
   describes an event in the future until the event clock reaches it. Sealed until then. */
function benchmarkUnlocked() {
  const lpsMs = milestoneMs('lps');
  const now = eventNowMs();
  return lpsMs !== null && now !== null && now >= lpsMs;
}

function detectionMs() {
  const inc = S.data.incident;
  const fromLead = inc && inc.lead_time ? tsMs(inc.lead_time.earliest_detection_timestamp) : null;
  if (fromLead !== null) return fromLead;
  const card = evidenceCardBySensor('DV_pressure');
  return card && card.provenance ? tsMs(card.provenance.event_time) : null;
}

/* The brake safety threshold is the ActionGuard policy condition returned by the API. */
function brakeSafeThresholdBar() {
  const check = guardCheck('BRAKE_RESERVOIR_PRESSURE_SAFE');
  const label = check && check.label ? String(check.label) : '';
  const m = label.match(/(-?\d+(?:\.\d+)?)\s*bar/);
  return m ? Number(m[1]) : null;
}

/* ══════════════════════════════ master render ══════════════════════════════ */
function render() {
  renderHeader();
  renderKpis();
  renderFleet();
  renderQueue();
  renderWorkbench();
  renderTimeline();
  renderReplayBar();
  renderValidationDrawer();
  renderOperatorRail();
  renderPhaseGates();
}

/* ─────────────── header ─────────────── */
function renderHeader() {
  const ops = S.data.operations;
  const sim = S.data.simStatus;
  renderBootState();
  const point = latestPoint();

  if (ops) {
    /* Two levels on screen; the full Layer A path lives in the tooltip. */
    const crumb = clear($('#breadcrumb'));
    const chain = [
      [ops.fleet.fleet_id, ops.fleet.name],
      [ops.train.train_id, `${ops.train.model} · ${ops.train.car_number}`],
      [ops.subsystem.subsystem_id, ops.subsystem.name],
      [ops.asset.asset_id, ops.asset.name]
    ];
    crumb.title = chain.map(([id, label]) => `${id} ${label}`).join(' › ');
    [[ops.train.train_id, null], [ops.asset.asset_id, 'crumb-leaf']].forEach(([id, cls], i) => {
      if (i > 0) crumb.appendChild(el('span', 'crumb-arrow mono', '›'));
      crumb.appendChild(el('b', 'mono', id));
    });
  }

  const simClock = sim && sim.current_event_time ? sim.current_event_time : (point ? point.timestamp : null);
  const clockNode = $('#event-clock');
  if (clockNode) clockNode.textContent = txt(simClock ? `${utcOf(simClock)} UTC` : (S.degraded ? 'API gián đoạn' : 'luồng dừng'));

  if (sim) {
    const label = $('#stream-pill-label');
    if (label) {
      label.textContent = `${CFG.pillBase}${sim.is_paused ? ' · ĐÃ DỪNG' : ''}`;
    }
    const rate = $('#stream-rate');
    if (rate) {
      const hz = sim.is_paused ? 0 : Number(sim.speed_multiplier) / CFG.samplingIntervalSeconds;
      rate.textContent = `${num(sim.speed_multiplier, 0)}x · ${num(hz, 1)} Hz`;
    }
  }
}

/* ─────────────── KPI strip ─────────────── */
function renderKpis() {
  const ops = S.data.operations;
  const inc = S.data.incident;
  const ev = S.data.evidence;
  const an = S.data.analytics;
  const sim = S.data.simStatus;

  if (ops && ops.operations_summary) {
    const sum = ops.operations_summary;
    kpi('monitored_assets_count', sum.monitored_assets_count, 'info');
    kpi('active_cases_count', sum.active_cases_count, sum.active_cases_count > 0 ? 'crit' : 'ok');
    kpi('assets_observing_count', sum.assets_observing_count, sum.assets_observing_count > 0 ? 'ok' : null);
    kpi('scenario_name', sum.scenario_name, null);
    kpiNote('mode', `kiểu: ${sum.simulation_mode}`);
    const badgeEl = $('#nav-queue-count');
    if (badgeEl) {
      badgeEl.textContent = String(sum.active_cases_count);
      badgeEl.setAttribute('data-hot', sum.active_cases_count > 0 ? 'true' : 'false');
    }
  }

  const state = (inc && inc.lifecycle_state) || 'NONE';
  kpi('phase', state === 'NONE' ? PHASE_LABEL.NONE : txt(PHASE_LABEL[state] || state), state === 'NONE' ? 'ok' : 'crit');
  kpiNote('provenance', sim ? `nguồn: ${sim.provenance}` : 'nguồn: chờ /demo/status');

  kpi('regime', ev ? regimeLabel(ev.regime) : DASH, ev && isLoaded(ev.regime) ? 'info' : 'idle');
  kpiNote('duty', an && an.regime_analytics
    ? `tải trọng: ${num(an.regime_analytics.loaded_duty_cycle_pct, 1)}% · ${an.regime_analytics.loaded_samples_count}/${an.regime_analytics.total_samples_analyzed} mẫu`
    : 'tải trọng: —');
  kpiNote('transient', an && an.alert_fatigue_protection
    ? `nhiễu đã chặn: ${an.alert_fatigue_protection.suppressed_transients_count}`
    : 'nhiễu đã chặn: —');

  const windowLabel = `${CFG.timeframeLabels[S.timeframe]} · ${S.data.window ? S.data.window.count : 0} mẫu · cửa sổ ${S.data.window ? S.data.window.window_size : DASH}s`;
  bind('window-label', windowLabel);
  bind('wb-window-label', windowLabel);
}

/* ─────────────── SCREEN 01: fleet & telemetry ─────────────── */
function renderFleet() {
  renderTree();
  renderAssetGrid();
  renderSensorMatrix();
  renderSuppressionStream();
  renderCharts();
}

function renderTree() {
  const ops = S.data.operations;
  const host = $('#fleet-tree');
  if (!ops || !host) return;
  clear(host);
  const inc = S.data.incident;
  const aRow = el('div', 'tree-node');
  aRow.appendChild(el('span', 'tree-caret mono', '●'));
  aRow.appendChild(el('span', 'tree-id', ops.asset.asset_id));
  aRow.appendChild(el('span', 'tree-desc', ` ${ops.asset.name} · ${ops.asset.discharge_valve_model}`));
  aRow.appendChild(badge(inc ? vlabel(inc.asset_health) : 'CHƯA RÕ', tone(inc && inc.asset_health)));
  const openBtn = el('button', 'mini-btn', 'Mở bàn điều tra');
  openBtn.addEventListener('click', () => setView('workbench'));
  aRow.appendChild(openBtn);

  const levels = [
    { id: ops.fleet.fleet_id, label: ops.fleet.name, chip: `${ops.fleet.operator_name} · ${ops.fleet.depot_location}` },
    { id: ops.train.train_id, label: `${ops.train.model} · ${ops.train.car_number}`, chip: ops.train.service_status },
    { id: ops.subsystem.subsystem_id, label: `${ops.subsystem.name} (${ops.subsystem.subsystem_code})`, chip: `${ops.subsystem.asset_ids.length} tài sản` }
  ];
  let cursor = host;
  levels.forEach((lv) => {
    const row = el('div', 'tree-node');
    row.appendChild(el('span', 'tree-caret mono', '▾'));
    row.appendChild(el('span', 'tree-id', lv.id));
    row.appendChild(el('span', 'tree-desc', ` ${lv.label}`));
    if (lv.chip) row.appendChild(el('span', 'crumb-chip mono', lv.chip));
    cursor.appendChild(row);
    const childWrap = el('div', 'tree-children');
    cursor.appendChild(childWrap);
    cursor = childWrap;
  });
  cursor.appendChild(aRow);
}

function renderAssetGrid() {
  const ops = S.data.operations;
  const tbody = $('#asset-grid tbody');
  const inc = S.data.incident;
  const ev = S.data.evidence;
  if (!ops || !tbody) return;
  clear(tbody);

  const rows = [{
    assetId: ops.asset.asset_id,
    assetName: ops.asset.name,
    train: `${ops.train.train_id} · ${ops.fleet.name}`,
    criticality: ops.asset.criticality,
    health: inc ? inc.asset_health : DASH,
    regime: ev ? regimeLabel(ev.regime) : DASH
  }];

  const q = ($('#asset-search') ? $('#asset-search').value : '').trim().toLowerCase();
  const fh = ($('#filter-health') && $('#filter-health').value) || 'ALL';
  const fr = ($('#filter-regime') && $('#filter-regime').value) || 'ALL';

  const visible = rows.filter((r) => {
    if (q && !`${r.assetId} ${r.assetName} ${r.train}`.toLowerCase().includes(q)) return false;
    if (fh !== 'ALL' && r.health !== fh) return false;
    if (fr !== 'ALL' && r.regime !== fr) return false;
    return true;
  });

  visible.forEach((r) => {
    const tr = el('tr', `row-${tone(r.health) === 'idle' ? 'ok' : tone(r.health)}`);
    const c1 = el('td', 'strong');
    c1.appendChild(el('span', null, r.assetId));
    c1.appendChild(el('span', 'cell-sub mono', `${r.assetName} · ${r.train}`));
    tr.appendChild(c1);
    tr.appendChild(el('td')).appendChild(badge(vlabel(r.criticality), r.criticality === 'CRITICAL' ? 'crit' : 'idle'));
    tr.appendChild(el('td')).appendChild(badge(vlabel(r.health), tone(r.health)));
    tr.appendChild(el('td')).appendChild(badge(r.regime, isLoaded(r.regime) ? 'info' : 'idle'));
    const action = el('td');
    const btn = el('button', 'mini-btn', 'Mở chi tiết');
    btn.addEventListener('click', () => setView('workbench'));
    action.appendChild(btn);
    tr.appendChild(action);
    tbody.appendChild(tr);
  });
  const empty = $('#asset-grid-empty');
  if (empty) empty.hidden = visible.length > 0;
}

const SENSOR_ROWS = [
  { label: 'Chế độ vận hành', key: 'regime', kind: 'regime' },
  { label: 'DV_pressure', key: 'dv_pressure_bar', unit: 'bar', digits: 4, sensor: 'DV_pressure' },
  { label: 'Oil_temperature', key: 'oil_temp_c', unit: '°C', digits: 2, sensor: 'Oil_temperature' },
  { label: 'Motor_current', key: 'motor_current_a', unit: 'A', digits: 3 },
  { label: 'H1_pressure', key: 'h1_bar', unit: 'bar', digits: 4 },
  { label: 'TP2_pressure', key: 'tp2_bar', unit: 'bar', digits: 3 },
  { label: 'TP3_pressure', key: 'tp3_bar', unit: 'bar', digits: 3 },
  { label: 'Bình chứa khí', key: 'reservoirs_bar', unit: 'bar', digits: 3 },
  { label: 'Công tắc LPS', key: 'lps_active', kind: 'digital' },
  { label: 'Công tắc áp suất', key: 'pressure_switch', kind: 'digital' },
  { label: 'Mức dầu thấp', key: 'oil_level_low', kind: 'digital' },
  { label: 'Xung lưu lượng', key: 'caudal_impulses', unit: 'imp', digits: 1 },
  { label: 'TB trượt DV (10p)', key: 'rolling_avg_dv', unit: 'bar', digits: 4, derived: true },
  { label: 'Độ lệch TB DV (10p)', key: 'rolling_std_dv', unit: 'bar', digits: 4, derived: true },
  { label: 'TB trượt Oil_temp (10p)', key: 'rolling_avg_oil_temp', unit: '°C', digits: 2, derived: true }
];

function renderSensorMatrix() {
  const tbody = $('#sensor-matrix tbody');
  const point = latestPoint();
  if (!tbody) return;
  clear(tbody);
  const note = $('[data-bind="matrix-clock"]');
  if (note) note.textContent = point ? `event_time mới nhất ${utcOf(point.timestamp)} UTC` : 'chưa có mẫu trong bộ đệm';
  if (!point) {
    const tr = el('tr'); const td = el('td', 'muted', 'Đang chờ worker ghi mẫu đầu tiên vào luồng.');
    td.colSpan = 3; tr.appendChild(td); tbody.appendChild(tr); return;
  }
  SENSOR_ROWS.forEach((row) => {
    const raw = point[row.key];
    const tr = el('tr');
    tr.appendChild(el('td', 'strong', row.label));
    const cell = el('td', 'mono');
    let valueText;
    if (raw === undefined || raw === null) valueText = DASH;
    else if (row.kind === 'regime') valueText = regimeLabel(raw);
    else if (row.kind === 'digital') valueText = Number(raw) > 0 ? '1 · KÍCH' : '0 · KHÔNG';
    else valueText = `${num(raw, row.digits)} ${row.unit || ''}`.trim();
    cell.textContent = valueText;
    tr.appendChild(cell);

    const status = el('td');
    if (row.sensor) {
      const card = evidenceCardBySensor(row.sensor);
      if (card) {
        status.appendChild(badge(vlabel(card.status), tone(card.status)));
        if (card.sigma_deviation !== null && card.sigma_deviation !== undefined) {
          status.appendChild(el('span', 'cell-sub mono', `Δ ${signed(card.sigma_deviation)}σ so với ${num(card.baseline_value, 2)}`));
        }
      } else {
        status.appendChild(badge('TRONG BASELINE', 'ok'));
      }
    } else if (row.kind === 'digital') {
      status.appendChild(badge(Number(raw) > 0 ? 'KẸP' : 'CỜ Ở 0', Number(raw) > 0 ? 'warn' : 'ok'));
    } else if (row.derived) {
      status.appendChild(badge('MONGO $setWindowFields', 'info'));
    } else if (row.kind === 'regime') {
      status.appendChild(badge(Number(point.motor_current_a) > 0 ? 'KỲ CÓ TẢI' : 'KỲ NGHỈ', 'idle'));
    } else {
      status.appendChild(badge('ĐỌC ĐƯỢC', 'idle'));
    }
    tr.appendChild(status);
    if (row.key === 'dv_pressure_bar') tr.className = `row-${tone((evidenceCardBySensor('DV_pressure') || {}).status || '') || 'ok'}`;
    tbody.appendChild(tr);
  });
}

function renderSuppressionStream() {
  const tbody = $('#suppression-stream tbody');
  const an = S.data.analytics;
  if (!tbody) return;
  clear(tbody);
  const signals = (an && an.alert_fatigue_protection && an.alert_fatigue_protection.recent_suppressed_signals) || [];
  const counter = $('[data-bind="suppression-count"]');
  if (counter) {
    counter.textContent = an
      ? `nhiễu đã chặn: ${an.alert_fatigue_protection.suppressed_transients_count} · mẫu đã xét: ${an.regime_analytics.total_samples_analyzed}`
      : 'nhiễu đã chặn: —';
  }
  const empty = $('#suppression-empty');
  if (empty) empty.hidden = signals.length > 0;
  if (!signals.length) {
    const tr = el('tr'); const td = el('td', 'muted', 'Cửa sổ này không có nhiễu bị chặn.');
    td.colSpan = 6; tr.appendChild(td); tbody.appendChild(tr);
    return;
  }
  signals.slice(0, 12).forEach((sig) => {
    const tr = el('tr', 'row-warn');
    tr.appendChild(el('td', 'mono', utcOf(sig.timestamp)));
    tr.appendChild(el('td', 'mono', sig.asset_id || DASH));
    const reading = el('td', 'mono');
    reading.appendChild(el('span', null, `${sig.signal_code} · ${num(sig.observed_value, 4)}`));
    reading.appendChild(el('span', 'cell-sub', `detector: ${sig.detector_id || DASH}`));
    tr.appendChild(reading);
    tr.appendChild(el('td', 'mono', `${signed(sig.sigma_deviation)}σ`));
    tr.appendChild(el('td', 'mono', regimeLabel(sig.regime)));
    const disp = el('td');
    disp.appendChild(badge(vlabel(sig.disposition || 'SUPPRESSED_TRANSIENT'), 'warn'));
    disp.appendChild(el('span', 'cell-sub', mtxt(sig.reason || '')));
    tr.appendChild(disp);
    tbody.appendChild(tr);
  });
}

/* ══════════════════════════════ CHARTS ══════════════════════════════ */
const CHART_THEME = {
  grid: 'rgba(255,255,255,.045)',
  tick: '#6f8296',
  loaded: 'rgba(55,196,244,.10)',
  unloaded: 'rgba(127,143,161,.06)',
  series: ['#37c4f4', '#ff8a5c', '#3ddc97', '#7aa2ff', '#f5b544']
};

function makeChart(canvasId, series, opts) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;
  if (typeof window.Chart === 'undefined') return renderFallbackChart(canvas, series);
  const config = {
    type: 'line',
    data: { datasets: series.map((s, i) => ({
      label: s.label,
      data: [],
      borderColor: s.color || CHART_THEME.series[i % CHART_THEME.series.length],
      backgroundColor: s.color || CHART_THEME.series[i % CHART_THEME.series.length],
      borderWidth: 1.6,
      pointRadius: 0,
      pointHoverRadius: 3,
      tension: 0,
      spanGaps: false,
      yAxisID: s.axis || 'y',
      stepped: !!s.stepped
    })) },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: series.length > 1, labels: { color: '#a9b8c9', boxWidth: 9, font: { size: 9, family: 'JetBrains Mono' } } },
        tooltip: {
          backgroundColor: '#121b25', borderColor: '#33424f', borderWidth: 1,
          titleFont: { family: 'JetBrains Mono', size: 10 }, bodyFont: { family: 'JetBrains Mono', size: 10 },
          callbacks: {
            title: (items) => `${opts && opts.title ? opts.title : ''} ${items[0].label}`.trim(),
            afterBody: (items) => {
              const meta = items[0].chart.$pointMeta ? items[0].chart.$pointMeta[items[0].dataIndex] : null;
              return meta && meta.p ? [`chế độ: ${meta.p.regime}`, `event_time: ${meta.p.timestamp}`] : [];
            }
          }
        }
      },
      scales: {
        x: {
          type: 'linear',
          grid: { color: CHART_THEME.grid },
          ticks: {
            color: CHART_THEME.tick, font: { size: 9, family: 'JetBrains Mono' }, maxTicksLimit: 8, autoSkip: true,
            callback(value) {
              const chart = this && this.chart;
              return hmsOfAxis(value, chart ? chart.$t0 : null);
            }
          }
        },
        y: { grid: { color: CHART_THEME.grid }, ticks: { color: CHART_THEME.tick, font: { size: 9, family: 'JetBrains Mono' } } }
      }
    },
    plugins: [regimeBandPlugin(), thresholdLinePlugin(), markerLinePlugin()]
  };
  const chart = new window.Chart(canvas.getContext('2d'), config);
  chart.$seriesSpec = series;
  chart.$lines = (opts && opts.lines) || [];
  chart.$markers = [];
  return chart;
}

/* x is elapsed seconds since the first sample of the plotted window. */
function hmsOfAxis(seconds, t0) {
  if (t0 === null || t0 === undefined) return String(Math.round(seconds));
  const d = new Date(t0 + seconds * 1000);
  return `${String(d.getUTCHours()).padStart(2, '0')}:${String(d.getUTCMinutes()).padStart(2, '0')}:${String(d.getUTCSeconds()).padStart(2, '0')}`;
}

/* Samples are placed at their real event_time; a gap wider than the break threshold
   inserts an empty slot so the line stops instead of drawing a bridge over missing data. */
function chartSlots(rows) {
  const t0 = rows.length ? tsMs(rows[0].timestamp) : null;
  const slots = [];
  rows.forEach((p, i) => {
    const t = tsMs(p.timestamp);
    const x = (t === null || t0 === null) ? i : (t - t0) / 1000;
    if (i > 0 && t !== null && slots.length) {
      const prevT = tsMs(rows[i - 1].timestamp);
      if (prevT !== null && (t - prevT) / 1000 > CFG.gapBreakSeconds) {
        slots.push({ x: (prevT + t) / 2000 - t0 / 1000, p: null });
      }
    }
    slots.push({ x, p });
  });
  return { t0, slots };
}

function updateChart(chart, rows, keys) {
  if (!chart) return;
  if (chart.$fallback) { updateFallbackChart(chart, rows, keys); return; }
  const { t0, slots } = chartSlots(rows);
  chart.$t0 = t0;
  chart.$slots = slots;
  chart.data.datasets.forEach((dataset, i) => {
    const key = keys[i];
    dataset.data = slots.map((s) => ({
      x: s.x,
      y: s.p && key && typeof s.p[key] === 'number' ? s.p[key] : null
    }));
  });
  chart.$pointMeta = slots.map((s) => ({ x: s.x, p: s.p }));
  chart.update('none');
}

function regimeBandPlugin() {
  return {
    id: 'regimeBands',
    beforeDraw(chart) {
      if (!S.shading) return;
      const meta = (chart.$pointMeta || []).filter((m) => m.p);
      const { ctx, chartArea, scales } = chart;
      if (!chartArea || meta.length < 2) return;
      const half = Math.max(1, (chartArea.width / meta.length) / 2);
      ctx.save();
      let i = 0;
      while (i < meta.length) {
        const loaded = isLoaded(meta[i].p.regime);
        let j = i;
        while (j + 1 < meta.length && isLoaded(meta[j + 1].p.regime) === loaded
          && meta[j + 1].x - meta[j].x <= CFG.gapBreakSeconds) j += 1;
        const x0 = i === 0 ? chartArea.left : scales.x.getPixelForValue(meta[i].x) - half;
        const x1 = j === meta.length - 1 ? chartArea.right : scales.x.getPixelForValue(meta[j].x) + half;
        ctx.fillStyle = loaded ? CHART_THEME.loaded : CHART_THEME.unloaded;
        ctx.fillRect(x0, chartArea.top, Math.max(1, x1 - x0), chartArea.bottom - chartArea.top);
        if (loaded && (i === 0 || !isLoaded(meta[i - 1].p.regime))) {
          ctx.fillStyle = 'rgba(55,196,244,.55)';
          ctx.fillRect(x0, chartArea.top, 1, chartArea.bottom - chartArea.top);
        }
        i = j + 1;
      }
      ctx.restore();
    }
  };
}

function thresholdLinePlugin() {
  return {
    id: 'thresholdLines',
    afterDatasetsDraw(chart) {
      if (!S.thresholds) return;
      const lines = (chart.$lines || []).filter((l) => !l.engineering || S.engineering);
      const { ctx, chartArea, scales } = chart;
      ctx.save();
      lines.filter((l) => typeof l.value === 'number' && !Number.isNaN(l.value)).forEach((line) => {
        const y = scales.y.getPixelForValue(line.value);
        if (y < chartArea.top || y > chartArea.bottom) return;
        ctx.beginPath();
        ctx.setLineDash([5, 4]);
        ctx.strokeStyle = line.color || '#f5b544';
        ctx.lineWidth = 1;
        ctx.moveTo(chartArea.left, y);
        ctx.lineTo(chartArea.right, y);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = line.color || '#f5b544';
        ctx.font = '9px JetBrains Mono, monospace';
        ctx.fillText(`${line.label} ${num(line.value, line.digits === undefined ? 3 : line.digits)}`, chartArea.left + 4, y - 3);
      });
      ctx.restore();
    }
  };
}

/* Vertical event markers, e.g. the moment the case opened. */
function markerLinePlugin() {
  return {
    id: 'eventMarkers',
    afterDatasetsDraw(chart) {
      const markers = chart.$markers || [];
      const { ctx, chartArea, scales } = chart;
      ctx.save();
      markers.forEach((marker) => {
        const x = scales.x.getPixelForValue(marker.x);
        if (x < chartArea.left || x > chartArea.right) return;
        ctx.beginPath();
        ctx.setLineDash([3, 3]);
        ctx.strokeStyle = marker.color || '#ff8a5c';
        ctx.lineWidth = 1.2;
        ctx.moveTo(x, chartArea.top);
        ctx.lineTo(x, chartArea.bottom);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = marker.color || '#ff8a5c';
        ctx.font = '9px JetBrains Mono, monospace';
        ctx.fillText(marker.label, Math.min(x + 4, chartArea.right - 60), chartArea.top + 9);
      });
      ctx.restore();
    }
  };
}

/* Minimal SVG fallback if the Chart.js CDN is unreachable (keeps charts honest, not empty). */
function renderFallbackChart(canvas, series) {
  const wrap = canvas && canvas.parentNode;
  if (!wrap) return null;
  clear(wrap);
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('class', 'chart-fallback');
  svg.setAttribute('preserveAspectRatio', 'none');
  svg.setAttribute('viewBox', '0 0 100 40');
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', series.map((s) => s.label).join(', '));
  const api = { $fallback: true, $svg: svg, $spec: series, $pointMeta: [], data: { labels: [] } };
  series.forEach((s, i) => {
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', s.color || CHART_THEME.series[i % CHART_THEME.series.length]);
    path.setAttribute('stroke-width', '0.7');
    path.setAttribute('vector-effect', 'non-scaling-stroke');
    svg.appendChild(path);
  });
  wrap.appendChild(svg);
  return api;
}

function updateFallbackChart(chart, rows, keys) {
  if (!rows.length) return;
  const paths = Array.from(chart.$svg.children);
  const lo = -0.05, hi = 1.05;
  keys.forEach((k, i) => {
    const vals = rows.map((p) => (typeof p[k] === 'number' ? p[k] : null));
    const nums = vals.filter((v) => v !== null);
    if (!nums.length || !paths[i]) return;
    const min = Math.min(...nums);
    const max = Math.max(...nums);
    const span = (max - min) || 1;
    const pts = vals.map((v, idx) => {
      const x = ((idx / (vals.length - 1 || 1)) * (hi - lo) + lo) * 100;
      const y = v === null ? null : (40 - (((v - min) / span) * 34 + 3));
      return v === null ? null : `${x.toFixed(2)},${y.toFixed(2)}`;
    }).filter(Boolean).join(' ');
    paths[i].setAttribute('points', pts);
  });
  chart.$pointMeta = rows.map((p) => ({ regime: p.regime, eventTime: p.timestamp }));
}

function chartLines() {
  const rec = S.data.recovery;
  const dvCard = evidenceCardBySensor('DV_pressure');
  const oilCard = evidenceCardBySensor('Oil_temperature');
  const dvStats = statsFor('dv_pressure_bar');
  const oilStats = statsFor('oil_temp_c');
  const currentStats = statsFor('motor_current_a');
  const unloaded = chronologicalPoints().filter((p) => !isLoaded(p.regime) && typeof p.motor_current_a === 'number');
  const maxUnloaded = unloaded.length ? Math.max(...unloaded.map((p) => p.motor_current_a)) : null;
  const loadGate = (currentStats && maxUnloaded !== null) ? (currentStats.min + maxUnloaded) / 2 : null;
  const an = S.data.analytics;
  /* The plotted baselines are the same healthy baselines the evidence table quotes;
     the rolling 3σ band is MongoDB $setWindowFields work and stays behind the engineering toggle. */
  return {
    dv: [
      { label: 'baseline lành', value: dvCard ? dvCard.baseline_value : null, color: '#7aa2ff' },
      { label: 'ngưỡng nghiệm thu', value: rec && rec.criteria ? rec.criteria.dv_pressure_max : null, color: '#3ddc97' },
      { label: 'băng 3σ cửa sổ', value: dvStats ? dvStats.mean + 3 * dvStats.std : null, color: '#f5b544', engineering: true }
    ],
    oil: [
      { label: 'baseline lành', value: oilCard ? oilCard.baseline_value : null, color: '#7aa2ff' },
      { label: 'ngưỡng nghiệm thu', value: rec && rec.criteria ? rec.criteria.oil_temp_max : null, color: '#3ddc97' },
      { label: 'băng 3σ cửa sổ', value: oilStats ? oilStats.mean + 3 * oilStats.std : null, color: '#f5b544', engineering: true }
    ],
    current: [{ label: 'ngưỡng LOADED/UNLOADED (suy từ dữ liệu)', value: loadGate, color: '#37c4f4', digits: 2 }],
    tp: [{ label: 'TP3 thấp nhất cửa sổ', value: an && an.regime_analytics ? an.regime_analytics.min_tp3_bar : null, color: '#f5b544', digits: 2 }],
    ifScore: [{ label: 'ngưỡng AI xác nhận', value: (evidenceCardByCode('CORROBORAT') || {}).baseline_value, color: '#f5b544', digits: 3 }]
  };
}

/* When a case is open the charts frame the event instead of the whole buffer. */
function chartWindowRows() {
  const rows = chronologicalPoints();
  const det = detectionMs();
  if (det === null || rows.length < 2) return rows;
  const from = det - CFG.detectionWindowSeconds * 1000;
  const kept = rows.filter((p) => {
    const t = tsMs(p.timestamp);
    return t === null || t >= from;
  });
  return kept.length > 1 ? kept : rows;
}

/* Honest scale: the Y axis never auto-zooms noise into a trend. */
function applyYBounds(chart, rows, keys, lines) {
  if (!chart || chart.$fallback || !chart.options || !chart.options.scales) return;
  const y = chart.options.scales.y;
  const values = [];
  keys.forEach((k) => rows.forEach((p) => { if (typeof p[k] === 'number') values.push(p[k]); }));
  const refs = (lines || []).filter((l) => !l.engineering && typeof l.value === 'number');
  if (!values.length) { delete y.min; delete y.max; return; }
  const dataMin = Math.min(...values);
  const dataMax = Math.max(...values);
  const refMin = refs.length ? Math.min(...refs.map((l) => l.value)) : dataMin;
  const refMax = refs.length ? Math.max(...refs.map((l) => l.value)) : dataMax;
  const floor = chart.$zeroAnchored ? Math.min(0, dataMin) : Math.min(dataMin, refMin);
  const top = Math.max(dataMax, refMax * 1.2);
  const pad = Math.max((top - floor) * 0.06, 0.01);
  y.min = Number((floor - pad).toFixed(3));
  y.max = Number((top + pad).toFixed(3));
}

function applyDetectionMarker(chart) {
  if (!chart || chart.$fallback) return;
  const det = detectionMs();
  const t0 = chart.$t0;
  chart.$markers = (det !== null && t0 !== null && det >= t0)
    ? [{ x: (det - t0) / 1000, label: 'Phát hiện', color: '#ff8a5c' }]
    : [];
}

let chartsReady = false;
function ensureCharts() {
  if (chartsReady) return;
  const lines = chartLines();
  S.charts.dv = makeChart('chart-dv', [{ label: 'DV_pressure (bar)' }], { lines: lines.dv, title: 'DV_pressure' });
  S.charts.oil = makeChart('chart-oil', [{ label: 'Oil_temp (°C)' }], { lines: lines.oil, title: 'Oil_temp' });
  S.charts.current = makeChart('chart-current', [{ label: 'Motor_current (A)' }], { lines: lines.current, title: 'Motor_current' });
  S.charts.tp = makeChart('chart-tp', [
    { label: 'TP2 (bar)' }, { label: 'TP3 (bar)', color: '#3ddc97' }, { label: 'Bình chứa (bar)', color: '#f5b544' }
  ], { lines: lines.tp, title: 'Mạng phanh khí nén' });
  S.charts.dv.$zeroAnchored = true;
  S.chartsReady = chartsReady = true;
  const notice = $('#chart-notice');
  if (notice && typeof window.Chart === 'undefined') {
    notice.hidden = false;
    notice.textContent = 'Không tải được Chart.js — dùng SVG nội tuyến từ cùng payload /api/telemetry/window. Không bịa giá trị.';
  }
}

function renderCharts() {
  ensureCharts();
  const rows = chartWindowRows();
  const lines = chartLines();
  setLines(S.charts.dv, lines.dv);
  setLines(S.charts.oil, lines.oil);
  setLines(S.charts.current, lines.current);
  setLines(S.charts.tp, lines.tp);

  paintChart(S.charts.dv, rows, ['dv_pressure_bar'], lines.dv);
  paintChart(S.charts.oil, rows, ['oil_temp_c'], lines.oil);
  paintChart(S.charts.current, rows, ['motor_current_a'], lines.current);
  paintChart(S.charts.tp, rows, ['tp2_bar', 'tp3_bar', 'reservoirs_bar'], lines.tp);

  renderIfGauge();
}

function paintChart(chart, rows, keys, lines) {
  updateChart(chart, rows, keys);
  applyYBounds(chart, rows, keys, lines);
  applyDetectionMarker(chart);
  if (chart && !chart.$fallback) chart.update('none');
}

function setLines(chart, lines) {
  if (!chart || chart.$fallback) return;
  chart.$lines = lines || [];
}

function renderIfGauge() {
  const card = evidenceCardByCode('CORROBORAT');
  const fill = $('#if-fill');
  const mark = $('#if-mark');
  const read = $('#if-read');
  if (!card) {
    if (fill) fill.style.width = '0%';
    if (mark) mark.style.left = '50%';
    if (read) read.textContent = 'Isolation Forest chưa cho điểm xác nhận cho cửa sổ này';
    return;
  }
  const score = Number(card.observed_value) || 0;
  const thr = Number(card.baseline_value) || 0;
  const scaleMax = Math.max(0.5, score * 1.25, thr * 1.5);
  if (fill) fill.style.width = `${Math.min(100, (score / scaleMax) * 100)}%`;
  if (mark) mark.style.left = `${Math.min(100, (thr / scaleMax) * 100)}%`;
  if (read) {
    const feats = (card.provenance && (card.provenance.feature_count || (card.provenance.feature_names || []).length)) || null;
    read.textContent = `${num(score, 4)} so ngưỡng ${num(thr, 3)} · ${vlabel(card.status)}${feats ? ` · ${feats} đặc trưng LOADED` : ''}`;
  }
}

/* ══════════════════════════════ SCREEN 02: queue ══════════════════════════════ */
function renderQueue() {
  renderQueueCards();
  renderArchive();
}

function renderQueueCards() {
  const host = $('#queue-cards');
  const ops = S.data.operations;
  const inc = S.data.incident;
  if (!host) return;
  clear(host);
  const active = (ops && ops.active_case) || (inc && inc.incident_id ? inc : null);
  const opsSafe = ops || { train: {}, fleet: {}, asset: {} };
  const empty = $('#queue-empty');
  if (empty) empty.hidden = Boolean(active);
  if (!active) {
    const idle = el('div', 'case-card');
    idle.style.borderLeftColor = 'var(--ok)';
    idle.appendChild(el('div', 'case-id', 'KHÔNG CA MỞ'));
    const dl = el('dl', 'case-grid');
    pushDl(dl, [['Giai đoạn', inc ? `${vlabel(inc.lifecycle_state)} · ${vlabel(inc.asset_health)}` : DASH]]);
    idle.appendChild(dl);
    const actions = el('div', 'case-actions');
    const btn = el('button', 'mini-btn', 'Mở lưới cảm biến');
    btn.addEventListener('click', () => setView('fleet'));
    actions.appendChild(btn);
    idle.appendChild(actions);
    host.appendChild(idle);
    return;
  }

  const q = $('#case-search') ? $('#case-search').value.trim().toLowerCase() : '';
  const ackFilter = ($('#filter-ack') && $('#filter-ack').value) || 'ALL';
  const acked = Boolean(inc && inc.acknowledged);
  const ackToken = acked ? 'ACKED' : 'UNACKED';
  if (q && !`${active.incident_id || ''} ${active.asset_id || ''} ${opsSafe.train.train_id || ''}`.toLowerCase().includes(q)) return;
  if (ackFilter !== 'ALL' && ackFilter !== ackToken) return;

  const guard = S.data.guard;
  const card = el('div', 'case-card');
  card.setAttribute('data-ack', acked ? 'true' : 'false');
  const top = el('div', 'case-top');
  top.appendChild(el('span', 'case-id', active.incident_id || DASH));
  top.appendChild(el('span', 'case-prio', inc ? inc.priority : DASH));
  top.appendChild(badge(ackToken, acked ? 'ok' : 'crit'));
  card.appendChild(top);

  const dl = el('dl', 'case-grid');
  const dvCard = evidenceCardBySensor('DV_pressure');
  const oilCard = evidenceCardBySensor('Oil_temperature');
  const ifCard = evidenceCardByCode('CORROBORAT');
  pushDl(dl, [
    ['Tài sản / Tàu', `${active.asset_id || DASH} · ${opsSafe.train.train_id || DASH} (${opsSafe.fleet.name || DASH})`],
    ['Giai đoạn', `${vlabel(active.lifecycle_state)} · ${vlabel(active.asset_health)} · tin cậy ${vlabel(active.operational_confidence)}`],
    ['Người phụ trách', acked ? `${inc.acknowledged_by}` : 'chưa nhận'],
    ['Bằng chứng', dvCard ? `DV ${signed(dvCard.sigma_deviation)}σ (${num(dvCard.observed_value, 4)} ${dvCard.unit})` : DASH],
    ['Nhiệt', oilCard ? `Oil ${signed(oilCard.sigma_deviation)}σ (${num(oilCard.observed_value, 2)} ${oilCard.unit})` : 'chờ trôi nhiệt'],
    ['AI', ifCard ? `${num(ifCard.observed_value, 4)} → ${vlabel(ifCard.status)}` : 'chờ xác nhận'],
    ['ActionGuard', guardSummary(guard)],
    ['Lệnh công tác', inc && inc.work_order ? `${inc.work_order.work_order_id} · ${vlabel(inc.work_order.status)} → ${inc.work_order.target_depot}` : 'chưa phát'],
    ['Tóm tắt', mtxt(active.summary) || DASH]
  ]);
  card.appendChild(dl);

  const actions = el('div', 'case-actions');
  if (!acked) {
    const ackBtn = el('button', 'mini-btn', 'Xác nhận ngay');
    ackBtn.addEventListener('click', () => {
      setView('workbench');
      runOperatorAction('acknowledge');
    });
    actions.appendChild(ackBtn);
  }
  const openBtn = el('button', 'mini-btn', 'Mở bàn điều tra');
  openBtn.addEventListener('click', () => setView('workbench'));
  actions.appendChild(openBtn);
  const tlBtn = el('button', 'mini-btn', 'Sổ theo dõi');
  tlBtn.addEventListener('click', () => setView('timeline'));
  actions.appendChild(tlBtn);
  card.appendChild(actions);
  host.appendChild(card);
}

function pushDl(dl, pairs) {
  pairs.forEach(([k, v]) => {
    dl.appendChild(el('dt', null, k));
    dl.appendChild(el('dd', null, v === null || v === undefined || v === '' ? DASH : String(v)));
  });
}

function renderArchive() {
  const tbody = $('#archive-grid tbody');
  if (!tbody) return;
  clear(tbody);
  const events = S.data.events || [];
  const closed = events.filter((e) => ['CASE_CLOSED', 'CLOSED'].includes(String(e.event_type).toUpperCase()));
  const empty = $('#archive-empty');
  if (empty) empty.hidden = closed.length > 0;
  const counter = $('[data-bind="archive-count"]');
  if (counter) counter.textContent = `đã nghiệm thu: ${closed.length}`;
  if (!closed.length) {
    const tr = el('tr'); const td = el('td', 'muted', 'Chưa có nghiệm thu trong phiên này.');
    td.colSpan = 5; tr.appendChild(td); tbody.appendChild(tr);
    return;
  }
  const ops = S.data.operations;
  closed.slice().reverse().forEach((e) => {
    const tr = el('tr', 'row-ok');
    const c1 = el('td', 'mono');
    c1.appendChild(el('span', null, e.case_id || DASH));
    c1.appendChild(el('span', 'cell-sub', clockOf(e.event_time)));
    tr.appendChild(c1);
    tr.appendChild(el('td', 'mono', ops ? `${ops.asset.asset_id} / ${ops.train.train_id}` : DASH));
    tr.appendChild(el('td', null, (e.provenance && (e.provenance.root_cause || e.provenance.root_cause_tag)) || e.detail || DASH));
    tr.appendChild(el('td', 'mono', utcOf(e.event_time)));
    tr.appendChild(el('td')).appendChild(badge(e.provenance && e.provenance.root_cause ? 'CÓ NGUYÊN NHÂN' : 'KHÔNG PHÂN LOẠI', e.provenance && e.provenance.root_cause ? 'ok' : 'idle'));
    tbody.appendChild(tr);
  });
}

/* ══════════════════════════════ SCREENS 03–06: workbench ══════════════════════════════ */
function renderWorkbench() {
  const inc = S.data.incident;
  const ops = S.data.operations;
  const guard = S.data.guard;
  const rec = S.data.recovery;
  const an = S.data.analytics;

  bind('wb-case-id', activeCaseId() || 'CHƯA CÓ VỤ VIỆC');
  bind('wb-asset', ops ? `${ops.asset.asset_id} · ${ops.train.train_id} · ${ops.fleet.name}` : DASH);

  const hasCase = hasActiveCase();
  const state = (inc && inc.lifecycle_state) || 'NONE';
  setChip('[data-bind="chip-health"]', inc ? `SỨC KHỎE ${vlabel(inc.asset_health)}` : 'SỨC KHỎE —', tone(inc && inc.asset_health));
  setChip('[data-bind="chip-ack"]', hasCase && inc ? (inc.acknowledged ? `ĐÃ XÁC NHẬN ${inc.acknowledged_by || ''}` : 'CHƯA XÁC NHẬN') : 'CHƯA XÁC NHẬN —', hasCase ? (inc && inc.acknowledged ? 'ok' : 'crit') : null);
  setChip('[data-bind="chip-guard"]', hasCase && guard ? `Chốt an toàn ${guard.passed_count}/${guard.total_checks}` : 'Chốt an toàn —', hasCase && guard ? (guard.is_permitted ? 'ok' : 'warn') : null);

  const rw = inc ? inc.runtime_warning : null;
  const warningActive = Boolean(rw && rw.is_warning_active);
  const unlocked = benchmarkUnlocked();
  const lead = unlocked && inc && inc.lead_time ? inc.lead_time.lead_time_formatted : null;
  const leadRow = $('#wb-lead-row');
  if (leadRow) leadRow.hidden = !lead;
  bind('wb-lead', lead || DASH, lead ? 'crit' : 'idle');
  bind('wb-elapsed', warningActive ? stripPlus(rw.elapsed_warning_formatted) : DASH, warningActive ? 'crit' : 'idle');
  bind('wb-onset', inc && inc.lead_time ? utcOf(inc.lead_time.earliest_detection_timestamp) : DASH);
  bind('wb-legacy', rw ? (rw.legacy_lps_still_silent ? 'im lặng' : 'đã kích hoạt') : DASH, rw && rw.legacy_lps_still_silent ? 'ok' : 'crit');
  const tp3 = rw ? rw.brake_reservoir_tp3_bar : null;
  bind('wb-tp3', tp3 === null || tp3 === undefined ? DASH : `${num(tp3, 2)} bar`);
  const brakeThreshold = brakeSafeThresholdBar();
  const margin = (typeof tp3 === 'number' && brakeThreshold !== null) ? tp3 - brakeThreshold : null;
  bind('wb-margin', margin === null ? DASH : `${signed(margin, 2)} bar`, margin !== null && margin > 0 ? 'ok' : 'crit');

  const calm = $('#wb-calm');
  if (calm) {
    const suppressed = an && an.alert_fatigue_protection ? an.alert_fatigue_protection.suppressed_transients_count : null;
    calm.textContent = suppressed === null ? 'Đang giám sát' : `Đang giám sát · đã chặn ${suppressed} nhiễu`;
    calm.hidden = hasCase;
  }
  const alertBox = $('#wb-alert');
  if (alertBox) alertBox.hidden = !hasCase;

  bind('wb-summary', inc ? mtxt(inc.summary) : DASH);
  bind('wb-confidence', inc ? `${inc.operational_confidence}` : DASH);

  renderBusinessContext();
  renderEvidenceCards();
  renderDeltaTable();
  renderGuardTable();
  renderRecoveryBlock();
  applyWorkbenchFocus();
}

function setChip(selector, text, toneValue) {
  const node = $(selector);
  if (!node) return;
  node.textContent = text;
  if (toneValue) node.setAttribute('data-tone', toneValue); else node.removeAttribute('data-tone');
}

function setChipVisible(selector, visible) {
  const node = $(selector);
  if (node) node.hidden = !visible;
}

function blockPhaseVisible(block, vis) {
  if (block.dataset.step) return vis.steps.includes(Number(block.dataset.step));
  if (block.closest('.pane-center')) {
    const name = block.getAttribute('data-block');
    if (name === 'guard') return vis.guard;
    if (name === 'recovery') return vis.recovery;
  }
  return true;
}

function renderPhaseGates() {
  const state = (S.data.incident && S.data.incident.lifecycle_state) || 'NONE';
  const vis = PHASE_VISIBILITY[state] || PHASE_VISIBILITY.NONE;
  const hasCase = hasActiveCase();

  /* The workbench opens exactly the step the case is in: focus tab AND lifecycle phase must allow it. */
  const focusMap = { changed: ['changed'], evidence: ['evidence'], guard: ['guard'], recovery: ['recovery'], audit: ['guard', 'recovery'] };
  const show = focusMap[S.wbFocus] || ['changed'];
  $$('#view-workbench .block[data-block]').forEach((b) => {
    b.hidden = !(show.includes(b.getAttribute('data-block')) && blockPhaseVisible(b, vis));
  });

  setChipVisible('[data-bind="chip-ack"]', hasCase);
  setChipVisible('[data-bind="chip-guard"]', hasCase);
}

function renderBusinessContext() {
  const host = $('.pane-left .block:nth-child(3) .kv-list');
  if (!host || !S.data.operations) return;
  clear(host);
  const ops = S.data.operations;
  const inc = S.data.incident;
  const pairs = [
    ['Hạm đội', `${ops.fleet.name} (${ops.fleet.fleet_id}) · ${ops.fleet.operator_name}`],
    ['Tàu', `${ops.train.train_id} · ${ops.train.model} · ${ops.train.car_number}`],
    ['Phân hệ', `${ops.subsystem.name} (${ops.subsystem.subsystem_id})`],
    ['Tài sản', `${ops.asset.name} (${ops.asset.asset_id}) · ${ops.asset.service_role}`],
    ['Thiết bị', `${ops.asset.discharge_valve_model} · định mức ${num(ops.asset.rated_pressure_bar, 1)} bar`],
    ['Depot', ops.fleet.depot_location],
    ['Tầng ngữ cảnh', ops.fleet.is_illustrative_context ? 'Layer A minh hoạ; số liệu là MetroPT-3 thật' : 'Layer A đã xác minh']
  ];
  pairs.forEach(([k, v]) => {
    const row = el('div');
    row.appendChild(el('dt', null, k));
    row.appendChild(el('dd', 'mono', v));
    host.appendChild(row);
  });
  if (inc && inc.work_order) {
    const row = el('div');
    row.appendChild(el('dt', null, 'Lệnh công tác'));
    row.appendChild(el('dd', 'mono', `${inc.work_order.work_order_id} · ${vlabel(inc.work_order.status)}`));
    host.appendChild(row);
  }
}

const EV_TITLE = { PRESSURE: 'THẺ A · ÁP SUẤT VAN XẢ', THERMAL: 'THẺ B · NHIỆT ĐỘ DẦU', TEMPORAL: 'THẺ C · ĐỘ BỀN BƯỚC NHẢY', CORROBORAT: 'THẺ D · ISOLATION FOREST', LPS: 'THẺ E · CÔNG TẮC ÁP THẤP' };

function evidenceTitleOf(card) {
  const code = String(card.code || '').toUpperCase();
  if (code.includes('PRESSURE')) return EV_TITLE.PRESSURE;
  if (code.includes('THERMAL')) return EV_TITLE.THERMAL;
  if (code.includes('TEMPORAL')) return EV_TITLE.TEMPORAL;
  if (code.includes('CORROBORAT') || code.includes('ML_')) return EV_TITLE.CORROBORAT;
  if (code.includes('LPS')) return EV_TITLE.LPS;
  return `THẺ · ${mtxt(card.signal_name) || code}`;
}

function renderEvidenceCards() {
  const host = $('#evidence-list');
  if (!host) return;
  clear(host);
  const pack = (S.data.evidence && S.data.evidence.evidence_pack) || [];
  if (!pack.length) {
    const box = el('div', 'ev-card');
    box.appendChild(el('div', 'ev-name', 'Chưa có bằng chứng ở mẫu hiện tại'));
    box.appendChild(el('div', 'ev-prov', `chế độ ${regimeLabel(S.data.evidence && S.data.evidence.regime)} · detector chạy mỗi nhịp`));
    host.appendChild(box);
  }
  pack.forEach((card) => {
    const box = el('div', 'ev-card');
    box.setAttribute('data-tone', tone(card.status));
    const top = el('div', 'ev-top');
    top.appendChild(el('span', 'ev-name', evidenceTitleOf(card)));
    const statusWrap = el('span');
    statusWrap.appendChild(badge(card.status, tone(card.status)));
    if (card.is_primary) statusWrap.appendChild(el('span', 'cell-sub mono', 'chính'));
    top.appendChild(statusWrap);
    box.appendChild(top);
    box.appendChild(el('div', 'ev-name mono', card.signal_name || card.code));

    const vals = el('div', 'ev-vals');
    vals.appendChild(miniVal('Quan trắc', `${num(card.observed_value, 4)} ${card.unit || ''}`));
    vals.appendChild(miniVal('Baseline', `${num(card.baseline_value, 4)} ${card.unit || ''}`));
    vals.appendChild(miniVal('Độ lệch', card.sigma_deviation === null || card.sigma_deviation === undefined ? DASH : `${signed(card.sigma_deviation)}σ`));
    box.appendChild(vals);

    const prov = el('div', 'ev-prov');
    const p = card.provenance || {};
    prov.appendChild(provLine('source', p.source || p.detector_class || DASH));
    prov.appendChild(provLine('method', p.method || DASH));
    prov.appendChild(provLine('event_time', utcOf(p.event_time)));
    prov.appendChild(provLine('regime', regimeLabel(p.regime)));
    if (p.feature_count || p.feature_names) {
      prov.appendChild(provLine('features', `${p.feature_count || (p.feature_names || []).length}: ${(p.feature_names || []).join(', ')}`));
    }
    if (p.step_diff !== undefined) {
      prov.appendChild(provLine('step Δ', `${num(p.step_diff, 4)} bar · ${p.recent_observations}/${p.required_observations} kỳ gần đây · liên tục ${p.is_temporally_contiguous ? 'có' : 'không'}`));
    }
    if (p.role) prov.appendChild(provLine('role', p.role));
    box.appendChild(prov);
    host.appendChild(box);
  });

  const dots = clear($('#persist-dots'));
  const persistence = S.data.evidence && S.data.evidence.persistence;
  const required = persistence ? persistence.required_observations : null;
  const recent = persistence ? persistence.recent_observations : null;
  if (persistence) {
    for (let i = 0; i < Math.max(required, 1); i += 1) {
      const dot = el('span', 'pdot');
      dot.setAttribute('data-on', i < recent ? 'true' : 'false');
      dots.appendChild(dot);
    }
  }
  /* This counter only ever describes the window being polled now, never the case:
     an open case was confirmed on an earlier window, so 0/3 here is not a contradiction. */
  bind('persist-text', persistence
    ? `${recent}/${required} chu kỳ LOADED cửa sổ hiện tại · ${
        hasActiveCase()
          ? (persistence.confirmed ? 'đang tái xác nhận' : 'ca đã mở, cửa sổ này chưa đủ')
          : (persistence.confirmed ? 'đủ điều kiện mở ca' : 'chưa đủ — chặn nhiễu thoáng qua')
      }`
    : DASH);
}

function miniVal(label, value) {
  const box = el('div', 'ev-val');
  box.appendChild(el('span', null, label));
  box.appendChild(el('b', null, value));
  return box;
}

function provLine(k, v) {
  const line = el('div');
  line.appendChild(el('span', null, `${k}: `));
  line.appendChild(el('b', null, v));
  return line;
}

function renderDeltaTable() {
  const tbody = $('#delta-table tbody');
  if (!tbody) return;
  clear(tbody);
  const pack = (S.data.evidence && S.data.evidence.evidence_pack) || [];
  const rec = S.data.recovery;
  const point = latestPoint();
  const state = (S.data.incident && S.data.incident.lifecycle_state) || 'NONE';
  if (!pack.length) {
    const tr = el('tr'); const td = el('td', 'muted', 'Chưa có bằng chứng ở mẫu hiện tại.');
    td.colSpan = 5; tr.appendChild(td); tbody.appendChild(tr);
    return;
  }
  pack.forEach((card) => {
    const tr = el('tr', `row-${tone(card.status) === 'idle' ? 'ok' : tone(card.status)}`);
    tr.appendChild(el('td', 'strong', mtxt(card.signal_name)));
    tr.appendChild(el('td', 'mono', `${num(card.observed_value, 4)} ${card.unit || ''}`));
    tr.appendChild(el('td', 'mono', num(card.baseline_value, 4)));
    tr.appendChild(el('td', 'mono', card.sigma_deviation === null || card.sigma_deviation === undefined ? DASH : `${signed(card.sigma_deviation)}σ`));
    const st = el('td');
    st.appendChild(badge(card.status, tone(card.status)));
    st.appendChild(el('span', 'cell-sub mono', `${card.code} · ${card.provenance && card.provenance.source ? card.provenance.source : DASH}`));
    tr.appendChild(st);
    tbody.appendChild(tr);
  });
  if (point && rec && rec.criteria && recoveryPhase(state)) {
    const tr = el('tr');
    tr.appendChild(el('td', 'strong', 'Chốt nghiệm thu (mẫu mới nhất)'));
    tr.appendChild(el('td', 'mono', `DV ${num(point.dv_pressure_bar, 4)} · Oil ${num(point.oil_temp_c, 2)}`));
    tr.appendChild(el('td', 'mono', `< ${num(rec.criteria.dv_pressure_max, 3)} · < ${num(rec.criteria.oil_temp_max, 1)}`));
    tr.appendChild(el('td', 'mono', regimeLabel(point.regime)));
    const ok = point.dv_pressure_bar < rec.criteria.dv_pressure_max && point.oil_temp_c < rec.criteria.oil_temp_max && regimeLabel(point.regime) === 'LOADED';
    const st = el('td');
    st.appendChild(badge(ok ? 'ĐẠT TIÊU CHÍ NGHIỆM THU' : 'CHƯA ĐẠT TIÊU CHÍ', ok ? 'ok' : 'warn'));
    tr.appendChild(st);
    tbody.appendChild(tr);
  }
}

/* "4/5 DENIED" reads as if four gates were refused; the console states what passes and what is missing. */
function guardSummary(guard) {
  if (!guard) return DASH;
  const missing = (guard.checklist || []).filter((c) => !c.passed).map((c) => c.id);
  const head = `Chốt an toàn ${guard.passed_count}/${guard.total_checks} đạt`;
  return missing.length ? `${head} · còn thiếu: ${missing.join(', ')}` : `${head} · được phép điều độ`;
}

function renderGuardTable() {
  const tbody = $('#guard-table tbody');
  const box = $('#guard-denial');
  const guard = S.data.guard;
  if (!tbody) return;
  clear(tbody);
  bind('guard-count', guard ? `${guard.passed_count}/${guard.total_checks} chốt đạt` : DASH);
  const list = (guard && guard.checklist) || [];
  if (!list.length) {
    const tr = el('tr'); const td = el('td', 'muted', 'ActionGuard chưa được đánh giá.');
    td.colSpan = 4; tr.appendChild(td); tbody.appendChild(tr);
  }
  list.forEach((check, i) => {
    const tr = el('tr');
    tr.appendChild(el('td', 'mono', `${i + 1} · ${check.id}`));
    tr.appendChild(el('td', null, vlabel(check.label)));
    tr.appendChild(el('td', 'mono', check.current_value === null || check.current_value === undefined ? DASH : check.current_value));
    const st = el('td');
    st.appendChild(badge(check.passed ? 'PASS' : 'FAIL', check.passed ? 'ok' : 'crit'));
    tr.appendChild(st);
    if (!check.passed) tr.className = 'row-crit';
    tbody.appendChild(tr);
  });
  if (box) {
    clear(box);
    if (!guard) { box.setAttribute('data-tone', 'denied'); box.textContent = 'Chưa đọc được chốt an toàn.'; return; }
    box.setAttribute('data-tone', guard.is_permitted ? 'permitted' : 'denied');
    const detail = guard.is_permitted ? '' : ` — ${mtxt(guard.denial_reason || '')}`;
    box.textContent = `${guardSummary(guard)}${detail}`;
  }
}

function renderRecoveryBlock() {
  const rec = S.data.recovery;
  const steps = clear($('#verify-steps'));
  if (!rec) {
    steps.appendChild(el('span', 'vstep', 'chờ /api/recovery'));
    return;
  }
  const target = rec.target_healthy_observations || 5;
  const done = rec.consecutive_healthy_observations || 0;
  for (let i = 1; i <= target; i += 1) {
    const chip = el('span', 'vstep', `#${i}`);
    chip.setAttribute('data-on', i <= done ? 'true' : 'false');
    steps.appendChild(chip);
    if (i < target) steps.appendChild(el('span', 'varrow mono', '→'));
  }
  const status = el('span', 'verify-status mono', rec.is_verified ? `${done}/${target} ĐẠT TIÊU CHÍ · ĐÃ MỞ KHOÁ CHỐT` : `${done}/${target} · ${rec.is_recovering ? 'luồng sau bảo trì, đang đếm kỳ LOADED' : 'chưa vào nhánh nghiệm thu'}`);
  status.setAttribute('data-tone', rec.is_verified ? 'ok' : 'warn');
  status.style.color = rec.is_verified ? 'var(--ok)' : 'var(--warn)';
  steps.appendChild(status);
  bind('recovery-count', `${done}/${target} kỳ LOADED khỏe liên tiếp`);

  const c = rec.criteria || {};
  const latest = rec.latest_telemetry || {};
  bind('rec-dv', `${num(latest.dv_pressure_bar, 4)} bar`);
  bind('rec-dv-max', `ngưỡng < ${num(c.dv_pressure_max, 3)} bar · bắt buộc ${c.required_regime}`);
  bind('rec-oil', `${num(latest.oil_temp_c, 2)} °C`);
  bind('rec-oil-max', `max < ${num(c.oil_temp_max, 1)} °C`);
  const dvOk = typeof latest.dv_pressure_bar === 'number' && c.dv_pressure_max !== undefined && latest.dv_pressure_bar < c.dv_pressure_max;
  const oilOk = typeof latest.oil_temp_c === 'number' && c.oil_temp_max !== undefined && latest.oil_temp_c < c.oil_temp_max;
  setBadgeIn('[data-bind="rec-dv-state"]', dvOk ? 'PASS' : 'FAIL', dvOk ? 'ok' : 'crit');
  setBadgeIn('[data-bind="rec-oil-state"]', oilOk ? 'PASS' : 'FAIL', oilOk ? 'ok' : 'crit');

  renderRecoveryLog(rec, target);
}

function setBadgeIn(selector, label, toneValue) {
  $$(`${selector}`).forEach((node) => {
    clear(node);
    node.appendChild(badge(label, toneValue));
  });
}

function renderRecoveryLog(rec, target) {
  const tbody = $('#recovery-log tbody');
  if (!tbody) return;
  clear(tbody);
  const loaded = chronologicalPoints().filter((p) => regimeLabel(p.regime) === 'LOADED').slice(-target);
  const criteria = (rec && rec.criteria) || {};
  if (!loaded.length) {
    const tr = el('tr'); const td = el('td', 'muted', 'Không có kỳ LOADED trong cửa sổ hiện tại — chọn khoảng thời gian dài hơn.');
    td.colSpan = 6; tr.appendChild(td); tbody.appendChild(tr);
    return;
  }
  loaded.forEach((p, i) => {
    const okDv = criteria.dv_pressure_max === undefined ? null : p.dv_pressure_bar < criteria.dv_pressure_max;
    const okOil = criteria.oil_temp_max === undefined ? null : p.oil_temp_c < criteria.oil_temp_max;
    const pass = okDv && okOil;
    const tr = el('tr', pass ? 'row-ok' : 'row-crit');
    tr.appendChild(el('td', 'mono', `#${i + 1}`));
    tr.appendChild(el('td', 'mono', utcOf(p.timestamp)));
    tr.appendChild(el('td', 'mono', regimeLabel(p.regime)));
    tr.appendChild(el('td', 'mono', num(p.dv_pressure_bar, 4)));
    tr.appendChild(el('td', 'mono', num(p.oil_temp_c, 2)));
    const st = el('td');
    st.appendChild(badge(pass ? 'PASS' : 'FAIL', pass ? 'ok' : 'crit'));
    st.appendChild(el('span', 'cell-sub mono', `DV < ${num(criteria.dv_pressure_max, 3)} · Oil < ${num(criteria.oil_temp_max, 1)}`));
    tr.appendChild(st);
    tbody.appendChild(tr);
  });
}

let lastAutoPhase = null;
function applyWorkbenchFocus() {
  const state = (S.data.incident && S.data.incident.lifecycle_state) || 'NONE';
  if (state !== lastAutoPhase) {
    lastAutoPhase = state;
    S.wbFocus = PHASE_FOCUS[state] || 'changed';
    $$('#wb-focus-tabs .focus-btn').forEach((x) => x.classList.toggle('is-active', x.dataset.focus === S.wbFocus));
  }
  renderPhaseGates();
}

/* ══════════════════════════════ SCREEN 07: timeline ══════════════════════════════ */
function renderTimeline() {
  const host = $('#timeline-list');
  if (!host) return;
  const events = S.data.events || [];

  const typeFilter = $('#filter-type');
  if (typeFilter) {
    const wanted = Array.from(new Set(events.map((e) => e.event_type).filter(Boolean)));
    const current = typeFilter.value || 'ALL';
    if (typeFilter.dataset.signature !== wanted.join('|')) {
      clear(typeFilter);
      const all = el('option', null, 'LOẠI: MỌI LOẠI'); all.value = 'ALL'; typeFilter.appendChild(all);
      wanted.forEach((t) => { const o = el('option', null, t); o.value = t; typeFilter.appendChild(o); });
      typeFilter.dataset.signature = wanted.join('|');
      if (wanted.includes(current)) typeFilter.value = current;
    }
  }

  clear(host);
  const actorFilter = ($('#filter-actor') && $('#filter-actor').value) || 'ALL';
  const type = typeFilter ? (typeFilter.value || 'ALL') : 'ALL';
  const q = $('#event-search') ? $('#event-search').value.trim().toLowerCase() : '';

  const visible = events.filter((e) => {
    if (actorFilter === 'system' && !String(e.actor).startsWith('system')) return false;
    if (actorFilter === 'operator' && !String(e.actor).startsWith('operator')) return false;
    if (type !== 'ALL' && e.event_type !== type) return false;
    if (q && !`${e.title} ${e.detail} ${e.source} ${e.actor} ${e.phase}`.toLowerCase().includes(q)) return false;
    return true;
  });

  const empty = $('#timeline-empty');
  if (empty) empty.hidden = visible.length > 0;

  visible.forEach((e) => {
    const row = el('div', 'tl-row');
    const isOperator = String(e.actor).startsWith('operator');
    const critTypes = ['DETECTION', 'CASE_CLOSED', 'FALSE_POSITIVE', 'LPS_BENCHMARK', 'BENCHMARK_REFERENCE_REACHED'];
    const okTypes = ['RECOVERY', 'ACTION', 'WORK_ORDER'];
    let t = 'idle';
    if (isOperator) t = 'info';
    if (critTypes.includes(String(e.event_type))) t = e.event_type === 'CASE_CLOSED' ? 'ok' : 'crit';
    if (okTypes.includes(String(e.event_type))) t = 'ok';
    if (String(e.event_type) === 'CORROBORATION') t = 'warn';
    if (String(e.event_type) === 'OBSERVATION') t = 'warn';
    row.setAttribute('data-tone', t);
    row.appendChild(el('span', 'tl-dot'));
    row.appendChild(el('span', 'tl-time', `${utcOf(e.event_time)}`));
    const typeCell = el('span', 'tl-type');
    typeCell.appendChild(badge(e.event_type, t));
    row.appendChild(typeCell);
    row.appendChild(el('span', 'tl-phase', `Giai đoạn: ${e.phase || DASH}`));
    const actor = el('span', 'tl-actor');
    actor.appendChild(el('b', null, e.actor || DASH));
    row.appendChild(actor);
    const body = el('span');
    body.appendChild(el('div', 'tl-body-title', mtxt(e.title) || DASH));
    body.appendChild(el('div', 'tl-body-detail', mtxt(e.detail)));
    const provKeys = Object.keys(e.provenance || {});
    body.appendChild(el('div', 'tl-src', `nguồn: ${e.source || DASH} · ${e.event_id || ''}${provKeys.length ? ` · provenance: ${provKeys.slice(0, 4).map((k) => `${k}=${String(e.provenance[k]).slice(0, 40)}`).join(', ')}` : ''}`));
    row.appendChild(body);
    host.appendChild(row);
  });
}

/* ══════════════════════════════ Replay Studio drawer ══════════════════════════════ */
function renderReplayBar() {
  const sim = S.data.simStatus;
  const meta = $('#replay-tab-meta');
  if (meta && sim) meta.textContent = `${num(sim.speed_multiplier, 0)}x · ${sim.is_paused ? 'ĐÃ DỪNG' : 'ĐANG PHÁT'}`;
  bind('replay-state', sim
    ? `${sim.is_paused ? 'ĐÃ DỪNG' : 'ĐANG PHÁT'} · ${num(sim.speed_multiplier, 0)}x · ${sim.total_points_emitted} mẫu đã phát · cursor ${sim.current_event_time ? utcOf(sim.current_event_time) : 'chưa bắt đầu'} · ${sim.mode}`
    : DASH);

  const play = $('#btn-play');
  const pause = $('#btn-pause');
  if (play) play.disabled = Boolean(sim && !sim.is_paused);
  if (pause) pause.disabled = Boolean(sim && sim.is_paused);
  $$('#speed-seg .seg-btn').forEach((b) => {
    b.classList.toggle('is-active', Boolean(sim && Number(b.dataset.speed) === Number(sim.speed_multiplier)));
  });

  const sel = $('#scenario-select');
  const catalog = S.data.scenarios;
  if (sel && catalog && sel.dataset.signature !== `${catalog.active_scenario_id}|${(catalog.scenarios || []).length}`) {
    clear(sel);
    (catalog.scenarios || []).forEach((sc) => {
      const o = el('option', null, sc.name);
      /* Scenario clocks stay out of the DOM: stream_end can name a future LPS breach. */
      o.dataset.range = `${sc.stream_start} -> ${sc.stream_end}`;
      o.value = sc.scenario_id;
      if (sc.scenario_id === catalog.active_scenario_id) o.selected = true;
      sel.appendChild(o);
    });
    sel.dataset.signature = `${catalog.active_scenario_id}|${(catalog.scenarios || []).length}`;
  }

  const grid = $('#chapter-bar');
  if (grid && catalog) {
    const active = (catalog.scenarios || []).find((s) => s.scenario_id === catalog.active_scenario_id) || (catalog.scenarios || [])[0];
    const milestones = (active && active.milestones) || {};
    const sig = Object.keys(milestones).join('|');
    if (grid.dataset.signature !== sig) {
      clear(grid);
      const keys = Object.keys(milestones);
      if (!keys.length) grid.appendChild(el('span', 'mono muted', 'kịch bản này không có mốc chẩn đoán'));
      keys.forEach((key) => {
        const b = el('button', 'chapter-btn', chapterLabel(key));
        /* The milestone clock stays out of the DOM: it can name a future LPS breach. */
        b.dataset.milestone = key;
        b.addEventListener('click', () => jumpTo(key));
        grid.appendChild(b);
      });
      grid.dataset.signature = sig;
    }
  }
}

/* Chapter labels key off the milestone stem from /api/scenarios, never off its clock. */
const CHAPTER_VI = [
  [/early_excursion/, 'Nhiễu thoáng qua'],
  [/ml_corroborated/, 'AI xác nhận'],
  [/lps_reactive/, 'Rơ-le cũ kêu'],
  [/post_maintenance/, 'Nghiệm thu'],
  [/onset/, 'Phát hiện']
];

function chapterLabel(key) {
  const hit = CHAPTER_VI.find(([rx]) => rx.test(String(key)));
  return hit ? hit[1] : String(key);
}

async function postDemo(path, body) {
  try {
    const res = await request(path, { method: 'POST', body: body || {} });
    S.data.simStatus = await request('/demo/status');
    await refreshAllData();
    return res;
  } catch (err) {
    toast('error', `Lệnh replay lỗi · ${path}`, err.message);
    return null;
  }
}

async function jumpTo(milestone) {
  const res = await postDemo('/demo/jump', { milestone });
  if (res) toast('info', 'Đã dời cursor', `mốc ${res.milestone} → ${res.lifecycle_state}`, 4000);
}

function toggleReplay(force) {
  const panel = $('#dev-panel');
  if (!panel) return;
  const wantOpen = force === undefined ? panel.hidden : force;
  panel.hidden = !wantOpen;
  const btn = $('#btn-dev');
  if (btn) btn.setAttribute('aria-expanded', String(wantOpen));
}

/* A paused stream with zero samples is not a fault: it is a demo that has not started. */
function renderBootState() {
  const sim = S.data.simStatus;
  const booting = Boolean(sim) && Number(sim.total_points_emitted) === 0;
  const box = $('#boot-state');
  if (box) box.hidden = !booting;
  document.body.classList.toggle('is-booting', booting);
}

/* ══════════════════════════════ Validation Reference drawer ══════════════════════════════ */
function renderValidationDrawer() {
  const ref = S.data.validation;
  const host = $('#vr-body');
  if (!ref || !host || host.dataset.signature) return;
  clear(host);
  const items = [
    ['Kịch bản', `${ref.scenario_name} (${ref.scenario_id})`],
    ['Nguồn dữ liệu', ref.dataset_source],
    ['Giai đoạn lịch sử', ref.historical_period],
    ['Hỏng hóc ghi nhận', ref.reported_failure_mode],
    ['Bắt đầu hỏng', ref.reported_failure_start],
    ['LPS quy ước', ref.conventional_lps_breach],
    ['Detector online xác nhận', ref.online_detector_confirmation],
    ['Cửa sổ can thiệp', `${ref.confirmed_intervention_window_formatted} (${ref.confirmed_intervention_window_minutes} phút)`],
    ['Báo cáo bảo trì', ref.maintenance_summary]
  ];
  items.forEach(([k, v]) => {
    const box = el('div', 'vr-item');
    box.appendChild(el('span', null, k));
    box.appendChild(el('b', k === 'Detector online xác nhận' ? 'computed' : null, v));
    host.appendChild(box);
  });
  if (ref.computed_by_compressorguard) {
    const box = el('div', 'vr-item');
    box.appendChild(el('span', null, 'CompressorGuard tính (Layer B)'));
    box.appendChild(el('b', 'computed', JSON.stringify(ref.computed_by_compressorguard)));
    host.appendChild(box);
  }
  const note = el('div', 'vr-item');
  note.appendChild(el('span', null, 'Đối chứng trực tiếp'));
  note.appendChild(el('b', null, `Thời gian báo trước của engine: ${(S.data.incident && S.data.incident.lead_time && S.data.incident.lead_time.lead_time_formatted) || 'chưa xác nhận ở phiên này'}`));
  host.appendChild(note);
}

function toggleVr(open) {
  const drawer = $('#vr-drawer');
  const backdrop = $('#vr-backdrop');
  const willOpen = open === undefined ? !drawer.classList.contains('is-open') : open;
  drawer.classList.toggle('is-open', willOpen);
  backdrop.hidden = !willOpen;
  if (willOpen) {
    S.data.validation = null;
    $('#vr-body').dataset.signature = '';
    request(CFG.api.validation).then((payload) => {
      S.data.validation = payload;
      renderValidationDrawer();
      toast('info', 'Đã mở đối chứng', 'Sự thật lịch sử Layer C — không cấp cho detector online.');
    }).catch((err) => toast('error', 'Đọc đối chứng thất bại', err.message));
  }
}

/* ══════════════════════════════ operator rail ══════════════════════════════ */
function renderOperatorRail() {
  const inc = S.data.incident;
  const guard = S.data.guard;
  const rec = S.data.recovery;
  const ops = S.data.operations;
  const an = S.data.analytics;
  const active = hasActiveCase();
  const state = (inc && inc.lifecycle_state) || 'NONE';
  const woAllowed = active && ['DETECTED', 'INVESTIGATING', 'MITIGATING'].includes(state);

  // Build the operator form choices from live API data first, so a fresh render never
  // disables a control merely because its options have not been populated yet.
  fillPlaybookOptions(an);
  fillDepotOptions(ops, inc);
  fillRootCauseOptions(an);

  bind('ack-state', active
    ? (inc.acknowledged ? `${vlabel('ACKNOWLEDGED')} bởi ${inc.acknowledged_by || 'operator'} · ưu tiên ${inc.priority}` : `${vlabel('UNACKNOWLEDGED')} · giai đoạn ${vlabel(state)}`)
    : 'chưa có vụ việc mở', inc && inc.acknowledged ? 'ok' : (active ? 'warn' : null));

  const ackBtn = $('#btn-acknowledge');
  if (ackBtn) ackBtn.disabled = !active || Boolean(inc && inc.acknowledged);
  const fpBtn = $('#btn-false-positive');
  if (fpBtn) fpBtn.disabled = !active;
  const noteBtn = $('#btn-add-note');
  if (noteBtn) noteBtn.disabled = !active || !$('#note-body').value.trim();
  const woBtn = $('#btn-work-order');
  if (woBtn) {
    woBtn.disabled = !woAllowed || !$('#wo-playbook').value || !$('#wo-instructions').value.trim();
    woBtn.textContent = inc && inc.work_order ? 'Cập nhật lệnh công tác' : 'Phát lệnh công tác';
  }
  const safeBtn = $('#btn-safe-mode');
  if (safeBtn) safeBtn.disabled = !(guard && guard.is_permitted) || !active || state === 'MITIGATING' || state === 'VERIFYING_RECOVERY' || state === 'RESOLVED';
  const closeBtn = $('#btn-close-case');
  if (closeBtn) closeBtn.disabled = !active || !closeable();

  bind('close-hint', !active
    ? 'Chưa có vụ việc để chốt.'
    : (closeable()
      ? `Nghiệm thu đạt ${rec.consecutive_healthy_observations}/${rec.target_healthy_observations} · đã mở khoá trả tàu.`
      : `Chốt khi đủ ${rec ? rec.consecutive_healthy_observations : 0}/${rec ? rec.target_healthy_observations : 5} kỳ LOADED khỏe.`));
  bind('safe-hint', guard && guard.is_permitted
    ? 'Mọi chốt ActionGuard đạt · được phép điều độ.'
    : `ActionGuard chặn: ${guard ? guard.denial_reason || `${guard.passed_count}/${guard.total_checks} chốt đạt` : 'chưa đọc được chốt'}`);

  const branch = guardCheck('REPLAY_BRANCH_AVAILABLE');
  bind('branch-info', `Chốt nhánh luồng: ${branch ? `${vlabel(branch.passed ? 'AVAILABLE' : 'NOT AVAILABLE')} — ${branch.current_value}` : 'chưa báo'}${S.lastAction && S.lastAction.stream_branch ? ` · phát trước → ${S.lastAction.stream_branch.source} @ ${S.lastAction.stream_branch.offset_timestamp}` : ''}`,
    branch && branch.passed ? 'ok' : null);

  bind('wo-state', inc && inc.work_order
    ? `${inc.work_order.work_order_id} · ${inc.work_order.status} · ${inc.work_order.playbook_id} → ${inc.work_order.target_depot} (${inc.work_order.maintenance_window})`
    : 'chưa thảo lệnh công tác');

}

function fillPlaybookOptions(an) {
  const sel = $('#wo-playbook');
  if (!sel || !an) return;
  const matches = an.fingerprint_matches || [];
  const sig = matches.map((m) => m.recommended_playbook).join('|');
  if (sel.dataset.signature === sig) return;
  clear(sel);
  if (!matches.length) {
    const o = el('option', null, 'mặc định engine · chưa khớp vân hỏng');
    o.value = '';
    sel.appendChild(o);
  }
  matches.forEach((m) => {
    const o = el('option', null, `${m.recommended_playbook} · ${m.title} · giống ${num(m.similarity_score * 100, 1)}%`);
    o.value = m.recommended_playbook;
    o.dataset.action = m.recommended_action || '';
    sel.appendChild(o);
  });
  sel.dataset.signature = sig;
  const top = an.top_diagnosis;
  const instructions = $('#wo-instructions');
  if (top && instructions && !instructions.dataset.touched) {
    instructions.value = top.recommended_action || '';
    const match = Array.from(sel.options).find((o) => o.value === top.recommended_playbook);
    if (match) sel.value = match.value;
  }
}

function fillDepotOptions(ops, inc) {
  const sel = $('#wo-depot');
  if (!sel || !ops) return;
  const existing = inc && inc.work_order ? inc.work_order.target_depot : '';
  const primary = ops.fleet.depot_location;
  const sig = [primary, existing].filter(Boolean).join('|');
  if (sel.dataset.signature === sig) return;
  clear(sel);
  const opts = [
    { value: primary, label: `${primary} · depot hạm đội (${ops.fleet.name})` }
  ];
  if (existing && existing !== primary) opts.push({ value: existing, label: `${existing} · depot đã phát trước` });
  opts.push({ value: '', label: 'bỏ trống · engine tự chọn' });
  opts.forEach((o, i) => {
    const option = el('option', null, o.label);
    option.value = o.value;
    if (i === 0) option.selected = true;
    sel.appendChild(option);
  });
  sel.dataset.signature = sig;
}

function fillRootCauseOptions(an) {
  const sel = $('#close-root-cause');
  if (!sel || !an) return;
  const matches = an.fingerprint_matches || [];
  const sig = matches.map((m) => m.root_cause_component).join('|');
  if (sel.dataset.signature === sig) return;
  clear(sel);
  if (!matches.length) {
    const o = el('option', null, 'chưa phân loại nguyên nhân gốc');
    o.value = '';
    sel.appendChild(o);
  }
  matches.forEach((m) => {
    const o = el('option', null, `${m.root_cause_component} · giống ${num(m.similarity_score * 100, 1)}%`);
    o.value = m.root_cause_component;
    sel.appendChild(o);
  });
  sel.dataset.signature = sig;
}

async function runOperatorAction(kind) {
  const endpoints = {
    acknowledge: { path: '/api/case/acknowledge', build: () => ({ operator_id: S.operator, priority: $('#ack-priority').value, note: $('#ack-note').value.trim() }), ok: 'Đã xác nhận vụ việc' },
    note: { path: '/api/case/notes', build: () => ({ operator_id: S.operator, note: $('#note-body').value.trim() }), ok: 'Đã ghi chú vào sổ theo dõi' },
    workOrder: {
      path: '/api/case/work-order',
      build: () => {
        const body = {
          operator_id: S.operator,
          maintenance_window: $('#wo-window').value,
          instructions: $('#wo-instructions').value.trim()
        };
        const playbook = $('#wo-playbook').value;
        const depot = $('#wo-depot').value;
        if (playbook) body.playbook_id = playbook;
        if (depot) body.target_depot = depot;
        return body;
      },
      ok: 'Đã phát lệnh công tác depot'
    },
    safeMode: { path: '/api/action/safe-mode', build: () => ({ operator_id: S.operator }), ok: 'Đã phát can thiệp an toàn' },
    falsePositive: { path: '/api/case/false-positive', build: () => ({ operator_id: S.operator, reason: $('#fp-reason').value.trim() || 'Operator bỏ qua từ console vận hành.' }), ok: 'Đã đánh dấu dương tính giả' },
    close: {
      path: '/api/case/close',
      build: () => {
        const rc = $('#close-root-cause').value;
        const body = $('#close-notes').value.trim();
        return { operator_id: S.operator, notes: `${rc ? `Nguyên nhân gốc: ${rc}. ` : ''}${body || 'Đã kiểm tiêu chí nghiệm thu.'}` };
      },
      ok: 'Đã chốt vụ việc · trả tài sản'
    }
  };
  const spec = endpoints[kind];
  if (!spec) return;
  try {
    const res = await request(spec.path, { method: 'POST', body: spec.build() });
    S.lastAction = res;
    if (kind === 'note') {
      const ta = $('#note-body'); if (ta) ta.value = '';
    }
    if (kind === 'acknowledge') { const ta = $('#ack-note'); if (ta) ta.value = ''; }
    if (kind === 'close' || kind === 'falsePositive') { const ta = $('#close-notes'); if (ta) ta.value = ''; }
    const detail = summariseResponse(kind, res);
    toast('ok', spec.ok, detail);
    await refreshAllData();
  } catch (err) {
    const status = err.status || '';
    toast('error', `Hành động bị từ chối ${status}`.trim(), err.message, 9000);
    await refreshAllData();
  }
}

function summariseResponse(kind, res) {
  if (!res) return '';
  if (kind === 'acknowledge') return `${res.case_id} · ${vlabel(res.priority)} · ${res.operator_id} · ${res.event_id}`;
  if (kind === 'note') return `${res.event_time} · ${res.event_id}`;
  if (kind === 'workOrder') return `${res.work_order_id} · ${res.playbook_id} → ${res.target_depot} (${res.maintenance_window})`;
  if (kind === 'safeMode') return `${res.status} · ${vlabel(res.target_state)} · ${res.stream_branch.source} @ ${res.stream_branch.offset_timestamp}`;
  if (kind === 'falsePositive') return `${vlabel(res.lifecycle_state)} · ${vlabel(res.asset_health)} · ${res.event_id}`;
  if (kind === 'close') return `${res.status} · ${vlabel(res.lifecycle_state)} · ${vlabel(res.asset_health)}`;
  return JSON.stringify(res).slice(0, 180);
}

/* ══════════════════════════════ view switching & wiring ══════════════════════════════ */
function setView(view) {
  S.view = view;
  $$('.view').forEach((v) => v.classList.toggle('is-active', v.id === `view-${view}`));
  $$('.nav-tab').forEach((t) => t.classList.toggle('is-active', t.dataset.view === view));
  document.body.setAttribute('data-view', view);
  if (view === 'fleet' || view === 'workbench') renderCharts();
}

function wireEvents() {
  $$('.nav-tab').forEach((t) => t.addEventListener('click', () => setView(t.dataset.view)));

  $$('#timeframe-seg .seg-btn').forEach((b) => {
    b.addEventListener('click', () => {
      S.timeframe = b.dataset.timeframe;
      $$('#timeframe-seg .seg-btn').forEach((x) => x.classList.toggle('is-active', x === b));
      refreshAllData();
    });
  });

  $('#operator-select').addEventListener('change', (e) => {
    S.operator = e.target.value;
    toast('info', 'Đổi ca vận hành', `Từ nay sự kiện ghi cho ${S.operator}.`);
  });

  $('#toggle-regime-shading').addEventListener('change', (e) => { S.shading = e.target.checked; renderCharts(); });
  $('#toggle-thresholds').addEventListener('change', (e) => { S.thresholds = e.target.checked; renderCharts(); });
  $('#toggle-engineering').addEventListener('change', (e) => { S.engineering = e.target.checked; renderCharts(); });

  ['asset-search', 'filter-health', 'filter-regime'].forEach((id) => {
    const node = document.getElementById(id);
    node.addEventListener('input', renderAssetGrid);
    node.addEventListener('change', renderAssetGrid);
  });
  ['case-search', 'filter-ack'].forEach((id) => document.getElementById(id).addEventListener('input', renderQueueCards));
  ['filter-actor', 'filter-type', 'event-search'].forEach((id) => document.getElementById(id).addEventListener('input', renderTimeline));

  $('#note-body').addEventListener('input', () => { $('#btn-add-note').disabled = !hasActiveCase() || !$('#note-body').value.trim(); });
  $('#wo-instructions').addEventListener('input', (e) => { e.target.dataset.touched = 'true'; renderOperatorRail(); });
  $('#wo-playbook').addEventListener('change', (e) => {
    const opt = e.target.selectedOptions[0];
    const box = $('#wo-instructions');
    if (opt && opt.dataset.action) { box.value = opt.dataset.action; box.dataset.touched = 'true'; }
    renderOperatorRail();
  });

  $('#btn-acknowledge').addEventListener('click', () => runOperatorAction('acknowledge'));
  $('#btn-add-note').addEventListener('click', () => runOperatorAction('note'));
  $('#btn-work-order').addEventListener('click', () => runOperatorAction('workOrder'));
  $('#btn-safe-mode').addEventListener('click', () => runOperatorAction('safeMode'));
  $('#btn-false-positive').addEventListener('click', () => runOperatorAction('falsePositive'));
  $('#btn-close-case').addEventListener('click', () => runOperatorAction('close'));

  $('#btn-toggle-vr').addEventListener('click', () => toggleVr());
  $('#btn-toggle-replay').addEventListener('click', () => toggleReplay());
  $('#vr-close').addEventListener('click', () => toggleVr(false));
  $('#vr-backdrop').addEventListener('click', () => toggleVr(false));
  $$('[data-open-vr]').forEach((b) => b.addEventListener('click', () => toggleVr(true)));

  $('#btn-play').addEventListener('click', async () => { await postDemo('/demo/play'); toast('info', 'Đã phát lại luồng', 'Worker backend đẩy mẫu; console chỉ đọc.'); });
  $('#btn-pause').addEventListener('click', async () => { await postDemo('/demo/pause'); toast('info', 'Đã dừng luồng', 'MongoDB ngừng nhận mẫu cho tới khi phát lại.'); });
  $$('#speed-seg .seg-btn').forEach((b) => {
    b.addEventListener('click', async () => {
      const res = await postDemo('/demo/speed', { speed_multiplier: Number(b.dataset.speed) });
      if (res) toast('info', 'Đã đổi nhịp phát', `${num(res.speed_multiplier, 0)}x · ${res.is_paused ? 'đã dừng' : 'đang phát'}`);
    });
  });
  $('#btn-apply-scenario').addEventListener('click', async () => {
    const id = $('#scenario-select').value;
    if (!id) return;
    try {
      const res = await request('/api/operations/scenario', { method: 'POST', body: { scenario_id: id } });
      toast('info', 'Đã đổi kịch bản', `${res.scenario_name} · cursor về đầu kịch bản`);
      S.data.scenarios = null;
      S.data.window = null;
      await refreshAllData();
    } catch (err) {
      toast('error', 'Đổi kịch bản thất bại', err.message);
    }
  });
  $('#btn-boot-play').addEventListener('click', async () => { await postDemo('/demo/play'); });

  $('#btn-reset-stream').addEventListener('click', async () => {
    if (!window.confirm('Đặt lại toàn bộ phiên phát?')) return;
    const res = await postDemo('/demo/reset', {});
    if (res) toast('warn', 'Đã đặt lại phiên', 'State machine, detector và sổ dựng lại từ đầu CSV.');
  });

  $('#btn-export').addEventListener('click', exportDossier);

  $$('#wb-focus-tabs .focus-btn').forEach((b) => {
    b.addEventListener('click', () => {
      /* The ledger lives in one place: the audit chip opens the Case Timeline screen. */
      if (b.dataset.focus === 'audit') {
        setView('timeline');
        return;
      }
      S.wbFocus = b.dataset.focus;
      $$('#wb-focus-tabs .focus-btn').forEach((x) => x.classList.toggle('is-active', x === b));
      applyWorkbenchFocus();
    });
  });

  document.addEventListener('keydown', (e) => {
    if (e.shiftKey && (e.key === 'S' || e.key === 's')) {
      const tag = (e.target.tagName || '').toLowerCase();
      if (['input', 'textarea', 'select'].includes(tag)) return;
      e.preventDefault();
      toggleReplay();
    }
    if (e.key === 'Escape') { toggleVr(false); }
  });
}

async function exportDossier() {
  const dossier = {
    exported_at_simulation_time: new Date().toISOString(),
    provenance: S.data.simStatus ? S.data.simStatus.provenance : null,
    operations: S.data.operations,
    incident: S.data.incident,
    evidence: S.data.evidence,
    action_guard: S.data.guard,
    recovery: S.data.recovery,
    analytics: S.data.analytics,
    validation_reference: S.data.validation,
    case_event_ledger: S.data.events
  };
  const blob = new Blob([JSON.stringify(dossier, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = el('a');
  a.href = url;
  a.download = `compressorguard-dossier-${activeCaseId() || 'session'}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
  toast('ok', 'Đã xuất hồ sơ', 'JSON hậu kiểm dựng từ state API, kèm sổ theo dõi.');
}

/* ══════════════════════════════ boot ══════════════════════════════ */
function boot() {
  wireEvents();
  toast('info', 'Đã kết nối console', 'Console chỉ đọc API; worker backend phát luồng dữ liệu.');
  refreshAllData();
  setInterval(refreshAllData, CFG.pollMs);
}

document.addEventListener('DOMContentLoaded', boot);
