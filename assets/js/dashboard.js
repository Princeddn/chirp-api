// --- Global State ---
let chartInstance = null;
let allData = [];

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
  fetchData();
  // Simuler des logs dans la console
  addConsoleLog('system', 'Connexion au serveur LoRaWAN établie.');
  addConsoleLog('rx', 'Uplink reçu [Device: 24E12...] RSSI: -112dBm');
});

// --- Navigation SPA ---
function switchView(viewName) {
  // Update Menu
  document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active'));
  event.currentTarget.classList.add('active');

  // Update Sections
  document.querySelectorAll('.view-section').forEach(el => el.style.display = 'none');
  document.getElementById(`view-${viewName}`).style.display = 'block';

  // Update Header Title
  const titles = {
    'dashboard': 'Vue Globale',
    'devices': 'Gestion des Appareils',
    'console': 'Terminal de Commande',
    'analytics': 'Analyses & Rapports'
  };
  document.getElementById('page-title').innerText = titles[viewName];
  
  // Resize charts if needed
  if(viewName === 'analytics' || viewName === 'dashboard') {
     if(chartInstance) chartInstance.resize();
  }
}

// --- Data Fetching ---
async function fetchData() {
  try {
    const response = await fetch('database.json');
    if (!response.ok) throw new Error("Erreur chargement données");
    const data = await response.json();
    
    // Validate data structure
    if (!Array.isArray(data)) {
        console.error("Format de données invalide");
        return;
    }
    
    allData = data.sort((a, b) => new Date(a.received_at) - new Date(b.received_at));
    
    updateGlobalStats();
    updateDevicesList();
    initChart(allData); // Init main chart
    
  } catch (error) {
    console.error("Erreur:", error);
    addConsoleLog('system', 'Erreur de chargement des données historiques.');
  }
}

// --- Stats & Dashboard ---
function updateGlobalStats() {
  const uniqueSensors = [...new Set(allData.map(d => d.device_name || d.device_eui))];
  
  // Animate numbers
  animateValue("total-sensors", 0, uniqueSensors.length, 1000);
  animateValue("total-data", 0, allData.length, 1500);
  
  // Network Traffic (Mock simulation for UI)
  document.getElementById('network-traffic').innerText = (Math.random() * 100).toFixed(1) + " Kbps";
}

function animateValue(id, start, end, duration) {
    const obj = document.getElementById(id);
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = Math.floor(progress * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// --- Devices Management ---
function updateDevicesList() {
    const tbody = document.getElementById('devices-list-body');
    const uniqueSensors = [...new Set(allData.map(d => d.device_name))];
    
    tbody.innerHTML = '';
    
    if(uniqueSensors.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Aucun appareil détecté</td></tr>';
        return;
    }

    uniqueSensors.forEach(sensor => {
        // Find last data for this sensor
        const sensorData = allData.filter(d => d.device_name === sensor);
        const lastPacket = sensorData[sensorData.length - 1];
        const lastSeen = luxon.DateTime.fromISO(lastPacket.received_at).toRelative();
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><span class="status-dot"></span> Online</td>
            <td style="font-family: monospace; color: var(--accent);">${sensor}</td>
            <td>${lastSeen}</td>
            <td>-112 dBm / 5.2</td>
            <td><div class="progress" style="height: 6px; width: 60px; background: #333;"><div class="progress-bar bg-success" style="width: 85%"></div></div></td>
            <td>
                <button class="btn btn-sm btn-outline-light"><i class="bi bi-three-dots"></i></button>
            </td>
        `;
        tbody.appendChild(tr);
        
        // Also populate selects
        const option = new Option(sensor, sensor);
        document.getElementById('quick-sensor-select').add(option.cloneNode(true));
        document.getElementById('downlink-device').add(option);
    });
}

// --- Charting ---
function initChart(data) {
  const ctx = document.getElementById('main-chart').getContext('2d');
  
  // Prepare defaults (last 24h of all sensors)
  // For demo, just plotting distribution over time
  // Group by hour
  
  const dataset = {
    label: 'Trames Reçues',
    data: data.map(d => ({x: d.received_at, y: 1})), // Simplified density
    borderColor: '#5e6ad2',
    backgroundColor: 'rgba(94, 106, 210, 0.1)',
    borderWidth: 2,
    tension: 0.4,
    pointRadius: 0
  };

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: { datasets: [dataset] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          type: 'time',
          grid: { color: '#2a2a35' },
          ticks: { color: '#8d8d99' }
        },
        y: {
          grid: { color: '#2a2a35' },
          ticks: { color: '#8d8d99' },
          display: false // minimalistic
        }
      }
    }
  });
}

// --- Console Logic ---
function addConsoleLog(type, message) {
    const container = document.getElementById('live-logs');
    const div = document.createElement('div');
    div.className = `log-entry ${type}`;
    const time = new Date().toLocaleTimeString();
    div.innerText = `[${time}] ${message}`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function sendDownlink() {
    const dev = document.getElementById('downlink-device').value;
    const pl = document.getElementById('downlink-payload').value;
    
    if(!dev || !pl) return alert("Veuillez remplir les champs");
    
    addConsoleLog('tx', `Envoi Downlink -> ${dev} : ${pl}`);
    // Ici appeler votre API réelle plus tard
}

// --- Tools ---
function showAddDeviceModal() {
    alert("Fonctionnalité à venir : Formulaire d'ajout");
}