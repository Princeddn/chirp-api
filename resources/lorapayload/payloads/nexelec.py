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
import binascii
#from binascii import unhexlify

class nexelec():
	def __init__(self):
		self.name = 'nexelec'

	def parse(self,data,device):
		logging.debug('Nexelec Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			payload = data['payload']
			logging.debug('Parsing')
			if dataarray[0] == 0xA2:
				logging.debug('This is insafe+ Origin Lora')
				if dataarray[1] == 0x00:
					logging.debug('This is status')
					if dataarray[2] == 0x00:
						parsed['hardware'] = 'C027A'
					else:
						parsed['hardware'] = 'N/A'
					if dataarray[3] == 0x00:
						parsed['software'] = 'S077A'
					else:
						parsed['hardware'] = 'N/A'
					parsed['remainLife'] = int(hex(dataarray[4]),16)
					binary5 = bin(int(str(dataarray[5])))[2:].zfill(8)
					parsed['smoke'] = binary5[0:1]
					parsed['temp'] = binary5[1:2]
					parsed['bat1'] = 2000+ int(hex(dataarray[6]),16)*5
					parsed['bat2'] = 2000+ int(hex(dataarray[7]),16)*5
				elif dataarray[1] == 0x03:
					binary2 = bin(int(str(dataarray[2])))[2:].zfill(8)
					parsed['smoke'] = binary2[0:1]
					parsed['smokehush'] = binary2[1:2]
					parsed['smoketest'] = binary2[2:3]
					parsed['smokemaintenance'] = binary2[3:4]
					parsed['smokehum'] = binary2[4:5]
					parsed['smoketemp'] = binary2[5:6]
					parsed['timesincemaint'] = int(hex(dataarray[3]),16)
				elif dataarray[1] == 0x04:
					binary = str(bin(int(payload, 16))[2:])
					parsed['daily_iaq_global'] = int(binary[16:19],2)
					parsed['daily_iaq_source'] = int(binary[19:23],2)
					parsed['daily_temp_min'] = int(payload[6:8],16) * 0.2
					parsed['daily_temp_max'] = int(payload[8:10],16) * 0.2
					parsed['daily_temp_avg'] = int(payload[10:12],16) * 0.2
					parsed['daily_hum_min'] = int(payload[12:14],16) * 0.5
					parsed['daily_hum_max'] = int(payload[14:16],16) * 0.5
					parsed['daily_hum_avg'] = int(payload[16:18],16) * 0.5
				elif dataarray[1] == 0x05:
					binary = str(bin(int(payload, 16))[2:])
					parsed['iaq_global'] = int(binary[17:20],2)
					parsed['iaq_source'] = int(binary[20:23],2)
					parsed['iaq_dry'] = int(binary[23:26],2)
					parsed['iaq_mould'] = int(binary[26:29],2)
					parsed['iaq_dm'] = int(binary[29:32],2)
					parsed['temperature'] = int(binary[32:41],2) * 0.1
					parsed['humidity'] = int(binary[41:49],2) * 0.5
				elif dataarray[1] == 0x06:
					binary = str(bin(int(payload, 16))[2:])
					nb_mesure = int(payload[4:6],16)
					start = 23+(nb_mesure*9)
					end = 23+(nb_mesure*9)+9
					logging.debug('nb_mesure:'+str(nb_mesure)+' start:'+str(start)+' end:'+str(end)+' value:'+binary[start:end])
					parsed['temperature'] = int(binary[start:end],2) * 0.1
				elif dataarray[1] == 0x07:
					binary = str(bin(int(payload, 16))[2:])
					nb_mesure = int(payload[4:6],16)
					start = 24+(nb_mesure*8)
					end = 24+(nb_mesure*8)+8
					logging.debug('nb_mesure:'+str(nb_mesure)+' start:'+str(start)+' end:'+str(end)+' binary:'+binary[start:end])
					parsed['humidity'] = int(binary[start:end],2) * 0.5
			elif dataarray[0] == 0x72:
				logging.debug('This is insafe+ Carbon Real time data')
				binary = str(bin(int(payload, 16))[2:])
				parsed['CO2level'] = int(hex(dataarray[1]),16) * 20
				parsed['temperature'] = int(hex(dataarray[2]),16) * 0.2
				parsed['humidity'] = int(hex(dataarray[3]),16) * 0.5
				parsed['iaq_global'] = int(binary[32:35],2)
				parsed['iaq_source'] = int(binary[35:39],2)
				parsed['iaq_co2'] = int(binary[39:42],2)
				parsed['iaq_dry'] = int(binary[42:45],2)
				parsed['iaq_mould'] = int(binary[45:48],2)
				parsed['iaq_dm'] = int(binary[48:51],2)
				parsed['hci'] = int(binary[51:53],2)
			elif dataarray[0] == 0x73:
				logging.debug('This is insafe+ Carbon Product Status')
				binary = str(bin(int(payload, 16))[2:])
				parsed['battery_level'] = int(binary[8:10],2)
			elif dataarray[0] == 0x74:
				logging.debug('This is insafe+ Carbon Button Press')
				parsed['button'] = 1	
			elif dataarray[0] == 0x60:
				logging.debug('This is insafe+ Pilot Product Status')
				binary = str(bin(int(payload, 16))[2:])
				parsed['battery_level'] = int(binary[8:10],2)
			elif dataarray[0] == 0x61:
				logging.debug('This is insafe+ Pilot Real time data')
				binary = str(bin(int(payload, 16))[2:])
				parsed['temperature'] = int(hex(dataarray[1]),16) * 0.2
				parsed['humidity'] = int(hex(dataarray[2]),16) * 0.5
				parsed['iaq_global'] = int(binary[24:27],2)
				parsed['iaq_source'] = int(binary[27:31],2)
				parsed['iaq_dry'] = int(binary[31:34],2)
				parsed['iaq_mould'] = int(binary[34:37],2)
				parsed['iaq_dm'] = int(binary[37:40],2)
				parsed['hci'] = int(binary[40:42],2)
			elif dataarray[0] == 0x64:
				logging.debug('This is insafe+ Pilot Button Press')
				parsed['button'] = 1	
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(nexelec)
