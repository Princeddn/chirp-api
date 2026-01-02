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

class milesight_WS202():
	def __init__(self):
		self.name = 'milesight_WS202'

	def parse(self,data,device):
		logging.debug('WS202 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			logging.debug(payload)
			x=0
			i=0
			for i in range(3):
				channel_id = payload[x:x+2]
				channel_type = payload[x+2:x+4]
				if channel_id == '01' and channel_type == '75':
					parsed['battery'] = int(payload[x+4:x+6],16)
				elif channel_id == '03' and channel_type == '00':
					channel_value = int(payload[x+4:x+6],16)
					if channel_value == 0:
						parsed['pirState'] = 0
					elif channel_value == 1:
						parsed['pirState'] = 1
					else:
						logging.debug('UNSUPPORTED')
				elif channel_id == '04' and channel_type == '00':
					channel_value = int(payload[x+4:x+6],16)
					if channel_value == 0:
						parsed['daylightState'] = 'Nuit'
					elif channel_value == 1:
						parsed['daylightState'] = 'Jour'
					else:
						logging.debug('UNSUPPORTED')
				else:
					logging.debug('BREAK')
				x=x+6

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(milesight_WS202)
