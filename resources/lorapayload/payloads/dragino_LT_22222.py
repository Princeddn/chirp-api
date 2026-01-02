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

class dragino_LT_22222():
	def __init__(self):
		self.name = 'dragino_LT_22222'

	def parse(self,data,device):
		logging.debug('dragino_LT_22222 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			logging.debug('Parsing')
			payload = data['payload']
			mod = int(payload[-1], 16)
			if mod == 1 :
				logging.debug('MOD1')
				parsed['mod'] = 1
				parsed['AVI1']=int(payload[0:4], 16) / 1000
				parsed['AVI2']=int(payload[4:8], 16) / 1000
				parsed['ACI1']=int(payload[8:12], 16) / 1000
				parsed['ACI2']=int(payload[12:16], 16) / 1000
				binary = bin(int(payload[16:18], 16))[2:].zfill(8)
				parsed['RO1']=binary[0:1]
				parsed['RO2']=binary[1:2]
				parsed['DI3']=binary[2:3]
				parsed['DI2']=binary[3:4]
				parsed['DI1']=binary[4:5]
				parsed['DO3']=binary[5:6]
				parsed['DO2']=binary[6:7]
				parsed['DO1']=binary[7:8]
			if mod == 2 :
				logging.debug('MOD2')
				parsed['mod'] = 2
				parsed['COUNT1']=int(payload[0:8], 16)
				parsed['COUNT2']=int(payload[8:16], 16)
				binary = bin(int(payload[16:18], 16))[2:].zfill(8)
				parsed['RO1']=binary[0:1]
				parsed['RO2']=binary[1:2]
				parsed['DI3']=binary[2:3]
				parsed['DI2']=binary[3:4]
				parsed['DI1']=binary[4:5]
				parsed['DO3']=binary[5:6]
				parsed['DO2']=binary[6:7]
				parsed['DO1']=binary[7:8]
			if mod == 3 :
				logging.debug('MOD3')
				parsed['mod'] = 3
				parsed['COUNT1']=int(payload[0:8], 16)
				parsed['ACI1']=int(payload[8:12], 16) / 1000
				parsed['ACI2']=int(payload[12:16], 16) / 1000
				binary = bin(int(payload[16:18], 16))[2:].zfill(8)
				parsed['RO1']=binary[0:1]
				parsed['RO2']=binary[1:2]
				parsed['DI3']=binary[2:3]
				parsed['DI2']=binary[3:4]
				parsed['DI1']=binary[4:5]
				parsed['DO3']=binary[5:6]
				parsed['DO2']=binary[6:7]
				parsed['DO1']=binary[7:8]
			if mod == 4 :
				logging.debug('MOD4')
				parsed['mod'] = 4
				parsed['COUNT1']=int(payload[0:8], 16)
				parsed['AVI1COUNT']=int(payload[8:16], 16)
				binary = bin(int(payload[16:18], 16))[2:].zfill(8)
				parsed['RO1']=binary[0:1]
				parsed['RO2']=binary[1:2]
				parsed['DI3']=binary[2:3]
				parsed['DI2']=binary[3:4]
				parsed['DI1']=binary[4:5]
				parsed['DO3']=binary[5:6]
				parsed['DO2']=binary[6:7]
				parsed['DO1']=binary[7:8]
			if mod == 5 :
				logging.debug('MOD5')
				parsed['mod'] = 5
				parsed['AVI1']=int(payload[0:4], 16) / 1000
				parsed['AVI2']=int(payload[4:8], 16) / 1000
				parsed['ACI1']=int(payload[8:12], 16) / 1000
				parsed['COUNT1']=int(payload[12:16], 16)
				binary = bin(int(payload[16:18], 16))[2:].zfill(8)
				parsed['RO1']=binary[0:1]
				parsed['RO2']=binary[1:2]
				parsed['DI3']=binary[2:3]
				parsed['DI2']=binary[3:4]
				parsed['DI1']=binary[4:5]
				parsed['DO3']=binary[5:6]
				parsed['DO2']=binary[6:7]
				parsed['DO1']=binary[7:8]
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(dragino_LT_22222)
