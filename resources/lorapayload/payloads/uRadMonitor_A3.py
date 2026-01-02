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

class uRadMonitor_A3():
	def __init__(self):
		self.name = 'uRadMonitor_A3'

	def parse(self,data,device):
		logging.debug('uRadMonitor_A3 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			logging.debug(payload)
			parsed['id'] = payload[0:8]
			parsed['versionHW'] = int(payload[8:10],16)
			parsed['versionSW'] = int(payload[10:12],16)
			parsed['timestamp'] = int(payload[12:20],16)
			parsed['temperature'] = (int(payload[20:24],16))/100
			parsed['pression'] = int(payload[24:28],16) + 65535
			parsed['humidity'] = (int(payload[28:30],16))/2
			parsed['voc'] = (int(payload[30:36],16))/1000
			parsed['noise'] = (int(payload[36:38],16))/2
			parsed['CO2'] = int(payload[38:42],16)
			parsed['formaldehyde'] = int(payload[42:46],16)
			parsed['ozone'] = int(payload[46:50],16)
			parsed['PM1'] = int(payload[50:54],16)
			parsed['PM25'] = int(payload[54:58],16)
			parsed['PM10'] = int(payload[58:62],16)
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(uRadMonitor_A3)
