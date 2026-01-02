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

class dragino_RS485_LN_EM540():
	def __init__(self):
		self.name = 'dragino_RS485_LN_EM540'

	def parse(self,data,device):
		logging.debug('dragino_RS485 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			logging.debug('Parsing')
			payload = data['payload']
			parsed['VOLTAGE1'] = int(payload[0:4], 16) * 10
			parsed['VOLTAGE2'] = int(payload[4:8], 16) * 10
			parsed['VOLTAGE3'] = int(payload[8:12], 16) * 10
			parsed['TotalVOLTAGE'] = int(payload[12:16], 16) * 10
			parsed['CURRENT1'] = int(payload[16:20], 16) * 1000
			parsed['CURRENT2'] = int(payload[20:24], 16) * 1000
			parsed['CURRENT3'] = int(payload[24:28], 16) * 1000
			parsed['POWER1'] = int(payload[28:32], 16) * 10
			parsed['POWER2'] = int(payload[32:36], 16) * 10
			parsed['POWER3'] = int(payload[36:40], 16) * 10
			parsed['TotalPOWER'] = int(payload[40:44], 16) * 10
			parsed['TotalCONSO'] = int(payload[44:48], 16) * 10

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(dragino_RS485_LN_EM540)
