function decodeUplink(input) {
  return { 
    data: Decode(input.fPort, input.bytes)
  };   
}

function Str1(str2) {
  var str3 = "";
  for (var i = 0; i < str2.length; i++) {
    if (str2[i] <= 0x0f) {
      str2[i] = "0" + str2[i].toString(16);
    }
    str3 += str2[i].toString(16);
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
  var bb = parseFloat(((bytes[0 + i] << 24 >> 16 | bytes[1 + i]) / 10).toFixed(2));
  var cc = parseFloat(((bytes[2 + i] << 24 >> 16 | bytes[3 + i]) / 10).toFixed(2));
  var dd = parseFloat(((bytes[4 + i] << 24 >> 16 | bytes[5 + i]) / 10).toFixed(2));
  var ee = getMyDate((bytes[7 + i] << 24 | bytes[8 + i] << 16 | bytes[9 + i] << 8 | bytes[10 + i]).toString(10));
  return `[${bb},${cc},${dd},${ee}],`;
}

function getzf(c_num) { 
  return (parseInt(c_num) < 10) ? "0" + c_num : c_num; 
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

  return Y + "-" + getzf(M) + "-" + getzf(D) + " " + getzf(h) + ":" + getzf(m) + ":" + getzf(s);
}
function fromHexString(hex) {
  return hex.match(/.{1,2}/g).map(b => parseInt(b, 16));
}

function dumpBytes(bytes) {
  let dump = "";
  for (let i = 0; i < bytes.length; i++) {
    dump += "[" + i + "]=" + bytes[i] + "(0x" + bytes[i].toString(16).padStart(2,"0") + ") ";
  }
  console.log("Payload dump:", dump);
}

function Decode(input) {
    bytes = input.bytes;
    port = input.fPort;
    let decoded = {};
    //port = 2;
    if (port === 2) {
        let value = (bytes[0] << 8) | bytes[1];
   
        decoded.Bat = value / 1000; // V

        value = (bytes[2] << 8) | bytes[3];
    if (bytes[2] & 0x80) {
            value |= 0xFFFF0000;
    }
    decoded.TempC_DS18B20 = (value / 10).toFixed(2);

    value = (bytes[4] << 8) | bytes[5];
    decoded.Leaf_Moisture = (value / 10).toFixed(2);

    value = (bytes[6] << 8) | bytes[7];
    if ((value & 0x8000) >> 15 === 0) {
        decoded.Leaf_Temperature = (value / 10).toFixed(2);
    } else {
        decoded.Leaf_Temperature = ((value - 0xFFFF) / 10).toFixed(2);
    }

    decoded.Interrupt_flag = bytes[8];
    decoded.Message_type = bytes[10];
    decoded.Node_type = "LMS01-LB";

    return decoded;
    }

    if (port === 3) {
        let data_sum = "";
    for (let i = 0; i < bytes.length; i += 11) {
        data_sum += datalog(i, bytes);
    }
    decoded.Node_type = "LMS01-LB";
    decoded.DATALOG = data_sum;
    decoded.PNACKMD = ((bytes[6] >> 7) & 0x01) ? "True" : "False";

    return decoded;
    }

    if (port === 5) {
        let sensor = (bytes[0] === 0x2D) ? "LMS01-LB" : "Unknown";
        let sub_band = (bytes[4] === 0xff) ? "NULL" : bytes[4];

        let freq_band_map = {
            0x01: "EU868", 0x02: "US915", 0x03: "IN865", 0x04: "AU915",
            0x05: "KZ865", 0x06: "RU864", 0x07: "AS923", 0x08: "AS923_1",
            0x09: "AS923_2", 0x0A: "AS923_3", 0x0B: "CN470", 0x0C: "EU433",
            0x0D: "KR920", 0x0E: "MA869"
        };

        decoded.SENSOR_MODEL = sensor;
        decoded.FIRMWARE_VERSION = (bytes[1] & 0x0f) + "." + ((bytes[2] >> 4) & 0x0f) + "." + (bytes[2] & 0x0f);
        decoded.FREQUENCY_BAND = freq_band_map[bytes[3]] || "UNKNOWN";
        decoded.SUB_BAND = sub_band;
        decoded.BAT = ((bytes[5] << 8) | bytes[6]) / 1000;

        return decoded;
    }

    return decoded;
    }

module.exports = {
    Decode
};