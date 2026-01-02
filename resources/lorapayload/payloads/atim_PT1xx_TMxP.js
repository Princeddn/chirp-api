function Decode(input) {
    const bytes = input.bytes || [];
    if (!bytes.length) return { errors: ['empty payload'] };

    const b = bytes;
    let i = 0;
    const data = {};

    const header = b[i++];
    data.frameHeader = '0x' + header.toString(16).padStart(2,'0');

    const newGen = !!(header & 0x80);
    const hasTimestamp = !!(header & 0x40);
    data.newGeneration = newGen;
    data.timestampEnabled = hasTimestamp;

    const logicalType = header & 0x1F; // bas 5 bits (pattern doc)
    data.frameType = '0x' + logicalType.toString(16).padStart(2,'0');

    function readU16BE(pos){ return (b[pos] << 8) | b[pos+1]; }
    function readU32BE(pos){ return (b[pos] << 24)|(b[pos+1]<<16)|(b[pos+2]<<8)|b[pos+3]; }
    function toHexSlice(pos,len){ return b.slice(pos,pos+len).map(x=>x.toString(16).padStart(2,'0')).join(''); }

    const EPOCH2013_UNIX = Date.UTC(2013,0,1)/1000;
    function epoch2013ToUnix(e){ return (EPOCH2013_UNIX + e)>>>0; }
    function readTimestamp() {
        if (i + 4 > b.length) throw new Error('truncated timestamp');
        const ts2013 = readU32BE(i); i += 4;
        data.timestamp = ts2013;
        const ux = epoch2013ToUnix(ts2013);
        data.timestampUnix = ux;
        data.timestampIso = new Date(ux*1000).toISOString();
    }

    const errorCodeMap = {
        0x81:'ERR_UNKNOWN', 0x82:'ERR_BUF_SMALLER', 0x83:'ERR_DEPTH_HISTORIC_OUT_OF_RANGE',
        0x84:'ERR_NB_SAMPLE_OUT_OF_RANGE', 0x85:'ERR_NWAY_OUT_OF_RANGE',
        0x86:'ERR_TYPEWAY_OUT_OF_RANGE', 0x87:'ERR_SAMPLING_PERIOD', 0x88:'ERR_SUBTASK_END',
        0x89:'ERR_NULL_POINTER', 0x8A:'ERR_BATTERY_LEVEL_DEAD', 0x8B:'ERR_EEPROM', 0x8C:'ERR_ROM',
        0x8D:'ERR_RAM', 0x8E:'ERR_ARM_INIT_FAIL', 0x8F:'ERR_ARM_BUSY', 0x90:'ERR_ARM_BRIDGE_ENABLE',
        0x91:'ERR_RADIO_QUEUE_FULL', 0x92:'ERR_CFG_BOX_INIT_FAIL', 0x93:'ERR_KEEP_ALIVE_PERIOD',
        0x94:'ERR_ENTER_DEEP_SLEEP', 0x95:'ERR_BATTERY_LEVEL_LOW', 0x96:'ERR_ARM_TRANSMISSION',
        0x97:'ERR_ARM_PAYLOAD_BIGGER', 0x98:'ERR_RADIO_PAIRING_TIMEOUT', 0x99:'ERR_SENSORS_TIMEOUT',
        0x9A:'ERR_SENSOR_STOP', 0x9B:'ERR_SENSORS_FAIL', 0x9C:'ERR_BOX_OPENED', 0x9D:'ERR_BOX_CLOSED'
    };

    const alertTypeMap = {
        0: 'RETURN_BETWEEN_THRESHOLDS',
        1: 'HIGH_THRESHOLD_EXCEEDED',
        2: 'LOW_THRESHOLD_EXCEEDED',
        3: 'RESERVED'
    };

    function measureTypeInfo(nibble) {
        switch (nibble) {
            case 0x01: return { code:0x01, name:'input_state', size:1, signed:false, parse:(arr)=>arr[0] };
            case 0x04: return { code:0x04, name:'counter', size:4, signed:false, parse:(arr)=>((arr[0]<<24)|(arr[1]<<16)|(arr[2]<<8)|arr[3])>>>0 };
            case 0x08: return { code:0x08, name:'temperature', size:2, signed:true, parse:(arr)=>{
                let v=(arr[0]<<8)|arr[1];
                if (v & 0x8000) v = v - 0x10000;
                // 0x8000 est l'erreur mais impossible ici car sign bit -> déjà ajusté. On vérifie valeur brute avant conversion si besoin.
                return v/100;
            }};
            default: return { code:nibble, name:'unknown_'+nibble, size:1, signed:false, parse:(arr)=>arr[0] };
        }
    }

    if (hasTimestamp) {
        // Les exemples de trame de mesure n'ont PAS de timestamp (bit6=0).
        readTimestamp();
    }

    // ==== Dispatch selon logicalType ====
    if (logicalType === 0x01) { // Trame de vie
        if (i + 4 > b.length) return { errors:['heartbeat too short'] };
        const idle = readU16BE(i); i+=2;
        const tx   = readU16BE(i); i+=2;
        data.batteryIdleMv = idle;
        data.batteryIdleV = +(idle/1000).toFixed(3);
        data.batteryTxMv = tx;
        data.batteryTxV = +(tx/1000).toFixed(3);
        if (i < b.length) data.extraHex = toHexSlice(i,b.length-i);

    } else if ((header & 0xE0) === 0xA0) {
        // Trame de mesure nouvelle génération (pattern 0xA0,0xA1,0xA2,...)
        // Nombre d'échantillons:
        const sampleCount = (header & 0x07) + 1;
        data.sampleCount = sampleCount;

        // Historique : pas présent dans exemples -> profondeur = 1
        data.historicDepth = 1;

        // Emission period si sampleCount>1
        if (sampleCount > 1) {
            if (i + 2 > b.length) return { errors:['missing emission period'] };
            data.emissionPeriodMinutes = readU16BE(i); i += 2;
        }

        data.measures = [];
        while (i < b.length) {
            const channelHeader = b[i++];
            // Pattern confirmé: high nibble = channel, low nibble = type code
            const channel = (channelHeader >> 4) & 0x0F;
            const mTypeCode = channelHeader & 0x0F;
            const info = measureTypeInfo(mTypeCode);
            const needed = sampleCount * info.size;
            if (i + needed > b.length) {
                data.measures.push({ channel, type:info.name, error:'truncated', available:b.length - i });
                break;
            }
            const samples = [];
            for (let s=0; s<sampleCount; s++) {
                const slice = b.slice(i + s*info.size, i + (s+1)*info.size);
                const parsed = info.parse(slice);
                const rawHex = toHexSlice(i + s*info.size, info.size);
                samples.push({ value: parsed, valueRawHex: rawHex });
            }
            i += needed;
            data.measures.push({
                channel,
                type: info.name,
                rawType: mTypeCode,
                unit: info.name === 'temperature' ? '°C' :
                      (info.name === 'counter' ? 'impulses' :
                      (info.name === 'input_state' ? 'bitfield' : '')),
                samples
            });
        }

    } else if (logicalType === 0x0D || ((header & 0xF0) === 0x80 && (header & 0x0F) === 0x0D)) {
        // Trame alerte mesure nouvelle génération (ex header 0x8D : 1000 1101)
        data.alerts = [];
        while (i < b.length) {
            const alertHeader = b[i++];
            const alertType = alertHeader >> 6; // bits7..6
            const channel = alertHeader & 0x07; // bits2..0
            // Valeur 2 octets température (centième °C)
            if (i + 2 > b.length) {
                data.alerts.push({ channel, alertType, alertTypeText: alertTypeMap[alertType]||'UNKNOWN', error:'truncated' });
                break;
            }
            const raw = readU16BE(i); i += 2;
            let v = raw;
            if (v & 0x8000) v = v - 0x10000;
            const value = v / 100;
            data.alerts.push({
                channel,
                alertType,
                alertTypeText: alertTypeMap[alertType] || 'UNKNOWN',
                temperatureC: value,
                rawValueHex: raw.toString(16).padStart(4,'0')
            });
        }

    } else if (logicalType === 0x0E || ((header & 0x1F) === 0x0E)) {
        // Trame erreur
        data.errorsList = [];
        while (i < b.length) {
            const segHeader = b[i++];
            const idx = (segHeader >> 5) & 0x07;
            const segLen = segHeader & 0x1F;
            if (i + segLen > b.length) {
                data.errorsList.push({ index: idx, error:'truncated', expected:segLen, available:b.length - i});
                break;
            }
            const segment = b.slice(i, i+segLen); i += segLen;
            if (!segment.length) {
                data.errorsList.push({ index: idx, error:'emptySegment'});
                continue;
            }
            const code = segment[0];
            const entry = { index: idx, code, codeText: errorCodeMap[code] || 'UNKNOWN' };
            if ((code === 0x8A || code === 0x95) && segLen >= 3) {
                const mv = (segment[1]<<8)|segment[2];
                entry.batteryMv = mv;
                entry.batteryV = +(mv/1000).toFixed(3);
            }
            data.errorsList.push(entry);
        }

    } else if (logicalType === 0x05) {
        // Trame test compteur (1 octet)
        if (i >= b.length) return { errors:['counter test frame empty'] };
        data.testCounter = b[i++];

    } else {
        // Autres: expose hex restant
        if (i < b.length) data.payloadHex = toHexSlice(i, b.length - i);
    }

    return { data };
}

module.exports = { Decode };
