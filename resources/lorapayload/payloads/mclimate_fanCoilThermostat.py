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

class mclimate_fanCoilThermostat():
	def __init__(self):
		self.name = 'mclimate_fanCoilThermostat'

	def parse(self,data,device):
		logging.debug('mclimate_fanCoilThermostat Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			#logging.debug(len(payload)) # 0102888001090102020101

			def decodageTrame(payload):
				reason = payload[0:2]
				if reason == '01':
					# 01 0288 80 0109 01 02 02 01 01
					parsed['temperature'] = (int(payload[2:6], 16) - 400) / 10
					parsed['humidity'] = (int(payload[6:8], 16) * 100) / 256
					parsed['targetTemp'] = int(payload[8:12], 16)/10

					operationMode = payload[12:14]
					if operationMode == '00':
						parsed['operationalMode'] = 'Ventilation'
					elif operationMode == '01':
						parsed['operationalMode'] = 'Heating'
					elif operationMode == '02':
						parsed['operationalMode'] = 'Cooling'

					displayedFanSpeed = payload[14:16]
					if displayedFanSpeed == '00':
						parsed['displayedFanSpeed'] = 'Auto'
						parsed['fanSpeed'] = 'Auto'
					elif displayedFanSpeed == '01':
						parsed['displayedFanSpeed'] = 'Speed 1'
						parsed['fanSpeed'] = 'NA'
					elif displayedFanSpeed == '02':
						parsed['displayedFanSpeed'] = 'Speed 2'
						parsed['fanSpeed'] = 'Low'
					elif displayedFanSpeed == '03':
						parsed['displayedFanSpeed'] = 'Speed 3'
						parsed['fanSpeed'] = 'NA'
					elif displayedFanSpeed == '04':
						parsed['displayedFanSpeed'] = 'Speed 4'
						parsed['fanSpeed'] = 'Medium'
					elif displayedFanSpeed == '05':
						parsed['displayedFanSpeed'] = 'Speed 5'
						parsed['fanSpeed'] = 'NA'
					elif displayedFanSpeed == '06':
						parsed['displayedFanSpeed'] = 'Speed 6'
						parsed['fanSpeed'] = 'High'

					actualFanSpeed = payload[16:18]
					if actualFanSpeed == '01':
						parsed['actualFanSpeedECM'] = 'Speed 1'
						parsed['actualfanSpeed'] = 'NA'
					elif actualFanSpeed == '02':
						parsed['actualFanSpeedECM'] = 'Speed 2'
						parsed['actualfanSpeed'] = 'Low'
					elif actualFanSpeed == '03':
						parsed['actualFanSpeedECM'] = 'Speed 3'
						parsed['actualfanSpeed'] = 'NA'
					elif actualFanSpeed == '04':
						parsed['actualFanSpeedECM'] = 'Speed 4'
						parsed['actualfanSpeed'] = 'Medium'
					elif actualFanSpeed == '05':
						parsed['actualFanSpeedECM'] = 'Speed 5'
						parsed['actualfanSpeed'] = 'NA'
					elif actualFanSpeed == '06':
						parsed['actualFanSpeedECM'] = 'Speed 6'
						parsed['actualfanSpeed'] = 'High'
					elif actualFanSpeed == '07':
						parsed['actualFanSpeedECM'] = 'Fan off'
						parsed['actualfanSpeed'] = 'Fan off'

					valveStatus = payload[18:20]
					if valveStatus == '00':
						parsed['valveStatus'] = '0'
					elif valveStatus == '01':
						parsed['valveStatus'] = '1'

					deviceStatus = payload[20:22]
					if deviceStatus == '00':
						parsed['deviceStatus'] = '0'
					elif deviceStatus == '01':
						parsed['deviceStatus'] = '1'

			if len(payload) > 22 :
				if payload[0:2] == '12':
					parsed['keepAliveMinutes'] = int(payload[2:4],16)
				elif payload[0:2] == '67':
					if payload[2:4] == '00':
						parsed['deviceStatus'] = 0
					elif payload[2:4] == '01':
						parsed['deviceStatus'] = 1
				elif payload[0:2] == '55':
					if payload[2:4] == '00':
						parsed['AllowedoperationalMode'] = 'Ventilation'
					elif payload[2:4] == '01':
						parsed['AllowedoperationalMode'] = 'Heating'
					elif payload[2:4] == '02':
						parsed['AllowedoperationalMode'] = 'Cooling'
				elif payload[0:2] == '53':
					if payload[2:4] == '00':
						parsed['operationalMode'] = 'Ventilation'
					elif payload[2:4] == '01':
						parsed['operationalMode'] = 'Heating'
					elif payload[2:4] == '02':
						parsed['operationalMode'] = 'Cooling'
				elif payload[0:2] == '2f':
					parsed['targetTemp'] = int(payload[2:6],16)/10
				elif payload[0:2] == '30':
					parsed['targetTemp'] = int(payload[2:6],16)/10
					logging.debug(parsed['targetTemp'])
				elif payload[0:2] == '45':
					if payload[2:4] == '00':
						parsed['actualfanSpeed'] = 'Automatic'
					elif payload[2:4] == '01':
						parsed['actualFanSpeedECM'] = 'Speed 1'
					elif payload[2:4] == '02':
						parsed['actualFanSpeedECM'] = 'Speed 2'
						parsed['actualfanSpeed'] = 'Low'
					elif payload[2:4] == '03':
						parsed['actualFanSpeedECM'] = 'Speed 3'
					elif payload[2:4] == '04':
						parsed['actualFanSpeedECM'] = 'Speed 4'
						parsed['actualfanSpeed'] = 'Medium'
					elif payload[2:4] == '05':
						parsed['actualFanSpeedECM'] = 'Speed 5'
					elif payload[2:4] == '06':
						parsed['actualFanSpeedECM'] = 'Speed 6'
						parsed['actualfanSpeed'] = 'High'
					elif payload[2:4] == '07':
						parsed['actualFanSpeedECM'] = 'Fan off'
						parsed['actualfanSpeed'] = 'Fan off'
				elif payload[0:2] == '14':
					if payload[2:4] == '00':
						parsed['keysLock'] = 'No keys are locked.'
					elif payload[2:4] == '01':
						parsed['keysLock'] = 'All keys are locked.'
					elif payload[2:4] == '02':
						parsed['keysLock'] = 'ON/OFF and mode change are locked.'
					elif payload[2:4] == '03':
						parsed['keysLock'] = 'ON/OFF is locked.'
					elif payload[2:4] == '04':
						parsed['keysLock'] = 'All keys except ON/OFF key are locked.'
					elif payload[2:4] == '05':
						parsed['keysLock'] = 'Mode change is locked.'
				elif payload[0:2] == '36':
					if payload[2:4] == '00':
						parsed['automaticTempControl'] = 0
					elif payload[2:4] == '01':
						parsed['automaticTempControl'] = 1
				elif payload[0:2] == '75':
					if payload[2:4] == '00':
						parsed['powerModuleCom'] = 1
					elif payload[2:4] == '01':
						parsed['powerModuleCom'] = 0
				elif payload[0:2] == '5f':
					if payload[2:4] == '00':
						parsed['automaticStatus'] = 0
					elif payload[2:4] == '01':
						parsed['automaticStatus'] = 1
				elif payload[0:2] == '69':
					if payload[2:4] == '00':
						parsed['statusAfterReboot'] = "Last status"
					elif payload[2:4] == '01':
						parsed['statusAfterReboot'] = "On - after return of power supply"
					elif payload[2:4] == '02':
						parsed['statusAfterReboot'] = "Off - after return of power supply"
				elif payload[0:2] == '04':
					parsed['hardwareV'] = payload[2:3] + '.' + payload[3:4]
					parsed['softwareV'] = payload[4:5] + '.' + payload[5:6]
				elif payload[0:2] == '4f':
					if payload[2:4] == '00':
						parsed['frostProtectionStatus'] = 0
					elif payload[2:4] == '01':
						parsed['frostProtectionStatus'] = 1
				elif payload[0:2] == '4f':
					if payload[2:4] == '00':
						parsed['frostProtectionOnOff'] = 0
					elif payload[2:4] == '01':
						parsed['frostProtectionOnOff'] = 1
				elif payload[0:2] == '6e':
					if payload[2:4] == '00':
						parsed['frostProtection'] = 0
					elif payload[2:4] == '01':
						parsed['frostProtection'] = 1

				newPayload = payload[-22:]
				decodageTrame(newPayload)

			if len(payload) == 22 :
				decodageTrame(payload)

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(mclimate_fanCoilThermostat)