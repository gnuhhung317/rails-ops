/**
 * CompressorGuard — Industrial Operations Command Console
 * Reactive SPA Engine v2.3
 */

// --- Global Application State ---
const state = {
  currentView: 'operations', // 'operations', 'active_cases', 'workspace'
  activeWorkspaceTab: 'what_changed', // 'what_changed', 'evidence', 'what_did_we_do', 'did_it_work', 'timeline'
  isDrawerOpen: false,
  isSimRunning: false,
  simSpeed: 60.0,
  
  operations: null,
  activeCase: null,
  evidence: null,
  recovery: null,
  timeline: [],
  validationRef: null,
  simStatus: null,
  
  simTimer: null,
  refreshInterval: null
};

// --- API Client ---
const api = {
  async getOperations() {
    const res = await fetch('/api/operations');
    return res.json();
  },
  async getCase() {
    const res = await fetch('/api/case');
    return res.json();
  },
  async getEvidence() {
    const res = await fetch('/api/evidence');
    return res.json();
  },
  async getRecovery() {
    const res = await fetch('/api/recovery');
    return res.json();
  },
  async getTimeline() {
    const res = await fetch('/api/case/events');
    return res.json();
  },
  async getValidationReference() {
    const res = await fetch('/api/validation-reference');
    return res.json();
  },
  async getSimStatus() {
    const res = await fetch('/demo/status');
    return res.json();
  },
  async tick() {
    const res = await fetch('/demo/tick', { method: 'POST' });
    return res.json();
  },
  async jump(milestone) {
    const res = await fetch('/demo/jump', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ milestone })
    });
    return res.json();
  },
  async reset(milestone = null) {
    const res = await fetch('/demo/reset', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(milestone ? { milestone } : {})
    });
    return res.json();
  },
  async play() {
    const res = await fetch('/demo/play', { method: 'POST' });
    return res.json();
  },
  async pause() {
    const res = await fetch('/demo/pause', { method: 'POST' });
    return res.json();
  },
  async setSpeed(speed_multiplier) {
    const res = await fetch('/demo/speed', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ speed_multiplier })
    });
    return res.json();
  },
  async triggerSafeMode() {
    const res = await fetch('/api/action/safe-mode', { method: 'POST' });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || err.error || 'ActionGuard rejected safe mode');
    }
    return res.json();
  },
  async closeCase(notes = 'Verified recovery. Asset released back to revenue service.') {
    const res = await fetch('/api/case/close', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ operator_id: 'DISPATCHER-0941', notes })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || err.error || 'Recovery criteria not verified');
    }
    return res.json();
  }
};

// --- Toast Notifications ---
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  const colorMap = {
    info: 'border-sky-500 bg-slate-900/90 text-sky-300',
    success: 'border-emerald-500 bg-slate-900/90 text-emerald-300',
    warning: 'border-amber-500 bg-slate-900/90 text-amber-300',
    error: 'border-rose-500 bg-slate-900/90 text-rose-300'
  };
  toast.className = `toast-message flex items-center gap-3 px-4 py-3 rounded-lg border text-sm shadow-xl backdrop-blur-md ${colorMap[type] || colorMap.info}`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// --- Data Refresh & Orchestration ---
async function refreshAllData() {
  try {
    const [ops, sim] = await Promise.all([
      api.getOperations(),
      api.getSimStatus().catch(() => null)
    ]);
    state.operations = ops;
    state.simStatus = sim;

    if (ops.active_case) {
      state.activeCase = ops.active_case;
      const [ev, rec, tl] = await Promise.all([
        api.getEvidence().catch(() => null),
        api.getRecovery().catch(() => null),
        api.getTimeline().catch(() => [])
      ]);
      state.evidence = ev;
      state.recovery = rec;
      state.timeline = tl;
    } else {
      // Fallback fetch case endpoint to check if CLOSED or NONE
      const c = await api.getCase().catch(() => null);
      state.activeCase = c;
      if (c) {
        const [ev, rec, tl] = await Promise.all([
          api.getEvidence().catch(() => null),
          api.getRecovery().catch(() => null),
          api.getTimeline().catch(() => [])
        ]);
        state.evidence = ev;
        state.recovery = rec;
        state.timeline = tl;
      }
    }

    renderHeader();
    renderMainView();
  } catch (err) {
    console.error('Error refreshing data:', err);
  }
}

// --- View & Tab Switching ---
function setView(viewName) {
  state.currentView = viewName;
  document.querySelectorAll('.nav-btn').forEach(btn => {
    if (btn.dataset.view === viewName) {
      btn.classList.add('border-sky-500', 'text-sky-400', 'bg-sky-500/10');
      btn.classList.remove('border-transparent', 'text-slate-400');
    } else {
      btn.classList.remove('border-sky-500', 'text-sky-400', 'bg-sky-500/10');
      btn.classList.add('border-transparent', 'text-slate-400');
    }
  });
  renderMainView();
}

function setWorkspaceTab(tabName) {
  state.activeWorkspaceTab = tabName;
  document.querySelectorAll('.workspace-tab-btn').forEach(btn => {
    if (btn.dataset.tab === tabName) {
      btn.classList.add('border-sky-500', 'text-sky-400', 'bg-sky-500/10');
      btn.classList.remove('border-transparent', 'text-slate-400');
    } else {
      btn.classList.remove('border-sky-500', 'text-sky-400', 'bg-sky-500/10');
      btn.classList.add('border-transparent', 'text-slate-400');
    }
  });
  renderWorkspaceSubTabs();
}

function toggleDrawer(open = null) {
  state.isDrawerOpen = open !== null ? open : !state.isDrawerOpen;
  const drawer = document.getElementById('validation-drawer');
  const backdrop = document.getElementById('drawer-backdrop');
  if (state.isDrawerOpen) {
    drawer.classList.remove('translate-x-full');
    backdrop.classList.remove('opacity-0', 'pointer-events-none');
    backdrop.classList.add('opacity-100');
    loadValidationDrawer();
  } else {
    drawer.classList.add('translate-x-full');
    backdrop.classList.add('opacity-0', 'pointer-events-none');
    backdrop.classList.remove('opacity-100');
  }
}

async function loadValidationDrawer() {
  if (!state.validationRef) {
    state.validationRef = await api.getValidationReference().catch(() => null);
  }
  const ref = state.validationRef;
  const content = document.getElementById('drawer-content-body');
  if (!ref || !content) return;
  content.innerHTML = `
    <div class="space-y-5 text-sm">
      <div class="p-3 bg-slate-900/70 border border-slate-700/60 rounded-lg">
        <div class="text-xs uppercase font-semibold text-slate-400 mb-1">Scenario Identifier</div>
        <div class="text-base font-bold text-sky-400">${ref.scenario_name} (${ref.scenario_id})</div>
        <div class="text-xs text-slate-400 mt-1">${ref.dataset_source} · ${ref.historical_period}</div>
      </div>

      <div class="space-y-3">
        <div class="p-3 bg-slate-900/40 border border-slate-800 rounded-lg">
          <div class="text-xs uppercase font-semibold text-amber-400 mb-1">Reported Failure Mode</div>
          <div class="text-slate-200 font-medium">${ref.reported_failure_mode}</div>
          <div class="text-xs text-slate-400 mt-1">First degradation noted: <span class="mono text-slate-300">${ref.reported_failure_start}</span></div>
        </div>

        <div class="p-3 bg-slate-900/40 border border-slate-800 rounded-lg">
          <div class="text-xs uppercase font-semibold text-rose-400 mb-1">Conventional LPS Alarm Trip</div>
          <div class="mono text-slate-200">${ref.conventional_lps_breach}</div>
          <div class="text-xs text-slate-400 mt-1">Reactive mechanical pressure switch tripped at 2.88 bar</div>
        </div>

        <div class="p-3 bg-slate-900/40 border border-slate-800 rounded-lg">
          <div class="text-xs uppercase font-semibold text-emerald-400 mb-1">CompressorGuard Online Detection</div>
          <div class="mono text-slate-200">${ref.online_detector_confirmation}</div>
          <div class="text-xs text-emerald-400 mt-1 font-semibold">Confirmed Lead Time: ${ref.confirmed_intervention_window_formatted} (${ref.confirmed_intervention_window_minutes} mins)</div>
        </div>

        <div class="p-3 bg-slate-900/40 border border-slate-800 rounded-lg">
          <div class="text-xs uppercase font-semibold text-slate-400 mb-1">Historical Maintenance Work Order</div>
          <div class="text-xs text-slate-300 leading-relaxed">${ref.maintenance_summary}</div>
        </div>
      </div>

      <div class="p-4 bg-sky-950/20 border border-sky-800/40 rounded-lg text-xs text-sky-200/90 leading-relaxed">
        <div class="font-bold text-sky-300 mb-1">🔬 Scientific Zero-Leakage Principle</div>
        This ground truth record exists strictly for post-hoc validation and operator auditing. It has zero interaction with online detectors or the decision engine.
      </div>
    </div>
  `;
}

