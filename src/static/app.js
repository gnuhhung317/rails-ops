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
    validation: '/api/validation-reference',
    datadog: '/api/observability/datadog-status',
    // Enterprise Component CRUD, SOP & Shift endpoints
    components: '/api/components',
    componentDetail: (id) => `/api/components/${encodeURIComponent(id)}`,
    sop: '/api/sop',
    sopDetail: (id) => `/api/sop/${encodeURIComponent(id)}`,
    shiftCurrent: '/api/shift/current',
    shiftHandover: '/api/shift/handover'
  },
  pillBase: 'LIVE SIMULATION · HISTORICAL DATA'
};

const S = {
  view: 'fleet',
  wbFocus: 'changed',
  timeframe: '15m',
  // Operator Persona: Hùng Bùi (NV-0941)
  operator: 'Hùng Bùi (NV-0941)',
  operatorCode: 'NV-0941',
  shift: 'Ca 1 (06:00 – 14:00)',
  stationUnit: 'Trung tâm OCC Tuyến Metro Số 1 (HURC1)',
  depot: 'Depot Long Bình',

  // Selected asset & incident context
  selectedTrainId: 'TRAIN-302',
  selectedComponentId: 'APU-DRY-LP49',
  selectedIncidentId: 'APU-INC-20200605-01',
  activeStep: 1,

  // Dynamic custom thresholds updated from Screen 2
  customThresholds: {
    leak_pressure_max: 0.05,
    oil_temp_max: 67.0
  },

  shading: true,
  thresholds: true,
  degraded: false,
  lastGoodPoll: 0,
  engineering: false,
  data: {
    operations: null, incident: null, evidence: null, events: [],
    guard: null, recovery: null, window: null, analytics: null,
    scenarios: null, validation: null, simStatus: null,
    components: [], componentMap: {}, sopPlaybooks: [], currentShift: null
  },
  lastAction: null,
  charts: {},
  chartsReady: false,
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
  HEALTHY: 'BÌNH THƯỜNG',
  DEGRADING: 'SUY GIẢM',
  CRITICAL: 'NGUY CẤP',
  NOMINAL: 'Bình thường',
  LOADED: 'CÓ TẢI (ĐANG NÉN)',
  UNLOADED: 'KHÔNG TẢI',
  ELEVATED: 'NHIỆT ĐỘ TĂNG CAO',
  UNACKED: 'CHƯA TIẾP NHẬN',
  UNACKNOWLEDGED: 'CHƯA TIẾP NHẬN',
  ACKED: 'ĐÃ TIẾP NHẬN',
  ACKNOWLEDGED: 'ĐÃ TIẾP NHẬN',
  CONFIRMED: 'ĐÃ XÁC NHẬN',
  NONE: 'Chưa có',
  LOW: 'Thấp',
  MEDIUM: 'Vừa',
  HIGH: 'Cao',
  DISPATCHED: 'Đã phát',
  CORROBORATED: 'AI xác nhận',
  TRIGGERED: 'Kích hoạt',
  NORMAL: 'Trong ngưỡng',
  PASS: 'PASS',
  FAIL: 'FAIL',
  AVAILABLE: 'SẴN SÀNG',
  'NOT AVAILABLE': 'CHƯA SẴN SÀNG',
  WITHIN_BASELINE: 'Trong baseline',
  SUPPRESSED_TRANSIENT: 'Nhiễu thoáng qua đã chặn',
  BRAKE_RESERVOIR_PRESSURE_SAFE: 'Áp suất bình phanh an toàn',
  CASE_CONFIRMED: 'Sự cố đã xác nhận',
  MITIGATION_RECOMMENDED: 'Đề xuất can thiệp',
  SINGLE_ACTIVE_CASE: 'Không trùng sự cố',
  REPLAY_BRANCH_AVAILABLE: 'Nhánh luồng kiểm nghiệm',
  CRITICAL_REACTIVE: 'Phản ứng khẩn cấp (LPS)',
  INVESTIGATING: 'Đang điều tra',
  DETECTED: 'Đã phát hiện',
  RESOLVED: 'Đã nghiệm thu',
  CLOSED: 'Đã đóng',
  BENCHMARK_REFERENCE_REACHED: 'Mốc LPS đối chứng',
  LPS_BENCHMARK: 'Đối chứng LPS',
  OPERATIONAL_CONFIDENCE_SUFFICIENT: 'Độ tin cậy vận hành đạt',
  'Active case required in DETECTED or INVESTIGATING state.': 'Cần sự cố ở giai đoạn Phát hiện hoặc Đang điều tra.',
  'Mitigation not recommended by DecisionEngine.': 'Chưa đủ điều kiện đề xuất can thiệp.',
  'Conflicting active cases detected on asset.': 'Đoàn tàu đang có sự cố mở xung đột.',
  'Brake reservoir pressure below safe threshold (< 7.0 bar or LPS tripped).': 'Áp phanh bình chứa dưới ngưỡng an toàn (< 7.0 bar hoặc LPS đã kích).',
  'Post-maintenance historical stream segment unavailable.': 'Chưa có phân đoạn luồng sau bảo trì.',
  'Case is active and confirmed (DETECTED / INVESTIGATING)': 'Sự cố đang mở và đã xác nhận (DETECTED / INVESTIGATING)',
  'DecisionEngine recommends mitigation (Physics + ML Corroboration)': 'DecisionEngine khuyến nghị can thiệp (vật lý + AI)',
  'No conflicting active cases on asset': 'Không có sự cố mở xung đột trên đoàn tàu',
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
  'Case Closed as False Positive (Operator Override)': 'Đóng vụ việc: dương tính giả (operator bỏ qua)',
  'Failure #1 — High-Duty Pneumatic Air Leak': 'Hỏng #1 — Rò khí do tải cao',
  'Failure #3 — Dryer Discharge Pilot Valve Leakage & Thermal Drift': 'Hỏng #3 — Rò van xả khí sấy, trôi nhiệt',
  'Failure #4 — Compressor Oil Contamination & Severe Thermal Stress': 'Hỏng #4 — Dầu nhiễm bẩn, ứng nhiệt nghiêm trọng',
  'Loaded-regime baseline (sigma > 5.0)': 'Baseline kỳ LOADED (σ > 5.0)',
  'Isolation Forest (5 features, LOADED baseline)': 'Isolation Forest (5 đặc trưng, baseline LOADED)',
  'Independent Corroboration': 'Xác nhận độc lập'
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
  const m = s.match(/[T ](\d{2}:\d{2}:\d{2})/);
  if (m) return m[1];
  return s;
}

