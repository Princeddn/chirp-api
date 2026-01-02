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

class rak7205():
	def __init__(self):
		self.name = 'rak7205'

	def parse(self,data,device):
		logging.debug('rak7205 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			payload = data['payload']
			logging.debug('Parsing')
			while len(payload) > 4 :
				flag = payload[0:4]
				if flag == "0768":
					parsed['humidity'] = int(payload[4:6], 16) * 0.5
					payload = payload[6:];
				elif flag == "0673":
					parsed['pressure'] = int(payload[4:8], 16) * 0.1
					payload = payload[8:];
				elif flag == "0267":
					parsed['temperature'] = int(payload[4:8], 16) * 0.1
					payload = payload[8:];
				elif flag == "0188":
					parsed['latitude'] = int(payload[4:10], 16) * 0.0001
					parsed['longitude'] = int(payload[10:16], 16) * 0.0001
					parsed['altitude'] = int(payload[16:22], 16) * 0.01
					payload = payload[22:];
				elif flag == "0371":
					parsed['accelerationx'] = int(payload[4:8], 16) * 0.0001
					parsed['accelerationy'] = int(payload[8:12], 16) * 0.0001
					parsed['accelerationz'] = int(payload[12:16], 16) * 0.01
					payload = payload[16:];
				elif flag == "0402":
					parsed['gas'] = int(payload[4:8], 16) * 0.01
					payload = payload[8:];
				elif flag == "0802":
					parsed['battery'] = round(int(payload[4:8], 16) * 0.01,2)
					payload = payload[8:];
				elif flag == "0586":
					payload = payload[16:];
				elif flag == "0902":
					payload = payload[8:];
				elif flag == "0a02":
					payload = payload[8:];
				elif flag == "0b02":
					payload = payload[28:];
				else :
					payload = payload[7:];
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(rak7205)
