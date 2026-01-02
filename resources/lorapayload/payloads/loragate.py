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

class loragate():
	def __init__(self):
		self.name = 'loragate'

	def parse(self,data,device):
		logging.debug('Loragate Received')
		parsed={}
		data['parsed'] = parsed
		if device == "loragate_ascii":
			try:
				dataarray = utils.hexarray_from_string(data['payload'])
				logging.debug('Parsing')
				parsed['value'] = bytearray.fromhex(data['payload']).decode()
			except Exception as e:
				logging.debug(str(e))
				logging.debug('Unparsable data')
		return data

globals.COMPATIBILITY.append(loragate)