function decodeUplink(input) {
        return {
            data: Decode(input.fPort, input.bytes, input.variables)
        };
}
function Decode(input) {
    bytes = input.bytes;
    port = input.fPort;
    var decode = {};
    port = 2;

//LSN50 Decode
if(port==0x02)
{
  var mode=(bytes[6] & 0x7C)>>2;

  decode.Digital_IStatus= (bytes[6] & 0x02)? "H":"L";

  if(mode!=2)
  {
    decode.BatV= (bytes[0]<<8 | bytes[1])/1000;
    if((bytes[2]==0x7f)&&(bytes[3]==0xff))
      decode.TempC1= "NULL";
    else
      decode.TempC1= parseFloat(((bytes[2]<<24>>16 | bytes[3])/10).toFixed(1));
    if(mode!=8)
      decode.ADC_CH0V= (bytes[4]<<8 | bytes[5])/1000;
  }

  if((mode!=5)&&(mode!=6))
  {
  	decode.EXTI_Trigger= (bytes[6] & 0x01)? "TRUE":"FALSE";
    decode.Door_status= (bytes[6] & 0x80)? "CLOSE":"OPEN";
  }

  if(mode=='0')
  {
    decode.Work_mode="IIC";
    if((bytes[9]<<8 | bytes[10])===0)
      decode.Illum= (bytes[7]<<8 | bytes[8]);
    else
    {
      if(((bytes[7]==0x7f)&&(bytes[8]==0xff))||((bytes[7]==0xff)&&(bytes[8]==0xff)))
        decode.TempC_SHT= "NULL";
      else
        decode.TempC_SHT= parseFloat(((bytes[7]<<24>>16 | bytes[8])/10).toFixed(1));

      if((bytes[9]==0xff)&&(bytes[10]==0xff))
        decode.Hum_SHT= "NULL";
      else
        decode.Hum_SHT= parseFloat(((bytes[9]<<8 | bytes[10])/10).toFixed(1));
    }
  }
  else if(mode=='1')
  {
    decode.Work_mode="Distance";

    if((bytes[7]===0x00)&&(bytes[8]===0x00))
      decode.Distance_cm= "NULL";
    else
      decode.Distance_cm= parseFloat(((bytes[7]<<8 | bytes[8])/10).toFixed(1));

    if(!((bytes[9]==0xff)&&(bytes[10]==0xff)))
      decode.Distance_signal_strength= (bytes[9]<<8 | bytes[10]);
  }
  else if(mode=='2')
  {
    decode.Work_mode="3ADC+IIC";
    decode.BatV= bytes[11]/10;
    decode.ADC_CH0V= (bytes[0]<<8 | bytes[1])/1000;
    decode.ADC_CH1V= (bytes[2]<<8 | bytes[3])/1000;
    decode.ADC_CH4V= (bytes[4]<<8 | bytes[5])/1000;
    if((bytes[9]<<8 | bytes[10])===0)
      decode.Illum= (bytes[7]<<8 | bytes[8]);
    else
    {
      if(((bytes[7]==0x7f)&&(bytes[8]==0xff))||((bytes[7]==0xff)&&(bytes[8]==0xff)))
        decode.TempC_SHT= "NULL";
      else
        decode.TempC_SHT= parseFloat(((bytes[7]<<24>>16 | bytes[8])/10).toFixed(1));

      if((bytes[9]==0xff)&&(bytes[10]==0xff))
        decode.Hum_SHT= "NULL";
      else
        decode.Hum_SHT= parseFloat(((bytes[9]<<8 | bytes[10])/10).toFixed(1));
    }
  }
  else if(mode=='3')
  {
    decode.Work_mode="3DS18B20";
    if((bytes[7]==0x7f)&&(bytes[8]==0xff))
      decode.TempC2= "NULL";
    else
      decode.TempC2= parseFloat(((bytes[7]<<24>>16 | bytes[8])/10).toFixed(1));

    if((bytes[9]==0x7f)&&(bytes[10]==0xff))
      decode.TempC3= "NULL";
    else
      decode.TempC3= parseFloat(((bytes[9]<<24>>16 | bytes[10])/10).toFixed(1));
  }
  else if(mode=='4')
  {
    decode.Work_mode="Weight";
    decode.Weight= (bytes[9]<<24 | bytes[10]<<16 | bytes[7]<<8 | bytes[8]);
  }
  else if(mode=='5')
  {
    decode.Work_mode="1Count";
    decode.Count= (bytes[7]<<24 | bytes[8]<<16 | bytes[9]<<8 | bytes[10])>>>0;
  }
  else if(mode=='6')
  {
    decode.Work_mode="3Interrupt";
    decode.EXTI1_Trigger= (bytes[6] & 0x01)? "TRUE":"FALSE";
    decode.EXTI1_Status= (bytes[6] & 0x80)? "CLOSE":"OPEN";
    decode.EXTI2_Trigger= (bytes[7] & 0x10)? "TRUE":"FALSE";
    decode.EXTI2_Status= (bytes[7] & 0x01)? "CLOSE":"OPEN";
    decode.EXTI3_Trigger= (bytes[8] & 0x10)? "TRUE":"FALSE";
    decode.EXTI3_Status= (bytes[8] & 0x01)? "CLOSE":"OPEN";
  }
  else if(mode=='7')
  {
    decode.Work_mode="3ADC+1DS18B20";
    decode.ADC_CH1V= (bytes[7]<<8 | bytes[8])/1000;
    decode.ADC_CH4V= (bytes[9]<<8 | bytes[10])/1000;
  }
  else if(mode=='8')
  {
    decode.Work_mode="3DS18B20+2Count";
    if((bytes[4]==0x7f)&&(bytes[5]==0xff))
      decode.TempC2= "NULL";
    else
      decode.TempC2= parseFloat(((bytes[4]<<24>>16 | bytes[5])/10).toFixed(1));

    if((bytes[7]==0x7f)&&(bytes[8]==0xff))
      decode.TempC3= "NULL";
    else
      decode.TempC3= parseFloat(((bytes[7]<<24>>16 | bytes[8])/10).toFixed(1));

    decode.Count1= (bytes[9]<<24 | bytes[10]<<16 | bytes[11]<<8 | bytes[12])>>>0;
    decode.Count2= (bytes[13]<<24 | bytes[14]<<16 | bytes[15]<<8 | bytes[16])>>>0;
  }
  decode.Node_type="LSN50";
  }

  else if(port==5)
  {
  	var freq_band;
  	var sub_band;

    if(bytes[0]==0x01)
        freq_band="EU868";
  	else if(bytes[0]==0x02)
        freq_band="US915";
  	else if(bytes[0]==0x03)
        freq_band="IN865";
  	else if(bytes[0]==0x04)
        freq_band="AU915";
  	else if(bytes[0]==0x05)
        freq_band="KZ865";
  	else if(bytes[0]==0x06)
        freq_band="RU864";
  	else if(bytes[0]==0x07)
        freq_band="AS923";
  	else if(bytes[0]==0x08)
        freq_band="AS923_1";
  	else if(bytes[0]==0x09)
        freq_band="AS923_2";
  	else if(bytes[0]==0x0A)
        freq_band="AS923_3";
  	else if(bytes[0]==0x0F)
        freq_band="AS923_4";
  	else if(bytes[0]==0x0B)
        freq_band="CN470";
  	else if(bytes[0]==0x0C)
        freq_band="EU433";
  	else if(bytes[0]==0x0D)
        freq_band="KR920";
  	else if(bytes[0]==0x0E)
        freq_band="MA869";

    if(bytes[1]==0xff)
      sub_band="NULL";
	  else
      sub_band=bytes[1];

	  var firm_ver= (bytes[2]&0x0f)+'.'+(bytes[3]>>4&0x0f)+'.'+(bytes[3]&0x0f);

	  var tdc_time= bytes[4]<<16 | bytes[5]<<8 | bytes[6];

  	decode.FIRMWARE_VERSION = firm_ver;
  	decode.FREQUENCY_BAND = freq_band;
  	decode.SUB_BAND = sub_band;
  	decode.TDC_sec = tdc_time;
  }

  return { decode };
}


