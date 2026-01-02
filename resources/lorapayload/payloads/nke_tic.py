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
import subprocess
import time
import os
import json
import threading
import utils
from binascii import unhexlify

class nke_tic():
	def __init__(self):
		self.name = 'nke_tic'

	def parse(self,data,device):
		logging.debug('Nke Tic')
		parsed={}
		data['parsed'] = parsed
		try:
			dir_path = os.path.dirname(os.path.realpath(__file__))
			programpath = os.path.join(dir_path,'nketic/_tools_/bintotic')
			proc = subprocess.run([programpath], shell=True, capture_output=True, input=data['payload'].encode())
			result = proc.stdout
			lines = result.decode().splitlines()
			count=1
			for x in lines :
				try:
					logging.debug(str(x) + ' line ' + str(count))
					if x.startswith('ADS'):
						logging.debug('ADS found ' + x)
						parsed['ADS']=x.split(' ')[1]
					elif x.startswith('MESURES1'):
						logging.debug('MESURES1 found ' + x)
						parsed['MESURES1']=x.split(' ')[2]
					elif x.startswith('PTCOUR1'):
						logging.debug('PTCOUR1 found ' + x)
						parsed['PTCOUR1']=x.split(' ')[1]
					elif x.startswith('EAP_s'):
						logging.debug('EAP_s found ' + x)
						parsed['EAP_s']=x.split(' ')[1].replace('kWh','')
					elif x.startswith('DATE'):
						logging.debug('DATE found ' + x)
						parsed['DATE']=x.split(' ')[1]+' '+x.split(' ')[2]
				except Exception as e:
					logging.debug(str(e))
					continue
		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		if 'PTCOUR1' in parsed and 'EAP_s' in parsed:
			parsed['EAP_s_'+parsed['PTCOUR1']] = parsed['EAP_s']
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(nke_tic)



