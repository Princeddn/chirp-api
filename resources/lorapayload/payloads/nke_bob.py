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

class nke_bob():
	def __init__(self):
		self.name = 'nke_bob'

	def parse(self,data,device):
		logging.debug('Nke BOB Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			payload = data['payload']
			logging.debug('Parsing')
			
			def calculateFFT(index, vl):
			   varName = 'FFT' + str(index)
			   freqName = 'Freq' + str(index)
			   k = 16 + 2*index
			   l = 18 + 2*index
			   parsed[varName] = int(payload[k:l], 16) * vl / 127
			   parsed[freqName] = str(index*100)+'-'+str((index+1)*100)

			header = int(payload[0:2], 16)
			if header == 108: # Learning
				logging.debug('Learning Header')
				parsed['header'] = 'Learning'
				parsed['learningPercentage'] = int(payload[2:4], 16)
				vl_1 = int(payload[4:6], 16)
				vl_2 = int(payload[6:8], 16)
				vl_3 = int(payload[8:10], 16)
				parsed['vl'] = (vl_1*128 + vl_2 + vl_3/100)/10/121.45
				parsed['freq_index'] = int(payload[10:12], 16) + 1
				parsed['freq_value'] = parsed['freq_index'] * 800 / 256
				parsed['temperature'] = int(payload[12:14], 16) - 30
				parsed['learningScratch'] = int(payload[14:16], 16)
				for k in range(0,32):
					calculateFFT(k, parsed['vl'])
			if header == 114: # Report +++
				logging.debug('Report Header')
				parsed['header'] = 'Report'
				parsed['anomalyLevel'] = int(payload[2:4], 16) * 100 / 127
				parsed['operatingTime'] = int(payload[4:6], 16) * 180 / 127
				parsed['anomalyTime0_10'] = int(payload[6:8], 16) * 180 / 127
				parsed['alarmNumber'] = int(payload[8:10], 16)
				parsed['temperature'] = int(payload[10:12], 16) - 30
				reportPeriod = int(payload[12:14], 16)
				if reportPeriod < 59:
					parsed['reportPeriod'] = reportPeriod
				else:
					parsed['reportPeriod'] = (reportPeriod - 59) * 60
				parsed['reportId'] = int(payload[14:16], 16)
				vl_1 = int(payload[16:18], 16)
				vl_2 = int(payload[18:20], 16)
				vl_3 = int(payload[20:22], 16)
				parsed['vl'] = (vl_1*128 + vl_2 + vl_3/100)/10/121.45
				parsed['freq_index'] = int(payload[22:24], 16) + 1
				parsed['freq_value'] = parsed['freq_index'] * 800 / 256
				parsed['anomalyTime10_20'] = (parsed['operatingTime'] - parsed['anomalyTime0_10']) * int(payload[24:26], 16) / 127
				parsed['anomalyTime20_40'] = (parsed['operatingTime'] - parsed['anomalyTime0_10']) * int(payload[26:28], 16) / 127
				parsed['anomalyTime40_60'] = (parsed['operatingTime'] - parsed['anomalyTime0_10']) * int(payload[28:30], 16) / 127
				parsed['anomalyTime60_80'] = (parsed['operatingTime'] - parsed['anomalyTime0_10']) * int(payload[30:32], 16) / 127
				parsed['anomalyTime80_100'] = (parsed['operatingTime'] - parsed['anomalyTime0_10']) * int(payload[32:34], 16) / 127
				parsed['battery'] = int(payload[34:36], 16) * 100 / 127
				parsed['anomalylevelto20last24h'] = int(payload[36:38], 16)
				if parsed['anomalylevelto20last24h'] == 255:
					parsed['anomalylevelto20last24h'] = 0
				parsed['anomalylevelto50last24h'] = int(payload[38:40], 16)
				if parsed['anomalylevelto50last24h'] == 255:
					parsed['anomalylevelto50last24h'] = 0
				parsed['anomalylevelto80last24h'] = int(payload[40:42], 16)
				if parsed['anomalylevelto80last24h'] == 255:
					parsed['anomalylevelto80last24h'] = 0
				parsed['anomalylevelto20last30d'] = int(payload[42:44], 16)
				if parsed['anomalylevelto20last30d'] == 255:
					parsed['anomalylevelto20last30d'] = 0
				parsed['anomalylevelto50last30d'] = int(payload[44:46], 16)
				if parsed['anomalylevelto50last30d'] == 255:
					parsed['anomalylevelto50last30d'] = 0
				parsed['anomalylevelto80last30d'] = int(payload[46:48], 16)
				if parsed['anomalylevelto80last30d'] == 255:
					parsed['anomalylevelto80last30d'] = 0
				parsed['anomalylevelto20last6mo'] = int(payload[48:50], 16)
				if parsed['anomalylevelto20last6mo'] == 255:
					parsed['anomalylevelto20last6mo'] = 0
				parsed['anomalylevelto50last6mo'] = int(payload[50:52], 16)
				if parsed['anomalylevelto50last6mo'] == 255:
					parsed['anomalylevelto50last6mo'] = 0
				parsed['anomalylevelto80last6mo'] = int(payload[52:54], 16)
				if parsed['anomalylevelto80last6mo'] == 255:
					parsed['anomalylevelto80last6mo'] = 0
			if header == 83: # State
				logging.debug('State Header')
				parsed['header'] = 'State'
				state = int(payload[2:4], 16)
				if state == 100:
					parsed['sensor'] = 1
				if state == 101:
					parsed['sensor'] = 0
				if state == 125:
					parsed['machine'] = 0
				if state == 126:
					parsed['machine'] = 1
				if state == 104:
					logging.debug('>>>>>> Keep alive sent during the vibration testing cycle, there is not enough vibration to start learning')
				if state == 105:
					logging.debug('>>>>>> Vibration testing cycle timeout, device goes to poweroff')
				if state == 106:
					logging.debug('>>>>>> Learning mode keep alive message, sent when the machine goes off for a long time during a learning session')
				if state == 110:
					logging.debug('>>>>>>  Machine stop with flash erase')
				parsed['battery'] = int(payload[4:6], 16) * 100 / 127
			if header == 97: # Alarm
				logging.debug('Alarm Header')
				parsed['header'] = 'Alarm'
				parsed['anomalyLevel'] = int(payload[2:4], 16) * 100 / 127
				parsed['temperature'] = int(payload[4:6], 16) - 30
				vl_1 = int(payload[8:10], 16)
				vl_2 = int(payload[10:12], 16)
				vl_3 = int(payload[12:14], 16)
				parsed['vl'] = (vl_1*128 + vl_2 + vl_3/100)/10/121.45
				parsed['freq_index'] = int(payload[14:16], 16) + 1
				parsed['freq_value'] = parsed['freq_index'] * 800 / 256
				for j in range(0,32):
					calculateFFT(j, parsed['vl'])
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(nke_bob)