function decodeUplink(input) {
    return {
        data: Decode(input.fPort, input.bytes, input.variables)
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

function Decode(fPort, bytes, variables) {
    let decoded = {};
    let value;
    let mod = (bytes[16] >> 7) & 0x01;

    if (fPort === 0x02) {
        decoded.BatV = ((bytes[0] << 8 | bytes[1]) & 0x3FFF) / 1000;

        value = (bytes[2] << 8) | bytes[3];
        if (bytes[2] & 0x80) {
            value |= 0xFFFF0000;
        }
        decoded.temp_DS18B20 = (value / 10).toFixed(2);

        if (mod === 0) {
            // Canal 1
            value = (bytes[6] << 8) | bytes[7];
            if ((value & 0x8000) >> 15 === 0) {
                decoded.temp_SOIL = (value / 100).toFixed(2);
            } else {
                decoded.temp_SOIL = ((value - 0xFFFF) / 100).toFixed(2);
            }
            decoded.water_SOIL = ((bytes[4] << 8 | bytes[5]) / 100).toFixed(2);
            decoded.conduct_SOIL = (bytes[8] << 8) | bytes[9];

            // Canal 2
            value = (bytes[12] << 8) | bytes[13];
            if ((value & 0x8000) >> 15 === 0) {
                decoded.temp_SOIL2 = (value / 100).toFixed(2);
            } else {
                decoded.temp_SOIL2 = ((value - 0xFFFF) / 100).toFixed(2);
            }
            decoded.water_SOIL2 = ((bytes[10] << 8 | bytes[11]) / 100).toFixed(2);
            decoded.conduct_SOIL2 = (bytes[14] << 8) | bytes[15];
        } else {
            // Mode Raw
            decoded.Soil_dielectric_constant = ((bytes[4] << 8 | bytes[5]) / 10).toFixed(1);
            decoded.Raw_water_SOIL = (bytes[6] << 8) | bytes[7];
            decoded.Raw_conduct_SOIL = (bytes[8] << 8) | bytes[9];

            decoded.Soil_dielectric_constant2 = ((bytes[10] << 8 | bytes[11]) / 10).toFixed(1);
            decoded.Raw_water_SOIL2 = (bytes[12] << 8) | bytes[13];
            decoded.Raw_conduct_SOIL2 = (bytes[14] << 8) | bytes[15];
        }

        decoded.s_flag = (bytes[16] >> 4) & 0x01;
        decoded.i_flag = bytes[16] & 0x0F;
        decoded.Mod = mod;
        decoded.Node_type = "SE02-LB";

        return decoded;
    }

    if (fPort === 0x03) {
        let data_sum = [];
        let pnack = ((bytes[12] >> 7) & 0x01) ? "1" : "0";

        for (let i = 0; i < bytes.length; i += 17) {
            let entry = {
                CH1_Temp: parseFloat(((bytes[0 + i] << 24 >> 16 | bytes[1 + i]) / 100).toFixed(2)),
                CH1_Humi: parseFloat(((bytes[2 + i] << 24 >> 16 | bytes[3 + i]) / 100).toFixed(2)),
                CH1_Cond: (bytes[4 + i] << 8 | bytes[5 + i]),
                CH2_Temp: parseFloat(((bytes[6 + i] << 24 >> 16 | bytes[7 + i]) / 100).toFixed(2)),
                CH2_Humi: parseFloat(((bytes[8 + i] << 24 >> 16 | bytes[9 + i]) / 100).toFixed(2)),
                CH2_Cond: (bytes[10 + i] << 8 | bytes[11 + i]),
                TIME: getMyDate(((bytes[13 + i] << 24) | (bytes[14 + i] << 16) | (bytes[15 + i] << 8) | bytes[16 + i]).toString(10))
            };
            data_sum.push(entry);
        }

        decoded.Node_type = "SE02-LB";
        decoded.DATALOG = data_sum;
        decoded.PNACKMD = pnack;

        return decoded;
    }

    if (fPort === 0x05) {
        let sub_band = (bytes[4] === 0xff) ? "NULL" : bytes[4];
        let sensor = (bytes[0] === 0xF1) ? "SE02-LB" : "UNKNOWN";

        const bandMap = {
            0x01: "EU868", 0x02: "US915", 0x03: "IN865", 0x04: "AU915",
            0x05: "KZ865", 0x06: "RU864", 0x07: "AS923", 0x08: "AS923_1",
            0x09: "AS923_2", 0x0A: "AS923_3", 0x0B: "CN470", 0x0C: "EU433",
            0x0D: "KR920", 0x0E: "MA869"
        };

        decoded.SENSOR_MODEL = sensor;
        decoded.FIRMWARE_VERSION = (bytes[1] & 0x0f) + "." + ((bytes[2] >> 4) & 0x0f) + "." + (bytes[2] & 0x0f);
        decoded.FREQUENCY_BAND = bandMap[bytes[3]] || "UNKNOWN";
        decoded.SUB_BAND = sub_band;
        decoded.BAT = ((bytes[5] << 8) | bytes[6]) / 1000;

        return decoded;
    }

    return decoded; // fallback si aucun port reconnu
}

module.exports = { Decode };
