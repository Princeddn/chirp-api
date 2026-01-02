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

class nke():
	def __init__(self):
		self.name = 'nke'

	def parse(self,data,device):
		logging.debug('Nke Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			if dataarray[0] == 0x11:
				logging.debug('This is endpoint 0')
			if dataarray[1] == 0x0a:
				logging.debug('This is report attribute standard')
				binary = bin(int(str(dataarray[1])))[2:].zfill(8)
				if dataarray[2] == 0x04 and dataarray[3] == 0x02:
					logging.debug('This is temperature measurement')
					if dataarray[4] == 0x00 and dataarray[5] == 0x00:
						logging.debug('This is real measurement')
						parsed['temperature'] = int(hex( (dataarray[7]<<8) | dataarray[8] ),16)/100
						logging.debug("Brut Value : " + str(parsed['temperature']))
						if parsed['temperature'] > 100:
							logging.debug('Negative value detected')
							parsed['temperature'] = (655.35 - parsed['temperature'])*(-1)
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(nke)