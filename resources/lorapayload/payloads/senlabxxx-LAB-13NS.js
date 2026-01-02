/**
 * UNIVERSAL SENLAB DECODER - Rev S
 * FPorts: 3 (data), 4 (start message)
 */

// Chirpstack v4
function decodeUplink(input) {
  var decoded = senlabDeviceDecode(input.bytes, input.fPort);
  return { data: decoded };
}

// Chirpstack v3
function Decode(input) {
  bytes = input.bytes;
  fport = input.fPort || input.fport || 3;
  return senlabDeviceDecode(bytes, fport);
}

function senlabDeviceDecode(bytes, fport) {
  var decoded = {};

  if (!bytes || bytes.length < 2) {
    decoded.error = "Payload invalide";
    return decoded;
  }

  // Convertir fport en nombre si c'est une chaîne
  if (typeof fport === 'string') {
    fport = parseInt(fport, 10);
  }

  // Par défaut, port 3 pour les données
  if (!fport || isNaN(fport) || fport === '') {
    fport = 3;
  }

  var id = bytes[0];
  var battery = bytes[1];

  // Gestion des valeurs spéciales de batterie Senlab
  if (battery === 0xFE) {
    decoded.battery = 99; // 0xFE = valeur spéciale 99%
  } else if (battery === 0xEB) {
    decoded.battery = 92; // 0xEB = valeur spéciale 92%
  } else {
    // Senlab utilise une échelle 0-254 pour représenter 0-100%
    decoded.battery = Math.round((battery / 254) * 100 * 10) / 10;
  }
  decoded.fport = fport;

  // === Table de correspondance APP_TYPE ===
  var appTypeMap = {
    0x02: "Senlab D",
    0x41: "Senlab A",
    0x44: "Senlab D",
    0x48: "Senlab H",
    0x4D: "Senlab M",
    0x4F: "Senlab O",
    0x50: "Senlab P",
    0x54: "Senlab T",
    0x56: "Senlab V"
  };

  // ================== FPORT 1 (non géré) ==================
  if (fport === 1) {
    decoded.message = "FPort 1 - Pas de decodage specifique disponible";
    return decoded;
  }

  // ================== DOWNLINK ACK (FPort 2) ==================
  if (fport === 2) {
    decoded.frame = "Downlink ACK";

    if (id === 0x81) {
      decoded.ack_type = "Configuration ACK";
      decoded.message = "Commande de configuration confirmee";
    } else if (id === 0x85) {
      decoded.ack_type = "Status Response";
      decoded.message = "Reponse de statut du capteur";
    } else {
      decoded.ack_type = "Unknown ACK";
      decoded.message = "ACK de type inconnu (0x" + id.toString(16).toUpperCase() + ")";
    }

    return decoded;
  }

  // ================== START MESSAGE (FPort 4) ==================
  if (fport === 4) {
    decoded.frame = "Uplink START MESSAGE";

    var appType = bytes[10];
    decoded.app_type_hex = "0x" + appType.toString(16).toUpperCase();
    decoded.device_type = appTypeMap[appType] || "Inconnu";

    var version_major = bytes[11];
    var version_minor = bytes[12];
    var version_rev = bytes[13];
    decoded.firmware = version_major + "." + version_minor + "." + version_rev;

    var functional_mode = bytes[14];
    decoded.functional_mode = functional_mode === 0x01 ? "basic/datalog" : "other";

    var logPeriod = (bytes[15] << 8) + bytes[16];
    var txPeriod = (bytes[17] << 8) + bytes[18];
    decoded.log_period_s = logPeriod * 2;
    decoded.tx_period_s = txPeriod * 2;

    if (bytes.length >= 23) {
      var randWindow = (bytes[19] << 8) + bytes[20];
      var redundancy = bytes[21];
      decoded.random_window_s = randWindow;
      decoded.redundancy_factor = redundancy;
    }

    return decoded;
  }

  // ================== BASIC DATA (FPort 3) ==================
  if (fport === 3) {
    switch (id) {
      case 0x00: // Senlab A
        decoded.type = "Senlab A (courant)";
        decoded.current_mA = parseFloat((((bytes[bytes.length - 2] << 8) + bytes[bytes.length - 1]) / 200).toFixed(3));
        break;

      case 0x01: // Senlab T simple
        decoded.type = "Senlab T (température)";
        var tempRaw = (bytes[bytes.length - 2] << 8) + bytes[bytes.length - 1];

        // Gestion des codes d'erreur
        if (tempRaw === 0x8000) {
          decoded.temp_error = "no_temperature_probe";
          decoded.temp_C = null;
        } else if (tempRaw === 0x8001) {
          decoded.temp_error = "unknown_error";
          decoded.temp_C = null;
        } else if (tempRaw === 0x8002 || tempRaw === 0x8003 || tempRaw === 0x8004) {
          decoded.temp_error = "sensor_reading_error - check probe connection";
          decoded.temp_C = null;
        } else {
          decoded.temp_C = parseFloat(((tempRaw >= 0x8000 ? tempRaw - 0x10000 : tempRaw) / 16).toFixed(2));
        }
        break;

      case 0x0C: // Senlab T double
        decoded.type = "Senlab T (double sonde)";
        var blue = (bytes[bytes.length - 4] << 8) + bytes[bytes.length - 3];
        var red = (bytes[bytes.length - 2] << 8) + bytes[bytes.length - 1];

        // Gestion des codes d'erreur pour sonde bleue
        if (blue === 0x8000) {
          decoded.temp_blue_error = "no_temperature_probe";
          decoded.temp_blue_C = null;
        } else if (blue === 0x8001) {
          decoded.temp_blue_error = "unknown_error";
          decoded.temp_blue_C = null;
        } else if (blue === 0x8002 || blue === 0x8003 || blue === 0x8004) {
          decoded.temp_blue_error = "sensor_reading_error - check probe connection";
          decoded.temp_blue_C = null;
        } else {
          decoded.temp_blue_C = parseFloat(((blue >= 0x8000 ? blue - 0x10000 : blue) / 16).toFixed(2));
        }

        // Gestion des codes d'erreur pour sonde rouge
        if (red === 0x8000) {
          decoded.temp_red_error = "no_temperature_probe";
          decoded.temp_red_C = null;
        } else if (red === 0x8001) {
          decoded.temp_red_error = "unknown_error";
          decoded.temp_red_C = null;
        } else if (red === 0x8002 || red === 0x8003 || red === 0x8004) {
          decoded.temp_red_error = "sensor_reading_error - check probe connection";
          decoded.temp_red_C = null;
        } else {
          decoded.temp_red_C = parseFloat(((red >= 0x8000 ? red - 0x10000 : red) / 16).toFixed(2));
        }
        break;

      case 0x03: // Senlab H
        decoded.type = "Senlab H (T° + humidité)";
        var tRaw = (bytes[bytes.length - 3] << 8) + bytes[bytes.length - 2];
        decoded.temp_C = parseFloat(((tRaw >= 0x8000 ? tRaw - 0x10000 : tRaw) / 16).toFixed(2));
        decoded.humidity = bytes[bytes.length - 1];
        break;

      case 0x05: // Senlab D
        decoded.type = "Senlab D (contact)";
        var v = bytes[2];
        decoded.state = (v & 0x80) ? "open" : "closed";
        break;

      case 0x02: // Senlab M/P simple
        decoded.type = "Senlab M/P (compteur)";
        decoded.count = ((bytes[bytes.length - 4] << 24) |
                        (bytes[bytes.length - 3] << 16) |
                        (bytes[bytes.length - 2] << 8) |
                        bytes[bytes.length - 1]) >>> 0;
        break;

      case 0x07: // Senlab M Enhanced
        decoded.type = "Senlab M (enhanced)";
        var status = bytes[2];
        decoded.wirecut_activated = (status & 0x04) !== 0;
        decoded.wirecut_detected = (status & 0x01) !== 0;
        decoded.count = ((bytes[bytes.length - 4] << 24) |
                        (bytes[bytes.length - 3] << 16) |
                        (bytes[bytes.length - 2] << 8) |
                        bytes[bytes.length - 1]) >>> 0;
        break;

      case 0x0A: // Senlab M dual input
        decoded.type = "Senlab M (dual input)";
        var s = bytes[2];
        decoded.wirecut_activated = (s & 0x04) !== 0;
        decoded.input1 = ((bytes[bytes.length - 8] << 24) |
                         (bytes[bytes.length - 7] << 16) |
                         (bytes[bytes.length - 6] << 8) |
                         bytes[bytes.length - 5]) >>> 0;
        decoded.input2 = ((bytes[bytes.length - 4] << 24) |
                         (bytes[bytes.length - 3] << 16) |
                         (bytes[bytes.length - 2] << 8) |
                         bytes[bytes.length - 1]) >>> 0;
        break;

      default:
        decoded.type = "Type inconnu (uplink FPort 3)";
        decoded.raw = bytes.map(function(b) { return b.toString(16).padStart(2, "0"); }).join(" ");
    }
  }

  return decoded;
}

