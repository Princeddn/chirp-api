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

class nexelec_air_2():
	def __init__(self):
		self.name = 'nexelec_air_2'

	def parse(self, data, device):
		logging.debug('Nexelec Received')
		parsed = {}
		data['parsed'] = parsed
		try:
			# Lecture du payload
			payload_hex = data.get('payload', '')
			dataarray = utils.hexarray_from_string(payload_hex)
			if len(dataarray) < 4:
				return data
			payload = payload_hex
			logging.debug(f'Parsing payload bytes: {dataarray}')
			binstr = bin(int(payload, 16))[2:].zfill(len(dataarray) * 8)

			#
			#
			#  Tous les capteurs LoRa (Feel/Rise/Move/…) et messages 0x01–0x17
			#
			if dataarray[0] in (0xA9,0xAA,0xAB,0xAC,0xAD,0xBE,0xBF,0xC9,0xCA):
				msg = dataarray[1]
				logging.debug(f'LoRa device msg 0x{msg:02X}')
				binstr = bin(int(payload,16))[2:].zfill(len(dataarray)*8)

				if msg == 0x01:
					parsed['message_type'] = 'Periodic Data'
					# Température (10 bits)
					raw = (int(payload[4:8], 16) >> 6) & 0x3FF
					parsed['temperature'] = None if raw>=0x3FF else round(raw/10-30,1)
					# Humidité (10 bits)
					raw = int(payload[6:9],16) & 0x3FF
					parsed['humidity'] = None if raw>=0x3FF else round(raw/10,1)
					# CO2 (14 bits)
					raw = (int(payload[9:13],16) >> 2) & 0x3FFF
					parsed['co2'] = None if raw>=0x3FFF else raw
					# COV (14 bits)
					raw = int(payload[12:16],16) & 0x3FFF
					parsed['cov'] = None if raw>=0x3FFF else raw
					# Luminosité (10 bits x5)
					raw = (int(payload[16:19],16) >> 2) & 0x3FF
					parsed['luminosity'] = None if raw>=0x3FF else raw*5
					# Bouton
					raw = (int(payload[18:19],16) >> 1) & 0x01
					parsed['button_press'] = bool(raw)
					# Bruit moyen (7 bits)
					raw = (int(payload[18:21],16) >> 2) & 0x7F
					parsed['noise_avg'] = None if raw>=0x7F else raw
					# Pic de bruit (7 bits)
					raw = (int(payload[20:23],16) >> 3) & 0x7F
					parsed['noise_peak'] = None if raw>=0x7F else raw
					# Occupation (7 bits)
					raw = int(payload[22:24],16) & 0x7F
					parsed['occupancy'] = None if raw>=0x7F else raw
					# IAQ global/co2/cov/source
					ia   = (int(payload[24:26],16) >> 5) & 0x07
					isrc = (int(payload[24:26],16) >> 1) & 0x0F
					ico2 = (int(payload[25:27],16) >> 2) & 0x07
					icov = (int(payload[26:28],16) >> 3) & 0x07
					labels = ["Excellent","Reserved","Fair","Reserved","Bad","Reserved","Reserved","Error"]
					parsed['iziair_global'] = labels[ia]
					parsed['iziair_src']    = labels[isrc]
					parsed['iziair_co2']    = labels[ico2]
					parsed['iziair_cov']    = labels[icov]

				elif msg == 0x02:
					parsed['message_type'] = 'CO2 Historical Data'
					count    = (int(payload[2:4],16) >> 2) & 0x3F
					interval = ((int(payload[2:6],16) >> 2) & 0xFF) * 10
					values = []
					for i in range(count):
						start = 36 + 10*i
						raw = int(binstr[start:start+10],2)
						values.append(0 if raw==0x3FF else round(raw*5,2))
					parsed['co2_history']            = values
					parsed['history_interval_min']   = interval
					parsed['history_count']          = count

				elif msg == 0x03:
					parsed['message_type'] = 'Temperature Historical Data'
					count    = (int(payload[2:4],16) >> 2) & 0x3F
					interval = ((int(payload[2:6],16) >> 2) & 0xFF) * 10
					values = []
					for i in range(count):
						start = 36 + 10*i
						raw = int(binstr[start:start+10],2)
						values.append(0 if raw==0x3FF else round(raw/10-30,2))
					parsed['temp_history']          = values
					parsed['history_interval_min']  = interval
					parsed['history_count']         = count

				elif msg == 0x04:
					parsed['message_type'] = 'Humidity Historical Data'
					count    = (int(payload[2:4],16) >> 2) & 0x3F
					interval = ((int(payload[2:6],16) >> 2) & 0xFF) * 10
					values = []
					for i in range(count):
						start = 36 + 10*i
						raw = int(binstr[start:start+10],2)
						values.append(0 if raw==0x3FF else round(raw*0.1,2))
					parsed['hum_history']          = values
					parsed['history_interval_min'] = interval
					parsed['history_count']        = count

				elif msg == 0x05:
					parsed['message_type'] = 'Product Status'
                    # version hardware (octet 2)
					parsed['hardware_version'] = int(binstr[16:24], 2)
                    # version software (octet 3)
					parsed['software_version'] = int(binstr[24:32], 2)
                    # alimentation principale (bits 32-33)
					ps = int(binstr[32:34], 2)
					parsed['power_source'] = ['Battery','External 5V','Reserved','Reserved'][ps]
	                    # tension batterie (bits 34-43) → 0-1000 => 0-5000 mV

					bv = int(binstr[34:44], 2)
					if bv == 1022:
						parsed['battery_voltage'] = 'External power'
					elif bv == 1023:
						parsed['battery_voltage'] = 'Error'
					else:
						parsed['battery_voltage'] = bv * 5
                    # niveau batterie (bits 44-46)
					bl = int(binstr[44:47], 2)
					lvl = ['High','Medium','Low','Critical','External','Reserved','Reserved','Reserved']
					parsed['battery_level'] = lvl[bl]
                    # statut global matériel (bit 47)
					gs = int(binstr[47:48], 2)
					parsed['hardware_status'] = ['OK','Hardware fault'][gs] \
                        if gs < 2 else f'Reserved({gs})'
                    # statuts capteurs, tous 3 bits chacun
					sensor_labels = ['OK','Fault','Missing','Disabled','EoL','Reserved','Reserved','Reserved']
					parsed['temp_hum_status']      = sensor_labels[int(binstr[48:51],2)]
					parsed['co2_status']           = sensor_labels[int(binstr[51:54],2)]
					parsed['cov_status']           = sensor_labels[int(binstr[54:57],2)]
					parsed['pir_status']           = sensor_labels[int(binstr[57:60],2)]
					parsed['microphone_status']    = sensor_labels[int(binstr[60:63],2)]
					parsed['luminosity_status']    = sensor_labels[int(binstr[63:66],2)]
                    # statut carte SD (bits 66-68)
					sd_labels = ['OK','Mount error','Missing','Disabled','EoL','Reserved','Reserved','Reserved']
					parsed['sd_status'] = sd_labels[int(binstr[66:69],2)]
                    # durée cumulée activation produit (bits 69-78) en mois
					parsed['activation_months'] = int(binstr[69:79],2)
                    # jours depuis dernière calibration (bits 79-86)
					days = int(binstr[79:87],2)
					parsed['days_since_calibration'] = None if days == 255 else days
                    # statut anti-arrachement (bits 96-97)
					at = int(binstr[96:98],2)
					anti = ['Dock not detected','Dock detected','Just removed','Just installed']
					parsed['anti_tear_status'] = anti[at]
				elif msg == 0x06:
					parsed['message_type'] = 'Product Configuration'

                    #  0xA9…0xCA déjà géré plus haut pour parsed['product_type']

                    # Offset de départ : bit 16 dans binstr
                    # 16–18 (3 bits) : source de reconfiguration

					src = int(binstr[16:19], 2)
					parsed['reconfig_source'] = [
                        'NFC',
                        'Downlink applicatif',
                        'Démarrage du produit',
                        'Réseau',
                        'GPS',
                        'Local',
                        'Réservé',
                        'Réservé'
                    ][src]

                    # 19–20 (2 bits) : état de la reconfiguration

					st = int(binstr[19:21], 2)
					parsed['reconfig_status'] = [
                        'Succès total',
                        'Succès partiel',
                        'Échec total',
                        'Réservé'
                    ][st]

                    # 21–25 (5 bits) : période de mesure (minutes)

					period = int(binstr[21:26], 2)
					parsed['measuring_period_min'] = f"{period} min"

                    # 26      (1 bit) : CO2 On/Off
					co2_on = int(binstr[26], 2)
					parsed['co2_active'] = bool(co2_on)

                    # 27      (1 bit) : COV On/Off

					cov_on = int(binstr[27], 2)
					parsed['cov_active'] = bool(cov_on)

                    # 28      (1 bit) : PIR On/Off
					pir_on = int(binstr[28], 2)
					parsed['pir_active'] = bool(pir_on)

                    # 29      (1 bit) : Microphone On/Off
					mic_on = int(binstr[29], 2)
					parsed['microphone_active'] = bool(mic_on)

                    # 30      (1 bit) : Stockage local On/Off
				elif msg == 0x06:
					parsed['message_type'] = 'Product Configuration'

					# …vos premiers décodages (src, st, period, etc.)…

					# 30      (1 bit) : Stockage local On/Off
					sd_on = int(binstr[30], 2)
					parsed['sd_storage_active'] = bool(sd_on)

					# 31      (1 bit) : Calibration automatique CO2
					calib = int(binstr[31], 2)
					parsed['auto_calibration_co2'] = bool(calib)

					# 32–41 (10 bits) : Seuil CO2 niveau moyen (0-1000 → 0-5000ppm)
					thr_mid = int(binstr[32:42], 2) * 5
					parsed['co2_threshold_medium_ppm'] = thr_mid

					# 42–51 (10 bits) : Seuil CO2 niveau élevé (0-1000 → 0-5000ppm)
					thr_hi = int(binstr[42:52], 2) * 5
					parsed['co2_threshold_high_ppm'] = thr_hi

					# 52      (1 bit) : LED CO2 On/Off
					led_co2 = int(binstr[52], 2)
					parsed['led_co2'] = bool(led_co2)

					# 53      (1 bit) : LED niveau moyen On/Off
					led_mid = int(binstr[53], 2)
					parsed['led_medium_level'] = bool(led_mid)

					# 54      (1 bit) : Buzzer On/Off
					buz = int(binstr[54], 2)
					parsed['buzzer'] = bool(buz)

					# 55      (1 bit) : Confirmation buzzer On/Off
					buz_conf = int(binstr[55], 2)
					parsed['buzzer_confirmation'] = bool(buz_conf)

					# 56–57 (2 bits) : Donnée utilisée par LED et buzzer
					led_data = int(binstr[56:58], 2)
					parsed['led_buzzer_data'] = ['CO2', 'iZiAIR', 'Réservé', 'Réservé'][led_data]

					# 58      (1 bit) : Bouton notification On/Off
					btn_notif = int(binstr[58], 2)
					parsed['button_notification'] = bool(btn_notif)

					# 59–62 (4 bits) : Protocole et région
					pr = int(binstr[59:63], 2)
					regions = {
						1: 'LR-EU868',
						2: 'LR-US915',
						4: 'LR-AU915',
						6: 'LR-IN865',
						8: 'SF-RC1'
					}
					parsed['protocol_region'] = regions.get(pr, f"Réservé(0x{pr:02X})")

					# 63      (1 bit) : Données périodiques On/Off
					dp = int(binstr[63], 2)
					parsed['periodic_data_active'] = bool(dp)

					# 64–69 (6 bits) : Période envoi mesures périodiques (10-60min)
					pmin = int(binstr[64:70], 2)
					parsed['periodic_interval_min'] = f"{pmin} min"

					# 70–77 (8 bits) : Delta CO2 (0-250 → 0-1000ppm, 255 désactivé)
					dco2 = int(binstr[70:78], 2)
					parsed['delta_co2_ppm'] = None if dco2 == 255 else dco2 * 4

					# 78–84 (7 bits) : Delta Température (0-99 → 0-9.9°C, 127 désactivé)
					dtmp = int(binstr[78:85], 2)
					parsed['delta_temperature_c'] = None if dtmp == 127 else round(dtmp * 0.1, 1)

					# 85      (1 bit) : Hist. CO2 On/Off
					hist_co2 = int(binstr[85], 2)
					parsed['history_co2_active'] = bool(hist_co2)

					# 86      (1 bit) : Hist. Temp On/Off
					hist_tmp = int(binstr[86], 2)
					parsed['history_temp_active'] = bool(hist_tmp)

					# 87–92 (6 bits) : Nombre nouvelles mesures (1-36)
					cnt = int(binstr[87:93], 2)
					parsed['history_new_count'] = cnt

					# 93–97 (5 bits) : Nombre transmissions (1-24)
					tx = int(binstr[93:98], 2)
					parsed['history_repetition'] = tx

					# 98–105 (8 bits) : Période envoi historisé (3-144min, 255 erreur)
					hp = int(binstr[98:106], 2)
					parsed['history_interval_min'] = None if hp == 255 else hp

					# 106     (1 bit) : Connexion réseau différée
					dr = int(binstr[106], 2)
					parsed['delayed_join'] = bool(dr)

					# 107–108 (2 bits) : Statut NFC
					nf = int(binstr[107:109], 2)
					parsed['nfc_status'] = ['Découvrable','Non découvrable','Réservé','Réservé'][nf]

					# 109–114 (6 bits) : Année (depuis 2000)
					yr = int(binstr[109:115], 2)
					parsed['product_year'] = 2000 + yr

					# 115–118 (4 bits) : Mois (1-12)
					mo = int(binstr[115:119], 2)
					parsed['product_month'] = mo

					# 119–123 (5 bits) : Jour (1-31)
					dy = int(binstr[119:124], 2)
					parsed['product_day'] = dy

					# 124–128 (5 bits) : Heure (0-23)
					hr = int(binstr[124:129], 2)
					parsed['product_hour'] = hr

					# 129–134 (6 bits) : Minute (0-59)
					mn = int(binstr[129:135], 2)
					parsed['product_minute'] = mn

					# 135     (1 bit) : Hist. Humidité On/Off
					hist_h = int(binstr[135], 2)
					parsed['history_humidity_active'] = bool(hist_h)

					# 136–151 (16 bits) : Downlink FCnt (reconfig trigger)
					fc = int(binstr[136:152], 2)
					parsed['downlink_fcnt'] = fc

				else:
					parsed['message_type'] = f'Unknown LoRa msg 0x{msg:02X}'

				parsed['product_type'] = {
					0xA9: 'Feel LoRa', 0xAA: 'Rise LoRa', 0xAB: 'Move LoRa',
					0xAC: 'Wave LoRa', 0xAD: 'Sign LoRa', 0xBE: 'Rise LoRa',
					0xBF: 'Move LoRa', 0xC9: 'Echo LoRa', 0xCA: 'View LoRa'
				}.get(dataarray[0], 'Unknown')

			else:
				parsed['message_type'] = 'Unknown'
		except Exception as e:
			logging.debug(f'Erreur décodage Nexelec: {e}')
		return data
	def encode_downlink(self, config: dict) -> str:

