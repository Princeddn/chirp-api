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

class dragino_RS485_LN_NILAN():
	def __init__(self):
		self.name = 'dragino_RS485_LN_NILAN'

	def parse(self,data,device):
		logging.debug('dragino_RS485 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			logging.debug('Parsing')
			payload = data['payload']
			tempAmb = int(payload[2:6], 16)
			if tempAmb != 65535:
				if tempAmb > 32767:
					tempAmb = tempAmb - 65536
				parsed['tempAmb'] = tempAmb / 100
			tempConsigne = int(payload[6:10], 16)
			if tempConsigne != 65535:
				parsed['tempConsigne'] = tempConsigne / 100
			tempExt = int(payload[10:14], 16)
			if tempExt != 65535:
				if tempExt > 32767:
					tempExt = tempExt - 65536
				parsed['tempExt'] = tempExt / 100
			parsed['alarm'] = int(payload[14:18], 16)

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(dragino_RS485_LN_NILAN)
