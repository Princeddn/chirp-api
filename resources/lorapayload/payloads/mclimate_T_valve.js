/*
https://docs.mclimate.eu/mclimate-lorawan-devices/devices/mclimate-t-valve-lorawan/decoding-and-bacnet-object-mapping/t-valve-uplink-decoder
Supports both short (2 bytes) and long (5+ bytes) packet formats
*/

function Decode(input) {
    var bytes = input.bytes;
    var data = {};

    if (!bytes || bytes.length < 2) {
        return data;
    }

    // Short packet format (2 bytes) - Keepalive
    if (bytes.length === 2) {
        data.reason = "keepalive";

        // Byte 0: Water temperature
        data.waterTemp = (bytes[0] & 0xFF) / 2;

        // Byte 1: Valve state (bit 7) + Ambient temperature (bits 6-0)
        data.valveState = ((bytes[1] >> 7) & 0x01) === 1;
        data.ambientTemp = ((bytes[1] & 0x7F) - 20) / 2;

        return data;
    }

    // Long packet format (5+ bytes)
    if (bytes.length >= 5) {
        // Byte 0: [7:5] Reason, [3] Box tamper, [2] Wire status, [1] Flood, [0] Magnet
        var byte0 = bytes[0];
        var reason = (byte0 >> 5) & 0x07;
        var reasonTexts = [
            'keepalive',
            'testButtonPressed',
            'floodDetected',
            'controlButtonPressed',
            'fraudDetected',
            'fraudDetected',
            'fraudDetected',
            'fraudDetected'
        ];
        data.reason = reasonTexts[reason];
        data.boxTamper = ((byte0 >> 3) & 0x01) === 1;
        data.floodDetectionWireState = ((byte0 >> 2) & 0x01) === 0; // 0 = working, 1 = not working
        data.flood = ((byte0 >> 1) & 0x01) === 1;
        data.magnet = (byte0 & 0x01) === 1;

        // Byte 1: [7] Alarm verified, [6] Manual open, [5] Manual close, [4:0] Firmware version
        var byte1 = bytes[1];
        data.alarmValidated = ((byte1 >> 7) & 0x01) === 1;
        data.manualOpenIndicator = ((byte1 >> 6) & 0x01) === 1;
        data.manualCloseIndicator = ((byte1 >> 5) & 0x01) === 1;
        data.softwareVersion = byte1 & 0x1F;

        // Byte 2: Close time in minutes
        data.closeTime = bytes[2];

        // Byte 3: Open time in minutes
        data.openTime = bytes[3];

        // Byte 4: Battery voltage = byte4 * 8 + 1600 (mV), converted to V
        data.battery = (bytes[4] * 8 + 1600) / 1000;

        // Handle extended responses (more than 5 bytes)
        if (bytes.length > 5) {
            handleResponse(bytes.slice(0, -5), data);
        }
    }

    return data;
}

function handleResponse(responseBytes, data) {
    var i = 0;

    while (i < responseBytes.length) {
        var command = responseBytes[i];

        switch (command) {
            case 0x0e: // Opening/closing time extended
                if (i + 4 < responseBytes.length) {
                    var openTimeHi = responseBytes[i + 1];
                    var openTimeLo = responseBytes[i + 2];
                    var closeTimeHi = responseBytes[i + 3];
                    var closeTimeLo = responseBytes[i + 4];
                    data.openCloseTimeExtended = {
                        open: (openTimeHi << 8) | openTimeLo,
                        close: (closeTimeHi << 8) | closeTimeLo
                    };
                    i += 5;
                } else {
                    i++;
                }
                break;

            case 0x0f: // Emergency openings
                if (i + 1 < responseBytes.length) {
                    data.emergencyOpenings = responseBytes[i + 1];
                    i += 2;
                } else {
                    i++;
                }
                break;

            case 0x10: // Flood alarm time
                if (i + 1 < responseBytes.length) {
                    data.floodAlarmTime = responseBytes[i + 1];
                    i += 2;
                } else {
                    i++;
                }
                break;

            case 0x11: // Working voltage
                if (i + 1 < responseBytes.length) {
                    data.workingVoltage = responseBytes[i + 1];
                    i += 2;
                } else {
                    i++;
                }
                break;

            case 0x12: // Keep-alive time
                if (i + 1 < responseBytes.length) {
                    data.keepAliveTime = responseBytes[i + 1];
                    i += 2;
                } else {
                    i++;
                }
                break;

            case 0x13: // Device flood sensor
                if (i + 1 < responseBytes.length) {
                    data.deviceFloodSensor = responseBytes[i + 1];
                    i += 2;
                } else {
                    i++;
                }
                break;

            case 0x16: // Join retry period
                if (i + 1 < responseBytes.length) {
                    var periodValue = responseBytes[i + 1];
                    data.joinRetryPeriod = (periodValue * 5) / 60; // Convert to minutes
                    i += 2;
                } else {
                    i++;
                }
                break;

            case 0x18: // Uplink type
                if (i + 1 < responseBytes.length) {
                    data.uplinkType = responseBytes[i + 1];
                    i += 2;
                } else {
                    i++;
                }
                break;

            case 0x1a: // Watchdog parameters
                if (i + 2 < responseBytes.length) {
                    var wdpC = responseBytes[i + 1] === 0 ? false : responseBytes[i + 1];
                    var wdpUc = responseBytes[i + 2] === 0 ? false : responseBytes[i + 2];
                    data.watchDogParams = { 'wdpC': wdpC, 'wdpUc': wdpUc };
                    i += 3;
                } else {
                    i++;
                }
                break;

            case 0xa0: // FUOTA address
                if (i + 4 < responseBytes.length) {
                    data.fuotaAddress = (responseBytes[i + 1] << 24) |
                                       (responseBytes[i + 2] << 16) |
                                       (responseBytes[i + 3] << 8) |
                                       responseBytes[i + 4];
                    i += 5;
                } else {
                    i++;
                }
                break;

            default:
                i++;
                break;
        }
    }

    return data;
}

module.exports = {
    Decode
};
