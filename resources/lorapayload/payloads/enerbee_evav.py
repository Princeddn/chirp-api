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
import datetime

class enerbee_evav():
	def __init__(self):
		self.name = 'enerbee_evav'

	def parse(self,data,device):
		logging.debug('enerbee_evav Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			logging.debug(len(payload))
			length = len(payload)
			
			idx = 0
			if payload[6:8] == "ff" and payload[8:10] == "ff" :
				logging.debug('Message initial')
				idx = 10
			
			# First two bytes are data format
			payload_format = int(payload[idx:idx+4], 16)
			idx += 4

			# Third byte in header is the measurement interval in minutes
			interval = int(payload[idx:idx+2], 16)
			idx += 2

			# Calculate block_len
			block_len = 0
			# Temperature
			if (payload_format & 0x0001) != 0:
				block_len += 2
			# Humidity
			if (payload_format & 0x0002) != 0:
				block_len += 2
			# Airflow
			if (payload_format & 0x0004) != 0:
				block_len += 4
			# CO2
			if (payload_format & 0x0008) != 0:
				block_len += 4
			# IAQ
			if (payload_format & 0x0010) != 0:
				block_len += 4
			# Charge
			if (payload_format & 0x0020) != 0:
				block_len += 2
			# Iris position
			if (payload_format & 0x0040) != 0:
				block_len += 2
			# Extended airflow
			if (payload_format & 0x0200) != 0:
				block_len += 2
			# System status
			if (payload_format & 0x0400) != 0:
				block_len += 2

			# Must be a multiple of blocklen
			if (block_len != 0) and (((length-idx) % block_len) == 0):
				blocks = (length-idx) / block_len

				#  Treat each block of data from oldest to most recent
				while idx < length:
					blocks -= 1

					#parsed['date'] = dateMessage - datetime.timedelta(minutes=blocks*interval)

					if (payload_format & 0x0001) != 0:
						temp = int(payload[idx:idx+2], 16)
						if temp > 127:
							temp = 0
						parsed['temperature'] = temp
						idx += 2

					if (payload_format & 0x0002) != 0:
						parsed['humidity'] = int(payload[idx:idx+2], 16)
						idx += 2

					if (payload_format & 0x0004) != 0:
						parsed['airFlowTarget'] = int(payload[idx:idx+2], 16)
						idx += 2
						parsed['airFlowCurrent'] = int(payload[idx:idx+2], 16)
						idx += 2

					if (payload_format & 0x0008) != 0:
						parsed['co2'] = int(payload[idx:idx+4], 16)
						idx += 4

					if (payload_format & 0x0010) != 0:
						parsed['iaq'] = int(payload[idx:idx+4], 16)
						idx += 4

					if (payload_format & 0x0020) != 0:
						parsed['charge'] = int(payload[idx:idx+2], 16)
						idx += 2

					if (payload_format & 0x0040) != 0:
						parsed['register'] = int(payload[idx:idx+2], 16)
						idx += 2

					if (payload_format & 0x0200) != 0:
						ext = int(payload[idx:idx+2], 16)
						if (payload_format & 0x0004) != 0:
							parsed['airFlowTarget'] += ((ext & 0x0F) << 8)
						else :
							parsed['airFlowTarget'] = ((ext & 0x0F) << 8)
						if (payload_format & 0x0004) != 0:
							parsed['airFlowCurrent'] += ((ext & 0xF0) << 4)
						else :
							parsed['airFlowCurrent'] = ((ext & 0xF0) << 4)
						idx += 2

					if (payload_format & 0x0400) != 0:
						status = int(payload[idx:idx+2], 16)
						if status == 0:
							parsed['status'] = 'Non défini'
						elif status == 1:
							parsed['status'] = 'Fonctionnement normal'
						elif status == 2:
							parsed['status'] = 'En charge'
						elif status == 3:
							parsed['status'] = 'Standby'
						elif status == 4:
							parsed['status'] = 'Arret'
						elif status == 5:
							parsed['status'] = 'Erreur moteur'
						elif status == 6:
							parsed['status'] = 'Erreur capteur T/H'
						elif status == 7:
							parsed['status'] = "Erreur capteur qualité d'air"
						idx +=2
			
			return data
		
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(enerbee_evav)