#		Génère un downlink hex (port 56) en fonction du groupe :

#        - capteurs LoRa (FEEL, RISE, MOVE…)
#        """

        #  Table pour le 2nd groupe (LoRa FEEL/Rise/…)
		id_length_lora = {
            0x01: 0, 0x03: 1, 0x04: 1, 0x05: 1,
            0x08: 1, 0x0A: 1, 0x10: 1, 0x12: 1,
            0x13: 1, 0x19: 1, 0x1C: 2, 0x1D: 2,
            0x28: 1, 0x2D: 1, 0x2E: 1, 0x2F: 1,
            0x49: 1, 0x4A: 1, 0x4B: 1, 0x54: 1,
            0x55: 1, 0x56: 1, 0x57: 1, 0x58: 1,
            0x59: 1, 0x5A: 1, 0x5B: 1, 0x5C: 1,
            0x5D: 1, 0x5E: 1, 0x5F: 1
        }

        # Détection du groupe d'après self.product_type_code

		lora_codes = (0xA9, 0xAA, 0xAB, 0xAC, 0xAD, 0xBE, 0xBF, 0xC9, 0xCA)

		if self.product_type_code in lora_codes:
			id_length = id_length_lora


        # Construction du payload
		payload = bytearray([0x55])
		for id_byte in sorted(config.keys()):
			length = id_length.get(id_byte)
			if length is None:
                # ID non reconnu pour ce groupe
				continue

            # commande sans data
			if length == 0:
				payload.append(id_byte)
				payload.append(0)
				continue
			val = config[id_byte]
			if isinstance(val, bool):
				val = 1 if val else 0
            # conversion big-endian sur 'length' octets
			data_bytes = int(val).to_bytes(length, 'big')
			payload.append(id_byte)
			payload.append(length)
			payload.extend(data_bytes)
		return payload.hex().upper()

# … fin de la classe …

# Ajout du décodeur à Jeedom
globals.COMPATIBILITY.append(nexelec_air_2)