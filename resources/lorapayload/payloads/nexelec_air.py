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

class nexelec_air():
	def __init__(self):
		self.name = 'nexelec_air'

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
			# 1) Realtime air quality ATMO/SENSE/AERO…
			#
			if dataarray[0] in (0xA3, 0xA4, 0xA5, 0xA6, 0xA7):
				logging.debug('ATMO/SENSE/AERO Real time data')
				# Map produit
				pt_map = {
					0xA3: 'ATMO',
					0xA4: 'SENSE',
					0xA5: 'AERO',
					0xA6: 'PMI',
					0xA7: 'AERO_CO2'
				}

				if dataarray[1] == 0x01:
					# PM1 : bits 16–26 (11 bits)
					pm1 = int(binstr[16:27], 2)
					parsed['pm1'] = None if pm1 == 0x7FF else pm1
					# PM2.5 : bits 27–37
					pm25 = int(binstr[27:38], 2)
					parsed['pm2_5'] = None if pm25 == 0x7FF else pm25
					# PM10 : bits 38–48
					pm10 = int(binstr[38:49], 2)
					parsed['pm10'] = None if pm10 == 0x7FF else pm10
					# Température : bits 49–58
					temp_raw = int(binstr[49:59], 2)
					parsed['temperature'] = None if temp_raw == 0x3FF else round((temp_raw / 10) - 30, 1)
					# Humidité : bits 59–66
					hum_raw = int(binstr[59:67], 2)
					parsed['humidity'] = None if hum_raw == 0xFF else round(hum_raw / 2, 1)
					# CO2 : bits 67–80
					co2_raw = int(binstr[67:81], 2)
					parsed['co2'] = None if co2_raw == 0x3FFF else co2_raw
					# COV : bits 81–94
					cov_raw = int(binstr[81:95], 2)
					parsed['cov'] = None if cov_raw == 0x3FFF else cov_raw
					# Formaldéhyde : bits 95–104
					hcho_raw = int(binstr[95:105], 2)
					parsed['formaldehyde'] = None if hcho_raw == 0x3FF else hcho_raw
					# Luminosité : bits 133–140
					lum_raw = int(binstr[133:141], 2)
					parsed['luminosity'] = None if lum_raw == 0xFF else lum_raw * 5
					# Bruit moyen : bits 141–147
					noise_avg = int(binstr[141:148], 2)
					parsed['noise_avg'] = None if noise_avg == 0x7F else noise_avg
					# Pic de bruit : bits 148–154
					noise_peak = int(binstr[148:155], 2)
					parsed['noise_peak'] = None if noise_peak == 0x7F else noise_peak
					# Taux d'occupation : bits 155–163
					occupancy = int(binstr[155:163], 2)
					parsed['occupancy'] = None if occupancy == 0xFF else occupancy
					# Pression : bits 163–173
					press_raw = int(binstr[163:173], 2)
					parsed['pressure'] = None if press_raw == 0x400 else press_raw + 300

					# Métadonnées
					parsed['product_type'] = pt_map[dataarray[0]]
					parsed['message_type'] = 'Realtime air quality'

				elif dataarray[1] == 0x03:
					# Product general configuration
					logging.debug('Product general configuration')
					b2 = dataarray[2]
					src    = (b2 & 0xC0) >> 6
					stat   = (b2 & 0x30) >> 4
					led_en = (b2 & 0x08) >> 3
					led_fn = (b2 & 0x06) >> 1
					iaq    = b2 & 0x01
					b3        = dataarray[3]
					notif_btn = (b3 & 0x80) >> 7
					keepalive = (b3 & 0x40) >> 6
					nfc_stat  = (b3 & 0x30) >> 4
					region    = b3 & 0x07

					src_map  = {0:'NFC',1:'Downlink',2:'Product start-up',3:'RFU'}
					stat_map = {0:'Total success',1:'Partial success',2:'Total failure',3:'RFU'}
					led_map  = {0:'Global air quality',1:'CO2 Level',2:'RFU',3:'RFU'}
					nfc_map  = {0:'Discoverable',1:'Not discoverable',2:'RFU',3:'RFU'}
					reg_map  = {0:'EU868',1:'US915',2:'AS923',3:'AU915',
								4:'KR920',5:'IN865',6:'RU864',7:'RFU'}

					period        = dataarray[4]
					keepalive_per = dataarray[5]
					co2_low       = dataarray[7] * 20
					co2_high      = dataarray[8] * 20

					parsed.update({
						'product_type':         pt_map[dataarray[0]],
						'message_type':         'Product general configuration',
						'reconfig_source':      src_map[src],
						'reconfig_status':      stat_map[stat],
						'led_enable':           'Active' if led_en else 'Inactive',
						'led_function':         led_map[led_fn],
						'iaq_led_average':      'Indicated' if iaq else 'Not indicated',
						'notification_button':  'Active' if notif_btn else 'Inactive',
						'keepalive_enable':     'Active' if keepalive else 'Inactive',
						'nfc_status':           nfc_map[nfc_stat],
						'region':               reg_map[region],
						'measuring_period_min': f"{period} min",
						'keepalive_period_h':   f"{keepalive_per} h",
						'co2_low_threshold':    f"{co2_low} ppm",
						'co2_high_threshold':   f"{co2_high} ppm",
					})

				else:
					parsed['message_type'] = 'Unknown'

			else:
				parsed['message_type'] = 'Unknown'
		except Exception as e:
			logging.debug(f'Erreur décodage Nexelec: {e}')
		return data
	def encode_downlink(self, config: dict) -> str:

#		Génère un downlink hex (port 56) en fonction du groupe :
#       - capteurs air (ATMO/SENSE/AERO…)
#        - capteurs LoRa (FEEL, RISE, MOVE…)
#        """
        # 1) Table pour le 1er groupe (nexelec_air)

		id_length_air = {
            0x03: 1, 0x04: 1, 0x09: 1, 0x0A: 1,
            0x11: 1, 0x12: 1, 0x13: 1, 0x1C: 2,
            0x2D: 1, 0x2E: 1, 0x2F: 1, 0x46: 1
        }

        # Détection du groupe d'après self.product_type_code
		air_codes = (0xA3, 0xA4, 0xA5, 0xA6, 0xA7)
		lora_codes = (0xA9, 0xAA, 0xAB, 0xAC, 0xAD, 0xBE, 0xBF, 0xC9, 0xCA)
		if self.product_type_code in air_codes:
			id_length = id_length_air

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
globals.COMPATIBILITY.append(nexelec_air)

