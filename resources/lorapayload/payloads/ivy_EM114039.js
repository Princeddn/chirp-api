/**
 * Payload Decoder
 *
 * @product IVY METERING EM114039-01
 * IoT Energy Meter - LoRaWAN Smart Power Meter
 *
 * 解码上行链路数据(Decoding uplink data)
 * 该函数负责解析从设备接收到的字节流数据，并将其转换为有意义的信息(This function is responsible for parsing the byte stream data received from the device and converting it into meaningful information)
 * 主要解析包括版本号、地址、序列号、电能数据、功率数据、电压、电流、功率因数、频率和继电器状态(The main analysis includes version number, address, serial number, energy data, power data, voltage, current, power factor, frequency and relay status)
 */

// 工具函数：从指定位置读取2字节无符号整数(Utility function: Read a 2-byte unsigned integer from the specified position)
function getUint16_BE(bytes, offset) { // big-endian
  return (bytes[offset] << 8) | bytes[offset + 1];
}
function getUint32_BE(bytes, offset) {
  return (
    (bytes[offset] << 24) |
    (bytes[offset + 1] << 16) |
    (bytes[offset + 2] << 8) |
    (bytes[offset + 3])
  ) >>> 0;
}

function Decode(input) {
  const bytes = input.bytes || [];
  const decode = {};

  // Longueur réelle de ta trame: 39 octets
  if (bytes.length < 39) {
    decode.error = "Data length too short";
    return decode;
  }

  // Version (octets 3..4)
  const versionNum = getUint16_BE(bytes, 3); // 0x03F2 = 1010 -> "1.0.10"
  const v1 = Math.floor(versionNum / 1000);
  const v2 = Math.floor((versionNum % 1000) / 100);
  const v3 = Math.floor((versionNum % 100) / 10);
  const v4 = versionNum % 10;
  decode.version = `${v1}.${v2}.${v3}${v4}`;

  // Adresse (5..6)
  decode.address = getUint16_BE(bytes, 5);

  // S/N (7..10)
  decode.serialNumber = Array.from(bytes.slice(7, 11))
    .map(b => ("0" + b.toString(16)).slice(-2))
    .join("");

  // Énergies (11..18, 19..22 etc.) – dans TA trame, c'est 0
  decode.positiveActiveEnergy = getUint32_BE(bytes, 11) / 100;   // kWh
  decode.reverseActiveEnergy  = getUint32_BE(bytes, 15) / 100;   // kWh
  decode.reactiveEnergy       = getUint32_BE(bytes, 19) / 100;   // kvarh

  // Puissances (23..24, 25..26) – ta trame=0
  decode.activePower   = getUint16_BE(bytes, 23); // W (si échelle 1)
  decode.reactivePower = getUint16_BE(bytes, 25); // var

  // >>> Tension (27..28) big-endian, échelle /100
  decode.voltage = getUint16_BE(bytes, 27) / 100; // -> 237.91 V

  // Courant (29..30) – ta trame=0
  decode.current = getUint16_BE(bytes, 29) / 100; // A

  // Facteur de puissance (31..32) – ta trame=0
  decode.powerFactor = getUint16_BE(bytes, 31) / 1000;

  // Fréquence (33..34) – échelle /100
  decode.frequency = getUint16_BE(bytes, 33) / 100; // -> 49.96 Hz

  // Relais (35..36)
  const relayWord = getUint16_BE(bytes, 35);
  const relayOn = (relayWord & 0x0001) === 0x0001;      // bit0
  const relayFault = (relayWord & 0x0002) === 0x0002;   // bit1

  decode.relay_switch = relayOn ? "1" : "0";         // => "on"/"off"
  decode.relay_fault = relayFault;                      // boolean
  decode.relay_health = relayFault ? "malfunction" : "normal";

  return decode;
}

/**
 * ============================================================================
 * ENCODER SECTION
 * ============================================================================
 */

/**
 * Encodeur du compteur LoRaWAN IVY METERING EM114039-01
 * Compatible TTN / ChirpStack / Jeedom (lorapayload)
 *
 * @param {Object} payload - Paramètres à encoder
 * @returns {Array} bytes - Tableau de bytes à envoyer
 */
function Encode(payload) {
    return ivyMeteringEncode(payload);
}

function ivyMeteringEncode(payload) {
    // Helper pour calculer le CRC16 Modbus
    function crc16(buffer) {
        var crc = 0xFFFF;
        for (var i = 0; i < buffer.length; i++) {
            crc ^= buffer[i];
            for (var j = 0; j < 8; j++) {
                if (crc & 0x0001) crc = (crc >> 1) ^ 0xA001;
                else crc >>= 1;
            }
        }
        return crc;           
    }

    // Construction du payload
    var bytes = [];

    // Par défaut, l'adresse esclave est 0x01
    var slaveAddr = 0x01;

    // Check if payload is valid
    if (!payload || typeof payload !== 'object') {
        throw new Error("Invalid payload: expected object, got " + typeof payload);
    }

    // Traitement des commandes
    if ("relay_on" in payload) {
        // Function 0x06 (écrire un registre unique)
        bytes = [slaveAddr, 0x06, 0x00, 0x10, 0x00, 0x01]; // 0010 = relais, 0001 = fermé
    }
    else if ("relay_off" in payload) {
        bytes = [slaveAddr, 0x06, 0x00, 0x10, 0x00, 0x00]; // 0000 = ouvert
    }
    else if ("set_interval" in payload) {
        var interval = parseInt(payload.set_interval);
        if (isNaN(interval) || interval < 1 || interval > 1440) {
            throw new Error("L'intervalle doit être compris entre 1 et 1440 minutes");
        }
        // Function 0x06 pour modifier le registre 0x0034 (data report interval)
        bytes = [slaveAddr, 0x06, 0x00, 0x34, (interval >> 8) & 0xFF, interval & 0xFF];
    }
    else if ("read_relay_status" in payload) {
        // Function 0x03 (lire registre) - Registre 0x0010 (relay status), 1 registre
        bytes = [slaveAddr, 0x03, 0x00, 0x10, 0x00, 0x02];
    }
    else if ("read_all_registers" in payload) {
        // Function 0x03 (lire registres) - Depuis 0x0000, lire 53 registres (0x35)
        // Couvre: version, adresse, S/N, énergies, puissances, tension, courant, PF, fréquence, relay, etc.
        bytes = [slaveAddr, 0x03, 0x00, 0x00, 0x00, 0x35];
    }
    else {
        throw new Error("Commande invalide : utilisez relay_on, relay_off, set_interval, read_relay_status ou read_all_registers");
    }

    // Calcul CRC16 (low byte first)
    var crc = crc16(bytes);
    bytes.push(crc & 0xFF);         // Low byte
    bytes.push((crc >> 8) & 0xFF);  // High byte

    return bytes;
}

module.exports = {
    Decode,
    Encode
};
