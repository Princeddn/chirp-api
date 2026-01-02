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

class micropelt_mlr003():
	def __init__(self):
		self.name = 'micropelt_mlr003'

	def parse(self,data,device):
		logging.debug('MLR 003 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			payload = data['payload']
			logging.debug('Parsing')
			logging.debug(dataarray) # 21 32 40 63 63 00 81 ff 00 10 21
			parsed['Current_Valve_Position'] = dataarray[0]
			parsed['Flow_Sensor_Raw'] = dataarray[1] * 0.5
			parsed['Flow_Temperature'] = dataarray[2] * 0.5
			parsed['Ambient_Sensor_Raw'] = dataarray[3] * 0.25
			parsed['Ambient_Temperature'] = dataarray[4] * 0.25
			parsed['Energy_Storage'] = dataarray[5] >> 6 & 0x01
			parsed['Harvesting_Active'] = dataarray[5] >> 5 & 0x01
			parsed['Ambient_Sensor_Failure'] = dataarray[5] >> 4 & 0x01
			parsed['Flow_Sensor_Failure'] = dataarray[5] >> 3 & 0x01
			parsed['Radio_Communication_Error'] = dataarray[5] >> 2 & 0x01
			parsed['Received_Signal_Strength'] = dataarray[5] >> 1 & 0x01
			parsed['Motor_Error'] = dataarray[5] >> 0 & 0x01
			parsed['Storage_Voltage'] = round(dataarray[6] * 0.02,2)
			parsed['Average_Current_Consumed'] = dataarray[7] * 10
			parsed['Average_Current_Generated'] = dataarray[8] * 10
			parsed['Reference_Completed'] = dataarray[9] >> 4 & 0x01
			parsed['Operating_Mode'] = dataarray[9] >> 7 & 0x01
			parsed['Storage_Fully_Charged'] = dataarray[9] >> 6 & 0x01
			if len(dataarray) == 11:
				um = dataarray[9] & 0x03
				if um == 0:
					uv = dataarray[10]
				else:
					uv = dataarray[10] * 0.5
			parsed['User_Mode'] = um
			parsed['User_Value'] = uv
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(micropelt_mlr003)
