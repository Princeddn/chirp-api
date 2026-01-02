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

class mclimate_AQI():
	def __init__(self):
		self.name = 'mclimate_AQI'

	def parse(self,data,device):
		logging.debug('mclimate AQI Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			sAQI1 = str(bin(int(payload[2:4], 16))[2:].zfill(8))
			binary2 = str(bin(int(payload[4:6], 16))[2:].zfill(8))
			sAQI2 = binary2[0:1]
			p1 = str(bin(int(payload[12:14], 16))[2:].zfill(8))
			binary7 = str(bin(int(payload[14:16], 16))[2:].zfill(8))
			p2 = binary7[0:3]
			t1 = binary7[4:]
			binary8 = str(bin(int(payload[16:18], 16))[2:].zfill(8))
			t2 = binary8[0:6]
			parsed['saqi'] = int('' + sAQI1 + sAQI2, 2) * 16 # 32
			parsed['aqi'] = int(binary2[1:7], 2) * 16 # 128
			parsed['voc'] = int(payload[8:10], 16) * 4 # 0
			parsed['humidity'] = (int(payload[10:12], 16) * 4) / 10 # 53,6
			parsed['pressure'] = (int('' + p1 + p2, 2) * 40 + 30000) / 100 # 982
			parsed['temperature'] = (int('' + t1 + t2, 2) - 400) / 10 # 24,5
			parsed['accuracy'] = int(binary8[-2:], 2) # 1
			parsed['voltage'] = ((int(payload[18:20], 16) * 8) + 1600) / 1000 # 3,4 V
			#logging.debug(parsed['saqi'])
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(mclimate_AQI)
