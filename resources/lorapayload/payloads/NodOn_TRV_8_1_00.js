// ==============================
// Decoder NodOn TRV-8-1-00
// ==============================

const OFFSET_LOOKUP = {
    0xf6 : "-5,0", 0xf7 : "-4,5", 0xf8 : "-4,0", 0xf9 : "-3,5",
    0xfa : "-3,0", 0xfb : "-2,5", 0xfc : "-2,0", 0xfd : "-1,5",
    0xfe : "-1.0", 0xff : "-0,5", 0x00 : "0,0",  0x01 : "0,5",
    0x02 : "1,0",  0x03 : "1,5",  0x04 : "2,0",  0x05 : "2,5",
    0x06 : "3,0",  0x07 : "3,5",  0x08 : "4,0",  0x09 : "4,5",
    0x0a : "5,0",
};

const decbin = (number) => {
    if (number < 0) number = 0xFFFFFFFF + number + 1;
    let bin = number.toString(2);
    return ("00000000" + bin).slice(-8);
};
const boolCon = (bit) => bit == 1;
const temperature = (temp) => parseInt(temp, 16) / 2;

const flagCalculation = (f0, f1, f2) => {
    let b0 = decbin(parseInt(f0,16));
    let b1 = decbin(parseInt(f1,16));
    let b2 = decbin(parseInt(f2,16));    
    return {        
        heatingTemperatureInUse: boolCon(b0[6]),
        energySavingTemperatureInUse : boolCon(b0[5]),
        operationModeOff : boolCon(b0[4]),
        positionModeEnabled : boolCon(b0[3]),
        windowOpenDetectionTimerActive : boolCon(b0[2]),  
        childProtection : boolCon(b1[7]),
        childProtectionPlus : boolCon(b1[6]),   
        displayOrientationChanged : boolCon(b1[5]),
        rfSymbolState : boolCon(b1[4]),
        modeJumping : boolCon(b1[3]),
        dailyBatteryReporting: boolCon(b2[4]),
        batteryLessThan15Percent: boolCon(b2[3]), 
        batteryLessThan25Percent: boolCon(b2[2]),
        deviceErrorState: flagErrorState(b2),
    };
};

const flagErrorState = (flagByte2) => {
    let errorState = (flagByte2[5]+flagByte2[6]+flagByte2[7]).toString();  
    return {
        deviceError:{
            e1ErrorState: (errorState === "001"),
            e2ErrorState: (errorState === "011"),
            deviceIsBusy: (errorState === "101"),
            deviceInMountingPosition: (errorState === "110"),
            deviceInValveMountingPosition: (errorState === "111"),
        }
    };    
};

const calculateTemperatureOffset = (offset) => OFFSET_LOOKUP[offset];
const calculateWindowOpenDetection = (thr) => {
    thr = parseInt(thr,16);
    return (thr >= 4 && thr <= 12) ? thr : "deactivated";
};