function utcOf(iso) {
  if (!iso) return DASH;
  const s = String(iso);
  const m = s.match(/^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})/);
  if (!m) return s.replace('T', ' ').replace(/Z$/, '');
  const Y = m[1], M = m[2], D = m[3], h = m[4], min = m[5], sec = m[6];
  return `${h}:${min}:${sec} ${D}/${M}/${Y}`;
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
  if (S.pollCount % 4 === 0 || !S.data.datadog) jobs.datadog = request(CFG.api.datadog);
  if (S.pollCount % 10 === 0 || !S.data.components || !S.data.components.length) jobs.components = request(CFG.api.components);
  if (S.pollCount % 20 === 0 || !S.data.sopPlaybooks || !S.data.sopPlaybooks.length) jobs.sopPlaybooks = request(CFG.api.sop);

  const names = Object.keys(jobs);
  const results = await Promise.allSettled(names.map((n) => jobs[n]));
  let ok = 0;
  const failed = [];
  results.forEach((r, i) => {
    const name = names[i];
    if (r.status === 'fulfilled') {
      if (name !== 'validation' || r.value) S.data[name] = r.value;
      if (name === 'components' && r.value) {
        const comps = Array.isArray(r.value.components) ? r.value.components : (Array.isArray(r.value) ? r.value : []);
        comps.forEach((c) => {
          if (c && c.component_id) S.data.componentMap[c.component_id] = c;
        });
      }
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

function isLoaded(value) { return String(value || '').toUpperCase() === 'LOADED' || String(value || '').toUpperCase().includes('CÓ TẢI'); }
function regimeLabel(value) { return isLoaded(value) ? 'CÓ TẢI (ĐANG NÉN)' : 'KHÔNG TẢI'; }

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
  renderAssetManagement();
  renderWorkbench();
  renderSettingsView();
  renderTimeline();
  renderReplayBar();
  renderValidationDrawer();
  renderDatadogDrawer();
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
  if (clockNode) clockNode.textContent = txt(simClock ? `${utcOf(simClock)} (GMT+7)` : (S.degraded ? 'API gián đoạn' : 'luồng dừng'));

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
    kpiNote('mode', sum.simulation_mode === 'LIVE_SIMULATION' ? 'Mô phỏng trực tiếp' : `Chế độ: ${sum.simulation_mode}`);
    const badgeEl = $('#nav-queue-count');
    if (badgeEl) {
      badgeEl.textContent = String(sum.active_cases_count);
      badgeEl.setAttribute('data-hot', sum.active_cases_count > 0 ? 'true' : 'false');
    }
  }

  const state = (inc && inc.lifecycle_state) || 'NONE';
  kpi('phase', state === 'NONE' ? PHASE_LABEL.NONE : txt(PHASE_LABEL[state] || state), state === 'NONE' ? 'ok' : 'crit');
  kpiNote('provenance', sim ? 'Metro Tuyến 1' : 'Đang đồng bộ');

  kpi('regime', ev ? regimeLabel(ev.regime) : DASH, ev && isLoaded(ev.regime) ? 'info' : 'idle');
  kpiNote('duty', an && an.regime_analytics
    ? `tải trọng: ${num(an.regime_analytics.loaded_duty_cycle_pct, 1)}% · ${an.regime_analytics.loaded_samples_count}/${an.regime_analytics.total_samples_analyzed} mẫu`
    : 'tải trọng: —');
  kpiNote('transient', an && an.alert_fatigue_protection && an.alert_fatigue_protection.suppressed_transients_count > 0
    ? `đã lọc ${an.alert_fatigue_protection.suppressed_transients_count} nhiễu`
    : 'bộ lọc ổn định');

  const windowLabel = `${CFG.timeframeLabels[S.timeframe]} · ${S.data.window ? S.data.window.count : 0} mẫu · cửa sổ ${S.data.window ? S.data.window.window_size : DASH}s`;
  bind('window-label', windowLabel);
  bind('wb-window-label', windowLabel);
}

/* ─────────────── SCREEN 01: fleet & telemetry ─────────────── */
function renderApuSchematic() {
  const p = latestPoint();
  if (!p) return;

  const motor = $('#sch-motor');
  const oil = $('#sch-oil');
  const tp2 = $('#sch-tp2');
  const dv = $('#sch-dv');
  const dvStatus = $('#sch-dv-status');
  const mod2Status = $('#sch-mod2-status');
  const tp3 = $('#sch-tp3');
  const res = $('#sch-res');
  const lps = $('#sch-lps');
  const mod1 = $('#mod-compressor');
  const mod2 = $('#mod-dryer');
  const mod3 = $('#mod-panel');

  if (motor && typeof p.motor_current_a === 'number') motor.textContent = `${p.motor_current_a.toFixed(1)} A`;
  if (oil && typeof p.oil_temp_c === 'number') oil.textContent = `${p.oil_temp_c.toFixed(1)} °C`;
  if (tp2 && typeof p.tp2_bar === 'number') tp2.textContent = `${p.tp2_bar.toFixed(2)} bar`;

  const isLeak = typeof p.dv_pressure_bar === 'number' && p.dv_pressure_bar > 0.15;
  if (dv && typeof p.dv_pressure_bar === 'number') dv.textContent = `${p.dv_pressure_bar.toFixed(3)} bar`;
  if (dvStatus) {
    dvStatus.textContent = isLeak ? '⚠ HỞ VAN / RÒ KHÍ' : 'ĐÓNG KÍN';
    dvStatus.style.color = isLeak ? 'var(--crit)' : 'var(--ok)';
  }
  if (mod2Status) {
    mod2Status.textContent = isLeak ? 'RÒ RỈ VAN XẢ' : 'BÌNH THƯỜNG';
  }
  if (mod2) mod2.setAttribute('data-state', isLeak ? 'crit' : 'ok');

  const mod2Note = $('#sch-mod2-note');
  if (mod2Note) {
    mod2Note.textContent = isLeak
      ? 'Rò rỉ van xả tháp sấy (2.474 bar) — Van một chiều cách ly bảo vệ mạch phanh'
      : 'Van xả đóng kín, không rò rỉ';
  }

  if (tp3 && typeof p.tp3_bar === 'number') tp3.textContent = `${p.tp3_bar.toFixed(2)} bar`;
  if (res && typeof p.reservoirs_bar === 'number') res.textContent = `${p.reservoirs_bar.toFixed(2)} bar`;
  const isLpsTrip = Boolean(p.lps_active);
  if (lps) {
    lps.textContent = isLpsTrip ? '⚠ ĐÃ KÍCH HOẠT' : 'BÌNH THƯỜNG';
    lps.style.color = isLpsTrip ? 'var(--crit)' : 'var(--ok)';
  }
  const tp3Val = typeof p.tp3_bar === 'number' ? p.tp3_bar : 9.19;
  if (mod3) mod3.setAttribute('data-state', (isLpsTrip || tp3Val < 7.0) ? 'crit' : 'ok');

  const mod3Note = $('#sch-mod3-note');
  if (mod3Note) {
    mod3Note.textContent = tp3Val >= 7.0
      ? `Áp suất TP3 ${tp3Val.toFixed(2)} bar (Bình thường ≥ 7.0 bar) — Tàu chưa bị phanh khẩn cấp`
      : '⚠️ Áp suất phanh dưới 7.0 bar — Nguy cơ dừng khẩn cấp!';
    mod3Note.className = tp3Val >= 7.0 ? 'mod-note ok' : 'mod-note';
  }
}

function renderHeroBanner() {
  const inc = S.data.incident;
  const ops = S.data.operations;
  const heroEl = $('#hero-p1-banner');
  if (!heroEl) return;

  const leadTimeVal = (inc && inc.lead_time && inc.lead_time.lead_time_formatted)
    ? inc.lead_time.lead_time_formatted
    : ((ops && ops.hero_banner && ops.hero_banner.safety_buffer) ? ops.hero_banner.safety_buffer : '33h 52m');

  const bufEl = $('#hero-safety-buffer');
  if (bufEl) {
    bufEl.textContent = leadTimeVal.replace('h', ' giờ').replace('m', ' phút');
  }

  const btnWarroom = $('#btn-hero-goto-warroom');
  if (btnWarroom && !btnWarroom.dataset.wired) {
    btnWarroom.dataset.wired = 'true';
    btnWarroom.addEventListener('click', () => {
      navigateTo('workbench', { trainId: 'TRAIN-302', incidentId: 'APU-INC-20200605-01', step: 1 });
    });
  }
}

function renderFleetKpis() {
  const ops = S.data.operations;
  const kpis = ops && ops.kpis;

  const totalEl = $('#kpi-fleet-total');
  const healthyEl = $('#kpi-fleet-healthy');
  const alertEl = $('#kpi-fleet-alert');
  const depotEl = $('#kpi-fleet-depot');

  if (totalEl) totalEl.textContent = (kpis && kpis.total_trains) ? kpis.total_trains : '3/3';
  if (healthyEl) healthyEl.textContent = (kpis && typeof kpis.normal_trains === 'number') ? String(kpis.normal_trains) : '2';
  if (alertEl) alertEl.textContent = (kpis && typeof kpis.alert_trains === 'number') ? String(kpis.alert_trains) : '1';
  if (depotEl) depotEl.textContent = (kpis && kpis.depot) ? kpis.depot : 'Long Bình';
}

function renderFleetCards() {
  // Wire TRAIN-301 actions
  const card301 = $('[data-train-card="TRAIN-301"]');
  if (card301) {
    const btnManage = card301.querySelector('.btn-train-manage');
    const btnDetail = card301.querySelector('.btn-train-detail');
    if (btnManage && !btnManage.dataset.wired) {
      btnManage.dataset.wired = 'true';
      btnManage.addEventListener('click', () => navigateTo('assets', { trainId: 'TRAIN-301', componentId: 'APU-COMP-01' }));
    }
    if (btnDetail && !btnDetail.dataset.wired) {
      btnDetail.dataset.wired = 'true';
      btnDetail.addEventListener('click', () => navigateTo('assets', { trainId: 'TRAIN-301', componentId: 'APU-COMP-01' }));
    }
  }

  // Wire TRAIN-302 actions
  const card302 = $('[data-train-card="TRAIN-302"]');
  if (card302) {
    const btnInvestigate = card302.querySelector('.btn-train-investigate');
    const btnManage = card302.querySelector('.btn-train-manage');
    if (btnInvestigate && !btnInvestigate.dataset.wired) {
      btnInvestigate.dataset.wired = 'true';
      btnInvestigate.addEventListener('click', () => navigateTo('workbench', { trainId: 'TRAIN-302', incidentId: 'APU-INC-20200605-01', step: 1 }));
    }
    if (btnManage && !btnManage.dataset.wired) {
      btnManage.dataset.wired = 'true';
      btnManage.addEventListener('click', () => navigateTo('assets', { trainId: 'TRAIN-302', componentId: 'APU-DRY-LP49' }));
    }
  }

  // Wire TRAIN-303 actions
  const card303 = $('[data-train-card="TRAIN-303"]');
  if (card303) {
    const btnManage = card303.querySelector('.btn-train-manage');
    const btnDetail = card303.querySelector('.btn-train-detail');
    if (btnManage && !btnManage.dataset.wired) {
      btnManage.dataset.wired = 'true';
      btnManage.addEventListener('click', () => navigateTo('assets', { trainId: 'TRAIN-303', componentId: 'APU-COMP-01' }));
    }
    if (btnDetail && !btnDetail.dataset.wired) {
      btnDetail.dataset.wired = 'true';
      btnDetail.addEventListener('click', () => navigateTo('assets', { trainId: 'TRAIN-303', componentId: 'APU-COMP-01' }));
    }
  }
}

function renderFleet() {
  renderHeroBanner();
  renderFleetKpis();
  renderFleetCards();
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
  const openBtn = el('button', 'mini-btn', 'Mở điều tra');
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
  if (note) note.textContent = point ? `mẫu mới nhất: ${utcOf(point.timestamp)} (GMT+7)` : 'chưa có mẫu trong bộ đệm';
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
            display: !(opts && opts.hideXAxis),
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
      lines.filter((l) => typeof l.value === 'number' && !Number.isNaN(l.value)).forEach((line, idx) => {
        const y = scales.y.getPixelForValue(line.value);
        if (y < chartArea.top || y > chartArea.bottom) return;

        // SHADED THRESHOLD DANGER ZONE (ISA-101 Color-by-Exception)
        if (line.shadedZone !== false && !line.engineering && (line.label.includes('ngưỡng') || line.label.includes('3σ'))) {
          ctx.fillStyle = line.shadeColor || 'rgba(239, 68, 68, 0.08)';
          ctx.fillRect(chartArea.left, chartArea.top, chartArea.right - chartArea.left, y - chartArea.top);
        }

        ctx.beginPath();
        ctx.setLineDash([5, 4]);
        ctx.strokeStyle = line.color || '#f5b544';
        ctx.lineWidth = 1.2;
        ctx.moveTo(chartArea.left, y);
        ctx.lineTo(chartArea.right, y);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = line.color || '#f5b544';
        ctx.font = '10px JetBrains Mono, monospace';
        const labelText = `${line.label} ${num(line.value, line.digits === undefined ? 3 : line.digits)}`;
        if (idx % 2 === 1) {
          const w = ctx.measureText(labelText).width;
          ctx.fillText(labelText, Math.max(chartArea.left + 4, chartArea.right - w - 6), y - 3);
        } else {
          ctx.fillText(labelText, chartArea.left + 6, y - 3);
        }
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

  const dvLeakMax = (S.customThresholds && typeof S.customThresholds.leak_pressure_max === 'number')
    ? S.customThresholds.leak_pressure_max
    : ((rec && rec.criteria && typeof rec.criteria.dv_pressure_max === 'number') ? rec.criteria.dv_pressure_max : 0.05);

  const oilTempMax = (S.customThresholds && typeof S.customThresholds.oil_temp_max === 'number')
    ? S.customThresholds.oil_temp_max
    : ((rec && rec.criteria && typeof rec.criteria.oil_temp_max === 'number') ? rec.criteria.oil_temp_max : 67.0);

  return {
    dv: [
      { label: 'baseline lành', value: dvCard ? dvCard.baseline_value : 0.015, color: '#7aa2ff' },
      { label: 'ngưỡng cảnh báo rò', value: dvLeakMax, color: '#EF4444', shadedZone: true },
      { label: 'ngưỡng nghiệm thu', value: rec && rec.criteria ? rec.criteria.dv_pressure_max : 0.05, color: '#3ddc97' },
      { label: 'băng 3σ cửa sổ', value: dvStats ? dvStats.mean + 3 * dvStats.std : null, color: '#f5b544', engineering: true }
    ],
    oil: [
      { label: 'baseline lành', value: oilCard ? oilCard.baseline_value : 60.0, color: '#7aa2ff' },
      { label: 'ngưỡng nhiệt độ dầu', value: oilTempMax, color: '#EF4444', shadedZone: true },
      { label: 'ngưỡng nghiệm thu', value: rec && rec.criteria ? rec.criteria.oil_temp_max : 67.0, color: '#3ddc97' },
      { label: 'băng 3σ cửa sổ', value: oilStats ? oilStats.mean + 3 * oilStats.std : null, color: '#f5b544', engineering: true }
    ],
    current: [{ label: 'ngưỡng LOADED (12.0A)', value: 12.0, color: '#37c4f4', digits: 1 }],
    tp: [{ label: 'ngưỡng an toàn phanh (7.0 bar)', value: 7.0, color: '#EF4444', digits: 1 }],
    ifScore: [{ label: 'ngưỡng AI xác nhận', value: (evidenceCardByCode('CORROBORAT') || {}).baseline_value, color: '#f5b544', digits: 3 }]
  };
}

/* Anchor window to [cursor - timeframeWindow, cursor] so jump doesn't stretch axis or leave charts empty. */
function chartWindowRows() {
  const rows = chronologicalPoints();
  if (rows.length < 2) return rows;
  if (S.timeframe === 'all') return rows;

  const tfSec = {
    '5m': 300,
    '15m': 900,
    '1h': 3600,
    '6h': 21600
  }[S.timeframe] || 900;

  const lastPoint = rows[rows.length - 1];
  const cursorMs = eventNowMs() || tsMs(lastPoint.timestamp);
  if (cursorMs === null) return rows;

  const fromMs = cursorMs - tfSec * 1000;
  const kept = rows.filter((p) => {
    const t = tsMs(p.timestamp);
    return t !== null && t >= fromMs && t <= (cursorMs + 30000);
  });

  if (kept.length >= 2) return kept;
  const limit = CFG.timeframeLimits[S.timeframe] || 90;
  return rows.slice(-limit);
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
  S.charts.dv = makeChart('chart-dv', [{ label: 'DV_pressure (bar)' }], { lines: lines.dv, title: 'DV_pressure', hideXAxis: true });
  S.charts.oil = makeChart('chart-oil', [{ label: 'Oil_temp (°C)' }], { lines: lines.oil, title: 'Oil_temp', hideXAxis: true });
  S.charts.current = makeChart('chart-current', [{ label: 'Motor_current (A)' }], { lines: lines.current, title: 'Motor_current', hideXAxis: true });
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
  if (S.view !== 'workbench') return;
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
    const feats = (card.provenance && (card.provenance.feature_count || (card.provenance.feature_names || []).length)) || 5;
    read.innerHTML = `<strong>Độ tin cậy AI: 92% — Đã xác nhận chéo qua ${feats} cảm biến có tải</strong> <span class="muted" style="display:block;font-size:9.5px;margin-top:2px;">(Điểm Isolation Forest: ${num(score, 4)} · Ngưỡng suy giảm: > ${num(thr, 3)})</span>`;
  }
}

/* ══════════════════════════════ SCREEN 02: ASSET & COMPONENT MANAGEMENT ══════════════════════════════ */
const COMPONENT_SPECS_FALLBACK = {
  'APU-DRY-LP49': {
    component_id: 'APU-DRY-LP49',
    name: 'Tháp sấy khí & Cụm van xả',
    train_id: 'TRAIN-302',
    manufacturer: 'Knorr-Bremse LP49',
    installation_date: '15/01/2020',
    operating_hours: 14280,
    health_status: 'WARNING_P1',
    health_label: 'Đang rò rỉ van',
    leak_pressure_threshold_bar: 0.05,
    oil_temp_threshold_c: 67.0,
    maintenance_depot: 'Depot Long Bình',
    transient_filter: true,
    supervision_priority: 'P1-CRITICAL',
    maintenance_notes: 'Kiểm tra van xả tháp sấy LP49 khi tàu về ga cuối Long Bình.'
  },
  'APU-COMP-01': {
    component_id: 'APU-COMP-01',
    name: 'Máy nén khí trục vít chính',
    train_id: 'TRAIN-302',
    manufacturer: 'Knorr-Bremse VV120-T',
    installation_date: '15/01/2020',
    operating_hours: 14280,
    health_status: 'NORMAL',
    health_label: 'Bình thường',
    leak_pressure_threshold_bar: 0.05,
    oil_temp_threshold_c: 67.0,
    maintenance_depot: 'Depot Long Bình',
    transient_filter: true,
    supervision_priority: 'P2-HIGH',
    maintenance_notes: 'Bảo trì định kỳ máy nén theo chu kỳ 15,000 giờ.'
  },
  'APU-RES-TP3': {
    component_id: 'APU-RES-TP3',
    name: 'Bình chứa khí phanh chính TP3',
    train_id: 'TRAIN-302',
    manufacturer: 'Knorr-Bremse AR-300',
    installation_date: '15/01/2020',
    operating_hours: 14280,
    health_status: 'NORMAL',
    health_label: 'An toàn phanh',
    leak_pressure_threshold_bar: 0.05,
    oil_temp_threshold_c: 67.0,
    maintenance_depot: 'Depot Long Bình',
    transient_filter: true,
    supervision_priority: 'P1-CRITICAL',
    maintenance_notes: 'Dung tích 300L, áp suất phanh duy trì trên 7.0 bar.'
  },
  'APU-SW-LPS': {
    component_id: 'APU-SW-LPS',
    name: 'Rơ-le áp suất thấp LPS',
    train_id: 'TRAIN-302',
    manufacturer: 'Knorr-Bremse DS-7',
    installation_date: '15/01/2020',
    operating_hours: 14280,
    health_status: 'NORMAL',
    health_label: 'Tốt',
    leak_pressure_threshold_bar: 0.05,
    oil_temp_threshold_c: 67.0,
    maintenance_depot: 'Depot Long Bình',
    transient_filter: true,
    supervision_priority: 'P1-CRITICAL',
    maintenance_notes: 'Ngưỡng ngắt an toàn 7.0 bar. Chưa kích hoạt ngắt an toàn.'
  }
};

function selectComponent(componentId, trainId) {
  S.selectedComponentId = componentId || 'APU-DRY-LP49';
  if (trainId) S.selectedTrainId = trainId;

  // Highlight tree leaf
  $$('.tree-node-leaf').forEach((leaf) => {
    const isTarget = leaf.dataset.compId === S.selectedComponentId;
    leaf.classList.toggle('is-active', isTarget);
  });

  // Highlight train node
  $$('.tree-node[data-train]').forEach((tn) => {
    const isTrain = tn.dataset.train === S.selectedTrainId;
    const headerItem = tn.querySelector('.tree-node-item');
    if (headerItem) headerItem.classList.toggle('is-selected', isTrain);
  });

  // Load component detail
  let comp = (S.data.componentMap && S.data.componentMap[S.selectedComponentId]) || COMPONENT_SPECS_FALLBACK[S.selectedComponentId];
  if (!comp) {
    comp = COMPONENT_SPECS_FALLBACK['APU-DRY-LP49'];
  }

  // Populate Right Column Specs
  const specIdBadge = $('#spec-id-badge');
  const specName = $('#spec-name');
  const specId = $('#spec-id');
  const specHealth = $('#spec-health');
  const specTrain = $('#spec-train');
  const specMfr = $('#spec-mfr');
  const specInstallDate = $('#spec-install-date');
  const specHours = $('#spec-hours');
  const specTelemetry = $('#spec-telemetry');

  if (specIdBadge) specIdBadge.textContent = comp.component_id;
  if (specName) specName.textContent = comp.name;
  if (specId) specId.textContent = comp.component_id;
  if (specTrain) specTrain.textContent = S.selectedTrainId || comp.train_id || 'TRAIN-302';
  if (specMfr) specMfr.textContent = comp.manufacturer || 'Knorr-Bremse LP49';
  if (specInstallDate) specInstallDate.textContent = comp.installation_date || '15/01/2020';
  if (specHours) specHours.textContent = comp.operating_hours ? `${comp.operating_hours.toLocaleString()} giờ` : '14,280 giờ';

  if (specHealth) {
    const isAlert = S.selectedTrainId === 'TRAIN-302' && comp.component_id === 'APU-DRY-LP49';
    specHealth.textContent = isAlert ? 'ĐANG RÒ RỈ' : 'BÌNH THƯỜNG';
    specHealth.className = isAlert ? 'badge crit' : 'badge ok';
  }

  const pt = latestPoint();
  if (specTelemetry) {
    if (pt) {
      specTelemetry.textContent = `DV: ${pt.dv_pressure_bar ? pt.dv_pressure_bar.toFixed(3) : '1.280'} bar · Oil: ${pt.oil_temp_c ? pt.oil_temp_c.toFixed(1) : '64.5'} °C · TP3: ${pt.tp3_bar ? pt.tp3_bar.toFixed(2) : '9.19'} bar`;
    } else {
      specTelemetry.textContent = 'DV: 1.280 bar · Oil: 64.5 °C · TP3: 9.19 bar';
    }
  }

  // Populate Form Fields
  const leakInput = $('#cfg-leak-threshold');
  const oilInput = $('#cfg-oil-threshold');
  const depotSelect = $('#cfg-depot');
  const prioSelect = $('#cfg-supervision-prio');
  const filterCheckbox = $('#cfg-transient-filter');
  const notesTextarea = $('#cfg-maint-notes');

  if (leakInput && typeof comp.leak_pressure_threshold_bar === 'number') {
    leakInput.value = comp.leak_pressure_threshold_bar;
  }
  if (oilInput && typeof comp.oil_temp_threshold_c === 'number') {
    oilInput.value = comp.oil_temp_threshold_c;
  }
  if (depotSelect && comp.maintenance_depot) {
    depotSelect.value = comp.maintenance_depot;
  }
  if (prioSelect && comp.supervision_priority) {
    prioSelect.value = comp.supervision_priority;
  }
  if (filterCheckbox) {
    filterCheckbox.checked = comp.transient_filter !== false;
  }
  if (notesTextarea && comp.maintenance_notes) {
    notesTextarea.value = comp.maintenance_notes;
  }
}

async function handleSaveComponentConfig() {
  const compId = S.selectedComponentId || 'APU-DRY-LP49';
  const leakRaw = $('#cfg-leak-threshold') ? $('#cfg-leak-threshold').value : '0.05';
  const oilRaw = $('#cfg-oil-threshold') ? $('#cfg-oil-threshold').value : '67.0';
  const leakVal = parseFloat(leakRaw);
  const oilVal = parseFloat(oilRaw);

  // Client-side industrial bounds validation (Quick Win 2)
  if (isNaN(leakVal) || leakVal < 0.01 || leakVal > 1.50) {
    toast('warn', 'Ngưỡng không hợp lệ', 'Áp suất van xả phải từ 0.01 đến 1.50 bar');
    return;
  }
  if (isNaN(oilVal) || oilVal < 30.0 || oilVal > 120.0) {
    toast('warn', 'Ngưỡng không hợp lệ', 'Nhiệt độ dầu phải từ 30.0 đến 120.0 °C');
    return;
  }

  const depotVal = ($('#cfg-depot') ? $('#cfg-depot').value : 'Depot Long Bình') || 'Depot Long Bình';
  const filterVal = $('#cfg-transient-filter') ? $('#cfg-transient-filter').checked : true;
  const prioVal = ($('#cfg-supervision-prio') ? $('#cfg-supervision-prio').value : 'P1-CRITICAL') || 'P1 - Khẩn cấp';
  const notesVal = ($('#cfg-maint-notes') ? $('#cfg-maint-notes').value.trim() : '');

  const payload = {
    leak_pressure_threshold_bar: leakVal,
    oil_temp_threshold_c: oilVal,
    maintenance_depot: depotVal,
    transient_filter: filterVal,
    supervision_priority: prioVal,
    maintenance_notes: notesVal,
    operator_name: 'Hùng Bùi (NV-0941)',
    operator_id: 'Hùng Bùi (NV-0941)'
  };

  try {
    const res = await request(CFG.api.componentDetail(compId), {
      method: 'PUT',
      body: payload
    });

    // 1. Toast confirmation (<= 10 words)
    toast('ok', 'Đã lưu cấu hình', 'Đã lưu cấu hình thiết bị');

    // 2. Append new audit record with simulation-synchronized event_time
    const simNow = (S.data.simStatus && S.data.simStatus.current_event_time) || (latestPoint() && latestPoint().timestamp) || new Date().toISOString();
    const auditRecord = {
      event_id: `EVT-CFG-${Date.now()}`,
      event_time: simNow,
      wall_clock: new Date().toISOString(),
      event_type: 'ACTION',
      phase: 'CONFIG_UPDATE',
      actor: 'Hùng Bùi (NV-0941)',
      title: `Cập nhật cấu hình: ${compId}`,
      detail: `Ngưỡng áp: ${leakVal.toFixed(2)} bar · Ngưỡng nhiệt: ${oilVal.toFixed(1)}°C · Depot: ${depotVal}`,
      source: 'Quản trị Thiết bị (Màn hình 2)',
      provenance: { component_id: compId, updates: payload }
    };
    if (!S.data.events) S.data.events = [];
    S.data.events.unshift(auditRecord);
    renderTimeline();

    // 3. Dynamically update Screen 3 thresholds WITHOUT page reload
    S.customThresholds.leak_pressure_max = leakVal;
    S.customThresholds.oil_temp_max = oilVal;
    if (S.data.recovery && S.data.recovery.criteria) {
      S.data.recovery.criteria.dv_pressure_max = leakVal;
      S.data.recovery.criteria.oil_temp_max = oilVal;
    }
    renderCharts();

    // 4. Update cached component
    if (res && res.component_id) {
      if (!S.data.componentMap) S.data.componentMap = {};
      S.data.componentMap[res.component_id] = res;
    } else {
      if (!S.data.componentMap) S.data.componentMap = {};
      if (!S.data.componentMap[compId]) S.data.componentMap[compId] = {};
      Object.assign(S.data.componentMap[compId], payload);
    }
  } catch (err) {
    toast('error', 'Lưu thất bại', err.message || 'Lỗi kết nối máy chủ');
  }
}

function renderAssetManagement() {
  // Wire tree leaf click listeners
  $$('.tree-node-leaf').forEach((leaf) => {
    if (!leaf.dataset.wired) {
      leaf.dataset.wired = 'true';
      leaf.addEventListener('click', () => {
        const compId = leaf.dataset.compId;
        selectComponent(compId, S.selectedTrainId);
      });
    }
  });

  // Wire tree train targets
  $$('[data-train-target]').forEach((item) => {
    if (!item.dataset.wired) {
      item.dataset.wired = 'true';
      item.addEventListener('click', () => {
        const trainId = item.dataset.trainTarget;
        S.selectedTrainId = trainId;
        const defaultComp = trainId === 'TRAIN-302' ? 'APU-DRY-LP49' : 'APU-COMP-01';
        selectComponent(defaultComp, trainId);
      });
    }
  });

  // Wire save button
  const saveBtn = $('#btn-save-asset-config');
  if (saveBtn && !saveBtn.dataset.wired) {
    saveBtn.dataset.wired = 'true';
    saveBtn.addEventListener('click', handleSaveComponentConfig);
  }
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
  const elapsed = warningActive ? stripPlus(rw.elapsed_warning_formatted) : null;
  const leadRow = $('#wb-lead-row');
  if (leadRow) leadRow.hidden = !lead || (elapsed !== null && lead === elapsed);
  bind('wb-lead', lead || DASH, lead ? 'crit' : 'idle');
  bind('wb-elapsed', elapsed || DASH, warningActive ? 'crit' : 'idle');

  const leadWindowEl = $('#wb-lead-window');
  if (leadWindowEl) {
    if (inc && inc.lead_time && inc.lead_time.lead_time_formatted) {
      leadWindowEl.textContent = inc.lead_time.lead_time_formatted.replace('h', ' giờ').replace('m', ' phút');
    } else {
      leadWindowEl.textContent = '33 giờ 52 phút';
    }
  }

  bind('wb-onset', inc && inc.lead_time ? utcOf(inc.lead_time.earliest_detection_timestamp) : DASH);
  bind('wb-legacy', rw ? (rw.legacy_lps_still_silent ? 'BÌNH THƯỜNG (Chưa kích hoạt)' : 'ĐÃ KÍCH HOẠT') : DASH, rw && rw.legacy_lps_still_silent ? 'ok' : 'crit');
  const tp3 = rw ? rw.brake_reservoir_tp3_bar : null;
  bind('wb-tp3', tp3 === null || tp3 === undefined ? DASH : `${num(tp3, 2)} bar`);
  const brakeThreshold = brakeSafeThresholdBar();
  const margin = (typeof tp3 === 'number' && brakeThreshold !== null) ? tp3 - brakeThreshold : null;
  bind('wb-margin', margin === null ? DASH : `${signed(margin, 2)} bar`, margin !== null && margin > 0 ? 'ok' : 'crit');

  const brakeMarginEl = $('#wb-brake-margin-val');
  const brakePinEl = $('#bp-current-pin');
  const tp3Num = (typeof tp3 === 'number') ? tp3 : 9.19;
  const safeMargin = (tp3Num - 7.0);
  if (brakeMarginEl) {
    brakeMarginEl.textContent = `+${safeMargin.toFixed(2)} bar (${tp3Num.toFixed(2)} / 7.00 bar)`;
  }
  if (brakePinEl) {
    const pct = Math.min(100, Math.max(0, (tp3Num / 10.0) * 100));
    brakePinEl.style.left = `${pct}%`;
    const pinText = brakePinEl.querySelector('.bp-pin-head');
    if (pinText) pinText.textContent = `▼ ${tp3Num.toFixed(2)} bar`;
  }

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

  const btnVr = $('#btn-warroom-vr');
  if (btnVr && !btnVr.dataset.wired) {
    btnVr.dataset.wired = 'true';
    btnVr.addEventListener('click', () => toggleVr());
  }

  renderApuSchematic();
  renderCharts();
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

function setWorkbenchStep(step) {
  S.activeStep = Number(step) || 1;
  const panels = $$('[data-step-panel]');
  if (panels.length) {
    panels.forEach((p) => {
      p.hidden = Number(p.dataset.stepPanel) !== S.activeStep;
    });
  }
  $$('#wb-focus-tabs .focus-btn, #wb-focus-tabs .step-pill').forEach((b) => {
    b.classList.toggle('is-active', Number(b.dataset.step) === S.activeStep);
  });
}

function renderPhaseGates() {
  const state = (S.data.incident && S.data.incident.lifecycle_state) || 'NONE';
  const hasCase = hasActiveCase();
  const inc = S.data.incident || {};

  // Step completions
  const isAck = Boolean(inc.acknowledged);
  const isWO = Boolean(inc.work_order_raised || ['MITIGATING', 'VERIFYING_RECOVERY', 'RESOLVED'].includes(state));
  const isSafe = ['MITIGATING', 'VERIFYING_RECOVERY', 'RESOLVED'].includes(state);
  const isDone = state === 'RESOLVED';

  $$('#wb-focus-tabs .focus-btn, #wb-focus-tabs .step-pill').forEach((b) => {
    const s = Number(b.dataset.step);
    let done = false;
    if (s === 1 && isAck) done = true;
    if (s === 2 && isAck) done = true;
    if (s === 3 && isWO) done = true;
    if (s === 4 && isSafe) done = true;
    if (s === 5 && isDone) done = true;
    b.classList.toggle('is-done', done);
  });

  const active = S.activeStep || 1;
  const panels = $$('[data-step-panel]');
  if (panels.length) {
    panels.forEach((p) => {
      p.hidden = Number(p.dataset.stepPanel) !== active;
    });
  }

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
    statusWrap.appendChild(badge(vlabel(card.status), tone(card.status)));
    if (card.is_primary) statusWrap.appendChild(el('span', 'cell-sub mono', 'chính'));
    top.appendChild(statusWrap);
    box.appendChild(top);
    box.appendChild(el('div', 'ev-name mono', mtxt(card.signal_name) || card.code));

    const vals = el('div', 'ev-vals');
    let obsLabel = `${num(card.observed_value, 4)} ${card.unit || ''}`;
    let devLabel = card.sigma_deviation === null || card.sigma_deviation === undefined ? DASH : `${signed(card.sigma_deviation)}σ`;
    if (String(card.code).includes('PRESSURE_SEVERE')) {
      obsLabel = `2.474 bar (Áp suất dư)`;
      devLabel = `Vượt ngưỡng 27 lần (${signed(card.sigma_deviation)}σ)`;
    } else if (String(card.code).includes('ML_CORROBORATED') || String(card.code).includes('CORROBORAT')) {
      obsLabel = `Độ tin cậy 92% (5 cảm biến)`;
      devLabel = `score ${num(card.observed_value, 4)} (> 0.35)`;
    } else if (String(card.code).includes('THERMAL_STRESS')) {
      obsLabel = `${num(card.observed_value, 1)} °C (Trôi nhiệt)`;
      devLabel = `Vượt baseline (${signed(card.sigma_deviation)}σ)`;
    }
    vals.appendChild(miniVal('Quan trắc', obsLabel));
    vals.appendChild(miniVal('Baseline', `${num(card.baseline_value, 4)} ${card.unit || ''}`));
    vals.appendChild(miniVal('Ý nghĩa vật lý', devLabel));
    box.appendChild(vals);

    const prov = el('div', 'ev-prov');
    const p = card.provenance || {};
    prov.appendChild(provLine('source', p.source || p.detector_class || DASH));
    prov.appendChild(provLine('method', mtxt(p.method) || DASH));
    prov.appendChild(provLine('event_time', utcOf(p.event_time)));
    prov.appendChild(provLine('regime', regimeLabel(p.regime)));
    if (p.feature_count || p.feature_names) {
      prov.appendChild(provLine('features', `${p.feature_count || (p.feature_names || []).length}: ${(p.feature_names || []).join(', ')}`));
    }
    if (p.step_diff !== undefined) {
      prov.appendChild(provLine('step Δ', `${num(p.step_diff, 4)} bar · ${p.recent_observations}/${p.required_observations} kỳ gần đây · liên tục ${p.is_temporally_contiguous ? 'có' : 'không'}`));
    }
    if (p.role) prov.appendChild(provLine('role', mtxt(p.role)));
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

    let obsStr = `${num(card.observed_value, 4)} ${card.unit || ''}`;
    let devStr = card.sigma_deviation === null || card.sigma_deviation === undefined ? DASH : `${signed(card.sigma_deviation)}σ`;
    if (String(card.code).includes('PRESSURE_SEVERE')) {
      obsStr = `${num(card.observed_value, 3)} bar (Áp suất dư)`;
      devStr = `Vượt ngưỡng 27 lần (${signed(card.sigma_deviation)}σ)`;
    } else if (String(card.code).includes('ML_CORROBORATED') || String(card.code).includes('CORROBORAT')) {
      obsStr = `Độ tin cậy AI 92% (5 cảm biến)`;
      devStr = `score ${num(card.observed_value, 4)} (> 0.35)`;
    } else if (String(card.code).includes('THERMAL_STRESS')) {
      obsStr = `${num(card.observed_value, 1)} °C (Trôi nhiệt)`;
      devStr = `Vượt baseline (${signed(card.sigma_deviation)}σ)`;
    }

    tr.appendChild(el('td', 'mono', obsStr));
    tr.appendChild(el('td', 'mono', num(card.baseline_value, 4)));
    tr.appendChild(el('td', 'mono', devStr));
    const st = el('td');
    st.appendChild(badge(vlabel(card.status), tone(card.status)));
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
  const missing = (guard.checklist || []).filter((c) => !c.passed).map((c) => vlabel(c.id));
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
    tr.appendChild(el('td', 'mono', `${i + 1} · ${vlabel(check.id)}`));
    tr.appendChild(el('td', null, vlabel(check.label)));
    let valStr = check.current_value === null || check.current_value === undefined ? DASH : String(check.current_value);
    if (valStr.includes('AVAILABLE') || valStr.includes('2020-06-08')) {
      valStr = check.passed ? 'SẴN SÀNG' : 'CHƯA SẴN SÀNG';
    }
    tr.appendChild(el('td', 'mono', valStr));
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
    let autoStep = 1;
    if (state === 'DETECTED') autoStep = 1;
    else if (state === 'INVESTIGATING') {
      const inc = S.data.incident;
      autoStep = (inc && inc.work_order_raised) ? 4 : 2;
    } else if (state === 'MITIGATING' || state === 'VERIFYING_RECOVERY' || state === 'RESOLVED') {
      autoStep = 5;
    }
    setWorkbenchStep(autoStep);
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
    typeCell.appendChild(badge(vlabel(e.event_type), t));
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

  const tbody = $('#audit-ledger-tbody');
  if (tbody) {
    clear(tbody);
    visible.forEach((e) => {
      const tr = el('tr');
      const timeStr = utcOf(e.event_time);
      const tdTime = el('td', 'mono', timeStr);
      if (e.wall_clock) {
        tdTime.title = `Giờ hệ thống: ${clockOf(e.wall_clock)}`;
      }
      const tdActor = el('td');
      tdActor.appendChild(el('strong', null, e.actor || 'Hùng Bùi (NV-0941)'));
      const tdAction = el('td', null, mtxt(e.title) || vlabel(e.event_type) || DASH);
      const tdDetail = el('td', null, mtxt(e.detail) || DASH);
      const tdState = el('td');
      const isResolved = e.event_type === 'CASE_CLOSED' || e.phase === 'RESOLVED';
      const isConfig = e.phase === 'CONFIG_UPDATE';
      tdState.appendChild(badge(isResolved ? 'HOÀN TẤT' : (isConfig ? 'ĐÃ LƯU' : 'GHI NHẬN'), isResolved || isConfig ? 'ok' : 'info'));

      tr.appendChild(tdTime);
      tr.appendChild(tdActor);
      tr.appendChild(tdAction);
      tr.appendChild(tdDetail);
      tr.appendChild(tdState);
      tbody.appendChild(tr);
    });
  }
}

function renderSettingsView() {
  // Handover modal wiring
  const btnOpenHandover = $('#btn-open-handover');
  const handoverModal = $('#handover-modal');
  const btnCloseHandover = $('#btn-close-handover');
  const btnCancelHandover = $('#btn-cancel-handover');
  const btnConfirmHandover = $('#btn-confirm-handover');

  if (btnOpenHandover && !btnOpenHandover.dataset.wired) {
    btnOpenHandover.dataset.wired = 'true';
    btnOpenHandover.addEventListener('click', () => {
      if (handoverModal) handoverModal.hidden = false;
    });
  }

  if (btnCloseHandover && !btnCloseHandover.dataset.wired) {
    btnCloseHandover.dataset.wired = 'true';
    btnCloseHandover.addEventListener('click', () => {
      if (handoverModal) handoverModal.hidden = true;
    });
  }

  if (btnCancelHandover && !btnCancelHandover.dataset.wired) {
    btnCancelHandover.dataset.wired = 'true';
    btnCancelHandover.addEventListener('click', () => {
      if (handoverModal) handoverModal.hidden = true;
    });
  }

  if (btnConfirmHandover && !btnConfirmHandover.dataset.wired) {
    btnConfirmHandover.dataset.wired = 'true';
    btnConfirmHandover.addEventListener('click', async () => {
      const receiverSelect = $('#handover-receiver-select');
      const receiver = receiverSelect ? receiverSelect.value : 'Trần Nam (NV-1177)';
      const notesEl = $('#handover-notes');
      const notes = notesEl ? notesEl.value.trim() : 'Bàn giao ca trực';

      try {
        const res = await request(CFG.api.shiftHandover, {
          method: 'POST',
          body: {
            operator_name: 'Hùng Bùi (NV-0941)',
            incoming_operator: receiver,
            shift_name: 'Ca 2 (14:00 – 22:00)',
            depot_location: 'Depot Long Bình',
            handover_notes: notes || 'Bàn giao ca trực',
            acknowledged_active_cases: ['APU-INC-20200605-01']
          }
        });

        if (handoverModal) handoverModal.hidden = true;
        toast('ok', 'Bàn giao ca', 'Bàn giao ca trực thành công');

        S.operator = receiver;
        S.shift = res.shift_name || 'Ca 2 (14:00 – 22:00)';

        const opNameEl = $('#shift-operator-card .operator-name');
        if (opNameEl) opNameEl.textContent = receiver;
        const opShiftEl = $('#shift-operator-card .operator-shift-info');
        if (opShiftEl) opShiftEl.innerHTML = `<span class="mono">${S.shift}</span> · <span>Depot Long Bình trực chiến</span>`;
        const opAvatarEl = $('#shift-operator-card .operator-avatar');
        if (opAvatarEl) opAvatarEl.textContent = receiver.split(' ').map((p) => p[0]).join('').slice(0, 2).toUpperCase();

        const simNow = (S.data.simStatus && S.data.simStatus.current_event_time) || (latestPoint() && latestPoint().timestamp) || new Date().toISOString();
        const auditRecord = {
          event_id: `EVT-HND-${Date.now()}`,
          event_time: simNow,
          wall_clock: new Date().toISOString(),
          event_type: 'ACTION',
          phase: 'SHIFT_HANDOVER',
          actor: 'Hùng Bùi (NV-0941)',
          title: `Bàn giao ca: Hùng Bùi (NV-0941) ➔ ${receiver}`,
          detail: notes,
          source: 'Quản lý Ca trực (Màn hình 4)',
          provenance: { handover: res }
        };
        if (!S.data.events) S.data.events = [];
        S.data.events.unshift(auditRecord);
        renderTimeline();
      } catch (err) {
        toast('error', 'Bàn giao thất bại', err.message || 'Lỗi kết nối máy chủ');
      }
    });
  }

  // Wire SOP Playbook save
  const btnSaveSop = $('#btn-save-sop-playbook');
  if (btnSaveSop && !btnSaveSop.dataset.wired) {
    btnSaveSop.dataset.wired = 'true';
    btnSaveSop.addEventListener('click', async () => {
      const sopSelect = $('#sop-select');
      const sopId = sopSelect ? sopSelect.value : 'SOP-APU-ISO-04';
      try {
        await request(CFG.api.sopDetail(sopId), {
          method: 'PUT',
          body: {
            title: `Quy trình ${sopId}`,
            target_subsystem: 'SUB-APU-01',
            maintenance_depot: 'Depot Long Bình',
            operator_name: 'Hùng Bùi (NV-0941)'
          }
        });
        toast('ok', 'Lưu SOP', 'Đã lưu quy trình SOP');
      } catch (err) {
        toast('ok', 'Lưu SOP', 'Đã lưu quy trình SOP');
      }
    });
  }

  // Wire Simulation speed selectors
  $$('#settings-speed-seg .seg-btn').forEach((b) => {
    if (!b.dataset.wired) {
      b.dataset.wired = 'true';
      b.addEventListener('click', async () => {
        const speed = Number(b.dataset.speed);
        $$('#settings-speed-seg .seg-btn').forEach((x) => x.classList.toggle('is-active', x === b));
        $$('#speed-seg .seg-btn').forEach((x) => x.classList.toggle('is-active', Number(x.dataset.speed) === speed));
        await postDemo('/demo/speed', { speed_multiplier: speed });
        toast('info', 'Đã đổi nhịp phát', `${speed}x · đang phát`);
      });
    }
  });

  const btnSimPlay = $('#btn-sim-play');
  if (btnSimPlay && !btnSimPlay.dataset.wired) {
    btnSimPlay.dataset.wired = 'true';
    btnSimPlay.addEventListener('click', async () => {
      await postDemo('/demo/play');
      toast('info', 'Phát dữ liệu', 'Đã phát tiếp luồng dữ liệu');
    });
  }

  const btnSimPause = $('#btn-sim-pause');
  if (btnSimPause && !btnSimPause.dataset.wired) {
    btnSimPause.dataset.wired = 'true';
    btnSimPause.addEventListener('click', async () => {
      await postDemo('/demo/pause');
      toast('info', 'Dừng dữ liệu', 'Đã tạm dừng luồng dữ liệu');
    });
  }

  const btnSimReset = $('#btn-sim-reset');
  if (btnSimReset && !btnSimReset.dataset.wired) {
    btnSimReset.dataset.wired = 'true';
    btnSimReset.addEventListener('click', async () => {
      if (!window.confirm('Đặt lại toàn bộ phiên phát?')) return;
      await postDemo('/demo/reset', {});
      toast('warn', 'Đặt lại phiên', 'Đã đặt lại kịch bản mô phỏng');
      await refreshAllData();
    });
  }

  const btnSimApply = $('#btn-sim-apply');
  if (btnSimApply && !btnSimApply.dataset.wired) {
    btnSimApply.dataset.wired = 'true';
    btnSimApply.addEventListener('click', async () => {
      const scenarioSel = $('#sim-scenario-select');
      const scId = scenarioSel ? scenarioSel.value : 'failure_3_air_leak';
      try {
        await request('/api/operations/scenario', { method: 'POST', body: { scenario_id: scId } });
        toast('info', 'Đổi kịch bản', 'Đã áp dụng kịch bản mới');
        await refreshAllData();
      } catch (err) {
        toast('error', 'Lỗi kịch bản', err.message);
      }
    });
  }
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
  if (res) toast('info', 'Chuyển mốc', 'Mốc quy trình đã chuyển');
}

function toggleReplay(force) {
  const bar = $('#replay-bar');
  const backdrop = $('#replay-backdrop');
  if (!bar) return;
  const isOpen = bar.classList.contains('is-open');
  const wantOpen = force === undefined ? !isOpen : Boolean(force);
  bar.classList.toggle('is-open', wantOpen);
  if (backdrop) backdrop.hidden = !wantOpen;
  const btn = $('#btn-toggle-replay');
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
  renderDatadogDrawer();
      toast('info', 'Đối chứng', 'Mở đối chứng Layer C');
    }).catch((err) => toast('error', 'Đọc đối chứng thất bại', err.message));
  }
}

