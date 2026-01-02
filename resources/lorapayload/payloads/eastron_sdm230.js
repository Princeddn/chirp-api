// round a number to a set number of places whilst avoiding floating point precision errors

function epsilonRound(num, places) {
    return Math.round((num + Math.pow(2,-52)) * Math.pow(10,places)) / Math.pow(10,places);
}

// convert a byte to uint8

function bytesToUInt8(bytes) {
    return parseInt(bytes[0]);
}

// convert 2 bytes to a uint16

function bytesToUInt16(bytes) {
    console.log(bytes);
    var result = (bytes[0] << 8) | bytes[1];
    return parseInt(result);
}

// convert 4 bytes to a uint32

function bytesToUInt32(bytes) {
    var result = (bytes[0] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3];
    return parseInt(result);
}

// convert 4 bytes to a float32

function bytesToFloat32(bytes) {
    var bits = bytes[0]<<24 | bytes[1]<<16 | bytes[2]<<8 | bytes[3];
    var sign = (bits>>>31 === 0) ? 1.0 : -1.0;
    var e = bits>>>23 & 0xff;
    var m = (e === 0) ? (bits & 0x7fffff)<<1 : (bits & 0x7fffff) | 0x800000;
    var f = sign * m * Math.pow(2, e - 150);
    return parseFloat(f);
}

// decode a lorawan payload

function Decode(fPort, bytes, variables) {
  
  return {
	serialNumber: bytesToUInt32(bytes.slice(0,4)),
	energy: epsilonRound(bytesToFloat32(bytes.slice(6,10)),5),
	frequency: epsilonRound(bytesToFloat32(bytes.slice(10,14)),5),
	powerFactor: epsilonRound(bytesToFloat32(bytes.slice(14,18)),5),
	maxDemand: epsilonRound(bytesToFloat32(bytes.slice(18,22)),5),
	current: epsilonRound(bytesToFloat32(bytes.slice(22,26)),5)
  };
  
}

module.exports = {
    Decode
};