// ==============================
// Main decode function
// ==============================
function Decode(input){  
    let decoded = {};
    let commands = input.bytes.map(b => ("0" + b.toString(16)).substr(-2));  
    let command_len = 0;

    commands.map((cmd, i) => {          
        switch(cmd){
            case 'e3': // External temperature
                command_len = 1;
                decoded.externalTemperatureValue = (parseInt(commands[i+1],16) !== 0xff)
                    ? temperature(commands[i+1])
                    : "disabled";
                break;

            case 'e9': // Summary
                command_len = 6;
                decoded.summary_flags = flagCalculation(commands[i+1], commands[i+2], commands[i+3]);
                decoded.summary_measuredTemperature = temperature(commands[i+5]);
                decoded.summary_valvePosition = parseInt(commands[i+6],16);
                break;

            case 'f3': // Battery
                command_len = 1;
                decoded.battery_level = parseInt(commands[i+1],16);
                break;

            case 'f4': // Temperature settings
                command_len = 7;
                decoded.temperature_measured = temperature(commands[i+1]);
                decoded.temperature_energySaving = temperature(commands[i+2]);
                decoded.temperature_heating = temperature(commands[i+3]);
                decoded.temperatureOffset = calculateTemperatureOffset(parseInt(commands[i+4],16));
                decoded.windowOpenDetectionThreshold = calculateWindowOpenDetection(commands[i+5]);
                decoded.windowOpenDetectionDuration = parseInt(commands[i+6],16);
                break;

            case 'f5': // Temperature settings (detailed)
                command_len = 7;
                decoded.temperature = {
                    measuredTemperature: temperature(commands[i+1]),  
                    energySavingTemperature: temperature(commands[i+2]),        
                    heatingTemperature: temperature(commands[i+3]),
                    temperatureOffset: calculateTemperatureOffset(parseInt(commands[i+4],16)),
                    windowOpenDetectionThreshold: calculateWindowOpenDetection(commands[i+5]), 
                    windowOpenDetectionDuration: parseInt(commands[i+6],16), 
                    reportTemperature: temperature(commands[i+7]) 
                };
                break;

            case 'f6': // Flags
                command_len = 5;
                decoded.flags = flagCalculation(commands[i+1], commands[i+2], commands[i+3]);
                break;

            case 'f7': // Flags (extended downlink reply)
                command_len = 5;
                decoded.flags = flagCalculation(commands[i+1], commands[i+2], commands[i+3]);
                break;

            case 'f8': // Setpoint limits
                command_len = 2;
                decoded.setpoint_min = temperature(commands[i+1]);
                decoded.setpoint_max = temperature(commands[i+2]);
                break;

            case 'fe': // Valve position
                command_len = 2;
                decoded.valve_currentPosition = parseInt(commands[i+1],16);
                decoded.valve_maxLimit = parseInt(commands[i+2],16);
                break;

            case 'e2': // Max allowed valve position
                command_len = 1;
                decoded.valve_allowedMax = parseInt(commands[i+1],16);
                break;

            default:
                break;    
        }        
        commands.splice(i, command_len);     
    }); 

    return { data: decoded };
}

function Encode(payload) {
    var encoded = [];

    if ("setPointLimitation" in payload) {
        encoded = encoded.concat(setTemperatureControlLimitations(payload.setPointLimitation));
    }
    if ("valveControl" in payload) {
        encoded = encoded.concat(setValvePosition(payload.valveControl));
    }
    if ("temperature" in payload) {
        encoded = encoded.concat(setTemperature(payload.temperature));
    }
    if ("energySavingTemperature" in payload) {
        encoded = encoded.concat(setEnergySavingTemperature(payload.energySavingTemperature));
    }
    if ("heatingTemperature" in payload) {
        encoded = encoded.concat(setHeatingTemperature(payload.heatingTemperature));
    }
    if ("temperatureOffset" in payload) {
        encoded = encoded.concat(setTemperatureOffset(payload.temperatureOffset));
    }
    if ("windowOpenDetection" in payload) {
        encoded = encoded.concat(setWindowOpenDetection(payload.windowOpenDetection));
    }

    return encoded;
}


/**
 * Set temperature control limitations
 * @param {object} setPointLimitation
 * @param {number} setPointLimitation.minimumTemperatureSetPoint unit: celsius, range: [7.5, 28.5], step: 0.5
 * @param {number} setPointLimitation.maximumTemperatureSetPoint unit: celsius, range: [7.5, 28.5], step: 0.5
 * @example { "setPointLimitation": { "minimumTemperatureSetPoint": 7.5, "maximumTemperatureSetPoint": 28.5 } }
 */
function setTemperatureControlLimitations(input) {
    let output = [];

    let low = Math.floor(input.minimumTemperatureSetPoint * 2);
    let high = Math.floor(input.maximumTemperatureSetPoint * 2);

    // bornes autorisées : 15 → 7.5°C, 57 → 28.5°C
    if (low < 15 || low > 57) low = 0x80;
    if (high < 15 || high > 57) high = 0x80;

    output.push(0xf9, low, high);
    return output;
}

/**
 * Set valve control position
 * @param {object} valveControl
 * @param {number} valveControl.currentValvePosition unit: step, range: [0, 255]
 * @param {number} valveControl.maximumValvePositionLimit must be 0x00 (auto-calculated by TRV)
 * @example { "valveControl": { "currentValvePosition": 80, "maximumValvePositionLimit": 0 } }
 */
