// --- Global State ---
let chartInstance = null; // Main Dashboard Chart
let detailedChartInstance = null; // Analytics Chart
let allData = [];
let currentPage = 1;
const rowsPerPage = 15;

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
  fetchData();
  // Simuler des logs
  addConsoleLog('system', 'Connexion au serveur LoRaWAN établie.');
});

// --- Navigation SPA ---
function switchView(viewName) {
  document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active'));
  event.currentTarget.classList.add('active');

  document.querySelectorAll('.view-section').forEach(el => el.style.display = 'none');
  document.getElementById(`view-${viewName}`).style.display = 'block';

  const titles = {
    'dashboard': 'Vue Globale',
    'devices': 'Gestion des Appareils',
    'console': 'Terminal de Commande',
    'analytics': 'Analyses & Rapports',
    'data': 'Historique des Données'
  };
  document.getElementById('page-title').innerText = titles[viewName];

  if (viewName === 'analytics' && detailedChartInstance) detailedChartInstance.resize();
  if (viewName === 'dashboard' && chartInstance) chartInstance.resize();
}

// --- Data Fetching ---
async function fetchData() {
  try {
    const response = await fetch('database.json');
    if (!response.ok) throw new Error("Erreur chargement données");
    const data = await response.json();

    if (!Array.isArray(data)) return console.error("Format de données invalide");

    // Standardization
    allData = data.map(d => ({
      received_at: d.timestamp,
      timestamp_obj: parseFlexibleDate(d.timestamp),
      device_name: d.deviceInfo?.deviceName || d.devEUI || "Inconnu",
      device_eui: d.devEUI || "N/A",
      rssi: -110,
      snr: 5.0,
      battery: 100,
      raw_payload: d.data,
      decoded: d.decoded || {}
    })).sort((a, b) => a.timestamp_obj - b.timestamp_obj);

    updateGlobalStats();
    updateDevicesList();
    initOverviewChart();
    renderTable(1);
    populateSensorSelect();

  } catch (error) {
    console.error("Erreur:", error);
    addConsoleLog('system', 'Erreur chargement base de données.');
  }
}

// --- Helpers ---
function parseFlexibleDate(input) {
  if (!input) return new Date();
  // Try ISO parse
  let d = new Date(input);
  if (!isNaN(d)) return d;
  // Try cleanup custom format
  const cleaned = input.replace(/ CEST| CET| UTC| GMT.*$/, '').replace(' ', 'T');
  d = new Date(cleaned);
  return isNaN(d) ? new Date() : d;
}

// --- Stats & Dashboard ---
function updateGlobalStats() {
  const uniqueSensors = [...new Set(allData.map(d => d.device_name))];
  animateValue("total-sensors", 0, uniqueSensors.length, 1000);
  animateValue("total-data", 0, allData.length, 1500);

  if (allData.length > 0) {
    const last = allData[allData.length - 1];
    const dt = luxon.DateTime.fromJSDate(last.timestamp_obj);
    document.getElementById('last-received').innerText = dt.toRelative();
  }
}

function animateValue(id, start, end, duration) {
  const obj = document.getElementById(id);
  if (!obj) return;
  let startTimestamp = null;
  const step = (timestamp) => {
    if (!startTimestamp) startTimestamp = timestamp;
    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
    obj.innerHTML = Math.floor(progress * (end - start) + start);
    if (progress < 1) window.requestAnimationFrame(step);
  };
  window.requestAnimationFrame(step);
}

// --- Devices Management ---
function updateDevicesList() {
  const tbody = document.getElementById('devices-list-body');
  if (!tbody) return;
  const uniqueSensors = [...new Set(allData.map(d => d.device_name))];
  tbody.innerHTML = '';

  uniqueSensors.forEach(sensor => {
    const sensorData = allData.filter(d => d.device_name === sensor);
    const lastPacket = sensorData[sensorData.length - 1];
    const dt = luxon.DateTime.fromJSDate(lastPacket.timestamp_obj);

    const tr = document.createElement('tr');
    tr.innerHTML = `
            <td><span class="status-dot"></span> Online</td>
            <td style="font-family: monospace; color: var(--accent);">${sensor}</td>
            <td>${dt.toRelative()}</td>
            <td>${lastPacket.rssi} / ${lastPacket.snr}</td>
            <td><div class="progress" style="height: 6px; width: 60px; background: #333;"><div class="progress-bar bg-success" style="width: ${lastPacket.battery}%"></div></div></td>
            <td><button class="btn btn-sm btn-outline-light"><i class="bi bi-three-dots"></i></button></td>
        `;
    tbody.appendChild(tr);

    // Populate console select
    const dlSelect = document.getElementById('downlink-device');
    if (dlSelect && !Array.from(dlSelect.options).some(o => o.value === sensor)) {
      dlSelect.add(new Option(sensor, sensor));
    }
  });
}

