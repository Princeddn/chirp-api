
# --------------------------------------------------------------------------------
# RECOVERED BATCHNKE MODULE
# --------------------------------------------------------------------------------

class batchnke_constants:
    ST_UNDEF = 0
    ST_BL = 1
    ST_U4 = 2
    ST_I4 = 3
    ST_U8 = 4
    ST_I8 = 5
    ST_U16 = 6
    ST_I16 = 7
    ST_U24 = 8
    ST_I24 = 9
    ST_U32 = 10
    ST_I32 = 11
    ST_FL = 12

    BR_HUFF_MAX_INDEX_TABLE = 14
    NB_HUFF_ELEMENT = 16
    NUMBER_OF_SERIES = 16

    huff = [
        [
            {"sz": 2, "lbl": 0x000},
            {"sz": 2, "lbl": 0x001},
            {"sz": 2, "lbl": 0x003},
            {"sz": 3, "lbl": 0x005},
            {"sz": 4, "lbl": 0x009},
            {"sz": 5, "lbl": 0x011},
            {"sz": 6, "lbl": 0x021},
            {"sz": 7, "lbl": 0x041},
            {"sz": 8, "lbl": 0x081},
            {"sz": 10, "lbl": 0x200},
            {"sz": 11, "lbl": 0x402},
            {"sz": 11, "lbl": 0x403},
            {"sz": 11, "lbl": 0x404},
            {"sz": 11, "lbl": 0x405},
            {"sz": 11, "lbl": 0x406},
            {"sz": 11, "lbl": 0x407},
        ],
        [
            {"sz": 7, "lbl": 0x06f},
            {"sz": 5, "lbl": 0x01a},
            {"sz": 4, "lbl": 0x00c},
            {"sz": 3, "lbl": 0x003},
            {"sz": 3, "lbl": 0x007},
            {"sz": 2, "lbl": 0x002},
            {"sz": 2, "lbl": 0x000},
            {"sz": 3, "lbl": 0x002},
            {"sz": 6, "lbl": 0x036},
            {"sz": 9, "lbl": 0x1bb},
            {"sz": 9, "lbl": 0x1b9},
            {"sz": 10, "lbl": 0x375},
            {"sz": 10, "lbl": 0x374},
            {"sz": 10, "lbl": 0x370},
            {"sz": 11, "lbl": 0x6e3},
            {"sz": 11, "lbl": 0x6e2},
        ],
        [
            {"sz": 4, "lbl": 0x009},
            {"sz": 3, "lbl": 0x005},
            {"sz": 2, "lbl": 0x000},
            {"sz": 2, "lbl": 0x001},
            {"sz": 2, "lbl": 0x003},
            {"sz": 5, "lbl": 0x011},
            {"sz": 6, "lbl": 0x021},
            {"sz": 7, "lbl": 0x041},
            {"sz": 8, "lbl": 0x081},
            {"sz": 10, "lbl": 0x200},
            {"sz": 11, "lbl": 0x402},
            {"sz": 11, "lbl": 0x403},
            {"sz": 11, "lbl": 0x404},
            {"sz": 11, "lbl": 0x405},
            {"sz": 11, "lbl": 0x406},
            {"sz": 11, "lbl": 0x407},
        ],
    ]

# -----------------
# BATCHNKE LOGIC
# -----------------
from collections import namedtuple
import struct
from datetime import datetime
import json
import ctypes

Tag = namedtuple("Tag", "size lbl")

class Printer:
    def __init__(self, muted=True):
        self._muted = muted
    def print(self, message, end="\n"):
        if not self._muted:
            print(message, end=end)
    def mute(self): self._muted = True
    def unmute(self): self._muted = False

P = Printer(muted=True)

class SzError(Exception): pass

