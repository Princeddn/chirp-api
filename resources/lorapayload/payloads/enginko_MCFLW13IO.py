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

class enginko_MCFLW13IO():
	def __init__(self):
		self.name = 'enginko_MCFLW13IO'

	def parse(self,data,device):
		logging.debug('enginko_MCFLW13IO Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			payload = data['payload']
			logging.debug('Parsing')

			if(payload[0:2] == '0a'):
				datetime = payload[2:10]
				inputs = payload[10:18]
				outputs = payload[18:26]
				inputsEvents = payload[26:34]
				inputState = '1' in inputs
				if inputState:
					parsed['inputState'] = '1'
				else:
					parsed['inputState'] = '0'	
				outputState = '1' in outputs
				if outputState:
					parsed['outputState'] = '1'
				else:
					parsed['outputState'] = '0'				
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(enginko_MCFLW13IO)
