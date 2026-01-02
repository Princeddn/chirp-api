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

class ewattchambiance():
	def __init__(self):
		self.name = 'ewattchambiance'

	def parse(self,data,device):
		logging.debug('Ewattch Ambiance Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			if dataarray[0] == 0x00:
				logging.debug('This is a periodic message')
				parsed['temperature'] = str(int(utils.to_hex_string([dataarray[4],dataarray[3]]),16)/100)
				logging.debug('Temperature is : ' + parsed['temperature'])
				parsed['humidity'] = str(int(utils.to_hex_string([dataarray[6]]),16)/2)
				logging.debug('Humidity is : ' + parsed['humidity'])
				if len(dataarray)>8:
					parsed['luminosity'] = str(int(utils.to_hex_string([dataarray[9],dataarray[8]]),16))
					logging.debug('Luminosity is : ' + parsed['luminosity'])
					parsed['presence'] = str(int(utils.to_hex_string([dataarray[12],dataarray[11]]),16)*10)
					logging.debug('Presence is : ' + parsed['presence'])
				if len(dataarray)>13 and dataarray[13] == 0x08:
					parsed['co2'] = str(int(utils.to_hex_string([dataarray[15],dataarray[14]]),16))
					logging.debug('Co2 is : ' + parsed['co2'])
					if len(dataarray)>16 and dataarray[16] == 0x0C:
						parsed['compteur1'] = str(int(utils.to_hex_string([dataarray[18],dataarray[17]]),16))
						parsed['compteur2'] = str(int(utils.to_hex_string([dataarray[22],dataarray[21]]),16))
						parsed['compteur3'] = str(int(utils.to_hex_string([dataarray[26],dataarray[25]]),16))
				if len(dataarray)>13 and dataarray[13] == 0x0C:
					parsed['compteur1'] = str(int(utils.to_hex_string([dataarray[15],dataarray[14]]),16))
					parsed['compteur2'] = str(int(utils.to_hex_string([dataarray[19],dataarray[18]]),16))
					parsed['compteur3'] = str(int(utils.to_hex_string([dataarray[23],dataarray[22]]),16))
			elif dataarray[0] == 0x10:
				logging.debug('This is a state message')
				parsed['batterylevel'] = utils.to_hex_string([dataarray[8]])
				logging.debug('Battery level is : ' + parsed['batterylevel'])
				if parsed['batterylevel'] == '0':
					parsed['battery'] = 0
				elif parsed['batterylevel'] == '1':
					parsed['battery'] = 25
				elif parsed['batterylevel'] == '2':
					parsed['battery'] = 50
				elif parsed['batterylevel'] == '7':
					parsed['battery'] = 100
				elif parsed['batterylevel'] == '8':
					parsed['battery'] = 100
			else:
				logging.debug('Unknown message')
				return data
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(ewattchambiance)