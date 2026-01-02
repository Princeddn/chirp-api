/**
 * Decoder for Dragino MDS120-LB
 */
function decodeUplink(input) {
    return {
        data: Decode(input.fPort, input.bytes, input.variables)
    };
}

/* ----------------- Helpers ----------------- */
function getzf(num) {
    return (parseInt(num) < 10) ? "0" + num : num;
}

function getMyDate(str) {
    let c_Date = (str > 9999999999)
        ? new Date(parseInt(str))
        : new Date(parseInt(str) * 1000);

    let Y = c_Date.getFullYear(),
        M = c_Date.getMonth() + 1,
        D = c_Date.getDate(),
        h = c_Date.getHours(),
        m = c_Date.getMinutes(),
        s = c_Date.getSeconds();

    return `${Y}-${getzf(M)}-${getzf(D)} ${getzf(h)}:${getzf(m)}:${getzf(s)}`;
}

function datalog(i, bytes) {
    let aa = (bytes[0 + i] << 8 | bytes[1 + i]) / 1000;   // Battery V
    let bb = (bytes[2 + i] << 8 | bytes[3 + i]);          // Value 1
    let cc = (bytes[4 + i] << 8 | bytes[5 + i]);          // Value 2
    let dd = ((bytes[6 + i] >> 1) & 0x01) ? "1" : "0"; // Leak flag
    let ee = (bytes[6 + i] & 0x40) ? "1" : "0";           // Extra flag
    let ff = getMyDate(
        (bytes[7 + i] << 24 | bytes[8 + i] << 16 | bytes[9 + i] << 8 | bytes[10 + i]).toString(10)
    );

    return {
        Bat: aa,
        Value1: bb,
        Value2: cc,
        LeakFlag: dd,
        ExtraFlag: ee,
        Time: ff
    };
}

/* ----------------- Main Decode ----------------- */
function Decode(input) {
    bytes = input.bytes;
    fPort = input.fPort;
    let decoded = {};
    decoded.Node_type = "MDS120-LB";

    if (fPort === 2) {
        let value = (bytes[0] << 8 | bytes[1]);
        decoded.Bat = value / 1000;

        let distance = (bytes[2] << 8 | bytes[3]);
        decoded.Distance = (distance === 0x3FFF) ? "Invalid Reading" : distance;

        decoded.Interrupt_flag = bytes[4] & 0x01;

        value = (bytes[5] << 8) | bytes[6];
        if (bytes[5] & 0x80) value |= 0xFFFF0000;
        decoded.TempC_DS18B20 = (value / 10).toFixed(2);

        decoded.Sensor_flag = bytes[7] & 0x01;
    }

    else if (fPort === 3) {
        let dataArr = [];
        for (let i = 0; i < bytes.length; i += 11) {
            dataArr.push(datalog(i, bytes));
        }
        decoded.DATALOG = dataArr;
        decoded.PNACKMD = ((bytes[0] >> 7) & 0x01) ? "1" : "0";
    }

    else if (fPort === 4) {
        decoded.TDC = (bytes[0] << 16) | (bytes[1] << 8) | bytes[2];
        decoded.Stop_Timer = bytes[4];
        decoded.Alarm_Timer = (bytes[5] << 8) | bytes[6];
    }

    else if (fPort === 5) {
        decoded.SENSOR_MODEL = (bytes[0] === 0x2A) ? "MDS120-LB" : "Unknown";
        decoded.SUB_BAND = (bytes[4] === 0xFF) ? "NULL" : bytes[4];

        const bandMap = {
            0x01: "EU868", 0x02: "US915", 0x03: "IN865", 0x04: "AU915",
            0x05: "KZ865", 0x06: "RU864", 0x07: "AS923", 0x08: "AS923_1",
            0x09: "AS923_2", 0x0A: "AS923_3", 0x0B: "CN470", 0x0C: "EU433",
            0x0D: "KR920", 0x0E: "MA869"
        };
        decoded.FREQUENCY_BAND = bandMap[bytes[3]] || "UNKNOWN";

        decoded.FIRMWARE_VERSION =
            (bytes[1] & 0x0f) + "." +
            ((bytes[2] >> 4) & 0x0f) + "." +
            (bytes[2] & 0x0f);

        decoded.BAT = ((bytes[5] << 8) | bytes[6]) / 1000;
    }

    return decoded;
}

module.exports = { Decode };
