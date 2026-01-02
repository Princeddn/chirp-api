/**
 * BMeters IWM-LR5 - Water Meter Reader
 * Decoder for Jeedom LoRaPayload plugin
 * Supports multiple frame types: Standard, Compact, Extended, Datalogger, JSON, Immediate Alarm
 */

function Decode(input) {
    // Get byte array (already converted by lorapayload.js)
    const bytes = input.bytes || input.payload || [];

    // Auto-detect fPort based on payload length if not provided
    let fPort = null;
    // Auto-detect based on payload length
    const len = bytes.length;
    if (len === 47) {
        fPort = 1;  // Standard frame
    } else if (len >= 3 && len <= 7) {
        fPort = 10; // Compact frame
    } else if (len >= 16 && len <= 18) {
        fPort = 11; // Extended frame
    } else if (len === 51) {
        fPort = 12; // Datalogger frame
    } else if (len === 3 && bytes[0] === 0x49) {
        fPort = 20; // Immediate alarm (if ambiguous with compact, check first byte)
    } else {
        fPort = 13; // JSON or unknown - try JSON
    }

    const decoded = {};
    console.log(`Decoding BMeters IWM-LR5 payload on port ${fPort}, bytes length: ${bytes.length}`);
    // Helper functions
    const u16 = (b, i) => (b[i] | (b[i+1] << 8)) >>> 0;
    const u24 = (b, i) => (b[i] | (b[i+1] << 8) | (b[i+2] << 16)) >>> 0;
    const u32 = (b, i) => (b[i] | (b[i+1] << 8) | (b[i+2] << 16) | (b[i+3] << 24)) >>> 0;
    const i16 = (b, i) => { let v = u16(b, i); if (v & 0x8000) v = v - 0x10000; return v; };
    const toIso = (secs) => new Date(secs * 1000).toISOString();
    const hex = (b) => [...b].map(v => v.toString(16).padStart(2, "0")).join("");
    const ascii = (b) => String.fromCharCode(...b);

    const alarmLabels = [
        [0x0001, "module_removed"],
        [0x0002, "magnetic_fraud"],
        [0x0004, "nfc_fraud"],
        [0x0008, "reverse_flow"],
        [0x0010, "leakage"],
        [0x0020, "qmax_overflow"],
        [0x0040, "low_battery"],
        [0x0080, "reverse_installation"],
        [0x0100, "burst"],
        [0x0200, "no_consumption"],
        [0x0400, "excessive_temperature"],
        [0x0800, "freezing"],
        [0x1000, "rtc_reset"],
        [0x2000, "device_reset"]
    ];

    const decodeAlarmBits = (bits) =>
        alarmLabels.filter(([m]) => (bits & m) !== 0).map(([, name]) => name);

    // Check application code
    if (bytes.length === 0) {
        return { errors: ['Payload vide'] };
    }

    if (bytes[0] !== 0x49) {
        decoded.warning = 'Application code inattendu (byte0 != 0x49)';
    }

    try {
        switch (fPort) {
            // STANDARD FRAME (47 bytes) - Port 1
            case 1: {
                if (bytes.length < 47) {
                    decoded.warning = 'Longueur inattendue pour standard (attendu 47 bytes)';
                }
                decoded.frameType = 'standard';

                let i = 1;
                const deviceTime = u32(bytes, i); i += 4;
                const moduleSerial = u32(bytes, i); i += 4;
                const wmSerialRaw = bytes.slice(i, i + 14); i += 14;
                const stackVer = bytes.slice(i, i + 3); i += 3;
                const appVer = bytes.slice(i, i + 3); i += 3;
                const alarms = u16(bytes, i); i += 2;
                const absVolL = u32(bytes, i); i += 4;
                const leakThH = u16(bytes, i); i += 2;
                const revThL = u16(bytes, i); i += 2;
                const qmaxLh = u16(bytes, i); i += 2;
                const noConsD = u16(bytes, i); i += 2;
                const diameter = bytes[i++];
                const medium = bytes[i++];
                const monthlyDay = bytes[i++];
                const hourlySave = bytes[i++];

                decoded.timestampUnix = deviceTime;
                decoded.timestampIso = toIso(deviceTime);
                decoded.moduleSerial = moduleSerial;
                decoded.wmSerialAscii = ascii(wmSerialRaw.reverse());
                decoded.wmSerialHex = hex(wmSerialRaw);
                decoded.lorawanStackVersion = hex(stackVer);
                decoded.appVersion = hex(appVer);
                decoded.alarmsBits = alarms;
                decoded.alarmsActive = decodeAlarmBits(alarms).join(', ') || 'none';
                decoded.absVolumeL = absVolL;
                decoded.absVolumeM3 = (absVolL / 1000).toFixed(3);
                decoded.leakageThresholdHours = leakThH;
                decoded.reverseFlowThresholdL = revThL;
                decoded.qmaxOverflowLph = qmaxLh;
                decoded.noConsumptionDays = noConsD;
                decoded.diameterDN = diameter === 1 ? 15 : (diameter === 2 ? 20 : diameter);
                decoded.medium = medium === 6 ? 'water' : (medium === 7 ? 'hot_water' : medium);
                decoded.monthlyHistoryDay = monthlyDay;
                decoded.hourlyLogTimeH = hourlySave;
                break;
            }

            // COMPACT FRAME (<=7 bytes) - Port 10
            case 10: {
                decoded.frameType = 'compact';
                if (bytes.length < 3) {
                    return { errors: ['Compact: payload trop court'] };
                }
                const alarms = u16(bytes, 1);
                const volBytes = bytes.slice(3);
                let absVolL = 0;
                for (let k = 0; k < volBytes.length; k++) {
                    absVolL |= (volBytes[k] << (8 * k));
                }
                decoded.alarmsBits = alarms;
                decoded.alarmsActive = decodeAlarmBits(alarms).join(', ') || 'none';
                decoded.absVolumeL = absVolL >>> 0;
                decoded.absVolumeM3 = ((absVolL >>> 0) / 1000).toFixed(3);
                break;
            }

            // EXTENDED FRAME (17 bytes) - Port 11
            case 11: {
                if (bytes.length < 17) {
                    decoded.warning = '�tendu: longueur inattendue (doc: 17 bytes)';
                }
                decoded.frameType = 'extended';

                const alarms = u16(bytes, 1);
                const absVolL = u32(bytes, 3);
                const revFlowL = u24(bytes, 7);
                const prevMonthAbsL = u32(bytes, 10);
                const tempRaw = i16(bytes, 14);
                let batteryPct = null;

                if (bytes.length >= 18) {
                    batteryPct = u16(bytes, 16);
                } else if (bytes.length >= 17) {
                    batteryPct = bytes[16];
                }

                decoded.alarmsBits = alarms;
                decoded.alarmsActive = decodeAlarmBits(alarms).join(', ') || 'none';
                decoded.absVolumeL = absVolL;
                decoded.absVolumeM3 = (absVolL / 1000).toFixed(3);
                decoded.reverseFlowL = revFlowL;
                decoded.prevMonthAbsL = prevMonthAbsL;
                decoded.prevMonthAbsM3 = (prevMonthAbsL / 1000).toFixed(3);
                decoded.ambientTempC = (tempRaw / 10).toFixed(1);
                if (batteryPct != null) {
                    decoded.batteryPercent = batteryPct;
                }
                break;
            }

            // DATALOGGER FRAME (51 bytes) - Port 12
            case 12: {
                if (bytes.length < 51) {
                    decoded.warning = 'decodedlogger: longueur inattendue (doc: 51 bytes)';
                }
                decoded.frameType = 'decodedlogger';

                let i = 1;
                const currentAbsL = u32(bytes, i); i += 4;
                const deviceTime = u32(bytes, i); i += 4;
                const lastLogAbsL = u32(bytes, i); i += 4;
                const firstLogTime = u32(bytes, i); i += 4;
                const deltas = [];
                for (let d = 0; d < 16; d++) {
                    deltas.push(u16(bytes, i));
                    i += 2;
                }
                const alarms = u16(bytes, i);

                decoded.currentAbsL = currentAbsL;
                decoded.currentAbsM3 = (currentAbsL / 1000).toFixed(3);
                decoded.timestampUnix = deviceTime;
                decoded.timestampIso = toIso(deviceTime);
                decoded.lastLogAbsL = lastLogAbsL;
                decoded.firstLogTimestampUnix = firstLogTime;
                decoded.firstLogTimestampIso = toIso(firstLogTime);
                decoded.hourlyDeltasL = deltas.join(', ');
                decoded.alarmsBits = alarms;
                decoded.alarmsActive = decodeAlarmBits(alarms).join(', ') || 'none';
                break;
            }

            // JSON FRAME (ASCII) - Port 13
            case 13: {
                decoded.frameType = 'json';
                const text = ascii(bytes);
                try {
                    const obj = JSON.parse(text);
                    decoded.rawJson = JSON.stringify(obj);
                    if (obj.C) {
                        const v = parseFloat(String(obj.C).replace(",", "."));
                        if (!isNaN(v)) {
                            decoded.absVolumeM3 = v.toFixed(3);
                        }
                    }
                    if (obj.U) decoded.unit = obj.U;
                    if (obj.S) decoded.serial = obj.S;
                    if (obj.A) decoded.application = obj.A;
                } catch (e) {
                    return { errors: ['JSON invalide'] };
                }
                break;
            }

            // IMMEDIATE ALARM - Port 20
            case 20: {
                decoded.frameType = 'immediate_alarm';
                const rest = bytes.slice(1);
                decoded.rawHex = hex(rest);

                if (rest.length === 2) {
                    const a = u16(rest, 0);
                    decoded.alarmsBits = a;
                    decoded.alarmsActive = decodeAlarmBits(a).join(', ') || 'none';
                }
                break;
            }

            default:
                return { errors: [`Port ${fPort} non g�r� par ce d�codeur`] };
        }
    } catch (e) {
        return { errors: [String(e)] };
    }

    return { decoded };
}

module.exports = {
    Decode
};
