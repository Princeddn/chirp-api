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

class PE6v2():
	def __init__(self):
		self.name = 'PE6v2'

	def parse(self,data,device):
		logging.debug('PE6v2 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			frameType = payload[0:2]
			if frameType == '01':
			   parsed['headerType'] = 'Active energy index'
			   parsed['headerUnit'] = 'kWh'
			elif frameType == '02':
			   parsed['headerType'] = 'Reactive energy index'
			   parsed['headerUnit'] = 'kvarh'
			offset = 2
			channelNb = 1

			CHANNEL_MODES = [ '', 'Mono-phase', 'Three-phase with neutral', 'Balanced three-phase with neutral', 'Three-phase without neutral', 'Balanced three-phase without neutral' ]

			def getChannelInfo(offset, channelNb):
				# Channel
			   channel = bin(int(payload[offset:offset+2], 16))[2:].zfill(8)
			   connecteurID = int(channel[0:3],2)
			   voieID = int(channel[3:5],2)
			   modeID = 'Mode-Connecteur' + str(connecteurID)
			   # Mode
			   parsed[modeID] = CHANNEL_MODES[int(channel[5:8],2)]
			   # Connecteur
			   parsed[connecteurID] = int(channel[0:3],2)
			   offset = offset + 2
			   # Index
			   indexID = 'Index' + str(connecteurID) + '.' + str(voieID)
			   little_hex = bytearray.fromhex(payload[offset:offset+8])
			   little_hex.reverse()
			   hex_string = ''.join(format(x, '02x') for x in little_hex)
			   floatVal = struct.unpack('!f', bytes.fromhex(hex_string))[0]
			   parsed[indexID] = round(floatVal,3)
			   offset = offset + 8
			   channelNb = channelNb + 1
			   return offset,channelNb

			result, channelNb = getChannelInfo(offset, channelNb)
			nbConnecteur = int((len(dataarray)-1)/5)
			while(channelNb < nbConnecteur+1):
			   result, channelNb = getChannelInfo(result,channelNb)

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(PE6v2)