// --- Simulation Controls ---
async function onPlayPause() {
  if (state.isSimRunning) {
    await api.pause();
    state.isSimRunning = false;
    clearInterval(state.simTimer);
    showToast('Simulation paused', 'info');
  } else {
    await api.play();
    state.isSimRunning = true;
    startSimulationLoop();
    showToast(`Simulation running at ${state.simSpeed}x speed`, 'success');
  }
  updatePlayButtonUI();
}

function updatePlayButtonUI() {
  const btn = document.getElementById('btn-play-pause');
  if (!btn) return;
  if (state.isSimRunning) {
    btn.innerHTML = `<span>⏸</span><span>Pause</span>`;
    btn.classList.add('bg-amber-600/20', 'text-amber-400', 'border-amber-500/40');
    btn.classList.remove('bg-sky-600/20', 'text-sky-400', 'border-sky-500/40');
  } else {
    btn.innerHTML = `<span>▶</span><span>Play</span>`;
    btn.classList.remove('bg-amber-600/20', 'text-amber-400', 'border-amber-500/40');
    btn.classList.add('bg-sky-600/20', 'text-sky-400', 'border-sky-500/40');
  }
}

function startSimulationLoop() {
  clearInterval(state.simTimer);
  // Calculate interval based on 10s step / simSpeed. Bound to min 100ms
  const intervalMs = Math.max(100, Math.round(10000 / state.simSpeed));
  state.simTimer = setInterval(async () => {
    if (!state.isSimRunning) return;
    try {
      await api.tick();
      await refreshAllData();
      if (state.activeCase && state.activeCase.phase === 'CLOSED') {
        state.isSimRunning = false;
        clearInterval(state.simTimer);
        updatePlayButtonUI();
      }
    } catch (e) {
      console.error('Tick error:', e);
    }
  }, intervalMs);
}

async function onStep() {
  try {
    await api.tick();
    await refreshAllData();
    showToast('Stepped 10 seconds forward', 'info');
  } catch (e) {
    showToast(e.message, 'error');
  }
}

async function onSpeedChange(mult) {
  state.simSpeed = mult;
  await api.setSpeed(mult);
  document.querySelectorAll('.speed-btn').forEach(btn => {
    if (parseFloat(btn.dataset.speed) === mult) {
      btn.classList.add('bg-sky-500', 'text-slate-950', 'font-bold');
      btn.classList.remove('bg-slate-800', 'text-slate-300');
    } else {
      btn.classList.remove('bg-sky-500', 'text-slate-950', 'font-bold');
      btn.classList.add('bg-slate-800', 'text-slate-300');
    }
  });
  if (state.isSimRunning) {
    startSimulationLoop();
  }
  showToast(`Pacing speed adjusted to ${mult}x`, 'info');
}

async function onMilestoneJump(milestone) {
  try {
    showToast(`Jumping to milestone: ${milestone}...`, 'info');
    await api.jump(milestone);
    await refreshAllData();
    showToast(`Arrived at milestone: ${milestone}`, 'success');
  } catch (e) {
    showToast(e.message, 'error');
  }
}

async function onReset() {
  try {
    await api.reset();
    state.isSimRunning = false;
    clearInterval(state.simTimer);
    updatePlayButtonUI();
    await refreshAllData();
    showToast('Simulation reset to initial stream onset', 'info');
  } catch (e) {
    showToast(e.message, 'error');
  }
}

// --- Safe Mode & Case Closure Handlers ---
async function onTriggerSafeMode() {
  const btn = document.getElementById('btn-safe-mode');
  if (btn) btn.disabled = true;
  try {
    showToast('Validating ActionGuard 5 pre-flight criteria...', 'info');
    const res = await api.triggerSafeMode();
    showToast(`Safe Mode Activated! Stream branched to Post-Maintenance segment (2020-06-08 16:05:00 UTC)`, 'success');
    await refreshAllData();
    setWorkspaceTab('did_it_work');
  } catch (e) {
    showToast(e.message, 'error');
    if (btn) btn.disabled = false;
  }
}

async function onCloseCase() {
  const btn = document.getElementById('btn-close-case');
  if (btn) btn.disabled = true;
  try {
    showToast('Validating 5/5 healthy LOADED recovery criteria...', 'info');
    const res = await api.closeCase();
    showToast(`Case closed! Asset APU-COMP-01 released back to normal revenue service.`, 'success');
    await refreshAllData();
    setView('operations');
  } catch (e) {
    showToast(e.message, 'error');
    if (btn) btn.disabled = false;
  }
}

// --- Header Rendering ---
function renderHeader() {
  const ops = state.operations;
  const sim = state.simStatus;
  const activeCase = state.activeCase;

  // Header clocks
  const eventTimeEl = document.getElementById('hdr-event-time');
  const simSpeedEl = document.getElementById('hdr-sim-speed');
  const liveBadgeEl = document.getElementById('hdr-live-badge');

  if (eventTimeEl && sim && sim.current_event_time) {
    eventTimeEl.textContent = `${sim.current_event_time.replace('T', ' ').replace('Z', '')} UTC`;
  }

  // Counters
  const cntAssets = document.getElementById('cnt-monitored-assets');
  const cntCases = document.getElementById('cnt-active-cases');
  const cntObserving = document.getElementById('cnt-assets-observing');
  const cntLead = document.getElementById('cnt-lead-time');

  if (ops && ops.operations_summary) {
    const s = ops.operations_summary;
    if (cntAssets) cntAssets.textContent = `${s.monitored_assets_count} ASSET`;
    if (cntCases) {
      cntCases.textContent = `${s.active_cases_count} ACTIVE ${s.active_cases_count === 1 ? 'CASE' : 'CASES'}`;
      if (s.active_cases_count > 0) {
        cntCases.className = 'px-3 py-1 text-xs font-semibold rounded-md border badge-critical flex items-center gap-1.5';
      } else {
        cntCases.className = 'px-3 py-1 text-xs font-semibold rounded-md border badge-healthy flex items-center gap-1.5';
      }
    }
    if (cntObserving) cntObserving.textContent = `${s.assets_observing_count} OBSERVING`;
    if (cntLead) {
      cntLead.textContent = s.confirmed_intervention_window || 'STANDBY';
    }
  }
}

// --- Main View Dispatcher ---
function renderMainView() {
  const container = document.getElementById('view-container');
  if (!container) return;

  if (state.currentView === 'operations') {
    renderOperationsView(container);
  } else if (state.currentView === 'active_cases') {
    renderActiveCasesView(container);
  } else if (state.currentView === 'workspace') {
    renderWorkspaceView(container);
  }
}