// Chirpstack v4
function encodeDownlink(input) {
  var encoded = senlabDeviceEncode(input.data);
  return { bytes: encoded, fPort: 2 };
}

// Chirpstack v3
function Encode(obj) {
  return senlabDeviceEncode(obj);
}

function senlabDeviceEncode(payload) {
  var encoded = [];

  if ("stop" in payload) {
    encoded = encoded.concat(stopDatalog(payload.stop));
  }
  if ("get_config" in payload) {
    encoded = encoded.concat(getConfig(payload.get_config));
  }
  if ("config" in payload) {
    encoded = encoded.concat(setConfig(payload.config));
  }
  if ("reset_index" in payload) {
    encoded = encoded.concat(resetIndex(payload.reset_index));
  }
  if ("reset_detection" in payload) {
    encoded = encoded.concat(resetDetection(payload.reset_detection));
  }
  if ("reset_battery" in payload) {
    encoded = encoded.concat(resetBattery(payload.reset_battery));
  }
  if ("wirecut_on" in payload) {
    encoded = encoded.concat(wirecutOn(payload.wirecut_on));
  }
  if ("wirecut_off" in payload) {
    encoded = encoded.concat(wirecutOff(payload.wirecut_off));
  }

  return encoded;
}

/**
 * Stop datalog
 * @example { "stop": 1 }
 */
