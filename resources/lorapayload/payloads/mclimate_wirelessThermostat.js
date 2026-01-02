/* https://docs.mclimate.eu/mclimate-lorawan-devices/devices/mclimate-wireless-thermostat/decoding-and-bacnet-object-mapping/mclimate-wireless-thermostat-uplink-decoder */

// DataCake
function Decoder(bytes, port){
    var decoded = decodeUplink({ bytes: bytes, fPort: port }).data;
    return decoded;
}

// Milesight
function Decode(port, bytes){
    var decoded = decodeUplink({ bytes: bytes, fPort: port }).data;
    return decoded;
}

// The Things Industries / Main
function Decode(input) {
    try{
        var bytes = input.bytes;
        var data = {};
        function toBool(value){
            return value == '1';
        }
        function calculateTemperature(rawData){return (rawData - 400) / 10};
        function calculateHumidity(rawData){return (rawData * 100) / 256};
        function decbin(number) {
            if (number < 0) {
                number = 0xFFFFFFFF + number + 1
            }
            number = number.toString(2);
            return "00000000".substr(number.length) + number;
        }
        function handleKeepalive(bytes, data){
            var tempRaw = (bytes[1] << 8) | bytes[2];
            var temperature = calculateTemperature(tempRaw);
            var humidity = calculateHumidity(bytes[3]);
            var batteryVoltage = ((bytes[4] << 8) | bytes[5])/1000;

            var targetTemperature, powerSourceStatus, lux, pir;
        if(bytes[0] == 1){
            targetTemperature = bytes[6];
            powerSourceStatus = bytes[7];
            lux = (bytes[8] << 8) | bytes[9];
            pir = toBool(bytes[10]);
        }else{
            targetTemperature = ((parseInt(decbin(bytes[6]), 2)) << 8) | parseInt(decbin(bytes[7]), 2)/10;
            powerSourceStatus = bytes[8];
            lux = (bytes[9] << 8) | bytes[10];
            pir = toBool(bytes[11]);
        }

            data.sensorTemperature = Number(temperature.toFixed(2));
            data.relativeHumidity = Number(humidity.toFixed(2));
            data.batteryVoltage = Number(batteryVoltage.toFixed(2));
            data.targetTemperature = targetTemperature;
            data.powerSourceStatus = powerSourceStatus;
            data.lux = lux;
            data.pir = pir;
            return data;
        }
    
        function handleResponse(bytes, data, keepaliveLength){
        var commands = bytes.map(function(byte){
            return ("0" + byte.toString(16)).substr(-2); 
        });
        commands = commands.slice(0,-keepaliveLength);
        var command_len = 0;
    
        commands.map(function (command, i) {
            switch (command) {
                case '04':
                    {
                        command_len = 2;
                        var hardwareVersion = commands[i + 1];
                        var softwareVersion = commands[i + 2];
                        data.deviceVersions = { hardware: Number(hardwareVersion), software: Number(softwareVersion) };
                    }
                break;
                case '12':
                    {
                        command_len = 1;
                        data.keepAliveTime = parseInt(commands[i + 1], 16);
                    }
                break;
                case '14':
                    {
                        command_len = 1;
                        data.childLock = toBool(parseInt(commands[i + 1], 16)) ;
                    }
                break;
                case '15':
                    {
                        command_len = 2;
                        data.temperatureRangeSettings = { min: parseInt(commands[i + 1], 16), max: parseInt(commands[i + 2], 16) };
                    }
                    break;
                case '19':
                    {
                        command_len = 1;
                        var commandResponse = parseInt(commands[i + 1], 16);
                        var periodInMinutes = commandResponse * 5 / 60;
                        data.joinRetryPeriod =  periodInMinutes;
                    }
                break;
                case '1b':
                    {
                        command_len = 1;
                        data.uplinkType = parseInt(commands[i + 1], 16) ;
                    }
                break;
                case '1d':
                    {
                        command_len = 2;
                        var wdpC = commands[i + 1] == '00' ? false : (parseInt(commands[i + 1], 16))
                        var wdpUc = commands[i + 2] == '00' ? false : parseInt(commands[i + 2], 16);
                        data.watchDogParams= { wdpC: wdpC, wdpUc: wdpUc } ;
                    }
                break;
                case '2f':
                    {
                        command_len = 1;
                        data.targetTemperature = parseInt(commands[i + 1], 16) ;
                    }
                break;
                case '30':
                    {
                        command_len = 1;
                        data.manualTargetTemperatureUpdate = parseInt(commands[i + 1], 16) ;
                    }
                break;
                case '32':
                    {
                        command_len = 1;
                        data.heatingStatus = parseInt(commands[i + 1], 16) ;
                    }
                break;
                case '34':
                    {
                        command_len = 1;
                        data.displayRefreshPeriod = parseInt(commands[i + 1], 16) ;
                    }
                break;
                case '36':
                    {
                        command_len = 1;
                        data.sendTargetTempDelay = parseInt(commands[i + 1], 16) ;
                    }
                break;
                case '38':
                    {
                        command_len = 1;
                        data.automaticHeatingStatus = parseInt(commands[i + 1], 16) ;
                    }
                break;
                case '3a':
                    {
                        command_len = 1;
                        data.sensorMode = parseInt(commands[i + 1], 16) ;
                    }
                break;
                case '3d':
                    {
                        command_len = 1;
                        data.pirSensorStatus = parseInt(commands[i + 1], 16) ;
                    }
                break;
                case '3f':
                    {
                        command_len = 1;
                        data.pirSensorSensitivity = parseInt(commands[i + 1], 16) ;
                    }
                break;
                case '41':
                    {
                        command_len = 1;
                        data.currentTemperatureVisibility = parseInt(commands[i + 1], 16) ;
                    }
                break;
                case '43':
                    {
                        command_len = 1;
                        data.humidityVisibility = parseInt(commands[i + 1], 16) ;
                    }
                break;
                case '45':
                    {
                        command_len = 1;
                        data.lightIntensityVisibility = parseInt(commands[i + 1], 16) ;
                    }
                break;
                case '47':
                    {
                        command_len = 1;
                        data.pirInitPeriod = parseInt(commands[i + 1], 16) ;
                    }
                break;
                case '49':
                    {
                        command_len = 1;
                        data.pirMeasurementPeriod = parseInt(commands[i + 1], 16) ;
                    }
                break;
                case '4b':
                    {
                        command_len = 1;
                        data.pirCheckPeriod = parseInt(commands[i + 1], 16) ;
                    }
                break;
                case '4d':
                    {
                        command_len = 1;
                        data.pirBlindPeriod = parseInt(commands[i + 1], 16) ;
                    }
                break;
                case '4f':
                    {
                        command_len = 1;
                        data.temperatureHysteresis = parseInt(commands[i + 1], 16)/10 ;
                    }
                break;
                case '51':
                    {
                        command_len = 2;
                        data.targetTemperature = ((parseInt(commands[i + 1], 16) << 8) | parseInt(commands[i + 2], 16))/10  ;
                    }
                break;
                case '53':
                    {
                        command_len = 1;
                        data.targetTemperatureStep = parseInt(commands[i + 1], 16) / 10;
                    }
                break;
                case '54':
                    {
                        command_len = 2;
                        data.manualTargetTemperatureUpdate = ((parseInt(commands[i + 1], 16) << 8) | parseInt(commands[i + 2], 16))/10;
                    }
                break;
                case 'a0': {
                    command_len = 4;
                    var fuota_address = (parseInt(commands[i + 1], 16) << 24) | 
                                        (parseInt(commands[i + 2], 16) << 16) | 
                                        (parseInt(commands[i + 3], 16) << 8) | 
                                        parseInt(commands[i + 4], 16);
                    var fuota_address_raw = commands[i + 1] + commands[i + 2] + 
                                            commands[i + 3] + commands[i + 4];
                    
                    data.fuota = { fuota_address: fuota_address, fuota_address_raw: fuota_address_raw };
                    break;
                }
                default:
                    break;
            }
            commands.splice(i,command_len);
        });
        return data;
        }
        if (bytes[0] == 1|| bytes[0] == 129) {
            data = handleKeepalive(bytes, data);
        }else{
            var keepaliveLength = 11;
            var potentialKeepAlive = bytes.slice(-12);
            if(potentialKeepAlive[0] == 129) keepaliveLength = 12;
            data = handleResponse(bytes,data, keepaliveLength);
            bytes = bytes.slice(-keepaliveLength);
            data = handleKeepalive(bytes, data);
        }
        return {data: data};
    } catch (e) {
        console.log(e)
        throw new Error('Unhandled data');
    }
}
/**
 * Payload Encoder
 *
 * MClimate Wireless Thermostat
 */

