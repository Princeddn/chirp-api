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

class milesight_EM300():
	def __init__(self):
		self.name = 'milesight_EM300'

	def parse(self,data,device):
		logging.debug('WS301 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing') # 01755C03673401046865050000
			payload = data['payload']
			logging.debug(payload) # 01 75 5C 03 67 34 01 04 68 65 05 00 00
			x=0
			i=0
			for i in range(4):
				channel_id = payload[x:x+2]
				channel_type = payload[x+2:x+4]
				logging.debug('CHANNEL ID ' + str(channel_id))
				logging.debug('CHANNEL TYPE ' + str(channel_type))
				if channel_id == '01' and channel_type == '75':
					parsed['battery'] = int(payload[x+4:x+6],16)
					logging.debug('-------------------------- BATTERY ' + str(parsed['battery']))
					x=x+6
				elif channel_id == '03' and channel_type == '67':
					#parsed['temperature'] = payload[x+4:x+8]
					channel_value = (int(payload[x+6:x+8],16) << 8) + int(payload[x+4:x+6],16)
					parsed['temperature'] = (channel_value & 0xffff)/10
					x=x+8
					logging.debug('-------------------------- TEMPERATURE ' + str(parsed['temperature']))
				elif channel_id == '04' and channel_type == '68':
					parsed['humidity'] = int(payload[x+4:x+6],16)/2
					x=x+6
					logging.debug('-------------------------- HUMIDITY ' + str(parsed['humidity']))
				elif channel_id == '05' and channel_type == '00':
					channel_value = int(payload[x+4:x+6],16)
					x=x+6
					logging.debug('-------------------------- STATUS ' + str(channel_value))
					if channel_value == 0:
						parsed['status'] = 0
					elif channel_value == 1:
						parsed['status'] = 1
					else:
						logging.debug('UNSUPPORTED')
				else:
					logging.debug('BREAK')
				#x=x+6

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(milesight_EM300)
