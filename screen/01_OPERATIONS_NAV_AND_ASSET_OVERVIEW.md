# SCREEN 01 — FLEET OPERATIONS & LIVE TELEMETRY MATRIX (v3.0 PRODUCTION-READY)
> **Mục tiêu:** Cung cấp bảng điều khiển vận hành hạm đội mật độ cao (`High-Density Fleet Operations Console`), kết hợp **Bảng Lọc Tài Sản Hạm Đội (`Filterable Fleet Grid`)**, **Biểu Đồ Chuỗi Thời Gian Đa Kênh (`Multi-Channel Synchronized Strip Charts`)**, và **Luồng Sự Kiện Chặn Báo Động Giả Thời Gian Thực (`Real-Time Anomaly & Suppression Stream`)**.
> **Điểm khác biệt v3.0 (Xoá bỏ cảm giác Auto-Pilot):**
> 1. **Gỡ bỏ thanh nút nhảy Milestone khỏi Header chính:** Đưa toàn bộ nút `Play/Pause`, `Speed`, `Scenario Switcher`, `Milestone Bookmarks` vào ngăn kéo thu gọn `🎛️ Replay Studio` ở góc dưới bên phải.
> 2. **100% Data-Driven Telemetry:** Mọi con số trên thẻ KPI, bảng cảm biến và đồ thị đường đều đọc động từ `GET /api/operations` và `GET /api/telemetry/window?limit=60`.

---

