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

class nke_torano():
	def __init__(self):
		self.name = 'nke_torano'

	def parse(self,data,device):
		logging.debug('Nke Torano Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			payload = data['payload']
			logging.debug('Parsing')

			logging.debug(payload[4:8])
			if payload[4:8] == '000c':
				logging.debug('Analog Input Report')
				parsed['AnalogInput'] = struct.unpack('!f', bytes.fromhex(payload[14:22]))[0]

			elif payload[4:8] == '0050':
				logging.debug('Configuration Report')
				parsed['battery'] = struct.unpack('!B', bytes.fromhex(payload[14:16]))[0]

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(nke_torano)