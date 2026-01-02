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

class ewattchsquidprorogowski():
	def __init__(self):
		self.name = 'ewattchsquidprorogowski'

	def parse(self,data,device):
		logging.debug('Ewattch Squid')
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
				binary_string = format(int(hex_string, 16), '024b')

				# Si le bit de poids fort est '1', c'est un nombre négatif en complément à deux
				if binary_string[0] == "1":
					# On inverse les bits et on ajoute 1 pour obtenir la valeur positive en complément à deux
					inverted_binary = ''.join('1' if bit == '0' else '0' for bit in binary_string)
					inverted_binary = format(int(inverted_binary, 2) + 1, '024b')

					# Convertir le binaire modifié en hex
					modified_hex_string = format(int(inverted_binary, 2), '06x')

					# Retourne la valeur négative sous forme hexadécimale inversée
					return "-" + modified_hex_string
				else:
					# Si c'est un nombre positif, on le convertit normalement
					modified_hex_string = format(int(binary_string, 2), '06x')
					return modified_hex_string




			def getTypeMesure(typeMesure):
				mesures = {
					0: ("Index courant", 10),
					1: ("Courant", 1),
					2: ("Index courant + courant", 10),
					3: ("Index énergie active consommée", 10),
					4: ("Puissance active", 1),
					5: ("Index énergie active produite", 10),
					6: ("Index énergie réactive positive", 10),
					7: ("Index énergie réactive négative", 10),
					8: ("Puissance réactive", 1),
					9: ("Index énergie apparente", 10),
					10: ("Tension", 0.1),
					11: ("Puissance apparente", 1),
					12: ("Fréquence", 1)
				}
				return mesures.get(typeMesure, ("Inconnu", 1))

			if payload[0:2] == "00":
				logging.debug('This is a periodic message')
				payloadSize = int(payload[2:4],16) * 2
				blockSize = 38
				numBlocks = payloadSize // blockSize
				newPayload = payload[-payloadSize:]
		
				logging.debug(str(payloadSize) + " octets")
				logging.debug(newPayload)

				i=0
				while i < len(newPayload):
					objectType = newPayload[i:i+2]
					logging.debug(objectType)
					if objectType == "41":
						nbMesure = int(newPayload[i+4:i+5],16)
						typeMesure = int(newPayload[i+5:i+6],16)
						nomMesure, multiple = getTypeMesure(typeMesure)
						logging.debug(f'Nombre de mesures: {nbMesure}')
						logging.debug(f'Type de mesure: {typeMesure}')
						logging.debug(f'Nom de la mesure: {nomMesure}')
						i += 6 
						for j in range(nbMesure):
							if typeMesure == 10 or typeMesure == 12:
								var = 4
							else:
								var = 6
							block = newPayload[i:i+6]
							valeur = int(convertHex(block), 16) * multiple
							parsed[f'channel{j+1}_{typeMesure}'] = valeur

							i += var
					else: # le bloc général
						nbMesure = int(newPayload[i+2:i+3],16)
						typeMesure = int(newPayload[i+3:i+4],16)
						nomMesure, multiple = getTypeMesure(typeMesure)
						logging.debug(f'Nombre de mesures: {nbMesure}')
						logging.debug(f'Type de mesure: {typeMesure}')
						logging.debug(f'Nom de la mesure: {nomMesure}')
						i += 4
						for j in range(nbMesure):
							if typeMesure == 10 or typeMesure == 12:
								var = 4
							else:
								var = 6
							block = newPayload[i:i+var]
							valeur = int(convertHex(block), 16) * multiple
							parsed[f'channel{j+1}_{typeMesure}'] = valeur
							i += var


		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(ewattchsquidprorogowski)