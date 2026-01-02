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

class adeunis_ARF8230ABA():
	def __init__(self):
		self.name = 'adeunis_ARF8230ABA'

	def parse(self,data,device):
		logging.debug('adeunis_ARF8230ABA Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			logging.debug(payload) # 100001000239012C57003C27107530000A0000000300050103060A0D

			def decode_debounce(binary_value):
				# Ensure the binary value is 8 bits long
				binary_value = binary_value.zfill(8)

				# Split the binary into two groups
				channel_b_bits = binary_value[:4]  # Bits 4 to 7
				channel_a_bits = binary_value[4:]  # Bits 0 to 3

				# Define debounce period mappings
				debounce_periods = {
					0: "deactivated",
					1: "1",
					2: "10",
					3: "20",
					4: "50",
					5: "100",
					6: "200",
					7: "500",
					8: "1000",
					9: "2000",
					10: "5000",
					11: "10000",
				}
				# Convert binary to integer
				channel_a_value = int(channel_a_bits, 2)
				channel_b_value = int(channel_b_bits, 2)
				# Get debounce periods or reserved
				channel_a_debounce = debounce_periods.get(channel_a_value, "reserved")
				channel_b_debounce = debounce_periods.get(channel_b_value, "reserved")
				return channel_a_debounce, channel_b_debounce

			if payload[0:2] == '46':
				logging.debug('Periodic data without historization')
				parsed['status'] = int(payload[2:4],16)
				parsed['meterChannelA'] = int(payload[4:12],16)
				parsed['meterChannelB'] = int(payload[12:20],16)

			if payload[0:2] == '10':
			   frameCounter = payload[2:4]
			   parsed['productMode'] = int(payload[4:6],16)
			   parsed['historizationsPerSavings'] = int(payload[6:10],16)

			   inputConfiguration = bin(int(str(payload[10:12]),16))[2:].zfill(8)
			   parsed['tamperInputChannelB'] = int(inputConfiguration[0],16)
			   meterChannelB = inputConfiguration[2]
			   if meterChannelB == '0':
				   parsed['meterChannelB'] = 'meter different than gas'
			   elif meterChannelB == '1':
				   parsed['meterChannelB'] = 'Gas meter'
			   parsed['activationChannelB'] = int(inputConfiguration[3],16)
			   parsed['tamperInputChannelA'] = int(inputConfiguration[4],16)
			   meterChannelA = inputConfiguration[6]
			   if meterChannelA == '0':
				   parsed['meterChannelA'] = 'meter different than gas'
			   elif meterChannelA == '1':
				   parsed['meterChannelA'] = 'Gas meter'
			   parsed['activationChannelA'] = int(inputConfiguration[7],16)

			   parsed['historizationPeriod'] = int(payload[12:16],16)*2/60

			   debounceDurations = bin(int(str(payload[16:18]),16))[2:].zfill(8)
			   channel_a, channel_b = decode_debounce(debounceDurations)
			   parsed['debounceDurationChannelA'] =  channel_a
			   parsed['debounceDurationChannelB'] =  channel_b

			   parsed['flowCalculationPeriod'] = int(payload[18:22],16)
			   parsed['flowThresholdChannelA'] = int(payload[22:26],16) 
			   parsed['flowThresholdChannelB'] = int(payload[26:30],16)
			   parsed['leakThresholdChannelA'] = int(payload[30:34],16)
			   parsed['leakThresholdChannelB'] = int(payload[34:38],16)
			   parsed['dailyPeriodsUnderTamperThresholdChannelA'] = int(payload[38:42],16)
			   parsed['dailyPeriodsUnderTamperThresholdChannelB'] = int(payload[42:46],16)
			   parsed['samplingPeriodTamper1'] = int(payload[46:48],16)
			   parsed['samplingBeforeTamper1Alarm'] = int(payload[48:50],16)
			   parsed['samplingPeriodTamper2'] = int(payload[50:52],16)
			   parsed['samplingBeforeTamper2Alarm'] = int(payload[52:54],16)
			   parsed['redundantSamplesPerFrame'] = int(payload[54:56],16)
                   
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(adeunis_ARF8230ABA)