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

class dragino_RS485_BL_TUF2000():
	def __init__(self):
		self.name = 'dragino_RS485_BL_TUF2000'

	def parse(self,data,device):
		logging.debug('dragino_RS485 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			logging.debug('Parsing')
			payload = data['payload']
			parsed['FLOWRATE'] = struct.unpack('!f', bytes.fromhex(payload[10:14]+payload[6:10]))[0]
			parsed['ENERGYFLOWRATE'] = struct.unpack('!f', bytes.fromhex(payload[18:22]+payload[14:18]))[0]
			parsed['NETACCUMULATOR'] = int(payload[26:30]+payload[22:26], 16)
			parsed['NETENERGYACCUMULATOR'] = int(payload[34:38]+payload[30:34], 16)
			parsed['TEMPERATURE1'] = struct.unpack('!f', bytes.fromhex(payload[42:46]+payload[38:42]))[0]
			parsed['SIGNALQUALITY'] = int(payload[48:50], 16)
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(dragino_RS485_BL_TUF2000)