var RAW_VALUE = 0x00;

/* eslint no-redeclare: "off" */
/* eslint-disable */
// Chirpstack v4
function encodeDownlink(input) {
    var encoded = thermostatEncode(input.data || {});
    return { bytes: encoded };
}

// Chirpstack v3
function Encode(obj) {
    return thermostatEncode(obj || {});
}

// The Things Network
function Encoder(obj, port) {
    return thermostatEncode(obj || {});
}
/* eslint-enable */

function thermostatEncode(payload) {
    var encoded = [];

    if ("SetTargetTemp" in payload) {
        encoded = encoded.concat(setTargetTemp(payload.SetTargetTemp));
    }

    if ("Child Lock" in payload) {
        encoded = encoded.concat(setChildLock(payload["Child Lock"]));
    }

    if ("Child Unlock" in payload) {
        encoded = encoded.concat(setChildUnlock(payload["Child Unlock"]));
    }

    if ("Get Childlock Status" in payload) {
        encoded = encoded.concat(getChildLockStatus(payload["Get Childlock Status"]));
    }

    if ("Get Pir Status" in payload) {
        encoded = encoded.concat(getPirStatus(payload["Get Pir Status"]));
    }

    if ("PIR Off" in payload) {
        encoded = encoded.concat(setPirOff(payload["PIR Off"]));
    }

    if ("PIR On" in payload) {
        encoded = encoded.concat(setPirOn(payload["PIR On"]));
    }

    if ("Show temperature" in payload) {
        encoded = encoded.concat(setTemperatureVisibility(payload["Show temperature"], 1));
    }

    if ("Hide temperature" in payload) {
        encoded = encoded.concat(setTemperatureVisibility(payload["Hide temperature"], 0));
    }

    if ("Show humidity" in payload) {
        encoded = encoded.concat(setHumidityVisibility(payload["Show humidity"], 1));
    }

    if ("Hide humidity" in payload) {
        encoded = encoded.concat(setHumidityVisibility(payload["Hide humidity"], 0));
    }

    if ("Show light intensity" in payload) {
        encoded = encoded.concat(setLightVisibility(payload["Show light intensity"], 1));
    }

    if ("Hide light intensity" in payload) {
        encoded = encoded.concat(setLightVisibility(payload["Hide light intensity"], 0));
    }

    if ("Turn off sensor mode" in payload) {
        encoded = encoded.concat(setSensorMode(payload["Turn off sensor mode"], 0));
    }

    if ("Turn on sensor mode" in payload) {
        encoded = encoded.concat(setSensorMode(payload["Turn on sensor mode"], 1));
    }

    if ("setTemperatureRange" in payload) {
        encoded = encoded.concat(setTemperatureRange(payload.setTemperatureRange));
    }

    return encoded;
}

