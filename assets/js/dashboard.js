let chart, currentData = [], rowsPerPage = 10, currentPage = 1;

function toUTCDateFromLocalInput(dateStr) {
  return dateStr ? new Date(dateStr) : null;
}

function parseFlexibleDate(input) {
  const iso = Date.parse(input);
  if (!isNaN(iso)) return new Date(iso);
  const cleaned = input.replace(/ CEST| CET| UTC| GMT.*$/, '');
  const attempt = new Date(cleaned);
  return isNaN(attempt) ? null : attempt;
}

function showMessage(msg) {
  const container = document.getElementById("message-container");
  container.classList.remove("d-none");
  container.textContent = msg;
  setTimeout(() => container.classList.add("d-none"), 5000);
}

async function loadData() {
  const res = await fetch('database.json', { cache: 'no-store' });
  return await res.json();
}

function updateStats(data) {
  // Nombre de capteurs uniques
  const sensors = new Set();
  data.forEach(d => {
    const name = d?.deviceInfo?.deviceName;
    if (name) sensors.add(name);
  });
  document.getElementById('total-sensors').textContent = sensors.size;

  // Nombre total de données
  document.getElementById('total-data').textContent = data.length.toLocaleString();

  // Dernière réception
  if (data.length > 0) {
    const latest = data.reduce((latest, current) => {
      const currentTime = new Date(current.timestamp);
      const latestTime = new Date(latest.timestamp);
      return currentTime > latestTime ? current : latest;
    });
    const timeAgo = getTimeAgo(new Date(latest.timestamp));
    document.getElementById('last-received').textContent = timeAgo;
  }

  // Statut (basé sur la récence des données)
  const now = new Date();
  const oneHour = 60 * 60 * 1000;
  const recentData = data.filter(d => {
    const dataTime = new Date(d.timestamp);
    return (now - dataTime) < oneHour;
  });

  if (recentData.length > 0) {
    document.getElementById('status-indicator').textContent = '🟢';
  } else {
    document.getElementById('status-indicator').textContent = '🟡';
  }
}

function getTimeAgo(date) {
  const now = new Date();
  const diff = now - date;
  const minutes = Math.floor(diff / (1000 * 60));
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (minutes < 60) return `${minutes}min`;
  if (hours < 24) return `${hours}h`;
  return `${days}j`;
}

function safeDateLabel(str) {
  const cleaned = str.replace(/( CEST| CET| UTC| GMT.*)$/, '').replace(' ', 'T');
  const date = new Date(cleaned);
  return isNaN(date.getTime()) ? "Date invalide" : date.toLocaleString("fr-FR", { hour12: false });
}

async function updateChart() {
  const capteur   = document.getElementById("capteur").value;
  const startDate = toUTCDateFromLocalInput(document.getElementById("start-time").value);
  const endDate   = toUTCDateFromLocalInput(document.getElementById("end-time").value);
  const selected  = Array.from(document.querySelectorAll("#grandeur-checkboxes input:checked"))
                          .map(cb => cb.value);

  if (!capteur || selected.length === 0) {
    showMessage("Sélectionne un capteur et au moins une grandeur.");
    return;
  }

  const data     = await loadData();
  const filtered = data.filter(d => {
    const ts = parseFlexibleDate(d.timestamp);
    if (!ts) return false;
    const okDate = (!startDate || ts >= startDate) && (!endDate || ts <= endDate);
    const okCap  = capteur === "all" || d.deviceInfo?.deviceName === capteur;
    return okDate && okCap;
  });

  if (filtered.length === 0) {
    showMessage("Aucune donnée trouvée pour cette période ou ce capteur.");
    return;
  }

  const datasets = selected.map((g, i) => {
    const rawPts = filtered
      .map(d => {
        const ts  = parseFlexibleDate(d.timestamp);
        const raw = d.decoded?.[g];
        const y   = (raw && typeof raw === 'object') ? raw.value : raw;
        return (ts && typeof y === 'number') ? { x: ts, y } : null;
      })
      .filter(p => p !== null && p.y >= 0)
      .sort((a, b) => a.x - b.x);

    // Filtrage des variations extrêmes
    const maxDelta = 200;
    const pts = rawPts.filter((p,i, arr) =>{
      if (i===0) return true;
      return Math.abs(p.y - arr[i-1].y) <= maxDelta;
    });

    const values = pts.map(p => p.y);
    const min    = Math.min(...values);
    const max    = Math.max(...values);
    const avg    = values.reduce((sum, v) => sum + v, 0) / values.length;

    return {
      label: `${g} (min : ${min.toFixed(2)}, moy : ${avg.toFixed(2)}, max : ${max.toFixed(2)})`,
      data: pts,
      borderColor: getColor(i),
      fill: false,
      tension: 0.3
    };
  });

  chart.data.datasets = datasets;
  chart.update();

  document.getElementById("nb-trames").textContent =
    `${filtered.length} / ${data.length} trames affichées`;
  document.getElementById("last-update").textContent =
    "Dernière mise à jour : " + new Date().toLocaleString('fr-FR');
}

