// Thermokon Sensortechnik GmbH 
// Payload Decoder for Thermokon LoRaWAN devices
// Template: Adaption to corresponding NS/AS necessary
// -Revision A-

// Questions or remarks: steven.jam@thermokon.fr


// https://github.com/ProVuUK/Alliot-decoders/blob/e6ce54b6a64e56c4d651963d945ab47959a7b2e3/Thermokon/thermokon_decoder.js

// Fonctions utilitaires de conversion
function u16_to_s16(u16) {
    var s16 = u16 & 0xFFFF;
    if (0x8000 & s16) {
        s16 = -(0x010000 - s16);
    }
    return s16;
}

function u8_to_s8(u8) {
    var s8 = u8 & 0xFF;
    if (0x80 & s8) {
        s8 = -(0x0100 - s8);
    }
    return s8;
}


function DecodeLNS(fPort, bytes) {
var LPP_PARSER              = 0x0000;
var LPP_DUMMY               = 0x0001;
var LPP_TEMP                = 0x0010;
var LPP_RHUM                = 0x0011;
var LPP_CO2                 = 0x0012;
var LPP_VOC                 = 0x0013;
var LPP_ATM_P               = 0x0030;
var LPP_DP                  = 0x0031;
var LPP_FLOW                = 0x0032;
var LPP_VISIBLE_LIGHT       = 0x0040;
var LPP_OCCU0               = 0x0041;
var LPP_REED0               = 0x0050;
var LPP_CONDENSATION        = 0x0051;
var LPP_VBAT                = 0x0054;
var LPP_SETPOINT            = 0x0063;
var LPP_VBAT_HI_RES         = 0x8540;
var LPP_OCCU1               = 0x9410;
var LPP_REED1               = 0x9500;
var LPP_CONDENSATION_RAW    = 0x9510;
var LPP_DEV_KEY             = 0xC000;
var LPP_CMD                 = 0xC100;
var LPP_LEARN               = 0xC103;
var LPP_BAT_TYPE            = 0xC105;
var LPP_HEARTBEAT           = 0xC106;
var LPP_MEAS_INTERVAL       = 0xC108;
var LPP_CNT_MEAS            = 0xC10A;
var LPP_BIN_LATENCY         = 0xC10B;
var LPP_TLF_MODE            = 0xC120;
var LPP_TLF_ONTIME          = 0xC121;
var LPP_TLF_INTERVAL_0      = 0xC123;
var LPP_TLF_INTERVAL_1      = 0xC125;
var LPP_TLF_INTERVAL_2      = 0xC127;
var LPP_TLF_INTERVAL_3      = 0xC129;
var LPP_TLF_INTERVAL_4      = 0xC12B;
var LPP_TLF_INTERVAL_5      = 0xC12D;
var LPP_LED_MODE            = 0xC134;
var LPP_LED_ONTIME          = 0xC135;
var LPP_LED_INTERVAL_0      = 0xC136;
var LPP_LED_INTERVAL_1      = 0xC137;
var LPP_LED_INTERVAL_2      = 0xC138;
var LPP_LED_INTERVAL_3      = 0xC139;
var LPP_FORCED_UPLINK       = 0xC230;
var LPP_OCCU0ENABLE         = 0x8415;
var LPP_BUTTON              = 0x8550;
var LPP_TEMP_2              = 0x9100;
var LPP_MOISTURE_2          = 0x9140;
var LPP_BUTTON_2            = 0x9550;
var LPP_SETPOINT_2          = 0x9630;
var LPP_TEMP_3              = 0xA100;
var LPP_EPD_VALUE_EXT_OVERLOAD_0 = 0xC194;
var LPP_EPD_VALUE_EXT_OVERLOAD_1 = 0xC19C;
var LPP_EPD_VALUE_EXT_OVERLOAD_2 = 0xC1A4;
var LPP_EPD_VALUE_EXT_OVERLOAD_3 = 0xC1AC;
    
    var decoded = {};
    var data = bytes;

    function u16_to_s16(u16) {
        var s16 = u16 & 0xFFFF;
        if (s16 & 0x8000) {
            s16 = -(0x10000 - s16);
        }
        return s16;
    }

    function u8_to_s8(u8) {
        var s8 = u8 & 0xFF;
        if (s8 & 0x80) {
            s8 = -(0x100 - s8);
        }
        return s8;
    }

    // --- Gestion automatique du type de batterie et conversion en pourcentage ---
    function voltageToBatteryPercentage(voltage) {
        var maxVoltage, minVoltage, absoluteMaxVoltage, percentage;

        if (voltage < 2.0) {
            // Cas batterie 1.5 V (type alcaline ou NiMH)
            minVoltage = 1.0;
            maxVoltage = 1.5;
            absoluteMaxVoltage = 1.9; // Toute tension > 1.5V = 100%

            if (voltage < minVoltage) {
                percentage = 0;
            } else if (voltage >= maxVoltage && voltage <= absoluteMaxVoltage) {
                percentage = 100;
            } else if (voltage > absoluteMaxVoltage) {
                percentage = 100;
            } else {
                percentage = ((voltage - minVoltage) / (maxVoltage - minVoltage)) * 100;
            }
        } else {
            // Cas batterie 3.6 V (type Li-SOCl₂)
            minVoltage = 2.7;
            maxVoltage = 3.6;
            absoluteMaxVoltage = 4.0; // Toute tension > 3.6V = 100%

            if (voltage < minVoltage) {
                percentage = 0;
            } else if (voltage >= maxVoltage && voltage <= absoluteMaxVoltage) {
                percentage = 100;
            } else if (voltage > absoluteMaxVoltage) {
                percentage = 100;
            } else {
                percentage = ((voltage - minVoltage) / (maxVoltage - minVoltage)) * 100;
            }
        }

        // Arrondi au multiple de 20% le plus proche
        percentage = Math.round(percentage / 20) * 20;

        // Clamp entre 0% et 100%
        if (percentage < 0) percentage = 0;
        if (percentage > 100) percentage = 100;

        return percentage;
    }
    
    for (i = 0; i < data.length; i++) {
        var lpp = 0;
        // Vérification si l'identifiant est sur 1 octet (<= 0x7F) ou sur 2 octets sinon
        if (data[i] <= 0x7F) {
            lpp = data[i];
            i++;
        } else {
            lpp = (data[i] << 8) + data[i + 1];
            i += 2;
        }
        
        switch (lpp) {
            case LPP_PARSER:
                decoded.PARSER = u16_to_s16(data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_DUMMY:
                decoded.DUMMY = u8_to_s8(data[i]) / 1;
                break;
            case LPP_TEMP:
                decoded.TEMP = u16_to_s16(data[i] << 8 | data[i + 1]) / 10;
                i++;
                break;
            case LPP_RHUM:
                decoded.RHUM = u8_to_s8(data[i]) / 1;
                break;
            case LPP_CO2:
                decoded.CO2 = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_VOC:
                decoded.VOC = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_ATM_P:
                decoded.ATM_P = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_DP:
                decoded.DP = u16_to_s16((data[i] << 8 | data[i + 1]) / 1);
                i++;
                break;
            case LPP_FLOW:
                decoded.FLOW = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_VISIBLE_LIGHT:
                decoded.VISIBLE_LIGHT = (data[i] << 8 | data[i + 1]) / 1;
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
                decoded.CONDENSATION_RAW = (u16_to_s16(data[i] << 8 | data[i + 1]) / 1) & 0x0FFF;
                i++;
                break;
            case LPP_VBAT:
                tempVBAT = data[i] / (1.0 / 20);
                decoded.VBAT = tempVBAT;
                var vbatVolts = tempVBAT / 1000.0;
                decoded.PBAT = voltageToBatteryPercentage(vbatVolts);
                break;
            case LPP_SETPOINT:
                decoded.SETPOINT = data[i] / 1;
                break;
            case LPP_VBAT_HI_RES:
                decoded.VBAT_HI_RES = (data[i] << 8 | data[i + 1]) / 1;
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
                decoded.CONDENSATION_RAW = u16_to_s16(data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_DEV_KEY:
                decoded.DEV_KEY = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_CMD:
                decoded.CMD = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_LEARN:
                decoded.LEARN = data[i] / 1;
                break;
            case LPP_BAT_TYPE:
                decoded.BAT_TYPE = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_HEARTBEAT:
                decoded.HEARTBEAT = (data[i] << 8 | data[i + 1]) / (1.0 / 60000);
                i++;
                break;
            case LPP_MEAS_INTERVAL:
                decoded.MEAS_INTERVAL = (data[i] << 8 | data[i + 1]) / (1.0 / 1000);
                i++;
                break;
            case LPP_CNT_MEAS:
                decoded.CNT_MEAS = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_BIN_LATENCY:
                decoded.BIN_LATENCY = (data[i] << 8 | data[i + 1]) / (1.0 / 1000);
                i++;
                break;
            case LPP_TLF_MODE:
                decoded.TLF_MODE = data[i] / 1;
                break;
            case LPP_TLF_ONTIME:
                decoded.TLF_ONTIME = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_TLF_INTERVAL_0:
                decoded.TLF_INTERVAL_0 = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_TLF_INTERVAL_1:
                decoded.TLF_INTERVAL_1 = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_TLF_INTERVAL_2:
                decoded.TLF_INTERVAL_2 = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_TLF_INTERVAL_3:
                decoded.TLF_INTERVAL_3 = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_TLF_INTERVAL_4:
                decoded.TLF_INTERVAL_4 = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_TLF_INTERVAL_5:
                decoded.TLF_INTERVAL_5 = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_LED_MODE:
                decoded.LED_MODE = data[i] / 1;
                break;
            case LPP_LED_ONTIME:
                decoded.LED_ONTIME = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_LED_INTERVAL_0:
                decoded.LED_INTERVAL_0 = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_LED_INTERVAL_1:
                decoded.LED_INTERVAL_1 = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_LED_INTERVAL_2:
                decoded.LED_INTERVAL_2 = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_LED_INTERVAL_3:
                decoded.LED_INTERVAL_3 = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            case LPP_FORCED_UPLINK:
                decoded.FORCED_UPLINK = (data[i] << 8 | data[i + 1]) / 1;
                i++;
                break;
            // Cas supplémentaires du second décodeur
            case LPP_OCCU0ENABLE:
                decoded.OCCU0ENABLE = data[i] / 1;
                break;
            case LPP_BUTTON:
                decoded.BUTTON_PRESSED = (data[i] >= 2) ? 1 : 0;
                decoded.BUTTON_LAST_TYPE = ((data[i] & 0x01) >= 1) ? "Long Press" : "Short Press";
                decoded.BUTTON_CNT = data[i] >> 1;
                break;
            case LPP_TEMP_2:
                decoded.TEMP_2 = u16_to_s16((data[i] << 8) | data[i + 1]) / 10;
                i++;
                break;
            case LPP_MOISTURE_2:
                decoded.MOISTURE_2 = ((data[i] << 8) | data[i + 1]) / 1;
                i++;
                break;
            case LPP_BUTTON_2:
                decoded.BUTTON_2_PRESSED = (data[i] >= 2) ? 1 : 0;
                decoded.BUTTON_2_LAST_TYPE = ((data[i] & 0x01) >= 1) ? "Long Press" : "Short Press";
                decoded.BUTTON_2_CNT = data[i] >> 1;
                break;
            case LPP_SETPOINT_2:
                decoded.SETPOINT_2 = ((data[i] << 8) | data[i + 1]) / 10;
                i++;
                break;
            case LPP_TEMP_3:
                decoded.TEMP_3 = u16_to_s16((data[i] << 8) | data[i + 1]) / 10;
                i++;
                break;
            case LPP_EPD_VALUE_EXT_OVERLOAD_0:
                decoded.EPD_VALUE_EXT_OVERLOAD_0 = u16_to_s16((data[i] << 8) | data[i + 1]) / 1;
                i++;
                break;
            case LPP_EPD_VALUE_EXT_OVERLOAD_1:
                decoded.EPD_VALUE_EXT_OVERLOAD_1 = u16_to_s16((data[i] << 8) | data[i + 1]) / 1;
                i++;
                break;
            case LPP_EPD_VALUE_EXT_OVERLOAD_2:
                decoded.EPD_VALUE_EXT_OVERLOAD_2 = u16_to_s16((data[i] << 8) | data[i + 1]) / 1;
                i++;
                break;
            case LPP_EPD_VALUE_EXT_OVERLOAD_3:
                decoded.EPD_VALUE_EXT_OVERLOAD_3 = u16_to_s16((data[i] << 8) | data[i + 1]) / 1;
                i++;
                break;
            default:
                // Si l'identifiant n'est pas reconnu, on arrête le décodage
                i = data.length;
                break;
        }
    }
    return decoded;
}

// Fonction d'entrée pour le décodage uplink
function Decode(input) {
    var warnings = [];
    var data = DecodeLNS(input.fPort, input.bytes);
    return { data: data, warnings: warnings };
}


module.exports = {
	Decode
};