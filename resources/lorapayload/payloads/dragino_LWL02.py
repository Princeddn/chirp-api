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

class dragino_LWL02():
	def __init__(self):
		self.name = 'dragino_LWL02'

	def parse(self,data,device):
		logging.debug('dragino_LWL02 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			logging.debug(payload)
			# Battery
			parsed['BAT'] = float(int(hex( (dataarray[0]<<8) | dataarray[1]),16) & 0x3FFF) / 1000
			logging.debug(parsed['BAT'])
			# Status
			status = dataarray[0] & 0x40
			if status == 64:
				parsed['status'] = 1
			else:
				parsed['status'] = 0
			logging.debug(parsed['status'])
			# Mod
			parsed['mod'] = dataarray[2]
			logging.debug(parsed['mod'])
			# Water Leak Times
			parsed['water_leak_times'] = dataarray[3]<<16 | dataarray[4]<<8 | dataarray[5];
			logging.debug(parsed['water_leak_times'])
			# Water Leak Duration
			parsed['water_leak_duration'] = dataarray[6]<<16 | dataarray[7]<<8 | dataarray[8];
			logging.debug(parsed['water_leak_duration'])
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(dragino_LWL02)