class Buffer:
    def __init__(self, byte_array):
        self.index = 0
        self.array = byte_array

    def next_sample(self, sample_type, nb_bits):
        src_bit_start = self.index
        self.index += nb_bits
        if sample_type == batchnke_constants.ST_FL and nb_bits != 32:
            raise Exception(f"Mauvais sample type ({sample_type})")
        u32 = 0
        nbytes = int((nb_bits - 1) / 8) + 1
        nbitsfrombyte = nb_bits % 8
        if nbitsfrombyte == 0 and nbytes > 0:
            nbitsfrombyte = 8

        while nbytes > 0:
            bit_to_read = 0
            while nbitsfrombyte > 0:
                idx = src_bit_start >> 3
                if self.array[idx] & (1 << (src_bit_start & 0x07)):
                    u32 |= 1 << ((nbytes - 1) * 8 + bit_to_read)
                nbitsfrombyte -= 1
                bit_to_read += 1
                src_bit_start += 1
            nbytes -= 1
            nbitsfrombyte = 8

        if sample_type in (batchnke_constants.ST_I4,batchnke_constants.ST_I8, batchnke_constants.ST_I16,batchnke_constants.ST_I24) and u32 & (
            1 << (nb_bits - 1)
        ):
            for i in range(nb_bits, 32):
                u32 |= 1 << i
                nb_bits += 1
        
        if sample_type in (batchnke_constants.ST_I4,batchnke_constants.ST_I8,batchnke_constants.ST_I16, batchnke_constants.ST_I24,batchnke_constants.ST_I32) and u32 & (
            1 << (nb_bits - 1)
        ):
           return ctypes.c_long(u32).value
        return u32

    def next_bi_from_hi(self, huff_coding):
        for i in range(2, 12):
            lhuff = self._bits_buf2HuffPattern(i)
            # Patching access to constants
            for j in range(batchnke_constants.NB_HUFF_ELEMENT):
                if (
                    batchnke_constants.huff[huff_coding][j]["sz"] == i
                    and lhuff == batchnke_constants.huff[huff_coding][j]["lbl"]
                ):
                    self.index += i
                    return (i, j)
        raise SzError

    def _bits_buf2HuffPattern(self, nb_bits):
        src_bit_start = self.index
        sz = nb_bits - 1
        if len(self.array) * 8 < src_bit_start + nb_bits:
            raise Exception(f"Verify that dest buf is large enough ( {len(self.array)}, {src_bit_start}, {nb_bits})")
        bittoread = 0
        pattern = 0
        while nb_bits > 0:
            if self.array[src_bit_start >> 3] & (1 << (src_bit_start & 0x07)):
                pattern |= 1 << (sz - bittoread)
            nb_bits -= 1
            bittoread += 1
            src_bit_start += 1
        return pattern

class Flag:
    def __init__(self, flag_as_int):
        bin_str = f"{flag_as_int:08b}"
        self.cts = int(bin_str[-2], 2)
        self.no_sample = int(bin_str[-3], 2)
        self.batch_req = int(bin_str[-4], 2)
        self.nb_of_type_measure = int(bin_str[:4], 2)

class Serie:
    def __init__(self):
        self.coding_type = 0
        self.coding_table = 0
        self.compress_sample_nb = 0
        self.resolution = None
        self.uncompress_samples = []

class Measure:
    def __init__(self, timestamp):
        self.data_relative_timestamp = timestamp
        self.data = MeasuredData()

class MeasuredData:
    def __init__(self):
        self.value = None
        self.label = None

class UncompressedData:
    def __init__(self):
        self.batch_counter = 0
        self.batch_relative_timestamp = 0
        self.series = [Serie() for i in range(batchnke_constants.NUMBER_OF_SERIES)]

