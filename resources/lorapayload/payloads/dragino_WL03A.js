function decodeUplink(input) {
  return {
    data: Decode(input.fPort, input.bytes, input.variables)
  };
}

function datalog(i, bytes) {
  return {
    CMOD: (bytes[0 + i] & 0x08) ? "PART" : "SUM",
    TDC: (bytes[0 + i] & 0x04) ? "YES" : "NO",
    ALARM: (bytes[0 + i] & 0x02) ? "TRUE" : "FALSE",
    WATER_LEAK_STATUS: (bytes[0 + i] & 0x01) ? "LEAK" : "NO LEAK",
    WATER_LEAK_TIMES: (bytes[1 + i] << 16) | (bytes[2 + i] << 8) | bytes[3 + i],
    LAST_WATER_LEAK_DURATION: (bytes[4 + i] << 16) | (bytes[5 + i] << 8) | bytes[6 + i],
    TIME: getMyDate(((bytes[7 + i] << 24) | (bytes[8 + i] << 16) | (bytes[9 + i] << 8) | bytes[10 + i]).toString(10))
  };
}

function getzf(c_num) {
  return parseInt(c_num) < 10 ? "0" + c_num : c_num;
}

function getMyDate(str) {
  var c_Date = (str > 9999999999)
    ? new Date(parseInt(str))
    : new Date(parseInt(str) * 1000);

  var Y = c_Date.getFullYear(),
      M = c_Date.getMonth() + 1,
      D = c_Date.getDate(),
      h = c_Date.getHours(),
      m = c_Date.getMinutes(),
      s = c_Date.getSeconds();

  return Y + "-" + getzf(M) + "-" + getzf(D) + " " +
         getzf(h) + ":" + getzf(m) + ":" + getzf(s);
}

function Decode(input) {
  bytes = input.bytes;  
  fPort = input.fPort;
  let decoded = {};

  if (fPort === 0x03) {
    decoded.Node_type = "WL03A-LB";
    decoded.PNACKMD = ((bytes[0] >> 7) & 0x01) ? "True" : "False";
    let logs = [];
    for (let i = 0; i < bytes.length; i += 11) {
      logs.push(datalog(i, bytes));
    }
    decoded.DATALOG = logs;
    return decoded;
  }

  if (fPort === 0x04) {
    decoded.Node_type = "WL03A-LB";
    decoded.TDC = (bytes[0] << 16) | (bytes[1] << 8) | bytes[2];
    decoded.DISALARM = bytes[3] & 0x01;
    decoded.KEEP_STATUS = bytes[4] & 0x01;
    decoded.KEEP_TIME = (bytes[5] << 8) | bytes[6];
    decoded.LEAK_ALARM_TIME = bytes[7];
    return decoded;
  }

  if (fPort === 0x05) {
    decoded.SENSOR_MODEL = (bytes[0] === 0x1D) ? "WL03A-LB" : "UNKNOWN";
    decoded.FIRMWARE_VERSION =
      (bytes[1] & 0x0f) + "." + ((bytes[2] >> 4) & 0x0f) + "." + (bytes[2] & 0x0f);

    const bandMap = {
      0x01: "EU868", 0x02: "US915", 0x03: "IN865", 0x04: "AU915",
      0x05: "KZ865", 0x06: "RU864", 0x07: "AS923", 0x08: "AS923_1",
      0x09: "AS923_2", 0x0A: "AS923_3", 0x0B: "CN470", 0x0C: "EU433",
      0x0D: "KR920", 0x0E: "MA869"
    };
    decoded.FREQUENCY_BAND = bandMap[bytes[3]] || "UNKNOWN";
    decoded.SUB_BAND = (bytes[4] === 0xff) ? "NULL" : bytes[4];
    decoded.BAT = ((bytes[5] << 8) | bytes[6]) / 1000;
    return decoded;
  }

  // Default uplink
  if (bytes.length === 11) {
    decoded.Node_type = "WL03A-LB";
    decoded.CMOD = (bytes[0] & 0x08) ? "PART" : "SUM";
    decoded.TDC = (bytes[0] & 0x04) ? "YES" : "NO";
    decoded.ALARM = (bytes[0] & 0x02) ? "TRUE" : "FALSE";
    decoded.WATER_LEAK_STATUS = (bytes[0] & 0x01) ? "LEAK" : "NO LEAK";
    decoded.WATER_LEAK_TIMES = (bytes[1] << 16) | (bytes[2] << 8) | bytes[3];
    decoded.LAST_WATER_LEAK_DURATION = (bytes[4] << 16) | (bytes[5] << 8) | bytes[6];
    decoded.TIME = getMyDate(((bytes[7] << 24) | (bytes[8] << 16) |
                              (bytes[9] << 8) | bytes[10]).toString(10));
    return decoded;
  }

  return { Error: "Unknown fPort or payload format" };
}

module.exports = { Decode };