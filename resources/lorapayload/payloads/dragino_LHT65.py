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

class dragino_LHT65():
	def __init__(self):
		self.name = 'dragino_LHT65'

	def parse(self,data,device):
		logging.debug('dragino_LHT65 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			parsed['BAT']=float(int(hex( (dataarray[0]<<8) | dataarray[1]),16) & 0x3FFF) / 1000
			value = (dataarray[2]<<8) | dataarray[3]
			if(dataarray[2] & 0x80):
				value = int(hex(value),16) - 65536
			parsed['temperature'] = value/100
			parsed['humidity'] = int(payload[8:12], 16) / 10
			mod = str(payload[12:14])
			logging.debug(mod)
			if mod == "01" :
				logging.debug('MOD1')
				if payload[14:15] == "f" :
					value = int(payload[14:18], 16) - 65536
					parsed['E1'] = (value / 100)
				else :
					parsed['E1'] = int(payload[14:18], 16) / 100
			if mod == "04" :
				logging.debug('MOD4')
				parsed['E4']=int(payload[14:16], 16)
			if mod == "14" :
				logging.debug('MOD4 - ERROR CABLE')
			if mod == "05" :
				logging.debug('MOD5')
				parsed['E5']=int(payload[14:18], 16)
			if mod == "15" :
				logging.debug('MOD5 - ERROR CABLE')
			if mod == "06" :
				logging.debug('MOD6')
				parsed['E6']=int(payload[14:18], 16)
			if mod == "16" :
				logging.debug('MOD6 - ERROR CABLE')
			if mod == "07" :
				logging.debug('MOD7')
				parsed['E7']=int(payload[14:18], 16)
			if mod == "17" :
				logging.debug('MOD7 - ERROR CABLE')
			if mod == "08" :
				logging.debug('MOD8')
				parsed['E8']=int(payload[14:22], 16)
			if mod == "18" :
				logging.debug('MOD8 - ERROR CABLE')
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(dragino_LHT65)
