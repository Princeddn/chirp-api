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

class ewattchsquid():
	def __init__(self):
		self.name = 'ewattchsquid'

	def parse(self,data,device):
		logging.debug('Ewattch Squid')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			logging.debug(dataarray[2])
			if dataarray[2] == 0x48:
				logging.debug('Ewattch Squid')
				if dataarray[0] == 0x00:
					logging.debug('This is a periodic message')
					raw1=str(int(utils.to_hex_string([dataarray[5],dataarray[4],dataarray[3]]),16))
					logging.debug('Channel1 : ' + raw1)
					parsed['channel1'] = float(raw1)/100
					raw2=str(int(utils.to_hex_string([dataarray[8],dataarray[7],dataarray[6]]),16))
					logging.debug('Channel2 : ' + raw2)
					parsed['channel2'] = float(raw2)/100
					raw3=str(int(utils.to_hex_string([dataarray[11],dataarray[10],dataarray[9]]),16))
					logging.debug('Channel3 : ' + raw3)
					parsed['channel3'] = float(raw3)/100
					raw4=str(int(utils.to_hex_string([dataarray[14],dataarray[13],dataarray[12]]),16))
					logging.debug('Channel4 : ' + raw4)
					parsed['channel4'] = float(raw4)/100
					raw5=str(int(utils.to_hex_string([dataarray[17],dataarray[16],dataarray[15]]),16))
					logging.debug('Channel5 : ' + raw5)
					parsed['channel5'] = float(raw5)/100
					raw6=str(int(utils.to_hex_string([dataarray[20],dataarray[19],dataarray[18]]),16))
					logging.debug('Channel6 : ' + raw6)
					parsed['channel6'] = float(raw6)/100
					raw7=str(int(utils.to_hex_string([dataarray[23],dataarray[22],dataarray[21]]),16))
					logging.debug('Channel7 : ' + raw7)
					parsed['channel7'] = float(raw7)/100
					raw8=str(int(utils.to_hex_string([dataarray[26],dataarray[25],dataarray[24]]),16))
					logging.debug('Channel8 : ' + raw8)
					parsed['channel8'] = float(raw8)/100
					raw9=str(int(utils.to_hex_string([dataarray[29],dataarray[28],dataarray[27]]),16))
					logging.debug('Channel9 : ' + raw9)
					parsed['channel9'] = float(raw9)/100
					raw10=str(int(utils.to_hex_string([dataarray[32],dataarray[31],dataarray[30]]),16))
					logging.debug('Channel10 : ' + raw10)
					parsed['channel10'] = float(raw10)/100
					raw11=str(int(utils.to_hex_string([dataarray[35],dataarray[34],dataarray[33]]),16))
					logging.debug('Channel11 : ' + raw11)
					parsed['channel11'] = float(raw11)/100
					raw12=str(int(utils.to_hex_string([dataarray[38],dataarray[37],dataarray[36]]),16))
					logging.debug('Channel12 : ' + raw12)
					parsed['channel12'] = float(raw12)/100
			else:
				logging.debug('Unknown message')
				return data
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(ewattchsquid)