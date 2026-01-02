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

class mclimate_CO2():
	def __init__(self):
		self.name = 'mclimate_CO2'

	def parse(self,data,device):
		logging.debug('mclimate CO2 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			parsed['CO2'] = int(payload[2:6], 16)
			parsed['temperature'] = (int(payload[6:10], 16) - 400) / 10
			parsed['humidity'] = (int(payload[10:12], 16) * 100) / 256
			parsed['battery'] = (int(payload[12:14], 16) * 8) + 1600
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(mclimate_CO2)
