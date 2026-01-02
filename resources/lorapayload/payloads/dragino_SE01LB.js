function decodeUplink(input) {
  return {
    data: Decode(input.fPort, input.bytes, input.variables)
  };
}

// ---------- Helpers ----------
function Str1(str2) {
  var str3 = "";
  for (var i = 0; i < str2.length; i++) {
    if (str2[i] <= 0x0f) {
      str2[i] = "0" + str2[i].toString(16) + "";
    }
    str3 += str2[i].toString(16) + "";
  }
  return str3;
}

function str_pad(byte) {
  var zero = "00";
  var hex = byte.toString(16);
  var tmp = 2 - hex.length;
  return zero.substr(0, tmp) + hex + " ";
}

function datalog(i, bytes) {
  var bb = parseFloat(((bytes[0 + i] << 24 >> 16 | bytes[1 + i]) / 100).toFixed(2));
  var cc = parseFloat(((bytes[2 + i] << 24 >> 16 | bytes[3 + i]) / 100).toFixed(2));
  var dd = parseFloat((((bytes[4 + i] << 8 | bytes[5 + i]) & 0xFFF) / 10).toFixed(1));
  var ee = getMyDate((bytes[7 + i] << 24 | bytes[8 + i] << 16 | bytes[9 + i] << 8 | bytes[10 + i]).toString(10));
  return { V1: bb, V2: cc, V3: dd, TIME: ee };
}

function getzf(c_num) {
  return parseInt(c_num) < 10 ? "0" + c_num : c_num;
}

function getMyDate(str) {
  var c_Date;
  if (str > 9999999999) c_Date = new Date(parseInt(str));
  else c_Date = new Date(parseInt(str) * 1000);

  var Y = c_Date.getFullYear(),
    M = c_Date.getMonth() + 1,
    D = c_Date.getDate(),
    h = c_Date.getHours(),
    m = c_Date.getMinutes(),
    s = c_Date.getSeconds();

  return Y + "-" + getzf(M) + "-" + getzf(D) + " " +
    getzf(h) + ":" + getzf(m) + ":" + getzf(s);
}

// ---------- Decode ----------
function Decode(input) {
  bytes = input.bytes;
  fPort = input.fPort;
  var decoded = {};

  if (fPort === 0x02) {
    decoded.Node_type = "SE01-LB";

    decoded.BatV = ((bytes[0] << 8 | bytes[1]) & 0x3FFF) / 1000;

    var value = bytes[2] << 8 | bytes[3];
    if (bytes[2] & 0x80) value |= 0xFFFF0000;
    decoded.TempC_DS18B20 = (value / 10).toFixed(2);

    var mod = (bytes[10] >> 7) & 0x01;
    decoded.Mod = mod;

    if (mod === 0) {
      value = bytes[6] << 8 | bytes[7];
      if (((value & 0x8000) >> 15) === 0)
        decoded.Temp_SOIL = (value / 100).toFixed(2);
      else
        decoded.Temp_SOIL = ((value - 0xFFFF) / 100).toFixed(2);

      decoded.Water_SOIL = ((bytes[4] << 8 | bytes[5]) / 100).toFixed(2);
      decoded.Conduct_SOIL = bytes[8] << 8 | bytes[9];
    } else {
      decoded.Soil_dielectric_constant = ((bytes[4] << 8 | bytes[5]) / 10).toFixed(1);
      decoded.Raw_water_SOIL = bytes[6] << 8 | bytes[7];
      decoded.Raw_conduct_SOIL = bytes[8] << 8 | bytes[9];
    }

    decoded.s_flag = (bytes[10] >> 4) & 0x01;
    decoded.i_flag = bytes[10] & 0x0F;

    return decoded;
  }

  if (fPort === 0x03) {
    decoded.Node_type = "SE01-LB";
    decoded.PNACKMD = ((bytes[6] >> 7) & 0x01) ? "True" : "False";

    var dataArr = [];
    for (var i = 0; i < bytes.length; i += 11) {
      dataArr.push(datalog(i, bytes));
    }
    decoded.DATALOG = dataArr;

    return decoded;
  }

  if (fPort === 0x05) {
    decoded.Node_type = "SE01-LB";

    decoded.SENSOR_MODEL = (bytes[0] === 0x26) ? "SE01-LB" : "UNKNOWN";
    decoded.SUB_BAND = (bytes[4] === 0xff) ? "NULL" : bytes[4];

    var bandMap = {
      0x01: "EU868", 0x02: "US915", 0x03: "IN865", 0x04: "AU915",
      0x05: "KZ865", 0x06: "RU864", 0x07: "AS923", 0x08: "AS923_1",
      0x09: "AS923_2", 0x0A: "AS923_3", 0x0B: "CN470", 0x0C: "EU433",
      0x0D: "KR920", 0x0E: "MA869"
    };
    decoded.FREQUENCY_BAND = bandMap[bytes[3]] || "UNKNOWN";

    decoded.FIRMWARE_VERSION = (bytes[1] & 0x0f) + "." + ((bytes[2] >> 4) & 0x0f) + "." + (bytes[2] & 0x0f);
    decoded.BAT = (bytes[5] << 8 | bytes[6]) / 1000;

    return decoded;
  }

  return decoded;
}

module.exports = { Decode};