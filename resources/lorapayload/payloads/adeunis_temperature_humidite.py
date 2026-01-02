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

class adeunis_temperature_humidite():
	def __init__(self):
		self.name = 'adeunis_temperature_humidite'

	def parse(self,data,device):
		logging.debug('adeunis_temperature_humidite Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			logging.debug(payload)

			def convertHex(value):
			   little_hex = bytearray.fromhex(value)
			   little_hex.reverse()
			   hex_string = ''.join(format(x, '02x') for x in little_hex)
			   #logging.debug(hex_string)
			   return hex_string

			frameCode = payload[0:2]
			binary1 = payload[2:4]
			if (frameCode == '4c'):
			   parsed['tempT0'] = int(payload[4:8],16)/10
			   parsed['humiT0'] = int(payload[8:10],16)
			   parsed['tempT1'] = int(payload[10:14],16)/10
			   parsed['humiT1'] = int(payload[14:16],16)
			   parsed['tempT2'] = int(payload[16:20],16)/10
			   parsed['humiT2'] = int(payload[20:22],16)
                   
			if (frameCode == '4d'):
			   binary2 = bin(int(payload[4:6],16))[2:].zfill(8)
			   parsed['humidAlarmed'] = binary2[7:8]
			   parsed['tempAlarmed'] = binary2[3:4]
			   parsed['tempAlarm'] = int(payload[6:10],16)/10
			   parsed['humidAlarm'] = int(payload[10:12],16)
                   
			if (frameCode == '51'):
			   # Digital Input 1
			   parsed['IO1State'] = payload[4:5]
			   parsed['IO1Prev'] = payload[5:6]
			   parsed['events'] = int(payload[6:15],16)
			   parsed['eventsLastAlarm'] = int(payload[15:19],16)
               
			if (frameCode == '52'):
			   # Digital Input 2
			   parsed['IO2State'] = payload[4:5]
			   parsed['IO2Prev'] = payload[5:6]
			   parsed['events'] = int(payload[6:15],16)
			   parsed['eventsLastAlarm'] = int(payload[15:19],16)
			   #logging.debug(parsed['events'])
                   
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(adeunis_temperature_humidite)