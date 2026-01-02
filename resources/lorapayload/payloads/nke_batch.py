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
from .batchnke import batchnke

class nke_batch():
	def __init__(self):
		self.name = 'nke_batch'

	def parse(self,data,device):
		structDict = {"nke_atmo": {
								"size":3, 
								"args": [{'taglbl': 0, "lblname": "temperature", 'resol': 1.0, 'sampletype': 7}, 
										{'taglbl': 1, "lblname": "humidity", 'resol': 1.0, 'sampletype': 6},
										{'taglbl': 2, "lblname": "pression", 'resol': 1.0, 'sampletype': 7},
										{'taglbl': 3, 'resol': 1.0, 'sampletype': 10},
										{'taglbl': 4, 'resol': 1.0, 'sampletype': 10},
										{'taglbl': 5, "lblname": "battery", 'resol': 1.0, 'sampletype': 6}]
								},
						"nke_celso": {
								"size":1, 
								"args": [{'taglbl': 0, "lblname": "temperature", 'resol': 10.0, 'sampletype': 7}, 
										{'taglbl': 1, "lblname": "temperature2", 'resol': 100.0, 'sampletype': 6}]
								},
						"nke_pulsesenso": {
								"size":4, 
								"args": [{'taglbl': 0, "lblname": "index1", 'resol': 1.0, 'sampletype': 10}, 
										{'taglbl': 1, "lblname": "index2", 'resol': 1.0, 'sampletype': 10}, 
										{'taglbl': 2, "lblname": "index3", 'resol': 1.0, 'sampletype': 10}, 
										{'taglbl': 3, "lblname": "state1", 'resol': 1.0, 'sampletype': 1}, 
										{'taglbl': 4, "lblname": "state2", 'resol': 1.0, 'sampletype': 1}, 
										{'taglbl': 5, "lblname": "state3", 'resol': 1.0, 'sampletype': 1}, 
										{'taglbl': 6, "lblname": "battery", 'resol': 100.0, 'sampletype': 6}, 
										{'taglbl': 7, "lblname": "multistate", 'resol': 1.0, 'sampletype': 6}]
								},
						"nke_indoor": {
								"size":2, 
								"args": [{'taglbl': 0, "lblname": "temperature", 'resol': 10.0, 'sampletype': 7}, 
										{'taglbl': 1, "lblname": "humidity", 'resol': 100.0, 'sampletype': 6},
										{'taglbl': 2, "lblname": "battery", 'resol': 1.0, 'sampletype': 6},
										{'taglbl': 3, "lblname": "open", 'resol': 1.0, 'sampletype': 1}]
								}
					}
		logging.debug('Nke_batch Received for device ' + str(device))
		parsed={}
		data['parsed'] = parsed
		try:
			if device in structDict:
				parser = structDict[device]
				result = batchnke.uncompress(parser['size'],parser['args'],data['payload'])
				logging.debug(str(result))
				if 'dataset' in result:
					for datas in result['dataset']:
						if 'data' in datas:
							logging.debug(datas['data'])
							value = datas['data']['value']
							if datas['data']['label_name'] in ['temperature','humidity']:
								value = datas['data']['value']/100
							parsed[datas['data']['label_name']] = value
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(nke_batch)