function Encode(obj) {
    return lsn50DeviceEncode(obj);
}


function lsn50DeviceEncode(payload) {
    var encoded = [];

    if ("setWorkMode" in payload) {
        encoded = encoded.concat(setWorkMode(payload.setWorkMode));
    }
    if ("setInterruptMode" in payload) {
        encoded = encoded.concat(setInterruptMode(payload.setInterruptMode));
    }
    if ("setInterruptModeSingle" in payload) {
        encoded = encoded.concat(setInterruptModeSingle(payload.setInterruptModeSingle));
    }
    if ("set5VTime" in payload) {
        encoded = encoded.concat(set5VTime(payload.set5VTime));
    }
    if ("setWeightZero" in payload) {
        encoded = encoded.concat(setWeightZero(payload.setWeightZero));
    }
    if ("setWeightGap" in payload) {
        encoded = encoded.concat(setWeightGap(payload.setWeightGap));
    }
    return encoded;
}


/**
 * setWorkMode - Set work mode for LSN50V2
 * @param {number|string} mode - Work mode (0: IIC, 1: Distance, 2: 3ADC+IIC, 3: 3DS18B20, 4: Weight, 5: 1Count, 6: 3Interrupt, 7: 3ADC+1DS18B20, 8: 3DS18B20+2Count)
 * @example { "setWorkMode": 2 }
 * @example { "setWorkMode": "3" }
 * Downlink: 0A 03 (Equivalent to AT+MOD=3)
 */
