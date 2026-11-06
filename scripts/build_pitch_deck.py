"""RailOps VN — final-round pitch deck generator (12 slides, 16:9, dark enterprise theme).

Reproducible by design: edit the SLIDES table below and re-run to regenerate
docs/railops-vn-final-deck.pptx. Content is drawn from
docs/RAILOPS_VN_PLATFORM_BLUEPRINT.md and docs/PITCH_DECK_AND_DEMO_RUNBOOK.md.

    python scripts/build_pitch_deck.py
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

OUT = Path(__file__).resolve().parent.parent / "docs" / "railops-vn-final-deck.pptx"

W, H = Inches(13.333), Inches(7.5)

BG        = RGBColor(0x08, 0x0C, 0x12)
PANEL     = RGBColor(0x14, 0x20, 0x2E)
PANEL_ALT = RGBColor(0x0E, 0x17, 0x22)
INK       = RGBColor(0xE8, 0xEE, 0xF5)
MUTED     = RGBColor(0x9D, 0xAF, 0xC2)
TEAL      = RGBColor(0x4F, 0xD1, 0xC5)
AMBER     = RGBColor(0xF6, 0xC1, 0x5E)
RED       = RGBColor(0xF8, 0x71, 0x71)
FONT      = "Segoe UI"
MONO      = "Consolas"

MARGIN = Inches(0.7)
BODY_W = W - MARGIN * 2


def _box(slide, left, top, width, height):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return tf


def _fill(slide, color):
    shape = slide.shapes.add_shape(1, Emu(0), Emu(0), W, H)  # 1 = rectangle
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    shape.shadow.inherit = False
    slide.shapes._spTree.remove(shape._element)
    slide.shapes._spTree.insert(2, shape._element)
    return shape


def para(tf, text, size, color=MUTED, bold=False, font=FONT, space_after=6,
         space_before=0, first=False, align=PP_ALIGN.LEFT):
    p = tf.paragraphs[0] if first and not tf.paragraphs[0].runs else tf.add_paragraph()
    p.text = text
    p.alignment = align
    p.space_after = Pt(space_after)
    p.space_before = Pt(space_before)
    for run in p.runs:
        run.font.size = Pt(size)
        run.font.color.rgb = color
        run.font.bold = bold
        run.font.name = font
    return p


def header(slide, kicker, title):
    bar = slide.shapes.add_shape(1, MARGIN, Inches(0.55), Inches(0.09), Inches(0.62))
    bar.fill.solid(); bar.fill.fore_color.rgb = TEAL; bar.line.fill.background()
    tf = _box(slide, MARGIN + Inches(0.28), Inches(0.42), BODY_W - Inches(0.28), Inches(1.1))
    para(tf, kicker.upper(), 11.5, TEAL, bold=True, space_after=3, first=True)
    para(tf, title, 27, INK, bold=True, space_after=0)


def bullets(slide, items, top=Inches(1.75), width=None, size=14.5):
    tf = _box(slide, MARGIN, top, width or BODY_W, H - top - Inches(0.5))
    first = True
    for kind, text in items:
        if kind == "h":
            para(tf, text, 15.5, AMBER, bold=True, space_before=10, space_after=4, first=first)
        elif kind == "t":
            tf2 = _box(slide, MARGIN + Inches(0.25), top, width or BODY_W, Inches(0.01))
            pass
        elif kind == "mono":
            para(tf, text, 12.5, TEAL, font=MONO, space_after=4, first=first)
        elif kind == "note":
            para(tf, text, 12, MUTED, space_after=3, first=first)
        else:
            para(tf, ("•  " if kind == "b" else "   ") + text, size,
                 INK if kind == "b" else MUTED, space_after=6, first=first)
        first = False
    return tf


def table(slide, headers, rows, top, left=MARGIN, widths=None, font_size=12.5):
    shape = slide.shapes.add_table(len(rows) + 1, len(headers), left, top,
                                   BODY_W, Inches(0.4) * (len(rows) + 1))
    tbl = shape.table
    if widths:
        total = sum(widths)
        for i, wfrac in enumerate(widths):
            tbl.columns[i].width = Emu(int(BODY_W * wfrac / total))
    for c, text in enumerate(headers):
        cell = tbl.cell(0, c)
        cell.fill.solid(); cell.fill.fore_color.rgb = PANEL
        cell.text = text
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(font_size); p.font.bold = True
            p.font.color.rgb = TEAL; p.font.name = FONT
    for r, row in enumerate(rows, start=1):
        for c, text in enumerate(row):
            cell = tbl.cell(r, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = PANEL_ALT if r % 2 else BG
            cell.text = str(text)
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(font_size); p.font.name = FONT
                p.font.color.rgb = INK
    return tbl


def footer(slide, num, text="RailOps VN · CompressorGuard · MUGVN Hackathon 2026"):
    tf = _box(slide, MARGIN, H - Inches(0.5), BODY_W, Inches(0.3))
    para(tf, f"{text}   |   {num}", 10, MUTED, first=True)


# ---------------------------------------------------------------------------
# Deck content
# ---------------------------------------------------------------------------

def build() -> Presentation:
    prs = Presentation()
    prs.slide_width, prs.slide_height = W, H
    blank = prs.slide_layouts[6]

    def new():
        slide = prs.slides.add_slide(blank)
        _fill(slide, BG)
        return slide

    # 1 — Title
    s = new()
    tf = _box(s, MARGIN, Inches(2.2), BODY_W, Inches(3.4))
    para(tf, "MUGVN HACKATHON 2026  ·  MONGODB × DATADOG", 13, TEAL, bold=True, first=True,
         space_after=14)
    para(tf, "RailOps VN", 58, INK, bold=True, space_after=2)
    para(tf, "CompressorGuard — Phân hệ lõi sống còn", 26, AMBER, bold=True, space_after=18)
    para(tf, "Nền tảng vận hành đường sắt Việt Nam bằng dữ liệu thời gian thực: "
             "IoT telemetry thật, MongoDB đa mô thức, Datadog observability, "
             "và quyền quyết định nằm trong tay người điều độ.", 15, MUTED, space_after=0)
    footer(s, 1)

    # 2 — Hero number
    s = new()
    tf = _box(s, MARGIN, Inches(1.5), BODY_W, Inches(4.6))
    para(tf, "THỜI GIAN CHÚNG TÔI MUA LẠI ĐƯỢC", 13, TEAL, bold=True, first=True, space_after=8)
    para(tf, "33h 52m", 108, INK, bold=True, space_after=10, align=PP_ALIGN.LEFT)
    para(tf, "sớm hơn cách konvensional phát hiện lỗi rò khí máy nén — trên 1.516.948 "
             "điểm đo vật lý thật, không một giá trị do phần mềm sinh ra.", 17, AMBER,
         space_after=16)
    para(tf, "Chúng tôi không bán độ chính xác. Chúng tôi bán thời gian để quyết định: "
             "đủ một ca trực cộng một khoảng bảo trì đêm để kéo tàu về depot và thay một cái gioăng.",
         15, MUTED, space_after=0)
    footer(s, 2)

    # 3 — Real problem
    s = new()
    header(s, "Vấn đề có thật", "Một máy nén khí cấp khí cho ba hệ thống an toàn chạy tàu")
    bullets(s, [
        ("b", "Phanh khí động — mất áp là mất phanh, buộc dừng tàu."),
        ("b", "Treo khí — mất áp là goòng cứng, giới hạn tốc độ, nguy cơ ở ga cong."),
        ("b", "Cửa hành khách & còi — mất áp là tàu chết kẹt trong ga."),
    ], top=Inches(1.7))
    table(s, ["Bằng chứng thực tế tại Việt Nam", "Ý nghĩa vận hành"], [
        ["Cát Linh – Hà Đông xuống cấp nhiều hạng mục sau hơn 3 năm; ga Yên Nghĩa bị nước tràn (23/5/2025), Hà Nội đề xuất sửa chữa khẩn cấp",
         "Đầu tàu và hạ tầng đã vào vùng mòn; giám sát theo đồng hồ giờ đã hết chỗ dựa"],
        ["10 tuyến đường sắt đô thị đang chuẩn bị đầu tư trong 2025–2026; Hanoi Metro lập Xí nghiệp Quản lý Bảo trì riêng",
         "Đội tàu phình nhanh hơn tốc độ tuyển kỹ sư có kinh nghiệm"],
        ["ĐSCT Bắc – Nam 1.541 km, ~1,7 triệu tỷ VND, khởi công trước cuối 2026",
         "Cửa sổ thiết kế hệ thống giám sát ngay từ bàn giao vẫn đang mở"],
    ], top=Inches(3.35), widths=[6.2, 4.4], font_size=11.5)
    footer(s, 3)

    # 4 — Gap
    s = new()
    header(s, "Vì sao giải pháp hiện có chưa đủ", "Ba cách làm quen thuộc, mỗi cách thiếu một phần còn lại")
    table(s, ["Hướng đang dùng", "Giới hạn thật", "RailOps VN khác ở đâu"], [
        ["SCADA / ngưỡng tĩnh (CBM)",
         "Ngưỡng không phân biệt LOADED và UNLOADED → hoặc bỏ sót leak tiến triển, hoặc báo động ảo tràn lan",
         "Regime-aware: mọi sigma tính trong từng chế độ; nhảy bậc ≥3 chu kỳ mang tải mới nâng case"],
        ["ML dự báo hộp đen",
         "Trả về một điểm anomaly; không nói tại sao, đã lâu chưa, sửa xong thật chưa",
         "4 thẻ bằng chứng + provenance từng tín hiệu + Recovery Verification"],
        ["CMMS / EAM work order",
         "Ghi lại quyết định sau khi nó đã được đưa ra; không có dòng thời gian vật lý",
         "Sổ cái CaseEvent: actor + event_time + nguồn dữ liệu, nối được sang work order"],
    ], top=Inches(1.8), widths=[2.5, 4.6, 4.6], font_size=11.5)
    tf = _box(s, MARGIN, Inches(5.9), BODY_W, Inches(1.0))
    para(tf, "Bài toán không phải \"dự đoán lỗi\". Bài toán là mua lại được thời gian để một con người ra quyết định có căn cứ.",
         15, AMBER, bold=True, first=True)
    footer(s, 4)

    # 5 — Platform positioning
    s = new()
    header(s, "Định vị", "RailOps VN là nền tảng — CompressorGuard là bằng chứng nó chạy được")
    bullets(s, [
        ("mono", "RAILOPS VN  (platform)   ·   Data spine: Fleet → Train → Subsystem → Asset"),
        ("h", "PHÂN HỆ ĐANG CHẠY THẬT HÔM NAY"),
        ("b", "CompressorGuard — Mission-Critical Core: vật lý, telemetry, hồ sơ sự cố end-to-end"),
        ("h", "CÙNG MỘT SHARED ENGINE, CHỈ ĐỔI signal_pack + playbook"),
        ("t", "Brake & Door Air Circuit Guard (Phase 2) · Traction/HV interlock (Phase 3) · Platform & escalator (Phase 3) · Track & signals (Phase 4)"),
        ("h", "HẠ TẦNG CHUNG"),
        ("t", "MongoDB Time Series + Document  ·  Datadog APM/Metrics/Monitors  ·  IoT Edge (CAN/MVB → MQTT)"),
    ], top=Inches(1.7), size=14)
    tf = _box(s, MARGIN, Inches(6.15), BODY_W, Inches(0.8))
    para(tf, "Onboard một phân hệ mới là cấu hình, không phải code. Đây là tính nền tảng, không phải tham vọng.",
         15, TEAL, bold=True, first=True)
    footer(s, 5)

    # 6 — Creativity
    s = new()
    header(s, "Sáng tạo — 30%", "Bốn cơ chế chúng tôi chủ động chọn, không phải mặc định")
    table(s, ["Cơ chế", "Điều nó thay đổi trong vận hành"], [
        ["Regime-aware detection",
         "Sigma tính riêng trong LOADED / UNLOADED. Máy nén nghỉ thì áp thấp là bình thường — hệ thống biết điều đó."],
        ["Dual-clock + deterministic replay",
         "event_time vật lý không bao giờ bị ghi đè. Mọi sự cố replay lại y nguyên để điều tra và thanh tra."],
        ["ActionGuard — 5 cổng pre-flight",
         "Hàng rào chặn cả quyết định của con người khi bằng chứng chưa đủ. Sai một lần là mất người."],
        ["Recovery Verification",
         "Từ chối cho đóng hồ sơ nếu 5 mẫu mang tải liên tiếp chưa thực sự đạt chuẩn. Báo hết lỗi ≠ đã lành."],
        ["Anti-alert-fatigue có sổ cái",
         "Excursion transient bị suppression NHƯNG được ghi lại — chứng minh hệ thống đã thấy và có lý do không cắt tàu."],
    ], top=Inches(1.75), widths=[3.5, 7.2], font_size=12)
    footer(s, 6)

    # 7 — Technical
    s = new()
    header(s, "Kỹ thuật — 30%", "Không có dữ liệu giả, không có con số trang trí")
    bullets(s, [
        ("h", "DỮ LIỆU & PHÂN TÍCH"),
        ("b", "1.516.948 điểm đo MetroPT-3 thật (Nature Scientific Data) — Zero Fake Telemetry, kiểm toán bằng Gate 1"),
        ("b", "MongoDB Time Series + $setWindowFields: rolling mean/σ phân vùng theo chế độ mang tải, tính trong DB"),
        ("b", "4 detector + Isolation Forest đa biến đối chiếu; CaseEvent ledger bền hoá, có provenance từng event"),
        ("h", "VẬN HÀNH & BẰNG CHỨNG CHẤT LƯỢNG"),
        ("b", "Datadog: APM traces theo từng khung dữ liệu, DogStatsD metrics, monitors, dashboard, on-call"),
        ("b", "Evaluation Gates G1–G5: PASS — chạy lại được bằng một lệnh, không phải ảnh chụp"),
        ("b", "Producer độc lập scripts/stream_telemetry.py: dashboard không kéo telemetry, theo đúng ThreatLens pattern"),
    ], top=Inches(1.7), size=14)
    tf = _box(s, MARGIN, Inches(6.2), BODY_W, Inches(0.7))
    para(tf, "MongoDB để hiểu con tàu. Datadog để hiểu hệ thống đang hiểu con tàu.", 15, AMBER, bold=True, first=True)
    footer(s, 7)

    # 8 — IoT / realtime
    s = new()
    header(s, "Module IoT", "Gắn được ra thực địa ngay, vì ta không phải gắn gì mới")
    bullets(s, [
        ("mono", "CAN/MVB/TCMS → Edge Gateway → MQTT (store-and-forward) → Ingest → MongoDB → Engine → Datadog"),
        ("h", "ĐIỂM THEN CHỐT"),
        ("b", "Áp suất bình chính, nhiệt độ dầu, dòng động cơ đã có sẵn trên bus điều khiển của đầu tàu hiện đại."),
        ("b", "Pilot = bản sao read-only từ TCMS: không đụng mạch điều khiển, không cần phê duyệt an toàn chạy tàu."),
        ("b", "Trong hầm mất kết nối: gateway buffer, phát lại; mỗi điểm giữ event_time nên replay là xác định."),
        ("h", "KHI NÀO CẦN THÊM CẢM BIẾN"),
        ("t", "Rung / acoustic retrofit chỉ khi overhaul — dùng làm Layer C đối chứng, không rò vào detector online."),
    ], top=Inches(1.7), size=14)
    footer(s, 8)

    # 9 — Human in the loop
    s = new()
    header(s, "Cơ chế vận hành", "Engine đề xuất. Con người ký. Hàng rào chặn cả hai.")
    table(s, ["Bước", "Ai làm", "Bằng chứng để mở"], [
        ["1. Acknowledge & Triage", "Điều độ viên nhận case, đặt priority, ghi danh tính", "POST /api/case/acknowledge → event có actor"],
        ["2. Forensic note + Work Order", "Người viết ghi chú điều tra, chọn playbook & depot", "POST /api/case/notes · /api/case/work-order"],
        ["3. ActionGuard 5/5 → Safe Mode", "Hệ thống kiểm tra, người mới được phép bấm", "GET /api/action/guard-status — và HTTP 409 khi chưa đủ"],
        ["4. Recovery Verification + Sign-Off", "Hệ thống từ chối đóng nếu chưa 5/5 LOADED đạt chuẩn", "GET /api/recovery → POST /api/case/close"],
    ], top=Inches(1.8), widths=[3.3, 4.1, 4.3], font_size=11.5)
    tf = _box(s, MARGIN, Inches(5.75), BODY_W, Inches(1.1))
    para(tf, "Chúng tôi cố tình KHÔNG tự động hóa hết. Auto-pilot dừng tàu là rủi ro; auto-pilot trong điều tra là tiết kiệm nhân lực. Ranh giới đó là sản phẩm.",
         15, TEAL, bold=True, first=True, space_after=6)
    para(tf, "Bấm Safe Mode sớm sẽ bị từ chối công khai — đó là tính năng ta muốn BGK nhìn thấy, không phải bug cần che.",
         13, MUTED, space_after=0)
    footer(s, 9)

    # 10 — Impact
    s = new()
    header(s, "Tác động — 30%", "Giá trị tính bằng giờ chạy tàu và capex tránh được")
    table(s, ["Nguồn giá trị", "Cơ chế", "Loại con số"], [
        ["Avoided unplanned withdrawal", "33h52m đủ để dời sửa sang khoảng bảo trì đêm", "Mô hình hoá, có công thức"],
        ["Avoided catastrophic overhaul", "Thay gioăng sớm thay vì breakage piston", "Mô hình hoá"],
        ["Reduced fleet redundancy", "Tin vào trạng thái thiết bị → giữ ít đầu tàu dự phòng hơn", "Capex avoidance — khoản lớn nhất"],
        ["Safety exposure", "Một lần mất áp giữa tuyến không tính bằng tiền", "Không định giá, chỉ nêu rủi ro"],
    ], top=Inches(1.8), widths=[3.4, 4.6, 3.7], font_size=12)
    tf = _box(s, MARGIN, Inches(5.5), BODY_W, Inches(1.4))
    para(tf, "Minh bạch là một tính năng.", 16, AMBER, bold=True, first=True, space_after=6)
    para(tf, "Mọi con số mô hình hoá đều được gắn nhãn và tách khỏi số đo thực — chi tiết trong "
             "docs/RAILOPS_VN_PLATFORM_BLUEPRINT.md. Nhờ đó BGK có thể tin 100% phần số liệu còn lại.",
         13.5, MUTED, space_after=0)
    footer(s, 10)

    # 11 — Rollout
    s = new()
    header(s, "Kế hoạch triển khai", "Bốn phase, rủi ro giảm dần, không xin 18 tháng pilot")
    table(s, ["Phase", "Phạm vi", "Thời gian", "Thành công đo bằng"], [
        ["0 · Proof", "CompressorGuard end-to-end trên dữ liệu thật", "Đã xong (bài nộp này)", "Gates G1–G5 PASS + lead time 33h52m"],
        ["1 · Pilot", "2 đầu tàu Cát Linh – Hà Đông, read-only mirror từ TCMS", "6 tháng", "Tỷ lệ báo động ảo; số lead time thành quyết định thật"],
        ["2 · Mở rộng", "BrakeAirGuard, DoorAirGuard dùng chung engine; tích hợp EAM một chiều", "6–12 tháng", "Số phân hệ onboard bằng cấu hình, không sửa code"],
        ["3 · Nhân bản", "Metro số 1 Bến Thành – Suối Tiên & Line 3 Nhổn – Ga Hà Nội", "12–18 tháng", "Onboard đoàn mới = cấu hình Asset Registry"],
        ["4 · Chuẩn hoá", "Schema telemetry + event ledger cho ĐSCT Bắc – Nam", "từ 2026", "Dữ liệu sinh ra theo chuẩn, không retrofit"],
    ], top=Inches(1.75), widths=[1.5, 4.2, 1.6, 4.0], font_size=11)
    footer(s, 11)

    # 12 — Ask
    s = new()
    tf = _box(s, MARGIN, Inches(1.9), BODY_W, Inches(4.2))
    para(tf, "CHÚNG TÔI XIN", 13, TEAL, bold=True, first=True, space_after=8)
    para(tf, "Sáu tháng và hai đầu tàu.", 44, INK, bold=True, space_after=16)
    para(tf, "Đổi lại: một phân hệ đã chạy trọn đường — phát hiện sớm 33h52m, bằng chứng số, "
             "can thiệp có hàng rào, kiểm chứng phục hồi — và một kiến trúc nền tảng sẵn sàng "
             "cho 1.541 km đang được xây.", 16, MUTED, space_after=20)
    bullets(s, [
        ("h", "BỐN TỨA ĐIỂM, TỰ CHỨNG MINH"),
        ("t", "Sáng tạo: 4 cơ chế không mặc định  ·  Kỹ thuật: 1.5M điểm thật + gates PASS  ·  "
              "Tác động: vấn đề VN có thật + rollout 4 phase  ·  Trình bày: console zero-hardcode, không nút demo trên header"),
    ], top=Inches(5.35), size=13)
    tf2 = _box(s, MARGIN, Inches(6.5), BODY_W, Inches(0.6))
    para(tf2, "python run_demo.py  →  http://localhost:8000/console", 14, TEAL, font=MONO, first=True)
    footer(s, 12)

    return prs


if __name__ == "__main__":
    prs = build()
    prs.save(OUT)
    print(f"[OK] wrote {OUT} with {len(prs.slides._sldIdLst)} slides")
