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
from binascii import unhexlify

class nke_triphaso():
	def __init__(self):
		self.name = 'nke_triphaso'

	def parse(self,data,device):
		logging.debug('Nke Triphaso Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			payload = data['payload']
			logging.debug('Parsing')

			if payload[2:4] == '0a':
				logging.debug('Report attributes')
				cluser = payload[4:6] + payload[6:8]
				connector = payload[0:2]

				if connector == '11':
					logging.debug('Phase A')
					connectorPhase = 'PhaseA'
				elif connector == '31':
					logging.debug('Phase B')
					connectorPhase = 'PhaseB'
				elif connector == '51':
					logging.debug('Phase C')
					connectorPhase = 'PhaseC'
				elif connector == '71':
					logging.debug('Phase A+B+C')
					connectorPhase = 'PhaseABC'

				if cluser == '800a':
					logging.debug('Energy and power metering')
					positiveActiveEnergy = int(payload[16:24],16)
					parsed['positiveActiveEnergy_'+connectorPhase] = positiveActiveEnergy
					negativeActiveEnergy = int(payload[24:32], 16)
					parsed['negativeActiveEnergy_'+connectorPhase] = negativeActiveEnergy
					positiveReactiveEnergy = int(payload[32:40], 16)
					parsed['positiveReactiveEnergy_'+connectorPhase] = positiveReactiveEnergy
					negativeReactiveEnergy = int(payload[40:48], 16)
					parsed['negativeReactiveEnergy_'+connectorPhase] = negativeReactiveEnergy
					positiveActivePower = int(payload[48:56], 16)
					parsed['positiveActivePower_'+connectorPhase] = positiveActivePower
					negativeActivePower = int(payload[56:64], 16)
					parsed['negativeActivePower_'+connectorPhase] = negativeActivePower
					positiveReactivePower = int(payload[64:72], 16)
					parsed['positiveReactivePower_'+connectorPhase] = positiveReactivePower
					negativeReactivePower = int(payload[72:80], 16)
					parsed['negativeReactivePower_'+connectorPhase] = negativeReactivePower

				elif cluser == '800b':
					logging.debug('Voltage an current metering')
					voltage = int(payload[16:20], 16)/10
					parsed['voltage_' + connectorPhase] = voltage
					current = int(payload[20:24], 16)/10
					parsed['current_' + connectorPhase] = current
					angle = int(payload[24:28], 16) - 360
					parsed['angleVoltageCurrent_' + connectorPhase] = angle

				elif cluser == '000f':
					logging.debug('Binary Input State')
					state = int(payload[14:16], 16)
					parsed['binaryInputState_' + connectorPhase] = state

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(nke_triphaso)