class batchnke:
    @staticmethod
    def uncompress(tagsz, arg_list, hex_string, batch_absolute_timestamp=None):
        out = UncompressedData()
        array = batchnke.hex_to_array(hex_string)
        data_buffer = Buffer(array)
        flag = Flag(data_buffer.next_sample(batchnke_constants.ST_U8, 8))
        counter = data_buffer.next_sample(batchnke_constants.ST_U8, 3)
        out.batch_counter = counter
        ltemp2 = data_buffer.next_sample(batchnke_constants.ST_U8, 1) # dummy read?
        abs_timestamp = last_timestamp = 0
        index_of_the_first_sample = 0
        
        for i in range(flag.nb_of_type_measure):
            tag = Tag(size=tagsz, lbl=data_buffer.next_sample(batchnke_constants.ST_U8, tagsz))
            ii = batchnke.find_index_of_lbl(arg_list, tag.lbl)
            if i == 0:
                index_of_the_first_sample = ii
                timestamp = data_buffer.next_sample(batchnke_constants.ST_U8, batchnke.bm_st_sz(batchnke_constants.ST_U32))
                abs_timestamp = timestamp
                out.series[ii].uncompress_samples.append(Measure(timestamp))
            else:
                sz, bi = data_buffer.next_bi_from_hi(1)
                if not sz: raise Exception("Wrong sz from szbi")
                t = 0
                if bi <= batchnke_constants.BR_HUFF_MAX_INDEX_TABLE:
                    if bi > 0:
                        t = data_buffer.next_sample(batchnke_constants.ST_U32, bi)
                        t += abs_timestamp + 2 ** bi - 1
                    else: t = abs_timestamp
                else:
                    t = data_buffer.next_sample(batchnke_constants.ST_U32, batchnke.bm_st_sz(batchnke_constants.ST_U32))
                out.series[ii].uncompress_samples.append(Measure(t))
                abs_timestamp = t
            last_timestamp = abs_timestamp
            v = data_buffer.next_sample(arg_list[ii]["sampletype"], batchnke.bm_st_sz(arg_list[ii]["sampletype"]))
            if arg_list[ii]["sampletype"] == batchnke_constants.ST_FL:
                out.series[ii].uncompress_samples[0].data.value = batchnke.to_float(v)
            else:
                out.series[ii].uncompress_samples[0].data.value = v
            out.series[ii].uncompress_samples[0].data.label = tag.lbl
            if not flag.no_sample:
                out.series[ii].coding_type = data_buffer.next_sample(batchnke_constants.ST_U8, 2)
                out.series[ii].coding_table = data_buffer.next_sample(batchnke_constants.ST_U8, 2)
        
        if not flag.no_sample:
            if flag.cts:
                nb_sample_to_parse = data_buffer.next_sample(batchnke_constants.ST_U8, 8)
                ltimestamp_coding = data_buffer.next_sample(batchnke_constants.ST_U8, 2)
                timestamp_common = []
                for i in range(nb_sample_to_parse):
                    sz, bi = data_buffer.next_bi_from_hi(ltimestamp_coding)
                    if not sz: raise Exception("sz")
                    if bi <= batchnke_constants.BR_HUFF_MAX_INDEX_TABLE:
                        if i == 0:
                           timestamp_common.append(out.series[index_of_the_first_sample].uncompress_samples[0].data_relative_timestamp)
                        else:
                            if bi > 0:
                                raw = data_buffer.next_sample(batchnke_constants.ST_U32, bi)
                                timestamp_common.append(raw + timestamp_common[i - 1] + 2 ** bi - 1)
                            else: timestamp_common.append(timestamp_common[i - 1])
                    else:
                        timestamp_common.append(data_buffer.next_sample(batchnke_constants.ST_U32, batchnke.bm_st_sz(batchnke_constants.ST_U32)))
                    last_timestamp = timestamp_common[i]

                for j in range(flag.nb_of_type_measure):
                    first_null_delta_value = 1
                    tag = Tag(size=tagsz, lbl=data_buffer.next_sample(batchnke_constants.ST_U8, tagsz))
                    ii = batchnke.find_index_of_lbl(arg_list, tag.lbl)
                    for i in range(0, nb_sample_to_parse):
                        available = data_buffer.next_sample(batchnke_constants.ST_U8, 1)
                        if available:
                            sz, bi = data_buffer.next_bi_from_hi(out.series[ii].coding_table)
                            if not sz: raise Exception("Wrong sz")
                            current_measure = Measure(0)
                            if bi <= batchnke_constants.BR_HUFF_MAX_INDEX_TABLE:
                                if bi > 0:
                                    current_measure.data.value = data_buffer.next_sample(batchnke_constants.ST_U16, bi)
                                    if out.series[ii].coding_type == 0:
                                        if current_measure.data.value >= 2 ** (bi - 1):
                                            current_measure.data.value *= arg_list[ii]["resol"]
                                            current_measure.data.value += out.series[ii].uncompress_samples[-1].data.value
                                        else:
                                            current_measure.data.value += 1 - 2 ** bi
                                            current_measure.data.value *= arg_list[ii]["resol"]
                                            current_measure.data.value += out.series[ii].uncompress_samples[-1].data.value
                                    elif out.series[ii].coding_type == 1:
                                        current_measure.data.value += 2 ** bi - 1
                                        current_measure.data.value *= arg_list[ii]["resol"]
                                        current_measure.data.value += out.series[ii].uncompress_samples[-1].data.value
                                    else:
                                        current_measure.data.value += 2 ** bi - 1
                                        current_measure.data.value *= arg_list[ii]["resol"]
                                        current_measure.data.value = out.series[ii].uncompress_samples[-1].data.value - current_measure.data.value
                                else:
                                    if first_null_delta_value:
                                        first_null_delta_value = 0
                                        continue
                                    else:
                                        current_measure.data.value = out.series[ii].uncompress_samples[-1].data.value
                            else:
                                current_measure.data.value = data_buffer.next_sample(arg_list[ii]["sampletype"], batchnke.bm_st_sz(arg_list[ii]["sampletype"]))
                            current_measure.data_relative_timestamp = timestamp_common[i]
                            out.series[ii].uncompress_samples.append(current_measure)
            else:
                for i in range(flag.nb_of_type_measure):
                    tag = Tag(size=tagsz, lbl=data_buffer.next_sample(batchnke_constants.ST_U8, tagsz))
                    ii = batchnke.find_index_of_lbl(arg_list, tag.lbl)
                    compress_samples_nb = data_buffer.next_sample(batchnke_constants.ST_U8, 8)
                    if compress_samples_nb:
                        ltimestamp_coding = data_buffer.next_sample(batchnke_constants.ST_U8, 2)
                        for j in range(compress_samples_nb):
                            current_measure = Measure(0)
                            sz, bi = data_buffer.next_bi_from_hi(ltimestamp_coding)
                            if bi <= batchnke_constants.BR_HUFF_MAX_INDEX_TABLE:
                                if bi > 0:
                                    t = data_buffer.next_sample(batchnke_constants.ST_U32, bi)
                                    current_measure.data_relative_timestamp = t + out.series[ii].uncompress_samples[-1].data_relative_timestamp + 2 ** bi - 1
                                else:
                                    current_measure.data_relative_timestamp = out.series[ii].uncompress_samples[-1].data_relative_timestamp
                            else:
                                current_measure.data_relative_timestamp = data_buffer.next_sample(batchnke_constants.ST_U32, batchnke.bm_st_sz(batchnke_constants.ST_U32))
                            if current_measure.data_relative_timestamp > last_timestamp:
                                last_timestamp = current_measure.data_relative_timestamp
                            sz, bi = data_buffer.next_bi_from_hi(out.series[ii].coding_table)
                            if not sz: raise Exception("sz")
                            if bi <= batchnke_constants.BR_HUFF_MAX_INDEX_TABLE:
                                if bi > 0:
                                    current_measure.data.value = data_buffer.next_sample(batchnke_constants.ST_U16, bi)
                                    if out.series[ii].coding_type == 0:
                                        if current_measure.data.value >= 2 ** (bi - 1):
                                            current_measure.data.value *= arg_list[ii]["resol"]
                                            current_measure.data.value += out.series[ii].uncompress_samples[-1].data.value
                                        else:
                                            current_measure.data.value += 1 - 2 ** bi
                                            current_measure.data.value *= arg_list[ii]["resol"]
                                            current_measure.data.value += out.series[ii].uncompress_samples[-1].data.value
                                    elif out.series[ii].coding_type == 1:
                                        current_measure.data.value += 2 ** bi - 1
                                        current_measure.data.value *= arg_list[ii]["resol"]
                                        current_measure.data.value += out.series[ii].uncompress_samples[-1].data.value
                                    else:
                                        current_measure.data.value += 2 ** bi - 1
                                        current_measure.data.value *= arg_list[ii]["resol"]
                                        current_measure.data.value = out.series[ii].uncompress_samples[-1].data.value - current_measure.data.value
                                else:
                                    current_measure.data.value = out.series[ii].uncompress_samples[-1].data.value
                            else:
                                current_measure.data.value = data_buffer.next_sample(arg_list[ii]["sampletype"], batchnke.bm_st_sz(arg_list[ii]["sampletype"]))
                            out.series[ii].uncompress_samples.append(current_measure)
        
        global_timestamp = 0
        if not last_timestamp:
            global_timestamp = data_buffer.next_sample(batchnke_constants.ST_U32, batchnke.bm_st_sz(batchnke_constants.ST_U32))
        else:
            sz, bi = data_buffer.next_bi_from_hi(1)
            if not sz: raise Exception("sz")
            if bi <= batchnke_constants.BR_HUFF_MAX_INDEX_TABLE:
                if bi > 0:
                    global_timestamp = data_buffer.next_sample(batchnke_constants.ST_U32, bi)
                    global_timestamp += last_timestamp + 2 ** bi - 1
                else: global_timestamp = last_timestamp
            else:
                 global_timestamp = data_buffer.next_sample(batchnke_constants.ST_U32, batchnke.bm_st_sz(batchnke_constants.ST_U32))
        out.batch_relative_timestamp = global_timestamp
        return batchnke.format_expected_uncompress_result(out, arg_list, batch_absolute_timestamp)

    @staticmethod
    def format_expected_uncompress_result(out, arg_list, batch_absolute_timestamp):
        output = {"batch_counter": out.batch_counter, "batch_relative_timestamp": out.batch_relative_timestamp}
        if batch_absolute_timestamp: output["batch_absolute_timestamp"] = batch_absolute_timestamp
        dataset = []
        for index, serie in enumerate(out.series):
            for sample in serie.uncompress_samples:
                measure = {
                    "data_relative_timestamp": sample.data_relative_timestamp,
                    "data": {"value": sample.data.value, "label": arg_list[index]["taglbl"]},
                }
                if "lblname" in arg_list[index]: measure["data"]["label_name"] = arg_list[index]["lblname"]
                dataset.append(measure)
                if batch_absolute_timestamp:
                    measure["data_absolute_timestamp"] = batchnke.compute_data_absolute_timestamp(
                        batch_absolute_timestamp, out.batch_relative_timestamp, sample.data_relative_timestamp
                    )
        output["dataset"] = dataset
        return output

    @staticmethod
    def compute_data_absolute_timestamp(bat, brt, drt):
        d, t = bat.rstrip("Z").split("T")
        Y, M, D = [int(x) for x in d.split("-")]
        h, m, s = t.split(":")
        ss, ms = s.split(".")
        from_ts = datetime(Y, M, D, int(h), int(m), int(ss), int(ms) * 1000)
        return (datetime.fromtimestamp(from_ts.timestamp() - (brt - drt)).isoformat(timespec="milliseconds") + "Z")

    @staticmethod
    def is_hex(c):
        try:
            _ = int(c, 16)
            return True
        except ValueError: return False

    @staticmethod
    def hex_to_array(hex_string):
        filtered = [c for c in hex_string if batchnke.is_hex(c)]
        out = []
        i = 0
        while i < len(filtered):
            out.append(int(filtered[i] + filtered[i + 1], 16))
            i += 2
        return out

    @staticmethod
    def find_index_of_lbl(arg_list, label):
        for i, value in enumerate(arg_list):
            if value["taglbl"] == label: return i
        raise Exception("Cannot find index in arg_list")

    @staticmethod
    def bm_st_sz(st):
        if st > batchnke_constants.ST_I24: return 32
        if st > batchnke_constants.ST_I16: return 24
        if st > batchnke_constants.ST_I8: return 16
        if st > batchnke_constants.ST_I4: return 8
        if st > batchnke_constants.ST_BL: return 4
        if st > batchnke_constants.ST_UNDEF: return 1
        return 0

    @staticmethod
    def to_float(number):
        return struct.unpack(">f", number.to_bytes(4, "big"))[0]
