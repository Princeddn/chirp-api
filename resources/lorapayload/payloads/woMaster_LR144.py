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

class woMaster_LR144():
	def __init__(self):
		self.name = 'woMaster_LR144'



	def parse(self,data,fPort):
		logging.debug('woMaster_LR144 Received')
		parsed={}
		data['parsed'] = parsed
		try:

			def convertHex(value):
			   little_hex = bytearray.fromhex(value)
			   little_hex.reverse()
			   hex_string = ''.join(format(x, '02x') for x in little_hex)
			   #logging.debug(hex_string)
			   return hex_string
			
			def ascii_to_string(ascii_code):
				# Convert the ASCII code (hex format) to bytes, then decode to string
				byte_data = bytes.fromhex(ascii_code)
				return byte_data.decode('utf-8', errors='ignore').strip('\x00')  # 'ignore' skips invalid characters

	
			payload = data['payload']
			logging.debug("Fport is " + fPort)

			if fPort == '4':
				logging.debug('Hearbeat uplink') # 0a095704030285d10000e2
				# 05192200030a0000000000000000000000000000000000000000e2 (fport 4)
				# 0000501400000000e8033000 (fport 223)
				# 00007c1500000000e8032d00

			elif fPort == '223':
				if len(payload) == 24:
					logging.debug('Remote control uplink')
					parsed['currentOutput'] = int(convertHex(payload[0:4]),16)
					parsed['voltageOutput'] = int(convertHex(payload[4:8]),16)/100
					parsed['pwm5Vfrequency'] = int(convertHex(payload[8:12]),16)
					parsed['pwm5VdutyCycle'] = int(convertHex(payload[12:16]),16)
					parsed['pwm10Vfrequency'] = int(convertHex(payload[16:20]),16)
					parsed['pwm10VdutyCycle'] = int(convertHex(payload[20:24]),16)

			if len(payload) == 24:
				logging.debug('Remote control uplink')
				parsed['currentOutput'] = int(convertHex(payload[0:4]),16)
				parsed['voltageOutput'] = int(convertHex(payload[4:8]),16)/100
				parsed['pwm5Vfrequency'] = int(convertHex(payload[8:12]),16)
				parsed['pwm5VdutyCycle'] = int(convertHex(payload[12:16]),16)
				parsed['pwm10Vfrequency'] = int(convertHex(payload[16:20]),16)
				parsed['pwm10VdutyCycle'] = int(convertHex(payload[20:24]),16)

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(woMaster_LR144)
