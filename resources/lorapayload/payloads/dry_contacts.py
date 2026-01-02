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
import datetime

class dry_contacts():
	def __init__(self):
		self.name = 'dry_contacts'

	def parse(self,data,device):
		logging.debug('dry_contacts Received')
		parsed={}
		data['parsed'] = parsed
		try:

			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')

			parsed['frameCode'] = str(hex(dataarray[0])[2:].zfill(2))

			# KEEP ALIVE FRAME 0x30
			if parsed['frameCode'] == '30':
				logging.debug('Keep Alive Frame') # 30
				logging.debug('Frame code : ' + str(parsed['frameCode']))

				# Offset 1
				statusByte = bin(int(str(dataarray[1])))[2:].zfill(8)
				parsed['frameCounter'] = int(statusByte[0:3],2)
				logging.debug('Frame counter : ' + str(parsed['frameCounter']))
				parsed['lowBat'] = statusByte[6]
				logging.debug('Low Bat : ' + str(parsed['lowBat']))

				# Offset 2,3
				binary2 = ''
				for x in range(2,4):
					binary2 = binary2 + str(hex(dataarray[x])[2:].zfill(2))
				parsed['channel1EventCount'] = int(binary2,16)
				logging.debug(str(parsed['channel1EventCount']) + ' events detected on CH1')

				# Offset 4,5
				binary4 = ''
				for x in range(4,6):
					binary4 = binary4 + str(hex(dataarray[x])[2:].zfill(2))
				parsed['channel2EventCount'] = int(binary4,16)
				logging.debug(str(parsed['channel2EventCount']) + ' events detected on CH2')

				# Offset 6,7
				binary6 = ''
				for x in range(6,8):
					binary6 = binary6 + str(hex(dataarray[x])[2:].zfill(2))
				parsed['channel3EventCount'] = int(binary6,16)
				logging.debug(str(parsed['channel3EventCount']) + ' events detected on CH3')

				# Offset 8,9
				binary8 = ''
				for x in range(8,10):
					binary8 = binary8 + str(hex(dataarray[x])[2:].zfill(2))
				parsed['channel4EventCount'] = int(binary8,16)
				logging.debug(str(parsed['channel4EventCount']) + ' events detected on CH4')

				# Offset 10
				binary10 = bin(int(str(dataarray[10])))[2:].zfill(8)
				channel1State = binary10[7]
				channel2State = binary10[6]
				channel3State = binary10[5]
				channel4State = binary10[4]
				parsed['channel1State'] = 'ON' if channel1State == '1' else 'OFF'
				parsed['channel2State'] = 'ON' if channel2State == '1' else 'OFF'
				parsed['channel3State'] = 'ON' if channel3State == '1' else 'OFF'
				parsed['channel4State'] = 'ON' if channel4State == '1' else 'OFF'
				logging.debug('Channel 1 current state : ' + str(parsed['channel1State']))
				logging.debug('Channel 2 current state : ' + str(parsed['channel2State']))
				logging.debug('Channel 3 current state : ' + str(parsed['channel3State']))
				logging.debug('Channel 4 current state : ' + str(parsed['channel4State']))

			# DATA FRAME 0x40
			if parsed['frameCode'] == '40':
				logging.debug('Data Frame') # 40
				logging.debug('Frame code : ' + str(parsed['frameCode']))

				# Offset 1
				statusByte = bin(int(str(dataarray[1])))[2:].zfill(8)
				parsed['frameCounter'] = int(statusByte[0:3],2)
				logging.debug('Frame counter : ' + str(parsed['frameCounter']))
				parsed['lowBat'] = statusByte[6]
				logging.debug('Low Bat : ' + str(parsed['lowBat']))

				# Offset 2,3
				binary2 = ''
				for x in range(2,4):
					binary2 = binary2 + str(hex(dataarray[x])[2:].zfill(2))
				parsed['channel1Value'] = int(binary2,16)
				logging.debug('Channel 1 Value : ' + str(parsed['channel1Value']))

				# Offset 4,5
				binary4 = ''
				for x in range(4,6):
					binary4 = binary4 + str(hex(dataarray[x])[2:].zfill(2))
				parsed['channel2Value'] = int(binary4,16)
				logging.debug('Channel 2 Value : ' + str(parsed['channel2Value']))

				# Offset 6,7
				binary6 = ''
				for x in range(6,8):
					binary6 = binary6 + str(hex(dataarray[x])[2:].zfill(2))
				parsed['channel3Value'] = int(binary6,16)
				logging.debug('Channel 3 Value : ' + str(parsed['channel3Value']))

				# Offset 8,9
				binary8 = ''
				for x in range(8,10):
					binary8 = binary8 + str(hex(dataarray[x])[2:].zfill(2))
				parsed['channel4Value'] = int(binary8,16)
				logging.debug('Channel 4 Value : ' + str(parsed['channel4Value']))

				# Offset 10
				binary10 = bin(int(str(dataarray[10])))[2:].zfill(8)
				channel1CurrentState = binary10[7]
				channel1LastState = binary10[6]
				channel2CurrentState = binary10[5]
				channel2LastState = binary10[4]
				channel3CurrentState = binary10[3]
				channel3LastState = binary10[2]
				channel4CurrentState = binary10[1]
				channel4LastState = binary10[0]
				parsed['channel1CurrentState'] = 'ON' if channel1CurrentState == '1' else 'OFF'
				parsed['channel1LastState'] = 'ON' if channel1LastState == '1' else 'OFF'
				parsed['channel2CurrentState'] = 'ON' if channel2CurrentState == '1' else 'OFF'
				parsed['channel2LastState'] = 'ON' if channel2LastState == '1' else 'OFF'
				parsed['channel3CurrentState'] = 'ON' if channel3CurrentState == '1' else 'OFF'
				parsed['channel3LastState'] = 'ON' if channel3LastState == '1' else 'OFF'
				parsed['channel4CurrentState'] = 'ON' if channel4CurrentState == '1' else 'OFF'
				parsed['channel4LastState'] = 'ON' if channel4LastState == '1' else 'OFF'
				logging.debug('Channel 1 current state : ' + str(parsed['channel1CurrentState']) + ' , last state : ' + str(parsed['channel1LastState']))
				logging.debug('Channel 2 current state : ' + str(parsed['channel2CurrentState']) + ' , last state : ' + str(parsed['channel2LastState']))
				logging.debug('Channel 3 current state : ' + str(parsed['channel3CurrentState']) + ' , last state : ' + str(parsed['channel3LastState']))
				logging.debug('Channel 4 current state : ' + str(parsed['channel4CurrentState']) + ' , last state : ' + str(parsed['channel4LastState']))

			# TIME COUNTING FRAME 0x59
			if parsed['frameCode'] == '59':
				logging.debug('Time Counting Frame') # 59
				logging.debug('Frame code : ' + str(parsed['frameCode']))

				# Offset 1
				statusByte = bin(int(str(dataarray[1])))[2:].zfill(8)
				parsed['frameCounter'] = int(statusByte[0:3],2)
				logging.debug('Frame counter : ' + str(parsed['frameCounter']))
				parsed['lowBat'] = statusByte[6]
				logging.debug('Low Bat : ' + str(parsed['lowBat']))
				parsed['timestampStatus'] = statusByte[5]
				logging.debug('Status Timestamp : ' + str(parsed['timestampStatus']))

				# Offset 2
				binary2 = bin(int(str(dataarray[2])))[2:].zfill(8) # 0000 0101
				channels = []
				for x in range(4,8):
					if binary2[x] == '1':
						if x == 7:
							channels.append('1')
						elif x == 6:
							channels.append('2')
						elif x == 5:
							channels.append('3')
						elif x == 4:
							channels.append('4')
				nbCounters = len(channels)
				parsed['includedChannels'] = " & ".join(channels)
				logging.debug('Channels included in the frame : ' + str(parsed['includedChannels']))

				if nbCounters == 2:
					# Offset 3..6
					binary3 = ''
					for x in range(3,6):
						binary3 = binary3 + str(hex(dataarray[x])[2:].zfill(2)) # 012345
					parsed['firstCounter'] = int(binary3,16)
					logging.debug('First Counter : ' + str(parsed['firstCounter']) + ' s') # 74565

					# Offset 7..10
					binary7 = ''
					for x in range(6,9):
						binary7 = binary7 + str(hex(dataarray[x])[2:].zfill(2)) # 001100
					parsed['secondCounter'] = int(binary7,16)
					logging.debug('Second Counter : ' + str(parsed['secondCounter']) + ' s') # 4352

				# Offset 11..14
				binary11 = ''
				for x in range(9,13):
					binary11 = binary11 + str(hex(dataarray[x])[2:].zfill(2))
				logging.debug(binary11) # 126B94F9

				parsed['timestamp'] = datetime.datetime.utcfromtimestamp(309040377).strftime('%Y-%m-%d %H:%M:%S')
				logging.debug('Timestamp GMT : ' + str(parsed['timestamp']))
				# 1979-10-17 20:32:57 https://www.epochconverter.com/
				# 2022-10-17 20:32:57

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(dry_contacts)
