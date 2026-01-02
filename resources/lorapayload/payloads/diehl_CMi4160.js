// https://cdn.store-factory.com/www.compteur-energie.com/media/Diehl_module-lorawan-pour-sharky_notice_compteur-energie-2021.pdf

function Decode(input) {
    var bytes = input.bytes;
    var fPort = input.fPort;
    var pos = 0;
    var decoded = {};
  
    function readUIntLE(n) {
      let val = 0;
      for (let i = 0; i < n; i++) {
        val |= bytes[pos++] << (8 * i);
      }
      return val;
    }
  
    function readIntLE(n) {
      let val = readUIntLE(n);
      const max = 1 << (n * 8);
      const half = max >> 1;
      return val >= half ? val - max : val;
    }
  
    function decodeTimestamp(bytes) {
      if (bytes.length < 6) return null;
      const val = bytes.reduce((acc, b, i) => acc + (b << (8 * i)), 0);
      const year = ((val >> 28) & 0x0F) * 10 + ((val >> 21) & 0x07) + 2000;
      const month = (val >> 24) & 0x0F;
      const day = (val >> 16) & 0x1F;
      const hour = (val >> 8) & 0x1F;
      const minute = val & 0x3F;
      return `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')} ${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
    }
  
    const formatId = bytes[pos++];
    decoded.messageFormat = formatId;
  
    switch(formatId) {
      case 0x1E:
        decoded.type = "Standard";
        decoded.energyWh = readUIntLE(6);
        decoded.volumeM3 = readUIntLE(6) / 1000;
        decoded.powerKW = readIntLE(4) / 1000;
        decoded.flowM3h = readIntLE(4) / 1000;
        decoded.forwardTempC = readIntLE(4) / 10;
        decoded.returnTempC = readIntLE(4) / 10;
        decoded.meterAddress = bytes.slice(pos, pos + 10).map(b => b.toString(16).padStart(2, '0')).join('');
        pos += 10;
        decoded.errorFlags = bytes.slice(pos, pos + 4).map(b => b.toString(16).padStart(2, '0')).join('');
        break;
  
      case 0x1F:
        decoded.type = "Compact";
        decoded.energyWh = readUIntLE(6);
        decoded.meterAddress = bytes.slice(pos, pos + 10).map(b => b.toString(16)).join('');
        pos += 10;
        decoded.errorFlags = bytes.slice(pos, pos + 4).map(b => b.toString(16)).join('');
        break;
  
      case 0x20:
        decoded.type = "JSON";
        try {
          const jsonStr = String.fromCharCode(...bytes.slice(pos));
          Object.assign(decoded, JSON.parse(jsonStr));
        } catch {
          decoded.error = "Invalid JSON format";
        }
        break;
  
      case 0x21:
        decoded.type = "Scheduled-daily";
        decoded.energyWh = readUIntLE(6);
        decoded.volumeM3 = readUIntLE(6) / 1000;
        decoded.meterAddress = bytes.slice(pos, pos + 10).map(b => b.toString(16)).join('');
        pos += 10;
        decoded.errorFlags = bytes.slice(pos, pos + 4).map(b => b.toString(16)).join('');
        pos += 4;
        decoded.timestamp = decodeTimestamp(bytes.slice(pos, pos + 6));
        pos += 6;
        decoded.energy24hWh = readUIntLE(6);
        break;
  
      case 0x22:
        decoded.type = "Scheduled-extended";
        decoded.energyWh = readUIntLE(6);
        decoded.volumeM3 = readUIntLE(6) / 1000;
        decoded.powerKW = readIntLE(2) / 1000;
        decoded.flowM3h = readIntLE(2) / 1000;
        decoded.forwardTempC = readIntLE(2) / 100;
        decoded.returnTempC = readIntLE(2) / 100;
        decoded.meterAddress = bytes.slice(pos, pos + 10).map(b => b.toString(16)).join('');
        pos += 10;
        decoded.errorFlags = bytes.slice(pos, pos + 4).map(b => b.toString(16)).join('');
        pos += 4;
        decoded.timestamp = decodeTimestamp(bytes.slice(pos, pos + 6));
        break;
  
      case 0x23:
        decoded.type = "Combined heat/cooling";
        decoded.heatEnergyWh = readUIntLE(6);
        decoded.coolingEnergyWh = readUIntLE(8);
        decoded.volumeM3 = readUIntLE(6) / 1000;
        decoded.forwardTempC = readIntLE(4) / 10;
        decoded.returnTempC = readIntLE(4) / 10;
        decoded.meterAddress = bytes.slice(pos, pos + 10).map(b => b.toString(16)).join('');
        pos += 10;
        decoded.errorFlags = bytes.slice(pos, pos + 4).map(b => b.toString(16)).join('');
        break;
  
      default:
        decoded.error = "Unknown format ID";
        break;
    }
  
    return decoded;
  }
  
  module.exports = { Decode };