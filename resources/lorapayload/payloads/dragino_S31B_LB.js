/***
 * Dragino S31B-LB Payload Decoder for LoRaWAN
 * https://wiki.dragino.com/xwiki/bin/view/Main/User%20Manual%20for%20LoRaWAN%20End%20Nodes/S31-LB_S31B-LB/
 *
 */

function datalog(i,bytes){
  // Format DATALOG (11 bytes par entrée):
  // Bytes[0-1]: Ignore field (réservé, = 0x0000)
  // Bytes[2-3]: Humidité (big-endian)
  // Bytes[4-5]: Température (big-endian, complément à 2)
  // Byte[6]: Flags (bit1=alarm, bit0=poll/sampling)
  // Bytes[7-10]: Unix Timestamp (4 bytes, big-endian)

  var hum = parseFloat(((bytes[2+i]<<24>>16 | bytes[3+i])/10).toFixed(1));

  var temp = parseFloat(((bytes[4+i]<<24>>16 | bytes[5+i])/10).toFixed(1));

  var alarm_flag = (bytes[6+i] & 0x02) ? "High":"Low";
  var poll_flag = (bytes[6+i] & 0x01) ? "True":"False";

  // Timestamp sur bytes 7-10 (4 bytes)
  var timestamp = ((bytes[7+i]<<24 | bytes[8+i]<<16 | bytes[9+i]<<8 | bytes[10+i]) >>> 0);
  var date = getMyDate(timestamp.toString(10));

  var string='['+hum+','+temp+','+alarm_flag+','+poll_flag+','+date+']';

  return string;
}

function getzf(c_num){
  if(parseInt(c_num) < 10)
    c_num = '0' + c_num;

  return c_num;
}

function getMyDate(str){
  var c_Date;
  if(str > 9999999999)
    c_Date = new Date(parseInt(str));
  else
    c_Date = new Date(parseInt(str) * 1000);

  var c_Year = c_Date.getFullYear(),
  c_Month = c_Date.getMonth()+1,
  c_Day = c_Date.getDate(),
  c_Hour = c_Date.getHours(),
  c_Min = c_Date.getMinutes(),
  c_Sen = c_Date.getSeconds();
  var c_Time = c_Year +'-'+ getzf(c_Month) +'-'+ getzf(c_Day) +' '+ getzf(c_Hour) +':'+ getzf(c_Min) +':'+getzf(c_Sen);

  return c_Time;
}


function Decode(input) {
    var bytes = input.bytes;
    var fPort = input.fPort;
    var decoded={};

  // Si fPort n'est pas fourni, le déduire de la longueur du payload
  if (!fPort || fPort === '') {
    if (bytes.length === 7) {
      fPort = 0x05;
    } else if (bytes.length === 11) {
      fPort = 0x02;
    } else if (bytes.length % 11 === 0 && bytes.length > 11) {
      fPort = 0x03;
    }
  }

  //S31B-LB Decode
  if(fPort==0x02)
  {
    // Vérifier la longueur du payload (doit être 11 bytes)
    if(bytes.length != 11) {
      decoded.Error = "Invalid payload length for fPort 2. Expected 11 bytes, got " + bytes.length;
      return decoded;
    }

    decoded.Node_type="S31-LB";
    var mode=(bytes[6] & 0x7C)>>2;

    if(mode===0)
    {
      // Format fPort 2 (données en temps réel):
      // Bytes[0-1]: Battery (big-endian)
      // Bytes[2-5]: Unix Timestamp (big-endian)
      // Byte[6]: Status (mode, alarm, door)
      // Bytes[7-8]: Temperature (little-endian, complément à 2)
      // Bytes[9-10]: Humidity (little-endian)

      decoded.BatV=(bytes[0]<<8 | bytes[1])/1000;
      decoded.EXTI_Trigger=(bytes[6] & 0x01)? "1":"0";
      decoded.Door_status=(bytes[6] & 0x80)? "0":"1";

      // Température: utilise le décalage arithmétique pour gérer le complément à 2
      decoded.TempC_SHT31= parseFloat(((bytes[7]<<24>>16 | bytes[8])/10).toFixed(1));

      // Humidité: valeur non signée
      decoded.Hum_SHT31=parseFloat(((bytes[9]<<8 | bytes[10])/10).toFixed(1));

      decoded.Data_time= getMyDate((bytes[2]<<24 | bytes[3]<<16 | bytes[4]<<8 | bytes[5]).toString(10));
    }
    else if(mode==31)
    {
      decoded.SHTEMP_MIN= bytes[7]<<24>>24;
      decoded.SHTEMP_MAX= bytes[8]<<24>>24;
      decoded.SHHUM_MIN= bytes[9];
      decoded.SHHUM_MAX= bytes[10];
    }
    return decoded;
  }

  if (fPort === 0x03) {
    decoded.Node_type = "S31-LB";

    // Le flag PNACKMD est dans le byte 6 du premier datalog
    var pnack = ((bytes[6]>>7)&0x01) ? "1":"0";

    var dataArr = [];
    for (var i = 0; i < bytes.length; i += 11) {
      if(i + 10 <= bytes.length - 1) {
        dataArr.push(datalog(i, bytes));
      }
    }
    // Jointure des entrées
    decoded.DATALOG = dataArr.join(',');
    decoded.PNACKMD = pnack;

    return decoded;
  }

  if (fPort === 0x05) {
    // Vérifier la longueur du payload (doit être 7 bytes)
    if(bytes.length != 7) {
      decoded.Error = "Invalid payload length for fPort 5. Expected 7 bytes, got " + bytes.length;
      return decoded;
    }

    decoded.Node_type = "S31-LB";

    decoded.SENSOR_MODEL = (bytes[0] === 0x0A) ? "S31-LB" : "UNKNOWN";
    decoded.SUB_BAND = (bytes[4] === 0xff) ? "NULL" : bytes[4];

    var bandMap = {
      0x01: "EU868", 0x02: "US915", 0x03: "IN865", 0x04: "AU915",
      0x05: "KZ865", 0x06: "RU864", 0x07: "AS923", 0x08: "AS923_1",
      0x09: "AS923_2", 0x0A: "AS923_3", 0x0B: "CN470", 0x0C: "EU433",
      0x0D: "KR920", 0x0E: "MA869"
    };
    decoded.FREQUENCY_BAND = bandMap[bytes[3]] || "UNKNOWN";

    decoded.FIRMWARE_VERSION = (bytes[1] & 0x0f) + "." + ((bytes[2] >> 4) & 0x0f) + "." + (bytes[2] & 0x0f);
    decoded.BAT = (bytes[5] << 8 | bytes[6]) / 1000;

    return decoded;
  }

  // fPort non supporté
  decoded.Error = "Unsupported fPort: " + fPort;
  return decoded;
}
module.exports = { Decode};
