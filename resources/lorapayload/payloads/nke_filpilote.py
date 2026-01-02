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

class nke_filpilote():
	def __init__(self):
		self.name = 'nke_filpilote'

	def parse(self,data,device):
		logging.debug('Nke Fil Pilote Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			payload = data['payload']
			logging.debug('Parsing')
			l = len(payload)
			state = payload[l - 1:]
			if state == '0':
				parsed['state'] = 'Comfort'
			elif state == '1':
				parsed['state'] = 'Economic'
			elif state == '2':
				parsed['state'] = 'Antifreeze'
			elif state == '3':
				parsed['state'] = 'Stop'
			elif state == '4':
				parsed['state'] = 'Comfort -1°C'
			elif state == '5':
				parsed['state'] = 'Comfort -2°C'
			else:
				parsed['state'] = 'ERROR'
			logging.debug('State .... ' + str(parsed['state']))
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(nke_filpilote)
