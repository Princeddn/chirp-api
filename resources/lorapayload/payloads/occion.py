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

class occion():
	def __init__(self):
		self.name = 'occion'

	def parse(self,data,device):
		logging.debug('Occion Received')
		parsed={}
		data['parsed'] = parsed
		try:
			logging.debug('Parsing')
			payload = data['payload']
			parsed['battery'] = (int(payload[16:20], 16) - int("8000", 16)) / 100
			if payload[20:21] == "7" :
				value = int("8000", 16) - int(payload[20:24], 16)
				parsed['temperature'] = (value / 100)*(-1) 
			elif payload[20:21] == "8" :
				parsed['temperature'] = (int(payload[20:24], 16) - int("8000", 16)) / 100
			parsed['humidity'] = (int(payload[24:28], 16) - int("8000", 16)) / 100
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(occion)