// --- SCREEN 01: Operations & Fleet Assets Landing ---
function renderOperationsView(container) {
  const ops = state.operations;
  const hasActiveCase = ops && ops.active_case != null;
  const isObservingExcursion = ops && ops.operations_summary && ops.operations_summary.assets_observing_count > 0 && !hasActiveCase;
  const assetHealth = hasActiveCase ? (ops.active_case.asset_health || 'CRITICAL') : (isObservingExcursion ? 'DEGRADING' : 'HEALTHY');

  const healthBadgeClass = {
    HEALTHY: 'badge-healthy',
    DEGRADING: 'badge-warning',
    CRITICAL: 'badge-critical pulse-critical'
  }[assetHealth] || 'badge-healthy';

  container.innerHTML = `
    <div class="space-y-6">
      <!-- Operational Metric Counters Bar -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="glass-card p-4 rounded-xl border border-slate-800">
          <div class="text-xs uppercase font-semibold text-slate-400">Monitored Assets</div>
          <div class="text-2xl font-black text-slate-100 mt-1 mono">1 Asset</div>
          <div class="text-xs text-emerald-400 mt-1 flex items-center gap-1">● Continuous Replay Telemetry</div>
        </div>

        <div class="glass-card p-4 rounded-xl border border-slate-800">
          <div class="text-xs uppercase font-semibold text-slate-400">Active Incident Cases</div>
          <div class="text-2xl font-black mt-1 mono ${hasActiveCase ? 'text-rose-400' : 'text-slate-100'}">
            ${hasActiveCase ? '1 Active' : '0 Active'}
          </div>
          <div class="text-xs ${hasActiveCase ? 'text-rose-400' : 'text-slate-400'} mt-1">
            ${hasActiveCase ? '⚠️ Critical intervention required' : '✓ Normal operations posture'}
          </div>
        </div>

        <div class="glass-card p-4 rounded-xl border border-slate-800">
          <div class="text-xs uppercase font-semibold text-slate-400">Asset Observation State</div>
          <div class="text-2xl font-black text-slate-100 mt-1 mono">
            ${isObservingExcursion ? '1 Observing' : 'Baseline Norm'}
          </div>
          <div class="text-xs ${isObservingExcursion ? 'text-amber-400' : 'text-slate-400'} mt-1">
            ${isObservingExcursion ? 'Transient excursion filtered' : 'Zero unconfirmed alarms'}
          </div>
        </div>

        <div class="glass-card p-4 rounded-xl border border-slate-800">
          <div class="text-xs uppercase font-semibold text-slate-400">Intervention Window</div>
          <div class="text-2xl font-black text-sky-400 mt-1 mono">
            ${(hasActiveCase && ops.operations_summary.confirmed_intervention_window) ? ops.operations_summary.confirmed_intervention_window : '33h 52m Lead'}
          </div>
          <div class="text-xs text-slate-400 mt-1">Deterministic LPS baseline gap</div>
        </div>
      </div>

      <!-- Fleet Asset Hierarchy Spine (Enterprise APM Hierarchy) -->
      <div class="glass-panel p-6 rounded-xl border border-slate-800">
        <div class="flex items-center justify-between pb-4 border-b border-slate-800 mb-5">
          <div>
            <h2 class="text-base font-bold text-slate-100 tracking-wide flex items-center gap-2">
              <span>🏢</span> FLEET ASSET HIERARCHY (CÂY PHÂN CẤP TÀI SẢN VẬN HÀNH)
            </h2>
            <p class="text-xs text-slate-400 mt-0.5">Mô hình phân cấp chuẩn Siemens Senseye & IBM Maximo: Liên kết trực tiếp linh kiện vật lý tới an toàn đoàn tàu chở khách.</p>
          </div>
          <div class="text-xs mono px-2.5 py-1 rounded bg-slate-800/80 text-slate-300 border border-slate-700/60">
            Hierarchy: Fleet → Train → Subsystem → Compressor
          </div>
        </div>

        <div class="space-y-4 pl-2 font-mono text-xs">
          <!-- Fleet Node -->
          <div class="flex items-center gap-3 text-slate-200">
            <span class="text-slate-500">▼</span>
            <span class="px-2 py-0.5 rounded bg-sky-950/80 text-sky-400 border border-sky-800/60 font-bold">FLEET</span>
            <span class="font-bold text-slate-100">Linha Azul (Lisbon Metro Passenger Fleet)</span>
            <span class="text-slate-500 text-[11px] font-sans">— Illustrative Business Context (Tuyến Xanh chở khách)</span>
          </div>

          <!-- Train Node -->
          <div class="flex items-center gap-3 pl-6 text-slate-300">
            <span class="text-slate-500">└── ▼</span>
            <span class="px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700 font-bold">TRAIN-302</span>
            <span class="text-slate-100">Commercial Passenger Train</span>
            <span class="text-xs px-2 py-0.5 rounded ${hasActiveCase ? 'bg-rose-950/60 text-rose-300 border border-rose-800/60' : 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/60'}">
              ${hasActiveCase ? '⚠️ TRAIN AT RISK' : 'NORMAL SERVICE'}
            </span>
          </div>

          <!-- Subsystem Node -->
          <div class="flex items-center gap-3 pl-12 text-slate-300">
            <span class="text-slate-500">└── ▼</span>
            <span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">SUB-APU-01</span>
            <span class="text-slate-200">Air Production Unit (APU)</span>
            <span class="text-slate-400 font-sans text-[11px]">Cung cấp khí nén cho hệ thống phanh khí động & đóng mở cửa</span>
          </div>

          <!-- Compressor Asset Node -->
          <div class="pl-16">
            <div class="p-4 rounded-xl bg-slate-900/80 border border-slate-700/80 space-y-3">
              <div class="flex flex-wrap items-center justify-between gap-3">
                <div class="flex items-center gap-3">
                  <span class="text-lg">⚙️</span>
                  <div>
                    <div class="text-sm font-bold text-slate-100 mono">APU-COMP-01 (Air Compressor Unit #1)</div>
                    <div class="text-xs text-slate-400 font-sans">Knorr-Bremse Piston Compressor · Monitored by MetroPT-3 Telemetry</div>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <span class="px-2.5 py-1 rounded text-xs font-semibold ${healthBadgeClass}">${assetHealth}</span>
                  <span class="px-2 py-1 rounded text-xs bg-slate-800 text-slate-300 border border-slate-700 mono">REGIME: LOADED</span>
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2 border-t border-slate-800 text-xs">
                <div>
                  <span class="text-slate-400 font-sans">Active Case Status:</span>
                  <div class="font-bold mono mt-0.5 ${hasActiveCase ? 'text-rose-400' : 'text-emerald-400'}">
                    ${hasActiveCase ? 'CASE-20200605-01 (OPEN)' : 'NONE (NORMAL MONITORING)'}
                  </div>
                </div>
                <div>
                  <span class="text-slate-400 font-sans">Operational Risk:</span>
                  <div class="text-slate-300 font-sans mt-0.5">
                    ${hasActiveCase ? 'Nguy cơ sập áp phanh bình chứa H1 → Dừng tàu khẩn cấp' : 'Áp suất nén duy trì ổn định, an toàn chở khách'}
                  </div>
                </div>
                <div class="flex items-end justify-start md:justify-end">
                  ${hasActiveCase ? `
                    <button onclick="setView('workspace')" class="px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-bold text-xs transition flex items-center gap-1.5 shadow-lg shadow-sky-900/30">
                      <span>👉</span><span>OPEN CASE WORKSPACE</span>
                    </button>
                  ` : `
                    <button onclick="onMilestoneJump('onset_0950')" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs border border-slate-700 transition">
                      Simulate Failure #3 Onset
                    </button>
                  `}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Noise Rejection Demonstration Panel (Screen 01: 00:33:07 UTC) -->
      <div class="glass-panel p-6 rounded-xl border border-slate-800">
        <div class="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
          <div class="flex items-center gap-2">
            <span class="text-amber-400 text-lg">👁️</span>
            <div>
              <h3 class="text-sm font-bold text-slate-100 uppercase tracking-wider">
                Signal Observation Watchlist — Noise Rejection Demo (00:33:07 UTC)
              </h3>
              <p class="text-xs text-slate-400">Trình diễn chống báo động ảo: Phân biệt xung đột biến tức thời với hư hỏng vật lý bền vững.</p>
            </div>
          </div>
          <button onclick="onMilestoneJump('early_excursion_0033')" class="px-3 py-1.5 rounded bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-semibold transition">
            Replay 00:33:07 Excursion
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div class="p-4 rounded-lg bg-slate-900/70 border border-slate-800">
            <div class="text-xs text-slate-400 uppercase font-semibold">Discharge Valve Pressure (DV)</div>
            <div class="text-xl font-bold mono text-amber-400 mt-1">0.52 bar <span class="text-xs text-amber-500">(+4.21σ)</span></div>
            <div class="text-[11px] text-slate-400 mt-1">Source: PressureAnomalyDetector</div>
            <div class="mt-2 text-xs px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 inline-block font-semibold">
              TRANSIENT SPIKE OBSERVED
            </div>
          </div>

          <div class="p-4 rounded-lg bg-slate-900/70 border border-slate-800">
            <div class="text-xs text-slate-400 uppercase font-semibold">Thermal Drift (Oil Temp)</div>
            <div class="text-xl font-bold mono text-emerald-400 mt-1">56.10 °C <span class="text-xs text-slate-400">(+0.32σ)</span></div>
            <div class="text-[11px] text-slate-400 mt-1">Source: ThermalDriftDetector</div>
            <div class="mt-2 text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 inline-block font-semibold">
              NORMAL BASELINE THERMAL
            </div>
          </div>

          <div class="p-4 rounded-lg bg-slate-900/70 border border-slate-800">
            <div class="text-xs text-slate-400 uppercase font-semibold">Multivariate ML (Isolation Forest)</div>
            <div class="text-xl font-bold mono text-emerald-400 mt-1">0.182 <span class="text-xs text-slate-400">(&lt; 0.350)</span></div>
            <div class="text-[11px] text-slate-400 mt-1">Role: Independent Corroboration</div>
            <div class="mt-2 text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 inline-block font-semibold">
              MULTIVARIATE NORMAL
            </div>
          </div>
        </div>

        <div class="p-4 rounded-lg bg-slate-900/90 border border-slate-700/60 flex items-start gap-3">
          <div class="text-sky-400 text-lg mt-0.5">ℹ️</div>
          <div class="space-y-1 text-xs">
            <div class="font-bold text-slate-200">System Anti-Fatigue Reasoning:</div>
            <div class="text-slate-300 leading-relaxed">
              "A transient pressure excursion of 0.52 bar (+4.21σ) occurred at 00:33:07 UTC. However, thermal drift is absent (+0.32σ) and Isolation Forest confirms multivariate normality. Temporal persistence check: 1/3 loaded cycles. 
              <span class="text-amber-300 font-semibold">CASE CREATION IS SUPPRESSED</span> to prevent operator alert fatigue."
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

// --- SCREEN 02: Active Cases List ---
function renderActiveCasesView(container) {
  const ops = state.operations;
  const activeCase = state.activeCase;
  const hasActive = activeCase && activeCase.phase && activeCase.phase !== 'NONE' && activeCase.phase !== 'CLOSED';

  container.innerHTML = `
    <div class="space-y-6">
      <!-- Siemens Invariant Policy Banner -->
      <div class="p-4 rounded-xl bg-slate-900/90 border border-slate-800 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <span class="text-sky-400 text-xl">🛡️</span>
          <div>
            <div class="text-xs font-bold uppercase tracking-wider text-slate-200">Bất biến quản trị vận hành Siemens Senseye</div>
            <div class="text-xs text-slate-400 mt-0.5">Tối đa một Active Case trên một Asset tại một thời điểm. Mọi phát hiện mới được nối vào Evidence Chain của Case hiện hành.</div>
          </div>
        </div>
        <div class="text-xs px-3 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700 mono font-semibold">
          Asset: APU-COMP-01
        </div>
      </div>

      <!-- Active Cases Section -->
      <div>
        <h2 class="text-sm font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
          <span>🚨</span> Active Operational Cases (${hasActive ? '1' : '0'})
        </h2>

        ${hasActive ? `
          <div class="glass-panel p-6 rounded-xl border border-rose-500/40 relative overflow-hidden">
            <div class="absolute top-0 right-0 w-32 h-32 bg-rose-500/5 rounded-full blur-2xl pointer-events-none"></div>
            
            <div class="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800 mb-4">
              <div class="flex items-center gap-3">
                <span class="px-2.5 py-1 rounded text-xs font-black mono bg-rose-500/20 text-rose-300 border border-rose-500/40">
                  CASE-20200605-01
                </span>
                <span class="text-xs px-2.5 py-1 rounded font-bold uppercase ${activeCase.asset_health === 'CRITICAL' ? 'badge-critical' : 'badge-warning'}">
                  ${activeCase.asset_health || 'CRITICAL'}
                </span>
                <span class="text-xs px-2.5 py-1 rounded font-bold mono bg-purple-500/10 text-purple-300 border border-purple-500/30">
                  PHASE: ${activeCase.phase}
                </span>
              </div>
              <div class="text-right">
                <div class="text-xs text-slate-400 font-sans">Confirmed Intervention Window</div>
                <div class="text-lg font-black mono text-sky-400">
                  ${activeCase.lead_time?.lead_time_formatted || '33h 52m'}
                </div>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs mb-5">
              <div class="space-y-2">
                <div>
                  <span class="text-slate-400">Asset Hierarchy:</span>
                  <span class="text-slate-200 mono font-bold ml-1">Linha Azul ──► Train #302 ──► APU ──► APU-COMP-01</span>
                </div>
                <div>
                  <span class="text-slate-400">Summary:</span>
                  <span class="text-slate-200 font-medium ml-1">${activeCase.summary || 'Severe Discharge Valve Degradation with Thermal Drift'}</span>
                </div>
                <div>
                  <span class="text-slate-400">Confirmed Detection:</span>
                  <span class="text-slate-300 mono ml-1">${activeCase.detection_milestone?.confirmed_detection_timestamp || '2020-06-05 09:50:39 UTC'}</span>
                </div>
              </div>

              <div class="space-y-2">
                <div>
                  <span class="text-slate-400">Operational Risk:</span>
                  <span class="text-rose-300 font-semibold ml-1">Pneumatic line pressure collapse risk. Stoppage in tunnel if unaddressed.</span>
                </div>
                <div>
                  <span class="text-slate-400">Evidence Pack:</span>
                  <span class="text-slate-300 ml-1 font-mono">[Pressure +23.75σ] [Thermal +5.71σ] [Persistence 3/3] [ML Corroborated 0.382]</span>
                </div>
                <div>
                  <span class="text-slate-400">Assigned Dispatcher:</span>
                  <span class="text-slate-300 mono ml-1">DISPATCHER-0941 (Current Active Shift)</span>
                </div>
              </div>
            </div>

            <div class="flex items-center justify-between pt-4 border-t border-slate-800">
              <div class="text-xs text-slate-400 flex items-center gap-2">
                <span class="text-emerald-400">✓</span> ActionGuard 5 Safety Checks Cleared — Safe Mode simulation ready
              </div>
              <button onclick="setView('workspace')" class="px-5 py-2.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-bold text-xs transition flex items-center gap-2 shadow-lg shadow-sky-900/40">
                <span>👉</span><span>OPEN CASE WORKSPACE (4 TIERS)</span>
              </button>
            </div>
          </div>
        ` : `
          <div class="p-8 rounded-xl bg-slate-900/40 border border-slate-800 text-center space-y-3">
            <div class="text-3xl">🟢</div>
            <div class="text-sm font-bold text-slate-200">No Active Incidents Pending</div>
            <div class="text-xs text-slate-400 max-w-md mx-auto">
              All monitored rail assets are operating within healthy nominal boundaries. To simulate an operational degradation scenario, jump to the 09:50 milestone.
            </div>
            <button onclick="onMilestoneJump('onset_0950')" class="mt-2 px-4 py-2 rounded-lg bg-sky-600/20 hover:bg-sky-600/30 text-sky-300 border border-sky-500/30 text-xs font-semibold transition">
              Simulate Failure #3 Onset (09:50:39 UTC)
            </button>
          </div>
        `}
      </div>

      <!-- Past Resolved Cases History -->
      <div>
        <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
          Past Resolved Cases (Lịch sử sự cố đã nghiệm thu đóng hồ sơ)
        </h3>
        <div class="glass-panel rounded-xl border border-slate-800 divide-y divide-slate-800/80 text-xs">
          <div class="p-4 flex items-center justify-between">
            <div class="space-y-0.5">
              <div class="font-bold mono text-slate-200">CASE-20200512-04 · Train #302 (APU-COMP-01)</div>
              <div class="text-slate-400">Oil Filter High Differential Pressure Degradation — Scheduled filter cartridge replacement</div>
            </div>
            <div class="text-right">
              <div class="text-emerald-400 font-semibold">Closed & Verified ✓</div>
              <div class="text-slate-500 mono">2020-05-13 14:20 UTC</div>
            </div>
          </div>

          <div class="p-4 flex items-center justify-between">
            <div class="space-y-0.5">
              <div class="font-bold mono text-slate-200">CASE-20200420-01 · Train #301 (APU-COMP-02)</div>
              <div class="text-slate-400">Caudal Airflow Flowmeter Sensor Drift — Recalibrated during depot overhaul</div>
            </div>
            <div class="text-right">
              <div class="text-emerald-400 font-semibold">Closed & Verified ✓</div>
              <div class="text-slate-500 mono">2020-04-20 09:15 UTC</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

// --- SCREEN 03 - 07: Case Workspace (5 Sub-tabs) ---
function renderWorkspaceView(container) {
  const activeCase = state.activeCase || {};
  const phase = activeCase.phase || 'INVESTIGATING';
  const leadFormatted = activeCase.lead_time?.lead_time_formatted || '33h 52m';

  container.innerHTML = `
    <div class="space-y-6">
      <!-- Case Workspace Header Bar -->
      <div class="glass-panel p-5 rounded-xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-3">
            <span class="text-xs font-black mono px-2.5 py-1 rounded bg-sky-950 text-sky-400 border border-sky-800/60">
              CASE-20200605-01
            </span>
            <h1 class="text-base font-bold text-slate-100">
              APU-COMP-01 (Train #302 — Linha Azul)
            </h1>
            <span class="text-xs px-2.5 py-0.5 rounded font-bold uppercase ${phase === 'RESOLVED' || phase === 'CLOSED' ? 'badge-healthy' : 'badge-critical'}">
              PHASE: ${phase}
            </span>
          </div>
          <div class="text-xs text-slate-400 mt-1">
            Confirmed degradation detection: <span class="mono text-slate-300">2020-06-05 09:50:39 UTC</span> · Operator: <span class="mono text-slate-300">DISPATCHER-0941</span>
          </div>
        </div>

        <div class="flex items-center gap-6">
          <div class="text-right">
            <div class="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">Confirmed Intervention Window</div>
            <div class="text-2xl font-black mono text-sky-400 leading-none mt-0.5">${leadFormatted}</div>
            <div class="text-[10px] text-slate-500 mt-0.5">2,032 mins ahead of LPS alert</div>
          </div>
          <button onclick="toggleDrawer(true)" class="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-semibold transition flex items-center gap-1.5">
            <span>🗄️</span><span>Validation Ref</span>
          </button>
        </div>
      </div>

      <!-- Workspace 5 Sub-Tabs Navigation -->
      <div class="flex border-b border-slate-800 text-xs font-semibold gap-1">
        <button onclick="setWorkspaceTab('what_changed')" data-tab="what_changed" class="workspace-tab-btn px-4 py-2.5 border-b-2 ${state.activeWorkspaceTab === 'what_changed' ? 'border-sky-500 text-sky-400 bg-sky-500/10' : 'border-transparent text-slate-400 hover:text-slate-200'} transition flex items-center gap-1.5">
          <span>1.</span><span>WHAT CHANGED?</span>
        </button>
        <button onclick="setWorkspaceTab('evidence')" data-tab="evidence" class="workspace-tab-btn px-4 py-2.5 border-b-2 ${state.activeWorkspaceTab === 'evidence' ? 'border-sky-500 text-sky-400 bg-sky-500/10' : 'border-transparent text-slate-400 hover:text-slate-200'} transition flex items-center gap-1.5">
          <span>2.</span><span>WHY? (EVIDENCE)</span>
        </button>
        <button onclick="setWorkspaceTab('what_did_we_do')" data-tab="what_did_we_do" class="workspace-tab-btn px-4 py-2.5 border-b-2 ${state.activeWorkspaceTab === 'what_did_we_do' ? 'border-sky-500 text-sky-400 bg-sky-500/10' : 'border-transparent text-slate-400 hover:text-slate-200'} transition flex items-center gap-1.5">
          <span>3.</span><span>WHAT DID WE DO?</span>
        </button>
        <button onclick="setWorkspaceTab('did_it_work')" data-tab="did_it_work" class="workspace-tab-btn px-4 py-2.5 border-b-2 ${state.activeWorkspaceTab === 'did_it_work' ? 'border-sky-500 text-sky-400 bg-sky-500/10' : 'border-transparent text-slate-400 hover:text-slate-200'} transition flex items-center gap-1.5">
          <span>4.</span><span>DID IT WORK?</span>
        </button>
        <button onclick="setWorkspaceTab('timeline')" data-tab="timeline" class="workspace-tab-btn px-4 py-2.5 border-b-2 ${state.activeWorkspaceTab === 'timeline' ? 'border-sky-500 text-sky-400 bg-sky-500/10' : 'border-transparent text-slate-400 hover:text-slate-200'} transition flex items-center gap-1.5">
          <span>5.</span><span>CASE TIMELINE</span>
        </button>
      </div>

      <!-- Sub-Tab Content Container -->
      <div id="workspace-subtab-container"></div>
    </div>
  `;

  renderWorkspaceSubTabs();
}

function renderWorkspaceSubTabs() {
  const container = document.getElementById('workspace-subtab-container');
  if (!container) return;

  switch (state.activeWorkspaceTab) {
    case 'what_changed':
      renderSubTabWhatChanged(container);
      break;
    case 'evidence':
      renderSubTabEvidence(container);
      break;
    case 'what_did_we_do':
      renderSubTabWhatDidWeDo(container);
      break;
    case 'did_it_work':
      renderSubTabDidItWork(container);
      break;
    case 'timeline':
      renderSubTabTimeline(container);
      break;
  }
}

// --- TAB 1: WHAT CHANGED? (Screen 03: 4 Tiers) ---
function renderSubTabWhatChanged(container) {
  container.innerHTML = `
    <div class="space-y-6">
      <!-- 4 Tiers Block Architecture -->
      
      <!-- KHỐI 1: Observed Telemetry -->
      <div class="glass-panel p-5 rounded-xl border border-slate-800">
        <div class="text-xs uppercase font-bold text-sky-400 tracking-wider mb-4 flex items-center gap-2">
          <span>📊</span> KHỐI 1 — DỮ LIỆU CẢM BIẾN QUAN SÁT THỰC TẾ (OBSERVED TELEMETRY)
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="p-4 rounded-lg bg-slate-900/80 border border-slate-800">
            <div class="text-xs uppercase text-slate-400 font-semibold">Áp suất van xả tháp sấy (DV_pressure)</div>
            <div class="text-2xl font-black mono text-rose-400 mt-1 flex items-baseline gap-2">
              2.1856 bar <span class="text-xs px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-bold">▲ +23.75σ CRITICAL</span>
            </div>
            <div class="text-xs text-slate-400 mt-2 space-y-1">
              <div>Baseline nạp: <span class="mono text-slate-300">-0.016 ± 0.09 bar</span></div>
              <div class="text-rose-300/90 leading-relaxed font-sans mt-1">
                Hiện tượng: Van xả bị kẹt hở làm khí nén xả tràn ra ngoài buồng sấy trong lúc máy nén mang tải.
              </div>
            </div>
          </div>

          <div class="p-4 rounded-lg bg-slate-900/80 border border-slate-800">
            <div class="text-xs uppercase text-slate-400 font-semibold">Nhiệt độ dầu máy nén (Oil_temp)</div>
            <div class="text-2xl font-black mono text-amber-400 mt-1 flex items-baseline gap-2">
              74.97 °C <span class="text-xs px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold">▲ +5.71σ SEVERE</span>
            </div>
            <div class="text-xs text-slate-400 mt-2 space-y-1">
              <div>Baseline nạp: <span class="mono text-slate-300">54.98 ± 3.5 °C</span></div>
              <div class="text-amber-300/90 leading-relaxed font-sans mt-1">
                Hiện tượng trôi dạt: Máy nén bơm bù quá tải liên tục sinh nhiệt ma sát, nguy cơ sôi loãng dầu bôi trơn.
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- KHỐI 2: Operational Condition -->
      <div class="glass-panel p-5 rounded-xl border border-slate-800">
        <div class="text-xs uppercase font-bold text-amber-400 tracking-wider mb-4 flex items-center gap-2">
          <span>⚙️</span> KHỐI 2 — ĐIỀU KIỆN VẬN HÀNH THIẾT BỊ (OPERATIONAL CONDITION)
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div class="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
            <div class="text-slate-400 uppercase font-semibold">Asset Health</div>
            <div class="text-base font-bold text-rose-400 mt-1">CRITICAL</div>
            <div class="text-slate-400 mt-0.5">Suy thoái nhiệt động học nghiêm trọng</div>
          </div>
          <div class="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
            <div class="text-slate-400 uppercase font-semibold">Operating Regime</div>
            <div class="text-base font-bold text-slate-200 mono mt-1">LOADED</div>
            <div class="text-slate-400 mt-0.5">Dòng điện mô-tơ Motor_current &gt; 0.5A</div>
          </div>
          <div class="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
            <div class="text-slate-400 uppercase font-semibold">Degradation Stability</div>
            <div class="text-base font-bold text-purple-400 mt-1">CONFIRMED</div>
            <div class="text-slate-400 mt-0.5">Bền vững qua 3 chu kỳ nạp tải liên tiếp</div>
          </div>
        </div>
      </div>

      <!-- KHỐI 3: Business Context -->
      <div class="glass-panel p-5 rounded-xl border border-slate-800">
        <div class="text-xs uppercase font-bold text-purple-400 tracking-wider mb-4 flex items-center gap-2">
          <span>🚆</span> KHỐI 3 — BỐI CẢNH VẬN TẢI HẠM ĐỘI (BUSINESS CONTEXT)
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div class="space-y-2 p-3 bg-slate-900/60 rounded-lg border border-slate-800">
            <div><span class="text-slate-400">Service Unit:</span> <span class="font-bold text-slate-200">TRAIN-302</span> (Linha Azul Passenger Transit)</div>
            <div><span class="text-slate-400">Subsystem:</span> <span class="text-slate-200">Air Production Unit (APU)</span></div>
            <div><span class="text-slate-400">Operational Risk:</span> <span class="text-rose-300 font-semibold">Nguy cơ sập áp suất bình khí nén chính H1 → Dừng tàu khẩn cấp giữa đường hầm.</span></div>
          </div>
          <div class="space-y-2 p-3 bg-slate-900/60 rounded-lg border border-slate-800">
            <div><span class="text-slate-400">Conventional Alert (LPS=1):</span> <span class="mono text-slate-200">2020-06-06 19:42:19 UTC</span></div>
            <div><span class="text-slate-400">Confirmed Window:</span> <span class="font-bold text-sky-400 text-sm mono">33 GIỜ 52 PHÚT</span></div>
            <div class="text-slate-400 leading-relaxed">Cửa sổ thời gian quý giá để điều độ chủ động rút tàu về xưởng sửa chữa mà không gián đoạn lịch trình thương mại.</div>
          </div>
        </div>
      </div>

      <!-- KHỐI 4: Validation Reference -->
      <div class="glass-panel p-5 rounded-xl border border-slate-800">
        <div class="flex items-center justify-between mb-3">
          <div class="text-xs uppercase font-bold text-emerald-400 tracking-wider flex items-center gap-2">
            <span>🔬</span> KHỐI 4 — THAM CHIẾU KIỂM CHỨNG LỊCH SỬ (VALIDATION REFERENCE)
          </div>
          <button onclick="toggleDrawer(true)" class="text-xs text-sky-400 hover:text-sky-300 font-semibold flex items-center gap-1">
            <span>Open Drawer</span><span>→</span>
          </button>
        </div>
        <div class="p-3 bg-slate-900/60 rounded-lg border border-slate-800 text-xs text-slate-300 leading-relaxed">
          Đối chứng ăn khớp 100% với báo cáo hư hỏng thực tế <span class="font-bold text-slate-100">Failure #3 (Air Leak / High Stress)</span> của Metro do Porto. Thuật toán hoạt động hoàn toàn online dựa trên sự kiện vật lý, tôn trọng nguyên tắc không rò rỉ Ground Truth.
        </div>
      </div>
    </div>
  `;
}

// --- TAB 2: WHY? EVIDENCE DOSSIER (Screen 04) ---
function renderSubTabEvidence(container) {
  const ev = state.evidence || {};
  const pack = ev.evidence_pack || [];

  container.innerHTML = `
    <div class="space-y-6">
      <div class="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between text-xs">
        <div>
          <div class="font-bold text-slate-200 uppercase tracking-wide">BỘ BẰNG CHỨNG NHIỆT ĐỘNG LỰC HỌC TƯƠNG QUAN KÈM NGUỒN GỐC (EVIDENCE PROVENANCE)</div>
          <div class="text-slate-400 mt-0.5">Mỗi bằng chứng đều mang nguồn gốc (Source), phương pháp (Method), thời gian (Time) và chế độ (Regime).</div>
        </div>
        <div class="mono px-2.5 py-1 rounded bg-slate-800 text-sky-300 border border-slate-700">
          Evaluated in LOADED Regime (>0.5A)
        </div>
      </div>

      <!-- 4 Evidence Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Card 1: Pressure Anomaly -->
        <div class="glass-card p-5 rounded-xl border border-slate-800 space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold uppercase text-slate-400">THẺ A: ÁP SUẤT KHÍ XẢ (DV_PRESSURE)</span>
            <span class="text-xs px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-bold border border-rose-500/30">CRITICAL</span>
          </div>
          <div class="text-2xl font-black mono text-rose-400">
            2.1856 bar <span class="text-xs font-bold text-rose-300">▲ +23.75σ</span>
          </div>
          <div class="text-xs text-slate-400 space-y-1">
            <div>Baseline nạp danh định: <span class="mono text-slate-300">-0.016 ± 0.09 bar</span></div>
          </div>
          <div class="pt-3 border-t border-slate-800 text-[11px] mono text-slate-400 space-y-0.5">
            <div>SOURCE: <span class="text-slate-300">PressureAnomalyDetector</span></div>
            <div>METHOD: <span class="text-slate-300">Loaded-regime baseline deviation</span></div>
            <div>TIME:   <span class="text-slate-300">2020-06-05 09:50:39 UTC</span></div>
            <div>REGIME: <span class="text-slate-300">LOADED</span></div>
          </div>
        </div>

        <!-- Card 2: Thermal Stress -->
        <div class="glass-card p-5 rounded-xl border border-slate-800 space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold uppercase text-slate-400">THẺ B: NHIỆT ĐỘ DẦU MÁY (OIL_TEMP)</span>
            <span class="text-xs px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold border border-amber-500/30">SEVERE</span>
          </div>
          <div class="text-2xl font-black mono text-amber-400">
            74.97 °C <span class="text-xs font-bold text-amber-300">▲ +5.71σ</span>
          </div>
          <div class="text-xs text-slate-400 space-y-1">
            <div>Baseline nạp danh định: <span class="mono text-slate-300">54.98 ± 3.5 °C</span></div>
          </div>
          <div class="pt-3 border-t border-slate-800 text-[11px] mono text-slate-400 space-y-0.5">
            <div>SOURCE: <span class="text-slate-300">ThermalDriftDetector</span></div>
            <div>METHOD: <span class="text-slate-300">Cumulative thermal stress drift</span></div>
            <div>TIME:   <span class="text-slate-300">2020-06-05 09:50:39 UTC</span></div>
            <div>REGIME: <span class="text-slate-300">LOADED</span></div>
          </div>
        </div>

        <!-- Card 3: Temporal Step Persistence -->
        <div class="glass-card p-5 rounded-xl border border-slate-800 space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold uppercase text-slate-400">THẺ C: BƯỚC NHẢY BỀN VỮNG (PERSISTENCE)</span>
            <span class="text-xs px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 font-bold border border-purple-500/30">CONFIRMED</span>
          </div>
          <div class="text-2xl font-black mono text-purple-400">
            3 / 3 Chu Kỳ <span class="text-xs font-bold text-purple-300">PERSISTENT</span>
          </div>
          <div class="text-xs text-slate-400 space-y-1">
            <div>Delta ngưỡng bước nhảy: <span class="mono text-slate-300">&gt; 0.50 bar</span></div>
          </div>
          <div class="pt-3 border-t border-slate-800 text-[11px] mono text-slate-400 space-y-0.5">
            <div>SOURCE: <span class="text-slate-300">TemporalStepDetector</span></div>
            <div>METHOD: <span class="text-slate-300">Consecutive loaded cycle persistence</span></div>
            <div>TIME:   <span class="text-slate-300">2020-06-05 09:50:39 UTC</span></div>
            <div>REGIME: <span class="text-slate-300">LOADED</span></div>
          </div>
        </div>

        <!-- Card 4: Multivariate Isolation Forest Corroboration -->
        <div class="glass-card p-5 rounded-xl border border-slate-800 space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold uppercase text-slate-400">THẺ D: KIỂM CHỨNG ĐA BIẾN ML (ISOLATION FOREST)</span>
            <span class="text-xs px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 font-bold border border-sky-500/30">CORROBORATED</span>
          </div>
          <div class="text-2xl font-black mono text-sky-400">
            0.382 <span class="text-xs font-bold text-sky-300">▲ &gt; NGƯỠNG 0.350</span>
          </div>
          <div class="text-xs text-slate-400 space-y-1">
            <div>5 Loaded Features: <span class="mono text-slate-300">DV, H1, Oil_temp, Motor_current, TP3</span></div>
          </div>
          <div class="pt-3 border-t border-slate-800 text-[11px] mono text-slate-400 space-y-0.5">
            <div>SOURCE: <span class="text-slate-300">IsolationForestDetector</span></div>
            <div>ROLE:   <span class="text-sky-300 font-semibold">Độc lập kiểm chứng (Không tự tạo Case)</span></div>
            <div>TIME:   <span class="text-slate-300">2020-06-05 09:50:39 UTC</span></div>
            <div>REGIME: <span class="text-slate-300">LOADED</span></div>
          </div>
        </div>
      </div>

      <!-- Thermodynamic Causal Chain -->
      <div class="glass-panel p-5 rounded-xl border border-slate-800">
        <div class="text-xs uppercase font-bold text-slate-300 mb-4 tracking-wider">
          CHUỖI NHÂN QUẢ NHIỆT ĐỘNG LỰC HỌC (THERMODYNAMIC CAUSAL CHAIN)
        </div>
        <div class="grid grid-cols-1 md:grid-cols-5 gap-3 text-xs">
          <div class="p-3 bg-slate-900/80 rounded-lg border border-slate-800 text-center">
            <div class="text-slate-400 mb-1">1. Gốc Rễ</div>
            <div class="font-bold text-rose-400">Van xả tháp sấy hở</div>
            <div class="text-[10px] text-slate-500 mt-1">Desiccant drain stuck</div>
          </div>
          <div class="p-3 bg-slate-900/80 rounded-lg border border-slate-800 text-center">
            <div class="text-slate-400 mb-1">2. Áp Suất</div>
            <div class="font-bold text-rose-400">DV nhảy vọt 2.18 bar</div>
            <div class="text-[10px] text-slate-500 mt-1">Pressure breach +23.75σ</div>
          </div>
          <div class="p-3 bg-slate-900/80 rounded-lg border border-slate-800 text-center">
            <div class="text-slate-400 mb-1">3. Tải Cơ Học</div>
            <div class="font-bold text-amber-400">Máy nén bơm bù quá tải</div>
            <div class="text-[10px] text-slate-500 mt-1">Extended loaded cycle</div>
          </div>
          <div class="p-3 bg-slate-900/80 rounded-lg border border-slate-800 text-center">
            <div class="text-slate-400 mb-1">4. Nhiệt Năng</div>
            <div class="font-bold text-amber-400">Dầu nóng vọt 74.97°C</div>
            <div class="text-[10px] text-slate-500 mt-1">Thermal friction +5.71σ</div>
          </div>
          <div class="p-3 bg-slate-900/80 rounded-lg border border-rose-900/50 text-center bg-rose-950/20">
            <div class="text-rose-400 mb-1">5. Nguy Cơ</div>
            <div class="font-bold text-rose-300">Bó kẹt & Sập áp phanh</div>
            <div class="text-[10px] text-rose-400 mt-1">In 33h 52m if unaddressed</div>
          </div>
        </div>
      </div>
    </div>
  `;
}

// --- TAB 3: WHAT DID WE DO? (Screen 05) ---
function renderSubTabWhatDidWeDo(container) {
  const activeCase = state.activeCase || {};
  const phase = activeCase.phase || 'INVESTIGATING';
  const isMitigating = phase === 'MITIGATING' || phase === 'VERIFYING_RECOVERY' || phase === 'RESOLVED' || phase === 'CLOSED';

  container.innerHTML = `
    <div class="space-y-6">
      <div class="glass-panel p-5 rounded-xl border border-slate-800">
        <div class="text-xs uppercase font-bold text-sky-400 tracking-wider mb-2">
          QUY TRÌNH CAN THIỆP MÔ PHỎNG AN TOÀN (SOP-APU-ISO-04)
        </div>
        <p class="text-xs text-slate-300 leading-relaxed">
          Kích hoạt can thiệp an toàn (Safe Mode Simulated Intervention): Mô phỏng quy trình cách ly cụm van tháp sấy số 2 và rẽ nhánh luồng dữ liệu sang phân đoạn viễn thám thực tế sau bảo trì ngày 08/06/2020.
        </p>
      </div>

      <!-- ActionGuard 5 Safety Checks -->
      <div class="glass-panel p-5 rounded-xl border border-slate-800 space-y-4">
        <div class="text-xs uppercase font-bold text-slate-200 tracking-wider flex items-center gap-2">
          <span>🛡️</span> HÀNG RÀO KIỂM ĐỊNH CHÍNH SÁCH CAN THIỆP (ACTIONGUARD 5 PRE-FLIGHT CHECKS)
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div class="p-3 bg-slate-900/80 rounded-lg border border-slate-800 flex items-center justify-between">
            <div class="space-y-0.5">
              <div class="font-semibold text-slate-200">1. Case Confirmed</div>
              <div class="text-slate-400">Trạng thái phải là DETECTED hoặc INVESTIGATING</div>
            </div>
            <span class="text-emerald-400 font-bold mono">✓ PASS</span>
          </div>

          <div class="p-3 bg-slate-900/80 rounded-lg border border-slate-800 flex items-center justify-between">
            <div class="space-y-0.5">
              <div class="font-semibold text-slate-200">2. Mitigation Recommended</div>
              <div class="text-slate-400">DecisionEngine xác nhận đa cảm biến + ML</div>
            </div>
            <span class="text-emerald-400 font-bold mono">✓ PASS</span>
          </div>

          <div class="p-3 bg-slate-900/80 rounded-lg border border-slate-800 flex items-center justify-between">
            <div class="space-y-0.5">
              <div class="font-semibold text-slate-200">3. No Conflicting Active Case</div>
              <div class="text-slate-400">Tối đa một active case trên APU-COMP-01</div>
            </div>
            <span class="text-emerald-400 font-bold mono">✓ PASS</span>
          </div>

          <div class="p-3 bg-slate-900/80 rounded-lg border border-slate-800 flex items-center justify-between">
            <div class="space-y-0.5">
              <div class="font-semibold text-slate-200">4. Simulation Mode Only</div>
              <div class="text-slate-400">Môi trường kiểm thử có kiểm toán an toàn</div>
            </div>
            <span class="text-emerald-400 font-bold mono">✓ PASS</span>
          </div>

          <div class="p-3 bg-slate-900/80 rounded-lg border border-slate-800 flex items-center justify-between md:col-span-2">
            <div class="space-y-0.5">
              <div class="font-semibold text-slate-200">5. Replay Branch Available</div>
              <div class="text-slate-400">Phân đoạn dữ liệu sau bảo trì (2020-06-08 16:05:00 UTC) sẵn sàng</div>
            </div>
            <span class="text-emerald-400 font-bold mono">✓ PASS</span>
          </div>
        </div>
      </div>

      <!-- Safe Mode Action Execution Card -->
      <div class="glass-panel p-6 rounded-xl border ${isMitigating ? 'border-purple-500/40 bg-purple-950/10' : 'border-sky-500/40 bg-sky-950/10'} space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div class="text-xs uppercase font-bold ${isMitigating ? 'text-purple-300' : 'text-sky-300'}">
              ${isMitigating ? 'CAN THIỆP ĐÃ ĐƯỢC KÍCH HOẠT THÀNH CÔNG' : 'SẴN SÀNG KÍCH HOẠT CAN THIỆP MÔ PHỎNG'}
            </div>
            <div class="text-xs text-slate-300 mt-1">
              ${isMitigating ? 'Luồng viễn thám đã rẽ nhánh sang METROPT-3_POST_MAINTENANCE (08/06/2020 16:05:00 UTC).' : 'Bấm nút dưới đây để kích hoạt Safe Mode và rẽ nhánh luồng dữ liệu sang sau bảo trì.'}
            </div>
          </div>

          <div>
            <button id="btn-safe-mode" onclick="onTriggerSafeMode()" ${isMitigating ? 'disabled' : ''} class="px-6 py-3 rounded-lg ${isMitigating ? 'bg-purple-800/40 text-purple-300 cursor-not-allowed border border-purple-700/50' : 'bg-sky-600 hover:bg-sky-500 text-white font-bold shadow-lg shadow-sky-900/50'} text-xs transition flex items-center gap-2">
              <span>⚡</span><span>${isMitigating ? 'SAFE MODE ACTIVE (BRANCHED)' : 'ACTIVATE SAFE MODE (SIMULATED INTERVENTION)'}</span>
            </button>
          </div>
        </div>

        <div class="pt-3 border-t border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
          <div>Dispatcher Authorization: <span class="mono text-slate-300 font-semibold">DISPATCHER-0941</span></div>
          <div>Audit Trail: <span class="mono text-emerald-400">Logged to MongoDB case_events ledger</span></div>
        </div>
      </div>
    </div>
  `;
}

// --- TAB 4: DID IT WORK? (Screen 06: Recovery Verifier) ---
function renderSubTabDidItWork(container) {
  const rec = state.recovery || { consecutive_healthy_observations: 0, target_healthy_observations: 5, is_verified: false };
  const currentCount = rec.consecutive_healthy_observations || 0;
  const isVerified = rec.is_verified || currentCount >= 5;
  const activeCase = state.activeCase || {};
  const isClosed = activeCase.phase === 'CLOSED';

  // Construct 5 progress steps
  let stepsHtml = '';
  for (let i = 1; i <= 5; i++) {
    const passed = i <= currentCount;
    stepsHtml += `
      <div class="flex-1 text-center p-3 rounded-lg border ${passed ? 'bg-emerald-950/40 border-emerald-500/60 text-emerald-300' : 'bg-slate-900/60 border-slate-800 text-slate-500'}">
        <div class="text-xs font-bold mono">MẪU ${i}</div>
        <div class="text-sm mt-1">${passed ? '✓ ĐẠT' : '⏳ CHỜ'}</div>
      </div>
    `;
  }

  container.innerHTML = `
    <div class="space-y-6">
      <div class="glass-panel p-5 rounded-xl border border-slate-800">
        <div class="text-xs uppercase font-bold text-emerald-400 tracking-wider mb-2">
          TIẾN TRÌNH KIỂM CHỨNG TIÊU CHÍ PHỤC HỒI (RECOVERY CRITERIA VERIFIED)
        </div>
        <p class="text-xs text-slate-300 leading-relaxed">
          Tiêu chuẩn nghiệm thu: Đạt đủ <span class="font-bold text-slate-100">5 Quan sát lành mạnh liên tiếp</span> trong chế độ mang tải <span class="mono font-bold text-slate-100">LOADED</span>. Nếu vi phạm bất kỳ mẫu nào trước khi đủ 5, bộ đếm lập tức reset về 0/5 để đảm bảo an toàn tuyệt đối.
        </p>
      </div>

      <!-- 5 Steps Progress Indicator -->
      <div class="glass-panel p-5 rounded-xl border border-slate-800 space-y-4">
        <div class="flex items-center justify-between text-xs">
          <div class="font-bold text-slate-200">THANH TIẾN ĐỘ 5 QUAN SÁT MANG TẢI (LOADED):</div>
          <div class="font-bold mono ${isVerified ? 'text-emerald-400' : 'text-amber-400'}">
            ${currentCount} / 5 QUAN SÁT ${isVerified ? '(ĐẠT TIÊU CHUẨN ✓)' : ''}
          </div>
        </div>

        <div class="flex items-center gap-2">
          ${stepsHtml}
        </div>
      </div>

      <!-- Criteria Verification Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
          <div class="text-xs uppercase font-semibold text-slate-400">1. Áp suất xả tháp sấy (DV_pressure)</div>
          <div class="text-2xl font-black mono ${isVerified ? 'text-emerald-400' : 'text-slate-200'}">
            -0.016 bar <span class="text-xs font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">🟢 THỎA MÃN</span>
          </div>
          <div class="text-xs text-slate-400">Ngưỡng trần tối đa cho phép: <span class="mono text-slate-300">&lt; 0.050 bar</span></div>
          <div class="text-xs text-slate-300 pt-2 border-t border-slate-800/80">
            Đánh giá: Áp suất buồng xả duy trì ở mức chân không bình thường lúc mang tải.
          </div>
        </div>

        <div class="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
          <div class="text-xs uppercase font-semibold text-slate-400">2. Nhiệt độ dầu máy nén (Oil_temp)</div>
          <div class="text-2xl font-black mono ${isVerified ? 'text-emerald-400' : 'text-slate-200'}">
            64.12 °C <span class="text-xs font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">🟢 THỎA MÃN</span>
          </div>
          <div class="text-xs text-slate-400">Ngưỡng trần tối đa cho phép: <span class="mono text-slate-300">&lt; 67.0 °C</span></div>
          <div class="text-xs text-slate-300 pt-2 border-t border-slate-800/80">
            Đánh giá: Nhiệt độ dầu hạ nhiệt ổn định, không còn nguy cơ thoái hóa chất bôi trơn.
          </div>
        </div>
      </div>

      <!-- Close Case Sign-off Action -->
      <div class="glass-panel p-6 rounded-xl border ${isVerified ? 'border-emerald-500/40 bg-emerald-950/10' : 'border-slate-800'} space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div class="text-xs uppercase font-bold ${isVerified ? 'text-emerald-300' : 'text-slate-400'}">
              ${isClosed ? 'HỒ SƠ SỰ CỐ ĐÃ ĐƯỢC NGHIỆM THU ĐÓNG (CLOSED)' : (isVerified ? '🏆 RECOVERY CRITERIA VERIFIED — SẴN SÀNG NGHIỆM THU ĐÓNG CASE' : 'CHỜ THỎA MÃN ĐỦ 5 QUAN SÁT MANG TẢI TRƯỚC KHI ĐÓNG')}
            </div>
            <div class="text-xs text-slate-300 mt-1">
              ${isClosed ? 'Tài sản APU-COMP-01 đã được giải phóng trở về trạng thái HEALTHY trên Operations Landing.' : 'Hành động ký duyệt đóng Case giải phóng đoàn tàu Train #302 trở lại phục vụ chở khách thương mại.'}
            </div>
          </div>

          <div>
            <button id="btn-close-case" onclick="onCloseCase()" ${!isVerified || isClosed ? 'disabled' : ''} class="px-6 py-3 rounded-lg ${isVerified && !isClosed ? 'bg-emerald-600 hover:bg-emerald-500 text-white font-bold shadow-lg shadow-emerald-900/50' : 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'} text-xs transition flex items-center gap-2">
              <span>🔒</span><span>${isClosed ? 'CASE CLOSED ✓' : 'CLOSE CASE & RELEASE ASSET TO SERVICE'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
}

// --- TAB 5: CASE TIMELINE (Screen 07: Datadog-style Incident Timeline) ---
function renderSubTabTimeline(container) {
  const events = state.timeline || [];

  let timelineItemsHtml = '';
  if (events.length === 0) {
    timelineItemsHtml = `
      <div class="p-6 text-center text-xs text-slate-500">
        No case events recorded yet in append-only ledger.
      </div>
    `;
  } else {
    events.forEach((evt, idx) => {
      const typeColor = {
        DETECTION: 'bg-rose-500 text-slate-950',
        CORROBORATION: 'bg-sky-500 text-slate-950',
        DECISION: 'bg-amber-500 text-slate-950',
        ACTION: 'bg-purple-500 text-slate-950',
        RECOVERY: 'bg-emerald-500 text-slate-950',
        CASE_CLOSED: 'bg-emerald-400 text-slate-950'
      }[evt.event_type] || 'bg-slate-600 text-slate-100';

      timelineItemsHtml += `
        <div class="relative pl-8 pb-6 group">
          <!-- Timeline line -->
          ${idx < events.length - 1 ? '<div class="absolute left-3 top-3 -bottom-3 w-0.5 bg-slate-800"></div>' : ''}
          
          <!-- Timeline node dot -->
          <div class="absolute left-1.5 top-1.5 w-3.5 h-3.5 rounded-full border-2 border-slate-950 ${typeColor.split(' ')[0]}"></div>

          <!-- Content Card -->
          <div class="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1.5">
            <div class="flex flex-wrap items-center justify-between gap-2 text-xs">
              <div class="flex items-center gap-2">
                <span class="font-bold mono px-2 py-0.5 rounded text-[10px] ${typeColor}">
                  ${evt.event_type}
                </span>
                <span class="font-bold text-slate-200">${evt.title}</span>
              </div>
              <div class="mono text-slate-400 text-[11px]">
                ${evt.event_time.replace('T', ' ').replace('Z', '')} UTC
              </div>
            </div>

            <div class="text-xs text-slate-300 leading-relaxed font-sans">
              ${evt.detail}
            </div>

            <div class="pt-2 border-t border-slate-800/80 text-[11px] text-slate-400 mono flex items-center gap-4">
              <div>Actor: <span class="text-slate-300">${evt.actor}</span></div>
              <div>Source: <span class="text-slate-300">${evt.source}</span></div>
              <div>Phase: <span class="text-slate-300">${evt.phase}</span></div>
            </div>
          </div>
        </div>
      `;
    });
  }

  container.innerHTML = `
    <div class="space-y-6">
      <div class="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between text-xs">
        <div>
          <div class="font-bold text-slate-200 uppercase tracking-wide">SỔ CÁI SỰ KIỆN VÒNG ĐỜI SỰ CỐ (DATADOG APM INCIDENT TIMELINE)</div>
          <div class="text-slate-400 mt-0.5">Sổ cái append-only lưu vết từ phát hiện sớm, ML kiểm chứng, can thiệp cho tới hồi phục nghiệm thu.</div>
        </div>
        <div class="mono px-2.5 py-1 rounded bg-slate-800 text-sky-300 border border-slate-700">
          Append-Only Event Ledger (${events.length} Events)
        </div>
      </div>

      <div class="pl-2">
        ${timelineItemsHtml}
      </div>
    </div>
  `;
}

// --- App Initialization ---
window.addEventListener('DOMContentLoaded', async () => {
  // Bind Nav buttons
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => setView(btn.dataset.view));
  });

  // Initial data load
  await refreshAllData();

  // Set default view
  setView('operations');

  // Background slow sync (every 5 seconds when paused)
  state.refreshInterval = setInterval(() => {
    if (!state.isSimRunning) {
      refreshAllData();
    }
  }, 5000);
});
