/*
 * Codec for RAK10701 in Jeedom LoRaPayload plugin
 * Single-argument Decode(input), exported as Decode for compatibility.
 * Persists history to disk to compute historical min/max and best/worst values.
 */

var Jeedom = require('../jeedom/jeedom.js');
const fs   = require('fs');
const path = require('path');

// --- Configuration persistance ---
const HISTORY_FILE = path.join(__dirname, 'rak10701_history.json');
const MAX_HISTORY  = 500;
const CSV_FILE     = path.join(__dirname, 'rak10701.csv');

// En-tête CSV (mêmes colonnes que dans le codec exemple)
const CSV_HEADER = [
  'Date',
  'Latitude',
  'Longitude',
  'Gateway',
  'SF',
  'SNR',
  'RSSI',
  'Distance'
].join(',') + '\n';


// Charge l’historique depuis le fichier, ou vide si pas présent
function loadHistory() {
  try {
    return JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf8'));
  } catch {
    return [];
  }
}

// Sauve l’historique (truncation à MAX_HISTORY)
function saveHistory(history) {
  const toSave = history.slice(-MAX_HISTORY);
  fs.writeFileSync(HISTORY_FILE, JSON.stringify(toSave), 'utf8');
}

// Calcule la distance (km) entre deux points GPS
function distance(lat1, lon1, lat2, lon2) {
  if (lat1 === lat2 && lon1 === lon2) return 0;
  const rad = Math.PI / 180;
  const rlat1 = lat1 * rad, rlat2 = lat2 * rad;
  const dlon = (lon1 - lon2) * rad;
  let d = Math.sin(rlat1) * Math.sin(rlat2)
        + Math.cos(rlat1) * Math.cos(rlat2) * Math.cos(dlon);
  d = Math.min(d, 1);
  d = Math.acos(d) / rad;
  return d * 60 * 1.1515 * 1.609344;
}

// Formatte un timestamp en "DD-MM-YYYY HH:mm:ss"
function formatDate(ts) {
  const d = new Date(ts);
  const pad = n => String(n).padStart(2, '0');
  const DD = pad(d.getDate());
  const MM = pad(d.getMonth() + 1);
  const YYYY = d.getFullYear();
  const hh = pad(d.getHours());
  const mm = pad(d.getMinutes());
  const ss = pad(d.getSeconds());
  return `${DD}-${MM}-${YYYY} ${hh}:${mm}:${ss}`;
}

// Assure que le fichier CSV existe avec son en-tête
// Assure que le fichier CSV existe et contient l'en‐tête
function ensureCsvHeader() {
  try {
    const stats = fs.statSync(CSV_FILE);
    // Si le fichier existe mais est vide (taille = 0), on réécrit l'en‐tête
    if (stats.size === 0) {
      fs.writeFileSync(CSV_FILE, CSV_HEADER, 'utf8');
    }
  } catch (err) {
    // Si le fichier n'existe pas, écrit simplement l'en‐tête
    if (err.code === 'ENOENT') {
      fs.writeFileSync(CSV_FILE, CSV_HEADER, 'utf8');
    } else {
      throw err;
    }
  }
}


// Ajoute une ligne au fichier CSV (tableau de valeurs qui doit correspondre à l’ordre de CSV_HEADER)
function appendCsvLine(fields) {
  const line = fields.map(f => (f != null ? f : '')).join(',') + '\n';
  fs.appendFileSync(CSV_FILE, line, 'utf8');
}


function parseRxInfo(str) {
  // 1) on quote d'abord toutes les clés
  let s = str.replace(
    /([{,]\s*)([A-Za-z0-9_]+)\s*:/g,
    '$1"$2":'
  );

  // 2) on remplace TOUT ce qui suit ':' jusqu'à ',' ou '}', puis on décide
  s = s.replace(
    /:([^,}\]]+)(?=[,}])/g,
    (_m, raw) => {
      const val = raw.trim();
      // nombre pur ?
      if (/^-?\d+(\.\d+)?$/.test(val)) {
        return ':' + val;
      }
      // objet ou tableau ?
      if (val[0] === '{' || val[0] === '[') {
        return ':' + val;
      }
      // sinon c'est une chaîne (hex, UUID, date…)
      return ':"' + val + '"';
    }
  );

  return JSON.parse(s);
}

