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

class milesight_AM100():
	def __init__(self):
		self.name = 'milesight_AM100'

	def parse(self,data,device):
		logging.debug('AM100 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			logging.debug(payload)
			x=0
			i=0
			for i in range(8):
				channel_id = payload[x:x+2]
				channel_type = payload[x+2:x+4]
				if channel_id == '01' and channel_type == '75':
					parsed['battery'] = int(payload[x+4:x+6],16)
					x=x+6
				elif channel_id == '03' and channel_type == '67':
					channel_value = (int(payload[x+6:x+8],16) << 8) + int(payload[x+4:x+6],16)
					parsed['temperature'] = (channel_value & 0xffff)/10
					x=x+8
				elif channel_id == '04' and channel_type == '68':
					parsed['humidity'] = int(payload[x+4:x+6],16)/2
					x=x+6
				elif channel_id == '05' and channel_type == '6a':
					channel_value = (int(payload[x+6:x+8],16) << 8) + int(payload[x+4:x+6],16)
					parsed['activity'] = channel_value & 0xffff
					x=x+8
				elif channel_id == '06' and channel_type == '65':
					channel_value = (int(payload[x+6:x+8],16) << 8) + int(payload[x+4:x+6],16)
					parsed['illumination'] = channel_value & 0xffff
					channel_value = (int(payload[x+10:x+12],16) << 8) + int(payload[x+8:x+10],16)
					parsed['infrared_and_visible'] = channel_value & 0xffff
					channel_value = (int(payload[x+14:x+16],16) << 8) + int(payload[x+12:x+14],16)
					parsed['infrared'] = channel_value & 0xffff
					x=x+16
				elif channel_id == '07' and channel_type == '7d':
					channel_value = (int(payload[x+6:x+8],16) << 8) + int(payload[x+4:x+6],16)
					parsed['co2'] = channel_value & 0xffff
					x=x+8
				elif channel_id == '08' and channel_type == '7d':
					channel_value = (int(payload[x+6:x+8],16) << 8) + int(payload[x+4:x+6],16)
					parsed['tvoc'] = channel_value & 0xffff
					x=x+8
				elif channel_id == '09' and channel_type == '73':
					channel_value = (int(payload[x+6:x+8],16) << 8) + int(payload[x+4:x+6],16)
					parsed['pressure'] = (channel_value & 0xffff)/10
					x=x+8

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(milesight_AM100)
