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
from binascii import unhexlify

class eastron_sdm630():
	def __init__(self):
		self.name = 'eastron_sdm630'

	def parse(self,data,device):
		logging.debug('eastron_sdm630 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			payload = data['payload']
			logging.debug('Parsing')
			
			def bytes_to_float(bytes):
				bits = (bytes[0] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3]
				sign = 1.0 if (bits >> 31) == 0 else -1.0
				e = (bits >> 23) & 0xff
				m = ((bits & 0x7fffff) << 1) if e == 0 else (bits & 0x7fffff) | 0x800000
				f = sign * m * (2 ** (e - 150))
				return float(f)

			def hex_to_bytes(hex_string):
				bytes_array = []
				for c in range(0, len(hex_string), 2):
					bytes_array.append(int(hex_string[c:c+2], 16))
				return bytes_array

			if len(payload) == 56:
				logging.debug('Default Config')
				parsed['serialNumber'] = int(payload[0:8], 16)
				parsed['totalEnergy'] = bytes_to_float(hex_to_bytes(payload[12:20]))
				parsed['frequency'] = bytes_to_float(hex_to_bytes(payload[20:28]))
				parsed['totalPowerFactor'] = bytes_to_float(hex_to_bytes(payload[28:36]))
				parsed['maximumTotalSystemPowerDemand'] = bytes_to_float(hex_to_bytes(payload[36:44]))
				parsed['totalCurrent'] = bytes_to_float(hex_to_bytes(payload[44:52]))
			
			if len(payload) == 80: # 8 configs en même temps
				logging.debug('special config')
				parsed['serialNumber'] = int(payload[0:8], 16)
				parsed['config'] = int(payload[8:10], 16)
				parsed['nbParameters'] = int(payload[10:12], 16)
				parsed['L1'] = bytes_to_float(hex_to_bytes(payload[12:20]))
				parsed['L2'] = bytes_to_float(hex_to_bytes(payload[20:28]))
				parsed['L3'] = bytes_to_float(hex_to_bytes(payload[28:36]))
				parsed['C1'] = bytes_to_float(hex_to_bytes(payload[36:44]))
				parsed['C2'] = bytes_to_float(hex_to_bytes(payload[44:52]))
				parsed['C3'] = bytes_to_float(hex_to_bytes(payload[52:60]))
				parsed['AP'] = bytes_to_float(hex_to_bytes(payload[60:68]))
				parsed['TC'] = bytes_to_float(hex_to_bytes(payload[68:76]))

			if len(payload) == 40: # 3 configs en même temps
				logging.debug('special config')
				parsed['serialNumber'] = int(payload[0:8], 16)
				config = int(payload[8:10], 16)
				if config == 1:
					logging.debug('Payload 1')
					parsed['L1'] = bytes_to_float(hex_to_bytes(payload[12:20]))
					parsed['L2'] = bytes_to_float(hex_to_bytes(payload[20:28]))
					parsed['L3'] = bytes_to_float(hex_to_bytes(payload[28:36]))
				if config == 2:
					logging.debug('Payload 2')
					parsed['C1'] = bytes_to_float(hex_to_bytes(payload[12:20]))
					parsed['C2'] = bytes_to_float(hex_to_bytes(payload[20:28]))
					parsed['C3'] = bytes_to_float(hex_to_bytes(payload[28:36]))
				if config == 3:
					logging.debug('Payload 3')
					parsed['P1'] = bytes_to_float(hex_to_bytes(payload[12:20]))
					parsed['P2'] = bytes_to_float(hex_to_bytes(payload[20:28]))
					parsed['P3'] = bytes_to_float(hex_to_bytes(payload[28:36]))
				if config == 4:
					logging.debug('Payload 4')
					parsed['TAP'] = bytes_to_float(hex_to_bytes(payload[12:20]))
					parsed['L1C'] = bytes_to_float(hex_to_bytes(payload[20:28]))
					parsed['L2C'] = bytes_to_float(hex_to_bytes(payload[28:36]))
				if config == 5:
					logging.debug('Payload 5')
					parsed['L3C'] = bytes_to_float(hex_to_bytes(payload[12:20]))
					parsed['TC'] = bytes_to_float(hex_to_bytes(payload[20:28]))
					parsed['FR'] = bytes_to_float(hex_to_bytes(payload[28:36]))


		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(eastron_sdm630)
