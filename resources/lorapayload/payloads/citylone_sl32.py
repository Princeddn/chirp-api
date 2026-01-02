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
from datetime import datetime, timedelta

class citylone_sl32():
	def __init__(self):
		self.name = 'citylone_sl32'

	def parse(self,data,device):
		logging.debug('citylone_sl32 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			def checkOUTBitLamp(value, name):
			   concatNameMode = 'lamp'+name+'Mode'
			   concatNameLevel = 'lamp'+name+'Level'
			   level = int(value[1:8],2)
			   parsed[concatNameLevel] = level
			   if name == 'relay':
				   if level == 1:
					   parsed[concatNameLevel] = 'On'
				   elif level == 0:
					   parsed[concatNameLevel] = 'Off'
			   if (value[0] == '1'):
				   parsed[concatNameMode] = 'Forced'
			   elif (value[0] == '0'):
				   parsed[concatNameMode] = 'Auto'

			def checkOUTBitState(value):
			   parsed['stateS1'] = 0
			   parsed['stateS2'] = 0
			   parsed['stateS3'] = 0
			   parsed['stateS4'] = 0
			   if (value[0] == '1'):
				   parsed['stateS4'] = 1
			   if (value[1] == '1'):
				   parsed['stateS3'] = 1
			   if (value[2] == '1'):
				   parsed['stateS2'] = 1
			   if (value[3] == '1'):
				   parsed['stateS1'] = 1

			def checkOUTBitStatus(value):
			   parsed['statusS1'] = 'Auto'
			   parsed['statusS2'] = 'Auto'
			   parsed['statusS3'] = 'Auto'
			   parsed['statusS4'] = 'Auto'
			   if (value[0] == '1'):
				   parsed['statusS4'] = 'Priority'
			   if (value[1] == '1'):
				   parsed['statusS3'] = 'Priority'
			   if (value[2] == '1'):
				   parsed['statusS2'] = 'Priority'
			   if (value[3] == '1'):
				   parsed['statusS1'] = 'Priority'

			def convertHex(value):
			   little_hex = bytearray.fromhex(value)
			   little_hex.reverse()
			   hex_string = ''.join(format(x, '02x') for x in little_hex)
			   #logging.debug(hex_string)
			   return hex_string

			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			logging.debug(payload)

			if payload[0:2] == '17':
				logging.debug('Electrical measurement node')
				parsed['voltage'] = int(convertHex(payload[2:6]),16)
				parsed['current'] = int(convertHex(payload[6:10]),16)
				parsed['power'] = int(convertHex(payload[10:14]),16)
				parsed['powerFactor'] = int(convertHex(payload[14:18]),16)/1000
				parsed['temperature'] = int(convertHex(payload[18:22]),16)
				parsed['ledVoltage'] = int(convertHex(payload[22:26]),16)

			if payload[0:2] == '16':
				logging.debug('Node commands feedback')
				lamp11 = checkOUTBitLamp(bin(int(str(payload[2:4]),16))[2:].zfill(8), '11')
				lamp12 = checkOUTBitLamp(bin(int(str(payload[4:6]),16))[2:].zfill(8), '12')
				lamp21 = checkOUTBitLamp(bin(int(str(payload[6:8]),16))[2:].zfill(8), '21')
				lamp22 = checkOUTBitLamp(bin(int(str(payload[8:10]),16))[2:].zfill(8), '22')
				lamp110 = checkOUTBitLamp(bin(int(str(payload[10:12]),16))[2:].zfill(8), '110')
				lampRelay = checkOUTBitLamp(bin(int(str(payload[12:14]),16))[2:].zfill(8), 'relay')

			if payload[0:2] == '19':
				logging.debug('Node failures !!!!')

			if payload[0:2] == '09':
				logging.debug('SLB Ouptut feedback')
				states = bin(int(str(payload[2:4]),16))[2:].zfill(4)
				checkOUTBitState(states)
				status = bin(int(str(payload[4:6]),16))[2:].zfill(4)
				checkOUTBitStatus(status)

			if payload[0:2] == '07':
				logging.debug('Dry contact input 1')
				input1 = payload[3:4]
				if input1 == '1':
					parsed['entree1'] = 1
				elif input1 == '0':
					parsed['entree1'] = 0

			if payload[0:2] == '0b':
				logging.debug('Dry contact input 2')
				input2 = payload[3:4]
				if input2 == '1':
					parsed['entree2'] = 1
				elif input2 == '0':
					parsed['entree2'] = 0

			if payload[0:2] == '0e':
				logging.debug('RSSI feedback')
				valeur = payload[4:6] + payload[2:4]
				rssi = int(str(valeur),16)
				parsed['rssi'] = '-' + str(rssi)

			if payload[0:2] == '11':
				logging.debug('Current timestamp')
				original_timestamp = int(convertHex(payload[2:10]), 16)
				original_datetime = datetime.utcfromtimestamp(original_timestamp)

				time = int(convertHex(payload[10:14]),16)
				binary = bin(time)[2:].zfill(16)
				hours = int(binary[2:9],16)
				minutes = int(binary[9:16],16)
				operator = binary[0:2]
				if operator == '01':
					custom_hours = +hours
				elif operator == '10':
					custom_hours = -hours

				new_datetime = original_datetime + timedelta(hours=custom_hours)
				new_timestamp = int(new_datetime.timestamp())

				dt_object = datetime.utcfromtimestamp(original_timestamp)
				parsed['currentTimestampGMT'] = dt_object.strftime('%Y-%m-%d %H:%M:%S')
				dt_object = datetime.utcfromtimestamp(new_timestamp)
				parsed['currentTimestamp'] = dt_object.strftime('%Y-%m-%d %H:%M:%S')
				
				activation = payload[15:16]
				if activation == '1':
					parsed['updateViaLns'] = 1
				elif activation == '0':
					parsed['updateViaLns'] = 0

			if payload[0:2] == '12':
				logging.debug('Position feedback')
				parsed['longitude'] = int(convertHex(payload[2:10]),16)/1000000
				parsed['latitude'] = int(convertHex(payload[10:18]),16)/1000000

			if payload[0:2] == '04':
				logging.debug('Power Failure')
				parsed['powerFailure'] = 1
			
			if payload[0:2] == '13':
				state = payload[3:4]
				if state == '1':
					parsed['timeChangeState'] = 1
				elif state == '0':
					parsed['timeChangeState'] = 0

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(citylone_sl32)
