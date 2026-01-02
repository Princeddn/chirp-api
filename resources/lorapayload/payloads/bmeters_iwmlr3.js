/* https://github.com/IoTThinks/lorawan-devices/blob/master/vendor/b-meters/iwmlr3.js */
function Decode(input) {
  input.fPort = 1;
  var data = {};

  function toHexLE(bytes) {
      return bytes
          .slice()
          .reverse()
          .map(b => b.toString(16).padStart(2, '0'))
          .join('');
  }

  function bytesToIntBE(bytes) {
      return bytes.reduce((acc, b) => (acc << 8) + b, 0);
  }

  function bcdToInt (b) {
    return ((b >> 4) & 0x0f) * 10 + (b & 0x0f);
  }

  switch (parseInt(input.fPort, 10)) {
      case 1:
          var appCodeHex = input.bytes[0].toString(16).padStart(2, '0');
          data.application = appCodeHex;

          if (appCodeHex === '44') {
              data.absValue   = toHexLE(input.bytes.slice(1, 5));
              data.revFlow    = toHexLE(input.bytes.slice(5, 9));
              var idxK = input.bytes[9];
              var K = idxK === 0x01 ? 10 : idxK === 0x02 ? 100 : 1;
              var med = input.bytes[10];
              data.mediumValue = med === 0x00 ? 'Water' : med === 0x01 ? 'Hot Water' : 'Unknown';
              data.vif        = bcdToInt(input.bytes[11]) * K;
              var alarm       = input.bytes[12];
              data.alarmMagnetic    = (alarm & 0x01) ? 1 : 0;
              data.alarmRemoval     = (alarm & 0x02) ? 1 : 0;
              data.alarmSensorFraud = (alarm & 0x04) ? 1 : 0;
              data.alarmLeakage     = (alarm & 0x08) ? 1 : 0;
              data.alarmReverseFlow = (alarm & 0x10) ? 1 : 0;
              data.alarmLowBattery  = (alarm & 0x20) ? 1 : 0;
              var tempRaw     = bytesToIntBE(input.bytes.slice(13, 15));
              var isNeg       = (tempRaw & 0x8000) !== 0;
              data.temp       = (isNeg ? -(tempRaw & 0x7FFF) : tempRaw) / 10.0;
          }
          else if (appCodeHex === '07') {
              var last3 = input.bytes.slice(-3);
              data.firmware = bytesToIntBE(last3);
          }
          else if (appCodeHex === '17') {
            var rawFwd = bytesToIntBE(input.bytes.slice(6, 10));
            var unitBits = rawFwd >>> 30;
            var count = rawFwd & 0x3FFFFFFF;
            var factor = unitBits === 0 ? 1
                      : unitBits === 1 ? 10
                      : unitBits === 2 ? 100
                      : null;
            data.fwdCnt = factor !== null
              ? count * factor
              : 'Invalid unit code';
            data.backwardCnt = input.bytes[10];
          }
          else {
              data.error = 'Unknown appCode 0x' + appCodeHex;
          }

          return { data };

      default:
          return { errors: ['unknown FPort'] };
  }
}

module.exports = {
  Decode
};
