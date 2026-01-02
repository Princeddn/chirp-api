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

class dragino_D20LBLS():
	def __init__(self):
		self.name = 'dragino_D20LBLS'

	def parse(self,data,device):
		logging.debug('dragino_D20LBLS Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			logging.debug(payload)
			parsed['battery'] = int(payload[0:4], 16)/1000
			redProbe = int(payload[4:8],16) & 0x8000
			if redProbe == 0:
				parsed['tempC1'] = int(payload[4:8], 16)/10
			else:
				parsed['tempC1'] = (int(payload[4:8], 16)-65536)/10
			parsed['alarm'] = int(payload[12:14],16) & 0x01
			pa8Level = ( int(payload[12:14],16) & 0x80 ) >> 7
			if pa8Level == 0:
				parsed['pa8Level'] = 'high'
			else:
				parsed['pa8Level'] = 'low'
			mod = ( int(payload[12:14],16) & 0x7C ) >> 7
			if mod == 0:
				parsed['mod'] = '1'
			else:
				parsed['mod'] = '31'

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(dragino_D20LBLS)