function clearDates() {
  document.getElementById("start-time").value = "";
  document.getElementById("end-time").value = "";
}

function setToday() {
  const now = new Date();
  const yyyy = now.getFullYear();
  const mm = String(now.getMonth() + 1).padStart(2, '0');
  const dd = String(now.getDate()).padStart(2, '0');

  const start = `${yyyy}-${mm}-${dd}T00:00`;
  const end = `${yyyy}-${mm}-${dd}T23:59`;

  document.getElementById("start-time").value = start;
  document.getElementById("end-time").value = end;
}

function exportChart() {
  const link = document.createElement('a');
  link.download = "graphique-lora.png";
  link.href = chart.toBase64Image();
  link.click();
}

function populateCapteursFromCurrentData() {
  const select = document.getElementById("capteur");
  const seen = new Set();
  (currentData || []).forEach(d => {
    const name = d?.deviceInfo?.deviceName;
    if (name && !seen.has(name)) {
      seen.add(name);
      const opt = document.createElement("option");
      opt.value = name; opt.textContent = name;
      select.appendChild(opt);
    }
  });
}

function resetFilters() {
  document.getElementById("capteur").value = "all";
  clearDates();
  document.getElementById("grandeur-checkboxes").innerHTML = "";
  chart.data.datasets = [];
  chart.update();
}

async function refreshTable() {
  const loading = document.getElementById('loading-indicator');
  loading.classList.remove('d-none');

  try {
    const prevPage = currentPage;
    currentData = await loadData();
    updateStats(currentData);
    renderPage(prevPage);
  } finally {
    loading.classList.add('d-none');
  }
}

