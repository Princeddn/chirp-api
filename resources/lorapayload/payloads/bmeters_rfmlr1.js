function Decode(input) {
    input.fPort = 1;
    const bytes = input.bytes;
    const data = {};
    let i = 0;

    while (i < bytes.length) {
        const type = bytes[i++];
        if (type !== 0x01) {
            return { errors: ['unknown type 0x' + type.toString(16)] };
        }

        const idx = bytes[i++];
        switch (idx) {
            case 0x20: {  // Status alarms
                const s = bytes[i++];
                data.alarmLeakage       = (s & 0x01) ? 1 : 0;
                data.alarmModuleRemoved = (s & 0x08) ? 1 : 0;
                data.alarmMagneticFraud = (s & 0x20) ? 1 : 0;
                data.alarmFlowExceedQ3  = (s & 0x80) ? 1 : 0;
                break;
            }
            case 0x21: {  // Volume (UInt32 BE, litres)
                const v = (bytes[i++] << 24)
                        | (bytes[i++] << 16)
                        | (bytes[i++] << 8)
                        |  bytes[i++];
                data.volume = v;
                break;
            }
            case 0x22: {  // Reporting interval (UInt16 BE, minutes)
                const iv = (bytes[i++] << 8) | bytes[i++];
                data.reportingInterval = iv;
                break;
            }
            case 0x25: {  // Starting value (UInt32 BE, litres)
                const sv = (bytes[i++] << 24)
                         | (bytes[i++] << 16)
                         | (bytes[i++] << 8)
                         |  bytes[i++];
                data.startingValue = sv;
                break;
            }
            case 0x27: {  // Back‑flow volume (UInt32 BE, litres)
                const bf = (bytes[i++] << 24)
                         | (bytes[i++] << 16)
                         | (bytes[i++] << 8)
                         |  bytes[i++];
                data.backflowVolume = bf;
                break;
            }
            case 0x2B: {  // Q3 max flow (UInt16 BE, L/h)
                const q3 = (bytes[i++] << 8) | bytes[i++];
                data.Q3MaxFlow = q3;
                break;
            }
            case 0x2C: {  // Leak window size (UInt8, ×15 s samples)
                data.leakWindowSize = bytes[i++];
                break;
            }
            case 0x2D: {  // Leak zero tolerance (UInt8)
                data.leakZeroTolerance = bytes[i++];
                break;
            }
            case 0x03: {  // FW build hash (6 bytes)
                const h = bytes.slice(i, i + 6)
                    .map(b => b.toString(16).padStart(2,'0'))
                    .join('');
                data.fwBuildHash = h;
                i += 6;
                break;
            }
            case 0x06: {  // CPU voltage (UInt8, LSB=25 mV)
                data.cpuVoltage = bytes[i++] * 0.025;
                break;
            }
            case 0x0A: {  // CPU temperature (UInt16 BE, LSB=0.01 °C, –50 °C offset)
                const traw = (bytes[i++] << 8) | bytes[i++];
                data.cpuTemp = (traw * 0.01) - 50;
                break;
            }
            default:
                return { errors: ['unknown index 0x' + idx.toString(16)] };
        }
    }

    return { data };
}

module.exports = {
    Decode
};