function decode(input) {
  input = input || {};

  // 1) Charger l'historique persistant
  const history = loadHistory();
  ensureCsvHeader();

  // 2) Extraire metadata
  let fPort = parseInt(input.fPort, 10) || 1;
  const bytes = Array.isArray(input.bytes)
    ? input.bytes
    : Array.from(input.bytes || []);

  // 4) Décodage des données GPS (port 1)
  const decoded = {};
  if (fPort === 1) {
    const lonSign = (bytes[0] & 0x80) ? -1 : 1;
    const latSign = (bytes[0] & 0x40) ? -1 : 1;
    const encLat  = ((bytes[0] & 0x3f) << 17)
                  | (bytes[1] << 9)
                  | (bytes[2] << 1)
                  | (bytes[3] >> 7);
    const encLon  = ((bytes[3] & 0x7f) << 16)
                  | (bytes[4] << 8)
                  |  bytes[5];
    const hdop = bytes[8] / 10;
    const sats = bytes[9];

    decoded.latitude  = latSign * (encLat * 108 + 53)  / 1e7;
    decoded.longitude = lonSign * (encLon * 215 + 107) / 1e7;
    decoded.altitude  = ((bytes[6] << 8) + bytes[7]) - 1000;
    decoded.accuracy  = (hdop * 5 + 5) / 10;
    decoded.hdop      = hdop;
    decoded.sats      = sats;
    decoded.location  = `(${decoded.latitude},${decoded.longitude})`;
    if (hdop >= 2 || sats < 5) {
      decoded.error = `GPS precision too low (hdop=${hdop}, sats=${sats})`;
    }
  }
  // 5) Construction de la liste de passerelles
  let gwList = [];

  if (typeof input.rxInfo === 'string') {
    const parsed = parseRxInfo(input.rxInfo);

    if (Array.isArray(parsed)) {
      // Cas où la string est directement un tableau JSON
      gwList = parsed;
    } else if (parsed && Array.isArray(parsed.rxInfo)) {
      // Cas { rxInfo: [...] }
      gwList = parsed.rxInfo;
    } else {
      console.log('rxInfo parsé dans un format inattendu :', parsed);
      gwList = [];
    }

  } else if (Array.isArray(input.rxInfo)) {
    gwList = input.rxInfo;
  } else if (input.rxInfo && Array.isArray(input.rxInfo.rxInfo)) {
    // Cas où Jeedom / LNS t’envoie déjà un objet { rxInfo: [...] }
    gwList = input.rxInfo.rxInfo;
  } else {
    console.log('input.rxInfo dans un format inattendu :', input.rxInfo);
    gwList = [];
  }




  // 6) Initialisation des stats unifiées
  decoded.rssi     = 0;
  decoded.loRaSNR      = 0;
  decoded.DR =0;
  decoded.distance = 0;
  decoded.SF = 0;
  
  if (!Array.isArray(gwList)) {
    console.log('gwList N’EST PAS un tableau :', gwList);
    gwList = [];
  }
  // 5) Pour chaque gateway : calculs et stockage dans l’historique
  gwList.forEach(gw => {
    // a) extraire les valeurs
    const ts   = Date.now();
    const date = formatDate(ts);  
    const time      = Date.now();
    const id        = gw.gatewayID;
    const name      = gw.name || null;
    const rssi      = parseInt(gw.rssi, 10);
    const snr       = parseFloat(gw.loRaSNR);
    const lat_gw    = gw.location?.latitude;
    const lon_gw    = gw.location?.longitude;
    // b) calcul distance (en mètres) si coords dispos
    let dist_m = null;
    if (
      typeof decoded.latitude  === 'number' &&
      typeof decoded.longitude === 'number' &&
      typeof lat_gw === 'number' &&
      typeof lon_gw === 'number'
    ) {
      dist_m = parseInt(distance(decoded.latitude, decoded.longitude, lat_gw, lon_gw) * 1000);
    }

      decoded.rssi = rssi ;
      decoded.loRaSNR = snr ;
        // 9) Quantification distance
      decoded.mod      = Math.max(1, Math.floor(dist_m / 250));
      decoded.distance = decoded.mod * 250;
      decoded.DR = parseInt(input.DR);
      if (decoded.DR === 5) {
        decoded.SF = 7;
      } else if (decoded.DR === 4) {
        decoded.SF = 8;
      } else if (decoded.DR === 3) {
        decoded.SF = 9;
      } else if (decoded.DR === 2) {
        decoded.SF = 10;
      } else if (decoded.DR === 1) {
        decoded.SF = 11;
      } else if (decoded.DR === 0) {
        decoded.SF = 12;
      }                  
//      console.log("Mod valeur >>>>>>",decoded.mod)

    // d) stocke dans l’historique une entrée par gateway
    history.push({
      time,
      gatewayID: id,
      name,
      latitude_gateway: lat_gw,
      longitude_gateway: lon_gw ,
      latitude_testeur: decoded.latitude,
      longitude_testeur: decoded.longitude ,
      rssi,
      snr,
      SF : decoded.SF,
      distance: dist_m,
      distanceMod : decoded.mod 
    });
    // Colonnes : Date,Latitude,Longitude,Latitude testeur,Longitude testeur,Gateway,SF,SNR,RSSI
    // 1) Première ligne : on écrit la position de la GATEWAY
    const csvFieldsGateway = [
      date,                                // Date
      lat_gw != null ? lat_gw  : '',       // Latitude = gateway.latitude
      lon_gw != null ? lon_gw  : '',       // Longitude = gateway.longitude
      gw.gatewayID,                        // Gateway (ID)
      decoded.SF != null ? decoded.SF   : '',              // SF
      snr != null ? snr : '',              // SNR
      rssi != null ? rssi : '',             // RSSI
      dist_m
    ];
    appendCsvLine(csvFieldsGateway);

    // 2) Deuxième ligne : on écrit la position du TESTEUR
    //    (on garde les mêmes valeurs SF, SNR, RSSI pour rappel, ou on peut laisser vides)
    const lat_t = decoded.latitude;
    const lon_t = decoded.longitude;

    const csvFieldsTester = [
      date,                                // Date (même timestamp)
      lat_t != null ? lat_t  : '',         // Latitude = testeur.latitude
      lon_t != null ? lon_t  : '',         // Longitude = testeur.longitude
      "Testeur",                        // Gateway (le même ID pour identifier la paire)
      decoded.SF != null ? decoded.SF   : '',              // SF (ou vide si non pertinent ici)
      snr != null ? snr : '',              // SNR (ou vide)
      rssi != null ? rssi : '',             // RSSI (ou vide)
      dist_m
    ];
    appendCsvLine(csvFieldsTester);
  });
  saveHistory(history);

  // --- 11) Calcul statistiques historiques ---
  const rssiValues    = history.map(e => e.rssi).filter(v => typeof v === 'number');
  const snrValues     = history.map(e => e.snr ) .filter(v => typeof v === 'number');
  const distValues    = history.map(e => e.distance);
  const ModValues     = history.map(e => e.distanceMod);
  console.log('Mod Values ', ModValues)

  decoded.histMinRSSI     = rssiValues.length ? Math.min(...rssiValues) : null;
  decoded.histMaxRSSI     = rssiValues.length ? Math.max(...rssiValues) : null;
  decoded.histMinSNR      = snrValues .length ? Math.min(...snrValues ) : null;
  decoded.histMaxSNR      = snrValues .length ? Math.max(...snrValues ) : null;
  decoded.histMinDistance = distValues.length ? Math.min(...distValues) : null;
  decoded.histMaxDistance = distValues.length ? Math.max(...distValues) : null;
  decoded.histMinMod = ModValues.length ? Math.min(...ModValues) : null;
  decoded.histMaxMod = ModValues.length ? Math.max(...ModValues) : null;


  decoded.num_gw    = gwList.length;

  // send downlink
    // --- 13) Génération du downlink automatique ---
  const downBytes = encodePayload({
    MINRSSI: { value: decoded.histMinRSSI ?? decoded.rssi },
    MAXRSSI: { value: decoded.histMaxRSSI ?? decoded.rssi },
    MINMOD:  { value: decoded.histMinMod },
    MAXMOD:  { value: decoded.histMaxMod },
    NUM_GW:  { value: decoded.num_gw }
  }, fPort);
  console.log("Downlink ", downBytes)
  // Base64 pour Jeedom
  decoded.encoded = Buffer.from(downBytes).toString('base64');

  let keyValueArray = {
      'action': 'sendDownlink',
      'eqLogicId' : input.eqLogicId,
      'fport': '2',
      'confirmed': false,
      'payload': decoded.encoded
  };

  Jeedom.com.config(input.apikey,input.callback,1)
  Jeedom.com.send_change_immediate(keyValueArray)
  return { data: decoded };
}

// Encoder downlink (format interne)
function encodePayload(meas, port) {
  const buf = [];
  buf[0] = 1;
  buf[1] = meas.MINRSSI.value + 200;
  buf[2] = meas.MAXRSSI.value + 200;
  buf[3] = meas.MINMOD.value  || 1;
  buf[4] = meas.MAXMOD.value  || 1;
  buf[5] = meas.NUM_GW.value;
  return buf;
}

// Wrapper pour Encode (appelé depuis lorapayloadEncoder.js)
function Encode(input) {
  // Si input contient les propriétés directement (ex: input.MINRSSI)
  // on les transforme au format attendu par encodePayload
  const meas = {
    MINRSSI: { value: input.MINRSSI || -120 },
    MAXRSSI: { value: input.MAXRSSI || -30 },
    MINMOD:  { value: input.MINMOD || 1 },
    MAXMOD:  { value: input.MAXMOD || 1 },
    NUM_GW:  { value: input.NUM_GW || 1 }
  };

  return encodePayload(meas, input.fPort);
}

// Exports
module.exports = {
  Decode: decode,
  decode,
  Encode: Encode,
  encode: encodePayload
};
