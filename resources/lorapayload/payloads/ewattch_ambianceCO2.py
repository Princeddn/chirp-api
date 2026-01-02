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

class ewattch_ambianceCO2():
	def __init__(self):
		self.name = 'ewattch_ambianceCO2'

	def parse(self,data,device):
		logging.debug('Ewattch Ambiance CO2 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			def convertHex(value):
			   little_hex = bytearray.fromhex(value)
			   little_hex.reverse()
			   hex_string = ''.join(format(x, '02x') for x in little_hex)
			   #logging.debug(hex_string)
			   return hex_string

			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			
			if payload[0:2] == "00":
				logging.debug('This is a periodic message')
				parsed['temperature'] = int(convertHex(payload[6:10]), 16)/100
				parsed['humidity'] = int(payload[12:14], 16)/2
				parsed['luminosity'] = int(convertHex(payload[16:20]), 16)
				parsed['presence'] = int(convertHex(payload[22:26]), 16)*10
				parsed['co2'] = int(convertHex(payload[28:32]), 16)
			
			elif payload[0:2] == "10":
				logging.debug('This is a state message')
				batterylevel = payload[16:18]
				logging.debug(batterylevel)
				if batterylevel == '08':
					parsed['battery'] = 100
				elif batterylevel == '07':
					parsed['battery'] = 75
				elif batterylevel == '02':
					parsed['battery'] = 50
				elif batterylevel == '01':
					parsed['battery'] = 25
				elif batterylevel == '00':
					parsed['battery'] = 0
			
			else:
				logging.debug('Unknown message')
				return data
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(ewattch_ambianceCO2)