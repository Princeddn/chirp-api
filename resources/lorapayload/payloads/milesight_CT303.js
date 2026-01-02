/**
 * https://github.com/Milesight-IoT/SensorDecoders/blob/main/CT_Series/CT3xx/CT3xx_Decoder.js
 * Payload Decoder
 *
 * Copyright 2025 Milesight IoT
 *
 * @product CT303 / CT305 / CT310
 */
var RAW_VALUE = 0x00;

// Chirpstack v4
function decodeUplink(input) {
    var decoded = milesightDeviceDecode(input.bytes);
    return { data: decoded };
}

// Chirpstack v3
function Decode(input) {
    bytes = input.bytes
    return milesightDeviceDecode(bytes);
}

// The Things Network
function Decoder(bytes, port) {
    return milesightDeviceDecode(bytes);
}

var current_total_chns = [0x03, 0x05, 0x07];
var current_chns = [0x04, 0x06, 0x08];
var current_alarm_chns = [0x84, 0x86, 0x88];

function milesightDeviceDecode(bytes) {
    var decoded = {};
    for (var i = 0; i < bytes.length;) {
        var channel_id = bytes[i++];
        var channel_type = bytes[i++];

        // IPSO VERSION
        if (channel_id === 0xff && channel_type === 0x01) {
            decoded.ipso_version = readProtocolVersion(bytes[i]);
            i += 1;
        }
        // HARDWARE VERSION
        else if (channel_id === 0xff && channel_type === 0x09) {
            decoded.hardware_version = readHardwareVersion(bytes.slice(i, i + 2));
            i += 2;
        }
        // FIRMWARE VERSION
        else if (channel_id === 0xff && channel_type === 0x0a) {
            decoded.firmware_version = readFirmwareVersion(bytes.slice(i, i + 2));
            i += 2;
        }
        // TSL VERSION
        else if (channel_id === 0xff && channel_type === 0xff) {
            decoded.tsl_version = readTslVersion(bytes.slice(i, i + 2));
            i += 2;
        }
        // SERIAL NUMBER
        else if (channel_id === 0xff && channel_type === 0x16) {
            decoded.sn = readSerialNumber(bytes.slice(i, i + 8));
            i += 8;
        }
        // LORAWAN CLASS TYPE
        else if (channel_id === 0xff && channel_type === 0x0f) {
            decoded.lorawan_class = readLoRaWANClass(bytes[i]);
            i += 1;
        }
        // RESET EVENT
        else if (channel_id === 0xff && channel_type === 0xfe) {
            decoded.reset_event = readResetEvent(1);
            i += 1;
        }
        // DEVICE STATUS
        else if (channel_id === 0xff && channel_type === 0x0b) {
            decoded.device_status = readDeviceStatus(1);
            i += 1;
        }
        // TOTAL CURRENT
        else if (includes(current_total_chns, channel_id) && channel_type === 0x97) {
            var current_total_chn_name = "current_chn" + (current_total_chns.indexOf(channel_id) + 1) + "_total";
            decoded[current_total_chn_name] = readUInt32LE(bytes.slice(i, i + 4)) / 100;
            i += 4;
        }
        // CURRENT
        else if (includes(current_chns, channel_id) && channel_type === 0x99) {
            var current_alarm_chn_name = "current_chn" + (current_chns.indexOf(channel_id) + 1);
            var current_value = readUInt16LE(bytes.slice(i, i + 2));
            if (current_value === 0xffff) {
                decoded[current_alarm_chn_name + "_sensor_status"] = readSensorStatus(2);
            } else {
                decoded[current_alarm_chn_name] = current_value / 10;
            }
            i += 2;
        }
        // TEMPERATURE
        else if (channel_id === 0x09 && channel_type === 0x67) {
            var temperature_value = readUInt16LE(bytes.slice(i, i + 2));
            if (temperature_value === 0xfffd) {
                decoded.temperature_sensor_status = readSensorStatus(1);
            } else if (temperature_value === 0xffff) {
                decoded.temperature_sensor_status = readSensorStatus(2);
            } else {
                decoded.temperature = readInt16LE(bytes.slice(i, i + 2)) / 10;
            }
            i += 2;
        }
        // CURRENT ALARM
        else if (includes(current_alarm_chns, channel_id) && channel_type === 0x99) {
            var current_alarm_chn_name = "current_chn" + (current_alarm_chns.indexOf(channel_id) + 1);
            decoded[current_alarm_chn_name + "_max"] = readUInt16LE(bytes.slice(i, i + 2)) / 100;
            decoded[current_alarm_chn_name + "_min"] = readUInt16LE(bytes.slice(i + 2, i + 4)) / 100;
            decoded[current_alarm_chn_name] = readUInt16LE(bytes.slice(i + 4, i + 6)) / 100;
            Object.assign(decoded, readCurrentAlarm(bytes[i + 6], current_alarm_chns.indexOf(channel_id) + 1));
            i += 7;
        }
        // TEMPERATURE ALARM
        else if (channel_id === 0x89 && channel_type === 0x67) {
            decoded.temperature = readInt16LE(bytes.slice(i, i + 2)) / 10;
            decoded.temperature_alarm = readTemperatureAlarm(bytes[i + 2]);
            i += 3;
        }
        else {
            break;
        }
    }

    return decoded;
}



