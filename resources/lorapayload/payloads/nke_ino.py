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

class nke_ino():
	def __init__(self):
		self.name = 'nke_ino'

	def parse(self,data,device):
		logging.debug('Nke Ino Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			payload = data['payload']
			logging.debug('Parsing')

			if payload[2:4] == '0a':
				logging.debug('Report attributes')
				cluser = payload[4:6] + payload[6:8]

				endPoint = payload[0:2]
				if endPoint == '11':
					connectorPhase = 'Input1'
				elif endPoint == '31':
					connectorPhase = 'Input2'
				elif endPoint == '51':
					connectorPhase = 'Input3'
				elif endPoint == '71':
					connectorPhase = 'Input4'
				elif endPoint == '91':
					connectorPhase = 'Input5'
				elif endPoint == 'B1':
					connectorPhase = 'Input6'
				elif endPoint == 'D1':
					connectorPhase = 'Input7'
				elif endPoint == 'F1':
					connectorPhase = 'Input8'
				elif endPoint == '13':
					connectorPhase = 'Input9'
				elif endPoint == '33':
					connectorPhase = 'Input10'
				logging.debug('End point : ' + connectorPhase)

				attributeID = payload[8:10] + payload[10:12]
				if attributeID == '0055':
					dataType = 'PresentValue'
				elif attributeID == '0402':
					dataType = 'Count'
				logging.debug('dataType : ' + dataType)

				attributeType = payload[12:14]
				logging.debug('attributeType : ' + attributeType)
				if attributeType == '10':
					logging.debug('Binary Input State')
					state = int(payload[14:], 16)
					parsed['binaryInputState_' + connectorPhase] = state

				else:
					logging.debug('Count State')
					state = int(payload[14:], 16)
					parsed['countState_' + connectorPhase] = state

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(nke_ino)