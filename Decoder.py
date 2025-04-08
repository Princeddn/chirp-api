# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 16:40:22 2025

@author: nouko
"""

# -*- coding: utf-8 -*-
"""
LoRaWAN Decoder - Decode LoRaWAN payloads and extract useful data.
"""

import base64
import re
import struct

class BaseDecoder():
    def identify_and_process_data(self, input_data):
        """
        Identifie automatiquement le type de la donnée (Base64, hexadécimal ou brut)
        et la convertit en tableau d'octets.
        """
        if isinstance(input_data, str) and re.fullmatch(r"[A-Za-z0-9+/=]+", input_data):
            print("Reconnaissance : Base64 encodé.")
            return self.decode_base64(input_data)
        elif isinstance(input_data, str) and re.fullmatch(r"[0-9a-fA-F]+", input_data):
            print("Reconnaissance : Hexadécimal brut.")
            return self.decode_hex(input_data)
        elif isinstance(input_data, bytes) or isinstance(input_data, list):
            print("Reconnaissance : Tableau d'octets brut.")
            return bytes(input_data)
        else:
            raise ValueError("Format de donnée non reconnu ou invalide.")

    def decode_base64(self, encoded_data):
        """
        Décodage des données Base64.
        """
        try:
            return base64.b64decode(encoded_data)
        except Exception as e:
            raise ValueError(f"Erreur lors du décodage Base64 : {e}")

    def decode_hex(self, hex_string):
        """
        Décodage d'une chaîne hexadécimale brute en tableau d'octets.
        """
        try:
            return bytes.fromhex(hex_string)
        except Exception as e:
            raise ValueError(f"Erreur lors du décodage hexadécimal : {e}")
    def bytes_to_string(self, input_bytes):
        """
        Conversion des octets en chaîne hexadécimale.
        """
        return ''.join(format(byte, '02x') for byte in input_bytes)





class NexelecDecoder(BaseDecoder):

    def decode_uplink(self, input_bytes):
        """
        Traite les données uplink après conversion en tableau d'octets.
        """
        try:
            string_hex = self.bytes_to_string(input_bytes)
            octet_type_produit = int(string_hex[2:4], 16)
            octet_type_message = int(string_hex[4:6], 16)
            data = self.data_output(octet_type_message, string_hex)
            return {"data": data, "errors": None, "warnings": None}
        except Exception as e:
            return {"data": None, "errors": str(e), "warnings": "Erreur lors du décodage"}

    def decode_uplink_auto(self, input_data):
        """
        Décode automatiquement une trame uplink après identification du format.
        """
        try:
            input_bytes = self.identify_and_process_data(input_data)
            return self.decode_uplink(input_bytes)
        except Exception as e:
            return {"data": None, "errors": str(e), "warnings": "Erreur lors du traitement"}


    def data_output(self, octet_type_message, string_hex):
        """
        Décodage des données en fonction du type de message.
        """
        if octet_type_message == 0x01:
            return self.periodic_data_output(string_hex)
        elif octet_type_message == 0x02:
            return self.historical_co2_data_output(string_hex)
        elif octet_type_message == 0x06:
            return self.product_configuration_data_output(string_hex)
        else:
            raise ValueError(f"Type de message inconnu : {octet_type_message}")

    def periodic_data_output(self, string_hex):
        """
        Décodage des données périodiques.
        """
        octet_type_produit = int(string_hex[:2], 16)
        # octet_type_message = int(string_hex[2:4], 16)
        data_temperature = (int(string_hex[4:8], 16) >> 6) & 0x3FF

        data_humidity = int(string_hex[6:9], 16) & 0x3FF
        data_co2 = (int(string_hex[9:13], 16) >> 2) & 0x3FFF
        data_covt = int(string_hex[12:16], 16) & 0x3FFF
        data_luminosity = (int(string_hex[16:19], 16) >> 2) & 0x3FF
        # button_press_value = (int(string_hex[16:18], 16) >> 1) & 0x01
        avg_noise_value = (int(string_hex[18:21], 16) >> 2) & 0x7F
        peak_noise_value = (int(string_hex[20:23], 16) >> 3) & 0x7F
        occupancy_rate_value = int(string_hex[22:24], 16) & 0x7F
        # izi_air_global_value = (int(string_hex[24:26], 16) >> 5) & 0x07
        # izi_air_src_value = (int(string_hex[24:26], 16) >> 1) & 0x0F
        # izi_air_co2_value = (int(string_hex[25:27], 16) >> 2) & 0x07
        # izi_air_cov_value = (int(string_hex[26:28], 16) >> 3) & 0x07
        
        print(f"Température : {data_temperature}")
        print(f"Humidité : {data_humidity}")
        print(f"C02 : {data_co2}")
        print(f"covt : {data_covt}")
        print(f"Luminosity : {data_luminosity}")



        return {
            "Product_type": self.type_of_product(octet_type_produit),
            "temperature": self.decode_temperature(data_temperature),
            "humidity": self.decode_humidity(data_humidity),
            "co2": self.decode_co2(data_co2),
            "voc": self.decode_covt(data_covt),
            "luminosity": self.decode_luminosity(data_luminosity),
            "avg_noise": self.decode_noise(avg_noise_value),
            "peak_noise": self.decode_noise(peak_noise_value),
            "occupancy_rate": occupancy_rate_value,
        }
    
    def periodic_data_output_air(self, payload_hex):
        # On retire les espaces et on calcule le nombre total de bits (4 bits par hexadécimal)
        payload_hex = payload_hex.replace(" ", "")
        total_bits = len(payload_hex) * 4
        # Convertir la chaîne hexadécimale en chaîne binaire avec remplissage à gauche
        bin_str = bin(int(payload_hex, 16))[2:].zfill(total_bits)
        
        # Fonction d'extraction d'un champ de bits
        def get_field(start, length):
            # "start" est l'offset en bits depuis le début (bit 0 = premier bit de la trame)
            return int(bin_str[start:start+length], 2)
        
        # Extraction des champs selon leur position et taille (en bits)
        type_product = get_field(0, 8)
        type_message = get_field(8, 8)
        pm1 = {"value": get_field(16, 11), "unit": "μg/m³"}
        pm25 = {"value": get_field(27, 11), "unit": "μg/m³"}
        pm10 = {"value": get_field(38, 11), "unit": "μg/m³"}
        temp_raw = get_field(49, 10)
        # La température est donnée avec un facteur 0.1 et un décalage de -30°C :
        temperature = {"value": temp_raw * 0.1 - 30, "unit": "°C"}
        humidity_raw = get_field(59, 8)
        # L'humidité est donnée sur 0..200 et correspond à 0..100 %RH (on divise par 2)
        humidity = {"value": humidity_raw / 2, "unit": "%RH"}
        co2 = {"value": get_field(67, 14), "unit": "ppm"}
        voc = {"value": get_field(81, 14), "unit": "µg/m³"}
        formaldehyde = {"value": get_field(95, 10), "unit": "ppb"}
        luminosity_raw = get_field(133, 8)
        # Le champ luminosité, de 0 à 254 correspond à 0 à 1270 lux (facteur 5)
        luminosity = {"value": luminosity_raw * 5, "unit": "lux"}
        avg_noise_raw = get_field(141, 7)
        # Pour le bruit moyen, on ajoute 35 dBA (exemple : 15 + 35 = 50 dBA)
        avg_noise = {"value": avg_noise_raw + 35, "unit": "dBA"}
        peak_noise_raw = get_field(148, 7)
        peak_noise = {"value": peak_noise_raw + 35, "unit": "dBA"}
        occupancy = {"value": get_field(155, 8), "unit": "%"}
        pressure_raw = get_field(163, 10)
        # La pression est donnée avec un offset de 300 hPa : pression = valeur + 300
        pressure = {"value": pressure_raw + 300, "unit": "hPa"}
        frame_index = get_field(224, 3)
        # Les 5 derniers bits (offset 227, taille 5) sont réservés et non utilisés
        
        # Mappage pour le type de produit (en se basant sur la documentation)
        product_types = {
            0xA3: "ATMO",
            0xA4: "SENSE",
            0xA5: "AERO",
            0xA6: "PMI",
            0xA7: "AERO CO2"
        }
        type_product_str = product_types.get(type_product, f"Unknown (0x{type_product:02X})")
        
        # Mappage pour le type de message (ici 0x01 = Real Time Data)
        message_types = {
            0x01: "Real Time Data"
        }
        type_message_str = message_types.get(type_message, f"Unknown (0x{type_message:02X})")
        
        # Construction du résultat en prenant en compte les codes d'erreur (exemple : 2047 pour PM, etc.)
        result = {
            "Product_type": type_product_str,
            "type_message": type_message_str,
            "PM1": pm1 if pm1 != 2047 else "Error",
            "PM2.5": pm25 if pm25 != 2047 else "Error",
            "PM10": pm10 if pm10 != 2047 else "Error",
            "temperature": temperature if temp_raw != 1023 else "Error",
            "humidity": humidity if humidity_raw != 255 else "Error",
            "co2": co2 if co2 != 16383 else "Error",
            "voc": voc if voc != 16384 else "Error",
            "Formaldehyde": formaldehyde if formaldehyde != 1047 else "Error",
            "Luminosity": luminosity if luminosity_raw != 255 else "Error",
            "avg_noise": avg_noise if avg_noise_raw != 127 else "Error",
            "peak_noise": peak_noise if peak_noise_raw != 127 else "Error",
            "occupancy_rate": occupancy if occupancy != 255 else "Error",
            "pressure": pressure if pressure_raw != 1024 else "Error",
            "Indice de trame": frame_index
        }
        
        return result


    def type_of_product(self, octet_type_produit):
        """
        Identifie le type de produit.
        """
        products = {
            0xA3: "ATMO",
            0xA4: "SENSE",
            0xA5: "AERO",
            0xA6: "PMT",
            0xA7: "AERO CO2",
            0xA9: "FEEL",
            0xAA: "RISE",
            0xAB: "MOVE",
            0xFF: "WAVE",
            0xAD: "SIGN",
        }
        return products.get(octet_type_produit, "Inconnu")

    def decode_temperature(self, value):
        return {"value": (value / 10) - 30, "unit": "°C"} if value < 1023 else "Error"

    def decode_humidity(self, value):
        return {"value": value / 10, "unit": "%RH"} if value < 1023 else "Error"

    def decode_co2(self, value):
        return {"value": value, "unit": "ppm"} if value < 16383 else "Error"

    def decode_covt(self, value):
        return {"value": value, "unit": "µg/m³"} if value < 16383 else "Error"

    def decode_luminosity(self, value):
        return {"value": value * 5, "unit": "lux"} if value < 1023 else "Error"

    def decode_noise(self, value):
        return {"value": value, "unit": "dB"} if value != 127 else "Error"

    def decode_presso(self, string_hex):
        """DÃ©code une trame du capteur Press'O de Watteco (0-10V ou 4-20mA)."""

        if len(string_hex) < 11:
            return {"error": "Trame trop courte"}

        # Identifier le type de message et capteur
        # Les 4 derniers octets = 8 caractères hexadécimaux
        raw_value_hex = string_hex[-8:]  # e.g. "3ba15468"
        raw_bytes = bytes.fromhex(raw_value_hex)  # conversion vers bytes
        
        # Extraire le float (format IEEE754 en little-endian) 
        valeur_float = struct.unpack("<f", raw_bytes)[0]

        # Les 2 premiers octets (ou 4) permettent de déterminer le type
        # On conserve votre logique existante :
        type_message = string_hex[:8]  # par exemple "110a000c"        # Déterminer le type de capteur et appliquer la conversion
        if type_message.startswith("310a000c"):  # 0-10V
            capteur_type = "Press'O (0-10V)"
            valeur_V = round(valeur_float / 1000, 3)  # Conversion mV â†’ V
            Tension = {"value":valeur_V, "unit":"V"}
        elif type_message.startswith("110a000c"):  # 4-20mA
            capteur_type = "Press'O (4-20mA)"
            valeur_mA = valeur_float  # La valeur brute est en mA
            valeur_V = round(((valeur_mA - 4) / 16) * 10, 3)  # Conversion en Volts
            Tension = {"value":valeur_V, "unit":"V"}

        else:
            capteur_type = "Inconnu"
            valeur_V = None

        if capteur_type == "Press'O (0-10V)":
            return {"fabricant": "NKE Watteco",
            "Product_type": capteur_type,
            "type_message": type_message,
            "donnees": Tension}
        elif capteur_type == "Press'O (4-20mA)":
            return {"fabricant": "NKE Watteco",
            "Product_type": capteur_type,
            "type_message": type_message,
            "donnees": Tension
        
            }
        else:
            return "Erreur par rapport au type de produit"

