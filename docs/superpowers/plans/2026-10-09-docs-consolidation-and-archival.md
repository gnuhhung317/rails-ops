# Docs Consolidation and Archival Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tổ chức và chuẩn hóa hệ thống tài liệu trong `iot-hackathon`: bảo tồn `master_context.md` làm Single Source of Truth (SSOT), giữ `docs/PRODUCT_UX_SPEC.md` cho Phase 4 UI, và chuyển toàn bộ các bản nháp, research spikes, specs v1 và session logs cũ vào `docs/archive/` bằng `git mv` để giữ trọn vẹn git history.

**Architecture:** Phân tầng cấu trúc tài liệu thành 3 cấp độ: Active Root & SSOT (`master_context.md`, `README.md`), Active Domain Specs (`docs/PRODUCT_UX_SPEC.md`, `docs/superpowers/plans/`), và Historical Archive (`docs/archive/{research,specs-v1,session-logs}`).

**Tech Stack:** Git, Markdown, PowerShell.

---

### Task 1: Create Archive Directory Structure

**Files:**
- Create: `docs/archive/research/`
- Create: `docs/archive/specs-v1/`
- Create: `docs/archive/session-logs/`

- [ ] **Step 1: Tạo các thư mục lưu trữ**

Run: `mkdir -p docs/archive/research docs/archive/specs-v1 docs/archive/session-logs`

- [ ] **Step 2: Xác nhận các thư mục đã sẵn sàng**

---

### Task 2: Move Historical Documents with Git History

**Files:**
- Move: `master-spec.md` -> `docs/archive/research/master-spec.md`
- Move: `data-feasibility.md` -> `docs/archive/research/data-feasibility.md`
- Move: `how-to-win.md` -> `docs/archive/research/how-to-win.md`
- Move: `compressorguard_plan.md` -> `docs/archive/research/compressorguard_plan.md`
- Move: `docs/architecture.md` -> `docs/archive/specs-v1/architecture.md`
- Move: `docs/detection.md` -> `docs/archive/specs-v1/detection.md`
- Move: `docs/evidence-model.md` -> `docs/archive/specs-v1/evidence-model.md`
- Move: `docs/product.md` -> `docs/archive/specs-v1/product.md`
- Move: `docs/demo-scenario.md` -> `docs/archive/specs-v1/demo-scenario.md`
- Move: `docs/decision-matrix.md` -> `docs/archive/specs-v1/decision-matrix.md`
- Move: `docs/validation.md` -> `docs/archive/specs-v1/validation.md`
- Move: `docs/product-thesis-and-golden-experience.md` -> `docs/archive/specs-v1/product-thesis-and-golden-experience.md`
- Move: `task_plan.md` -> `docs/archive/session-logs/task_plan.md`
- Move: `findings.md` -> `docs/archive/session-logs/findings.md`
- Move: `progress.md` -> `docs/archive/session-logs/progress.md`
- Move: `report.md` -> `docs/archive/session-logs/report.md`

- [ ] **Step 1: Thực hiện di chuyển bằng `git mv`**
- [ ] **Step 2: Kiểm tra `git status` đảm bảo tất cả file chuyển dạng rename**

---

### Task 3: Create Archive README and Update Root Navigation

**Files:**
- Create: `docs/archive/README.md`
- Create/Update: `README.md`

- [ ] **Step 1: Tạo `docs/archive/README.md` chỉ mục và giải thích lý do archive**
- [ ] **Step 2: Tạo `README.md` ở root dẫn đường tới `master_context.md` và `docs/PRODUCT_UX_SPEC.md`**

---

### Task 4: Verify System Integrity

**Files:**
- Verify: `tests/test_api_vertical_slice.py`
- Verify: `tests/test_deterministic_replay.py`

- [ ] **Step 1: Chạy test suite để đảm bảo không có file nào bị lỗi import hoặc gãy phụ thuộc**
- [ ] **Step 2: Commit gọn gàng**