function readProtocolVersion(bytes) {
    var major = (bytes & 0xf0) >> 4;
    var minor = bytes & 0x0f;
    return "v" + major + "." + minor;
}

function readHardwareVersion(bytes) {
    var major = bytes[0] & 0xff;
    var minor = (bytes[1] & 0xff) >> 4;
    return "v" + major + "." + minor;
}

function readFirmwareVersion(bytes) {
    var major = bytes[0] & 0xff;
    var minor = bytes[1] & 0xff;
    return "v" + major + "." + minor;
}

function readTslVersion(bytes) {
    var major = bytes[0] & 0xff;
    var minor = bytes[1] & 0xff;
    return "v" + major + "." + minor;
}

function readSerialNumber(bytes) {
    var temp = [];
    for (var idx = 0; idx < bytes.length; idx++) {
        temp.push(("0" + (bytes[idx] & 0xff).toString(16)).slice(-2));
    }
    return temp.join("");
}

function readLoRaWANClass(type) {
    var class_map = {
        0: "Class A",
        1: "Class B",
        2: "Class C",
        3: "Class CtoB",
    };
    return getValue(class_map, type);
}

function readResetEvent(status) {
    var status_map = { 0: "0", 1: "1" };
    return getValue(status_map, status);
}

function readDeviceStatus(status) {
    var status_map = { 0: "0", 1: "1" };
    return getValue(status_map, status);
}

function readYesNoStatus(status) {
    var status_map = { 0: "0", 1: "1" };
    return getValue(status_map, status);
}

function readSensorStatus(status) {
    var status_map = { 0: "normal", 1: "over range alarm", 2: "read failed" };
    return getValue(status_map, status);
}

function readCurrentAlarm(value, channelIndex) {
    const alarm_bit_offset = {
        "threshold_alarm": 0,
        "threshold_alarm_release": 1,
        "over_range_alarm": 2,
        "over_range_alarm_release": 3
    };

    const alarmResults = {};

    for (const [alarmType, bit] of Object.entries(alarm_bit_offset)) {
        const key = `current_chn${channelIndex}_${alarmType}`;
        alarmResults[key] = readYesNoStatus((value >> bit) & 0x01);
    }

    return alarmResults;
}

function readConditionType(value) {
    var condition_map = { 0: "disable", 1: "below", 2: "above", 3: "between", 4: "outside" };
    return getValue(condition_map, value);
}

function readTemperatureAlarm(type) {
    var alarm_map = { 0: "0", 1: "1" };
    return getValue(alarm_map, type);
}

function readUInt8(bytes) {
    return bytes & 0xff;
}

function readInt8(bytes) {
    var ref = readUInt8(bytes);
    return ref > 0x7f ? ref - 0x100 : ref;
}

function readUInt16LE(bytes) {
    var value = (bytes[1] << 8) + bytes[0];
    return value & 0xffff;
}

function readInt16LE(bytes) {
    var ref = readUInt16LE(bytes);
    return ref > 0x7fff ? ref - 0x10000 : ref;
}

function readUInt32LE(bytes) {
    var value = (bytes[3] << 24) + (bytes[2] << 16) + (bytes[1] << 8) + bytes[0];
    return (value & 0xffffffff) >>> 0;
}

function readInt32LE(bytes) {
    var ref = readUInt32LE(bytes);
    return ref > 0x7fffffff ? ref - 0x100000000 : ref;
}

function readFloatLE(bytes) {
    var bits = (bytes[3] << 24) | (bytes[2] << 16) | (bytes[1] << 8) | bytes[0];
    var sign = bits >>> 31 === 0 ? 1.0 : -1.0;
    var e = (bits >>> 23) & 0xff;
    var m = e === 0 ? (bits & 0x7fffff) << 1 : (bits & 0x7fffff) | 0x800000;
    var f = sign * m * Math.pow(2, e - 150);
    return f;
}

function includes(items, value) {
    var size = items.length;
    for (var i = 0; i < size; i++) {
        if (items[i] == value) {
            return true;
        }
    }
    return false;
}

function getValue(map, key) {
    if (RAW_VALUE) return key;

    var value = map[key];
    if (!value) value = "unknown";
    return value;
}

if (!Object.assign) {
    Object.defineProperty(Object, "assign", {
        enumerable: false,
        configurable: true,
        writable: true,
        value: function (target) {
            "use strict";
            if (target == null) {
                throw new TypeError("Cannot convert first argument to object");
            }

            var to = Object(target);
            for (var i = 1; i < arguments.length; i++) {
                var nextSource = arguments[i];
                if (nextSource == null) {
                    continue;
                }
                nextSource = Object(nextSource);

                var keysArray = Object.keys(Object(nextSource));
                for (var nextIndex = 0, len = keysArray.length; nextIndex < len; nextIndex++) {
                    var nextKey = keysArray[nextIndex];
                    var desc = Object.getOwnPropertyDescriptor(nextSource, nextKey);
                    if (desc !== undefined && desc.enumerable) {
                        // concat array
                        if (Array.isArray(to[nextKey]) && Array.isArray(nextSource[nextKey])) {
                            to[nextKey] = to[nextKey].concat(nextSource[nextKey]);
                        } else {
                            to[nextKey] = nextSource[nextKey];
                        }
                    }
                }
            }
            return to;
        },
    });
}

module.exports = {
    Decode
};