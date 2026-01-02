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

class milesight_WS101():
	def __init__(self):
		self.name = 'milesight_WS101'

	def parse(self,data,device):
		logging.debug('WS101 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing') # 017510FF2E01
			payload = data['payload']
			logging.debug(payload) # 01 75 10 FF 2E 01
			x=0
			i=0
			for i in range(2):
				channel_id = payload[x:x+2]
				channel_type = payload[x+2:x+4]
				logging.debug('CHANNEL ID ' + str(channel_id))
				logging.debug('CHANNEL TYPE ' + str(channel_type))
				if channel_id == '01' and channel_type == '75':
					parsed['battery'] = int(payload[x+4:x+6],16)
					logging.debug('BATTERY ' + str(parsed['battery']))
				elif channel_id == 'ff' and channel_type == '2e':
					channel_value = int(payload[x+4:x+6],16)
					logging.debug('CHANNEL VALUE ' + str(channel_value))
					if channel_value == 1:
						parsed['press'] = 'Short'
					elif channel_value == 2:
						parsed['press'] = 'Long'
					elif channel_value == 3:
						parsed['press'] = 'Double'
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

globals.COMPATIBILITY.append(milesight_WS101)
