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

class rakc15003():
	def __init__(self):
		self.name = 'rakc15003'

	def parse(self,data,device):
		logging.debug('rakc15003 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			payload = data['payload']
			logging.debug('Parsing')
			while len(payload) > 4 :
				flag = payload[2:4]
				if flag == "67":
					if 'temperature' not in parsed:
						parsed['temperature'] = int(payload[4:8], 16) * 0.1
						payload = payload[8:]
						continue
					if 'temperature2' not in parsed:
						parsed['temperature2'] = int(payload[4:8], 16) * 0.1
						payload = payload[8:]
						continue
				elif flag == "68":
					parsed['humidity'] = int(payload[4:6], 16) * 0.5
					payload = payload[6:]
				elif flag == "73":
					parsed['pressure'] = int(payload[4:8], 16) * 0.1
					payload = payload[8:]
				else:
					break

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(rakc15003)
