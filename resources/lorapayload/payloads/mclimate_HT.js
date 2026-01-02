/* https://docs.mclimate.eu/mclimate-lorawan-devices/devices/mclimate-ht-sensor-lorawan/ht-sensor-uplink-decoder */

// The Things Industries / Main
function Decode(input) {
    try {
        var bytes = input.bytes;
        var data = {};
        
        function calculateTemperature (rawData) {return (rawData - 400) / 10;}
        function calculateHumidity (rawData) {return (rawData * 100) / 256;}

        function handleKeepalive(bytes) {
            var data = {};

            var temperatureRaw = (bytes[1] << 8) | bytes[2];
            data.sensorTemperature = Number(calculateTemperature(temperatureRaw).toFixed(2));

            data.relativeHumidity = Number(calculateHumidity(bytes[3]).toFixed(2));
            
            var batteryVoltageRaw = (bytes[4] >> 4) & 0x0F;
            data.batteryVoltage = Number((2 + batteryVoltageRaw * 0.1).toFixed(2));
            
            data.thermistorProperlyConnected = (bytes[5] & 0x20) === 0;

            var extT1 = bytes[5] & 0x0F;
            var extT2 = bytes[6];
            data.extThermistorTemperature = data.thermistorProperlyConnected 
                ? Number(((extT1 << 8 | extT2) * 0.1).toFixed(2))
                : 0;
            
            return data;
        }

        function handleResponse(bytes, data) {
             var commands = bytes.map(function (byte) {
                return ("0" + byte.toString(16)).substr(-2);
            });
            commands = commands.slice(0, -7);
            var command_len = 0;

            commands.forEach(function (command, i) {
                switch (command) {
                    case '04':
                        command_len = 2;
                        data.deviceVersions = {
                            hardware: Number(commands[i + 1]),
                            software: Number(commands[i + 2])
                        };
                        break;
                    case '12':
                        command_len = 1;
                        data.keepAliveTime = parseInt(commands[i + 1], 16);
                        break;
                    case '19':
                        command_len = 1;
                        var commandResponse = parseInt(commands[i + 1], 16);
                        data.joinRetryPeriod = (commandResponse * 5) / 60;
                        break;
                    case '1b':
                        command_len = 1;
                        data.uplinkType = parseInt(commands[i + 1], 16);
                        break;
                    case '1d':
                        command_len = 2;
                        data.watchDogParams = {
                            wdpC: commands[i + 1] === '00' ? false : parseInt(commands[i + 1], 16),
                            wdpUc: commands[i + 2] === '00' ? false : parseInt(commands[i + 2], 16)
                        };
                        break;
                    default:
                        break;
                }
                commands.splice(i, command_len);
            });
            return data;
        }

        if (bytes[0] === 1) {
            data = handleKeepalive(bytes);
        } else {
            data = handleResponse(bytes, data);
            bytes = bytes.slice(-7);
            data = handleKeepalive(bytes);
        }

        return { data: data };
    } catch (e) {
        throw new Error(e);
    }
}

module.exports = {
    Decode
};