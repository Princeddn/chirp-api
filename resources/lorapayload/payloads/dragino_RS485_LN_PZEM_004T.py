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

class dragino_RS485_LN_PZEM_004T():
	def __init__(self):
		self.name = 'dragino_RS485_LN_PZEM_004T'

	def parse(self,data,device):
		logging.debug('dragino_RS485 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			logging.debug('Parsing')
			payload = data['payload']
			parsed['VOLTAGE1'] = int(payload[2:6], 16) / 10
			parsed['CURRENT1'] = int(payload[10:14]+payload[6:10], 16) / 1000
			parsed['POWER1'] = int(payload[18:22]+payload[14:18], 16) / 10
			parsed['ENERGY1'] = int(payload[26:30]+payload[22:26], 16)
			parsed['FREQUENCY1'] = int(payload[30:34], 16) / 10
			parsed['POWERFACTOR1'] = int(payload[34:38], 16) / 100
			parsed['ALARM1'] = int(payload[38:42], 16)
			parsed['VOLTAGE2'] = int(payload[42:46], 16) / 10
			parsed['CURRENT2'] = int(payload[50:54]+payload[46:50], 16) / 1000
			parsed['POWER2'] = int(payload[58:62]+payload[54:58], 16) / 10
			parsed['ENERGY2'] = int(payload[66:70]+payload[62:66], 16)
			parsed['FREQUENCY2'] = int(payload[70:74], 16) / 10
			parsed['POWERFACTOR2'] = int(payload[74:78], 16) / 100
			parsed['ALARM2'] = int(payload[78:82], 16)
			parsed['VOLTAGE3'] = int(payload[82:86], 16) / 10
			parsed['CURRENT3'] = int(payload[90:94]+payload[86:90], 16) / 1000
			parsed['POWER3'] = int(payload[98:102]+payload[94:98], 16) / 10
			parsed['ENERGY3'] = int(payload[106:110]+payload[102:106], 16)
			parsed['FREQUENCY3'] = int(payload[110:114], 16) / 10
			parsed['POWERFACTOR3'] = int(payload[114:118], 16) / 100
			parsed['ALARM3'] = int(payload[118:122], 16)
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(dragino_RS485_LN_PZEM_004T)