// --- Table & Pagination ---
function renderTable(page) {
  const tbody = document.getElementById('sensor-tbody');
  const pagination = document.getElementById('pagination');
  if (!tbody) return;

  tbody.innerHTML = '';
  pagination.innerHTML = '';

  // Sort descending for table
  const sorted = [...allData].reverse();
  const totalPages = Math.ceil(sorted.length / rowsPerPage);
  currentPage = Math.min(Math.max(1, page), totalPages);

  const start = (currentPage - 1) * rowsPerPage;
  const visible = sorted.slice(start, start + rowsPerPage);

  visible.forEach(d => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td>${d.received_at}</td>
        <td>${d.device_name}</td>
        <td>${d.decoded.Product_type || '-'}</td>
        <td><pre style="margin:0; font-size:0.8em">${d.raw_payload || ''}</pre></td>
        <td><pre style="margin:0; font-size:0.8em; color:var(--text-muted)">${JSON.stringify(d.decoded, null, 2)}</pre></td>
      `;
    tbody.appendChild(tr);
  });

  // Pagination UI
  const createItem = (text, p, active = false, disabled = false) => {
    const li = document.createElement('li');
    li.className = `page-item ${active ? 'active' : ''} ${disabled ? 'disabled' : ''}`;
    li.innerHTML = `<a class="page-link" href="#">${text}</a>`;
    li.onclick = (e) => { e.preventDefault(); if (!disabled) renderTable(p); };
    return li;
  };

  pagination.appendChild(createItem('Préc.', currentPage - 1, false, currentPage === 1));
  let startP = Math.max(1, currentPage - 2);
  let endP = Math.min(totalPages, startP + 4);
  for (let i = startP; i <= endP; i++) {
    pagination.appendChild(createItem(i, i, i === currentPage));
  }
  pagination.appendChild(createItem('Suiv.', currentPage + 1, false, currentPage === totalPages));
}

function exportCSV() {
  if (!allData.length) return alert("Aucune donnée");
  const header = ["Horodatage", "Device", "Payload", "Decoded"];
  const rows = allData.map(d => [
    d.received_at, d.device_name, d.raw_payload, JSON.stringify(d.decoded).replace(/"/g, '""')
  ].map(v => `"${v}"`).join(","));

  const csv = [header.join(","), ...rows].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "export_lora.csv"; a.click();
}

// --- Charting Logic ---
function initOverviewChart() {
  const ctx = document.getElementById('overview-chart')?.getContext('2d');
  if (!ctx) return;

  // Simple density plot per hour
  // Group by day
  const grouped = {};
  allData.forEach(d => {
    const key = d.timestamp_obj.toISOString().split('T')[0];
    grouped[key] = (grouped[key] || 0) + 1;
  });

  const dataPts = Object.entries(grouped)
    .sort((a, b) => new Date(a[0]) - new Date(b[0]))
    .map(([k, v]) => ({ x: k, y: v }));

  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      datasets: [{
        label: 'Trames par jour',
        data: dataPts,
        backgroundColor: '#5e6ad2',
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { type: 'time', time: { unit: 'day' }, grid: { color: '#2a2a35' } },
        y: { grid: { color: '#2a2a35' } }
      }
    }
  });
}

// --- Analytics Logic ---
function populateSensorSelect() {
  const sel = document.getElementById('capteur');
  if (!sel) return;
  const sensors = [...new Set(allData.map(d => d.device_name))];
  sensors.forEach(s => sel.add(new Option(s, s)));
}

function updateGrandeurs() {
  const capteur = document.getElementById('capteur').value;
  const container = document.getElementById('grandeur-checkboxes');
  container.innerHTML = '';

  if (capteur === 'all') {
    container.innerHTML = `<span class="text-muted fst-italic">Veuillez sélectionner un capteur.</span>`;
    return;
  }

  // Find keys in decoded data
  const sensorData = allData.filter(d => d.device_name === capteur);
  const keys = new Set();
  sensorData.forEach(d => {
    if (d.decoded) {
      Object.entries(d.decoded).forEach(([k, v]) => {
        if (typeof v === 'object' && v.value !== undefined) keys.add(k);
        else if (typeof v === 'number') keys.add(k);
      });
    }
  });

  if (keys.size === 0) {
    container.innerHTML = "Aucune variable numérique trouvée.";
    return;
  }

  keys.forEach(k => {
    const div = document.createElement('div');
    div.className = 'form-check';
    div.innerHTML = `<input type="checkbox" class="form-check-input" value="${k}" id="chk-${k}" checked> <label for="chk-${k}">${k}</label>`;
    container.appendChild(div);
  });
}

function updateDetailedChart() {
  const capteur = document.getElementById('capteur').value;
  if (capteur === 'all') return alert("Sélectionnez un capteur");

  // get selected keys
  const checkboxes = document.querySelectorAll('#grandeur-checkboxes input:checked');
  const keys = Array.from(checkboxes).map(c => c.value);

  if (!keys.length) return alert("Sélectionnez au moins une variable");

  const startStr = document.getElementById('start-time').value;
  const endStr = document.getElementById('end-time').value;
  const start = startStr ? new Date(startStr) : new Date(0);
  const end = endStr ? new Date(endStr) : new Date(2099, 1, 1);

  const filtered = allData.filter(d =>
    d.device_name === capteur &&
    d.timestamp_obj >= start && d.timestamp_obj <= end
  );

  const datasets = keys.map((key, index) => {
    const rawPts = filtered.map(d => {
      let val = d.decoded[key];
      if (val && typeof val === 'object') val = val.value;
      return { x: d.timestamp_obj, y: val };
    }).filter(p => p.y !== undefined);

    return {
      label: key,
      data: rawPts,
      borderColor: getColor(index),
      backgroundColor: getColor(index),
      tension: 0.3,
      borderWidth: 2,
      pointRadius: 2
    };
  });

  const ctx = document.getElementById('detailed-chart').getContext('2d');

  if (detailedChartInstance) detailedChartInstance.destroy();

  detailedChartInstance = new Chart(ctx, {
    type: 'line',
    data: { datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          type: 'time',
          grid: { color: '#2a2a35' },
          ticks: { color: '#8d8d99' }
        },
        y: { grid: { color: '#2a2a35' } }
      },
      plugins: {
        tooltip: { mode: 'index', intersect: false }
      }
    }
  });
}

function getColor(i) {
  const colors = ['#5e6ad2', '#00f2ff', '#22c55e', '#f59e0b', '#ef4444', '#d946ef'];
  return colors[i % colors.length];
}

function setToday() {
  const now = new Date();
  document.getElementById('end-time').value = now.toISOString().slice(0, 16);
  now.setHours(0, 0, 0, 0);
  document.getElementById('start-time').value = now.toISOString().slice(0, 16);
}

function clearDates() {
  document.getElementById('start-time').value = '';
  document.getElementById('end-time').value = '';
}

function exportChart() {
  if (detailedChartInstance) {
    const a = document.createElement('a');
    a.href = detailedChartInstance.toBase64Image();
    a.download = 'chart.png';
    a.click();
  }
}

// --- Console ---
function addConsoleLog(type, message) {
  const container = document.getElementById('live-logs');
  if (!container) return;
  const div = document.createElement('div');
  div.className = `log-entry ${type}`;
  div.innerText = `[${new Date().toLocaleTimeString()}] ${message}`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

async function sendDownlink() {
  const dev = document.getElementById('downlink-device').value;
  const pl = document.getElementById('downlink-payload').value;
  const port = parseInt(document.getElementById('downlink-port')?.value || '1');

  if (!dev || !pl) return alert("Veuillez remplir Device et Payload");

  addConsoleLog('tx', `Envoi Downlink -> ${dev} : ${pl}...`);

  try {
    const res = await fetch('/api/downlink', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ devEui: dev, data: pl, fPort: port })
    });

    const json = await res.json();

    if (res.ok) {
      addConsoleLog('system', `Succès: ${json.status} (${json.message || 'Queued'})`);
      alert("Commande envoyée avec succès !");
    } else {
      addConsoleLog('system', `Erreur: ${json.error}`);
      alert("Erreur lors de l'envoi: " + json.error);
    }
  } catch (e) {
    console.error(e);
    addConsoleLog('system', "Erreur réseau lors de l'envoi.");
    alert("Erreur réseau: " + e.message);
  }
}

function showAddDeviceModal() { alert("Fonctionnalité backend à venir."); }

// Auto-refresh logic for Live Feel
setInterval(() => {
  // Only fetch if tab is active to save bandwidth? 
  // Or always to keep up.
  fetchData();
}, 30000);