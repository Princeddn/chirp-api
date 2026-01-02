// https://github.com/dragino/dragino-end-node-decoder/blob/main/LC01/LC01_ChirpstackV4_Decode.txt

function Datalog(bytes, num) {
    var decoded = {};

    decoded.Timestamp = 0;
    decoded.Timestamp |= bytes[num] << 24;
    decoded.Timestamp |= bytes[1 + num] << 16;
    decoded.Timestamp |= bytes[2 + num] << 8;
    decoded.Timestamp |= bytes[3 + num];

    var eventType = bytes[4 + num];
    switch (eventType) {
        case 0x03:
            decoded.Event = "HEARTBEAT_EVENT";
            break;
        case 0x04:
            decoded.Event = "RELAY_ACK_EVENT";
            break;
        default:
            decoded.Event = "ERROR";
    }

    decoded.RelayStatus = (bytes[5 + num] === 0x01) ? "1" :
                          (bytes[5 + num] === 0x00) ? "0" : "0";

    if (bytes[6 + num] & 0x80) {
        decoded.Datalog_Reply = "NO_ACK_REPLY";
    } else if (bytes[6 + num] & 0x40) {
        decoded.Datalog_Reply = "POLL_REPLY";
    }

    return decoded;
}

function Decode(input) {
  bytes = input.bytes
  port = input.fPort
  fPort = 2
    var decoded = {};

    if (fPort === 2) {
        decoded.Timestamp = 0;
        decoded.Timestamp |= bytes[0] << 24;
        decoded.Timestamp |= bytes[1] << 16;
        decoded.Timestamp |= bytes[2] << 8;
        decoded.Timestamp |= bytes[3];

        var eventType = bytes[4];
        switch (eventType) {
            case 0x03:
                decoded.Event = "HEARTBEAT_EVENT";
                break;
            case 0x04:
                decoded.Event = "RELAY_ACK_EVENT";
                break;
            default:
                decoded.Event = "ERROR";
        }
        console.log("Conversion eventtype en valeur Hexa de eventType : " + eventType.toString(16));
        console.log("Valeur décodée de eventType : " + decoded.Event);
        decoded.RelayStatus = (bytes[5] === 0x01) ? "1" :
                              (bytes[5] === 0x00) ? "0" : "0";

        decoded.LoraNode = "LC01";
    }

    else if (fPort === 3) {
        var data = [];
        for (var i = 0; i < bytes.length; i += 7) {
            data.push(Datalog(bytes, i));
        }
        decoded.DataLog = data;
        decoded.LoraNode = "LC01";
    }

    else if (fPort === 5) {
        if (bytes[0] === 0x47) {
            decoded.SENSOR_MODEL = "LC01";
        }

        decoded.FIRMWARE_VERSION = (bytes[1] & 0x0f) + '.' + ((bytes[2] >> 4) & 0x0f) + '.' + (bytes[2] & 0x0f);

        switch (bytes[3]) {
            case 0x01: decoded.FREQUENCY_BAND = "EU868"; break;
            case 0x02: decoded.FREQUENCY_BAND = "US915"; break;
            case 0x03: decoded.FREQUENCY_BAND = "IN865"; break;
            case 0x04: decoded.FREQUENCY_BAND = "AU915"; break;
            case 0x05: decoded.FREQUENCY_BAND = "KZ865"; break;
            case 0x06: decoded.FREQUENCY_BAND = "RU864"; break;
            case 0x07: decoded.FREQUENCY_BAND = "AS923"; break;
            case 0x08: decoded.FREQUENCY_BAND = "AS923_1"; break;
            case 0x09: decoded.FREQUENCY_BAND = "AS923_2"; break;
            case 0x0A: decoded.FREQUENCY_BAND = "AS923_3"; break;
            case 0x0F: decoded.FREQUENCY_BAND = "AS923_4"; break;
            case 0x0B: decoded.FREQUENCY_BAND = "CN470"; break;
            case 0x0C: decoded.FREQUENCY_BAND = "EU433"; break;
            case 0x0D: decoded.FREQUENCY_BAND = "KR920"; break;
            case 0x0E: decoded.FREQUENCY_BAND = "MA869"; break;
        }

        decoded.SUB_BAND = (bytes[4] === 0xff) ? "NULL" : bytes[4];
    }

    return decoded;
}

module.exports = {
    Decode
};