function setWorkMode(mode) {
    if (typeof mode === "string") {
        mode = parseInt(mode, 10);
    }

    if (typeof mode !== "number" || isNaN(mode)) {
        throw new Error("setWorkMode must be a number");
    }
    if (mode < 0 || mode > 8) {
        throw new Error("setWorkMode must be in range [0, 8] (0: IIC, 1: Distance, 2: 3ADC+IIC, 3: 3DS18B20, 4: Weight, 5: 1Count, 6: 3Interrupt, 7: 3ADC+1DS18B20, 8: 3DS18B20+2Count)");
    }

    return [
        0x0A,
        mode & 0xff
    ];
}


/**
 * setInterruptMode - Configure interrupt mode for LSN50V2
 * @param {object} setInterruptMode
 * @param {number} setInterruptMode.pin - Pin number (0: PB14, 1: PB15, 2: PA4)
 * @param {number} setInterruptMode.mode - Interrupt mode (0: Disabled, 1: Falling or Rising, 2: Falling, 3: Rising)
 * @example { "setInterruptMode": { "pin": 0, "mode": 1 } }
 * @example { "setInterruptMode": "0|1" }
 * Downlink: 06 00 00 01 (Equivalent to AT+INTMOD1=1)
 */
function setInterruptMode(setInterruptMode) {
    var pin, mode;

    // Support string format "pin|mode"
    if (typeof setInterruptMode === "string") {
        var parts = setInterruptMode.split("|");
        if (parts.length !== 2) {
            throw new Error("setInterruptMode string must be in format 'pin|mode' (e.g., '0|1')");
        }
        pin = parseInt(parts[0], 10);
        mode = parseInt(parts[1], 10);
    } else if (typeof setInterruptMode === "object") {
        pin = setInterruptMode.pin;
        mode = setInterruptMode.mode;
    } else {
        throw new Error("setInterruptMode must be an object or a string");
    }

    if (typeof pin !== "number" || isNaN(pin)) {
        throw new Error("setInterruptMode.pin must be a number");
    }
    if (pin < 0 || pin > 2) {
        throw new Error("setInterruptMode.pin must be in range [0, 2] (0: PB14, 1: PB15, 2: PA4)");
    }
    if (typeof mode !== "number" || isNaN(mode)) {
        throw new Error("setInterruptMode.mode must be a number");
    }
    if (mode < 0 || mode > 3) {
        throw new Error("setInterruptMode.mode must be in range [0, 3] (0: Disabled, 1: Falling or Rising, 2: Falling, 3: Rising)");
    }

    return [
        0x06,
        0x00,
        pin & 0xff,
        mode & 0xff
    ];
}


