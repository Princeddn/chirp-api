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

class dragino_LSN50_V2_mod4():
	def __init__(self):
		self.name = 'dragino_LSN50_V2_mod4'

	def parse(self,data,device):
		logging.debug('dragino_LSN50_V2_mod4 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			logging.debug('Parsing')
			payload = data['payload']
			parsed['battery'] = int(payload[0:4], 16) / 1000

			temperature1 = int(payload[4:8],16) & 0x8000
			if temperature1 == 0:
				parsed['temperature1'] = int(payload[4:8], 16)/10
			else:
				parsed['temperature1'] = (int(payload[4:8], 16)-65536)/10

			temperature2 = int(payload[14:18],16) & 0x8000
			if temperature2 == 0:
				parsed['temperature2'] = int(payload[14:18], 16)/10
			else:
				parsed['temperature2'] = (int(payload[14:18], 16)-65536)/10

			temperature3 = int(payload[18:22],16) & 0x8000
			if temperature3 == 0:
				parsed['temperature3'] = int(payload[18:22], 16)/10
			else:
				parsed['temperature3'] = (int(payload[18:22], 16)-65536)/10

			digitalInterrupt = int(payload[12:14],16) & 0x80
			if (int(payload[12:14], 16) & 0x80) == 0x80:
				parsed['digitalInterrupt'] = 1
			else:
				parsed['digitalInterrupt'] = 0
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(dragino_LSN50_V2_mod4)