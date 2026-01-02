function decodeUplink(input) {
    return {
        data: Decode(input.fPort, input.bytes, input.variables)
    };
}

function datalog(i, bytes) {
    var aa = (bytes[0 + i] & 0x08) ? "PART" : "SUM";
    var bb = (bytes[0 + i] & 0x04) ? "1" : "0";
    var cc = (bytes[0 + i] & 0x02) ? "1" : "0";
    var dd = (bytes[0 + i] & 0x01) ? "1" : "0";
    var ee = (bytes[1 + i] << 16 | bytes[2 + i] << 8 | bytes[3 + i]);
    var ff = (bytes[4 + i] << 16 | bytes[5 + i] << 8 | bytes[6 + i]);
    var gg = getMyDate((bytes[7 + i] << 24 | bytes[8 + i] << 16 | bytes[9 + i] << 8 | bytes[10 + i]).toString(10));

    return {
        CMOD: aa,
        TDC: bb,
        ALARM: cc,
        WATER_LEAK_STATUS: dd,
        WATER_LEAK_TIMES: ee,
        LAST_WATER_LEAK_DURATION: ff,
        TIME: gg
    };
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

    return Y + "-" + getzf(M) + "-" + getzf(D) + " " +
        getzf(h) + ":" + getzf(m) + ":" + getzf(s);
}

function Decode(input) {
    bytes = input.bytes;  
    fPort = input.fPort;
    let decoded = {};
    fPort = 5;
    if (fPort === 0x03) {
        let dataArr = [];
        for (let i = 0; i < bytes.length; i += 11) {
            dataArr.push(datalog(i, bytes));
        }
        decoded.Node_type = "LWL04";
        decoded.DATALOG = dataArr;
        decoded.PNACKMD = ((bytes[0] >> 7) & 0x01) ? "1" : "0";
        return decoded;
    }

    if (fPort === 0x04) {
        decoded.Node_type = "LWL04";
        decoded.TDC = (bytes[0] << 16) | (bytes[1] << 8) | bytes[2];
        decoded.DISALARM = bytes[3] & 0x01;
        decoded.KEEP_STATUS = bytes[4] & 0x01;
        decoded.KEEP_TIME = (bytes[5] << 8) | bytes[6];
        decoded.LEAK_ALARM_TIME = bytes[7];
        return decoded;
    }

    if (fPort === 0x05) {
        let sub_band, freq_band, sensor;
        if (bytes[0] === 0x36) sensor = "LWL04";
        sub_band = (bytes[4] === 0xff) ? "NULL" : bytes[4];

        const bandMap = {
            0x01: "EU868", 0x02: "US915", 0x03: "IN865", 0x04: "AU915",
            0x05: "KZ865", 0x06: "RU864", 0x07: "AS923", 0x08: "AS923_1",
            0x09: "AS923_2", 0x0A: "AS923_3", 0x0B: "CN470", 0x0C: "EU433",
            0x0D: "KR920", 0x0E: "MA869"
        };

        freq_band = bandMap[bytes[3]] || "UNKNOWN";
        let firm_ver = (bytes[1] & 0x0f) + "." + ((bytes[2] >> 4) & 0x0f) + "." + (bytes[2] & 0x0f);
        let bat = ((bytes[5] << 8) | bytes[6]) / 1000;

        decoded.SENSOR_MODEL = sensor;
        decoded.FIRMWARE_VERSION = firm_ver;
        decoded.FREQUENCY_BAND = freq_band;
        decoded.SUB_BAND = sub_band;
        decoded.BAT = bat;
        return decoded;
    }

    // Default case = standard uplink
    decoded.Node_type = "LWL04";
    decoded.CMOD = (bytes[0] & 0x08) ? "PART" : "SUM";
    decoded.TDC = (bytes[0] & 0x04) ? "1" : "0";
    decoded.ALARM = (bytes[0] & 0x02) ? "1" : "0";
    decoded.WATER_LEAK_STATUS = (bytes[0] & 0x01) ? "1" : "0";
    decoded.WATER_LEAK_TIMES = (bytes[1] << 16) | (bytes[2] << 8) | bytes[3];
    decoded.LAST_WATER_LEAK_DURATION = (bytes[4] << 16) | (bytes[5] << 8) | bytes[6];
    decoded.TIME = getMyDate(((bytes[7] << 24) | (bytes[8] << 16) | (bytes[9] << 8) | bytes[10]).toString(10));

    return decoded;
}

module.exports = { Decode };
