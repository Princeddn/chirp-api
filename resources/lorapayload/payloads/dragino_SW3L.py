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

class dragino_SW3L():
	def __init__(self):
		self.name = 'dragino_SW3L'

	def parse(self,data,device):
		logging.debug('dragino_SW3L Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			binary1 = bin(int(payload[0:2],16))[2:].zfill(8)
			CF = (int(payload[0:2], 16) & 0xFC) >> 2
			if CF == 0 :
				parsed['calculateFlag'] = 450
			elif CF == 1 :
				parsed['calculateFlag'] = 390
			elif CF == 2 :
				parsed['calculateFlag'] = 64
			parsed['alarm'] = binary1[6:7]
			mod = int(payload[10:12],16)
			if mod == 0 :
				parsed['totalPulse'] = int(payload[2:10],16)
				parsed['totalWFVolume'] =  parsed['totalPulse'] / parsed['calculateFlag']
			elif mod == 1 :
				parsed['lastPulse'] = int(payload[2:10],16)
				parsed['totalWFtdc'] = parsed['lastPulse'] / parsed['calculateFlag']
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(dragino_SW3L)
