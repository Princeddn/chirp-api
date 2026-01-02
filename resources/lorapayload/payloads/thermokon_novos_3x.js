// Thermokon NOVOS 3x LPP Payload Decoder
// https://www.thermokon.de/direct/alterra-base/mimes/get/9bea631b4cdbd539f

var LPP_PARSER = 0x0000;
var LPP_DUMMY = 0x0001;
var LPP_TEMP = 0x0010;
var LPP_RHUM = 0x0011;
var LPP_CO2 = 0x0012;
var LPP_VOC = 0x0013;
var LPP_ATM_P = 0x0030;
var LPP_DP =0x0031;
var LPP_FLOW =0x0032;
var LPP_VISIBLE_LIGHT = 0x0040;
var LPP_OCCU0 = 0x0041;
var LPP_REED0 = 0x0050;
var LPP_CONDENSATION = 0x0051;
var LPP_VBAT = 0x0054;
var LPP_SETPOINT = 0x0063;
var LPP_VBAT_HI_RES = 0x8540;
var LPP_OCCU1 = 0x9410;
var LPP_REED1 = 0x9500;
var LPP_CONDENSATION_RAW= 0x9510;
var LPP_DEV_KEY = 0xC000;
var LPP_CMD = 0xC100;
var LPP_LEARN = 0xC103;
var LPP_BAT_TYPE = 0xC105;
var LPP_HEARTBEAT = 0xC106;
var LPP_MEAS_INTERVAL = 0xC108;
var LPP_CNT_MEAS = 0xC10A;
var LPP_BIN_LATENCY = 0xC10B;
var LPP_TLF_MODE = 0xC120;
var LPP_TLF_ONTIME = 0xC121;
var LPP_TLF_INTERVAL_0 = 0xC123;
var LPP_TLF_INTERVAL_1 = 0xC125;
var LPP_TLF_INTERVAL_2 = 0xC127;
var LPP_TLF_INTERVAL_3 = 0xC129;
var LPP_TLF_INTERVAL_4 = 0xC12B;
var LPP_TLF_INTERVAL_5 = 0xC12D;
var LPP_LED_MODE = 0xC134;
var LPP_LED_ONTIME = 0xC135;
var LPP_LED_INTERVAL_0 = 0xC136;
var LPP_LED_INTERVAL_1 = 0xC137;
var LPP_LED_INTERVAL_2 = 0xC138;
var LPP_LED_INTERVAL_3 = 0xC139;
var LPP_FORCED_UPLINK = 0xC230;

function u16_to_s16(u16) {
	var s16 = u16&0xFFFF;
	if (0x8000 & s16){s16 = - (0x010000 - s16);}
	return s16;
}
function u8_to_s8(u8) {
	var s8=u8&0xFF;
	if (0x80 & s8) {s8 = - (0x0100 - s8);}
	return s8;
}