function exportCSV() {
  if (!Array.isArray(currentData) || currentData.length === 0) {
    showMessage("Aucune donnée à exporter.");
    return;
  }
  const header = ["timestamp","Nom du capteur","Product_type","Fabricant","data","decoded"];
  const rows = currentData.map(row => {
    const decoded = row.decoded || {};
    const product = decoded.Product_type ?? "Inconnu";
    const devName = row.deviceInfo?.deviceName ?? "Inconnu";
    const fabricant = decoded.Fabricant ?? "N/A";
    const payload = row.data ?? "";
    const decodedStr = JSON.stringify(decoded).replace(/\n/g," ");
    return [
      row.timestamp ?? "",
      devName,
      product,
      fabricant,
      payload,
      decodedStr
    ].map(v => `"${String(v).replace(/"/g,'""')}"`).join(",");
  });
  const csv = [header.join(","), ...rows].join("\n");
  const blob = new Blob([csv], {type:"text/csv;charset=utf-8"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "export.csv"; a.click();
  URL.revokeObjectURL(url);
}

function renderPage(page) {
  const tbody = document.getElementById('sensor-tbody');
  const pagination = document.getElementById('pagination');
  tbody.innerHTML = '';
  pagination.innerHTML = '';
  const totalPages = Math.ceil(currentData.length / rowsPerPage);
  currentPage = Math.min(Math.max(1, page), totalPages);
  const start = (currentPage - 1) * rowsPerPage;
  const visible = currentData.slice(start, start + rowsPerPage);

  visible.forEach(d => {
    const tr = document.createElement('tr');
    if (d.decoded?.co2?.value > 1000) tr.classList.add('alarm');
    tr.innerHTML = `
      <td>${safeDateLabel(d.timestamp)}</td>
      <td>${d.deviceInfo?.deviceName || 'Inconnu'}</td>
      <td>${d.decoded?.Product_type || 'Inconnu'}</td>
      <td>${d.decoded?.Fabricant || 'N/A'}</td>
      <td><pre>${d.data || ''}</pre></td>
      <td><pre>${JSON.stringify(d.decoded, null, 2)}</pre></td>
    `;
    tbody.appendChild(tr);
  });

  // Pagination
  const prevLi = document.createElement('li');
  prevLi.className = 'page-item'+(currentPage===1?' disabled':'');
  prevLi.innerHTML = `<a class="page-link" href="#">Précédent</a>`;
  prevLi.onclick = ()=> currentPage>1 && renderPage(currentPage-1);
  pagination.appendChild(prevLi);

  const maxBtns = 5;
  let startPage = Math.max(1, currentPage - Math.floor(maxBtns/2));
  let endPage = Math.min(totalPages, startPage + maxBtns - 1);
  if (endPage - startPage < maxBtns-1) startPage = Math.max(1, endPage - maxBtns + 1);

  for (let i = startPage; i <= endPage; i++) {
    const li = document.createElement('li');
    li.className = 'page-item'+(i===currentPage?' active':'');
    li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
    li.onclick = ()=> renderPage(i);
    pagination.appendChild(li);
  }

  const next = document.createElement('li');
  next.className = 'page-item' + (currentPage === totalPages ? ' disabled' : '');
  next.innerHTML = `<a class="page-link" href="#">Suivant</a>`;
  next.onclick = () => currentPage < totalPages && renderPage(currentPage + 1);
  pagination.appendChild(next);

  document.getElementById("nb-trames").textContent = `${currentData.length} trames affichées`;
  document.getElementById("last-update").textContent = "Dernière mise à jour : " + new Date().toLocaleString('fr-FR');
}

async function updateGrandeurs() {
  const capteur = document.getElementById("capteur").value;
  const container = document.getElementById("grandeur-checkboxes");
  container.innerHTML = '';
  if (capteur === "all") return;
  const data = await loadData();
  const filtered = data.filter(d => d.deviceInfo?.deviceName === capteur);
  const grandeursSet = new Set();

  filtered.forEach(d => {
    if (d.decoded) {
      Object.entries(d.decoded).forEach(([key, val]) => {
        if (typeof val === 'object' && 'value' in val) grandeursSet.add(key);
      });
    }
  });

  grandeursSet.forEach(gr => {
    const div = document.createElement('div');
    div.className = "form-check";
    div.innerHTML = `
      <input type="checkbox" class="form-check-input" id="chk-${gr}" value="${gr}">
      <label class="form-check-label" for="chk-${gr}">${gr}</label>
    `;
    container.appendChild(div);
  });
}

function getColor(i) {
  const colors = ['#007bff', '#dc3545', '#28a745', '#ffc107', '#17a2b8', '#6f42c1', '#fd7e14'];
  return colors[i % colors.length];
}

window.onload = async function() {
  try {
    const ctx = document.getElementById('chart').getContext('2d');
    chart = new Chart(ctx, {
      type: 'line',
      data: { datasets: [] },
      options: {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        scales: {
          x: { type: 'time' },
          y: { beginAtZero: false }
        },
        plugins: {
          tooltip: {
            callbacks: {
              title: items => items[0].label,
              label: context => context.parsed.y
            }
          }
        }
      }
    });
  } catch (e) {
    console.error("Échec init Chart.js:", e);
  }
  await refreshTable();
  populateCapteursFromCurrentData();
  setInterval(refreshTable, 10000);
};