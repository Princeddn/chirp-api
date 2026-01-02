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

class netvox():
	def __init__(self):
		self.name = 'netvox'

	def parse(self,data,device):
		logging.debug('Netvox Received')
		parsed={}
		data['parsed'] = parsed
		dataarray = utils.hexarray_from_string(data['payload'])
		if (dataarray[1] == 0x12 or dataarray[1] == 0x02 or dataarray[2] == 0x1D or dataarray[2] == 0x7D) :
			logging.debug('Parsing R311A/R313A')
			try:
				if dataarray[2] == 0x01:
					parsed['battery'] = int(dataarray[3])/10
					parsed['status'] = int(dataarray[4])
			except Exception as e:
				logging.debug(str(e))
				logging.debug('Unparsable data')
		if dataarray[1] == 0x59:
			logging.debug('Parsing R719A')
			try:
				if dataarray[2] == 0x01:
					parsed['battery'] = int(dataarray[3])/10
					parsed['parkingstatus'] = int(dataarray[4])
					parsed['radarstatus'] = int(dataarray[5])
					parsed['power1'] = int(dataarray[8])
			except Exception as e:
				logging.debug(str(e))
				logging.debug('Unparsable data')
		if dataarray[1] == 0x69:
			logging.debug('Parsing R602A')
			try:
				if dataarray[2] == 0x01:
					parsed['status'] = int(dataarray[5])
			except Exception as e:
				logging.debug(str(e))
				logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(netvox)
