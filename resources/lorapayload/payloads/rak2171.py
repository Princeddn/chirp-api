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
from datetime import datetime

class rak2171():
	def __init__(self):
		self.name = 'rak2171'

	def parse(self,data,device):
		logging.debug('rak2171 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			payload = data['payload']
			logging.debug('Parsing')
			logging.debug(payload)
			
			if payload[0:2] == 'ca':
				logging.debug('Payload Type > No Location')
				parsed['payloadType'] = 'No location payload > GPS has no fix'
				parsed['messageID'] = int(payload[2:4],16)
				parsed['applicationID'] = int(payload[4:12],16)
				parsed['deviceID'] = int(payload[12:20],16)
				parsed['battery'] = int(payload[20:22],16)
				timestamp = int(payload[22:30], 16)
				dt_object = datetime.utcfromtimestamp(timestamp)
				parsed['time'] = dt_object.strftime('%Y-%m-%d %H:%M:%S')
				status = bin(int(payload[30:32],16))[2:].zfill(8)
				parsed['epo'] = status[7:8]
				parsed['charging'] = status[6:7]
				if status[4:6] == '00':
					parsed['status'] = "Open the GPS fix"
				elif status[4:6] == '01':
					parsed['status'] = "Locating"
				elif status[4:6] == '10':
					parsed['status'] = "Successful"
				elif status[4:6] == '11':
					parsed['status'] = "Failed"
			
			elif payload[0:2] == 'cb':
				logging.debug('Payload Type > Location')
				parsed['payloadType'] = 'Location payload > GPS has a fix'
				parsed['messageID'] = int(payload[2:4],16)
				parsed['applicationID'] = int(payload[4:12],16)
				parsed['deviceID'] = int(payload[12:20],16)
				parsed['longitude'] = int(payload[20:28],16)
				parsed['latitude'] = int(payload[28:36],16)
				parsed['accuracy'] = int(payload[36:38],16)
				parsed['gpsNumber'] = int(payload[38:40],16)
				parsed['battery'] = int(payload[40:42],16)
				timestamp = int(payload[42:50], 16)
				dt_object = datetime.utcfromtimestamp(timestamp)
				parsed['time'] = dt_object.strftime('%Y-%m-%d %H:%M:%S')
				if status[50:52] == '00':
					parsed['status'] = "Open the GPS fix"
				elif status[50:52] == '01':
					parsed['status'] = "Locating"
				elif status[50:52] == '10':
					parsed['status'] = "Successful"
				elif status[50:52] == '11':
					parsed['status'] = "Failed"

			elif payload[0:2] == 'cc':
				logging.debug('Payload Type > Send SOS')
				parsed['payloadType'] = 'Send SOS Payload'
				parsed['messageID'] = int(payload[2:4],16)
				parsed['applicationID'] = int(payload[4:12],16)
				parsed['deviceID'] = int(payload[12:20],16)
				parsed['longitude'] = int(payload[20:28],16)
				parsed['latitude'] = int(payload[28:36],16)

			elif payload[0:2] == 'cd':
				logging.debug('Payload Type > Cancel SOS')
				parsed['payloadType'] = 'Cancel SOS Payload'
				parsed['sos'] = 0
				parsed['messageID'] = int(payload[2:4],16)
				parsed['applicationID'] = int(payload[4:12],16)
				parsed['deviceID'] = int(payload[12:20],16)

			elif payload[0:2] == 'ce':
				logging.debug('Payload Type > 6-level alarm')
				parsed['payloadType'] = '6-level Sensitivity Alarm Payload'
				parsed['messageID'] = int(payload[2:4],16)
				parsed['applicationID'] = int(payload[4:12],16)
				parsed['deviceID'] = int(payload[12:20],16)
				if payload[20:22] == '1':
					parsed['level'] = "Mild Vibration"
				elif payload[20:22] == '2':
					parsed['level'] = "Violent Vibration"
				elif payload[20:22] == '3':
					parsed['level'] = "Movement"
				elif payload[20:22] == '4':
					parsed['level'] = "Mild Shaking"
				elif payload[20:22] == '5':
					parsed['level'] = "Violent Shaking"
				elif payload[20:22] == '6':
					parsed['level'] = "Fall"

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(rak2171)
