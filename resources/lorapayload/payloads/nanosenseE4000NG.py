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

class nanosenseE4000NG():
	def __init__(self):
		self.name = 'nanosenseE4000NG'

	def parse(self,data,device):
		logging.debug('nanosenseE4000NG Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			if dataarray[0] == 0x00:
				logging.debug('There is nanosense E4000NG without capteurs')
				return data
			else:
				logging.debug('There is nanosense E4000NG with capteurs')
			parsed['co2-4'] = float(int(dataarray[1]))*19.6
			parsed['hum-4'] = float(int(dataarray[2]))*0.5
			parsed['temp-4'] = float(int(dataarray[3]))*0.2
			parsed['cov-4'] = float(int(hex( (dataarray[5]<<8) | dataarray[6] ),16))
			parsed['co2-3'] = float(int(dataarray[12]))*19.6
			parsed['hum-3'] = float(int(dataarray[13]))*0.5
			parsed['temp-3'] = float(int(dataarray[14]))*0.2
			parsed['cov-3'] = int(hex( (dataarray[16]<<8) | dataarray[17] ),16)
			parsed['co2-2'] = float(int(dataarray[23]))*19.6
			parsed['hum-2'] = float(int(dataarray[24]))*0.5
			parsed['temp-2'] = float(int(dataarray[25]))*0.2
			parsed['cov-2'] = int(hex( (dataarray[27]<<8) | dataarray[28] ),16)
			parsed['co2'] = float(int(dataarray[34]))*19.6
			parsed['hum'] = float(int(dataarray[35]))*0.5
			parsed['temp'] = float(int(dataarray[36]))*0.2
			parsed['cov'] = int(hex( (dataarray[38]<<8) | dataarray[29] ),16)
			parsed['co2-moy'] = (parsed['co2']+parsed['co2-2']+parsed['co2-3']+parsed['co2-4'])/4
			parsed['hum-moy'] = (parsed['hum']+parsed['hum-2']+parsed['hum-3']+parsed['hum-4'])/4
			parsed['temp-moy'] = (parsed['temp']+parsed['temp-2']+parsed['temp-3']+parsed['temp-4'])/4
			parsed['cov-moy'] = (parsed['cov']+parsed['cov-2']+parsed['cov-3']+parsed['cov-4'])/4
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(nanosenseE4000NG)