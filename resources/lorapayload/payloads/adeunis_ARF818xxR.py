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

class adeunis_ARF818xxR():
	def __init__(self):
		self.name = 'adeunis_ARF818xxR'

	def parse(self,data,device):
		logging.debug('adeunis_ARF818xxR Received')
		parsed={}
		data['parsed'] = parsed
		try:
			def parse_temperature(segment):
				raw_value = int(segment, 16)
				if raw_value >= 0x8000:
					raw_value -= 0x10000
				return raw_value / 10

			def parseSensorAlarm(alarm_byte):
				value = int(alarm_byte, 16)
				if value == 0:
					return "No alarm"
				elif value == 1:
					return "High threshold"
				elif value == 2:
					return "Low threshold"
				else:
					return "Unknown"
	
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			logging.debug(payload) 

			if payload[0:2] == '30':
				logging.debug('Keep alive frame')
				status_hex = payload[2:4]
				status = int(status_hex, 16)
				bin_status = format(status, '08b')
				appflag2 = (status >> 4) & 1   # bit4
				parsed['lowbat']  = (status >> 1) & 1    # bit1
				parsed['sensorsActivated'] = 2 if appflag2 == 1 else 1
				if parsed['sensorsActivated'] == 1:
					logging.debug('1 sensor activated')
					parsed['temperature1'] = parse_temperature(payload[4:8])
				elif parsed['sensorsActivated'] == 2:
					logging.debug("2 sensors activated")
					parsed['temperature1'] = parse_temperature(payload[4:8])
					parsed['temperature2'] = parse_temperature(payload[8:12])

			if payload[0:2] == '58':
				logging.debug('Keep alive frame')
				status_hex = payload[2:4]
				status = int(status_hex, 16)
				bin_status = format(status, '08b')
				appflag2 = (status >> 4) & 1   # bit4
				parsed['lowbat']  = (status >> 1) & 1    # bit1
				parsed['sensorsActivated'] = 2 if appflag2 == 1 else 1
				if parsed['sensorsActivated'] == 1:
					logging.debug('1 sensor activated')
					parsed['alarm1'] = parseSensorAlarm(payload[4:6])
					parsed['temperature1'] = parse_temperature(payload[6:10])
				elif parsed['sensorsActivated'] == 2:
					logging.debug("2 sensors activated")
					parsed['alarm1'] = parseSensorAlarm(payload[4:6])
					parsed['temperature1'] = parse_temperature(payload[6:10])
					parsed['alarm2'] = parseSensorAlarm(payload[10:12])
					parsed['temperature2'] = parse_temperature(payload[12:16])
                   
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(adeunis_ARF818xxR)