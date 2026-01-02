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

class dragino_LDS02():
	def __init__(self):
		self.name = 'dragino_LDS02'

	def parse(self,data,device):
		logging.debug('dragino_LDS02 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')

            # STATUS
			status = 1 if (dataarray[0] & 0x80) else 0
			parsed['status'] = status # 0
			logging.debug(status)

            # BATTERY
			value = (dataarray[0] << 8 | dataarray[1]) & 0x3FFF
			parsed['battery'] = value/1000 # 3.138
			logging.debug('Battery : ' + str(parsed['battery']))

            # MOD
			binary1 = str(hex(dataarray[2])[2:].zfill(2)) # 01
			logging.debug(binary1)
			if binary1 == '01':
			   parsed['MOD'] = 1
			if binary1 == '00':
			   parsed['MOD'] = 0

            # DOOR_OPEN_TIMES
			open_times = dataarray[3]<<16 | dataarray[4]<<8 | dataarray[5]
			parsed['totalopen'] = open_times # 147
			logging.debug('open_times : ' + str(parsed['totalopen']))

            # LAST_DOOR_OPEN_DURATION
			open_duration = dataarray[6]<<16 | dataarray[7]<<8 | dataarray[8]
			parsed['lastopenduration'] = open_duration # 0
			logging.debug('open_duration : ' + str(parsed['lastopenduration']))

            # ALARM
			alarm = dataarray[9]&0x01
			parsed['alarm'] = alarm # 0
			logging.debug('alarm : ' + str(parsed['alarm']))

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(dragino_LDS02)
