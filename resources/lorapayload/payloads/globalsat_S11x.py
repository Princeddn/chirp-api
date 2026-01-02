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
import binascii
from binascii import unhexlify

class globalsat_S11x():
	def __init__(self):
		self.name = 'globalsat_S11x'

	def parse(self,data):
		logging.debug('globalsat_S11x Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')

            # Device Type
			binary0 = ''
			for x in range(0,1):
			   binary0 = binary0 + str(hex(dataarray[x])[2:].zfill(2))
			if binary0 == '01':
			   parsed['deviceType'] = 'CO2'
			elif binary0 == '02':
			   parsed['deviceType'] = 'CO'
			elif binary0 == '03':
			   parsed['deviceType'] = 'PM2.5'
			logging.debug('Device Type : ' + parsed['deviceType'])

            # Temperature
			binary1 = ''
			for x in range(1,3):
			   binary1 = binary1 + str(hex(dataarray[x])[2:].zfill(2)) # 0961
			parsed['temperature'] = (int(binary1, 16))/100 # 24.01
			logging.debug('Temperature : ' + str(parsed['temperature']))

            # Humidity
			binary2 = ''
			for x in range(3,5):
			   binary2 = binary2 + str(hex(dataarray[x])[2:].zfill(2)) # 1395
			parsed['humidity'] = (int(binary2, 16))/100 # 50.13
			logging.debug('Humidity : ' + str(parsed['humidity']))

            # Density
			binary3 = ''
			for x in range(5,7):
			   binary3 = binary3 + str(hex(dataarray[x])[2:].zfill(2)) # 0292
			parsed['density'] = int(binary3, 16) # 658
			logging.debug('Density : ' + str(parsed['density']))

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(globalsat_S11x)
