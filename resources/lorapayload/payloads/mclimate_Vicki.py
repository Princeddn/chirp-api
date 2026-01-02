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

class mclimate_Vicki():
	def __init__(self):
		self.name = 'mclimate_Vicki'

	def parse(self,data,device):
		logging.debug('mclimate Vicki Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			logging.debug(len(payload))

			def decodageTrame(payload):
				reason = payload[0:2]
				if reason == '01':
					parsed['temperature'] = (int(payload[4:6], 16) * 165) / 256 - 40
				if reason == '81':
					parsed['temperature'] = (int(payload[4:6], 16) - 28.33333) / 5.66666
				parsed['targetTemp'] = int(payload[2:4], 16)
				parsed['humidity'] = (int(payload[6:8], 16) * 100) / 256
				parsed['battery'] = 2 + int(payload[14:15], 16) * 0.1
				binary7 = bin(int(payload[14:16], 16))[2:].zfill(8)
				parsed['openWindow'] = int(binary7[4:5])
				parsed['highMotorConsumption'] = int(binary7[-2:-1])
				parsed['lowMotorConsumption'] = int(binary7[-3:-2])
				parsed['brokenSensor'] = int(binary7[-4:-3])
				binary8 = bin(int(payload[16:18], 16))[2:].zfill(8)
				parsed['childLock'] = int(binary8[0])
				tmp = "0" + str(payload[12:14])
				tmp = tmp[-2:]
				motorRange1 = tmp[1]
				motorRange2 = "0" + str(payload[10:12])
				motorRange2 = motorRange2[-2:]
				parsed['motorRange'] = int("0x"+str(motorRange1+motorRange2),16)
				motorPosition1 = tmp[0]
				motorPosition2 = "0" + str(payload[8:10])
				motorPosition2 = motorPosition2[-2:]
				parsed['motorPosition'] = int("0x"+str(motorPosition1+motorPosition2),16)
				if parsed['motorRange'] != 0:
					parsed['motorPercentage'] = parsed['motorPosition'] / parsed['motorRange'] * 100
				else:
					parsed['motorPercentage'] = 0

				#parsed['motorPercentage'] = (int(parsed['motorPosition']) / int(parsed['motorRange'])) * 100

			if len(payload) > 18 :
				newPayload = payload[-18:]
				decodageTrame(newPayload)

			if len(payload) == 18 :
				decodageTrame(payload)

			if len(payload) == 24 :
				newPayload = payload[0:7]
				if newPayload[0:2] == '04':
					parsed['hardwareV'] = newPayload[2:3] + '.' + newPayload[3:4]
					parsed['softwareV'] = newPayload[4:5] + '.' + newPayload[5:6]

			if len(payload) == 22 :
				newPayload = payload[0:4]
				if newPayload[0:2] == '18':
					mode = newPayload[2:4]
					if mode == "00":
						parsed['mode'] = 'Online manual'
					elif mode == "01":
						parsed['mode'] = 'Online automatic'
					elif mode == "02":
						parsed['mode'] = 'Online automatic with external temp'
				elif newPayload[0:2] == '1f':
					primaryMode = newPayload[2:4]
					if primaryMode == "00":
						parsed['DevicePrimaryOperationalMode'] = 'Heating'
					elif primaryMode == "01":
						parsed['DevicePrimaryOperationalMode'] = 'Cooling'
				elif newPayload[0:2] == '12':
					parsed['keepAliveMinutes'] = int(newPayload[2:4],16)
				elif newPayload[0:2] == '2b':
					algo = newPayload[2:4]
					if algo == "00":
						parsed['controlalgorithm'] = 'Proportional control'
					elif algo == "01":
						parsed['controlalgorithm'] = 'Equal directional control'
					elif algo == "02":
						parsed['controlalgorithm'] = 'Proportional Integral control'

			if len(payload) == 28 :
				newPayload = payload[0:10]
				if newPayload[0:2] == '13':
					window = newPayload[2:4]
					if window == "00":
						parsed['G10_openWindow'] = 0
					elif window == "01":
						parsed['G10_openWindow'] = 1
					parsed['G10_durationValveChange'] = int(newPayload[4:6],16) * 5
					tmp = "0" + str(payload[8:10])
					tmp = tmp[-2:]
					motorPosition1 = tmp[0]
					motorPosition2 = "0" + str(payload[6:8])
					motorPosition2 = motorPosition2[-2:]
					parsed['G10_motorPosition'] = int("0x"+str(motorPosition1+motorPosition2),16)
					diff = bin(int(payload[8:10],16))[2:].zfill(8)
					parsed['G10_temperatureDelta'] = int(diff[5:8], 2)

			if len(payload) == 26 :
				newPayload = payload[0:10]
				if newPayload[0:2] == '46':
					window = newPayload[2:4]
					if window == "00":
						parsed['G01_openWindow'] = 0
					elif window == "01":
						parsed['G01_openWindow'] = 1
					parsed['G01_durationValveChange'] = int(newPayload[4:6],16) * 5
					parsed['G01_temperatureDelta'] = int(newPayload[4:6],16) * 5

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(mclimate_Vicki)
