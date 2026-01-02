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

class dragino_LAQ4():
	def __init__(self):
		self.name = 'dragino_LAQ4'

	def parse(self,data,device):
		logging.debug('LAQ4 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			logging.debug('Parsing')
			payload = data['payload']
			parsed['battery'] = int(payload[0:4], 16) / 1000
			parsed['tvoc'] = int(payload[6:10], 16)
			parsed['eco2'] = int(payload[10:14], 16)
			if payload[14:15] == "F" :
				value = int(payload[14:18], 16) - 65536
				parsed['temperature'] = (value / 10)
			else :
				parsed['temperature'] = int(payload[14:18], 16) / 10
			parsed['humidity'] = int(payload[18:22], 16) / 10
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(dragino_LAQ4)