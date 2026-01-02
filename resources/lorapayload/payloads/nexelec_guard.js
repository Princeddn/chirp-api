function Decode(input) {
    var stringHex = bytesString(input.bytes);

    var octetTypeProduit = parseInt(stringHex.substring(0, 2), 16);
    var octetTypeMessage = parseInt(stringHex.substring(2, 4), 16);

    // ---------------- Utils ----------------
    function bytesString(input) {
        return input.map(b => b.toString(16).padStart(2, "0")).join("");
    }

    function typeOfProduct(octet) {
        const map = {
            0xB1: "Origin+ LoRa",
            0xB2: "Origin LoRa",
            0xB3: "Guard+ LoRa",
            0xB4: "Guard LoRa",
            0xBD: "Origin+ LoRa/Sigfox"
        };
        return map[octet] || "Unknown";
    }

    function typeOfMessage(octet) {
        return ["Product Status", "Product Configuration", "Smoke Alarm", "Air Quality"][octet] || "Unknown";
    }

    // ---------------- Helpers ----------------
    function temperature(raw) {
        if (raw == 1023) return null;
        if (raw == 1022) return null;
        return (raw * 0.1 - 30) ;
    }

    function humidity(raw) {
        if (raw == 255) return null;
        return (raw * 0.5);
    }

    function batteryVoltage(raw) {
        return (raw * 5) + 2000;
    }

    function productLifetime(raw) {
        return raw;
    }

    function period(raw) {
        return raw * 10;
    }

    function periodWeek(raw) {
        return raw;
    }

    // ---------------- Parsers ----------------
    function productStatusDataOutput(hex) {
        return {
            typeOfProduct: typeOfProduct(octetTypeProduit),
            typeOfMessage: typeOfMessage(octetTypeMessage),
            hwVersion: parseInt(hex.substring(4, 6), 16),
            swVersion: parseInt(hex.substring(6, 8), 16) * 0.1,
            lifetime: productLifetime(parseInt(hex.substring(8, 10), 16)),
            smokeSensorStatus: ((parseInt(hex.substring(10, 11), 16) >> 3) & 0x01) ? "0" : "1",
            tempHumSensorStatus: ((parseInt(hex.substring(10, 11), 16) >> 2) & 0x01) ? "0" : "1",
            batteryLevel: ["High", "Medium", "Low", "Critical"][parseInt(hex.substring(11, 12), 16) & 0x03],
            batteryVoltage: batteryVoltage(parseInt(hex.substring(12, 14), 16))
        };
    }

    function productConfigurationDataOutput(hex) {
        return {
            typeOfProduct: typeOfProduct(octetTypeProduit),
            typeOfMessage: typeOfMessage(octetTypeMessage),
            reconfigurationSource: ["NFC", "Downlink", "Start up", "Reserved", "Reserved", "Local"][(parseInt(hex.substring(4, 5), 16) >> 1) & 0x07],
            reconfigurationStatus: ["Total Success", "Partial Success", "Total Fail", "Reserved"][(parseInt(hex.substring(4, 6), 16) >> 3) & 0x03],
            datalogEnable: ((parseInt(hex.substring(5, 6), 16) >> 2) & 0x01) ? "1" : "0",
            dailyAirEnable: ((parseInt(hex.substring(5, 6), 16) >> 1) & 0x01) ? "1" : "0",
            pendingJoin: (parseInt(hex.substring(6, 7), 16) >> 3) & 0x01,
            nfcStatus: ((parseInt(hex.substring(6, 7), 16) >> 1) & 0x03) ? "0" : "1",
            loraRegion: ["EU868", "Reserved", "Reserved", "Reserved"][((parseInt(hex.substring(6, 8), 16) >> 1) & 0x0F)] || "Unknown"
        };
    }

    function smokeAlarmDataOutput(hex) {
        return {
            typeOfProduct: typeOfProduct(octetTypeProduit),
            typeOfMessage: typeOfMessage(octetTypeMessage),
            smokeAlarm: ["Non-activated", "Local Alarm", "Remote Alarm"][(parseInt(hex.substring(4, 5), 16) >> 2) & 0x03],
            smokeAlarmHush: ["Stopped (no smoke)", "Stopped by button", "Stopped remotely"][(parseInt(hex.substring(4, 5), 16)) & 0x03],
            smokeLocalProductTest: ["Off", "Local test", "Remote test"][(parseInt(hex.substring(5, 6), 16) >> 2) & 0x03],
            timeSinceLastTest: periodWeek((parseInt(hex.substring(5, 8), 16) >> 2) & 0xFF),
            digitalMaintenanceCertificate: ((parseInt(hex.substring(7, 8), 16) >> 1) & 0x01) ? "1" : "0",
            timeSinceLastMaintenance: periodWeek((parseInt(hex.substring(7, 10), 16) >> 1) & 0xFF),
            temperature: temperature((parseInt(hex.substring(9, 13), 16) >> 3) & 0x3FF),
            humidity: humidity(parseInt(hex.substring(13, 15), 16) & 0xFF)
        };
    }

    function dailyAirDataOutput(hex) {
        return {
            typeOfProduct: typeOfProduct(octetTypeProduit),
            typeOfMessage: typeOfMessage(octetTypeMessage),
            temperatureMin: temperature((parseInt(hex.substring(4, 7), 16) >> 2) & 0x3FF),
            temperatureMax: temperature(parseInt(hex.substring(6, 9), 16) & 0x3FF),
            temperatureAvg: temperature((parseInt(hex.substring(9, 12), 16) >> 2) & 0x3FF),
            humidityMin: humidity((parseInt(hex.substring(11, 14), 16) >> 2) & 0xFF),
            humidityMax: humidity((parseInt(hex.substring(13, 16), 16) >> 2) & 0xFF),
            humidityAvg: humidity((parseInt(hex.substring(15, 18), 16) >> 2) & 0xFF)
        };
    }


    // ---------------- Dispatcher ----------------
    const parsers = [
        productStatusDataOutput,
        productConfigurationDataOutput,
        smokeAlarmDataOutput,
        dailyAirDataOutput
    ];

    let decoded = parsers[octetTypeMessage] ? parsers[octetTypeMessage](stringHex) : { error: "Unsupported message type" };
    return { data: decoded };
}


module.exports = { Decode };