/**
 * set target temperature
 * @param {number} SetTargetTemp unit: °C, range: [5, 30]
 * @example { "SetTargetTemp": 21 }
 */
function setTargetTemp(SetTargetTemp) {
    var temp = parseInt(SetTargetTemp, 10);
    if (isNaN(temp)) {
        throw new Error("SetTargetTemp must be a number");
    }
    if (temp < 5 || temp > 30) {
        throw new Error("SetTargetTemp must be between 5 and 30");
    }

    // 0x2E <temp>
    return [0x2E, temp];
}

/**
 * set target temperature range
 * @param {object} setTemperatureRange
 * @param {number} setTemperatureRange.minTemp unit: °C, range: [5, 29]
 * @param {number} setTemperatureRange.maxTemp unit: °C, range: [6, 30]
 * @example { "setTemperatureRange": { "minTemp": 8, "maxTemp": 25 } }
 */
function setTemperatureRange(setTemperatureRange) {
    if (typeof setTemperatureRange !== "object" || setTemperatureRange === null) {
        throw new Error("setTemperatureRange must be an object");
    }

    var minTemp = setTemperatureRange.minTemp !== undefined
        ? parseInt(setTemperatureRange.minTemp, 10)
        : 5;
    var maxTemp = setTemperatureRange.maxTemp !== undefined
        ? parseInt(setTemperatureRange.maxTemp, 10)
        : 30;

    if (isNaN(minTemp) || isNaN(maxTemp)) {
        throw new Error("setTemperatureRange.minTemp and maxTemp must be numbers");
    }

    if (minTemp < 5 || minTemp > 29) {
        throw new Error("setTemperatureRange.minTemp must be between 5 and 29");
    }
    if (maxTemp < 6 || maxTemp > 30) {
        throw new Error("setTemperatureRange.maxTemp must be between 6 and 30");
    }
    if (minTemp >= maxTemp) {
        throw new Error("setTemperatureRange.minTemp must be less than maxTemp");
    }

    // 0x08 <min> <max>
    return [0x08, minTemp, maxTemp];
}

