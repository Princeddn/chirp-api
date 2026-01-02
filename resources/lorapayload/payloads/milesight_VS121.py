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

class milesight_VS121():
	def __init__(self):
		self.name = 'milesight_VS121'

	def parse(self,data,device):
		logging.debug('VS121 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			logging.debug(payload)
			x=0
			i=0
			parsed['region_0'] = 0
			parsed['region_1'] = 0
			parsed['region_2'] = 0
			parsed['region_3'] = 0
			parsed['region_4'] = 0
			parsed['region_5'] = 0
			parsed['region_6'] = 0
			parsed['region_7'] = 0
			parsed['region_8'] = 0
			parsed['region_9'] = 0
			parsed['region_10'] = 0
			parsed['region_11'] = 0
			parsed['region_12'] = 0
			parsed['region_13'] = 0
			parsed['region_14'] = 0
			parsed['region_15'] = 0
			for i in range(20):
				channel_id = payload[x:x+2]
				channel_type = payload[x+2:x+4]
				#logging.debug('CHANNEL ID ' + str(channel_id))
				#logging.debug('CHANNEL TYPE ' + str(channel_type))
				if channel_id == 'ff' and channel_type == '01':
					parsed['protocolVersion'] = int(payload[x+4:x+6],16)
					logging.debug('-------------------------- Protocol Version ' + str(parsed['protocolVersion']))
					x=x+6
				elif channel_id == 'ff' and channel_type == '08':
					parsed['serialNumber'] = payload[x+4:x+16]
					x=x+16
					logging.debug('-------------------------- Serial Number ' + str(parsed['serialNumber']))
				elif channel_id == 'ff' and channel_type == '09':
					parsed['hardwareVersion'] = str(int(payload[x+4:x+6],16)) + '.' + str(int(payload[x+6:x+8],16))
					x=x+8
					logging.debug('-------------------------- Hardware Version ' + str(parsed['hardwareVersion']))
				elif channel_id == 'ff' and channel_type == '0a':
					parsed['firmwareVersion'] = str(int(payload[x+4:x+6],16)) + '.' + str(int(payload[x+6:x+8],16)) + '.' + str(int(payload[x+8:x+10],16)) + '.' + str(int(payload[x+10:x+12],16))
					x=x+12
					logging.debug('-------------------------- Firmware Version ' + str(parsed['firmwareVersion']))
				elif channel_id == '04' and channel_type == 'c9':
					parsed['people_counter_all'] = int(payload[x+4:x+6],16)
					region_count = int(payload[x+6:x+8],16)
					parsed['region_count'] = region_count
					logging.debug('-------------------------- people_counter_all === ' + str(parsed['people_counter_all']))
					#logging.debug('-------------------------- region_count === ' + str(parsed['region_count']))
					region = int(payload[x+8:x+12],16)
					index=1
					for index in range(0,region_count):
						tmp = "region_" + str(index+1)
						test = (region >> index)
						parsed[tmp] = (region >> index) & 1
						logging.debug('-------------------------- region name === ' + str(tmp))
						#logging.debug('-------------------------- test === ' + str(test))
						logging.debug('-------------------------- number of people === ' + str(parsed[tmp]))
					x=x+12
				elif channel_id == '05' and channel_type == 'cc':
					parsed['in'] = int(payload[x+4:x+6],16)
					parsed['out'] = int(payload[x+8:x+10],16)
					x=x+12
					logging.debug('-------------------------- IN ' + str(parsed['in']))
					logging.debug('-------------------------- OUT ' + str(parsed['out']))
				elif channel_id == '06' and channel_type == 'cd':
					parsed['max'] = int(payload[x+4:x+6],16)
					x=x+6
					logging.debug('-------------------------- Max ' + str(parsed['max']))
				#x=x+6

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(milesight_VS121)
