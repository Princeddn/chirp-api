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

class dragino_RS485_LN_OTMetricPolier():
	def __init__(self):
		self.name = 'dragino_RS485_LN_OTMetricPolier'

	def parse(self,data,device):
		logging.debug('dragino_RS485_LN_OTMetricPolier Received')
		parsed={}
		data['parsed'] = parsed
		try:
			logging.debug('Parsing')
			payload = data['payload']
			parsed['VOLTAGE1'] = int(payload[2:8], 16) / 1000
			parsed['VOLTAGE2'] = int(payload[8:14], 16) / 1000
			parsed['VOLTAGE3'] = int(payload[14:20], 16) / 1000
			parsed['CURRENT1'] = int(payload[20:26], 16) / 1000
			parsed['CURRENT2'] = int(payload[26:32], 16) / 1000
			parsed['CURRENT3'] = int(payload[32:38], 16) / 1000
			parsed['TotalPOWER'] = int(payload[38:48], 16) / 1000
			parsed['TotalCONSO'] = int(payload[48:58], 16) / 10000
			logging.debug('TotalCONSO : ' + payload[48:58])
			parsed['PolierTension'] = int(payload[68:74], 16)
			parsed['PolierCourant'] = int(payload[74:80], 16)
			parsed['PolierPower'] = int(payload[80:86], 16)
			parsed['PolierConso'] = int(payload[86:92], 16)

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(dragino_RS485_LN_OTMetricPolier)