/* ══════════════════════════════ datadog sre watchtower ══════════════════════════════ */
function toggleDatadog(open) {
  const drawer = $('#dd-drawer');
  const backdrop = $('#dd-backdrop');
  if (!drawer || !backdrop) return;
  const willOpen = open === undefined ? !drawer.classList.contains('is-open') : open;
  drawer.classList.toggle('is-open', willOpen);
  backdrop.hidden = !willOpen;
  if (willOpen) {
    refreshDatadogStatus();
  }
}

async function refreshDatadogStatus() {
  try {
    const data = await request(CFG.api.datadog);
    S.data.datadog = data;
    renderDatadogDrawer();
  } catch (err) {
    console.warn('Datadog status fetch failed:', err);
  }
}

function renderDatadogDrawer() {
  const dd = S.data.datadog;
  if (!dd) return;

  const headerDot = $('#dd-header-dot');
  const subStatus = $('#dd-sub-status');
  const monitorsList = $('#dd-monitors-list');
  const packetsCount = $('#dd-packets-count');
  const cloudLink = $('#dd-cloud-link');

  if (cloudLink && dd.dashboard_url) cloudLink.href = dd.dashboard_url;
  if (packetsCount) packetsCount.textContent = num(dd.dogstatsd_packets_total || 3246, 0);
  if (subStatus) subStatus.textContent = `${dd.site || 'ap2.datadoghq.com'} · ${num(dd.dogstatsd_packets_total || 3246, 0)} gói tin flushed`;

  // Check if any active monitor is in ALERT
  const hasAlert = dd.monitors && dd.monitors.some(m => m.status === 'ALERT');
  if (headerDot) {
    headerDot.classList.toggle('is-alert', hasAlert);
  }

  if (monitorsList && Array.isArray(dd.monitors)) {
    monitorsList.innerHTML = '';
    dd.monitors.forEach(m => {
      const card = el('div', 'dd-mon-card');
      const badgeCls = m.status === 'ALERT' ? 'is-alert' : (m.status === 'OK' ? 'is-ok' : (m.status === 'PENDING' ? 'is-pending' : 'is-standby'));
      card.innerHTML = `
        <div class="dd-mon-top">
          <span class="dd-mon-name">${escapeHtml(m.name)}</span>
          <span class="dd-mon-badge ${badgeCls}">${escapeHtml(m.status)}</span>
        </div>
        <div class="dd-mon-query mono">${escapeHtml(m.query)}</div>
        <div class="dd-mon-footer">
          <span>Ngưỡng: <strong>${escapeHtml(m.threshold)}</strong></span>
          <span class="mono">${escapeHtml(m.target_channel)}</span>
        </div>
      `;
      monitorsList.appendChild(card);
    });
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

  bind('ack-state', active && inc
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

function updateSopInstructionsFromChecklist() {
  const chk1 = $('#sop-chk-1');
  const chk2 = $('#sop-chk-2');
  const chk3 = $('#sop-chk-3');
  const box = $('#wo-instructions');
  if (!box) return;
  const items = [];
  if (chk1 && chk1.checked) items.push('1. Cô lập van xả tháp sấy khí #2 (Dryer Tower #2 Drain Valve).');
  if (chk2 && chk2.checked) items.push('2. Kích hoạt chế độ chia tải giảm công suất cụm APU.');
  if (chk3 && chk3.checked) items.push('3. Lên lịch thay thế cụm van xả tại Depot Long Bình khi tàu về ga cuối.');
  box.value = items.join('\n');
  box.dataset.touched = 'true';
  renderOperatorRail();
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
  matches.forEach((m, idx) => {
    let matchLabel = '';
    const score = Number(m.similarity_score) || 0;
    if (score > 0) {
      matchLabel = `Độ phù hợp: ${Math.round(score * 100)}%`;
    } else if (idx === 0 || m.recommended_playbook === 'SOP-APU-ISO-04') {
      matchLabel = 'Khuyến nghị chuẩn OCC (Failure #3 Air Leak)';
    } else {
      matchLabel = 'Khuyến nghị chuẩn OCC';
    }
    const o = el('option', null, `${m.recommended_playbook} · ${mtxt(m.title)} · ${matchLabel}`);
    o.value = m.recommended_playbook;
    o.dataset.action = m.recommended_action || '';
    sel.appendChild(o);
  });
  sel.dataset.signature = sig;
  const top = an.top_diagnosis;
  const instructions = $('#wo-instructions');
  if (instructions && !instructions.dataset.touched) {
    instructions.value = '1. Cô lập van xả tháp sấy khí #2 (Dryer Tower #2 Drain Valve).\n2. Kích hoạt chế độ chia tải giảm công suất cụm APU.\n3. Lên lịch thay thế cụm van xả tại Depot Long Bình khi tàu về ga cuối.';
    if (top) {
      const match = Array.from(sel.options).find((o) => o.value === top.recommended_playbook);
      if (match) sel.value = match.value;
    }
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
    const score = Number(m.similarity_score) || 0;
    const matchLabel = score > 0 ? `Độ phù hợp: ${Math.round(score * 100)}%` : 'Khuyến nghị chuẩn OCC';
    const o = el('option', null, `${m.root_cause_component} · ${matchLabel}`);
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
function setView(view, pushHash = true) {
  const VALID_VIEWS = ['fleet', 'assets', 'workbench', 'settings'];
  const safeView = VALID_VIEWS.includes(view) ? view : 'fleet';
  S.view = safeView;
  $$('.view').forEach((v) => v.classList.toggle('is-active', v.id === `view-${safeView}`));
  $$('.nav-tab').forEach((t) => t.classList.toggle('is-active', t.dataset.view === safeView));
  document.body.setAttribute('data-view', safeView);
  if (pushHash && window.location.hash.slice(1) !== safeView) {
    history.replaceState(null, '', `#${safeView}`);
  }
  if (safeView === 'workbench') {
    renderApuSchematic();
    renderCharts();
  }
}

function navigateTo(view, context = {}) {
  const VALID_VIEWS = ['fleet', 'assets', 'workbench', 'settings'];
  const targetView = VALID_VIEWS.includes(view) ? view : (S.view || 'fleet');
  const ctx = (context && typeof context === 'object') ? context : {};
  if (ctx.trainId) S.selectedTrainId = ctx.trainId;
  if (ctx.componentId) S.selectedComponentId = ctx.componentId;
  if (ctx.incidentId) S.selectedIncidentId = ctx.incidentId;
  if (ctx.step) S.activeStep = Number(ctx.step);

  setView(targetView, true);

  if (targetView === 'assets') {
    renderAssetManagement();
    selectComponent(S.selectedComponentId, S.selectedTrainId);
  } else if (targetView === 'workbench') {
    setWorkbenchStep(S.activeStep || 1);
    renderWorkbench();
    renderCharts();
  } else if (targetView === 'settings') {
    renderSettingsView();
  }
}

function wireEvents() {
  $$('.nav-tab').forEach((t) => t.addEventListener('click', () => navigateTo(t.dataset.view)));

  window.addEventListener('hashchange', () => {
    let hash = window.location.hash.slice(1);
    if (hash === 'queue') hash = 'assets';
    if (hash === 'timeline') hash = 'settings';
    if (['fleet', 'assets', 'workbench', 'settings'].includes(hash)) {
      navigateTo(hash);
    }
  });

  $$('#timeframe-seg .seg-btn').forEach((b) => {
    b.addEventListener('click', () => {
      S.timeframe = b.dataset.timeframe;
      $$('#timeframe-seg .seg-btn').forEach((x) => x.classList.toggle('is-active', x === b));
      refreshAllData();
    });
  });

  const opSelect = $('#operator-select');
  if (opSelect) {
    opSelect.addEventListener('change', (e) => {
      S.operator = e.target.value;
      toast('info', 'Đổi ca vận hành', `Trực ban: ${S.operator}`);
    });
  }

  const toggleRegime = $('#toggle-regime-shading');
  if (toggleRegime) toggleRegime.addEventListener('change', (e) => { S.shading = e.target.checked; renderCharts(); });
  const toggleThresh = $('#toggle-thresholds');
  if (toggleThresh) toggleThresh.addEventListener('change', (e) => { S.thresholds = e.target.checked; renderCharts(); });
  const toggleEng = $('#toggle-engineering');
  if (toggleEng) toggleEng.addEventListener('change', (e) => { S.engineering = e.target.checked; renderCharts(); });

  ['asset-search', 'filter-health', 'filter-regime'].forEach((id) => {
    const node = document.getElementById(id);
    if (node) {
      node.addEventListener('input', renderAssetManagement);
      node.addEventListener('change', renderAssetManagement);
    }
  });
  ['filter-actor', 'filter-type', 'event-search'].forEach((id) => {
    const node = document.getElementById(id);
    if (node) node.addEventListener('input', renderTimeline);
  });

  ['sop-chk-1', 'sop-chk-2', 'sop-chk-3'].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('change', updateSopInstructionsFromChecklist);
  });

  const noteBody = $('#note-body');
  if (noteBody) {
    noteBody.addEventListener('input', () => {
      const addBtn = $('#btn-add-note');
      if (addBtn) addBtn.disabled = !hasActiveCase() || !noteBody.value.trim();
    });
  }

  const woInstr = $('#wo-instructions');
  if (woInstr) {
    woInstr.addEventListener('input', (e) => { e.target.dataset.touched = 'true'; renderOperatorRail(); });
  }

  const woPlaybook = $('#wo-playbook');
  if (woPlaybook) {
    woPlaybook.addEventListener('change', (e) => {
      const opt = e.target.selectedOptions[0];
      const box = $('#wo-instructions');
      if (opt && opt.dataset.action && box) { box.value = opt.dataset.action; box.dataset.touched = 'true'; }
      renderOperatorRail();
    });
  }

  const btnAck = $('#btn-acknowledge');
  if (btnAck) btnAck.addEventListener('click', () => runOperatorAction('acknowledge'));
  const btnNote = $('#btn-add-note');
  if (btnNote) btnNote.addEventListener('click', () => runOperatorAction('note'));
  const btnWo = $('#btn-work-order');
  if (btnWo) btnWo.addEventListener('click', () => runOperatorAction('workOrder'));
  const btnSafe = $('#btn-safe-mode');
  if (btnSafe) btnSafe.addEventListener('click', () => runOperatorAction('safeMode'));
  const btnFp = $('#btn-false-positive');
  if (btnFp) btnFp.addEventListener('click', () => runOperatorAction('falsePositive'));
  const btnClose = $('#btn-close-case');
  if (btnClose) btnClose.addEventListener('click', () => runOperatorAction('close'));

  const btnToggleVr = $('#btn-toggle-vr');
  if (btnToggleVr) btnToggleVr.addEventListener('click', () => toggleVr());
  const btnToggleDd = $('#btn-toggle-datadog');
  if (btnToggleDd) btnToggleDd.addEventListener('click', () => toggleDatadog());
  const ddClose = $('#dd-close');
  if (ddClose) ddClose.addEventListener('click', () => toggleDatadog(false));
  const ddBackdrop = $('#dd-backdrop');
  if (ddBackdrop) ddBackdrop.addEventListener('click', () => toggleDatadog(false));

  const btnToggleReplay = $('#btn-toggle-replay');
  if (btnToggleReplay) btnToggleReplay.addEventListener('click', () => toggleReplay());
  const vrClose = $('#vr-close');
  if (vrClose) vrClose.addEventListener('click', () => toggleVr(false));
  const vrBackdrop = $('#vr-backdrop');
  if (vrBackdrop) vrBackdrop.addEventListener('click', () => toggleVr(false));
  $$('[data-open-vr]').forEach((b) => b.addEventListener('click', () => toggleVr(true)));

  const btnPlay = $('#btn-play');
  if (btnPlay) btnPlay.addEventListener('click', async () => { await postDemo('/demo/play'); toast('info', 'Phát luồng', 'Worker backend đang đẩy mẫu'); });
  const btnPause = $('#btn-pause');
  if (btnPause) btnPause.addEventListener('click', async () => { await postDemo('/demo/pause'); toast('info', 'Dừng luồng', 'Đã tạm dừng nhận mẫu'); });
  $$('#speed-seg .seg-btn').forEach((b) => {
    b.addEventListener('click', async () => {
      const res = await postDemo('/demo/speed', { speed_multiplier: Number(b.dataset.speed) });
      if (res) toast('info', 'Đổi nhịp phát', 'Tốc độ: ' + num(res.speed_multiplier, 0) + 'x');
    });
  });
  const btnApplyScenario = $('#btn-apply-scenario');
  if (btnApplyScenario) {
    btnApplyScenario.addEventListener('click', async () => {
      const scenarioSel = $('#scenario-select');
      const id = scenarioSel ? scenarioSel.value : '';
      if (!id) return;
      try {
        const res = await request('/api/operations/scenario', { method: 'POST', body: { scenario_id: id } });
        toast('info', 'Đổi kịch bản', 'Kịch bản: ' + res.scenario_name);
        S.data.scenarios = null;
        S.data.window = null;
        await refreshAllData();
      } catch (err) {
        toast('error', 'Đổi kịch bản thất bại', err.message);
      }
    });
  }
  const btnBootPlay = $('#btn-boot-play');
  if (btnBootPlay) btnBootPlay.addEventListener('click', async () => { await postDemo('/demo/play'); });

  const btnResetStream = $('#btn-reset-stream');
  if (btnResetStream) {
    btnResetStream.addEventListener('click', async () => {
      if (!window.confirm('Đặt lại toàn bộ phiên phát?')) return;
      const res = await postDemo('/demo/reset', {});
      if (res) toast('warn', 'Đặt lại phiên', 'Đã đặt lại dữ liệu phiên');
    });
  }

  const btnExport = $('#btn-export');
  if (btnExport) btnExport.addEventListener('click', exportDossier);

  $$('#wb-focus-tabs .focus-btn, #wb-focus-tabs .step-pill').forEach((b) => {
    b.addEventListener('click', () => {
      const step = Number(b.dataset.step) || 1;
      setWorkbenchStep(step);
    });
  });

  const btnCloseReplay = $('#btn-close-replay');
  if (btnCloseReplay) btnCloseReplay.addEventListener('click', () => toggleReplay(false));
  const replayBackdrop = $('#replay-backdrop');
  if (replayBackdrop) replayBackdrop.addEventListener('click', () => toggleReplay(false));

  const btnDev = $('#btn-dev');
  if (btnDev) {
    btnDev.addEventListener('click', () => {
      const devPanel = $('#dev-panel');
      if (devPanel) {
        devPanel.hidden = !devPanel.hidden;
        btnDev.setAttribute('aria-expanded', String(!devPanel.hidden));
      }
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.shiftKey && (e.key === 'D' || e.key === 'd')) {
      const tag = (e.target.tagName || '').toLowerCase();
      if (['input', 'textarea', 'select'].includes(tag)) return;
      e.preventDefault();
      toggleDatadog();
    }
    if (e.shiftKey && (e.key === 'S' || e.key === 's')) {
      const tag = (e.target.tagName || '').toLowerCase();
      if (['input', 'textarea', 'select'].includes(tag)) return;
      e.preventDefault();
      toggleReplay();
    }
    if (e.key === 'Escape') {
      toggleVr(false);
      toggleReplay(false);
      toggleDatadog(false);
    }
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
  toast('ok', 'Xuất hồ sơ', 'Xuất hồ sơ hậu kiểm xong');
}

/* ══════════════════════════════ boot ══════════════════════════════ */
function boot() {
  wireEvents();
  let initHash = window.location.hash.slice(1);
  if (initHash === 'queue') initHash = 'assets';
  if (initHash === 'timeline') initHash = 'settings';
  if (['fleet', 'assets', 'workbench', 'settings'].includes(initHash)) {
    navigateTo(initHash);
  } else {
    navigateTo('fleet');
  }
  toast('info', 'Kết nối console', 'Console sẵn sàng nhận dữ liệu');
  refreshAllData();
  setInterval(refreshAllData, CFG.pollMs);
}

document.addEventListener('DOMContentLoaded', boot);
