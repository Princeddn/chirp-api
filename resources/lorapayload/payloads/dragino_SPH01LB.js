function decodeUplink(input) {
    return {
        data: Decode(input.fPort, input.bytes, input.variables)
    };
}

function Decode(input) {
    bytes = input.bytes;
    fPort = input.fPort;
    let decoded = {};

    if (fPort === 0x02) {
        let value;

        // Batterie
        value = (bytes[0] << 8 | bytes[1]) & 0x3FFF;
        decoded.Bat = value / 1000;

        // Température DS18B20
        value = (bytes[2] << 8) | bytes[3];
        if (bytes[2] & 0x80) {
            value |= 0xFFFF0000;
        }
        decoded.TempC_DS18B20 = (value / 10).toFixed(2);

        // pH
        value = (bytes[4] << 8) | bytes[5];
        decoded.PH1_SOIL = (value / 100).toFixed(2);

        // Température sol
        value = (bytes[6] << 8) | bytes[7];
        if ((value & 0x8000) >> 15 === 0) {
            decoded.TEMP_SOIL = (value / 10).toFixed(2);
        } else {
            decoded.TEMP_SOIL = ((value - 0xFFFF) / 10).toFixed(2);
        }

        // Flags
        decoded.Interrupt_flag = bytes[8];
        decoded.Message_type = bytes[10];

        decoded.Node_type = "SPH01-LB";
        return decoded;
    }

    if (fPort === 0x03) {
        let dataArr = [];
        for (let i = 0; i < bytes.length; i += 11) {
            dataArr.push(datalog(i, bytes));
        }
        decoded.Node_type = "SPH01-LB";
        decoded.DATALOG = dataArr;
        return decoded;
    }

    if (fPort === 0x05) {
        let sub_band, freq_band, sensor;

        if (bytes[0] === 0x2C) sensor = "SPH01-LB";
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

    return { error: "Unsupported fPort" };
}

/* -------------------- HELPERS -------------------- */
function datalog(i, bytes) {
    let aa = (bytes[0 + i] << 8 | bytes[1 + i]) / 10;
    let bb = (bytes[2 + i] << 8 | bytes[3 + i]) / 10;
    let cc = (bytes[4 + i] << 8 | bytes[5 + i]) / 10;
    let dd = bytes[6 + i];
    let ee = getMyDate((bytes[7 + i] << 24 | bytes[8 + i] << 16 | bytes[9 + i] << 8 | bytes[10 + i]).toString(10));

    return {
        PH: aa,
        Temperature: bb,
        DS18B20_Temperature: cc,
        s_flag: dd,
        time: ee
    };
}

function getzf(c_num) {
    return (parseInt(c_num) < 10) ? "0" + c_num : c_num;
}

function getMyDate(str) {
    let c_Date;
    if (str > 9999999999) c_Date = new Date(parseInt(str));
    else c_Date = new Date(parseInt(str) * 1000);

    let Y = c_Date.getFullYear(),
        M = c_Date.getMonth() + 1,
        D = c_Date.getDate(),
        h = c_Date.getHours(),
        m = c_Date.getMinutes(),
        s = c_Date.getSeconds();

    return Y + "-" + getzf(M) + "-" + getzf(D) + " " +
        getzf(h) + ":" + getzf(m) + ":" + getzf(s);
}

module.exports = { Decode };
