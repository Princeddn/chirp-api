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

class vega():
	def __init__(self):
		self.name = 'vega'

	def parse(self,data,device):
		logging.debug('Vega Received')
		parsed={}
		data['parsed'] = parsed
		payload = data['payload']
		if device == "vega_si-11":
			try:
				dataarray = utils.hexarray_from_string(data['payload'])
				logging.debug('Parsing')
				if dataarray[0] == 0x01:
					parsed['battery'] = int(dataarray[1])
					parsed['temperature'] = int(dataarray[7])
					parsed['input1'] = str(int(utils.to_hex_string([dataarray[11],dataarray[10],dataarray[9],dataarray[8]]),16))
					parsed['input2'] = str(int(utils.to_hex_string([dataarray[15],dataarray[14],dataarray[13],dataarray[12]]),16))
					parsed['input3'] = str(int(utils.to_hex_string([dataarray[19],dataarray[18],dataarray[17],dataarray[16]]),16))
					parsed['input4'] = str(int(utils.to_hex_string([dataarray[23],dataarray[22],dataarray[21],dataarray[20]]),16))
			except Exception as e:
				logging.debug(str(e))
				logging.debug('Unparsable data')
		if device == "vega_si-11-REV2":
			try:
				dataarray = utils.hexarray_from_string(data['payload'])
				logging.debug('Parsing')
				if(len(dataarray) == 24):
					if dataarray[0] in [0x00,0x01,0x02,0x03,0x04]:
						parsed['battery'] = int(dataarray[1])
						parsed['temperature'] = int(dataarray[6])
						parsed['input1'] = str(int(utils.to_hex_string([dataarray[10],dataarray[9],dataarray[8],dataarray[7]]),16))
						parsed['input2'] = str(int(utils.to_hex_string([dataarray[14],dataarray[13],dataarray[12],dataarray[11]]),16))
						parsed['input3'] = str(int(utils.to_hex_string([dataarray[18],dataarray[17],dataarray[16],dataarray[15]]),16))
						parsed['input4'] = str(int(utils.to_hex_string([dataarray[22],dataarray[21],dataarray[20],dataarray[19]]),16))
						# --- Décodage du byte de configuration (dataarray[23]) ---
						conf_byte = dataarray[23]

						# Bit 0 : Confirmed uplinks
						parsed['confirmed_uplink'] = '1' if (conf_byte & 0b00000001) else '0'

						# Bits 1-3 : période de communication
						period_code = (conf_byte >> 1) & 0b00000111
						period_map = {
							0b000: '5 minutes',
							0b100: '15 minutes',
							0b010: '30 minutes',
							0b110: '1 hour',
							0b001: '6 hours',
							0b101: '12 hours',
							0b011: '24 hours'
						}
						parsed['communication_period'] = period_map.get(period_code, 'unknown')

						# Bits 4-7 : types d’entrée (0=pulse, 1=security)
						parsed['input1_type'] = 'security' if (conf_byte & 0b00010000) else 'pulse'
						parsed['input2_type'] = 'security' if (conf_byte & 0b00100000) else 'pulse'
						parsed['input3_type'] = 'security' if (conf_byte & 0b01000000) else 'pulse'
						parsed['input4_type'] = 'security' if (conf_byte & 0b10000000) else 'pulse'

			except Exception as e:
				logging.debug(str(e))
				logging.debug('Unparsable data')
		if device == "vega_td-11":
			try:
				dataarray = utils.hexarray_from_string(data['payload'])
				logging.debug('Parsing')
				if dataarray[0] == 0x01:
					parsed['battery'] = int(dataarray[1])
					parsed['temperature'] = int(utils.to_hex_string([dataarray[8],dataarray[7]]),16)/10
					if parsed['temperature'] > 100:
						parsed['temperature'] = (6553.5-parsed['temperature'])*-1
					parsed['output'] = int(dataarray[11])
			except Exception as e:
				logging.debug(str(e))
				logging.debug('Unparsable data')
		if device == "vega_SMART-MC0101":
			try:
				dataarray = utils.hexarray_from_string(data['payload'])
				logging.debug('Parsing')
				if dataarray[0] == 0x01:
					binary = str(bin(int(payload, 16))[2:])
					parsed['battery'] = int(dataarray[1])
					parsed['temperature'] = int(utils.to_hex_string([dataarray[4],dataarray[3]]),16)/10
					parsed['open1'] = int(binary[48:49],2)
					parsed['open2'] = int(binary[49:50],2)
			except Exception as e:
				logging.debug(str(e))
				logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(vega)
