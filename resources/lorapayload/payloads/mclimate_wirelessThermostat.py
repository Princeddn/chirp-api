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

class mclimate_wirelessThermostat():
	def __init__(self):
		self.name = 'mclimate_wirelessThermostat'

	def parse(self,data,device):
		logging.debug('mclimate_wirelessThermostat Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			logging.debug(len(payload)) 

			def decodageTrame(payload):
				reason = payload[0:2]
				if reason == '81': # 810288800A45010900027A00
					parsed['temperature'] = (int(payload[2:6], 16) - 400) / 10
					parsed['humidity'] = (int(payload[6:8], 16) * 100) / 256
					parsed['voltage'] = int(payload[8:12], 16)
					parsed['targetTemp'] = int(payload[12:16], 16) / 10
					powerSource = payload[16:18]
					if powerSource == '00':
						parsed['powerSource'] = 'Photovoltaic'
					elif powerSource == '01':
						parsed['powerSource'] = 'Battery'
					elif powerSource == '02':
						parsed['powerSource'] = 'USB'
					parsed['light'] = int(payload[18:22], 16)
					pir = payload[22:24]
					if pir == '00':
						parsed['pir'] = 0
					elif pir == '01':
						parsed['pir'] = 1
				elif reason == '01': # 010288800A451700027A00
					parsed['temperature'] = (int(payload[2:6], 16) - 400) / 10
					parsed['humidity'] = (int(payload[6:8], 16) * 100) / 256
					parsed['voltage'] = int(payload[8:12], 16)
					parsed['targetTemp'] = int(payload[12:14], 16)
					powerSource = payload[14:16]
					if powerSource == '00':
						parsed['powerSource'] = 'Photovoltaic'
					elif powerSource == '01':
						parsed['powerSource'] = 'Battery'
					elif powerSource == '02':
						parsed['powerSource'] = 'USB'
					parsed['light'] = int(payload[16:20], 16)
					pir = payload[20:22]
					if pir == '00':
						parsed['pir'] = 0
					elif pir == '01':
						parsed['pir'] = 1

			testPayload = payload[-22:]
			if testPayload[0:2] == '01':
				if len(payload) > 22 :
					if payload[0:2] == '14':
						if payload[2:4] == '00':
							parsed['ChildLockStatus'] = 0
						elif payload[2:4] == '01':
							parsed['ChildLockStatus'] = 1
					elif payload[0:2] == '3d':
						if payload[2:4] == '00':
							parsed['PirStatus'] = 0
						elif payload[2:4] == '01':
							parsed['PirStatus'] = 1
					elif payload[0:2] == '30':
						parsed['manualTargetTemperatureUpdate'] = int(payload[2:4], 16)
					newPayload = payload[-22:]
					decodageTrame(newPayload)

				if len(payload) == 22 :
					decodageTrame(payload)
			else:
				if len(payload) > 24 :
					if payload[0:2] == '14':
						if payload[2:4] == '00':
							parsed['ChildLockStatus'] = 0
						elif payload[2:4] == '01':
							parsed['ChildLockStatus'] = 1
					elif payload[0:2] == '3d':
						if payload[2:4] == '00':
							parsed['PirStatus'] = 0
						elif payload[2:4] == '01':
							parsed['PirStatus'] = 1
					elif payload[0:2] == '30':
						parsed['manualTargetTemperatureUpdate'] = int(payload[2:4], 16)
					newPayload = payload[-24:]
					decodageTrame(newPayload)

				if len(payload) == 24 :
					decodageTrame(payload)

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(mclimate_wirelessThermostat)