function DecodeLPPPayload(fPort, bytes) {
    var decoded = {};
    var data = bytes;

	for(i=0;i<data.length;i++){
		var lpp = 0;
		if(data[i] <= 0x7F) {lpp = data[i]; i++;}
		else {lpp = (data[i] << 8) + data[i + 1]; i+=2;}

		switch(lpp){
			case LPP_PARSER:
				decoded.PARSER = u16_to_s16(data[i] << 8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_DUMMY:
				decoded.DUMMY = u8_to_s8(data[i]) / 1;
			break;
			case LPP_TEMP:
				decoded.TEMP = u16_to_s16(data[i] << 8 | data[i+1]) / 10;
				i++;
			break;
			case LPP_RHUM:
				decoded.RHUM = u8_to_s8(data[i]) / 1;
			break;
			case LPP_CO2:
				decoded.CO2 = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_VOC:
				decoded.VOC = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_ATM_P:
				decoded.ATM_P = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_DP:
				decoded.DP = u16_to_s16((data[i]<<8 | data[i+1]) / 1);
				i++;
			break;
			case LPP_FLOW:
				decoded.FLOW = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			
			case LPP_VISIBLE_LIGHT:
				decoded.VISIBLE_LIGHT = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_OCCU0:
				decoded.OCCU0_STATE = data[i] & 0x01;
				decoded.OCCU0_CNT = data[i] >> 1;
			break;
			case LPP_REED0:
				decoded.REED0_STATE = data[i] & 0x01;
				decoded.REED0_CNT = data[i] >> 1;
			break;	
			case LPP_CONDENSATION:
				decoded.CONDENSATION_STATE = (data[i] >>> 7);
				decoded.CONDENSATION_RAW = (u16_to_s16(data[i] << 8 | data[i+1]) / 1)&0x0FFF;
				i++;	
			break;
			case LPP_VBAT:
				decoded.VBAT = data[i] / (1.0/20);
			break;
			case LPP_SETPOINT:
				decoded.SETPOINT = data[i] / 1;
			break;
			case LPP_VBAT_HI_RES:
				decoded.VBAT_HI_RES = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_OCCU1:
				decoded.OCCU1_STATE = data[i] & 0x01;
				decoded.OCCU1_CNT = data[i] >> 1;
			break;
			case LPP_REED1:
				decoded.REED1_STATE = data[i] & 0x01;
				decoded.REED1_CNT = data[i] >> 1;
			break;
			case LPP_CONDENSATION_RAW:
				decoded.CONDENSATION_RAW = u16_to_s16(data[i] << 8 | data[i+1]) / 1;	
				i++;
			break;
			case LPP_DEV_KEY:
				decoded.DEV_KEY = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_CMD:
				decoded.CMD = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_LEARN:
				decoded.LEARN = data[i] / 1;
			break;
			case LPP_BAT_TYPE:
				decoded.BAT_TYPE = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_HEARTBEAT:
				decoded.HEARTBEAT = (data[i]<<8 | data[i+1]) / (1.0/60000);
				i++;
			break;
			case LPP_MEAS_INTERVAL:
				decoded.MEAS_INTERVAL = (data[i]<<8 | data[i+1]) / (1.0/1000);
				i++;
			break;
			case LPP_CNT_MEAS:
				decoded.CNT_MEAS = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_BIN_LATENCY:
				decoded.BIN_LATENCY = (data[i]<<8 | data[i+1]) / (1.0/1000);
				i++;
			break;
			case LPP_TLF_MODE:
				decoded.TLF_MODE = data[i] / 1;
			break;
			case LPP_TLF_ONTIME:
				decoded.TLF_ONTIME = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_TLF_INTERVAL_0:
				decoded.TLF_INTERVAL_0 = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_TLF_INTERVAL_1:
				decoded.TLF_INTERVAL_1 = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_TLF_INTERVAL_2:
				decoded.TLF_INTERVAL_2 = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_TLF_INTERVAL_3:
				decoded.TLF_INTERVAL_3 = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_TLF_INTERVAL_4:
				decoded.TLF_INTERVAL_4 = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_TLF_INTERVAL_5:
				decoded.TLF_INTERVAL_5 = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_LED_MODE:
				decoded.LED_MODE = data[i] / 1;
			break;
			case LPP_LED_ONTIME:
				decoded.LED_ONTIME = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_LED_INTERVAL_0:
				decoded.LED_INTERVAL_0 = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_LED_INTERVAL_1:
				decoded.LED_INTERVAL_1 = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_LED_INTERVAL_2:
				decoded.LED_INTERVAL_2 = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_LED_INTERVAL_3:
				decoded.LED_INTERVAL_3 = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			case LPP_FORCED_UPLINK:
				decoded.FORCED_UPLINK = (data[i]<<8 | data[i+1]) / 1;
				i++;
			break;
			default: //somthing is wrong with data
				i = data.length;
			break;
		}
	}
	return decoded;
}

function Decode(input) {
	var warnings = [];
	warnings.push();
	var data = DecodeLPPPayload(input.fPort,input.bytes);
	return {data,warnings};
}

module.exports = {
	Decode
};