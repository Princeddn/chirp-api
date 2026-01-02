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

class SHE_MIO_LORA_V2():
	def __init__(self):
		self.name = 'SHE_MIO_LORA_V2'

	def parse(self,data,device):
		logging.debug('SHE_MIO_LORA_V2 Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload']
			logging.debug(payload)

			def convertHex(value):
			   little_hex = bytearray.fromhex(value)
			   little_hex.reverse()
			   hex_string = ''.join(format(x, '02x') for x in little_hex)
			   #logging.debug(hex_string)
			   return hex_string

			def checkINBit(value):
			   parsed['entree4'] = 0
			   parsed['entree3'] = 0
			   parsed['entree2'] = 0
			   parsed['entree1'] = 0
			   if (value[0] == '1'):
				   parsed['entree4'] = 1
			   if (value[1] == '1'):
				   parsed['entree3'] = 1
			   if (value[2] == '1'):
				   parsed['entree2'] = 1
			   if (value[3] == '1'):
				   parsed['entree1'] = 1

			def checkOUTBit(value):
			   parsed['sortie4'] = 0
			   parsed['sortie3'] = 0
			   parsed['sortie2'] = 0
			   parsed['sortie1'] = 0
			   if (value[0] == '1'):
				   parsed['sortie4'] = 1
			   if (value[1] == '1'):
				   parsed['sortie3'] = 1
			   if (value[2] == '1'):
				   parsed['sortie2'] = 1
			   if (value[3] == '1'):
				   parsed['sortie1'] = 1

			def parse_single_temperature(hex_value):
				temp = int(hex_value, 16)
				if temp > 127:
					if temp == 253:
						return 97 # sonde de température absente
					elif temp == 254:
						return 98 # déconnexion de l'alimentation (câble rouge). La sonde essaie de fonctionner en parasite power, mais elle n'y arrive pas tout le temps - Erreur en jaune sur l'interface web
					elif temp == 255:
						return 99 # déconnecté après que la carte l'a bien repéré au démarrage (déconnexion du câble jaune, ou noir de la sonde 1-wire) - Erreur en rouge sur l'interface web
					else:
						return temp - 256
				return temp

			parsed['type'] = int(payload[0:2],16)
			if (parsed['type'] == 1):
			   logging.debug('Payload Type 1........')
			   parsed['compteur1'] = int(convertHex(payload[2:10]),16)
			   parsed['compteur2'] = int(convertHex(payload[10:18]),16)
			   parsed['compteur3'] = int(convertHex(payload[18:26]),16)
			   parsed['compteur4'] = int(convertHex(payload[26:34]),16)
			   parsed['compteur5'] = int(convertHex(payload[34:42]),16)
			if (parsed['type'] == 2):
			   logging.debug('Payload Type 2........')
			   parsed['instantanee1'] = int(convertHex(payload[2:6]),16)
			   parsed['instantanee2'] = int(convertHex(payload[6:10]),16)
			   parsed['instantanee3'] = int(convertHex(payload[10:14]),16)
			   parsed['instantanee4'] = int(convertHex(payload[14:18]),16)
			   parsed['instantanee5'] = int(convertHex(payload[18:22]),16)
			   parsed['temperature1'] = int(convertHex(payload[22:24]),16)
			   if (parsed['temperature1'] > 127):
				   if (parsed['temperature1'] == 253):
					   parsed['temperature1'] = 97
				   elif (parsed['temperature1'] == 254):
					   parsed['temperature1'] = 98
				   elif (parsed['temperature1'] == 255):
					   parsed['temperature1'] = 99
				   else:
					   parsed['temperature1'] = parsed['temperature1'] - 256
			   parsed['temperature2'] = int(convertHex(payload[24:26]),16)
			   if (parsed['temperature2'] > 127):
				   if (parsed['temperature2'] == 253):
					   parsed['temperature2'] = 97
				   elif (parsed['temperature2'] == 254):
					   parsed['temperature2'] = 98
				   elif (parsed['temperature2'] == 255):
					   parsed['temperature2'] = 99
				   else:
					   parsed['temperature2'] = parsed['temperature2'] - 256
			   parsed['temperature3'] = int(convertHex(payload[26:28]),16)
			   if (parsed['temperature3'] > 127):
				   if (parsed['temperature3'] == 253):
					   parsed['temperature3'] = 97
				   elif (parsed['temperature3'] == 254):
					   parsed['temperature3'] = 98
				   elif (parsed['temperature3'] == 255):
					   parsed['temperature3'] = 99
				   else:
					   parsed['temperature3'] = parsed['temperature3'] - 256
			   entreeBinaire = bin(int(str(payload[28:30]),16))[2:].zfill(4)
			   if (len(entreeBinaire) == 4):
				   checkINBit(entreeBinaire)
			   sortieBinaire = bin(int(str(payload[30:32]),16))[2:].zfill(4)
			   checkOUTBit(sortieBinaire)
			if (parsed['type'] == 3):
			   logging.debug('Payload Type 3........')
			   parsed['pulse1'] = int(convertHex(payload[2:10]),16)
			   parsed['pulse2'] = int(convertHex(payload[10:18]),16)
			   parsed['pulse3'] = int(convertHex(payload[18:26]),16)
			   parsed['pulse4'] = int(convertHex(payload[26:34]),16)
			if (parsed['type'] == 4):
			   logging.debug('Payload Type 4........')
			   parsed['versionMIO'] = str(int(payload[2:4], 16)) + '.' + str(int(payload[4:6], 16)) + '.' + str(int(payload[6:8], 16)) + '.' + str(int(payload[8:10], 16))
			   parsed['tempsSecurite'] = int(payload[10:12],16)
			   parsed['TempG1'] = int(payload[12:14],16)
			   parsed['TempG2'] = int(payload[14:16],16)
			   parsed['TempG3'] = int(payload[16:18],16)
			   binary0 = bin(int(str(payload[18:20]), 16))[2:].zfill(8)
			   typeEntreeMio = binary0[0:4]
			   if (typeEntreeMio[0] == '0'):
				   parsed['Typeentree4'] = 'Entrée'
			   elif (typeEntreeMio[0] == '1'):
				   parsed['Typeentree4'] = 'Impulsion'
			   if (typeEntreeMio[1] == '0'):
				   parsed['Typeentree3'] = 'Entrée'
			   elif (typeEntreeMio[1] == '1'):
				   parsed['Typeentree3'] = 'Impulsion'
			   if (typeEntreeMio[2] == '0'):
				   parsed['Typeentree2'] = 'Entrée'
			   elif (typeEntreeMio[2] == '1'):
				   parsed['Typeentree2'] = 'Impulsion'
			   if (typeEntreeMio[3] == '0'):
				   parsed['Typeentree1'] = 'Entrée'
			   elif (typeEntreeMio[3] == '1'):
				   parsed['Typeentree1'] = 'Impulsion'

			   spreadFactor = int(binary0[4:8], 2)
			   if spreadFactor == 0:
				   parsed['sf'] = 'auto'
			   elif spreadFactor == 1:
				   parsed['sf'] = 'SF7'
			   elif spreadFactor == 2:
				   parsed['sf'] = 'SF8'
			   elif spreadFactor == 3:
				   parsed['sf'] = 'SF9'
			   elif spreadFactor == 4:
				   parsed['sf'] = 'SF10'
			   elif spreadFactor == 5:
				   parsed['sf'] = 'SF11'
			   elif spreadFactor == 6:
				   parsed['sf'] = 'SF12'

			   binary1 = bin(int(str(payload[20:22]), 16))[2:].zfill(8)
			   typeEntree4 = int(binary1[0:2], 2)
			   typeEntree3 = int(binary1[2:4], 2)
			   typeEntree2 = int(binary1[4:6], 2)
			   typeEntree1 = int(binary1[6:8], 2)
			   if typeEntree4 == 0:
				   parsed['TypeSortie4'] = 'Off'
			   elif typeEntree4 == 1:
				   parsed['TypeSortie4'] = 'On'
			   elif typeEntree4 == 2:
				   parsed['TypeSortie4'] = 'Etat précédent'
			   if typeEntree3 == 0:
				   parsed['TypeSortie3'] = 'Off'
			   elif typeEntree3 == 1:
				   parsed['TypeSortie3'] = 'On'
			   elif typeEntree3 == 2:
				   parsed['TypeSortie3'] = 'Etat précédent'
			   if typeEntree2 == 0:
				   parsed['TypeSortie2'] = 'Off'
			   elif typeEntree2 == 1:
				   parsed['TypeSortie2'] = 'On'
			   elif typeEntree2 == 2:
				   parsed['TypeSortie2'] = 'Etat précédent'
			   if typeEntree1 == 0:
				   parsed['TypeSortie1'] = 'Off'
			   elif typeEntree1 == 1:
				   parsed['TypeSortie1'] = 'On'
			   elif typeEntree1 == 2:
				   parsed['TypeSortie1'] = 'Etat précédent'

			   binary3 = bin(int(str(payload[22:24]), 16))[2:].zfill(8)
			   parsed['etatGroupe5'] = binary3[7:8]
			   etatSecu = binary3[5:7]
			   if etatSecu == '00':
				   parsed['etatSecu'] = 'Ne rien faire'
			   elif etatSecu == '01':
				   parsed['etatSecu'] = 'Fermer les sorties'
			   elif etatSecu == '10':
				   parsed['etatSecu'] = 'Ouvrir les sorties'

			if (parsed['type'] == 5):
			   logging.debug('Payload Type 5........')
			   for i in range(20):
				   hex_value = payload[(i*2)+2:(i*2)+4]
				   parsed[f'temperature{i+1}'] = parse_single_temperature(hex_value)


		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(SHE_MIO_LORA_V2)
