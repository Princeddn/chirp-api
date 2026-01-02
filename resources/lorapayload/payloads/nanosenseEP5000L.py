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

class nanosenseEP5000L():
	def __init__(self):
		self.name = 'nanosenseEP5000L'

	def parse(self,data,device):
		logging.debug('nanosenseEP5000L Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
            # Presence Sensor
			binary1 = bin(int(payload[0:2],16))[2:]
            # Autonomy
			parsed['autonomy'] = int(payload[10:12],16)
            # RH
			parsed['RH'] = int(payload[16:18],16)*0.5
            # Temperature
			binary10 = bin(int(payload[18:22],16))[2:]
			binary10 = binary10.zfill(16)
			parsed['temperature'] = int(binary10[0:9],2)*0.1
            # PM
			binary11 = bin(int(payload[20:28],16))[2:]
			binary11 = binary11.zfill(32)
			parsed['PM10'] = int(binary11[1:10],2)
			parsed['PM2.5'] = int(binary11[10:19],2)
			parsed['PM1'] = int(binary11[19:28],2)
            # Noise
			binary14 = bin(int(payload[26:32],16))[2:]
			binary14 = binary14.zfill(24)
			parsed['averageNoise'] = int(binary14[4:11],2)
			parsed['picNoise'] = int(binary14[11:18],2)
            # CO2
			binary16 = bin(int(payload[30:34],16))[2:]
			binary16 = binary16.zfill(16)
			parsed['CO2'] = int(binary16[3:16],2)
            # TVOC
			parsed['TVOC'] = int(payload[34:38],16)
            # Formaldehyde
			parsed['formaldehyde'] = int(payload[38:42],16)*0.01
            # Benzene
			parsed['benzene'] = int(payload[42:46],16)*0.01
            # Sulphurous Odors
			parsed['sulphurousOdors'] = int(payload[46:48],16)
            # NOx
			parsed['NOx'] = int(payload[48:50],16)*2
            # Ozone
			parsed['ozone'] = int(payload[50:52],16)*2
            # Atmospheric Pressure
			binary27 = bin(int(payload[52:56],16))[2:]
			binary27 = binary27.zfill(16)
			parsed['atmosphericPressure'] = int(binary27[0:14],2)*0.1
            # Lux
			binary28 = bin(int(payload[54:58],16))[2:]
			binary28 = binary28.zfill(16)
			parsed['lux'] = int(binary28[6:16],2)*4
            # Light Color Temperature
			parsed['lightColorTemperature'] = int(payload[58:60],16)*23
            # Light Flickering
			parsed['lightFlickering'] = int(payload[60:62],16)
            # Health Index
			parsed['healthIndex'] = int(payload[62:64],16)
            # Cognitivity Index
			parsed['cognitivityIndex'] = int(payload[64:66],16)
            # Sleeping Index
			parsed['sleepingIndex'] = int(payload[66:68],16)
            # Throat Irritation Index
			parsed['throatIrritationIndex'] = int(payload[68:70],16)
            # Building Index
			parsed['buildingIndex'] = int(payload[70:72],16)
            # Virus Spreading Risk
			parsed['virusSpreadingRisk'] = int(payload[72:74],16)
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(nanosenseEP5000L)