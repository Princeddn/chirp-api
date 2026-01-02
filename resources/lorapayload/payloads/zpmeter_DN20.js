/**
 * ZPMeter DN20 - Ultrasonic Water Meter with LoRaWAN
 * Payload Decoder and Encoder
 *
 * Device: ZPMeter DN20 Ultrasonic Water Meter
 * Manufacturer: Hangzhou Zhongpei Electronics Co., Ltd.
 * Protocol: LoRaWAN
 *
 * @product ZPMeter DN20
 */


// Chirpstack v3
function Decode(input) {
    var bytes = input.bytes;
    return zpmeterDeviceDecode(bytes);
}

/**
 * Main decoder function for ZPMeter DN20
 * @param {Array} bytes - The payload bytes to decode
 * @returns {Object} decoded - The decoded data object
 */
function zpmeterDeviceDecode(bytes) {
    var decoded = {};

    if (bytes.length < 40) {
        return decoded;
    }

    // Positive cumulative flow (bytes 13-17: 0x2C 25 00 00 00 → 0.025 m³)
    // Format: [type][value_bcd][00][00][00] - use only byte[1] as BCD
    decoded.positive_flow_m3 = bcdToNumber([bytes[14]], 0.001);

    // Reverse cumulative flow (bytes 18-22: 0x2C 25 00 00 00 → 0.025 m³)
    decoded.reverse_flow_m3 = bcdToNumber([bytes[19]], 0.001);

    // Instantaneous flow (bytes 23-27: 0x35 70 01 00 00 → 0.0170 m³/h)
    // Format: [type][value_low][value_high][00][00] - use bytes[1-2] as little-endian BCD
    decoded.instantaneous_flow_m3h = bcdToNumber([bytes[25], bytes[24]], 0.0001);

    // Temperature (bytes 28-30: 00 18 00 → 18.00°C)
    // Format: [00][temp_bcd][00] - use only byte[1] as BCD
    decoded.temperature_c = bcdToNumber([bytes[29]], 1.0);

    // Timestamp (bytes 32-38: 7 bytes BCD for second, minute, hour, day, month, year, century)
    decoded.timestamp = decodeTimestamp(bytes.slice(32, 39));

    // Status word (bytes 39-40: 40 00 → 0x4000)
    decoded.status_word = (bytes[39] << 8) | bytes[40];
    decoded.status = decodeStatus(decoded.status_word);

    return decoded;
}

// ============================================================================
// HELPER FUNCTIONS FOR DECODING
// ============================================================================

/**
 * Convert BCD (Binary Coded Decimal) bytes to number
 * @param {Array} arr - Array of BCD bytes
 * @param {number} scale - Scale factor to apply
 * @returns {number} The decoded number
 */
function bcdToNumber(arr, scale) {
    var s = "";
    for (var i = 0; i < arr.length; i++) {
        var b = arr[i];
        s += (b >> 4).toString();
        s += (b & 0x0f).toString();
    }
    return parseInt(s, 10) * scale;
}

/**
 * Decode timestamp from BCD bytes
 * @param {Array} bytes - 7 bytes in format: second, minute, hour, day, month, year, century
 * @returns {string} Formatted timestamp string
 */
function decodeTimestamp(bytes) {
    var t = [];
    for (var i = 0; i < bytes.length; i++) {
        var b = bytes[i];
        var high = (b >> 4) & 0x0f;
        var low = b & 0x0f;
        t.push(high.toString() + low.toString());
    }

    // Format: second, minute, hour, day, month, year, century
    // Output: YYYY-MM-DD HH:MM:SS
    // Example from doc: 11430011051920 = 2019-05-11 00:43:11
    var second = t[0];
    var minute = t[1];
    var hour = t[2];
    var day = t[3];
    var month = t[4];
    var year = t[5];
    var century = t[6];

    // Combine century and year to get full 4-digit year
    var fullYear = century + year;

    return fullYear + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + second;
}

/**
 * Decode status word into human-readable flags
 * @param {number} status - The 16-bit status word
 * @returns {Object} Object with status flags
 */
function decodeStatus(status) {
    return {
        valve_closed: (status & 0x0001) !== 0,
        valve_open: (status & 0x0002) !== 0,
        low_battery: (status & 0x0004) !== 0,
        leak_alarm: (status & 0x0008) !== 0,
        burst_pipe: (status & 0x0010) !== 0,
        tamper_alarm: (status & 0x0020) !== 0,
        sensor_error: (status & 0x0040) !== 0,
        reverse_flow: (status & 0x0080) !== 0,
        dry_alarm: (status & 0x0100) !== 0,
        overload: (status & 0x0200) !== 0
    };
}


module.exports = {
    Decode
};
