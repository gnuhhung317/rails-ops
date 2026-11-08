const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const OUTPUT_DIR = path.resolve(__dirname, '..', 'screenshots_audit');
const ARTIFACT_DIR = 'C:\\Users\\Acer\\.gemini\\antigravity\\brain\\8cb9cce1-2c02-4b36-9c66-d7f7bb3fb053\\screenshots_audit';

if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });
if (!fs.existsSync(ARTIFACT_DIR)) fs.mkdirSync(ARTIFACT_DIR, { recursive: true });

async function run() {
  const edgePath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
  const edge = spawn(edgePath, [
    '--headless',
    '--remote-debugging-port=9222',
    '--disable-gpu',
    '--window-size=1920,1080',
    'http://127.0.0.1:8000/'
  ]);

  try {
    console.log('Starting Edge headless on port 9222...');
    await new Promise(r => setTimeout(r, 2500));

    const tabs = await new Promise((resolve, reject) => {
      http.get('http://127.0.0.1:9222/json', (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => resolve(JSON.parse(data)));
      }).on('error', reject);
    });

    const page = tabs.find(t => t.type === 'page');
    if (!page) throw new Error('No page tab found in Edge');

    const ws = new WebSocket(page.webSocketDebuggerUrl);

    let id = 1;
    const pending = new Map();

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.id && pending.has(msg.id)) {
        const { resolve, reject } = pending.get(msg.id);
        pending.delete(msg.id);
        if (msg.error) reject(msg.error);
        else resolve(msg.result);
      }
    };

    await new Promise(r => ws.onopen = r);

    function send(method, params = {}) {
      return new Promise((resolve, reject) => {
        const reqId = id++;
        pending.set(reqId, { resolve, reject });
        ws.send(JSON.stringify({ id: reqId, method, params }));
      });
    }

    await send('Page.enable');
    await send('Runtime.enable');

    console.log('Waiting for initial data polling and chart rendering...');
    await new Promise(r => setTimeout(r, 3500));

    async function capture(filename, description) {
      const res = await send('Page.captureScreenshot', { format: 'png' });
      const buf = Buffer.from(res.data, 'base64');
      const outPath1 = path.join(OUTPUT_DIR, filename);
      const outPath2 = path.join(ARTIFACT_DIR, filename);
      fs.writeFileSync(outPath1, buf);
      fs.writeFileSync(outPath2, buf);
      console.log(`[SAVED] ${filename} - ${description}`);
    }

    async function evalCode(code) {
      await send('Runtime.evaluate', { expression: code });
    }

    // 1. Tab 1: Fleet & Telemetry (Top)
    await evalCode(`document.querySelector('[data-view="fleet"]').click()`);
    await evalCode(`window.scrollTo(0, 0)`);
    await new Promise(r => setTimeout(r, 1200));
    await capture('01_tab_fleet_top.png', 'Màn 1: Fleet & Telemetry (Phần trên)');

    // 1b. Tab 1: Scrolled down to see suppression stream
    await evalCode(`window.scrollTo(0, 800)`);
    await new Promise(r => setTimeout(r, 800));
    await capture('01b_tab_fleet_bottom_suppression.png', 'Màn 1: Fleet & Telemetry (Cuộn xuống xem bảng chống nhiễu)');

    // 2. Tab 2: Incident Queue
    await evalCode(`window.scrollTo(0, 0)`);
    await evalCode(`document.querySelector('[data-view="queue"]').click()`);
    await new Promise(r => setTimeout(r, 1200));
    await capture('02_tab_queue.png', 'Màn 2: Hàng đợi sự cố (Active & Closed Cases)');

    // 3. Tab 3: Incident Investigation Workbench (Focus: 1. Diễn biến)
    await evalCode(`document.querySelector('[data-view="workbench"]').click()`);
    await evalCode(`document.querySelector('[data-focus="changed"]')?.click()`);
    await new Promise(r => setTimeout(r, 1200));
    await capture('03a_workbench_focus1_dien_bien.png', 'Màn 3: Workbench - Focus 1: Diễn biến');

    // 3b. Focus: 2. Bằng chứng
    await evalCode(`document.querySelector('[data-focus="evidence"]')?.click()`);
    await new Promise(r => setTimeout(r, 1000));
    await capture('03b_workbench_focus2_bang_chung.png', 'Màn 3: Workbench - Focus 2: Bằng chứng');

    // 3c. Focus: 3. Chốt an toàn (ActionGuard)
    await evalCode(`document.querySelector('[data-focus="guard"]')?.click()`);
    await new Promise(r => setTimeout(r, 1000));
    await capture('03c_workbench_focus3_chot_an_toan.png', 'Màn 3: Workbench - Focus 3: Chốt an toàn (ActionGuard)');

    // 3d. Focus: 4. Nghiệm thu (Recovery)
    await evalCode(`document.querySelector('[data-focus="recovery"]')?.click()`);
    await new Promise(r => setTimeout(r, 1000));
    await capture('03d_workbench_focus4_nghiem_thu.png', 'Màn 3: Workbench - Focus 4: Nghiệm thu 5 mẫu');

    // 3e. Focus: 5. Sổ theo dõi (Audit)
    await evalCode(`document.querySelector('[data-focus="audit"]')?.click()`);
    await new Promise(r => setTimeout(r, 1000));
    await capture('03e_workbench_focus5_so_theo_doi.png', 'Màn 3: Workbench - Focus 5: Sổ theo dõi');

    // 4. Tab 4: Timeline / Audit Ledger
    await evalCode(`document.querySelector('[data-view="timeline"]').click()`);
    await new Promise(r => setTimeout(r, 1200));
    await capture('04_tab_timeline_ledger.png', 'Màn 7: Nhật ký sự cố (Append-Only Ledger)');

    // 5. Drawer: Validation Reference (Layer C)
    await evalCode(`document.getElementById('btn-toggle-vr')?.click()`);
    await new Promise(r => setTimeout(r, 1000));
    await capture('05_drawer_validation_reference_layer_c.png', 'Ngăn kéo đối chứng: Validation Reference (Layer C)');
    await evalCode(`document.getElementById('vr-close')?.click()`);
    await new Promise(r => setTimeout(r, 500));

    // 6. Drawer / Replay Studio Dev controls
    await evalCode(`document.getElementById('btn-toggle-replay')?.click()`);
    await evalCode(`document.getElementById('btn-dev')?.click()`);
    await new Promise(r => setTimeout(r, 1000));
    await capture('06_replay_studio_dev_panel.png', 'Ngăn điều khiển mô phỏng / Replay Dev Panel');

    console.log('Done! All screenshots captured and saved.');
    ws.close();
  } catch (err) {
    console.error('Error during screenshot capture:', err);
  } finally {
    edge.kill();
  }
}

run();