/**
 * setInterruptModeSingle - Set global interrupt mode (simple version)
 * @param {number|string} mode - Interrupt mode (0: Disabled, 1: Falling or Rising, 2: Falling, 3: Rising)
 * @example { "setInterruptModeSingle": 3 }
 * @example { "setInterruptModeSingle": "2" }
 * Downlink: 06 00 00 03 (Equivalent to AT+INTMOD=3)
 */
function setInterruptModeSingle(mode) {
    if (typeof mode === "string") {
        mode = parseInt(mode, 10);
    }

    if (typeof mode !== "number" || isNaN(mode)) {
        throw new Error("setInterruptModeSingle must be a number");
    }
    if (mode < 0 || mode > 3) {
        throw new Error("setInterruptModeSingle must be in range [0, 3] (0: Disabled, 1: Falling or Rising, 2: Falling, 3: Rising)");
    }

    return [
        0x06,
        0x00,
        0x00,
        mode & 0xff
    ];
}


/**
 * set5VTime - Set 5V power open time during sampling
 * @param {number|string} time_ms - Time in milliseconds (0-65535)
 * @example { "set5VTime": 1000 }
 * @example { "set5VTime": "1500" }
 * Downlink: 07 03 E8 (Equivalent to AT+5VT=1000)
 */
function set5VTime(time_ms) {
    if (typeof time_ms === "string") {
        time_ms = parseInt(time_ms, 10);
    }

    if (typeof time_ms !== "number" || isNaN(time_ms)) {
        throw new Error("set5VTime must be a number");
    }
    if (time_ms < 0 || time_ms > 65535) {
        throw new Error("set5VTime must be in range [0, 65535] milliseconds");
    }

    return [
        0x07,
        (time_ms >> 8) & 0xff,
        time_ms & 0xff
    ];
}


/**
 * setWeightZero - Set weight to 0g (Zero Calibration)
 * @param {boolean|number|string} enable - Enable zero calibration (any truthy value)
 * @example { "setWeightZero": true }
 * @example { "setWeightZero": 1 }
 * Downlink: 08 01 (Equivalent to AT+WEIGRE)
 */
function setWeightZero(enable) {
    // Accept any truthy value
    return [
        0x08,
        0x01
    ];
}


/**
 * setWeightGap - Set GAP Value (calibrate factor) of measurement
 * @param {number|string} gap - GAP value (0-6553.5, will be multiplied by 10)
 * @example { "setWeightGap": 403.0 }
 * @example { "setWeightGap": "500.5" }
 * Downlink: 08 02 0F BB (Equivalent to AT+WEIGAP=403.0)
 */
function setWeightGap(gap) {
    if (typeof gap === "string") {
        gap = parseFloat(gap);
    }

    if (typeof gap !== "number" || isNaN(gap)) {
        throw new Error("setWeightGap must be a number");
    }
    if (gap < 0 || gap > 6553.5) {
        throw new Error("setWeightGap must be in range [0, 6553.5]");
    }

    // Convert to integer by multiplying by 10
    var gap_int = Math.round(gap * 10);

    return [
        0x08,
        0x02,
        (gap_int >> 8) & 0xff,
        gap_int & 0xff
    ];
}


module.exports = {
    Decode,
    Encode
};
