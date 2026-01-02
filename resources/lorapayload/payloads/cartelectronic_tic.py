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

class cartelectronic_tic():
	def __init__(self):
		self.name = 'cartelectronic_tic'

	def parse(self,data,device):
		logging.debug('cartelectronic_tic Received')
		parsed={}
		data['parsed'] = parsed
		try:
			dataarray = utils.hexarray_from_string(data['payload'])
			logging.debug('Parsing')
			payload = data['payload'] # 01 02 001118c1 0008

			def calculPeriodeTarifairePMI(value):
				if value == 0:
					parsed['periode_tarifaire'] = "Heures de pointe"
					parsed['index_P'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
				elif value == 1:
					parsed['periode_tarifaire'] = "Heures pleines hiver"
					parsed['index_HPH'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
				elif value == 2:
					parsed['periode_tarifaire'] = "Heures creuses hiver"
					parsed['index_HCH'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
				elif value == 3:
					parsed['periode_tarifaire'] = "Heures pleines demi-saison"
					parsed['index_HPD'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
				elif value == 4:
					parsed['periode_tarifaire'] = "Heures creuses demi-saison"
					parsed['index_HCD'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
				elif value == 5:
					parsed['periode_tarifaire'] = "Heures pleines été"
					parsed['index_HPE'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
				elif value == 6:
					parsed['periode_tarifaire'] = "Heures creuses été"
					parsed['index_HCE'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
				elif value == 7:
					parsed['periode_tarifaire'] = "Heures juillet août"
					parsed['index_JA'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
				elif value == 8:
					parsed['periode_tarifaire'] = "Heures hiver"
					parsed['index_HH'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
				elif value == 9:
					parsed['periode_tarifaire'] = "Heures demi-saison"
					parsed['index_HD'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
				elif value == 10:
					parsed['periode_tarifaire'] = "Heures pointe mobile"
					parsed['index_PM'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
				elif value == 11:
					parsed['periode_tarifaire'] = "Heures hiver mobile"
					parsed['index_HM'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
				elif value == 12:
					parsed['periode_tarifaire'] = "Heures demi-saison mobile"
					parsed['index_DSM'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
				elif value == 13:
					parsed['periode_tarifaire'] = "Heures saison creuse mobile"
					parsed['index_SCM'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]

			if payload[0:2] == "01":
				contrat = int(payload[2:4], 16)
				binaryState = bin(int(payload[12:16],16))[2:].zfill(16) # 000000000 0001 0 0 0
				periode_tarifaire = int(binaryState[9:13],2)
				couleur_aujourdhui = int(binaryState[5:7],2)
				couleur_demain = int(binaryState[3:5],2)
				parsed['periode_tarifaire'] = 'N/A'
				parsed['couleur_aujourdhui'] = 'N/A'
				parsed['couleur_demain'] = 'N/A'
				if contrat == 0:
					parsed['contrat'] = "Pas défini"
				elif contrat == 1:
					parsed['contrat'] = "Base"
					parsed['periode_tarifaire'] = "Toutes heures"
					parsed['index_base'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
				elif contrat == 2:
					parsed['contrat'] = "Heures creuses/pleines"
					if periode_tarifaire == 1:
						parsed['periode_tarifaire'] = "Heures creuses"
						parsed['index_HC'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
					elif periode_tarifaire == 2:
						parsed['periode_tarifaire'] = "Heures pleines"
						parsed['index_HP'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
				elif contrat == 3:
					parsed['contrat'] = "EJP"
					if periode_tarifaire == 1:
						parsed['periode_tarifaire'] = "Heures normales"
						parsed['index_HN'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
					elif periode_tarifaire == 2:
						parsed['periode_tarifaire'] = "Heures pointes mobiles"
						parsed['index_HPB'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
				elif contrat == 4:
					parsed['contrat'] = "TEMPO"
					if periode_tarifaire == 1:
						parsed['periode_tarifaire'] = "Heures creuses bleues"
						parsed['index_HCBleu'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
					elif periode_tarifaire == 2:
						parsed['periode_tarifaire'] = "Heures creuses blanches"
						parsed['index_HCBlanche'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
					elif periode_tarifaire == 3:
						parsed['periode_tarifaire'] = "Heures creuses rouges"
						parsed['index_HCR'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
					elif periode_tarifaire == 4:
						parsed['periode_tarifaire'] = "Heures pleines bleues"
						parsed['index_HPBleu'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
					elif periode_tarifaire == 5:
						parsed['periode_tarifaire'] = "Heures pleines blanches"
						parsed['index_HPBlanche'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
					elif periode_tarifaire == 6:
						parsed['periode_tarifaire'] = "Heures pleines rouges"
						parsed['index_HPR'] = struct.unpack(">i", bytes.fromhex(payload[4:12]))[0]
					
					if couleur_aujourdhui == 0:
						parsed['couleur_aujourdhui'] = "Pas de couleur définie"
					elif couleur_aujourdhui == 1:
						parsed['couleur_aujourdhui'] = "Bleu"
					elif couleur_aujourdhui == 2:
						parsed['couleur_aujourdhui'] = "Blanc"
					elif couleur_aujourdhui == 3:
						parsed['couleur_aujourdhui'] = "Rouge"

					if couleur_demain == 0:
						parsed['couleur_demain'] = "Pas de couleur définie"
					elif couleur_demain == 1:
						parsed['couleur_demain'] = "Bleu"
					elif couleur_demain == 2:
						parsed['couleur_demain'] = "Blanc"
					elif couleur_demain == 3:
						parsed['couleur_demain'] = "Rouge"
				elif contrat == 5:
					parsed['contrat'] = "Production"
				elif contrat == 6:
					parsed['contrat'] = "Contrat Zen (Enedis)"
				elif contrat == 7:
					parsed['contrat'] = "Contrat Zen+ (Enedis)"
				elif contrat == 8:
					parsed['contrat'] = "Contrat Super Creuse"
				elif contrat == 9:
					parsed['contrat'] = "Contrat Week-end"
				elif contrat == 10:
					parsed['contrat'] = "Contrat Beaux jours"
				elif contrat == 11:
					parsed['contrat'] = "Contrat saison haute / saison basse"
				elif contrat == 12:
					parsed['contrat'] = "Contrat heures pleines/heures creuses 1 jour semaine et week-end"
				elif contrat == 13:
					parsed['contrat'] = "PMEPMI - Jaune base MU"
					calculPeriodeTarifairePMI(periode_tarifaire)
				elif contrat == 14:
					parsed['contrat'] = "PMEPMI - Jaune base LU"
					calculPeriodeTarifairePMI(periode_tarifaire)
				elif contrat == 15:
					parsed['contrat'] = "PMEPMI - Jaune EJP"
					calculPeriodeTarifairePMI(periode_tarifaire)
				elif contrat == 16:
					parsed['contrat'] = "PMEPMI - BT 4 SUP 36"
					calculPeriodeTarifairePMI(periode_tarifaire)
				elif contrat == 17:
					parsed['contrat'] = "PMEPMI - BT 5 SUP 36"
					calculPeriodeTarifairePMI(periode_tarifaire)
				elif contrat == 18:
					parsed['contrat'] = "PMEPMI - TV 5"
					calculPeriodeTarifairePMI(periode_tarifaire)
				elif contrat == 19:
					parsed['contrat'] = "PMEPMI - TV 8"
					calculPeriodeTarifairePMI(periode_tarifaire)
				elif contrat == 20:
					parsed['contrat'] = "PMEPMI - HTA 5"
					calculPeriodeTarifairePMI(periode_tarifaire)
				elif contrat == 21:
					parsed['contrat'] = "PMEPMI - HTA 8"
					calculPeriodeTarifairePMI(periode_tarifaire)
				else:
					logging.debug('Erreur de récupération du contrat')

				parsed['alimentation_exterieure'] = binaryState[15:16]
				parsed['erreur_lecture'] = binaryState[14:15]
				parsed['tele_info'] = 0 if binaryState[13:14] == '1' else 1 
				parsed['mode'] = 'Linky' if binaryState[8:9] == '1' else 'Historique'
				parsed['batterie_faible'] = binaryState[7:8]
				parsed['triphase'] = binaryState[2:3]

		except Exception as e:
			logging.debug(str(e))
			logging.debug('Unparsable data')
		data['parsed'] = parsed
		return data

globals.COMPATIBILITY.append(cartelectronic_tic)