function setValvePosition(valveControl) {
    let output = [];
    // Vérifie si les paramètres sont valides
    if (valveControl.currentValvePosition != null && valveControl.maximumValvePositionLimit != null) {
        output.push(0xff);
        // borne correcte (0–255), sinon fallback à 0
        if (valveControl.currentValvePosition >= 0 && valveControl.currentValvePosition <= 255) {
            output.push(valveControl.currentValvePosition);
        } else {
            output.push(0x00);
        }
        // toujours 0x00 d’après la doc
        output.push(0x00);
    }
    return output;
}

/**
 * Set temperature configuration (all parameters)
 * @param {object} temperature
 * @param {number} temperature.energySavingTemperature unit: celsius, range: [7.5, 28.5], step: 0.5 (0x80 ignore)
 * @param {number} temperature.heatingTemperature unit: celsius, range: [7.5, 28.5], step: 0.5 (0x80 ignore)
 * @param {number} temperature.measuredTemperature unit: celsius, read-only → always 0x80
 * @param {string} temperature.temperatureOffset values: "-5.0" … "+5.0" by 0.5 steps (0x80 ignore)
 * @param {number} temperature.windowOpenDetectionThreshold values: (4, 8, 12, 0xFF disable, else 0x80 ignore)
 * @param {number} temperature.windowOpenDetectionDuration unit: minute, range: [1, 30] (else 0x80)
 * @param {number} temperature.reportTemperature reserved, always 0x80
 * @example { "temperature": { "energySavingTemperature": 16, "heatingTemperature": 22.5, "temperatureOffset": "0.0", "windowOpenDetectionThreshold": 4, "windowOpenDetectionDuration": 10 } }
 */
function setTemperature(input){
    let output = [];
    output.push(0xf5);

    // Data01 : mesurée (toujours ignorée)
    output.push(0x80);

    // Data02 : Energy Saving Temp
    let energySavingTemp = 0x80;
    if (typeof input.energySavingTemperature === "number") {
        let tmp = Math.floor(input.energySavingTemperature * 2);
        if (tmp >= 14 && tmp <= 57) energySavingTemp = tmp;
    }
    output.push(energySavingTemp);

    // Data03 : Heating Temp
    let heatingTemperature = 0x80;
    if (typeof input.heatingTemperature === "number") {
        let tmp = Math.floor(input.heatingTemperature * 2);
        if (tmp >= 14 && tmp <= 57) heatingTemperature = tmp;
    }
    output.push(heatingTemperature);

    // Data04 : Offset
    let offsetKey = (typeof input.temperatureOffset === "number")
        ? input.temperatureOffset.toFixed(1)
        : input.temperatureOffset;
    let temperatureOffset = OFFSET_LOOKUP_TABLE[offsetKey];
    if (temperatureOffset === undefined) temperatureOffset = 0x80;
    output.push(temperatureOffset);

    // Data05 : Window detection threshold
    let threshold = 0x80;
    if (typeof input.windowOpenDetectionThreshold === "number") {
        if (input.windowOpenDetectionThreshold === 0xff ||
           (input.windowOpenDetectionThreshold >= 4 && input.windowOpenDetectionThreshold <= 12)) {
            threshold = input.windowOpenDetectionThreshold;
        }
    }
    output.push(threshold);

    // Data06 : Window detection duration
    let duration = 0x80;
    if (typeof input.windowOpenDetectionDuration === "number" &&
        input.windowOpenDetectionDuration >= 1 &&
        input.windowOpenDetectionDuration <= 30) {
        duration = input.windowOpenDetectionDuration;
    }
    output.push(duration);

    // Data07 : Report temperature (non utilisé)
    output.push(0x80);

    return output;
}

/**
 * Set energy saving temperature only
 * @param {number} energySavingTemperature unit: celsius, range: [7.5, 28.5], step: 0.5
 * @example { "energySavingTemperature": 16 }
 */
function setEnergySavingTemperature(energySavingTemperature) {
    let output = [];
    output.push(0xf5);
    output.push(0x80); // measured temperature (ignored)

    // Energy Saving Temp
    let tmp = Math.floor(energySavingTemperature * 2);
    if (tmp >= 14 && tmp <= 57) {
        output.push(tmp);
    } else {
        output.push(0x80);
    }

    output.push(0x80); // heating temperature (ignored)
    output.push(0x80); // offset (ignored)
    output.push(0x80); // window detection threshold (ignored)
    output.push(0x80); // window detection duration (ignored)
    output.push(0x80); // report temperature (ignored)

    return output;
}

