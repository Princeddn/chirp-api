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

class senlabM():
	def __init__(self):
		self.name = 'senlabM'

	def parse(self,data,device):
		#02dc8e179c100000222a
		logging.debug('SenlabM Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			pulse=str(int(utils.to_hex_string([dataarray[-4],dataarray[-3],dataarray[-2],dataarray[-1]]),16))
			logging.debug('Pulse is ' + str(pulse))
			parsed['pulse']=pulse
			parsed['battery']=int(hex(dataarray[1]),16)/254*100
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(senlabM)