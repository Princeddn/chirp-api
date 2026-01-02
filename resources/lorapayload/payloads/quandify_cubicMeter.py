# This file is part of Jeedom.
#
# Jeedom is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Jeedom is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Jeedom. If not, see <http://www.gnu.org/licenses/>.
#
import logging
import struct
import globals
import time
import json
import threading
import utils

class quandify_cubicMeter():
	def __init__(self):
		self.name = 'quandify_cubicMeter'

	def parse(self,data,device):
		logging.debug('quandify_cubicMeter Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			logging.debug(payload)

			def decode_uplink(input):
				decoded = None
				if get_packet_type(input["fPort"]) == "periodicReport" or get_packet_type(input["fPort"]) == "alarmReport":
					decoded = periodic_report_decoder(input["bytes"])
				return {
					"data" : {
						"type": get_packet_type(input["fPort"]),
						"decoded" : decoded,
						"hexBytes": to_hex_string(input["bytes"]),
						"fport": input["fPort"],
						"length": len(input["bytes"])
					},
					"warnings": [],
					"errors": []
				}

			def get_packet_type(type):
				if type == 0:
					return "ping"  # empty ping message
				elif type == 1:
					return "periodicReport"  # periodic message
				elif type == 2:
					return "alarmReport"  # same as periodic but pushed due to an urgent alarm
				else:
					return "Unknown"

			def periodic_report_decoder(bytes):
				buffer = bytearray(bytes)
				data = buffer
				if len(bytes) < 28:
					raise ValueError("payload too short")

				parsed['errorCode'] = data[4] if data[4] else "No Error"  # current error code > 419
				parsed['totalVolume'] = data[6]  # All-time aggregated water usage in litres
				parsed['leakStatus'] = get_leak_state(data[22])  # current water leakage state
				parsed['batteryStatus'] = decode_battery_status(data[23], data[24])  # current battery state
				parsed['waterTempMin'] = decode_temperature_C(data[25])  # min water temperature since last periodicReport
				parsed['waterTempMax'] = decode_temperature_C(data[26])  # max water temperature since last periodicReport
				parsed['ambientTemp'] = decode_temperature_C(data[27])  # current ambient temperature

			def to_hex_string(byte_array):
				return "".join(format(byte, "02X") for byte in byte_array)

			# Smaller water leakages only available when using Quandify platform API
			def get_leak_state(input):
				if input <= 2:
					return "NoLeak"
				elif input == 3:
					return "Medium"
				elif input == 4:
					return "Large"
				else:
					return "N/A"

			def decode_battery_status(input1, input2):
				level = 1800 + (input2 << 3)  # convert to status
				if level <= 3100:
					return "LOW_BATTERY"
				else:
					return "OK"

			def decode_temperature_C(input):
				return input * 0.5 - 20  # to °C

			def hex_to_bytes(hex_string):
				bytes_array = []
				for c in range(0, len(hex_string), 2):
					bytes_array.append(int(hex_string[c:c+2], 16))
				return bytes_array

			input_data = {
				"fPort": 1,
				"bytes" : hex_to_bytes(payload)  # Example bytes, replace with actual data
			}

			result = decode_uplink(input_data)

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(quandify_cubicMeter)