/**
 * Set heating temperature only
 * @param {number} heatingTemperature unit: celsius, range: [7.5, 28.5], step: 0.5
 * @example { "heatingTemperature": 22.5 }
 */
function setHeatingTemperature(heatingTemperature) {
    let output = [];
    output.push(0xf5);
    output.push(0x80); // measured temperature (ignored)
    output.push(0x80); // energy saving temperature (ignored)

    // Heating Temp
    let tmp = Math.floor(heatingTemperature * 2);
    if (tmp >= 14 && tmp <= 57) {
        output.push(tmp);
    } else {
        output.push(0x80);
    }

    output.push(0x80); // offset (ignored)
    output.push(0x80); // window detection threshold (ignored)
    output.push(0x80); // window detection duration (ignored)
    output.push(0x80); // report temperature (ignored)

    return output;
}

/**
 * Set temperature offset only
 * @param {string|number} temperatureOffset values: "-5.0" … "+5.0" by 0.5 steps
 * @example { "temperatureOffset": "0.0" } or { "temperatureOffset": 0.0 }
 */
function setTemperatureOffset(temperatureOffset) {
    let output = [];
    output.push(0xf5);
    output.push(0x80); // measured temperature (ignored)
    output.push(0x80); // energy saving temperature (ignored)
    output.push(0x80); // heating temperature (ignored)

    // Temperature Offset
    let offsetKey = (typeof temperatureOffset === "number")
        ? temperatureOffset.toFixed(1)
        : temperatureOffset;
    let offset = OFFSET_LOOKUP_TABLE[offsetKey];
    if (offset === undefined) offset = 0x80;
    output.push(offset);

    output.push(0x80); // window detection threshold (ignored)
    output.push(0x80); // window detection duration (ignored)
    output.push(0x80); // report temperature (ignored)

    return output;
}

/**
 * Set window open detection parameters
 * @param {object} windowOpenDetection
 * @param {number} windowOpenDetection.threshold values: (4, 8, 12, 0xFF to disable)
 * @param {number} windowOpenDetection.duration unit: minute, range: [1, 30]
 * @example { "windowOpenDetection": { "threshold": 4, "duration": 10 } }
 */
function setWindowOpenDetection(windowOpenDetection) {
    let output = [];
    output.push(0xf5);
    output.push(0x80); // measured temperature (ignored)
    output.push(0x80); // energy saving temperature (ignored)
    output.push(0x80); // heating temperature (ignored)
    output.push(0x80); // offset (ignored)

    // Window detection threshold
    let threshold = 0x80;
    if (typeof windowOpenDetection.threshold === "number") {
        if (windowOpenDetection.threshold === 0xff ||
           (windowOpenDetection.threshold >= 4 && windowOpenDetection.threshold <= 12)) {
            threshold = windowOpenDetection.threshold;
        }
    }
    output.push(threshold);

    // Window detection duration
    let duration = 0x80;
    if (typeof windowOpenDetection.duration === "number" &&
        windowOpenDetection.duration >= 1 &&
        windowOpenDetection.duration <= 30) {
        duration = windowOpenDetection.duration;
    }
    output.push(duration);

    output.push(0x80); // report temperature (ignored)

    return output;
}

const OFFSET_LOOKUP_TABLE = {
    "-5.0": 0xf6,
    "-4.5": 0xf7,
    "-4.0": 0xf8,
    "-3.5": 0xf9,
    "-3.0": 0xfa,
    "-2.5": 0xfb,
    "-2.0": 0xfc,
    "-1.5": 0xfd,
    "-1.0": 0xfe,
    "-0.5": 0xff,
    "0.0": 0x00,
    "0.5": 0x01,
    "1.0": 0x02,
    "1.5": 0x03,
    "2.0": 0x04,
    "2.5": 0x05,
    "3.0": 0x06,
    "3.5": 0x07,
    "4.0": 0x08,
    "4.5": 0x09,
    "5.0": 0x0a
};


// Export for Node.js
module.exports = { Decode, Encode };
 