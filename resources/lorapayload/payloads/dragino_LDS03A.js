function decodeUplink(input) {
  return {
    data: Decode(input)
  };
}

function datalog(i, bytes) {
  var aa = (bytes[0 + i] & 0x02) ? "1" : "0"; // alarm
  var bb = (bytes[0 + i] & 0x01) ? "1" : "0"; // door status
  var cc = (bytes[0 + i] & 0x04) ? "1" : "0"; // TDC
  var dd = (bytes[1 + i] << 16 | bytes[2 + i] << 8 | bytes[3 + i]).toString(10);
  var ee = (bytes[4 + i] << 16 | bytes[5 + i] << 8 | bytes[6 + i]).toString(10);
  var ff = getMyDate((bytes[7 + i] << 24 | bytes[8 + i] << 16 | bytes[9 + i] << 8 | bytes[10 + i]).toString(10));
  return `[${aa},${bb},${cc},${dd},${ee},${ff}],`;
}

function getzf(c_num) {
  return (parseInt(c_num) < 10) ? '0' + c_num : c_num;
}

function getMyDate(str) {
  var c_Date;
  if (str > 9999999999)
    c_Date = new Date(parseInt(str));
  else
    c_Date = new Date(parseInt(str) * 1000);

  var Y = c_Date.getFullYear(),
    M = c_Date.getMonth() + 1,
    D = c_Date.getDate(),
    h = c_Date.getHours(),
    m = c_Date.getMinutes(),
    s = c_Date.getSeconds();

  return Y + '-' + getzf(M) + '-' + getzf(D) + ' ' +
         getzf(h) + ':' + getzf(m) + ':' + getzf(s);
}

function Decode(input) {
  const bytes = input.bytes;
  const port = input.fPort;
  let decoded = {};
  if (port === 2) {
    decoded.Node_type = "LDS03A";
    decoded.alarm = (bytes[0] & 0x02) ? "1" : "0";
    decoded.door_status = (bytes[0] & 0x01) ? "1" : "0";
    decoded.total_open_times = (bytes[1] << 16) | (bytes[2] << 8) | bytes[3];
    decoded.last_open_duration = (bytes[4] << 16) | (bytes[5] << 8) | bytes[6];
    decoded.data_time = getMyDate(((bytes[7] << 24) | (bytes[8] << 16) | (bytes[9] << 8) | bytes[10]).toString(10));

    return decoded;
  }

  if (port === 3) {
    decoded.Node_type = "LDS03A";
    decoded.data_sum = "";

    for (let i = 0; i < bytes.length; i += 11) {
      decoded.data_sum += datalog(i, bytes);
    }

    return decoded;
  }

  if (port === 4) {
    decoded.Node_type = "LDS03A";
    decoded.TDC = (bytes[0] << 16) | (bytes[1] << 8) | bytes[2];
    decoded.disalarm = bytes[3] & 0x01;
    decoded.keep_status1 = bytes[4] & 0x01;
    decoded.keep_time1 = (bytes[5] << 8) | bytes[6];
    decoded.keep_status2 = bytes[7] & 0x01;
    decoded.keep_time2 = (bytes[8] << 8) | bytes[9];
    decoded.alarm_tdc = bytes[10];

    return decoded;
  }

  if (port === 5) {
    const freq_band_map = {
      0x01: "EU868", 0x02: "US915", 0x03: "IN865", 0x04: "AU915",
      0x05: "KZ865", 0x06: "RU864", 0x07: "AS923", 0x08: "AS923_1",
      0x09: "AS923_2", 0x0A: "AS923_3", 0x0B: "CN470", 0x0C: "EU433",
      0x0D: "KR920", 0x0E: "MA869"
    };

    decoded.Node_type = "LDS03A";
    decoded.sensor = (bytes[0] === 0x0A) ? "LDS03A" : "Unknown";
    decoded.sub_band = (bytes[4] === 0xff) ? "NULL" : bytes[4];
    decoded.freq_band = freq_band_map[bytes[3]] || "UNKNOWN";
    decoded.firm_ver = (bytes[1] & 0x0f) + '.' + ((bytes[2] >> 4) & 0x0f) + '.' + (bytes[2] & 0x0f);
    decoded.bat = ((bytes[5] << 8) | bytes[6]) / 1000;

    return decoded;
  }

  // Default case (doors)
  decoded.Node_type = "LDS03A";
  decoded.tdc_interval = (bytes[0] & 0x04) ? "1" : "0";
  decoded.alarm1 = (bytes[0] & 0x02) ? "1" : "0";
  decoded.door1_open_status = (bytes[0] & 0x01) ? "1" : "0";
  decoded.open1_times = (bytes[1] << 16) | (bytes[2] << 8) | bytes[3];
  decoded.open1_duration = (bytes[4] << 16) | (bytes[5] << 8) | bytes[6];
  decoded.data_time = getMyDate(((bytes[7] << 24) | (bytes[8] << 16) | (bytes[9] << 8) | bytes[10]).toString(10));

  if (bytes.length === 11) {
    return decoded;
  }

  if (bytes.length === 18) {
    decoded.alarm2 = (bytes[11] & 0x02) ? "1" : "0";
    decoded.door2_open_status = (bytes[11] & 0x01) ? "1" : "0";
    decoded.open2_times = (bytes[12] << 16) | (bytes[13] << 8) | bytes[14];
    decoded.open2_duration = (bytes[15] << 16) | (bytes[16] << 8) | bytes[17];
    decoded.alarm1 = (bytes[0] & 0x02) ? "1" : "0";
    decoded.door1_open_status = (bytes[0] & 0x01) ? "1" : "0";
    decoded.open1_times = (bytes[1] << 16) | (bytes[2] << 8) | bytes[3];
    decoded.open1_duration = (bytes[4] << 16) | (bytes[5] << 8) | bytes[6];

    return decoded;
  }

  return decoded; // fallback si aucune condition
}

module.exports = { Decode };
