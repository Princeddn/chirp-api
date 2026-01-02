function Decode(input) {
    const bytes = input.bytes || [];
    const data = {};
    if (!bytes.length) {
        return { errors: ['empty payload'] };
    }

    const fc = bytes[0]; // frame code
    data.frameCode = '0x' + fc.toString(16).padStart(2, '0').toUpperCase();

    // Helpers locaux
    const u16 = (i) => (bytes[i] << 8) | bytes[i+1];
    const u32 = (i) => (bytes[i] << 24) | (bytes[i+1] << 16) | (bytes[i+2] << 8) | bytes[i+3];
    const toHex = (i, len) => bytes.slice(i, i+len).map(b=>b.toString(16).padStart(2,'0')).join('');

    const EPOCH2013_UNIX = Date.UTC(2013,0,1)/1000;
    const epoch2013ToUnix = (v) => EPOCH2013_UNIX + v;
    const addTs = (prefix, e2013) => {
        data[prefix] = e2013;
        const unix = epoch2013ToUnix(e2013);
        data[prefix + 'Unix'] = unix;
        data[prefix + 'Iso']  = new Date(unix * 1000).toISOString();
    };

    // Status byte (position 1 sur toutes les trames que tu m’as données)
    // Bit1= LowBat (ex: KeepAlive 0x22 -> Bit1@1: Low Bat detected ; 0x20 -> Bit1@0: no LowBat)
    // Pour 0x10 ils disent "Bit1@0: configuration consistent" => même bit réutilisé différemment.
    function commonStatusInterpretation(frameCode) {
        const s = bytes[1];
        data.statusRaw = s;
        if (frameCode === 0x10) {
            data.configConsistent = ((s & 0x02) === 0); // Bit1 = 0 => consistent
        } else {
            data.lowBattery = !!(s & 0x02);
        }
        return 2; // offset après le status
    }

    switch (fc) {
        case 0x10: { // Product configuration
            if (bytes.length < 28) return { errors: ['length mismatch for 0x10'] };
            let o = commonStatusInterpretation(fc); // o=2
            data.productMode = bytes[o++];                // S306
            data.txPeriodHistorizations = u16(o); o += 2; // S301
            data.inputCfgRaw = bytes[o++];               // S320 (bits non détaillés)
            const histPeriodFactor = u16(o); o += 2;      // S321 (x2s)
            data.historizationPeriodSeconds = histPeriodFactor * 2;
            data.debounceRaw = bytes[o++];               // S322 (pas de formule précise dispo)
            data.flowCalcPeriodMin = u16(o); o += 2;      // S325
            data.flowThresholdA = u16(o); o += 2;         // S326 (pulses/h)
            data.flowThresholdB = u16(o); o += 2;         // S327
            data.leakThresholdA = u16(o); o += 2;         // S328
            data.leakThresholdB = u16(o); o += 2;         // S329
            data.dailyPeriodsUnderLeakA = u16(o); o += 2; // S330
            data.dailyPeriodsUnderLeakB = u16(o); o += 2; // S331
            data.tamper1SamplingPeriod = bytes[o++];      // S332
            data.tamper1SamplesBeforeAlarm = bytes[o++];  // S333
            data.tamper2SamplingPeriod = bytes[o++];      // S334
            data.tamper2SamplesBeforeAlarm = bytes[o++];  // S335
            data.redundantSamplesPerFrame = bytes[o++];   // S340
            break;
        }

        case 0x20: { // Network configuration
            if (bytes.length < 4) return { errors: ['length mismatch for 0x20'] };
            let o = commonStatusInterpretation(fc); // o=2
            const loraOpts = bytes[o++];
            data.loraOptionsRaw = loraOpts;
            data.adrOn = !!(loraOpts & 0x01);
            data.dutyCycleOn = !!(loraOpts & 0x04);
            const prov = bytes[o++];
            data.provisioningMode = prov === 0 ? 'ABP' : (prov === 1 ? 'OTAA' : prov);
            break;
        }

        case 0x37: { // Software version
            if (bytes.length < 8) return { errors: ['length mismatch for 0x37'] };
            let o = commonStatusInterpretation(fc); // o=2
            data.appVersionMajor  = bytes[o++];
            data.appVersionMinor  = bytes[o++];
            data.appVersionPatch  = bytes[o++];
            data.appVersion = data.appVersionMajor + '.' + data.appVersionMinor + '.' + data.appVersionPatch;
            data.rtuVersionMajor  = bytes[o++];
            data.rtuVersionMinor  = bytes[o++];
            data.rtuVersionPatch  = bytes[o++];
            data.rtuVersion = data.rtuVersionMajor + '.' + data.rtuVersionMinor + '.' + data.rtuVersionPatch;
            break;
        }

        case 0x30: { // Keep alive
            if (bytes.length < 3) return { errors: ['length mismatch for 0x30'] };
            let o = commonStatusInterpretation(fc); // o=2
            const alarms = bytes[o++];
            data.alarmsRaw = alarms;
            data.alarmExceedFlowA = !!(alarms & 0x01);
            data.alarmExceedFlowB = !!(alarms & 0x02);
            data.alarmTamperA     = !!(alarms & 0x04);
            data.alarmTamperB     = !!(alarms & 0x08);
            data.alarmLeakA       = !!(alarms & 0x10);
            data.alarmLeakB       = !!(alarms & 0x20);
            if (bytes.length >= 5) { data.maxFlowA = u16(o); o += 2; }
            if (bytes.length >= 7) { data.maxFlowB = u16(o); o += 2; }
            if (bytes.length >= 9) { data.minFlowA = u16(o); o += 2; }
            if (bytes.length >= 11){ data.minFlowB = u16(o); o += 2; }
            if (bytes.length >= 15){ addTs('timestamp', u32(o)); }
            break;
        }

        case 0x46: { // Periodic data without historization
            if (bytes.length < 2) return { errors: ['length mismatch for 0x46'] };
            let o = commonStatusInterpretation(fc); // o=2
            if (bytes.length >= 6) { data.counterA = u32(o); o += 4; }
            if (bytes.length >= 10){ data.counterB = u32(o); o += 4; }
            if (bytes.length >= 14){ addTs('timestamp', u32(o)); }
            break;
        }

        case 0x47: { // Alarm flow exceed
            if (bytes.length < 6 && bytes.length < 2) return { errors: ['length mismatch for 0x47'] };
            let o = commonStatusInterpretation(fc); // o=2
            if (bytes.length >= 4) { data.measuredFlowA = u16(o); o += 2; }
            if (bytes.length >= 6) { data.measuredFlowB = u16(o); o += 2; }
            if (bytes.length >= 10){ addTs('timestamp', u32(o)); }
            break;
        }

        case 0x5A:
        case 0x5B: { // Periodic with historization (channel A / B)
            if (bytes.length < 6) return { errors: ['length mismatch for 0x5A/0x5B'] };
            let o = commonStatusInterpretation(fc); // o=2
            data.channel = (fc === 0x5A) ? 'A' : 'B';
            const indexT0 = u32(o); o += 4;
            data.indexT0 = indexT0;

            // Heuristique pour détecter un timestamp final (4 octets) : si reste >=6 et (reste-4)%2==0
            const remaining = bytes.length - o;
            let hasTs = false;
            if (remaining >= 6 && ((remaining - 4) % 2 === 0)) hasTs = true;
            const endDeltas = hasTs ? bytes.length - 4 : bytes.length;

            const deltas = [];
            while (o + 1 < endDeltas) {
                deltas.push(u16(o));
                o += 2;
            }

            // Reconstruction absolues (t0, t-1, t-2...)
            let current = indexT0;
            data.histoSamples = [];
            data.histoSamples.push({ pos: 0, delta: 0, value: current });
            for (let i = 0; i < deltas.length; i++) {
                current -= deltas[i];
                data.histoSamples.push({ pos: i + 1, delta: deltas[i], value: current });
            }
            data.histoSampleCount = data.histoSamples.length;

            // Bit de "capacity warning" hypothétique : on expose simplement bit7
            data.capacityWarning = !!(bytes[1] & 0x80);

            if (hasTs) {
                addTs('timestamp', u32(bytes.length - 4));
            }
            break;
        }

        case 0x31: { // Get register response
            if (bytes.length < 2) return { errors: ['length mismatch for 0x31'] };
            let o = commonStatusInterpretation(fc); // o=2
            const regBytes = bytes.slice(o);
            data.regDataHex = regBytes.map(b=>b.toString(16).padStart(2,'0')).join('');
            // Optionnel: décodage si input.registerSizes fourni (array de 1/2/4)
            if (Array.isArray(input.registerSizes) && input.registerSizes.length) {
                let off = 0;
                data.registerValues = [];
                for (let i = 0; i < input.registerSizes.length; i++) {
                    const sz = input.registerSizes[i];
                    if (![1,2,4].includes(sz)) {
                        data.registerValues.push({ index: i, error: 'bad size ' + sz });
                        continue;
                    }
                    if (off + sz > regBytes.length) {
                        data.registerValues.push({ index: i, error: 'truncated' });
                        break;
                    }
                    let val;
                    if (sz === 1) val = regBytes[off];
                    else if (sz === 2) val = (regBytes[off] << 8) | regBytes[off+1];
                    else val = (regBytes[off] << 24) | (regBytes[off+1] << 16) | (regBytes[off+2] << 8) | regBytes[off+3];
                    const sliceHex = regBytes.slice(off, off+sz).map(b=>b.toString(16).padStart(2,'0')).join('');
                    data.registerValues.push({ index: i, size: sz, value: val, hex: sliceHex });
                    off += sz;
                }
                if (off < regBytes.length) {
                    data.registerRemainingHex = regBytes.slice(off).map(b=>b.toString(16).padStart(2,'0')).join('');
                }
            }
            break;
        }

        case 0x33: { // Set register response
            if (bytes.length < 3) return { errors: ['length mismatch for 0x33'] };
            let o = commonStatusInterpretation(fc); // o=2
            const reqStatus = bytes[o++];
            data.requestStatusRaw = reqStatus;
            const map = {
                0x01: 'success',
                0x02: 'success_no_update',
                0x03: 'error_coherency',
                0x04: 'error_invalid_register',
                0x05: 'error_invalid_value',
                0x06: 'error_truncated_value',
                0x07: 'error_access_not_allowed',
                0x08: 'error_other'
            };
            data.requestStatus = map[reqStatus] || 'unknown';
            if (reqStatus !== 0x01 && bytes.length >= o + 2) {
                data.registerId = u16(o);
            }
            break;
        }

        default:
            return { errors: ['unknown frame code 0x' + fc.toString(16)] };
    }

    return { data };
}

module.exports = { Decode };
