function decodeUplink(input) {
  return {
    data: Decode(input)
  };
}

function datalog(i, bytes) {
  var aa = (bytes[0 + i] & 0x08) ? "PART" : "SUM";
  var bb = (bytes[0 + i] & 0x04) ? "1" : "0";
  var cc = (bytes[0 + i] & 0x02) ? "1" : "0";
  var dd = (bytes[0 + i] & 0x01) ? "1" : "0";
  var ee = (bytes[1 + i] << 16 | bytes[2 + i] << 8 | bytes[3 + i]).toString(10);
  var ff = (bytes[4 + i] << 16 | bytes[5 + i] << 8 | bytes[6 + i]).toString(10);
  var gg = getMyDate((bytes[7 + i] << 24 | bytes[8 + i] << 16 | bytes[9 + i] << 8 | bytes[10 + i]).toString(10));
  return `[${aa},${bb},${cc},${dd},${ee},${ff},${gg}],`;
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

  var c_Year = c_Date.getFullYear(),
    c_Month = c_Date.getMonth() + 1,
    c_Day = c_Date.getDate(),
    c_Hour = c_Date.getHours(),
    c_Min = c_Date.getMinutes(),
    c_Sen = c_Date.getSeconds();

  return c_Year + '-' + getzf(c_Month) + '-' + getzf(c_Day) + ' ' +
         getzf(c_Hour) + ':' + getzf(c_Min) + ':' + getzf(c_Sen);
}

function Decode(input) {
  const bytes = input.bytes;
  const port = input.fPort;
  let decoded = {};

  if (port === 3) {
    decoded.pnack = ((bytes[0] >> 7) & 0x01) ? "1" : "0";
    decoded.Node_type = "DS03A-LB";
    decoded.data_sum = "";

    for (let i = 0; i < bytes.length; i += 11) {
      decoded.data_sum += datalog(i, bytes);
    }
    return decoded;
  }

  if (port === 4) {
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
    decoded.sensor = (bytes[0] === 0x1B) ? "DS03A-LB" : "Unknown";
    decoded.sub_band = (bytes[4] === 0xff) ? "NULL" : bytes[4];
    decoded.freq_band_map = {
      0x01: "EU868", 0x02: "US915", 0x03: "IN865", 0x04: "AU915",
      0x05: "KZ865", 0x06: "RU864", 0x07: "AS923", 0x08: "AS923_1",
      0x09: "AS923_2", 0x0A: "AS923_3", 0x0B: "CN470", 0x0C: "EU433",
      0x0D: "KR920", 0x0E: "MA869"
    };
    decoded.freq_band = freq_band_map[bytes[3]] || "UNKNOWN";

    decoded.firm_ver = (bytes[1] & 0x0f) + '.' + ((bytes[2] >> 4) & 0x0f) + '.' + (bytes[2] & 0x0f);
    decoded.bat = (bytes[5] << 8 | bytes[6]) / 1000;

    return decoded;
  }

  // Default case
  decoded.count_mod = (bytes[0] & 0x08) ? "PART" : "SUM";
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
    decoded.alarm1 = (bytes[0] & 0x02) ? "1" : "0";
    decoded.door1_open_status = (bytes[0] & 0x01) ? "1" : "0";
    decoded.open1_times = (bytes[1] << 16) | (bytes[2] << 8) | bytes[3];
    decoded.open1_duration = (bytes[4] << 16) | (bytes[5] << 8) | bytes[6];
    decoded.alarm2 = (bytes[11] & 0x02) ? "1" : "0";
    decoded.door2_open_status = (bytes[11] & 0x01) ? "1" : "0";
    decoded.open2_times = (bytes[12] << 16) | (bytes[13] << 8) | bytes[14];
    decoded.open2_duration = (bytes[15] << 16) | (bytes[16] << 8) | bytes[17];
    decoded.Node_type = "DS03A-LB";
    decoded.data_time = getMyDate(((bytes[7] << 24) | (bytes[8] << 16) | (bytes[9] << 8) | bytes[10]).toString(10));


    return decoded;
  }

  return decoded; // fallback
}

module.exports = { Decode };
