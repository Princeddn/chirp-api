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

class avidsen():
	def __init__(self):
		self.name = 'avidsen'

	def parse(self,data,device):
		logging.debug('Avidsen Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			if dataarray[0] == 0x11:
				logging.debug('This is a garage detector')
				binary = bin(int(str(dataarray[1])))[2:].zfill(8)
				logging.debug('DATA 1 binary is : ' + str(binary))
				open = binary[7:8]
				battery= binary[4:5]
				tension = int(dataarray[2])
				logging.debug('Open is : ' + str(open) + ' , battery is ' + str(battery) + ' and tension is ' + str(tension))
				parsed['ouverture'] = open
				parsed['battery'] = battery
				parsed['tension'] = tension
			elif dataarray[0] == 0x17:
				logging.debug('This is a current clamp')
				binary = bin(int(str(dataarray[1])))[2:].zfill(8)
				logging.debug('DATA 1 binary is : ' + str(binary))
				courant = binary[7:8]
				battery= binary[4:5]
				tension = int(dataarray[4])
				courantval = int(hex( (dataarray[2]<<8) | dataarray[3] ),16)
				logging.debug('Courant is : ' + str(courant) + ' , battery is ' + str(battery) + ' and tension is ' + str(tension) + ' with courant :' + str(courantval))
				parsed['courant'] = courant
				parsed['battery'] = battery
				parsed['tension'] = tension
				parsed['courantval'] = courantval
			else:
				logging.debug('Unknown message')
				return data
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(avidsen)