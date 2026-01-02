function decodeUplink(input) {
        return { 
            data: Decode(input.fPort, input.bytes, input.variables)
        };   
}
function Decode(input) {
    bytes = input.bytes;
    port = input.fPort;
    let decoded = {};
    //port = 2;

    var poll_message_status=(bytes[2]&0x40)>>6;


    decoded.Ext= bytes[2]&0x0F;
    decoded.BatV= ((bytes[0]<<8 | bytes[1]) & 0x3FFF)/1000;
    decoded.Node_type="LTC2";
    if(decoded.Ext==0x01)
    {
    decoded.Temp_Channel1=parseFloat(((bytes[3]<<24>>16 | bytes[4])/100).toFixed(2));
    decoded.Temp_Channel2=parseFloat(((bytes[5]<<24>>16 | bytes[6])/100).toFixed(2));
    }
    else if(decoded.Ext==0x02)
    {
    decoded.Temp_Channel1=parseFloat(((bytes[3]<<24>>16 | bytes[4])/10).toFixed(1));
    decoded.Temp_Channel2=parseFloat(((bytes[5]<<24>>16 | bytes[6])/10).toFixed(1));
    }
    else if(decoded.Ext==0x03)
    {
    decoded.Res_Channel1=parseFloat(((bytes[3]<<8 | bytes[4])/100).toFixed(2));
    decoded.Res_Channel2=parseFloat(((bytes[5]<<8 | bytes[6])/100).toFixed(2));
    }

    decoded.Systimestamp=(bytes[7]<<24 | bytes[8]<<16 | bytes[9]<<8 | bytes[10] );


    if(poll_message_status===0)
    {
    if(bytes.length==11)
    {
        return decoded;
    }
    }

}


function Encode(obj) {
    return milesightDeviceEncode(obj);
}


function milesightDeviceEncode(payload) {
    var encoded = [];

    if ("setRCable" in payload) {
        encoded = encoded.concat(setRCable(payload.setRCable));
    }
    return encoded;
}


/**
 * setRCable
 * @param {object} setRCable
 * @param {number} setRCable.ch1 range: [0, 65535]
 * @param {number} setRCable.ch2 range: [0, 65535]
 * @example { "setRCable": { "ch1": 296, "ch2": 300 } }
 */
function setRCable(setRCable) {
    var ch1 = setRCable.ch1;
    var ch2 = setRCable.ch2;

    if (typeof ch1 !== "number") {
        throw new Error("setRCable.ch1 must be a number");
    }
    if (ch1 < 0 || ch1 > 65535) {
        throw new Error("setRCable.ch1 must be in range [0, 65535]");
    }
    if (typeof ch2 !== "number") {
        throw new Error("setRCable.ch2 must be a number");
    }
    if (ch2 < 0 || ch2 > 65535) {
        throw new Error("setRCable.ch2 must be in range [0, 65535]");
    }

    return [
        0xA8,
        (ch1 >> 8) & 0xff,
        ch1 & 0xff,
        (ch2 >> 8) & 0xff,
        ch2 & 0xff
    ];
}


module.exports = { 
    Decode,
    Encode
};