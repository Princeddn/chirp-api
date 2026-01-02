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

class milesight_UC501():
	def __init__(self):
		self.name = 'milesight_UC501'

	def parse(self,data,device):
		logging.debug('UC501 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			logging.debug(payload)
			x=0
			i=0
			def convert_endian(var):
					little_hex = bytearray.fromhex(var)
					little_hex.reverse()
					hex_string = ''.join(format(x, '02x') for x in little_hex)
					return hex_string
			for i in range(3):
				channel_id = payload[x:x+2]
				channel_type = payload[x+2:x+4]
				logging.debug('CHANNEL ID ' + str(channel_id))
				logging.debug('CHANNEL TYPE ' + str(channel_type))
				if channel_id == '01' and channel_type == '75':
					parsed['battery'] = int(payload[x+4:x+6],16)
					logging.debug('BATTERY ' + str(parsed['battery']))
				if channel_id == '03' and channel_type != 'c8':
					if channel_type == '00':
						parsed['inputO1'] = int(payload[x+4:x+6],16)
					elif channel_type == '01':
						parsed['outputO1'] = int(payload[x+4:x+6],16)
				if channel_id == '04' and channel_type != 'c8':
					if channel_type == '00':
						parsed['inputO2'] = int(payload[x+4:x+6],16)
					elif channel_type == '01':
						parsed['outputO2'] = int(payload[x+4:x+6],16)
				if channel_id == '03' and channel_type == 'c8':
					var = payload[x+4:x+12]
					hex_string = convert_endian(var)
					parsed['counter01'] = int(hex_string, 16)
					logging.debug('counter01 ' + str(parsed['counter01']))
				if channel_id == '04' and channel_type == 'c8':
					var = payload[x+4:x+12]
					hex_string = convert_endian(var)
					parsed['counter02'] = int(hex_string, 16)
					logging.debug('counter02 ' + str(parsed['counter02']))
				if channel_id == '05':
					var = payload[x+4:x+8]
					hex_string = convert_endian(var)
					parsed['ccy01'] = int(hex_string, 16) / 100
					logging.debug('ccy ' + str(parsed['ccy01']))
					var = payload[x+8:x+12]
					hex_string = convert_endian(var)
					parsed['min01'] = int(hex_string, 16) / 100
					logging.debug('min ' + str(parsed['min01']))
					var = payload[x+12:x+16]
					hex_string = convert_endian(var)
					parsed['max01'] = int(hex_string, 16) / 100
					logging.debug('max ' + str(parsed['max01']))
					var = payload[x+16:x+20]
					hex_string = convert_endian(var)
					parsed['avg01'] = int(hex_string, 16) / 100
					logging.debug('avg ' + str(parsed['avg01']))
				if channel_id == '06':
					var = payload[x+4:x+8]
					hex_string = convert_endian(var)
					parsed['ccy02'] = int(hex_string, 16) / 100
					logging.debug('ccy ' + str(parsed['ccy02']))
					var = payload[x+8:x+12]
					hex_string = convert_endian(var)
					parsed['min02'] = int(hex_string, 16) / 100
					logging.debug('min ' + str(parsed['min02']))
					var = payload[x+12:x+16]
					hex_string = convert_endian(var)
					parsed['max02'] = int(hex_string, 16) / 100
					logging.debug('max ' + str(parsed['max02']))
					var = payload[x+16:x+20]
					hex_string = convert_endian(var)
					parsed['avg02'] = int(hex_string, 16) / 100
					logging.debug('avg ' + str(parsed['avg02']))
				######################################################
				if channel_id == 'ff' and channel_type == '0e':
					logging.debug('RS485')
					parsed['modbus_chn_id'] = int(payload[x+4:x+6],16) - 6
					package_type = int(payload[x+6:x+8],16)
					data_type = package_type & 7
					data_length = package_type >> 3
					chn = 'chn' + str(parsed['modbus_chn_id'])
					if data_type == 0:
						parsed['channel_value'] = int(payload[x+8:x+10],16)
					elif data_type == 1:
						parsed['channel_value'] = int(payload[x+8:x+10],16)
					elif data_type == 5: # 3
						bytes = payload[x+8:x+14] # 00 00 00
						logging.debug(bytes)
						logging.debug(bytes[0])
						logging.debug(bytes[1])
						value = (bin(bytes[1]) << 8) + bin(bytes[0])
				else:
					logging.debug('BREAK')
				x=x+6

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(milesight_UC501)
