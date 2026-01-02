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

class bmeters_iwmlr3():
	def __init__(self):
		self.name = 'bmeters_iwmlr3'

	def parse(self,data,device):
		logging.debug('IWM LR3 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			logging.debug('Parsing')
			payload = data['payload']

			def convertHex(value):
			   little_hex = bytearray.fromhex(value)
			   little_hex.reverse()
			   hex_string = ''.join(format(x, '02x') for x in little_hex)
			   #logging.debug(hex_string)
			   return hex_string

			appCode = payload[0:2]
			if appCode == '44':
				parsed['absValue'] = convertHex(payload[2:10])
				parsed['revFlow'] = convertHex(payload[10:18])
				indexK_value = payload[18:20]
				if indexK_value == '00':
					K = 1
				elif indexK_value == '01':
					K = 10
				elif indexK_value == '02':
					K = 100
				
				medium_value = payload[20:22]
				if medium_value == '00':
					parsed['mediumValue'] = 'Water'
				elif medium_value == '01':
					parsed['mediumValue'] = 'Hot Water'

				parsed['vif'] = payload[22:24] * K

				alarm_byte = int(payload[24:26], 16)
				if alarm_byte & 0x01:
					parsed['alarmMagnetic'] = 1
				else:
					parsed['alarmMagnetic'] = 0

				if alarm_byte & 0x02:
					parsed['alarmRemoval'] = 1
				else:
					parsed['alarmRemoval'] = 0

				if alarm_byte & 0x04:
					parsed['alarmSensorFraud'] = 1
				else:
					parsed['alarmSensorFraud'] = 0

				if alarm_byte & 0x08:
					parsed['alarmLeakage'] = 1
				else:
					parsed['alarmLeakage'] = 0

				if alarm_byte & 0x10:
					parsed['alarmReverseFlow'] = 1
				else:
					parsed['alarmReverseFlow'] = 0

				if alarm_byte & 0x20:
					parsed['alarmLowBattery'] = 1
				else:
					parsed['alarmLowBattery'] = 0

				temp_raw = int(payload[26:30], 16)
				if temp_raw & 0x8000:
					temp_value = -(temp_raw & 0x7FFF) / 10.0
				else:
					temp_value = temp_raw / 10.0
				parsed['temp'] = temp_value

			elif appCode == '07':
				logging.debug('Get firmware version')
				parsed['firmware'] = int(payload[-6:], 16)

			elif appCode == '17':
				logging.debug('GET_REVOLUTION_COUNTERS')
				parsed['fwdCnt'] = int(payload[12:20], 16)
				parsed['backwardCnt'] = int(payload[20:22], 16)

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(bmeters_iwmlr3)