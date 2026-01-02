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

class dragino_LGT92():
	def __init__(self):
		self.name = 'dragino_LGT92'

	def parse(self,data,device):
		logging.debug('dragino_LGHT92 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			payload = data['payload']
			logging.debug('Parsing')
			payload = data['payload']
			if payload[0:1] == "F" :
				value = int(payload[0:8], 16) - 4294967296
				parsed['latitude'] = (value / 1000000)
			else :
				parsed['latitude'] = int(payload[0:8], 16) / 1000000
			if payload[8:8] == "F" :
				value = int(payload[8:16], 16) - 4294967296
				parsed['longitude'] = (value / 1000000)
			else :
				parsed['longitude'] = int(payload[8:16], 16) / 1000000
			parsed['alarm'] = int( int(payload[16:18],16) & int("0x40",16) >0)
			parsed['battery'] = (int(payload[16:20],16) & int("0x3FFF",16))/1000
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(dragino_LGT92)