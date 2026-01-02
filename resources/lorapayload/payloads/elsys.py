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

def bin8dec(bin) :
	num=bin&0xFF
	if (0x80 & num):
		num = - (0x0100 - num)
	return num

class elsys():
	def __init__(self):
		self.name = 'elsys'

	def parse(self,data,device):
		# https://www.elsys.se/en/elsys-payload/
		logging.debug('Elsys Received')
		TYPE_TEMP = 0x01; #temp 2 bytes -3276.8°C -->3276.7°C
		TYPE_RH = 0x02; #Humidity 1 byte  0-100%
		TYPE_ACC = 0x03; #acceleration 3 bytes X,Y,Z -128 --> 127 +/-63=1G
		TYPE_LIGHT = 0x04; #Light 2 bytes 0-->65535 Lux
		TYPE_MOTION = 0x05; #No of motion 1 byte  0-255
		TYPE_CO2 = 0x06; #Co2 2 bytes 0-65535 ppm
		TYPE_VDD = 0x07; #VDD 2byte 0-65535mV
		TYPE_ANALOG1 = 0x08; #VDD 2byte 0-65535mV
		TYPE_GPS = 0x09; #3bytes lat 3bytes long binary
		TYPE_PULSE1 = 0x0A; #2bytes relative pulse count
		TYPE_PULSE1_ABS = 0x0B; #4bytes no 0->0xFFFFFFFF
		TYPE_EXT_TEMP1 = 0x0C; #2bytes -3276.5C-->3276.5C
		TYPE_EXT_DIGITAL = 0x0D; #1bytes value 1 or 0
		TYPE_EXT_DISTANCE = 0x0E; #2bytes distance in mm
		TYPE_ACC_MOTION = 0x0F; #1byte number of vibration/motion
		TYPE_IR_TEMP = 0x10; #2bytes internal temp 2bytes external temp -3276.5C-->3276.5C
		TYPE_OCCUPANCY = 0x11; #1byte data
		TYPE_WATERLEAK = 0x12; #1byte data 0-255
		TYPE_GRIDEYE = 0x13; #65byte temperature data 1byte ref+64byte external temp
		TYPE_PRESSURE = 0x14; #4byte pressure data (hPa)
		TYPE_SOUND = 0x15; #2byte sound data (peak/avg)
		TYPE_PULSE2 = 0x16; #2bytes 0-->0xFFFF
		TYPE_PULSE2_ABS = 0x17; #4bytes no 0->0xFFFFFFFF
		TYPE_ANALOG2 = 0x18; #2bytes voltage in mV
		TYPE_EXT_TEMP2 = 0x19; #2bytes -3276.5C-->3276.5C
		TYPE_EXT_DIGITAL2 = 0x1A; # 1bytes value 1 or 0
		TYPE_EXT_ANALOG_UV = 0x1B; # 4 bytes signed int (uV)
		TYPE_DEBUG = 0x3D; # 4bytes debug
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			i=0
			while i+1 < len(dataarray):
				if (i!=0):
					i+=1
				if dataarray[i] == TYPE_TEMP: #Temperature
					parsed['temperature'] = float((dataarray[i + 1] << 8) | (dataarray[i + 2])) /10
					i += 2
					continue
				elif dataarray[i] == TYPE_RH: #humidity
					parsed['humidity'] = dataarray[i + 1]
					i += 1
					continue
				elif dataarray[i] == TYPE_ACC: #Acceleration
					parsed['x'] = bin8dec(dataarray[i + 1])
					parsed['y'] = bin8dec(dataarray[i + 2])
					parsed['z'] = bin8dec(dataarray[i + 3])
					i += 3
					continue
				elif dataarray[i] == TYPE_LIGHT: #Light
					parsed['luminosity'] = (dataarray[i + 1] << 8) | (dataarray[i + 2])
					i += 2
					continue
				elif dataarray[i] == TYPE_MOTION: #Motion
					parsed['motion'] = dataarray[i + 1]
					i += 1
					continue
				elif dataarray[i] == TYPE_CO2: #Co2
					parsed['co2'] = (dataarray[i + 1] << 8) | (dataarray[i + 2])
					i += 2
					continue
				elif dataarray[i] == TYPE_VDD: #Battery
					parsed['battery'] = (dataarray[i + 1] << 8) | (dataarray[i + 2])
					i += 2
					continue
				elif dataarray[i] == TYPE_ANALOG1: #Analog1
					parsed['analog1'] = (dataarray[i + 1] << 8) | (dataarray[i + 2])
					i += 2
					continue
				elif dataarray[i] == TYPE_GPS: #GPS   TODO
					i += 5
					continue
				elif dataarray[i] == TYPE_PULSE1: #Pulse 1
					parsed['pulse1'] = (dataarray[i + 1] << 8) | (dataarray[i + 2])
					i += 2
					continue
				elif dataarray[i] == TYPE_PULSE1_ABS: #Puls abs
					parsed['pulse1abs'] = (dataarray[i + 1] << 24) | (dataarray[i + 2] << 16) | (dataarray[i + 3] << 8) | (dataarray[i + 4])
					i += 4
					continue
				elif dataarray[i] == TYPE_EXT_TEMP1: #Ext temp 1
					parsed['tempext1'] = float((dataarray[i + 1] << 8) | (dataarray[i + 2]))/10
					i += 2
					continue
				elif dataarray[i] == TYPE_EXT_DIGITAL: #Digital input
					parsed['digital'] = dataarray[i + 1]
					i += 1
					continue
				elif dataarray[i] == TYPE_EXT_DISTANCE: #Distance
					parsed['distance'] = (dataarray[i + 1] << 8) | (dataarray[i + 2])
					i += 2
					continue
				elif dataarray[i] == TYPE_ACC_MOTION: #Acc motion
					parsed['accmotion'] = dataarray[i + 1]
					i += 1
					continue
				elif dataarray[i] == TYPE_IR_TEMP: #IR TEMP  TODO
					i += 4
					continue
				elif dataarray[i] == TYPE_OCCUPANCY: #occupancy
					parsed['occupancy'] = dataarray[i + 1]
					i += 1
					continue
				elif dataarray[i] == TYPE_WATERLEAK: #waterleak
					parsed['leak'] = dataarray[i + 1]
					i += 1
					continue
				elif dataarray[i] == TYPE_GRIDEYE: #grideye TODO
					i += 64
					continue
				elif dataarray[i] == TYPE_PRESSURE: #pressure
					parsed['pressure'] = float((dataarray[i + 1] << 24) | (dataarray[i + 2] << 16) | (dataarray[i + 3] << 8) | (dataarray[i + 4]))/1000
					i += 4
					continue
				break
		except Exception as e:
				logging.debug(str(e))
				logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(elsys)