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

class citylone_smartlighting():
	def __init__(self):
		self.name = 'citylone_smartlighting'

	def parse(self,data,device):
		logging.debug('citylone_smartlighting Received')
		parsed={}
		data['parsed'] = parsed
		try:
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

			if payload[0:2] == '01':
				logging.debug('TIC meter frame 1')
				parsed['indexBase'] = int(convertHex(payload[2:10]),16)
				parsed['indexHcHc'] = int(convertHex(payload[10:18]),16)
				parsed['indexHcHp'] = int(convertHex(payload[18:26]),16)

			if payload[0:2] == '02':
				logging.debug('TIC meter frame 2')
				input1 = payload[3:4]
				if input1 == '1':
					parsed['entree1'] = 1
				elif input1 == '0':
					parsed['entree1'] = 0
				input2 = payload[5:6]
				if input2 == '1':
					parsed['entree2'] = 1
				elif input2 == '0':
					parsed['entree2'] = 0
				byte_data = bytes.fromhex(payload[6:32])
				utf8_string = byte_data.decode('utf-8')
				parsed['ticMeterId'] = utf8_string.replace('\u0000', '')
				byte_data = bytes.fromhex(payload[32:42])
				utf8_string = byte_data.decode('utf-8')
				parsed['tarifOption'] = utf8_string.replace('\u0000', '')
				parsed['indexBase'] = int(convertHex(payload[42:50]),16)
				parsed['indexHcHc'] = int(convertHex(payload[50:58]),16)
				parsed['indexHcHp'] = int(convertHex(payload[58:66]),16)

			if payload[0:2] == '03':
				logging.debug('TIC meter frame 3')
				parsed['courantInstantaneMonophase'] = int(convertHex(payload[2:6]),16)
				parsed['courantInstantanePhase1'] = int(convertHex(payload[6:10]),16)
				parsed['courantInstantanePhase2'] = int(convertHex(payload[10:14]),16)
				parsed['courantInstantanePhase3'] = int(convertHex(payload[14:18]),16)
				parsed['maxCourantInstantaneMonophase'] = int(convertHex(payload[18:22]),16)
				parsed['maxCourantInstantanePhase1'] = int(convertHex(payload[22:26]),16)
				parsed['maxCourantInstantanePhase2'] = int(convertHex(payload[26:30]),16)
				parsed['maxCourantInstantanePhase3'] = int(convertHex(payload[30:34]),16)
				parsed['maxPuissanceActive'] = int(convertHex(payload[34:38]),16)
				parsed['puissanceThresoldAlarm'] = int(convertHex(payload[38:42]),16)
				parsed['puissanceInstantaneApparente'] = int(convertHex(payload[42:46]),16)

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

globals.COMPATIBILITY.append(citylone_smartlighting)
