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
from binascii import unhexlify

class diehl_HRLcG3():
	def __init__(self):
		self.name = 'diehl_HRLcG3'

	def parse(self,data,device):
		logging.debug('diehl_HRLcG3 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			payload = data['payload']
			logging.debug('Parsing')
			logging.debug(payload)

			# EC 1 Array
			EC1 = [
			0,1,2,3,4,5,6,7,8,9,10,12,14,16,18,20,22,24,26,28,30,35,40,45,50,55,60,65,70,75,80,85,90,
			95,100,105,110,115,120,125,130,135,140,145,150,155,160,165,170,175,180,185,190,195,200,210,
			220,230,240,250,260,270,280,290,300,310,320,330,340,350,360,370,380,390,400,420,440,460,
			480,500,520,540,560,580,600,620,640,660,680,700,720,740,760,780,800,840,880,920,960,1000,
			1040,1080,1120,1160,1200,1240,1280,1320,1360,1400,1440,1480,1520,1560,1600,1680,1760,1840,
			1920,2000,2080,2160,2240,2320,2400,2480,2560,2640,2720,2800,2880,2960,3040,3120,3200,3360,
			3520,3680,3840,4000,4160,4320,4480,4640,4800,4960,5120,5280,5440,5600,5760,5920,6080,6240,
			6400,6720,7040,7360,7680,8000,8320,8640,8960,9280,9600,9920,10240,10560,10880,11200,11520,
			11840,12160,12480,12800,13440,14080,14720,15360,16000,16640,17280,17920,18560,19200,19840,
			20480,21120,21760,22400,23040,23680,24320,24960,25600,26880,28160,29440,30720,32000,33280,
			34560,35840,37120,38400,39680,40960,42240,43520,44800,46080,47360,48640,49920,51200,53760,
			56320,58880,61440,64000,66560,69120,71680,74240,76800,79360,81920,84480,87040,89600,92160,
			94720,97280,99840,102400,107520,112640,117760,122880,128000,133120,138240,143360,148480,
			153600,158720,163840,168960,174080,179200,184320,189440,194560,199680,'Overflow','Anomaly'
			]

			binary0 = bin(int(payload[0:2], 16))[2:].zfill(8) # 1000 1010
			binary1 = bin(int(payload[2:4], 16))[2:].zfill(8) # 0100 1011

			# TRAME 1 ----- DS51_A #
			if binary0[6:8] == '10':
				logging.debug('Trame 1 DS51_A')
				# OFFSET 0 #
				parsed['sequenceNumber'] = int(binary0[0:4], 2)
				parsed['type'] = binary0[4:6]
				parsed['frameType'] = 'DS51_A'

				# OFFSET 2
				binary2 = bin(int(str(dataarray[2])))[2:].zfill(8)
				binary2 = bin(int(payload[4:6], 16))[2:].zfill(8) # 0000 0011
				logging.debug(binary2)
				parsed['inProgressAlarm'] = binary2[7:8]
				parsed['metrology'] = binary2[6:7]
				parsed['system'] = binary2[5:6]
				parsed['tamper'] = binary2[4:5]
				parsed['waterQuality'] = binary2[3:4]
				parsed['flowPersistence'] = binary2[1:3]
				parsed['stopLeaks'] = binary2[0:1]
				if parsed['flowPersistence'] == '00':
					logging.debug('Nothing to report') # flag
				elif parsed['flowPersistence'] == '01':
					logging.debug('Past Persistence during the period')
				elif parsed['flowPersistence'] == '10':
					logging.debug('In progress persistence')
				elif parsed['flowPersistence'] == '10':
					logging.debug('In progress impacting persistence')

				# OFFSET 3
				binary3 = ''
				i = 0
				for x in range(3, 8):
					binary3 = binary3 + str(hex(dataarray[x])[2:].zfill(2))
				little_hex = bytearray.fromhex(binary3)
				little_hex.reverse()
				hex_string = ''.join(format(x, '02x') for x in little_hex)
				hex_value = hex(int(hex_string, 16))
				binary3 = bin(int(hex_value, 16))[2:].zfill(8)
				binary3 = binary3[::-1]
				parsed['blockedMeter'] = 0
				parsed['overflowSmallSize'] = 0
				parsed['overflowLargeSize'] = 0
				parsed['battery'] = 0
				parsed['clockUpdated'] = 0
				parsed['moduleConfigured'] = 0
				parsed['noiseDefense'] = 0
				parsed['lowTemperature'] = 0
				parsed['alarmCycleLimit'] = 0
				parsed['reversedMeter'] = 0
				parsed['moduleTampered'] = 0
				parsed['acquisitionStageFailure'] = 0
				parsed['backflow'] = 0
				for number in binary3:
					if number == '1':
						if i == 0:
							parsed['blockedMeter'] = 1
							logging.debug('Blocked meter alarm flag is raised')
						elif i == 6:
							parsed['overflowSmallSize'] = 1
							logging.debug('Overflow alarm flag is raised - small size') # flag
						elif i == 7:
							parsed['overflowLargeSize'] = 1
							logging.debug('Overflow alarm flag is raised – large size')
						elif i == 15:
							parsed['battery'] = 1
							logging.debug('Battery alarm flag is raised')
						elif i == 16:
							parsed['clockUpdated'] = 1
							logging.debug('Clock updated alarm flag is raised')
						elif i == 19:
							parsed['moduleConfigured'] = 1
							logging.debug('Module reconfigured alarm flag is raised')
						elif i == 22:
							parsed['noiseDefense'] = 1
							logging.debug('Noise defense - radio reception suspended alarm flag is raised')
						elif i == 24:
							parsed['lowTemperature'] = 1
							logging.debug('Low temperature - radio suspension alarm flag is raised')
						elif i == 25:
							parsed['alarmCycleLimit'] = 1
							logging.debug('Number of alarm cycle authorized reached alarm flag is raised')
						elif i == 27:
							parsed['reversedMeter'] = 1
							logging.debug('Reversed meter alarm flag is raised')
						elif i == 29:
							parsed['moduleTampered'] = 1
							logging.debug('Module tampered alarm flag is raised')
						elif i == 30:
							parsed['acquisitionStageFailure'] = 1
							logging.debug('Acquisition stage failure alarm flag is raised')
						elif i == 32:
							parsed['backflow'] = 1
							logging.debug('Backflow alarm flag is raised') # flag
					i=i+1

				# OFFSET 8
				binary8 = ''
				for x in range(8, 12):
					binary8 = binary8 + str(hex(dataarray[x])[2:].zfill(2))
				little_hex = bytearray.fromhex(binary8)
				little_hex.reverse()
				hex_string = ''.join(format(x, '02x') for x in little_hex)
				binary8 = int(hex_string, 16)
				parsed['midnightIndexPulses'] = binary8
				logging.debug('Midnight index = ' + str(parsed['midnightIndexPulses']) + ' pulses')

				# OFFSET 12
				binary12 = ''
				for x in range(12, 14):
					binary12 = binary12 + str(hex(dataarray[x])[2:].zfill(2))
				little_hex = bytearray.fromhex(binary12)
				little_hex.reverse()
				hex_string_1 = ''.join(format(x, '02x') for x in little_hex)
				hex_value_1 = hex(int(hex_string_1, 16)) # x -> 0x47

				# OFFSET 14
				binary14 = bin(int(str(dataarray[14])))[2:].zfill(8)

				binary_value_2 = binary14[4:8]
				hex_value_2 = hex(int(binary_value_2, 2)) # y -> 0x0
				x, y = int(hex_value_1, 16), int(hex_value_2, 16)
				DS51_VIPP_24 = int(hex(y + x),16) # DS51_VIPP_24 = value_2 & value_1 = 0x00047 = 71 pulses
				parsed['DS51_VIPP_24'] = DS51_VIPP_24
				logging.debug('Cumulative Positive Index in the Last 24 hours, DS51_VIPP_24 = ' + str(parsed['DS51_VIPP_24']))

				parsed['DS51_VIPN_24'] = binary14[0:4]
				binary_value_3 = binary14[0:4]
				hex_value_2 = hex(int(binary_value_3, 2)) # a -> 0x0

				# OFFSET 15
				binary15 = ''
				for x in range(15, 17):
					binary15 = binary15 + str(hex(dataarray[x])[2:].zfill(2))
				little_hex = bytearray.fromhex(binary15)
				little_hex.reverse()
				hex_string_4 = ''.join(format(x, '02x') for x in little_hex)
				hex_value_4 = hex(int(hex_string_4, 16)) # b -> 0x11

				a, b = int(hex_value_2, 16), int(hex_value_4, 16)
				DS51_VIPN_24 = int(hex(a + b),16) # DS51_VIPN_24 = value_2 & value_1 = 0x00011 = 17 pulses
				parsed['DS51_VIPN_24'] = DS51_VIPN_24
				logging.debug('Cumulative Negative Index in the Last 24 hours, DS51_VIPN_24 = ' + str(parsed['DS51_VIPN_24']))

				# EC 2 Array
				EC2 = [
				0,0.0025,0.0051,0.005304,0.00551616,0.005736807,0.005966279,0.00620493,0.006453127,0.006711252,
				0.006979702,0.00725889,0.007549246,0.007851216,0.008165265,0.008491875,0.00883155,0.009184812,
				0.009552204,0.009934293,0.010331665,0.010744931,0.011174728,0.011621717,0.012086586,0.01257005,
				0.013072852,0.013595766,0.014139596,0.01470518,0.015293387,0.015905123,0.016541328,0.017202981,
				0.0178911,0.018606744,0.019351014,0.020125054,0.020930056,0.021767258,0.022637949,0.023543467,
				0.024485205,0.025464614,0.026483198,0.027542526,0.028644227,0.029789996,0.030981596,0.03222086,
				0.033509694,0.034850082,0.036244085,0.037693849,0.039201603,0.040769667,0.042400454,0.044096472,
				0.04586033,0.047694743,0.049602533,0.051586635,0.0536501,0.055796104,0.058027948,0.060349066,
				0.062763029,0.06527355,0.067884492,0.070599871,0.073423866,0.076360821,0.079415254,0.082591864,
				0.085895539,0.08933136,0.092904614,0.096620799,0.100485631,0.104505056,0.108685259,0.113032669,
				0.117553975,0.122256134,0.12714638,0.132232235,0.137521525,0.143022386,0.148743281,0.154693012,
				0.160880732,0.167315962,0.1740086,0.180968944,0.188207702,0.19573601,0.203565451,0.211708069,
				0.220176391,0.228983447,0.238142785,0.247668496,0.257575236,0.267878246,0.278593375,0.28973711,
				0.301326595,0.313379658,0.325914845,0.338951439,0.352509496,0.366609876,0.381274271,0.396525242,
				0.412386251,0.428881701,0.446036969,0.463878448,0.482433586,0.50173093,0.521800167,0.542672173,
				0.56437906,0.586954223,0.610432392,0.634849687,0.660243675,0.686653422,0.714119559,0.742684341,
				0.772391715,0.803287383,0.835418879,0.868835634,0.903589059,0.939732621,0.977321926,1.016414803,
				1.057071395,1.099354251,1.143328421,1.189061558,1.23662402,1.286088981,1.33753254,1.391033842,
				1.446675196,1.504542204,1.564723892,1.627312847,1.692405361,1.760101576,1.830505639,1.903725864,
				1.979874899,2.059069895,2.14143269,2.227089998,2.316173598,2.408820542,2.505173363,2.605380298,
				2.70959551,2.81797933,2.930698504,3.047926444,3.169843501,3.296637241,3.428502731,3.56564284,
				3.708268554,3.856599296,4.010863268,4.171297798,4.33814971,4.511675699,4.692142727,4.879828436,
				5.075021573,5.278022436,5.489143334,5.708709067,5.937057429,6.174539727,6.421521316,6.678382168,
				6.945517455,7.223338153,7.512271679,7.812762547,8.125273048,8.45028397,8.788295329,9.139827142,
				9.505420228,9.885637038,10.28106252,10.69230502,11.11999722,11.56479711,12.027389,12.50848456,
				13.00882394,13.52917689,14.07034397,14.63315773,15.21848404,15.8272234,16.46031233,17.11872483,
				17.80347382,18.51561277,19.25623728,20.02648678,20.82754625,2,1.66064809,22.52707402,23.42815698,
				24.36528326,25.33989459,26.35349038,27.40762999,28.50393519,29.6440926,30.8298563,32.06305055,
				33.34557258,34.67939548,36.0665713,37.50923415,39.00960351,40.56998766,42.19278716,43.88049865,
				45.63571859,47.46114734,49.19587904,100,-0.25,-0.75,-1.5,-2.5,-3.5,-4.5,-5.5,-7.5,-10.5,-13.5,
				-17.5,-22.5,-27.5,-32.5,-37.5,-42.5,-47.5,-100];

				# OFFSET 17 NOT DONE YET
				binary17 = ''
				k=24
				for x in range(17, 41): # 24 fois
					binary17 = binary17 + str(hex(dataarray[x])[2:].zfill(2))
					#logging.debug('Offset : ' + str(x))
					#logging.debug('Hours : Timestamp Frame - ' + str(k) + 'h')
					#logging.debug('Hex Value : ' + str(hex(dataarray[x]).zfill(2)))
					#logging.debug('Dec Value : ' + str(int(hex(dataarray[x])[2:].zfill(2),16)))
					parsed['ConsumptionPercentage'] = EC2[dataarray[x]]
					logging.debug('EC2 Conversion - % Consumption : ' + str(EC2[dataarray[x]]))
					k=k-1

				# OFFSET 41
				parsed['minimumFlowRate'] = EC1[dataarray[41]]
				logging.debug('Minimum Flow Rate = ' + str(parsed['minimumFlowRate']) + ' pulses/h') # 300

				# OFFSET 42
				parsed['maximumFlowRate'] = EC1[dataarray[42]]
				logging.debug('Maximum Flow Rate = ' + str(EC1[dataarray[42]]) + ' pulses/h') # 2080

				# OFFSET 43
				binary43 = int(hex(dataarray[43])[2:].zfill(2),16)
				parsed['backflowAlternation'] = EC1[dataarray[43]]
				logging.debug('Backflow Alternation = ' + str(EC1[dataarray[43]])) # 4

				# OFFSET 44
				parsed['backflowCumulatedVolume'] = EC1[dataarray[44]]
				logging.debug('Backflow Cumulated Volume = ' + str(EC1[dataarray[44]]) + ' pulses') # 14

				# OFFSET 45
				binary45 = dataarray[45] & 0x0F
				parsed['Flow_DurationOfPersistenceFlowEqualToZero'] = binary45
				logging.debug('Flow Duration Of Persistence Flow Equal To Zero = ' + str(binary45))

				# OFFSET 46
				binary46 = dataarray[46] >> 4
				parsed['Flow_DurationOfPersistenceFlowOverZero'] = binary46
				logging.debug('Flow Duration Of Persistence Flow Over Zero = ' + str(binary46))

				# OFFSET 49
				binary49 = ''
				for x in range(49, 51):
					binary49 = binary49 + str(hex(dataarray[x])[2:].zfill(2))
				little_hex = bytearray.fromhex(binary49)
				little_hex.reverse()
				hex_string = ''.join(format(x, '02x') for x in little_hex)
				hex_value = hex(int(hex_string, 16))
				binary49 = bin(int(hex_value, 16))[2:].zfill(8)
				value_1 = int(binary49[0:5], 2)
				parsed['hours'] = value_1
				value_2 = int(binary49[5:12], 2)
				parsed['minutes'] = int(value_2/2)
				parsed['timestamp'] = str(parsed['hours']) + ':' + str(parsed['minutes']) # 22:38
				parsed['meterKey'] = int(binary49[12:16], 2) # 3
				logging.debug('Timestamp = ' + str(parsed['timestamp']))
				logging.debug('Meterkey = ' + str(parsed['meterKey']))

			# TRAME 3 ----- DS51_OE #
			if binary0[6:8] == '00':
				logging.debug('Trame 3 DS51_OE')
				# OFFSET 0
				parsed['sequenceNumber'] = int(binary0[0:4], 2)
				parsed['type'] = binary0[4:6]
				parsed['frameType'] = 'DS51_OE'
				logging.debug('Sequence number = ' + str(parsed['sequenceNumber'])) # 3
				logging.debug('Frame Type = ' + str(parsed['type'])) # 00
				logging.debug(str(parsed['frameType'])) # DS51_OE

				# OFFSET 2
				binary2 = bin(int(str(dataarray[2])))[2:].zfill(8) # 0000 1000
				parsed['nothing'] = binary2[7:8]
				parsed['reserved'] = binary2[6:7]
				parsed['AlarmsCauses_Tamper'] = binary2[5:6]
				parsed['AlarmsCauses_Backflow'] = binary2[4:5]
				parsed['AlarmsCauses_FlowPersistenceInProgess'] = binary2[3:4]
				parsed['AlarmsCauses_StopPersistenceInProgess'] = binary2[2:3]
				logging.debug('AlarmsCauses_Tamper : ' + parsed['AlarmsCauses_Tamper'])
				logging.debug('AlarmsCauses_Backflow : ' + parsed['AlarmsCauses_Backflow'])
				logging.debug('AlarmsCauses_FlowPersistenceInProgess : ' + parsed['AlarmsCauses_FlowPersistenceInProgess'])
				logging.debug('AlarmsCauses_StopPersistenceInProgess : ' + parsed['AlarmsCauses_StopPersistenceInProgess'])


				# OFFSET 3
				binary3 = ''
				i = 0
				for x in range(3, 8):
					binary3 = binary3 + str(hex(dataarray[x])[2:].zfill(2))
				little_hex = bytearray.fromhex(binary3)
				little_hex.reverse()
				hex_string = ''.join(format(x, '02x') for x in little_hex)
				hex_value = hex(int(hex_string, 16))
				binary3 = bin(int(hex_value, 16))[2:]
				binary3 = binary3[::-1]
				parsed['blockedMeter'] = 0
				parsed['overflowSmallSize'] = 0
				parsed['overflowLargeSize'] = 0
				parsed['battery'] = 0
				parsed['clockUpdated'] = 0
				parsed['moduleConfigured'] = 0
				parsed['noiseDefense'] = 0
				parsed['lowTemperature'] = 0
				parsed['alarmCycleLimit'] = 0
				parsed['reversedMeter'] = 0
				parsed['moduleTampered'] = 0
				parsed['acquisitionStageFailure'] = 0
				parsed['backflow'] = 0
				for number in binary3:
					if number == '1':
						if i == 0:
							parsed['blockedMeter'] = 1
							logging.debug('Blocked meter alarm flag is raised') # flag
						elif i == 6:
							parsed['overflowSmallSize'] = 1
							logging.debug('Overflow alarm flag is raised - small size') # flag
						elif i == 7:
							parsed['overflowLargeSize'] = 1
							logging.debug('Overflow alarm flag is raised – large size')
						elif i == 15:
							parsed['battery'] = 1
							logging.debug('Battery alarm flag is raised')
						elif i == 16:
							parsed['clockUpdated'] = 1
							logging.debug('Clock updated alarm flag is raised')
						elif i == 19:
							parsed['moduleConfigured'] = 1
							logging.debug('Module reconfigured alarm flag is raised') # flag
						elif i == 22:
							parsed['noiseDefense'] = 1
							logging.debug('Noise defense - radio reception suspended alarm flag is raised')
						elif i == 24:
							parsed['lowTemperature'] = 1
							logging.debug('Low temperature - radio suspension alarm flag is raised')
						elif i == 25:
							parsed['alarmCycleLimit'] = 1
							logging.debug('Number of alarm cycle authorized reached alarm flag is raised')
						elif i == 27:
							parsed['reversedMeter'] = 1
							logging.debug('Reversed meter alarm flag is raised')
						elif i == 29:
							parsed['moduleTampered'] = 1
							logging.debug('Module tampered alarm flag is raised')
						elif i == 30:
							parsed['acquisitionStageFailure'] = 1
							logging.debug('Acquisition stage failure alarm flag is raised')
						elif i == 32:
							parsed['backflow'] = 1
							logging.debug('Backflow alarm flag is raised') # flag
					i=i+1

				# OFFSET 8
				parsed['DS51_QMIN'] = EC1[dataarray[8]]
				logging.debug('NonZeroMinFlow = ' + str(parsed['DS51_QMIN']) + ' pulses/h') # 500

				# OFFSET 10
				parsed['DS51_QMAX'] = EC1[dataarray[10]]
				logging.debug('MaxFlow = ' + str(parsed['DS51_QMAX']) + ' pulses/h') # 8640

				# OFFSET 12
				parsed['DS51_RNA'] = EC1[dataarray[12]]
				logging.debug('Backflow_NumberOfAlternation = ' + str(parsed['DS51_RNA'])) # 2

				# OFFSET 13
				parsed['DS51_RVC'] = EC1[dataarray[13]]
				logging.debug('Backflow_CumulatedVolume = ' + str(parsed['DS51_RVC'])) # 30

				# OFFSET 19
				binary19 = bin(int(str(dataarray[19])))[2:].zfill(8) # 01110100
				parsed['Flow_DurationOfPersistenceFlowEqualToZero'] = int(binary19[4:8], 2)
				logging.debug('Flow_DurationOfPersistenceFlowEqualToZero = ' + str(parsed['Flow_DurationOfPersistenceFlowEqualToZero'])) # 4

				# OFFSET 20
				binary20 = bin(int(str(dataarray[20])))[2:].zfill(8) # 00010001
				parsed['Flow_DurationOfPersistenceFlowOverZero'] = int(binary20[0:4], 2)
				logging.debug('Flow_DurationOfPersistenceFlowOverZero = ' + str(parsed['Flow_DurationOfPersistenceFlowOverZero'])) # 1

				# OFFSET 31
				binary31 = bin(int(str(dataarray[31])))[2:].zfill(8) # 00010011
				parsed['DS51_OE_FrameRepetitionNumber'] = int(binary31[6:8], 2)
				logging.debug('DS51_OE_FrameRepetitionNumber = ' + str(parsed['DS51_OE_FrameRepetitionNumber'])) # 3

				# OFFSET 32
				binary32 = ''
				for x in range(32, 36):
					binary32 = binary32 + str(hex(dataarray[x])[2:].zfill(2))
				little_hex = bytearray.fromhex(binary32)
				little_hex.reverse()
				hex_string = ''.join(format(x, '02x') for x in little_hex)
				parsed['DS51_DAT'] = int(hex_string, 16)
				logging.debug('NumberOfSecondsSince01January2012AtMidnight = ' + str(parsed['DS51_DAT'])) # 236720342

				# OFFSET 38
				parsed['DS51_RFHRS'] = '5322' + '.' + str(hex(dataarray[38])[2:].zfill(2)) + '.' + str(hex(dataarray[39])[2:].zfill(2)) + '.' + str(hex(dataarray[40])[2:].zfill(2)) + '.' + str(hex(dataarray[41])[2:].zfill(2)) + '.' + str(hex(dataarray[42])[2:].zfill(2)) + '.' + str(hex(dataarray[43])[2:].zfill(2))
				logging.debug('LoRaWanStatistics_RadioSerialNumber = ' + str(parsed['DS51_RFHRS'])) # 5322.87.81.18.39.83.FB

				# OFFSET 44
				binary44 = bin(int(str(dataarray[44])))[2:].zfill(8)
				parsed['DS51_KEY'] = int(binary44[4:8], 2)
				logging.debug('MeterKey = ' + str(parsed['DS51_KEY'])) # 3

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(diehl_HRLcG3)