## 1. BỐ CỤC GIAO DIỆN (PRODUCTION HIGH-DENSITY WIREFRAME)

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [CG] COMPRESSORGUARD // OPERATIONS COMMAND CONSOLE    [ LIVE SIMULATION · HISTORICAL DATA · 0.1 Hz ]         │
│ Scope: Metro Line 1 Fleet / Train #302 / APU-COMP-01    Event Clock: 2020-06-04 00:33:07 UTC | [🗄️ Valid. Ref] │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ NAV: [★ 1. FLEET & TELEMETRY MATRIX]    [2. INCIDENT QUEUE (0)]    [3. CASE INVESTIGATION WORKBENCH]         │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ KPI STRIP (DYNAMIC BINDING):                                                                                 │
│ ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐ ┌───────────────────────────────┐ │
│ │ MONITORED ASSETS: 1  │ │ ACTIVE CASES: 0      │ │ OBSERVING STATE: 1   │ │ INTERVENTION WINDOW: STANDBY  │ │
│ │ Stream: MetroPT-3    │ │ Single-Case Policy   │ │ Transient Watchlist  │ │ Baseline Benchmark: LPS=1     │ │
│ └──────────────────────┘ └──────────────────────┘ └──────────────────────┘ └───────────────────────────────┘ │
├───────────────────────────────────────────────────┬──────────────────────────────────────────────────────────┤
│ LEFT PANE (5 COLS): FLEET ASSET HIERARCHY & GRID  │ RIGHT PANE (7 COLS): LIVE MULTI-CHANNEL STRIP CHARTS     │
│ ───────────────────────────────────────────────── │ ──────────────────────────────────────────────────────── │
│ [🔍 Search Train / Asset ID...] [Filter: All ▼]   │ Window: [Last 10m (60 pts) ▼]   Regime Shading: [ON ✓]   │
│                                                   │                                                          │
│ ▼ 🏢 FLEET-METRO-01 (Metro Line 1 · Depot Long Bình)  │ 1. DISCHARGE VALVE PRESSURE (DV_pressure_bar)            │
│   └── ▼ 🚆 TRAIN-302 (Series 300 EMU · In-Service)│    2.5 ┤─────────────────── threshold: 2.0 bar ────────  │
│         └── ▼ ⚙️ SUB-APU-01 (Air Production Unit) │    0.0 ┤─────────/\────────────────────────────────────  │
│               └── 🟡 APU-COMP-01 (Knorr LP49)     │                 (00:33:07 Spike: 6.046 bar, 1/3 cycle)   │
│                                                   │                                                          │
│ LIVE ASSET TELEMETRY MATRIX (15-SENSOR SNAPSHOT): │ 2. COMPRESSOR OIL TEMPERATURE (Oil_temp_c)               │
│ ┌────────────────────┬──────────────┬───────────┐ │   74.0 ┤─────────────────── threshold: 74.0 °C ────────  │
│ │ Signal             │ Live Reading │ Status    │ │   56.1 ┤───────────────────────────────────────────────  │
│ ├────────────────────┼──────────────┼───────────┤ │                                                          │
│ │ Operating Regime   │ LOADED       │ > 0.50 A  │ │ 3. MOTOR CURRENT & OPERATING REGIME (Motor_current_a)    │
│ │ DV_pressure        │ 6.0460 bar   │ ▲ +65.4σ  │ │    7.0 ┤   ████████████        ████████████ (LOADED)     │
│ │ Oil_temp           │ 56.10 °C     │ +0.32σ OK │ │    0.0 ┤───┘          └────────┘          └────────────  │
│ │ Motor_current      │ 6.82 A       │ LOADED    │ │                                                          │
│ │ H1_pressure        │ -0.012 bar   │ NOMINAL   │ │ 4. MULTIVARIATE ISOLATION FOREST (5-Feature Score)       │
│ │ TP2 / TP3          │ 8.91 / 8.74  │ NOMINAL   │ │   0.35 ┤─────────────────── corroboration: 0.35 ───────  │
│ │ LPS Switch         │ 0 (INACTIVE) │ OK        │ │   0.18 ┤───────────────────────────────────────────────  │
│ └────────────────────┴──────────────┴───────────┘ │                                                          │
│ [🔎 Inspect Telemetry]  [🛠️ Open Asset Workbench] │                                                          │
├───────────────────────────────────────────────────┴──────────────────────────────────────────────────────────┤
│ BOTTOM PANE: REAL-TIME ANOMALY & ANTI-FATIGUE SUPPRESSION STREAM (DYNAMIC EVENT LOG)                         │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│ Time (UTC)          │ Asset       │ Signal & Reading         │ Persistence │ Thermal │ Engine Decision       │
│ 2020-06-04 00:33:07 │ APU-COMP-01 │ DV_pressure: 6.046 bar   │ 1/3 Cycles  │ 56.1°C  │ [SUPPRESSED: NO CASE] │
│                     │             │ (+65.4σ transient spike) │ (Insuff.)   │ (+0.3σ) │ Marked DEGRADING only │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                                    ┌──────────────────────────────────────────┐
                                                                    │ 🎛️ Replay Studio (Failure #3 · 60x) [▲] │
                                                                    └──────────────────────────────────────────┘
```

---

## 2. CƠ CHẾ VẬN HÀNH THỰC TẾ (KHÔNG CÒN AUTO-PILOT)

### 2.1. Ngăn Kéo Điều Khiển Mô Phỏng Độc Lập (`🎛️ Replay Studio Drawer`)
- Trên một sản phẩm Production thực tế, thanh Header không bao giờ chứa các nút "Nhảy tới 00:33 / Nhảy tới 09:50".
- Toàn bộ chức năng điều khiển phát lại (`Play/Pause`, `Step +10s`, `Speed 1x/10x/60x/300x`), chuyển đổi kịch bản (`Failure #3`, `Failure #1`, `Failure #4`, `Healthy Baseline`), và các nút nhảy nhanh (`Diagnostic Bookmarks`) được gom vào một **Floating Drawer nhỏ gọn ở góc dưới bên phải**.
- Khi đóng ngăn kéo này lại, chuyên viên điều độ làm việc trên một giao diện giám sát công nghiệp thuần khiết 100%.

### 2.2. Biểu Đồ Chuỗi Thời Gian Đa Kênh & Ma Trận 15 Cảm Biến Sống
- Thay vì chỉ hiển thị vài thẻ chữ tĩnh, khung bên phải vẽ trực tiếp **4 đồ thị chuỗi thời gian đồng bộ trục ngang (Synchronized Time-Series Strip Charts)** từ API `GET /api/telemetry/window?limit=60`:
  1. `DV_pressure (bar)` kèm đường ngưỡng `2.0 bar` và dải chuẩn `LOADED (-0.016 ± 0.09 bar)`.
  2. `Oil_temp (°C)` kèm đường ngưỡng `74.0 °C` và dải chuẩn `54.98 ± 3.5 °C`.
  3. `Motor_current (A)` kèm vùng tô màu nền tự động phân biệt chu kỳ có tải (`LOADED > 0.5A`) và không tải (`UNLOADED`).
  4. `Isolation Forest Score` trên 5 đặc trưng mang tải so với ngưỡng kiểm chứng `0.35`.

### 2.3. Bảng Sự Kiện Chặn Báo Động Ảo Động (`Real-Time Suppression Stream`)
- Thay vì in cứng một đoạn văn giải thích mốc `00:33:07` lên giao diện mọi lúc, bảng **Real-Time Anomaly & Anti-Fatigue Suppression Stream** ở dưới cùng lắng nghe trực tiếp kết quả từ `DecisionEngine` và `CaseEvent` ledger:
  - Khi luồng dữ liệu đi qua thời điểm `2020-06-04 00:33:07 UTC` (hoặc bất kỳ xung áp suất thoáng qua nào có `persistence < 3`), một dòng log mới tự động đẩy vào bảng với nhãn `[SUPPRESSED: NO CASE CREATED]` kèm lý do định lượng (`Persistence: 1/3 Loaded Cycles`, `Thermal: Normal`).
  - Loại bỏ hoàn toàn các chỉ số phần trăm sức khỏe giả mạo hoặc nhãn trạng thái giả, thay bằng các bộ đếm vận hành trung thực và nhãn `[ LIVE SIMULATION · HISTORICAL DATA ]`.

---

## 3. RÀNG BUỘC DỮ LIỆU ĐỘNG (`GET /api/operations` & `GET /api/telemetry/window`)

```json
{
  "operations": {
    "fleet": {
      "fleet_id": "FLEET-METRO-01",
      "name": "RailOps VN — Metro Line 1 (Bến Thành – Suối Tiên)",
      "depot_location": "Depot Oriente"
    },
    "train": {
      "train_id": "TRAIN-302",
      "model": "Series 300 EMU",
      "service_status": "REVENUE_SERVICE"
    },
    "subsystem": {
      "subsystem_id": "SUB-APU-01",
      "name": "Air Production Unit"
    },
    "asset": {
      "asset_id": "APU-COMP-01",
      "name": "Air Compressor Unit #01",
      "criticality": "CRITICAL"
    },
    "operations_summary": {
      "monitored_assets_count": 1,
      "active_cases_count": 0,
      "assets_observing_count": 1,
      "scenario_name": "Failure #3 - Air Leak",
      "simulation_mode": "LIVE_SIMULATION",
      "confirmed_intervention_window": null
    },
    "active_case": null
  },
  "telemetry_window": {
    "asset_id": "APU-COMP-01",
    "current_event_time": "2020-06-04T00:33:07Z",
    "latest_point": {
      "timestamp": "2020-06-04T00:33:07Z",
      "regime": "LOADED",
      "dv_pressure_bar": 6.046,
      "oil_temp_c": 56.10,
      "motor_current_a": 6.82,
      "h1_bar": -0.012,
      "tp2_bar": 8.91,
      "tp3_bar": 8.74,
      "lps_active": 0.0
    }
  }
}
```