/**
 * child lock enable
 * @param {any} value ignored, presence of key déclenche la commande
 * @example { "Child Lock": 1 }
 */
function setChildLock(value) {
    return [0x07, 0x01];
}

/**
 * child lock disable
 * @param {any} value ignored
 * @example { "Child Unlock": 1 }
 */
function setChildUnlock(value) {
    return [0x07, 0x00];
}

/**
 * get childlock status
 * @param {any} value ignored
 * @example { "Get Childlock Status": 1 }
 */
function getChildLockStatus(value) {
    return [0x14];
}

/**
 * get pir status
 * @param {any} value ignored
 * @example { "Get Pir Status": 1 }
 */
function getPirStatus(value) {
    return [0x3D];
}

/**
 * pir off
 * @param {any} value ignored
 * @example { "PIR Off": 1 }
 */
function setPirOff(value) {
    return [0x3C, 0x00];
}

/**
 * pir on
 * @param {any} value ignored
 * @example { "PIR On": 1 }
 */
function setPirOn(value) {
    return [0x3C, 0x01];
}

/**
 * temperature visibility
 * @param {any} value ignored
 * @param {number} visible values: (0: hide, 1: show)
 * @example { "Show temperature": 1 }
 */
function setTemperatureVisibility(value, visible) {
    return [0x40, visible ? 0x01 : 0x00];
}

/**
 * humidity visibility
 * @param {any} value ignored
 * @param {number} visible values: (0: hide, 1: show)
 * @example { "Show humidity": 1 }
 */
function setHumidityVisibility(value, visible) {
    return [0x42, visible ? 0x01 : 0x00];
}

/**
 * light intensity visibility
 * @param {any} value ignored
 * @param {number} visible values: (0: hide, 1: show)
 * @example { "Show light intensity": 1 }
 */
function setLightVisibility(value, visible) {
    return [0x44, visible ? 0x01 : 0x00];
}

/**
 * sensor mode
 * @param {any} value ignored
 * @param {number} mode values: (0: off, 1: on)
 * @example { "Turn on sensor mode": 1 }
 */
function setSensorMode(value, mode) {
    return [0x39, mode ? 0x01 : 0x00];
}


module.exports = {
    Encode,
    Decode
};