function stopDatalog(value) {
  return [0x01, 0x07, 0x00];
}

/**
 * Get configuration
 * @example { "get_config": 1 }
 */
function getConfig(value) {
  return [0x05];
}

/**
 * Set configuration period
 * @param {string|number} period - "5min", "10min", "15min", "30min", "60min", "2h", "3h", "4h", "12h", "24h" ou index (0-9)
 * @example { "config": "10min" } ou { "config": 1 }
 */
function setConfig(period) {
  var configs = {
    "5min": "0107010100960071020096002609000F",
    "10min": "01070101012C010702012C007109000F",
    "15min": "0107010101C2019D0201C200BC09000F",
    "30min": "010701010384035F020384019D09000F",
    "60min": "01070101070806E3020708035F09000F",
    "2h": "010701010E100DEB020E1006E309000F",
    "3h": "01070101151814F30215180A6709000F",
    "4h": "010701011C201BFB021C200DEB09000F",
    "12h": "010701015460543B0254602A0B09000F",
    "24h": "01070101A8C0A89B02A8C0543B09000F"
  };

  // Mapping des valeurs numériques vers les clés de configuration
  var numericMapping = {
    5: "5min",
    10: "10min",
    15: "15min",
    30: "30min",
    60: "60min",
    120: "2h",
    180: "3h",
    240: "4h",
    720: "12h",
    1440: "24h"
  };

  // Si c'est un nombre, essayer de le mapper
  if (typeof period === "number") {
    // D'abord essayer le mapping direct (5, 10, 15, 30, 60, 120, 180, 240, 720, 1440)
    if (numericMapping[period]) {
      period = numericMapping[period];
    } else {
      // Sinon, essayer comme index de la liste (0-9)
      var periodList = ["5min", "10min", "15min", "30min", "60min", "2h", "3h", "4h", "12h", "24h"];
      if (period >= 0 && period < periodList.length) {
        period = periodList[period];
      } else {
        throw new Error("Valeur invalide: " + period + ". Valeurs acceptées: 5, 10, 15, 30, 60, 120, 180, 240, 720, 1440 (minutes) ou 0-9 (index)");
      }
    }
  }

  var hex = configs[period];
  if (!hex) {
    throw new Error("Période non supportée. Valeurs acceptées: 5min, 10min, 15min, 30min, 60min, 2h, 3h, 4h, 12h, 24h");
  }

  return hex.match(/.{1,2}/g).map(function(b) { return parseInt(b, 16); });
}

/**
 * Reset index (Senlab M)
 * @example { "reset_index": 1 }
 */
function resetIndex(value) {
  return [0x04, 0x02, 0x00, 0x00, 0x00, 0x00];
}

/**
 * Reset detection (Senlab D/P)
 * @example { "reset_detection": 1 }
 */
function resetDetection(value) {
  return [0x04, 0x02, 0x00, 0x00, 0x00, 0x00];
}

/**
 * Reset battery
 * @example { "reset_battery": 1 }
 */
function resetBattery(value) {
  return [0x04, 0x01, 0x00, 0x00, 0x00, 0x00];
}

/**
 * Activate wirecut (Senlab M)
 * @example { "wirecut_on": 1 }
 */
function wirecutOn(value) {
  return [0x01, 0x03, 0x00, 0x00, 0x00, 0x02];
}

/**
 * Deactivate wirecut (Senlab M)
 * @example { "wirecut_off": 1 }
 */
function wirecutOff(value) {
  return [0x01, 0x03, 0x00, 0x02, 0x00, 0x00];
}

module.exports = {
  Decode,
  Encode,
  encodeDownlink
};
