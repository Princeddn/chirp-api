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

class ewattchtyness():
	def __init__(self):
		self.name = 'ewattchtyness'

	def parse(self,data,device):
		logging.debug('Ewattch Tyness')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			if dataarray[2] == 0x50:
				logging.debug('Ewattch Tyness energy sensor Tic Mode')
				if dataarray[0] == 0x00:
					logging.debug('This is a periodic message')
					if dataarray[3] == 0x10:
						logging.debug('This is a blue compteur')
						parsed['compteur'] = 'Bleu'
						raw1=str(float(int(utils.to_hex_string([dataarray[9],dataarray[8],dataarray[7],dataarray[6]]),16))/1000)
						logging.debug('Raw 1 is ' + str(raw1))
						parsed['index1'] = float(raw1)
						raw2=str(float(int(utils.to_hex_string([dataarray[13],dataarray[12],dataarray[11],dataarray[10]]),16))/1000)
						logging.debug('Raw 2 is ' + str(raw2))
						parsed['index2'] = float(raw2)
						raw3=str(float(int(utils.to_hex_string([dataarray[17],dataarray[16],dataarray[15],dataarray[14]]),16))/1000)
						logging.debug('Raw 3 is ' + str(raw3))
						parsed['index3'] = float(raw3)
						logging.debug(parsed)
					elif dataarray[3] == 0x30:
						logging.debug('This is a PME-PMI compteur')
						parsed['compteur'] = 'PME-PMI'
						listAbo = {0x00:'TJ MU', 0x01:'TJ LU',0x02:'TJ LUS-SD',0x03:'TJ LU-P',0x04:'TJ LU-PH',0x05:'TJ LU-CH',0x06:'TJ EJP',0x07:'TJ EJP-SD',0x08:'TJ EJP-PM',0x09:'TJ EJP-HH',0x0A:'TV A5 BASE',0x0B:'TV A8 BASE',0x0C:'BT 4 SUP36',0x0D:'BT 5 SUP36',0x0E:'HTA 5',0X0F:'HTA 8'}
						listPer = {0x00:'P',0x01:'PM',0x02:'HH',0x03:'HP',0x04:'HC',0x05:'HPH',0x06:'HCH',0x07:'HPE',0x08:'HCE',0x09:'HPD',0x0A:'HCD',0x0B:'JA'}
						abonnement = dataarray[4]
						periode = dataarray[5]
						if abonnement in listAbo:
							parsed['abo'] = listAbo[abonnement]
						tar =''
						if periode in listPer:
							tar = listPer[periode]
						raw1=str(int(utils.to_hex_string([dataarray[8],dataarray[7],dataarray[6]]),16))
						logging.debug('Raw 1 is ' + str(raw1))
						parsed['index1-'+tar] = float(raw1)
						parsed['index1'] = float(raw1)
						raw2=str(int(utils.to_hex_string([dataarray[11],dataarray[10],dataarray[9]]),16))
						logging.debug('Raw 2 is ' + str(raw2))
						parsed['index2-'+tar] = float(raw2)
						parsed['index2'] = float(raw2)
						raw3=str(int(utils.to_hex_string([dataarray[14],dataarray[13],dataarray[12]]),16))
						logging.debug('Raw 3 is ' + str(raw3))
						parsed['index3-'+tar] = float(raw3)
						parsed['index3'] = float(raw3)
						logging.debug(parsed)
			else:
				logging.debug('Unknown message')
				return data
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(ewattchtyness)