class WattecoDecoder(BaseDecoder):

        
    def decode_presso(self, payload_hex: str) -> dict:
        try:
            header = payload_hex[:8].lower()
            data = {}

            # Décodage des grandeurs mesurées selon le header
            if header == "110a0402":  # Température
                raw = int(payload_hex[-4:], 16)
                value = raw / 100
                data = {"capteur": "THR", "mesure": "Température", "valeur": value, "unité": "°C"}

            elif header == "110a0405":  # Humidité
                raw = int(payload_hex[-4:], 16)
                value = raw / 100
                data = {"capteur": "THR", "mesure": "Humidité", "valeur": value, "unité": "%RH"}

            elif header == "110a040c":  # Luminosité (float)
                value = struct.unpack(">f", bytes.fromhex(payload_hex[-8:]))[0]
                data = {"capteur": "THR", "mesure": "Luminosité", "valeur": value, "unité": "% estimée"}

            elif header == "110a000c":  # Press'O 4-20 mA
                value = struct.unpack(">f", bytes.fromhex(payload_hex[-8:]))[0]
                data = {"capteur": "Press'O", "entrée": "4-20mA", "valeur": value, "unité": "mA"}

            elif header == "310a000c":  # Press'O 0-10V
                value = struct.unpack(">f", bytes.fromhex(payload_hex[-8:]))[0]
                data = {"capteur": "Press'O", "entrée": "0-10V", "valeur": value, "unité": "mV"}

            else:
                data = {"erreur": f"Header inconnu : {header}"}

            return data

        except Exception as e:
            return {"erreur": str(e)}