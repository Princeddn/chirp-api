# -*- coding: utf-8 -*-
import logging
import struct
import json
import math
import binascii
import sys
import base64
import re

# --- SHARED UTILS & GLOBALS ---

class utils:
    @staticmethod
    def hexarray_from_string(hex_str):
        if not hex_str: return []
        try:
            return [int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2)]
        except: return []

class globals:
    COMPATIBILITY = []

class BaseDecoder:
    def identify_and_process_data(self, input_data):
        if isinstance(input_data, str) and re.fullmatch(r"[A-Za-z0-9+/=]+", input_data):
            return base64.b64decode(input_data)
        elif isinstance(input_data, str) and re.fullmatch(r"[0-9a-fA-F]+", input_data):
            return bytes.fromhex(input_data)
        elif isinstance(input_data, (bytes, list, bytearray)):
            return bytes(input_data)
        return b""

    def bytes_to_string(self, input_bytes):
        return ''.join(format(byte, '02x') for byte in input_bytes)

# Mock logging
class MockLogger:
    def debug(self, msg): pass
    def info(self, msg): print(f"INFO: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")

logging.getLogger().handlers = []

# --- Source: adeunis_ARF818xxR.py ---

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

import time

import json

import threading



class adeunis_ARF818xxR():

    def __init__(self):

        self.name = 'adeunis_ARF818xxR'



    def parse(self,data,device):

        logging.debug('adeunis_ARF818xxR Received')

        parsed={}

        data['parsed'] = parsed

        try:

            def parse_temperature(segment):

                raw_value = int(segment, 16)

                if raw_value >= 0x8000:

                    raw_value -= 0x10000

                return raw_value / 10



            def parseSensorAlarm(alarm_byte):

                value = int(alarm_byte, 16)

                if value == 0:

                    return "No alarm"

                elif value == 1:

                    return "High threshold"

                elif value == 2:

                    return "Low threshold"

                else:

                    return "Unknown"



            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            logging.debug(payload) 



            if payload[0:2] == '30':

                logging.debug('Keep alive frame')

                status_hex = payload[2:4]

                status = int(status_hex, 16)

                bin_status = format(status, '08b')

                appflag2 = (status >> 4) & 1   # bit4

                parsed['lowbat']  = (status >> 1) & 1    # bit1

                parsed['sensorsActivated'] = 2 if appflag2 == 1 else 1

                if parsed['sensorsActivated'] == 1:

                    logging.debug('1 sensor activated')

                    parsed['temperature1'] = parse_temperature(payload[4:8])

                elif parsed['sensorsActivated'] == 2:

                    logging.debug("2 sensors activated")

                    parsed['temperature1'] = parse_temperature(payload[4:8])

                    parsed['temperature2'] = parse_temperature(payload[8:12])



            if payload[0:2] == '58':

                logging.debug('Keep alive frame')

                status_hex = payload[2:4]

                status = int(status_hex, 16)

                bin_status = format(status, '08b')

                appflag2 = (status >> 4) & 1   # bit4

                parsed['lowbat']  = (status >> 1) & 1    # bit1

                parsed['sensorsActivated'] = 2 if appflag2 == 1 else 1

                if parsed['sensorsActivated'] == 1:

                    logging.debug('1 sensor activated')

                    parsed['alarm1'] = parseSensorAlarm(payload[4:6])

                    parsed['temperature1'] = parse_temperature(payload[6:10])

                elif parsed['sensorsActivated'] == 2:

                    logging.debug("2 sensors activated")

                    parsed['alarm1'] = parseSensorAlarm(payload[4:6])

                    parsed['temperature1'] = parse_temperature(payload[6:10])

                    parsed['alarm2'] = parseSensorAlarm(payload[10:12])

                    parsed['temperature2'] = parse_temperature(payload[12:16])



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(adeunis_ARF818xxR)



# --- Source: adeunis_ARF8230ABA.py ---

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

import time

import json

import threading



class adeunis_ARF8230ABA():

    def __init__(self):

        self.name = 'adeunis_ARF8230ABA'



    def parse(self,data,device):

        logging.debug('adeunis_ARF8230ABA Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            logging.debug(payload) # 100001000239012C57003C27107530000A0000000300050103060A0D



            def decode_debounce(binary_value):

                # Ensure the binary value is 8 bits long

                binary_value = binary_value.zfill(8)



                # Split the binary into two groups

                channel_b_bits = binary_value[:4]  # Bits 4 to 7

                channel_a_bits = binary_value[4:]  # Bits 0 to 3



                # Define debounce period mappings

                debounce_periods = {

                    0: "deactivated",

                    1: "1",

                    2: "10",

                    3: "20",

                    4: "50",

                    5: "100",

                    6: "200",

                    7: "500",

                    8: "1000",

                    9: "2000",

                    10: "5000",

                    11: "10000",

                }

                # Convert binary to integer

                channel_a_value = int(channel_a_bits, 2)

                channel_b_value = int(channel_b_bits, 2)

                # Get debounce periods or reserved

                channel_a_debounce = debounce_periods.get(channel_a_value, "reserved")

                channel_b_debounce = debounce_periods.get(channel_b_value, "reserved")

                return channel_a_debounce, channel_b_debounce



            if payload[0:2] == '46':

                logging.debug('Periodic data without historization')

                parsed['status'] = int(payload[2:4],16)

                parsed['meterChannelA'] = int(payload[4:12],16)

                parsed['meterChannelB'] = int(payload[12:20],16)



            if payload[0:2] == '10':

               frameCounter = payload[2:4]

               parsed['productMode'] = int(payload[4:6],16)

               parsed['historizationsPerSavings'] = int(payload[6:10],16)



               inputConfiguration = bin(int(str(payload[10:12]),16))[2:].zfill(8)

               parsed['tamperInputChannelB'] = int(inputConfiguration[0],16)

               meterChannelB = inputConfiguration[2]

               if meterChannelB == '0':

                   parsed['meterChannelB'] = 'meter different than gas'

               elif meterChannelB == '1':

                   parsed['meterChannelB'] = 'Gas meter'

               parsed['activationChannelB'] = int(inputConfiguration[3],16)

               parsed['tamperInputChannelA'] = int(inputConfiguration[4],16)

               meterChannelA = inputConfiguration[6]

               if meterChannelA == '0':

                   parsed['meterChannelA'] = 'meter different than gas'

               elif meterChannelA == '1':

                   parsed['meterChannelA'] = 'Gas meter'

               parsed['activationChannelA'] = int(inputConfiguration[7],16)



               parsed['historizationPeriod'] = int(payload[12:16],16)*2/60



               debounceDurations = bin(int(str(payload[16:18]),16))[2:].zfill(8)

               channel_a, channel_b = decode_debounce(debounceDurations)

               parsed['debounceDurationChannelA'] =  channel_a

               parsed['debounceDurationChannelB'] =  channel_b



               parsed['flowCalculationPeriod'] = int(payload[18:22],16)

               parsed['flowThresholdChannelA'] = int(payload[22:26],16) 

               parsed['flowThresholdChannelB'] = int(payload[26:30],16)

               parsed['leakThresholdChannelA'] = int(payload[30:34],16)

               parsed['leakThresholdChannelB'] = int(payload[34:38],16)

               parsed['dailyPeriodsUnderTamperThresholdChannelA'] = int(payload[38:42],16)

               parsed['dailyPeriodsUnderTamperThresholdChannelB'] = int(payload[42:46],16)

               parsed['samplingPeriodTamper1'] = int(payload[46:48],16)

               parsed['samplingBeforeTamper1Alarm'] = int(payload[48:50],16)

               parsed['samplingPeriodTamper2'] = int(payload[50:52],16)

               parsed['samplingBeforeTamper2Alarm'] = int(payload[52:54],16)

               parsed['redundantSamplesPerFrame'] = int(payload[54:56],16)



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(adeunis_ARF8230ABA)



# --- Source: adeunis_motion.py ---

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

import time

import json

import threading



class adeunis_motion():

    def __init__(self):

        self.name = 'adeunis_motion'



    def parse(self,data,device):

        logging.debug('adeunis_motion Received')

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



            frameCode = payload[0:2]

            binary1 = payload[2:4]

            if (frameCode == '5c'):

               parsed['presence'] = int(payload[4:6],16)

               parsed['presencePercentage1'] = int(payload[6:8],16)

               parsed['luminosityPercentage1'] = int(payload[8:10],16)

               parsed['presencePercentage2'] = int(payload[10:12],16)

               parsed['luminosityPercentage2'] = int(payload[12:14],16)



            if (frameCode == '5d'):

               parsed['presenceAlarm'] = payload[4:6]

               parsed['alarmLumo'] = int(payload[6:8],16)



            if (frameCode == '50'):

               parsed['lumoAlarm'] = payload[4:6]

               parsed['alarmLumo'] = int(payload[6:8],16)



            if (frameCode == '51'):

               # Digital Input 1

               parsed['IO1State'] = payload[4:5]

               parsed['IO1Prev'] = payload[5:6]

               parsed['events'] = int(payload[6:15],16)

               parsed['eventsLastAlarm'] = int(payload[15:19],16)



            if (frameCode == '52'):

               # Digital Input 2

               parsed['IO2State'] = payload[4:5]

               parsed['IO2Prev'] = payload[5:6]

               parsed['events'] = int(payload[6:15],16)

               parsed['eventsLastAlarm'] = int(payload[15:19],16)

               #logging.debug(parsed['eventsLastAlarm'])



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(adeunis_motion)



# --- Source: adeunis_temperature_humidite.py ---

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

import time

import json

import threading



class adeunis_temperature_humidite():

    def __init__(self):

        self.name = 'adeunis_temperature_humidite'



    def parse(self,data,device):

        logging.debug('adeunis_temperature_humidite Received')

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



            frameCode = payload[0:2]

            binary1 = payload[2:4]

            if (frameCode == '4c'):

               parsed['tempT0'] = int(payload[4:8],16)/10

               parsed['humiT0'] = int(payload[8:10],16)

               parsed['tempT1'] = int(payload[10:14],16)/10

               parsed['humiT1'] = int(payload[14:16],16)

               parsed['tempT2'] = int(payload[16:20],16)/10

               parsed['humiT2'] = int(payload[20:22],16)



            if (frameCode == '4d'):

               binary2 = bin(int(payload[4:6],16))[2:].zfill(8)

               parsed['humidAlarmed'] = binary2[7:8]

               parsed['tempAlarmed'] = binary2[3:4]

               parsed['tempAlarm'] = int(payload[6:10],16)/10

               parsed['humidAlarm'] = int(payload[10:12],16)



            if (frameCode == '51'):

               # Digital Input 1

               parsed['IO1State'] = payload[4:5]

               parsed['IO1Prev'] = payload[5:6]

               parsed['events'] = int(payload[6:15],16)

               parsed['eventsLastAlarm'] = int(payload[15:19],16)



            if (frameCode == '52'):

               # Digital Input 2

               parsed['IO2State'] = payload[4:5]

               parsed['IO2Prev'] = payload[5:6]

               parsed['events'] = int(payload[6:15],16)

               parsed['eventsLastAlarm'] = int(payload[15:19],16)

               #logging.debug(parsed['events'])



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(adeunis_temperature_humidite)



# --- Source: avidsen.py ---

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

import time

import json

import threading

from binascii import unhexlify



class avidsen():

    def __init__(self):

        self.name = 'avidsen'



    def parse(self,data,device):

        logging.debug('Avidsen Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            if dataarray[0] == 0x11:

                logging.debug('This is a garage detector')

                binary = bin(int(str(dataarray[1])))[2:].zfill(8)

                logging.debug('DATA 1 binary is : ' + str(binary))

                open = binary[7:8]

                battery= binary[4:5]

                tension = int(dataarray[2])

                logging.debug('Open is : ' + str(open) + ' , battery is ' + str(battery) + ' and tension is ' + str(tension))

                parsed['ouverture'] = open

                parsed['battery'] = battery

                parsed['tension'] = tension

            elif dataarray[0] == 0x17:

                logging.debug('This is a current clamp')

                binary = bin(int(str(dataarray[1])))[2:].zfill(8)

                logging.debug('DATA 1 binary is : ' + str(binary))

                courant = binary[7:8]

                battery= binary[4:5]

                tension = int(dataarray[4])

                courantval = int(hex( (dataarray[2]<<8) | dataarray[3] ),16)

                logging.debug('Courant is : ' + str(courant) + ' , battery is ' + str(battery) + ' and tension is ' + str(tension) + ' with courant :' + str(courantval))

                parsed['courant'] = courant

                parsed['battery'] = battery

                parsed['tension'] = tension

                parsed['courantval'] = courantval

            else:

                logging.debug('Unknown message')

                return data

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(avidsen)



# --- Source: bmeters_iwmlr3.py ---

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

import time

import json

import threading



class bmeters_iwmlr3():

    def __init__(self):

        self.name = 'bmeters_iwmlr3'



    def parse(self,data,device):

        logging.debug('IWM LR3 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            logging.debug('Parsing')

            payload = data['payload']



            def convertHex(value):

               little_hex = bytearray.fromhex(value)

               little_hex.reverse()

               hex_string = ''.join(format(x, '02x') for x in little_hex)

               #logging.debug(hex_string)

               return hex_string



            appCode = payload[0:2]

            if appCode == '44':

                parsed['absValue'] = convertHex(payload[2:10])

                parsed['revFlow'] = convertHex(payload[10:18])

                indexK_value = payload[18:20]

                if indexK_value == '00':

                    K = 1

                elif indexK_value == '01':

                    K = 10

                elif indexK_value == '02':

                    K = 100



                medium_value = payload[20:22]

                if medium_value == '00':

                    parsed['mediumValue'] = 'Water'

                elif medium_value == '01':

                    parsed['mediumValue'] = 'Hot Water'



                parsed['vif'] = payload[22:24] * K



                alarm_byte = int(payload[24:26], 16)

                if alarm_byte & 0x01:

                    parsed['alarmMagnetic'] = 1

                else:

                    parsed['alarmMagnetic'] = 0



                if alarm_byte & 0x02:

                    parsed['alarmRemoval'] = 1

                else:

                    parsed['alarmRemoval'] = 0



                if alarm_byte & 0x04:

                    parsed['alarmSensorFraud'] = 1

                else:

                    parsed['alarmSensorFraud'] = 0



                if alarm_byte & 0x08:

                    parsed['alarmLeakage'] = 1

                else:

                    parsed['alarmLeakage'] = 0



                if alarm_byte & 0x10:

                    parsed['alarmReverseFlow'] = 1

                else:

                    parsed['alarmReverseFlow'] = 0



                if alarm_byte & 0x20:

                    parsed['alarmLowBattery'] = 1

                else:

                    parsed['alarmLowBattery'] = 0



                temp_raw = int(payload[26:30], 16)

                if temp_raw & 0x8000:

                    temp_value = -(temp_raw & 0x7FFF) / 10.0

                else:

                    temp_value = temp_raw / 10.0

                parsed['temp'] = temp_value



            elif appCode == '07':

                logging.debug('Get firmware version')

                parsed['firmware'] = int(payload[-6:], 16)



            elif appCode == '17':

                logging.debug('GET_REVOLUTION_COUNTERS')

                parsed['fwdCnt'] = int(payload[12:20], 16)

                parsed['backwardCnt'] = int(payload[20:22], 16)



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(bmeters_iwmlr3)



# --- Source: cartelectronic_tic.py ---

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

import time

import json

import threading



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



# --- Source: citylone_sl22.py ---

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

import time

import json

import threading

from datetime import datetime, timedelta



class citylone_sl22():

    def __init__(self):

        self.name = 'citylone_sl22'



    def parse(self,data,device):

        logging.debug('citylone_sl22 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            def checkOUTBitLamp(value, name):

               concatNameMode = 'lamp'+name+'Mode'

               concatNameLevel = 'lamp'+name+'Level'

               level = int(value[1:8],2)

               parsed[concatNameLevel] = level

               if name == 'relay':

                   if level == 1:

                       logging.debug('ON')

                       parsed[concatNameLevel] = 'On'

                   elif level == 0:

                       logging.debug('OFF')

                       parsed[concatNameLevel] = 'Off'

               if (value[0] == '1'):

                   logging.debug('Forced')

                   parsed[concatNameMode] = 'Forced'

               elif (value[0] == '0'):

                   logging.debug('Auto')

                   parsed[concatNameMode] = 'Auto'



            def checkOUTBitState(value):

               parsed['stateS1'] = 0

               parsed['stateS2'] = 0

               parsed['stateS3'] = 0

               parsed['stateS4'] = 0

               if (value[0] == '1'):

                   parsed['stateS4'] = 1

               if (value[1] == '1'):

                   parsed['stateS3'] = 1

               if (value[2] == '1'):

                   parsed['stateS2'] = 1

               if (value[3] == '1'):

                   parsed['stateS1'] = 1



            def checkOUTBitStatus(value):

               parsed['statusS1'] = 'Auto'

               parsed['statusS2'] = 'Auto'

               parsed['statusS3'] = 'Auto'

               parsed['statusS4'] = 'Auto'

               if (value[0] == '1'):

                   parsed['statusS4'] = 'Priority'

               if (value[1] == '1'):

                   parsed['statusS3'] = 'Priority'

               if (value[2] == '1'):

                   parsed['statusS2'] = 'Priority'

               if (value[3] == '1'):

                   parsed['statusS1'] = 'Priority'



            def convertHex(value):

               little_hex = bytearray.fromhex(value)

               little_hex.reverse()

               hex_string = ''.join(format(x, '02x') for x in little_hex)

               #logging.debug(hex_string)

               return hex_string



            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            logging.debug(payload)



            if payload[0:2] == '17':

                logging.debug('Electrical measurement node')

                parsed['voltage'] = int(convertHex(payload[2:6]),16)

                parsed['current'] = int(convertHex(payload[6:10]),16)

                parsed['power'] = int(convertHex(payload[10:14]),16)

                parsed['powerFactor'] = int(convertHex(payload[14:18]),16)/1000

                parsed['temperature'] = int(convertHex(payload[18:22]),16)

                parsed['ledVoltage'] = int(convertHex(payload[22:26]),16)



            if payload[0:2] == '16':

                logging.debug('Node commands feedback')

                lamp11 = checkOUTBitLamp(bin(int(str(payload[2:4]),16))[2:].zfill(8), '11')

                lamp12 = checkOUTBitLamp(bin(int(str(payload[4:6]),16))[2:].zfill(8), '12')

                lamp110 = checkOUTBitLamp(bin(int(str(payload[10:12]),16))[2:].zfill(8), '110')

                lampRelay = checkOUTBitLamp(bin(int(str(payload[12:14]),16))[2:].zfill(8), 'relay')



            if payload[0:2] == '19':

                logging.debug('Node failures !!!!')



            if payload[0:2] == '09':

                logging.debug('SLB Ouptut feedback')

                states = bin(int(str(payload[2:4]),16))[2:].zfill(4)

                checkOUTBitState(states)

                status = bin(int(str(payload[4:6]),16))[2:].zfill(4)

                checkOUTBitStatus(status)



            if payload[0:2] == '07':

                logging.debug('Dry contact input 1')

                input1 = payload[3:4]

                if input1 == '1':

                    parsed['entree1'] = 1

                elif input1 == '0':

                    parsed['entree1'] = 0



            if payload[0:2] == '0b':

                logging.debug('Dry contact input 2')

                input2 = payload[3:4]

                if input2 == '1':

                    parsed['entree2'] = 1

                elif input2 == '0':

                    parsed['entree2'] = 0



            if payload[0:2] == '0e':

                logging.debug('RSSI feedback')

                valeur = payload[4:6] + payload[2:4]

                rssi = int(str(valeur),16)

                parsed['rssi'] = '-' + str(rssi)



            if payload[0:2] == '11':

                logging.debug('Current timestamp')

                original_timestamp = int(convertHex(payload[2:10]), 16)

                original_datetime = datetime.utcfromtimestamp(original_timestamp)



                time = int(convertHex(payload[10:14]),16)

                binary = bin(time)[2:].zfill(16)

                hours = int(binary[2:9],16)

                minutes = int(binary[9:16],16)

                operator = binary[0:2]

                if operator == '01':

                    custom_hours = +hours

                elif operator == '10':

                    custom_hours = -hours



                new_datetime = original_datetime + timedelta(hours=custom_hours)

                new_timestamp = int(new_datetime.timestamp())



                dt_object = datetime.utcfromtimestamp(original_timestamp)

                parsed['currentTimestampGMT'] = dt_object.strftime('%Y-%m-%d %H:%M:%S')

                dt_object = datetime.utcfromtimestamp(new_timestamp)

                parsed['currentTimestamp'] = dt_object.strftime('%Y-%m-%d %H:%M:%S')



                activation = payload[15:16]

                if activation == '1':

                    parsed['updateViaLns'] = 1

                elif activation == '0':

                    parsed['updateViaLns'] = 0



            if payload[0:2] == '12':

                logging.debug('Position feedback')

                parsed['longitude'] = int(convertHex(payload[2:10]),16)/1000000

                parsed['latitude'] = int(convertHex(payload[10:18]),16)/1000000



            if payload[0:2] == '04':

                logging.debug('Power Failure')

                parsed['powerFailure'] = 1



            if payload[0:2] == '13':

                state = payload[3:4]

                if state == '1':

                    parsed['timeChangeState'] = 1

                elif state == '0':

                    parsed['timeChangeState'] = 0



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(citylone_sl22)



# --- Source: citylone_sl32.py ---

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

import time

import json

import threading

from datetime import datetime, timedelta



class citylone_sl32():

    def __init__(self):

        self.name = 'citylone_sl32'



    def parse(self,data,device):

        logging.debug('citylone_sl32 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            def checkOUTBitLamp(value, name):

               concatNameMode = 'lamp'+name+'Mode'

               concatNameLevel = 'lamp'+name+'Level'

               level = int(value[1:8],2)

               parsed[concatNameLevel] = level

               if name == 'relay':

                   if level == 1:

                       parsed[concatNameLevel] = 'On'

                   elif level == 0:

                       parsed[concatNameLevel] = 'Off'

               if (value[0] == '1'):

                   parsed[concatNameMode] = 'Forced'

               elif (value[0] == '0'):

                   parsed[concatNameMode] = 'Auto'



            def checkOUTBitState(value):

               parsed['stateS1'] = 0

               parsed['stateS2'] = 0

               parsed['stateS3'] = 0

               parsed['stateS4'] = 0

               if (value[0] == '1'):

                   parsed['stateS4'] = 1

               if (value[1] == '1'):

                   parsed['stateS3'] = 1

               if (value[2] == '1'):

                   parsed['stateS2'] = 1

               if (value[3] == '1'):

                   parsed['stateS1'] = 1



            def checkOUTBitStatus(value):

               parsed['statusS1'] = 'Auto'

               parsed['statusS2'] = 'Auto'

               parsed['statusS3'] = 'Auto'

               parsed['statusS4'] = 'Auto'

               if (value[0] == '1'):

                   parsed['statusS4'] = 'Priority'

               if (value[1] == '1'):

                   parsed['statusS3'] = 'Priority'

               if (value[2] == '1'):

                   parsed['statusS2'] = 'Priority'

               if (value[3] == '1'):

                   parsed['statusS1'] = 'Priority'



            def convertHex(value):

               little_hex = bytearray.fromhex(value)

               little_hex.reverse()

               hex_string = ''.join(format(x, '02x') for x in little_hex)

               #logging.debug(hex_string)

               return hex_string



            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            logging.debug(payload)



            if payload[0:2] == '17':

                logging.debug('Electrical measurement node')

                parsed['voltage'] = int(convertHex(payload[2:6]),16)

                parsed['current'] = int(convertHex(payload[6:10]),16)

                parsed['power'] = int(convertHex(payload[10:14]),16)

                parsed['powerFactor'] = int(convertHex(payload[14:18]),16)/1000

                parsed['temperature'] = int(convertHex(payload[18:22]),16)

                parsed['ledVoltage'] = int(convertHex(payload[22:26]),16)



            if payload[0:2] == '16':

                logging.debug('Node commands feedback')

                lamp11 = checkOUTBitLamp(bin(int(str(payload[2:4]),16))[2:].zfill(8), '11')

                lamp12 = checkOUTBitLamp(bin(int(str(payload[4:6]),16))[2:].zfill(8), '12')

                lamp21 = checkOUTBitLamp(bin(int(str(payload[6:8]),16))[2:].zfill(8), '21')

                lamp22 = checkOUTBitLamp(bin(int(str(payload[8:10]),16))[2:].zfill(8), '22')

                lamp110 = checkOUTBitLamp(bin(int(str(payload[10:12]),16))[2:].zfill(8), '110')

                lampRelay = checkOUTBitLamp(bin(int(str(payload[12:14]),16))[2:].zfill(8), 'relay')



            if payload[0:2] == '19':

                logging.debug('Node failures !!!!')



            if payload[0:2] == '09':

                logging.debug('SLB Ouptut feedback')

                states = bin(int(str(payload[2:4]),16))[2:].zfill(4)

                checkOUTBitState(states)

                status = bin(int(str(payload[4:6]),16))[2:].zfill(4)

                checkOUTBitStatus(status)



            if payload[0:2] == '07':

                logging.debug('Dry contact input 1')

                input1 = payload[3:4]

                if input1 == '1':

                    parsed['entree1'] = 1

                elif input1 == '0':

                    parsed['entree1'] = 0



            if payload[0:2] == '0b':

                logging.debug('Dry contact input 2')

                input2 = payload[3:4]

                if input2 == '1':

                    parsed['entree2'] = 1

                elif input2 == '0':

                    parsed['entree2'] = 0



            if payload[0:2] == '0e':

                logging.debug('RSSI feedback')

                valeur = payload[4:6] + payload[2:4]

                rssi = int(str(valeur),16)

                parsed['rssi'] = '-' + str(rssi)



            if payload[0:2] == '11':

                logging.debug('Current timestamp')

                original_timestamp = int(convertHex(payload[2:10]), 16)

                original_datetime = datetime.utcfromtimestamp(original_timestamp)



                time = int(convertHex(payload[10:14]),16)

                binary = bin(time)[2:].zfill(16)

                hours = int(binary[2:9],16)

                minutes = int(binary[9:16],16)

                operator = binary[0:2]

                if operator == '01':

                    custom_hours = +hours

                elif operator == '10':

                    custom_hours = -hours



                new_datetime = original_datetime + timedelta(hours=custom_hours)

                new_timestamp = int(new_datetime.timestamp())



                dt_object = datetime.utcfromtimestamp(original_timestamp)

                parsed['currentTimestampGMT'] = dt_object.strftime('%Y-%m-%d %H:%M:%S')

                dt_object = datetime.utcfromtimestamp(new_timestamp)

                parsed['currentTimestamp'] = dt_object.strftime('%Y-%m-%d %H:%M:%S')



                activation = payload[15:16]

                if activation == '1':

                    parsed['updateViaLns'] = 1

                elif activation == '0':

                    parsed['updateViaLns'] = 0



            if payload[0:2] == '12':

                logging.debug('Position feedback')

                parsed['longitude'] = int(convertHex(payload[2:10]),16)/1000000

                parsed['latitude'] = int(convertHex(payload[10:18]),16)/1000000



            if payload[0:2] == '04':

                logging.debug('Power Failure')

                parsed['powerFailure'] = 1



            if payload[0:2] == '13':

                state = payload[3:4]

                if state == '1':

                    parsed['timeChangeState'] = 1

                elif state == '0':

                    parsed['timeChangeState'] = 0



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(citylone_sl32)



# --- Source: citylone_smartlighting.py ---

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

import time

import json

import threading

from datetime import datetime, timedelta



class citylone_smartlighting():

    def __init__(self):

        self.name = 'citylone_smartlighting'



    def parse(self,data,device):

        logging.debug('citylone_smartlighting Received')

        parsed={}

        data['parsed'] = parsed

        try:

            def checkOUTBitState(value):

               parsed['stateS1'] = 0

               parsed['stateS2'] = 0

               parsed['stateS3'] = 0

               parsed['stateS4'] = 0

               if (value[0] == '1'):

                   parsed['stateS4'] = 1

               if (value[1] == '1'):

                   parsed['stateS3'] = 1

               if (value[2] == '1'):

                   parsed['stateS2'] = 1

               if (value[3] == '1'):

                   parsed['stateS1'] = 1



            def checkOUTBitStatus(value):

               parsed['statusS1'] = 'Auto'

               parsed['statusS2'] = 'Auto'

               parsed['statusS3'] = 'Auto'

               parsed['statusS4'] = 'Auto'

               if (value[0] == '1'):

                   parsed['statusS4'] = 'Priority'

               if (value[1] == '1'):

                   parsed['statusS3'] = 'Priority'

               if (value[2] == '1'):

                   parsed['statusS2'] = 'Priority'

               if (value[3] == '1'):

                   parsed['statusS1'] = 'Priority'



            def convertHex(value):

               little_hex = bytearray.fromhex(value)

               little_hex.reverse()

               hex_string = ''.join(format(x, '02x') for x in little_hex)

               #logging.debug(hex_string)

               return hex_string



            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            logging.debug(payload)



            if payload[0:2] == '09':

                logging.debug('SLB Ouptut feedback')

                states = bin(int(str(payload[2:4]),16))[2:].zfill(4)

                checkOUTBitState(states)

                status = bin(int(str(payload[4:6]),16))[2:].zfill(4)

                checkOUTBitStatus(status)



            if payload[0:2] == '07':

                logging.debug('Dry contact input 1')

                input1 = payload[3:4]

                if input1 == '1':

                    parsed['entree1'] = 1

                elif input1 == '0':

                    parsed['entree1'] = 0



            if payload[0:2] == '0b':

                logging.debug('Dry contact input 2')

                input2 = payload[3:4]

                if input2 == '1':

                    parsed['entree2'] = 1

                elif input2 == '0':

                    parsed['entree2'] = 0



            if payload[0:2] == '0e':

                logging.debug('RSSI feedback')

                valeur = payload[4:6] + payload[2:4]

                rssi = int(str(valeur),16)

                parsed['rssi'] = '-' + str(rssi)



            if payload[0:2] == '11':

                logging.debug('Current timestamp')

                original_timestamp = int(convertHex(payload[2:10]), 16)

                original_datetime = datetime.utcfromtimestamp(original_timestamp)



                time = int(convertHex(payload[10:14]),16)

                binary = bin(time)[2:].zfill(16)

                hours = int(binary[2:9],16)

                minutes = int(binary[9:16],16)

                operator = binary[0:2]

                if operator == '01':

                    custom_hours = +hours

                elif operator == '10':

                    custom_hours = -hours



                new_datetime = original_datetime + timedelta(hours=custom_hours)

                new_timestamp = int(new_datetime.timestamp())



                dt_object = datetime.utcfromtimestamp(original_timestamp)

                parsed['currentTimestampGMT'] = dt_object.strftime('%Y-%m-%d %H:%M:%S')

                dt_object = datetime.utcfromtimestamp(new_timestamp)

                parsed['currentTimestamp'] = dt_object.strftime('%Y-%m-%d %H:%M:%S')



                activation = payload[15:16]

                if activation == '1':

                    parsed['updateViaLns'] = 1

                elif activation == '0':

                    parsed['updateViaLns'] = 0



            if payload[0:2] == '12':

                logging.debug('Position feedback')

                parsed['longitude'] = int(convertHex(payload[2:10]),16)/1000000

                parsed['latitude'] = int(convertHex(payload[10:18]),16)/1000000



            if payload[0:2] == '01':

                logging.debug('TIC meter frame 1')

                parsed['indexBase'] = int(convertHex(payload[2:10]),16)

                parsed['indexHcHc'] = int(convertHex(payload[10:18]),16)

                parsed['indexHcHp'] = int(convertHex(payload[18:26]),16)



            if payload[0:2] == '02':

                logging.debug('TIC meter frame 2')

                input1 = payload[3:4]

                if input1 == '1':

                    parsed['entree1'] = 1

                elif input1 == '0':

                    parsed['entree1'] = 0

                input2 = payload[5:6]

                if input2 == '1':

                    parsed['entree2'] = 1

                elif input2 == '0':

                    parsed['entree2'] = 0

                byte_data = bytes.fromhex(payload[6:32])

                utf8_string = byte_data.decode('utf-8')

                parsed['ticMeterId'] = utf8_string.replace('\u0000', '')

                byte_data = bytes.fromhex(payload[32:42])

                utf8_string = byte_data.decode('utf-8')

                parsed['tarifOption'] = utf8_string.replace('\u0000', '')

                parsed['indexBase'] = int(convertHex(payload[42:50]),16)

                parsed['indexHcHc'] = int(convertHex(payload[50:58]),16)

                parsed['indexHcHp'] = int(convertHex(payload[58:66]),16)



            if payload[0:2] == '03':

                logging.debug('TIC meter frame 3')

                parsed['courantInstantaneMonophase'] = int(convertHex(payload[2:6]),16)

                parsed['courantInstantanePhase1'] = int(convertHex(payload[6:10]),16)

                parsed['courantInstantanePhase2'] = int(convertHex(payload[10:14]),16)

                parsed['courantInstantanePhase3'] = int(convertHex(payload[14:18]),16)

                parsed['maxCourantInstantaneMonophase'] = int(convertHex(payload[18:22]),16)

                parsed['maxCourantInstantanePhase1'] = int(convertHex(payload[22:26]),16)

                parsed['maxCourantInstantanePhase2'] = int(convertHex(payload[26:30]),16)

                parsed['maxCourantInstantanePhase3'] = int(convertHex(payload[30:34]),16)

                parsed['maxPuissanceActive'] = int(convertHex(payload[34:38]),16)

                parsed['puissanceThresoldAlarm'] = int(convertHex(payload[38:42]),16)

                parsed['puissanceInstantaneApparente'] = int(convertHex(payload[42:46]),16)



            if payload[0:2] == '04':

                logging.debug('Power Failure')

                parsed['powerFailure'] = 1



            if payload[0:2] == '13':

                state = payload[3:4]

                if state == '1':

                    parsed['timeChangeState'] = 1

                elif state == '0':

                    parsed['timeChangeState'] = 0



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(citylone_smartlighting)



# --- Source: diehl_HRLcG3.py ---

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

import time

import json

import threading

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



# --- Source: dragino_D20LBLS.py ---

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

import time

import json

import threading



class dragino_D20LBLS():

    def __init__(self):

        self.name = 'dragino_D20LBLS'



    def parse(self,data,device):

        logging.debug('dragino_D20LBLS Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            logging.debug(payload)

            parsed['battery'] = int(payload[0:4], 16)/1000

            redProbe = int(payload[4:8],16) & 0x8000

            if redProbe == 0:

                parsed['tempC1'] = int(payload[4:8], 16)/10

            else:

                parsed['tempC1'] = (int(payload[4:8], 16)-65536)/10

            parsed['alarm'] = int(payload[12:14],16) & 0x01

            pa8Level = ( int(payload[12:14],16) & 0x80 ) >> 7

            if pa8Level == 0:

                parsed['pa8Level'] = 'high'

            else:

                parsed['pa8Level'] = 'low'

            mod = ( int(payload[12:14],16) & 0x7C ) >> 7

            if mod == 0:

                parsed['mod'] = '1'

            else:

                parsed['mod'] = '31'



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(dragino_D20LBLS)



# --- Source: dragino_D22LBLS.py ---

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

import time

import json

import threading



class dragino_D22LBLS():

    def __init__(self):

        self.name = 'dragino_D22LBLS'



    def parse(self,data,device):

        logging.debug('dragino_D22LBLS Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            logging.debug(payload)

            parsed['battery'] = int(payload[0:4], 16)/1000

            whiteProbe = int(payload[4:8],16) & 0x8000

            if whiteProbe == 0:

                parsed['tempC1'] = int(payload[4:8], 16)/10

            else:

                parsed['tempC1'] = (int(payload[4:8], 16)-65536)/10

            parsed['alarm'] = int(payload[12:14],16) & 0x01

            pa8Level = ( int(payload[12:14],16) & 0x80 ) >> 7

            if pa8Level == 0:

                parsed['pa8Level'] = 'high'

            else:

                parsed['pa8Level'] = 'low'

            mod = ( int(payload[12:14],16) & 0x7C ) >> 7

            if mod == 0:

                parsed['mod'] = '1'

            else:

                parsed['mod'] = '31'

            redProbe = int(payload[14:18],16) & 0x8000

            if redProbe == 0:

                parsed['tempC2'] = int(payload[14:18], 16)/10

            else:

                parsed['tempC2'] = (int(payload[14:18], 16)-65536)/10



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(dragino_D22LBLS)



# --- Source: dragino_D23LBLS.py ---

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

import time

import json

import threading



class dragino_D23LBLS():

    def __init__(self):

        self.name = 'dragino_D23LBLS'



    def parse(self,data,device):

        logging.debug('dragino_D23LBLS Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            logging.debug(payload)

            parsed['battery'] = int(payload[0:4], 16)/1000

            whiteProbe = int(payload[4:8],16) & 0x8000

            if whiteProbe == 0:

                parsed['tempC1'] = int(payload[4:8], 16)/10

            else:

                parsed['tempC1'] = (int(payload[4:8], 16)-65536)/10

            parsed['alarm'] = int(payload[12:14],16) & 0x01

            pa8Level = ( int(payload[12:14],16) & 0x80 ) >> 7

            if pa8Level == 0:

                parsed['pa8Level'] = 'high'

            else:

                parsed['pa8Level'] = 'low'

            mod = ( int(payload[12:14],16) & 0x7C ) >> 7

            if mod == 0:

                parsed['mod'] = '1'

            else:

                parsed['mod'] = '31'

            redProbe = int(payload[14:18],16) & 0x8000

            if redProbe == 0:

                parsed['tempC2'] = int(payload[14:18], 16)/10

            else:

                parsed['tempC2'] = (int(payload[14:18], 16)-65536)/10

            blackProbe = int(payload[14:18],16) & 0x8000

            if blackProbe == 0:

                parsed['tempC3'] = int(payload[18:22], 16)/10

            else:

                parsed['tempC3'] = (int(payload[18:22], 16)-65536)/10



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(dragino_D23LBLS)



# --- Source: dragino_LAQ4.py ---

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

import time

import json

import threading



class dragino_LAQ4():

    def __init__(self):

        self.name = 'dragino_LAQ4'



    def parse(self,data,device):

        logging.debug('LAQ4 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            logging.debug('Parsing')

            payload = data['payload']

            parsed['battery'] = int(payload[0:4], 16) / 1000

            parsed['tvoc'] = int(payload[6:10], 16)

            parsed['eco2'] = int(payload[10:14], 16)

            if payload[14:15] == "F" :

                value = int(payload[14:18], 16) - 65536

                parsed['temperature'] = (value / 10)

            else :

                parsed['temperature'] = int(payload[14:18], 16) / 10

            parsed['humidity'] = int(payload[18:22], 16) / 10

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(dragino_LAQ4)



# --- Source: dragino_LDS02.py ---

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

import time

import json

import threading



class dragino_LDS02():

    def __init__(self):

        self.name = 'dragino_LDS02'



    def parse(self,data,device):

        logging.debug('dragino_LDS02 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')



            # STATUS

            status = 1 if (dataarray[0] & 0x80) else 0

            parsed['status'] = status # 0

            logging.debug(status)



            # BATTERY

            value = (dataarray[0] << 8 | dataarray[1]) & 0x3FFF

            parsed['battery'] = value/1000 # 3.138

            logging.debug('Battery : ' + str(parsed['battery']))



            # MOD

            binary1 = str(hex(dataarray[2])[2:].zfill(2)) # 01

            logging.debug(binary1)

            if binary1 == '01':

               parsed['MOD'] = 1

            if binary1 == '00':

               parsed['MOD'] = 0



            # DOOR_OPEN_TIMES

            open_times = dataarray[3]<<16 | dataarray[4]<<8 | dataarray[5]

            parsed['totalopen'] = open_times # 147

            logging.debug('open_times : ' + str(parsed['totalopen']))



            # LAST_DOOR_OPEN_DURATION

            open_duration = dataarray[6]<<16 | dataarray[7]<<8 | dataarray[8]

            parsed['lastopenduration'] = open_duration # 0

            logging.debug('open_duration : ' + str(parsed['lastopenduration']))



            # ALARM

            alarm = dataarray[9]&0x01

            parsed['alarm'] = alarm # 0

            logging.debug('alarm : ' + str(parsed['alarm']))



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(dragino_LDS02)



# --- Source: dragino_LGT92.py ---

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

import time

import json

import threading



class dragino_LGT92():

    def __init__(self):

        self.name = 'dragino_LGT92'



    def parse(self,data,device):

        logging.debug('dragino_LGHT92 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            payload = data['payload']

            logging.debug('Parsing')

            payload = data['payload']

            if payload[0:1] == "F" :

                value = int(payload[0:8], 16) - 4294967296

                parsed['latitude'] = (value / 1000000)

            else :

                parsed['latitude'] = int(payload[0:8], 16) / 1000000

            if payload[8:8] == "F" :

                value = int(payload[8:16], 16) - 4294967296

                parsed['longitude'] = (value / 1000000)

            else :

                parsed['longitude'] = int(payload[8:16], 16) / 1000000

            parsed['alarm'] = int( int(payload[16:18],16) & int("0x40",16) >0)

            parsed['battery'] = (int(payload[16:20],16) & int("0x3FFF",16))/1000

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(dragino_LGT92)



# --- Source: dragino_LHT65.py ---

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

import time

import json

import threading



class dragino_LHT65():

    def __init__(self):

        self.name = 'dragino_LHT65'



    def parse(self,data,device):

        logging.debug('dragino_LHT65 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            parsed['BAT']=float(int(hex( (dataarray[0]<<8) | dataarray[1]),16) & 0x3FFF) / 1000

            value = (dataarray[2]<<8) | dataarray[3]

            if(dataarray[2] & 0x80):

                value = int(hex(value),16) - 65536

            parsed['temperature'] = value/100

            parsed['humidity'] = int(payload[8:12], 16) / 10

            mod = str(payload[12:14])

            logging.debug(mod)

            if mod == "01" :

                logging.debug('MOD1')

                if payload[14:15] == "f" :

                    value = int(payload[14:18], 16) - 65536

                    parsed['E1'] = (value / 100)

                else :

                    parsed['E1'] = int(payload[14:18], 16) / 100

            if mod == "04" :

                logging.debug('MOD4')

                parsed['E4']=int(payload[14:16], 16)

            if mod == "14" :

                logging.debug('MOD4 - ERROR CABLE')

            if mod == "05" :

                logging.debug('MOD5')

                parsed['E5']=int(payload[14:18], 16)

            if mod == "15" :

                logging.debug('MOD5 - ERROR CABLE')

            if mod == "06" :

                logging.debug('MOD6')

                parsed['E6']=int(payload[14:18], 16)

            if mod == "16" :

                logging.debug('MOD6 - ERROR CABLE')

            if mod == "07" :

                logging.debug('MOD7')

                parsed['E7']=int(payload[14:18], 16)

            if mod == "17" :

                logging.debug('MOD7 - ERROR CABLE')

            if mod == "08" :

                logging.debug('MOD8')

                parsed['E8']=int(payload[14:22], 16)

            if mod == "18" :

                logging.debug('MOD8 - ERROR CABLE')

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(dragino_LHT65)



# --- Source: dragino_LSN50_V2_mod4.py ---

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

import time

import json

import threading



class dragino_LSN50_V2_mod4():

    def __init__(self):

        self.name = 'dragino_LSN50_V2_mod4'



    def parse(self,data,device):

        logging.debug('dragino_LSN50_V2_mod4 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            logging.debug('Parsing')

            payload = data['payload']

            parsed['battery'] = int(payload[0:4], 16) / 1000



            temperature1 = int(payload[4:8],16) & 0x8000

            if temperature1 == 0:

                parsed['temperature1'] = int(payload[4:8], 16)/10

            else:

                parsed['temperature1'] = (int(payload[4:8], 16)-65536)/10



            temperature2 = int(payload[14:18],16) & 0x8000

            if temperature2 == 0:

                parsed['temperature2'] = int(payload[14:18], 16)/10

            else:

                parsed['temperature2'] = (int(payload[14:18], 16)-65536)/10



            temperature3 = int(payload[18:22],16) & 0x8000

            if temperature3 == 0:

                parsed['temperature3'] = int(payload[18:22], 16)/10

            else:

                parsed['temperature3'] = (int(payload[18:22], 16)-65536)/10



            digitalInterrupt = int(payload[12:14],16) & 0x80

            if (int(payload[12:14], 16) & 0x80) == 0x80:

                parsed['digitalInterrupt'] = 1

            else:

                parsed['digitalInterrupt'] = 0

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(dragino_LSN50_V2_mod4)



# --- Source: dragino_LSN50_V2_mod6.py ---

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

import time

import json

import threading



class dragino_LSN50_V2_mod6():

    def __init__(self):

        self.name = 'dragino_LSN50_V2_mod6'



    def parse(self,data,device):

        logging.debug('dragino_LSN50_V2_mod6 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            logging.debug('Parsing')

            payload = data['payload']

            parsed['battery'] = int(payload[0:4], 16) / 1000

            parsed['temperature'] = int(payload[4:8], 16) / 10

            parsed['count'] = int(payload[14:22], 16)

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(dragino_LSN50_V2_mod6)



# --- Source: dragino_LT_22222.py ---

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

import time

import json

import threading



class dragino_LT_22222():

    def __init__(self):

        self.name = 'dragino_LT_22222'



    def parse(self,data,device):

        logging.debug('dragino_LT_22222 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            logging.debug('Parsing')

            payload = data['payload']

            mod = int(payload[-1], 16)

            if mod == 1 :

                logging.debug('MOD1')

                parsed['mod'] = 1

                parsed['AVI1']=int(payload[0:4], 16) / 1000

                parsed['AVI2']=int(payload[4:8], 16) / 1000

                parsed['ACI1']=int(payload[8:12], 16) / 1000

                parsed['ACI2']=int(payload[12:16], 16) / 1000

                binary = bin(int(payload[16:18], 16))[2:].zfill(8)

                parsed['RO1']=binary[0:1]

                parsed['RO2']=binary[1:2]

                parsed['DI3']=binary[2:3]

                parsed['DI2']=binary[3:4]

                parsed['DI1']=binary[4:5]

                parsed['DO3']=binary[5:6]

                parsed['DO2']=binary[6:7]

                parsed['DO1']=binary[7:8]

            if mod == 2 :

                logging.debug('MOD2')

                parsed['mod'] = 2

                parsed['COUNT1']=int(payload[0:8], 16)

                parsed['COUNT2']=int(payload[8:16], 16)

                binary = bin(int(payload[16:18], 16))[2:].zfill(8)

                parsed['RO1']=binary[0:1]

                parsed['RO2']=binary[1:2]

                parsed['DI3']=binary[2:3]

                parsed['DI2']=binary[3:4]

                parsed['DI1']=binary[4:5]

                parsed['DO3']=binary[5:6]

                parsed['DO2']=binary[6:7]

                parsed['DO1']=binary[7:8]

            if mod == 3 :

                logging.debug('MOD3')

                parsed['mod'] = 3

                parsed['COUNT1']=int(payload[0:8], 16)

                parsed['ACI1']=int(payload[8:12], 16) / 1000

                parsed['ACI2']=int(payload[12:16], 16) / 1000

                binary = bin(int(payload[16:18], 16))[2:].zfill(8)

                parsed['RO1']=binary[0:1]

                parsed['RO2']=binary[1:2]

                parsed['DI3']=binary[2:3]

                parsed['DI2']=binary[3:4]

                parsed['DI1']=binary[4:5]

                parsed['DO3']=binary[5:6]

                parsed['DO2']=binary[6:7]

                parsed['DO1']=binary[7:8]

            if mod == 4 :

                logging.debug('MOD4')

                parsed['mod'] = 4

                parsed['COUNT1']=int(payload[0:8], 16)

                parsed['AVI1COUNT']=int(payload[8:16], 16)

                binary = bin(int(payload[16:18], 16))[2:].zfill(8)

                parsed['RO1']=binary[0:1]

                parsed['RO2']=binary[1:2]

                parsed['DI3']=binary[2:3]

                parsed['DI2']=binary[3:4]

                parsed['DI1']=binary[4:5]

                parsed['DO3']=binary[5:6]

                parsed['DO2']=binary[6:7]

                parsed['DO1']=binary[7:8]

            if mod == 5 :

                logging.debug('MOD5')

                parsed['mod'] = 5

                parsed['AVI1']=int(payload[0:4], 16) / 1000

                parsed['AVI2']=int(payload[4:8], 16) / 1000

                parsed['ACI1']=int(payload[8:12], 16) / 1000

                parsed['COUNT1']=int(payload[12:16], 16)

                binary = bin(int(payload[16:18], 16))[2:].zfill(8)

                parsed['RO1']=binary[0:1]

                parsed['RO2']=binary[1:2]

                parsed['DI3']=binary[2:3]

                parsed['DI2']=binary[3:4]

                parsed['DI1']=binary[4:5]

                parsed['DO3']=binary[5:6]

                parsed['DO2']=binary[6:7]

                parsed['DO1']=binary[7:8]

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(dragino_LT_22222)



# --- Source: dragino_LWL02.py ---

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

import time

import json

import threading



class dragino_LWL02():

    def __init__(self):

        self.name = 'dragino_LWL02'



    def parse(self,data,device):

        logging.debug('dragino_LWL02 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            logging.debug(payload)

            # Battery

            parsed['BAT'] = float(int(hex( (dataarray[0]<<8) | dataarray[1]),16) & 0x3FFF) / 1000

            logging.debug(parsed['BAT'])

            # Status

            status = dataarray[0] & 0x40

            if status == 64:

                parsed['status'] = 1

            else:

                parsed['status'] = 0

            logging.debug(parsed['status'])

            # Mod

            parsed['mod'] = dataarray[2]

            logging.debug(parsed['mod'])

            # Water Leak Times

            parsed['water_leak_times'] = dataarray[3]<<16 | dataarray[4]<<8 | dataarray[5];

            logging.debug(parsed['water_leak_times'])

            # Water Leak Duration

            parsed['water_leak_duration'] = dataarray[6]<<16 | dataarray[7]<<8 | dataarray[8];

            logging.debug(parsed['water_leak_duration'])

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(dragino_LWL02)



# --- Source: dragino_RS485_BL_TUF2000.py ---

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

import time

import json

import threading



class dragino_RS485_BL_TUF2000():

    def __init__(self):

        self.name = 'dragino_RS485_BL_TUF2000'



    def parse(self,data,device):

        logging.debug('dragino_RS485 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            logging.debug('Parsing')

            payload = data['payload']

            parsed['FLOWRATE'] = struct.unpack('!f', bytes.fromhex(payload[10:14]+payload[6:10]))[0]

            parsed['ENERGYFLOWRATE'] = struct.unpack('!f', bytes.fromhex(payload[18:22]+payload[14:18]))[0]

            parsed['NETACCUMULATOR'] = int(payload[26:30]+payload[22:26], 16)

            parsed['NETENERGYACCUMULATOR'] = int(payload[34:38]+payload[30:34], 16)

            parsed['TEMPERATURE1'] = struct.unpack('!f', bytes.fromhex(payload[42:46]+payload[38:42]))[0]

            parsed['SIGNALQUALITY'] = int(payload[48:50], 16)

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(dragino_RS485_BL_TUF2000)



# --- Source: dragino_RS485_LN_EM540.py ---

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

import time

import json

import threading



class dragino_RS485_LN_EM540():

    def __init__(self):

        self.name = 'dragino_RS485_LN_EM540'



    def parse(self,data,device):

        logging.debug('dragino_RS485 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            logging.debug('Parsing')

            payload = data['payload']

            parsed['VOLTAGE1'] = int(payload[0:4], 16) * 10

            parsed['VOLTAGE2'] = int(payload[4:8], 16) * 10

            parsed['VOLTAGE3'] = int(payload[8:12], 16) * 10

            parsed['TotalVOLTAGE'] = int(payload[12:16], 16) * 10

            parsed['CURRENT1'] = int(payload[16:20], 16) * 1000

            parsed['CURRENT2'] = int(payload[20:24], 16) * 1000

            parsed['CURRENT3'] = int(payload[24:28], 16) * 1000

            parsed['POWER1'] = int(payload[28:32], 16) * 10

            parsed['POWER2'] = int(payload[32:36], 16) * 10

            parsed['POWER3'] = int(payload[36:40], 16) * 10

            parsed['TotalPOWER'] = int(payload[40:44], 16) * 10

            parsed['TotalCONSO'] = int(payload[44:48], 16) * 10



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(dragino_RS485_LN_EM540)



# --- Source: dragino_RS485_LN_NILAN.py ---

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

import time

import json

import threading



class dragino_RS485_LN_NILAN():

    def __init__(self):

        self.name = 'dragino_RS485_LN_NILAN'



    def parse(self,data,device):

        logging.debug('dragino_RS485 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            logging.debug('Parsing')

            payload = data['payload']

            tempAmb = int(payload[2:6], 16)

            if tempAmb != 65535:

                if tempAmb > 32767:

                    tempAmb = tempAmb - 65536

                parsed['tempAmb'] = tempAmb / 100

            tempConsigne = int(payload[6:10], 16)

            if tempConsigne != 65535:

                parsed['tempConsigne'] = tempConsigne / 100

            tempExt = int(payload[10:14], 16)

            if tempExt != 65535:

                if tempExt > 32767:

                    tempExt = tempExt - 65536

                parsed['tempExt'] = tempExt / 100

            parsed['alarm'] = int(payload[14:18], 16)



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(dragino_RS485_LN_NILAN)



# --- Source: dragino_RS485_LN_OTMetricPolier.py ---

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

import time

import json

import threading



class dragino_RS485_LN_OTMetricPolier():

    def __init__(self):

        self.name = 'dragino_RS485_LN_OTMetricPolier'



    def parse(self,data,device):

        logging.debug('dragino_RS485_LN_OTMetricPolier Received')

        parsed={}

        data['parsed'] = parsed

        try:

            logging.debug('Parsing')

            payload = data['payload']

            parsed['VOLTAGE1'] = int(payload[2:8], 16) / 1000

            parsed['VOLTAGE2'] = int(payload[8:14], 16) / 1000

            parsed['VOLTAGE3'] = int(payload[14:20], 16) / 1000

            parsed['CURRENT1'] = int(payload[20:26], 16) / 1000

            parsed['CURRENT2'] = int(payload[26:32], 16) / 1000

            parsed['CURRENT3'] = int(payload[32:38], 16) / 1000

            parsed['TotalPOWER'] = int(payload[38:48], 16) / 1000

            parsed['TotalCONSO'] = int(payload[48:58], 16) / 10000

            logging.debug('TotalCONSO : ' + payload[48:58])

            parsed['PolierTension'] = int(payload[68:74], 16)

            parsed['PolierCourant'] = int(payload[74:80], 16)

            parsed['PolierPower'] = int(payload[80:86], 16)

            parsed['PolierConso'] = int(payload[86:92], 16)



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(dragino_RS485_LN_OTMetricPolier)



# --- Source: dragino_RS485_LN_PZEM_004T.py ---

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

import time

import json

import threading



class dragino_RS485_LN_PZEM_004T():

    def __init__(self):

        self.name = 'dragino_RS485_LN_PZEM_004T'



    def parse(self,data,device):

        logging.debug('dragino_RS485 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            logging.debug('Parsing')

            payload = data['payload']

            parsed['VOLTAGE1'] = int(payload[2:6], 16) / 10

            parsed['CURRENT1'] = int(payload[10:14]+payload[6:10], 16) / 1000

            parsed['POWER1'] = int(payload[18:22]+payload[14:18], 16) / 10

            parsed['ENERGY1'] = int(payload[26:30]+payload[22:26], 16)

            parsed['FREQUENCY1'] = int(payload[30:34], 16) / 10

            parsed['POWERFACTOR1'] = int(payload[34:38], 16) / 100

            parsed['ALARM1'] = int(payload[38:42], 16)

            parsed['VOLTAGE2'] = int(payload[42:46], 16) / 10

            parsed['CURRENT2'] = int(payload[50:54]+payload[46:50], 16) / 1000

            parsed['POWER2'] = int(payload[58:62]+payload[54:58], 16) / 10

            parsed['ENERGY2'] = int(payload[66:70]+payload[62:66], 16)

            parsed['FREQUENCY2'] = int(payload[70:74], 16) / 10

            parsed['POWERFACTOR2'] = int(payload[74:78], 16) / 100

            parsed['ALARM2'] = int(payload[78:82], 16)

            parsed['VOLTAGE3'] = int(payload[82:86], 16) / 10

            parsed['CURRENT3'] = int(payload[90:94]+payload[86:90], 16) / 1000

            parsed['POWER3'] = int(payload[98:102]+payload[94:98], 16) / 10

            parsed['ENERGY3'] = int(payload[106:110]+payload[102:106], 16)

            parsed['FREQUENCY3'] = int(payload[110:114], 16) / 10

            parsed['POWERFACTOR3'] = int(payload[114:118], 16) / 100

            parsed['ALARM3'] = int(payload[118:122], 16)

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(dragino_RS485_LN_PZEM_004T)



# --- Source: dragino_SW3L.py ---

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

import time

import json

import threading



class dragino_SW3L():

    def __init__(self):

        self.name = 'dragino_SW3L'



    def parse(self,data,device):

        logging.debug('dragino_SW3L Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            binary1 = bin(int(payload[0:2],16))[2:].zfill(8)

            CF = (int(payload[0:2], 16) & 0xFC) >> 2

            if CF == 0 :

                parsed['calculateFlag'] = 450

            elif CF == 1 :

                parsed['calculateFlag'] = 390

            elif CF == 2 :

                parsed['calculateFlag'] = 64

            parsed['alarm'] = binary1[6:7]

            mod = int(payload[10:12],16)

            if mod == 0 :

                parsed['totalPulse'] = int(payload[2:10],16)

                parsed['totalWFVolume'] =  parsed['totalPulse'] / parsed['calculateFlag']

            elif mod == 1 :

                parsed['lastPulse'] = int(payload[2:10],16)

                parsed['totalWFtdc'] = parsed['lastPulse'] / parsed['calculateFlag']

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(dragino_SW3L)



# --- Source: dry_contacts.py ---

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

import time

import json

import threading

import datetime



class dry_contacts():

    def __init__(self):

        self.name = 'dry_contacts'



    def parse(self,data,device):

        logging.debug('dry_contacts Received')

        parsed={}

        data['parsed'] = parsed

        try:



            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')



            parsed['frameCode'] = str(hex(dataarray[0])[2:].zfill(2))



            # KEEP ALIVE FRAME 0x30

            if parsed['frameCode'] == '30':

                logging.debug('Keep Alive Frame') # 30

                logging.debug('Frame code : ' + str(parsed['frameCode']))



                # Offset 1

                statusByte = bin(int(str(dataarray[1])))[2:].zfill(8)

                parsed['frameCounter'] = int(statusByte[0:3],2)

                logging.debug('Frame counter : ' + str(parsed['frameCounter']))

                parsed['lowBat'] = statusByte[6]

                logging.debug('Low Bat : ' + str(parsed['lowBat']))



                # Offset 2,3

                binary2 = ''

                for x in range(2,4):

                    binary2 = binary2 + str(hex(dataarray[x])[2:].zfill(2))

                parsed['channel1EventCount'] = int(binary2,16)

                logging.debug(str(parsed['channel1EventCount']) + ' events detected on CH1')



                # Offset 4,5

                binary4 = ''

                for x in range(4,6):

                    binary4 = binary4 + str(hex(dataarray[x])[2:].zfill(2))

                parsed['channel2EventCount'] = int(binary4,16)

                logging.debug(str(parsed['channel2EventCount']) + ' events detected on CH2')



                # Offset 6,7

                binary6 = ''

                for x in range(6,8):

                    binary6 = binary6 + str(hex(dataarray[x])[2:].zfill(2))

                parsed['channel3EventCount'] = int(binary6,16)

                logging.debug(str(parsed['channel3EventCount']) + ' events detected on CH3')



                # Offset 8,9

                binary8 = ''

                for x in range(8,10):

                    binary8 = binary8 + str(hex(dataarray[x])[2:].zfill(2))

                parsed['channel4EventCount'] = int(binary8,16)

                logging.debug(str(parsed['channel4EventCount']) + ' events detected on CH4')



                # Offset 10

                binary10 = bin(int(str(dataarray[10])))[2:].zfill(8)

                channel1State = binary10[7]

                channel2State = binary10[6]

                channel3State = binary10[5]

                channel4State = binary10[4]

                parsed['channel1State'] = 'ON' if channel1State == '1' else 'OFF'

                parsed['channel2State'] = 'ON' if channel2State == '1' else 'OFF'

                parsed['channel3State'] = 'ON' if channel3State == '1' else 'OFF'

                parsed['channel4State'] = 'ON' if channel4State == '1' else 'OFF'

                logging.debug('Channel 1 current state : ' + str(parsed['channel1State']))

                logging.debug('Channel 2 current state : ' + str(parsed['channel2State']))

                logging.debug('Channel 3 current state : ' + str(parsed['channel3State']))

                logging.debug('Channel 4 current state : ' + str(parsed['channel4State']))



            # DATA FRAME 0x40

            if parsed['frameCode'] == '40':

                logging.debug('Data Frame') # 40

                logging.debug('Frame code : ' + str(parsed['frameCode']))



                # Offset 1

                statusByte = bin(int(str(dataarray[1])))[2:].zfill(8)

                parsed['frameCounter'] = int(statusByte[0:3],2)

                logging.debug('Frame counter : ' + str(parsed['frameCounter']))

                parsed['lowBat'] = statusByte[6]

                logging.debug('Low Bat : ' + str(parsed['lowBat']))



                # Offset 2,3

                binary2 = ''

                for x in range(2,4):

                    binary2 = binary2 + str(hex(dataarray[x])[2:].zfill(2))

                parsed['channel1Value'] = int(binary2,16)

                logging.debug('Channel 1 Value : ' + str(parsed['channel1Value']))



                # Offset 4,5

                binary4 = ''

                for x in range(4,6):

                    binary4 = binary4 + str(hex(dataarray[x])[2:].zfill(2))

                parsed['channel2Value'] = int(binary4,16)

                logging.debug('Channel 2 Value : ' + str(parsed['channel2Value']))



                # Offset 6,7

                binary6 = ''

                for x in range(6,8):

                    binary6 = binary6 + str(hex(dataarray[x])[2:].zfill(2))

                parsed['channel3Value'] = int(binary6,16)

                logging.debug('Channel 3 Value : ' + str(parsed['channel3Value']))



                # Offset 8,9

                binary8 = ''

                for x in range(8,10):

                    binary8 = binary8 + str(hex(dataarray[x])[2:].zfill(2))

                parsed['channel4Value'] = int(binary8,16)

                logging.debug('Channel 4 Value : ' + str(parsed['channel4Value']))



                # Offset 10

                binary10 = bin(int(str(dataarray[10])))[2:].zfill(8)

                channel1CurrentState = binary10[7]

                channel1LastState = binary10[6]

                channel2CurrentState = binary10[5]

                channel2LastState = binary10[4]

                channel3CurrentState = binary10[3]

                channel3LastState = binary10[2]

                channel4CurrentState = binary10[1]

                channel4LastState = binary10[0]

                parsed['channel1CurrentState'] = 'ON' if channel1CurrentState == '1' else 'OFF'

                parsed['channel1LastState'] = 'ON' if channel1LastState == '1' else 'OFF'

                parsed['channel2CurrentState'] = 'ON' if channel2CurrentState == '1' else 'OFF'

                parsed['channel2LastState'] = 'ON' if channel2LastState == '1' else 'OFF'

                parsed['channel3CurrentState'] = 'ON' if channel3CurrentState == '1' else 'OFF'

                parsed['channel3LastState'] = 'ON' if channel3LastState == '1' else 'OFF'

                parsed['channel4CurrentState'] = 'ON' if channel4CurrentState == '1' else 'OFF'

                parsed['channel4LastState'] = 'ON' if channel4LastState == '1' else 'OFF'

                logging.debug('Channel 1 current state : ' + str(parsed['channel1CurrentState']) + ' , last state : ' + str(parsed['channel1LastState']))

                logging.debug('Channel 2 current state : ' + str(parsed['channel2CurrentState']) + ' , last state : ' + str(parsed['channel2LastState']))

                logging.debug('Channel 3 current state : ' + str(parsed['channel3CurrentState']) + ' , last state : ' + str(parsed['channel3LastState']))

                logging.debug('Channel 4 current state : ' + str(parsed['channel4CurrentState']) + ' , last state : ' + str(parsed['channel4LastState']))



            # TIME COUNTING FRAME 0x59

            if parsed['frameCode'] == '59':

                logging.debug('Time Counting Frame') # 59

                logging.debug('Frame code : ' + str(parsed['frameCode']))



                # Offset 1

                statusByte = bin(int(str(dataarray[1])))[2:].zfill(8)

                parsed['frameCounter'] = int(statusByte[0:3],2)

                logging.debug('Frame counter : ' + str(parsed['frameCounter']))

                parsed['lowBat'] = statusByte[6]

                logging.debug('Low Bat : ' + str(parsed['lowBat']))

                parsed['timestampStatus'] = statusByte[5]

                logging.debug('Status Timestamp : ' + str(parsed['timestampStatus']))



                # Offset 2

                binary2 = bin(int(str(dataarray[2])))[2:].zfill(8) # 0000 0101

                channels = []

                for x in range(4,8):

                    if binary2[x] == '1':

                        if x == 7:

                            channels.append('1')

                        elif x == 6:

                            channels.append('2')

                        elif x == 5:

                            channels.append('3')

                        elif x == 4:

                            channels.append('4')

                nbCounters = len(channels)

                parsed['includedChannels'] = " & ".join(channels)

                logging.debug('Channels included in the frame : ' + str(parsed['includedChannels']))



                if nbCounters == 2:

                    # Offset 3..6

                    binary3 = ''

                    for x in range(3,6):

                        binary3 = binary3 + str(hex(dataarray[x])[2:].zfill(2)) # 012345

                    parsed['firstCounter'] = int(binary3,16)

                    logging.debug('First Counter : ' + str(parsed['firstCounter']) + ' s') # 74565



                    # Offset 7..10

                    binary7 = ''

                    for x in range(6,9):

                        binary7 = binary7 + str(hex(dataarray[x])[2:].zfill(2)) # 001100

                    parsed['secondCounter'] = int(binary7,16)

                    logging.debug('Second Counter : ' + str(parsed['secondCounter']) + ' s') # 4352



                # Offset 11..14

                binary11 = ''

                for x in range(9,13):

                    binary11 = binary11 + str(hex(dataarray[x])[2:].zfill(2))

                logging.debug(binary11) # 126B94F9



                parsed['timestamp'] = datetime.datetime.utcfromtimestamp(309040377).strftime('%Y-%m-%d %H:%M:%S')

                logging.debug('Timestamp GMT : ' + str(parsed['timestamp']))

                # 1979-10-17 20:32:57 https://www.epochconverter.com/

                # 2022-10-17 20:32:57



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(dry_contacts)



# --- Source: eastron_sdm630.py ---

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

import time

import json

import threading

from binascii import unhexlify



class eastron_sdm630():

    def __init__(self):

        self.name = 'eastron_sdm630'



    def parse(self,data,device):

        logging.debug('eastron_sdm630 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            payload = data['payload']

            logging.debug('Parsing')



            def bytes_to_float(bytes):

                bits = (bytes[0] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3]

                sign = 1.0 if (bits >> 31) == 0 else -1.0

                e = (bits >> 23) & 0xff

                m = ((bits & 0x7fffff) << 1) if e == 0 else (bits & 0x7fffff) | 0x800000

                f = sign * m * (2 ** (e - 150))

                return float(f)



            def hex_to_bytes(hex_string):

                bytes_array = []

                for c in range(0, len(hex_string), 2):

                    bytes_array.append(int(hex_string[c:c+2], 16))

                return bytes_array



            if len(payload) == 56:

                logging.debug('Default Config')

                parsed['serialNumber'] = int(payload[0:8], 16)

                parsed['totalEnergy'] = bytes_to_float(hex_to_bytes(payload[12:20]))

                parsed['frequency'] = bytes_to_float(hex_to_bytes(payload[20:28]))

                parsed['totalPowerFactor'] = bytes_to_float(hex_to_bytes(payload[28:36]))

                parsed['maximumTotalSystemPowerDemand'] = bytes_to_float(hex_to_bytes(payload[36:44]))

                parsed['totalCurrent'] = bytes_to_float(hex_to_bytes(payload[44:52]))



            if len(payload) == 80: # 8 configs en même temps

                logging.debug('special config')

                parsed['serialNumber'] = int(payload[0:8], 16)

                parsed['config'] = int(payload[8:10], 16)

                parsed['nbParameters'] = int(payload[10:12], 16)

                parsed['L1'] = bytes_to_float(hex_to_bytes(payload[12:20]))

                parsed['L2'] = bytes_to_float(hex_to_bytes(payload[20:28]))

                parsed['L3'] = bytes_to_float(hex_to_bytes(payload[28:36]))

                parsed['C1'] = bytes_to_float(hex_to_bytes(payload[36:44]))

                parsed['C2'] = bytes_to_float(hex_to_bytes(payload[44:52]))

                parsed['C3'] = bytes_to_float(hex_to_bytes(payload[52:60]))

                parsed['AP'] = bytes_to_float(hex_to_bytes(payload[60:68]))

                parsed['TC'] = bytes_to_float(hex_to_bytes(payload[68:76]))



            if len(payload) == 40: # 3 configs en même temps

                logging.debug('special config')

                parsed['serialNumber'] = int(payload[0:8], 16)

                config = int(payload[8:10], 16)

                if config == 1:

                    logging.debug('Payload 1')

                    parsed['L1'] = bytes_to_float(hex_to_bytes(payload[12:20]))

                    parsed['L2'] = bytes_to_float(hex_to_bytes(payload[20:28]))

                    parsed['L3'] = bytes_to_float(hex_to_bytes(payload[28:36]))

                if config == 2:

                    logging.debug('Payload 2')

                    parsed['C1'] = bytes_to_float(hex_to_bytes(payload[12:20]))

                    parsed['C2'] = bytes_to_float(hex_to_bytes(payload[20:28]))

                    parsed['C3'] = bytes_to_float(hex_to_bytes(payload[28:36]))

                if config == 3:

                    logging.debug('Payload 3')

                    parsed['P1'] = bytes_to_float(hex_to_bytes(payload[12:20]))

                    parsed['P2'] = bytes_to_float(hex_to_bytes(payload[20:28]))

                    parsed['P3'] = bytes_to_float(hex_to_bytes(payload[28:36]))

                if config == 4:

                    logging.debug('Payload 4')

                    parsed['TAP'] = bytes_to_float(hex_to_bytes(payload[12:20]))

                    parsed['L1C'] = bytes_to_float(hex_to_bytes(payload[20:28]))

                    parsed['L2C'] = bytes_to_float(hex_to_bytes(payload[28:36]))

                if config == 5:

                    logging.debug('Payload 5')

                    parsed['L3C'] = bytes_to_float(hex_to_bytes(payload[12:20]))

                    parsed['TC'] = bytes_to_float(hex_to_bytes(payload[20:28]))

                    parsed['FR'] = bytes_to_float(hex_to_bytes(payload[28:36]))





        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(eastron_sdm630)



# --- Source: elsys.py ---

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

import time

import json

import threading

from binascii import unhexlify



def bin8dec(bin) :

    num=bin&0xFF

    if (0x80 & num):

        num = - (0x0100 - num)

    return num



class elsys():

    def __init__(self):

        self.name = 'elsys'



    def parse(self,data,device):

        # https://www.elsys.se/en/elsys-payload/

        logging.debug('Elsys Received')

        TYPE_TEMP = 0x01; #temp 2 bytes -3276.8°C -->3276.7°C

        TYPE_RH = 0x02; #Humidity 1 byte  0-100%

        TYPE_ACC = 0x03; #acceleration 3 bytes X,Y,Z -128 --> 127 +/-63=1G

        TYPE_LIGHT = 0x04; #Light 2 bytes 0-->65535 Lux

        TYPE_MOTION = 0x05; #No of motion 1 byte  0-255

        TYPE_CO2 = 0x06; #Co2 2 bytes 0-65535 ppm

        TYPE_VDD = 0x07; #VDD 2byte 0-65535mV

        TYPE_ANALOG1 = 0x08; #VDD 2byte 0-65535mV

        TYPE_GPS = 0x09; #3bytes lat 3bytes long binary

        TYPE_PULSE1 = 0x0A; #2bytes relative pulse count

        TYPE_PULSE1_ABS = 0x0B; #4bytes no 0->0xFFFFFFFF

        TYPE_EXT_TEMP1 = 0x0C; #2bytes -3276.5C-->3276.5C

        TYPE_EXT_DIGITAL = 0x0D; #1bytes value 1 or 0

        TYPE_EXT_DISTANCE = 0x0E; #2bytes distance in mm

        TYPE_ACC_MOTION = 0x0F; #1byte number of vibration/motion

        TYPE_IR_TEMP = 0x10; #2bytes internal temp 2bytes external temp -3276.5C-->3276.5C

        TYPE_OCCUPANCY = 0x11; #1byte data

        TYPE_WATERLEAK = 0x12; #1byte data 0-255

        TYPE_GRIDEYE = 0x13; #65byte temperature data 1byte ref+64byte external temp

        TYPE_PRESSURE = 0x14; #4byte pressure data (hPa)

        TYPE_SOUND = 0x15; #2byte sound data (peak/avg)

        TYPE_PULSE2 = 0x16; #2bytes 0-->0xFFFF

        TYPE_PULSE2_ABS = 0x17; #4bytes no 0->0xFFFFFFFF

        TYPE_ANALOG2 = 0x18; #2bytes voltage in mV

        TYPE_EXT_TEMP2 = 0x19; #2bytes -3276.5C-->3276.5C

        TYPE_EXT_DIGITAL2 = 0x1A; # 1bytes value 1 or 0

        TYPE_EXT_ANALOG_UV = 0x1B; # 4 bytes signed int (uV)

        TYPE_DEBUG = 0x3D; # 4bytes debug

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            i=0

            while i+1 < len(dataarray):

                if (i!=0):

                    i+=1

                if dataarray[i] == TYPE_TEMP: #Temperature

                    parsed['temperature'] = float((dataarray[i + 1] << 8) | (dataarray[i + 2])) /10

                    i += 2

                    continue

                elif dataarray[i] == TYPE_RH: #humidity

                    parsed['humidity'] = dataarray[i + 1]

                    i += 1

                    continue

                elif dataarray[i] == TYPE_ACC: #Acceleration

                    parsed['x'] = bin8dec(dataarray[i + 1])

                    parsed['y'] = bin8dec(dataarray[i + 2])

                    parsed['z'] = bin8dec(dataarray[i + 3])

                    i += 3

                    continue

                elif dataarray[i] == TYPE_LIGHT: #Light

                    parsed['luminosity'] = (dataarray[i + 1] << 8) | (dataarray[i + 2])

                    i += 2

                    continue

                elif dataarray[i] == TYPE_MOTION: #Motion

                    parsed['motion'] = dataarray[i + 1]

                    i += 1

                    continue

                elif dataarray[i] == TYPE_CO2: #Co2

                    parsed['co2'] = (dataarray[i + 1] << 8) | (dataarray[i + 2])

                    i += 2

                    continue

                elif dataarray[i] == TYPE_VDD: #Battery

                    parsed['battery'] = (dataarray[i + 1] << 8) | (dataarray[i + 2])

                    i += 2

                    continue

                elif dataarray[i] == TYPE_ANALOG1: #Analog1

                    parsed['analog1'] = (dataarray[i + 1] << 8) | (dataarray[i + 2])

                    i += 2

                    continue

                elif dataarray[i] == TYPE_GPS: #GPS   TODO

                    i += 5

                    continue

                elif dataarray[i] == TYPE_PULSE1: #Pulse 1

                    parsed['pulse1'] = (dataarray[i + 1] << 8) | (dataarray[i + 2])

                    i += 2

                    continue

                elif dataarray[i] == TYPE_PULSE1_ABS: #Puls abs

                    parsed['pulse1abs'] = (dataarray[i + 1] << 24) | (dataarray[i + 2] << 16) | (dataarray[i + 3] << 8) | (dataarray[i + 4])

                    i += 4

                    continue

                elif dataarray[i] == TYPE_EXT_TEMP1: #Ext temp 1

                    parsed['tempext1'] = float((dataarray[i + 1] << 8) | (dataarray[i + 2]))/10

                    i += 2

                    continue

                elif dataarray[i] == TYPE_EXT_DIGITAL: #Digital input

                    parsed['digital'] = dataarray[i + 1]

                    i += 1

                    continue

                elif dataarray[i] == TYPE_EXT_DISTANCE: #Distance

                    parsed['distance'] = (dataarray[i + 1] << 8) | (dataarray[i + 2])

                    i += 2

                    continue

                elif dataarray[i] == TYPE_ACC_MOTION: #Acc motion

                    parsed['accmotion'] = dataarray[i + 1]

                    i += 1

                    continue

                elif dataarray[i] == TYPE_IR_TEMP: #IR TEMP  TODO

                    i += 4

                    continue

                elif dataarray[i] == TYPE_OCCUPANCY: #occupancy

                    parsed['occupancy'] = dataarray[i + 1]

                    i += 1

                    continue

                elif dataarray[i] == TYPE_WATERLEAK: #waterleak

                    parsed['leak'] = dataarray[i + 1]

                    i += 1

                    continue

                elif dataarray[i] == TYPE_GRIDEYE: #grideye TODO

                    i += 64

                    continue

                elif dataarray[i] == TYPE_PRESSURE: #pressure

                    parsed['pressure'] = float((dataarray[i + 1] << 24) | (dataarray[i + 2] << 16) | (dataarray[i + 3] << 8) | (dataarray[i + 4]))/1000

                    i += 4

                    continue

                break

        except Exception as e:

                logging.debug(str(e))

                logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(elsys)



# --- Source: enerbee_evav.py ---

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

import time

import json

import threading

from binascii import unhexlify

import datetime



class enerbee_evav():

    def __init__(self):

        self.name = 'enerbee_evav'



    def parse(self,data,device):

        logging.debug('enerbee_evav Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            logging.debug(len(payload))

            length = len(payload)



            idx = 0

            if payload[6:8] == "ff" and payload[8:10] == "ff" :

                logging.debug('Message initial')

                idx = 10



            # First two bytes are data format

            payload_format = int(payload[idx:idx+4], 16)

            idx += 4



            # Third byte in header is the measurement interval in minutes

            interval = int(payload[idx:idx+2], 16)

            idx += 2



            # Calculate block_len

            block_len = 0

            # Temperature

            if (payload_format & 0x0001) != 0:

                block_len += 2

            # Humidity

            if (payload_format & 0x0002) != 0:

                block_len += 2

            # Airflow

            if (payload_format & 0x0004) != 0:

                block_len += 4

            # CO2

            if (payload_format & 0x0008) != 0:

                block_len += 4

            # IAQ

            if (payload_format & 0x0010) != 0:

                block_len += 4

            # Charge

            if (payload_format & 0x0020) != 0:

                block_len += 2

            # Iris position

            if (payload_format & 0x0040) != 0:

                block_len += 2

            # Extended airflow

            if (payload_format & 0x0200) != 0:

                block_len += 2

            # System status

            if (payload_format & 0x0400) != 0:

                block_len += 2



            # Must be a multiple of blocklen

            if (block_len != 0) and (((length-idx) % block_len) == 0):

                blocks = (length-idx) / block_len



                #  Treat each block of data from oldest to most recent

                while idx < length:

                    blocks -= 1



                    #parsed['date'] = dateMessage - datetime.timedelta(minutes=blocks*interval)



                    if (payload_format & 0x0001) != 0:

                        temp = int(payload[idx:idx+2], 16)

                        if temp > 127:

                            temp = 0

                        parsed['temperature'] = temp

                        idx += 2



                    if (payload_format & 0x0002) != 0:

                        parsed['humidity'] = int(payload[idx:idx+2], 16)

                        idx += 2



                    if (payload_format & 0x0004) != 0:

                        parsed['airFlowTarget'] = int(payload[idx:idx+2], 16)

                        idx += 2

                        parsed['airFlowCurrent'] = int(payload[idx:idx+2], 16)

                        idx += 2



                    if (payload_format & 0x0008) != 0:

                        parsed['co2'] = int(payload[idx:idx+4], 16)

                        idx += 4



                    if (payload_format & 0x0010) != 0:

                        parsed['iaq'] = int(payload[idx:idx+4], 16)

                        idx += 4



                    if (payload_format & 0x0020) != 0:

                        parsed['charge'] = int(payload[idx:idx+2], 16)

                        idx += 2



                    if (payload_format & 0x0040) != 0:

                        parsed['register'] = int(payload[idx:idx+2], 16)

                        idx += 2



                    if (payload_format & 0x0200) != 0:

                        ext = int(payload[idx:idx+2], 16)

                        if (payload_format & 0x0004) != 0:

                            parsed['airFlowTarget'] += ((ext & 0x0F) << 8)

                        else :

                            parsed['airFlowTarget'] = ((ext & 0x0F) << 8)

                        if (payload_format & 0x0004) != 0:

                            parsed['airFlowCurrent'] += ((ext & 0xF0) << 4)

                        else :

                            parsed['airFlowCurrent'] = ((ext & 0xF0) << 4)

                        idx += 2



                    if (payload_format & 0x0400) != 0:

                        status = int(payload[idx:idx+2], 16)

                        if status == 0:

                            parsed['status'] = 'Non défini'

                        elif status == 1:

                            parsed['status'] = 'Fonctionnement normal'

                        elif status == 2:

                            parsed['status'] = 'En charge'

                        elif status == 3:

                            parsed['status'] = 'Standby'

                        elif status == 4:

                            parsed['status'] = 'Arret'

                        elif status == 5:

                            parsed['status'] = 'Erreur moteur'

                        elif status == 6:

                            parsed['status'] = 'Erreur capteur T/H'

                        elif status == 7:

                            parsed['status'] = "Erreur capteur qualité d'air"

                        idx +=2



            return data



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(enerbee_evav)



# --- Source: enginko_MCFLW13IO.py ---

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

import time

import json

import threading

from binascii import unhexlify



class enginko_MCFLW13IO():

    def __init__(self):

        self.name = 'enginko_MCFLW13IO'



    def parse(self,data,device):

        logging.debug('enginko_MCFLW13IO Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            payload = data['payload']

            logging.debug('Parsing')



            if(payload[0:2] == '0a'):

                datetime = payload[2:10]

                inputs = payload[10:18]

                outputs = payload[18:26]

                inputsEvents = payload[26:34]

                inputState = '1' in inputs

                if inputState:

                    parsed['inputState'] = '1'

                else:

                    parsed['inputState'] = '0'  

                outputState = '1' in outputs

                if outputState:

                    parsed['outputState'] = '1'

                else:

                    parsed['outputState'] = '0'             

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(enginko_MCFLW13IO)



# --- Source: ewattchambiance.py ---

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

import time

import json

import threading

from binascii import unhexlify



class ewattchambiance():

    def __init__(self):

        self.name = 'ewattchambiance'



    def parse(self,data,device):

        logging.debug('Ewattch Ambiance Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            if dataarray[0] == 0x00:

                logging.debug('This is a periodic message')

                parsed['temperature'] = str(int(utils.to_hex_string([dataarray[4],dataarray[3]]),16)/100)

                logging.debug('Temperature is : ' + parsed['temperature'])

                parsed['humidity'] = str(int(utils.to_hex_string([dataarray[6]]),16)/2)

                logging.debug('Humidity is : ' + parsed['humidity'])

                if len(dataarray)>8:

                    parsed['luminosity'] = str(int(utils.to_hex_string([dataarray[9],dataarray[8]]),16))

                    logging.debug('Luminosity is : ' + parsed['luminosity'])

                    parsed['presence'] = str(int(utils.to_hex_string([dataarray[12],dataarray[11]]),16)*10)

                    logging.debug('Presence is : ' + parsed['presence'])

                if len(dataarray)>13 and dataarray[13] == 0x08:

                    parsed['co2'] = str(int(utils.to_hex_string([dataarray[15],dataarray[14]]),16))

                    logging.debug('Co2 is : ' + parsed['co2'])

                    if len(dataarray)>16 and dataarray[16] == 0x0C:

                        parsed['compteur1'] = str(int(utils.to_hex_string([dataarray[18],dataarray[17]]),16))

                        parsed['compteur2'] = str(int(utils.to_hex_string([dataarray[22],dataarray[21]]),16))

                        parsed['compteur3'] = str(int(utils.to_hex_string([dataarray[26],dataarray[25]]),16))

                if len(dataarray)>13 and dataarray[13] == 0x0C:

                    parsed['compteur1'] = str(int(utils.to_hex_string([dataarray[15],dataarray[14]]),16))

                    parsed['compteur2'] = str(int(utils.to_hex_string([dataarray[19],dataarray[18]]),16))

                    parsed['compteur3'] = str(int(utils.to_hex_string([dataarray[23],dataarray[22]]),16))

            elif dataarray[0] == 0x10:

                logging.debug('This is a state message')

                parsed['batterylevel'] = utils.to_hex_string([dataarray[8]])

                logging.debug('Battery level is : ' + parsed['batterylevel'])

                if parsed['batterylevel'] == '0':

                    parsed['battery'] = 0

                elif parsed['batterylevel'] == '1':

                    parsed['battery'] = 25

                elif parsed['batterylevel'] == '2':

                    parsed['battery'] = 50

                elif parsed['batterylevel'] == '7':

                    parsed['battery'] = 100

                elif parsed['batterylevel'] == '8':

                    parsed['battery'] = 100

            else:

                logging.debug('Unknown message')

                return data

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(ewattchambiance)



# --- Source: ewattchsquid.py ---

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

import time

import json

import threading

from binascii import unhexlify



class ewattchsquid():

    def __init__(self):

        self.name = 'ewattchsquid'



    def parse(self,data,device):

        logging.debug('Ewattch Squid')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            logging.debug(dataarray[2])

            if dataarray[2] == 0x48:

                logging.debug('Ewattch Squid')

                if dataarray[0] == 0x00:

                    logging.debug('This is a periodic message')

                    raw1=str(int(utils.to_hex_string([dataarray[5],dataarray[4],dataarray[3]]),16))

                    logging.debug('Channel1 : ' + raw1)

                    parsed['channel1'] = float(raw1)/100

                    raw2=str(int(utils.to_hex_string([dataarray[8],dataarray[7],dataarray[6]]),16))

                    logging.debug('Channel2 : ' + raw2)

                    parsed['channel2'] = float(raw2)/100

                    raw3=str(int(utils.to_hex_string([dataarray[11],dataarray[10],dataarray[9]]),16))

                    logging.debug('Channel3 : ' + raw3)

                    parsed['channel3'] = float(raw3)/100

                    raw4=str(int(utils.to_hex_string([dataarray[14],dataarray[13],dataarray[12]]),16))

                    logging.debug('Channel4 : ' + raw4)

                    parsed['channel4'] = float(raw4)/100

                    raw5=str(int(utils.to_hex_string([dataarray[17],dataarray[16],dataarray[15]]),16))

                    logging.debug('Channel5 : ' + raw5)

                    parsed['channel5'] = float(raw5)/100

                    raw6=str(int(utils.to_hex_string([dataarray[20],dataarray[19],dataarray[18]]),16))

                    logging.debug('Channel6 : ' + raw6)

                    parsed['channel6'] = float(raw6)/100

                    raw7=str(int(utils.to_hex_string([dataarray[23],dataarray[22],dataarray[21]]),16))

                    logging.debug('Channel7 : ' + raw7)

                    parsed['channel7'] = float(raw7)/100

                    raw8=str(int(utils.to_hex_string([dataarray[26],dataarray[25],dataarray[24]]),16))

                    logging.debug('Channel8 : ' + raw8)

                    parsed['channel8'] = float(raw8)/100

                    raw9=str(int(utils.to_hex_string([dataarray[29],dataarray[28],dataarray[27]]),16))

                    logging.debug('Channel9 : ' + raw9)

                    parsed['channel9'] = float(raw9)/100

                    raw10=str(int(utils.to_hex_string([dataarray[32],dataarray[31],dataarray[30]]),16))

                    logging.debug('Channel10 : ' + raw10)

                    parsed['channel10'] = float(raw10)/100

                    raw11=str(int(utils.to_hex_string([dataarray[35],dataarray[34],dataarray[33]]),16))

                    logging.debug('Channel11 : ' + raw11)

                    parsed['channel11'] = float(raw11)/100

                    raw12=str(int(utils.to_hex_string([dataarray[38],dataarray[37],dataarray[36]]),16))

                    logging.debug('Channel12 : ' + raw12)

                    parsed['channel12'] = float(raw12)/100

            else:

                logging.debug('Unknown message')

                return data

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(ewattchsquid)



# --- Source: ewattchsquidprorogowski.py ---

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

import time

import json

import threading

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



# --- Source: ewattchtyness.py ---

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

import time

import json

import threading

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



# --- Source: ewattch_ambianceCO2.py ---

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

import time

import json

import threading

from binascii import unhexlify



class ewattch_ambianceCO2():

    def __init__(self):

        self.name = 'ewattch_ambianceCO2'



    def parse(self,data,device):

        logging.debug('Ewattch Ambiance CO2 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            def convertHex(value):

               little_hex = bytearray.fromhex(value)

               little_hex.reverse()

               hex_string = ''.join(format(x, '02x') for x in little_hex)

               #logging.debug(hex_string)

               return hex_string



            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']



            if payload[0:2] == "00":

                logging.debug('This is a periodic message')

                parsed['temperature'] = int(convertHex(payload[6:10]), 16)/100

                parsed['humidity'] = int(payload[12:14], 16)/2

                parsed['luminosity'] = int(convertHex(payload[16:20]), 16)

                parsed['presence'] = int(convertHex(payload[22:26]), 16)*10

                parsed['co2'] = int(convertHex(payload[28:32]), 16)



            elif payload[0:2] == "10":

                logging.debug('This is a state message')

                batterylevel = payload[16:18]

                logging.debug(batterylevel)

                if batterylevel == '08':

                    parsed['battery'] = 100

                elif batterylevel == '07':

                    parsed['battery'] = 75

                elif batterylevel == '02':

                    parsed['battery'] = 50

                elif batterylevel == '01':

                    parsed['battery'] = 25

                elif batterylevel == '00':

                    parsed['battery'] = 0



            else:

                logging.debug('Unknown message')

                return data

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(ewattch_ambianceCO2)



# --- Source: globalsat_S11x.py ---

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

import time

import json

import threading

import binascii

from binascii import unhexlify



class globalsat_S11x():

    def __init__(self):

        self.name = 'globalsat_S11x'



    def parse(self,data):

        logging.debug('globalsat_S11x Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')



            # Device Type

            binary0 = ''

            for x in range(0,1):

               binary0 = binary0 + str(hex(dataarray[x])[2:].zfill(2))

            if binary0 == '01':

               parsed['deviceType'] = 'CO2'

            elif binary0 == '02':

               parsed['deviceType'] = 'CO'

            elif binary0 == '03':

               parsed['deviceType'] = 'PM2.5'

            logging.debug('Device Type : ' + parsed['deviceType'])



            # Temperature

            binary1 = ''

            for x in range(1,3):

               binary1 = binary1 + str(hex(dataarray[x])[2:].zfill(2)) # 0961

            parsed['temperature'] = (int(binary1, 16))/100 # 24.01

            logging.debug('Temperature : ' + str(parsed['temperature']))



            # Humidity

            binary2 = ''

            for x in range(3,5):

               binary2 = binary2 + str(hex(dataarray[x])[2:].zfill(2)) # 1395

            parsed['humidity'] = (int(binary2, 16))/100 # 50.13

            logging.debug('Humidity : ' + str(parsed['humidity']))



            # Density

            binary3 = ''

            for x in range(5,7):

               binary3 = binary3 + str(hex(dataarray[x])[2:].zfill(2)) # 0292

            parsed['density'] = int(binary3, 16) # 658

            logging.debug('Density : ' + str(parsed['density']))



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(globalsat_S11x)



# --- Source: loragate.py ---

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

import time

import json

import threading

from binascii import unhexlify



class loragate():

    def __init__(self):

        self.name = 'loragate'



    def parse(self,data,device):

        logging.debug('Loragate Received')

        parsed={}

        data['parsed'] = parsed

        if device == "loragate_ascii":

            try:

                dataarray = utils.hexarray_from_string(data['payload'])

                logging.debug('Parsing')

                parsed['value'] = bytearray.fromhex(data['payload']).decode()

            except Exception as e:

                logging.debug(str(e))

                logging.debug('Unparsable data')

        return data



globals.COMPATIBILITY.append(loragate)



# --- Source: mclimate_AQI.py ---

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

import time

import json

import threading



class mclimate_AQI():

    def __init__(self):

        self.name = 'mclimate_AQI'



    def parse(self,data,device):

        logging.debug('mclimate AQI Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            sAQI1 = str(bin(int(payload[2:4], 16))[2:].zfill(8))

            binary2 = str(bin(int(payload[4:6], 16))[2:].zfill(8))

            sAQI2 = binary2[0:1]

            p1 = str(bin(int(payload[12:14], 16))[2:].zfill(8))

            binary7 = str(bin(int(payload[14:16], 16))[2:].zfill(8))

            p2 = binary7[0:3]

            t1 = binary7[4:]

            binary8 = str(bin(int(payload[16:18], 16))[2:].zfill(8))

            t2 = binary8[0:6]

            parsed['saqi'] = int('' + sAQI1 + sAQI2, 2) * 16 # 32

            parsed['aqi'] = int(binary2[1:7], 2) * 16 # 128

            parsed['voc'] = int(payload[8:10], 16) * 4 # 0

            parsed['humidity'] = (int(payload[10:12], 16) * 4) / 10 # 53,6

            parsed['pressure'] = (int('' + p1 + p2, 2) * 40 + 30000) / 100 # 982

            parsed['temperature'] = (int('' + t1 + t2, 2) - 400) / 10 # 24,5

            parsed['accuracy'] = int(binary8[-2:], 2) # 1

            parsed['voltage'] = ((int(payload[18:20], 16) * 8) + 1600) / 1000 # 3,4 V

            #logging.debug(parsed['saqi'])

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(mclimate_AQI)



# --- Source: mclimate_CO2.py ---

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

import time

import json

import threading



class mclimate_CO2():

    def __init__(self):

        self.name = 'mclimate_CO2'



    def parse(self,data,device):

        logging.debug('mclimate CO2 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            parsed['CO2'] = int(payload[2:6], 16)

            parsed['temperature'] = (int(payload[6:10], 16) - 400) / 10

            parsed['humidity'] = (int(payload[10:12], 16) * 100) / 256

            parsed['battery'] = (int(payload[12:14], 16) * 8) + 1600

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(mclimate_CO2)



# --- Source: mclimate_fanCoilThermostat.py ---

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

import time

import json

import threading



class mclimate_fanCoilThermostat():

    def __init__(self):

        self.name = 'mclimate_fanCoilThermostat'



    def parse(self,data,device):

        logging.debug('mclimate_fanCoilThermostat Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            #logging.debug(len(payload)) # 0102888001090102020101



            def decodageTrame(payload):

                reason = payload[0:2]

                if reason == '01':

                    # 01 0288 80 0109 01 02 02 01 01

                    parsed['temperature'] = (int(payload[2:6], 16) - 400) / 10

                    parsed['humidity'] = (int(payload[6:8], 16) * 100) / 256

                    parsed['targetTemp'] = int(payload[8:12], 16)/10



                    operationMode = payload[12:14]

                    if operationMode == '00':

                        parsed['operationalMode'] = 'Ventilation'

                    elif operationMode == '01':

                        parsed['operationalMode'] = 'Heating'

                    elif operationMode == '02':

                        parsed['operationalMode'] = 'Cooling'



                    displayedFanSpeed = payload[14:16]

                    if displayedFanSpeed == '00':

                        parsed['displayedFanSpeed'] = 'Auto'

                        parsed['fanSpeed'] = 'Auto'

                    elif displayedFanSpeed == '01':

                        parsed['displayedFanSpeed'] = 'Speed 1'

                        parsed['fanSpeed'] = 'NA'

                    elif displayedFanSpeed == '02':

                        parsed['displayedFanSpeed'] = 'Speed 2'

                        parsed['fanSpeed'] = 'Low'

                    elif displayedFanSpeed == '03':

                        parsed['displayedFanSpeed'] = 'Speed 3'

                        parsed['fanSpeed'] = 'NA'

                    elif displayedFanSpeed == '04':

                        parsed['displayedFanSpeed'] = 'Speed 4'

                        parsed['fanSpeed'] = 'Medium'

                    elif displayedFanSpeed == '05':

                        parsed['displayedFanSpeed'] = 'Speed 5'

                        parsed['fanSpeed'] = 'NA'

                    elif displayedFanSpeed == '06':

                        parsed['displayedFanSpeed'] = 'Speed 6'

                        parsed['fanSpeed'] = 'High'



                    actualFanSpeed = payload[16:18]

                    if actualFanSpeed == '01':

                        parsed['actualFanSpeedECM'] = 'Speed 1'

                        parsed['actualfanSpeed'] = 'NA'

                    elif actualFanSpeed == '02':

                        parsed['actualFanSpeedECM'] = 'Speed 2'

                        parsed['actualfanSpeed'] = 'Low'

                    elif actualFanSpeed == '03':

                        parsed['actualFanSpeedECM'] = 'Speed 3'

                        parsed['actualfanSpeed'] = 'NA'

                    elif actualFanSpeed == '04':

                        parsed['actualFanSpeedECM'] = 'Speed 4'

                        parsed['actualfanSpeed'] = 'Medium'

                    elif actualFanSpeed == '05':

                        parsed['actualFanSpeedECM'] = 'Speed 5'

                        parsed['actualfanSpeed'] = 'NA'

                    elif actualFanSpeed == '06':

                        parsed['actualFanSpeedECM'] = 'Speed 6'

                        parsed['actualfanSpeed'] = 'High'

                    elif actualFanSpeed == '07':

                        parsed['actualFanSpeedECM'] = 'Fan off'

                        parsed['actualfanSpeed'] = 'Fan off'



                    valveStatus = payload[18:20]

                    if valveStatus == '00':

                        parsed['valveStatus'] = '0'

                    elif valveStatus == '01':

                        parsed['valveStatus'] = '1'



                    deviceStatus = payload[20:22]

                    if deviceStatus == '00':

                        parsed['deviceStatus'] = '0'

                    elif deviceStatus == '01':

                        parsed['deviceStatus'] = '1'



            if len(payload) > 22 :

                if payload[0:2] == '12':

                    parsed['keepAliveMinutes'] = int(payload[2:4],16)

                elif payload[0:2] == '67':

                    if payload[2:4] == '00':

                        parsed['deviceStatus'] = 0

                    elif payload[2:4] == '01':

                        parsed['deviceStatus'] = 1

                elif payload[0:2] == '55':

                    if payload[2:4] == '00':

                        parsed['AllowedoperationalMode'] = 'Ventilation'

                    elif payload[2:4] == '01':

                        parsed['AllowedoperationalMode'] = 'Heating'

                    elif payload[2:4] == '02':

                        parsed['AllowedoperationalMode'] = 'Cooling'

                elif payload[0:2] == '53':

                    if payload[2:4] == '00':

                        parsed['operationalMode'] = 'Ventilation'

                    elif payload[2:4] == '01':

                        parsed['operationalMode'] = 'Heating'

                    elif payload[2:4] == '02':

                        parsed['operationalMode'] = 'Cooling'

                elif payload[0:2] == '2f':

                    parsed['targetTemp'] = int(payload[2:6],16)/10

                elif payload[0:2] == '30':

                    parsed['targetTemp'] = int(payload[2:6],16)/10

                    logging.debug(parsed['targetTemp'])

                elif payload[0:2] == '45':

                    if payload[2:4] == '00':

                        parsed['actualfanSpeed'] = 'Automatic'

                    elif payload[2:4] == '01':

                        parsed['actualFanSpeedECM'] = 'Speed 1'

                    elif payload[2:4] == '02':

                        parsed['actualFanSpeedECM'] = 'Speed 2'

                        parsed['actualfanSpeed'] = 'Low'

                    elif payload[2:4] == '03':

                        parsed['actualFanSpeedECM'] = 'Speed 3'

                    elif payload[2:4] == '04':

                        parsed['actualFanSpeedECM'] = 'Speed 4'

                        parsed['actualfanSpeed'] = 'Medium'

                    elif payload[2:4] == '05':

                        parsed['actualFanSpeedECM'] = 'Speed 5'

                    elif payload[2:4] == '06':

                        parsed['actualFanSpeedECM'] = 'Speed 6'

                        parsed['actualfanSpeed'] = 'High'

                    elif payload[2:4] == '07':

                        parsed['actualFanSpeedECM'] = 'Fan off'

                        parsed['actualfanSpeed'] = 'Fan off'

                elif payload[0:2] == '14':

                    if payload[2:4] == '00':

                        parsed['keysLock'] = 'No keys are locked.'

                    elif payload[2:4] == '01':

                        parsed['keysLock'] = 'All keys are locked.'

                    elif payload[2:4] == '02':

                        parsed['keysLock'] = 'ON/OFF and mode change are locked.'

                    elif payload[2:4] == '03':

                        parsed['keysLock'] = 'ON/OFF is locked.'

                    elif payload[2:4] == '04':

                        parsed['keysLock'] = 'All keys except ON/OFF key are locked.'

                    elif payload[2:4] == '05':

                        parsed['keysLock'] = 'Mode change is locked.'

                elif payload[0:2] == '36':

                    if payload[2:4] == '00':

                        parsed['automaticTempControl'] = 0

                    elif payload[2:4] == '01':

                        parsed['automaticTempControl'] = 1

                elif payload[0:2] == '75':

                    if payload[2:4] == '00':

                        parsed['powerModuleCom'] = 1

                    elif payload[2:4] == '01':

                        parsed['powerModuleCom'] = 0

                elif payload[0:2] == '5f':

                    if payload[2:4] == '00':

                        parsed['automaticStatus'] = 0

                    elif payload[2:4] == '01':

                        parsed['automaticStatus'] = 1

                elif payload[0:2] == '69':

                    if payload[2:4] == '00':

                        parsed['statusAfterReboot'] = "Last status"

                    elif payload[2:4] == '01':

                        parsed['statusAfterReboot'] = "On - after return of power supply"

                    elif payload[2:4] == '02':

                        parsed['statusAfterReboot'] = "Off - after return of power supply"

                elif payload[0:2] == '04':

                    parsed['hardwareV'] = payload[2:3] + '.' + payload[3:4]

                    parsed['softwareV'] = payload[4:5] + '.' + payload[5:6]

                elif payload[0:2] == '4f':

                    if payload[2:4] == '00':

                        parsed['frostProtectionStatus'] = 0

                    elif payload[2:4] == '01':

                        parsed['frostProtectionStatus'] = 1

                elif payload[0:2] == '4f':

                    if payload[2:4] == '00':

                        parsed['frostProtectionOnOff'] = 0

                    elif payload[2:4] == '01':

                        parsed['frostProtectionOnOff'] = 1

                elif payload[0:2] == '6e':

                    if payload[2:4] == '00':

                        parsed['frostProtection'] = 0

                    elif payload[2:4] == '01':

                        parsed['frostProtection'] = 1



                newPayload = payload[-22:]

                decodageTrame(newPayload)



            if len(payload) == 22 :

                decodageTrame(payload)



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(mclimate_fanCoilThermostat)



# --- Source: mclimate_Vicki.py ---

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

import time

import json

import threading



class mclimate_Vicki():

    def __init__(self):

        self.name = 'mclimate_Vicki'



    def parse(self,data,device):

        logging.debug('mclimate Vicki Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            logging.debug(len(payload))



            def decodageTrame(payload):

                reason = payload[0:2]

                if reason == '01':

                    parsed['temperature'] = (int(payload[4:6], 16) * 165) / 256 - 40

                if reason == '81':

                    parsed['temperature'] = (int(payload[4:6], 16) - 28.33333) / 5.66666

                parsed['targetTemp'] = int(payload[2:4], 16)

                parsed['humidity'] = (int(payload[6:8], 16) * 100) / 256

                parsed['battery'] = 2 + int(payload[14:15], 16) * 0.1

                binary7 = bin(int(payload[14:16], 16))[2:].zfill(8)

                parsed['openWindow'] = int(binary7[4:5])

                parsed['highMotorConsumption'] = int(binary7[-2:-1])

                parsed['lowMotorConsumption'] = int(binary7[-3:-2])

                parsed['brokenSensor'] = int(binary7[-4:-3])

                binary8 = bin(int(payload[16:18], 16))[2:].zfill(8)

                parsed['childLock'] = int(binary8[0])

                tmp = "0" + str(payload[12:14])

                tmp = tmp[-2:]

                motorRange1 = tmp[1]

                motorRange2 = "0" + str(payload[10:12])

                motorRange2 = motorRange2[-2:]

                parsed['motorRange'] = int("0x"+str(motorRange1+motorRange2),16)

                motorPosition1 = tmp[0]

                motorPosition2 = "0" + str(payload[8:10])

                motorPosition2 = motorPosition2[-2:]

                parsed['motorPosition'] = int("0x"+str(motorPosition1+motorPosition2),16)

                if parsed['motorRange'] != 0:

                    parsed['motorPercentage'] = parsed['motorPosition'] / parsed['motorRange'] * 100

                else:

                    parsed['motorPercentage'] = 0



                #parsed['motorPercentage'] = (int(parsed['motorPosition']) / int(parsed['motorRange'])) * 100



            if len(payload) > 18 :

                newPayload = payload[-18:]

                decodageTrame(newPayload)



            if len(payload) == 18 :

                decodageTrame(payload)



            if len(payload) == 24 :

                newPayload = payload[0:7]

                if newPayload[0:2] == '04':

                    parsed['hardwareV'] = newPayload[2:3] + '.' + newPayload[3:4]

                    parsed['softwareV'] = newPayload[4:5] + '.' + newPayload[5:6]



            if len(payload) == 22 :

                newPayload = payload[0:4]

                if newPayload[0:2] == '18':

                    mode = newPayload[2:4]

                    if mode == "00":

                        parsed['mode'] = 'Online manual'

                    elif mode == "01":

                        parsed['mode'] = 'Online automatic'

                    elif mode == "02":

                        parsed['mode'] = 'Online automatic with external temp'

                elif newPayload[0:2] == '1f':

                    primaryMode = newPayload[2:4]

                    if primaryMode == "00":

                        parsed['DevicePrimaryOperationalMode'] = 'Heating'

                    elif primaryMode == "01":

                        parsed['DevicePrimaryOperationalMode'] = 'Cooling'

                elif newPayload[0:2] == '12':

                    parsed['keepAliveMinutes'] = int(newPayload[2:4],16)

                elif newPayload[0:2] == '2b':

                    algo = newPayload[2:4]

                    if algo == "00":

                        parsed['controlalgorithm'] = 'Proportional control'

                    elif algo == "01":

                        parsed['controlalgorithm'] = 'Equal directional control'

                    elif algo == "02":

                        parsed['controlalgorithm'] = 'Proportional Integral control'



            if len(payload) == 28 :

                newPayload = payload[0:10]

                if newPayload[0:2] == '13':

                    window = newPayload[2:4]

                    if window == "00":

                        parsed['G10_openWindow'] = 0

                    elif window == "01":

                        parsed['G10_openWindow'] = 1

                    parsed['G10_durationValveChange'] = int(newPayload[4:6],16) * 5

                    tmp = "0" + str(payload[8:10])

                    tmp = tmp[-2:]

                    motorPosition1 = tmp[0]

                    motorPosition2 = "0" + str(payload[6:8])

                    motorPosition2 = motorPosition2[-2:]

                    parsed['G10_motorPosition'] = int("0x"+str(motorPosition1+motorPosition2),16)

                    diff = bin(int(payload[8:10],16))[2:].zfill(8)

                    parsed['G10_temperatureDelta'] = int(diff[5:8], 2)



            if len(payload) == 26 :

                newPayload = payload[0:10]

                if newPayload[0:2] == '46':

                    window = newPayload[2:4]

                    if window == "00":

                        parsed['G01_openWindow'] = 0

                    elif window == "01":

                        parsed['G01_openWindow'] = 1

                    parsed['G01_durationValveChange'] = int(newPayload[4:6],16) * 5

                    parsed['G01_temperatureDelta'] = int(newPayload[4:6],16) * 5



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(mclimate_Vicki)



# --- Source: mclimate_wirelessThermostat.py ---

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

import time

import json

import threading



class mclimate_wirelessThermostat():

    def __init__(self):

        self.name = 'mclimate_wirelessThermostat'



    def parse(self,data,device):

        logging.debug('mclimate_wirelessThermostat Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            logging.debug(len(payload)) 



            def decodageTrame(payload):

                reason = payload[0:2]

                if reason == '81': # 810288800A45010900027A00

                    parsed['temperature'] = (int(payload[2:6], 16) - 400) / 10

                    parsed['humidity'] = (int(payload[6:8], 16) * 100) / 256

                    parsed['voltage'] = int(payload[8:12], 16)

                    parsed['targetTemp'] = int(payload[12:16], 16) / 10

                    powerSource = payload[16:18]

                    if powerSource == '00':

                        parsed['powerSource'] = 'Photovoltaic'

                    elif powerSource == '01':

                        parsed['powerSource'] = 'Battery'

                    elif powerSource == '02':

                        parsed['powerSource'] = 'USB'

                    parsed['light'] = int(payload[18:22], 16)

                    pir = payload[22:24]

                    if pir == '00':

                        parsed['pir'] = 0

                    elif pir == '01':

                        parsed['pir'] = 1

                elif reason == '01': # 010288800A451700027A00

                    parsed['temperature'] = (int(payload[2:6], 16) - 400) / 10

                    parsed['humidity'] = (int(payload[6:8], 16) * 100) / 256

                    parsed['voltage'] = int(payload[8:12], 16)

                    parsed['targetTemp'] = int(payload[12:14], 16)

                    powerSource = payload[14:16]

                    if powerSource == '00':

                        parsed['powerSource'] = 'Photovoltaic'

                    elif powerSource == '01':

                        parsed['powerSource'] = 'Battery'

                    elif powerSource == '02':

                        parsed['powerSource'] = 'USB'

                    parsed['light'] = int(payload[16:20], 16)

                    pir = payload[20:22]

                    if pir == '00':

                        parsed['pir'] = 0

                    elif pir == '01':

                        parsed['pir'] = 1



            testPayload = payload[-22:]

            if testPayload[0:2] == '01':

                if len(payload) > 22 :

                    if payload[0:2] == '14':

                        if payload[2:4] == '00':

                            parsed['ChildLockStatus'] = 0

                        elif payload[2:4] == '01':

                            parsed['ChildLockStatus'] = 1

                    elif payload[0:2] == '3d':

                        if payload[2:4] == '00':

                            parsed['PirStatus'] = 0

                        elif payload[2:4] == '01':

                            parsed['PirStatus'] = 1

                    elif payload[0:2] == '30':

                        parsed['manualTargetTemperatureUpdate'] = int(payload[2:4], 16)

                    newPayload = payload[-22:]

                    decodageTrame(newPayload)



                if len(payload) == 22 :

                    decodageTrame(payload)

            else:

                if len(payload) > 24 :

                    if payload[0:2] == '14':

                        if payload[2:4] == '00':

                            parsed['ChildLockStatus'] = 0

                        elif payload[2:4] == '01':

                            parsed['ChildLockStatus'] = 1

                    elif payload[0:2] == '3d':

                        if payload[2:4] == '00':

                            parsed['PirStatus'] = 0

                        elif payload[2:4] == '01':

                            parsed['PirStatus'] = 1

                    elif payload[0:2] == '30':

                        parsed['manualTargetTemperatureUpdate'] = int(payload[2:4], 16)

                    newPayload = payload[-24:]

                    decodageTrame(newPayload)



                if len(payload) == 24 :

                    decodageTrame(payload)



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(mclimate_wirelessThermostat)



# --- Source: micropelt_mlr003.py ---

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

import time

import json

import threading

from binascii import unhexlify



class micropelt_mlr003():

    def __init__(self):

        self.name = 'micropelt_mlr003'



    def parse(self,data,device):

        logging.debug('MLR 003 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            payload = data['payload']

            logging.debug('Parsing')

            logging.debug(dataarray) # 21 32 40 63 63 00 81 ff 00 10 21

            parsed['Current_Valve_Position'] = dataarray[0]

            parsed['Flow_Sensor_Raw'] = dataarray[1] * 0.5

            parsed['Flow_Temperature'] = dataarray[2] * 0.5

            parsed['Ambient_Sensor_Raw'] = dataarray[3] * 0.25

            parsed['Ambient_Temperature'] = dataarray[4] * 0.25

            parsed['Energy_Storage'] = dataarray[5] >> 6 & 0x01

            parsed['Harvesting_Active'] = dataarray[5] >> 5 & 0x01

            parsed['Ambient_Sensor_Failure'] = dataarray[5] >> 4 & 0x01

            parsed['Flow_Sensor_Failure'] = dataarray[5] >> 3 & 0x01

            parsed['Radio_Communication_Error'] = dataarray[5] >> 2 & 0x01

            parsed['Received_Signal_Strength'] = dataarray[5] >> 1 & 0x01

            parsed['Motor_Error'] = dataarray[5] >> 0 & 0x01

            parsed['Storage_Voltage'] = round(dataarray[6] * 0.02,2)

            parsed['Average_Current_Consumed'] = dataarray[7] * 10

            parsed['Average_Current_Generated'] = dataarray[8] * 10

            parsed['Reference_Completed'] = dataarray[9] >> 4 & 0x01

            parsed['Operating_Mode'] = dataarray[9] >> 7 & 0x01

            parsed['Storage_Fully_Charged'] = dataarray[9] >> 6 & 0x01

            if len(dataarray) == 11:

                um = dataarray[9] & 0x03

                if um == 0:

                    uv = dataarray[10]

                else:

                    uv = dataarray[10] * 0.5

            parsed['User_Mode'] = um

            parsed['User_Value'] = uv

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(micropelt_mlr003)



# --- Source: milesight_AM100.py ---

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

import time

import json

import threading



class milesight_AM100():

    def __init__(self):

        self.name = 'milesight_AM100'



    def parse(self,data,device):

        logging.debug('AM100 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            logging.debug(payload)

            x=0

            i=0

            for i in range(8):

                channel_id = payload[x:x+2]

                channel_type = payload[x+2:x+4]

                if channel_id == '01' and channel_type == '75':

                    parsed['battery'] = int(payload[x+4:x+6],16)

                    x=x+6

                elif channel_id == '03' and channel_type == '67':

                    channel_value = (int(payload[x+6:x+8],16) << 8) + int(payload[x+4:x+6],16)

                    parsed['temperature'] = (channel_value & 0xffff)/10

                    x=x+8

                elif channel_id == '04' and channel_type == '68':

                    parsed['humidity'] = int(payload[x+4:x+6],16)/2

                    x=x+6

                elif channel_id == '05' and channel_type == '6a':

                    channel_value = (int(payload[x+6:x+8],16) << 8) + int(payload[x+4:x+6],16)

                    parsed['activity'] = channel_value & 0xffff

                    x=x+8

                elif channel_id == '06' and channel_type == '65':

                    channel_value = (int(payload[x+6:x+8],16) << 8) + int(payload[x+4:x+6],16)

                    parsed['illumination'] = channel_value & 0xffff

                    channel_value = (int(payload[x+10:x+12],16) << 8) + int(payload[x+8:x+10],16)

                    parsed['infrared_and_visible'] = channel_value & 0xffff

                    channel_value = (int(payload[x+14:x+16],16) << 8) + int(payload[x+12:x+14],16)

                    parsed['infrared'] = channel_value & 0xffff

                    x=x+16

                elif channel_id == '07' and channel_type == '7d':

                    channel_value = (int(payload[x+6:x+8],16) << 8) + int(payload[x+4:x+6],16)

                    parsed['co2'] = channel_value & 0xffff

                    x=x+8

                elif channel_id == '08' and channel_type == '7d':

                    channel_value = (int(payload[x+6:x+8],16) << 8) + int(payload[x+4:x+6],16)

                    parsed['tvoc'] = channel_value & 0xffff

                    x=x+8

                elif channel_id == '09' and channel_type == '73':

                    channel_value = (int(payload[x+6:x+8],16) << 8) + int(payload[x+4:x+6],16)

                    parsed['pressure'] = (channel_value & 0xffff)/10

                    x=x+8



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(milesight_AM100)



# --- Source: milesight_DS3604.py ---

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

import time

import json

import threading



class milesight_DS3604():

    def __init__(self):

        self.name = 'milesight_DS3604'



    def parse(self,data,device):

        logging.debug('DS3604 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing') # 017564ff7301

            payload = data['payload']

            logging.debug(payload) # 01 75 64 ff 73 01

            x=0

            i=0

            for i in range(4):

                channel_id = payload[x:x+2]

                channel_type = payload[x+2:x+4]

                logging.debug('CHANNEL ID ' + str(channel_id))

                logging.debug('CHANNEL TYPE ' + str(channel_type))

                if channel_id == '01' and channel_type == '75':

                    parsed['battery'] = int(payload[x+4:x+6],16)

                    x=x+6

                    channel_id = payload[x:x+2]

                    channel_type = payload[x+2:x+4]

                    if channel_id == 'ff' and channel_type == '73':

                        template = int(payload[x+4:x+6],16)

                        if template == 0:

                            parsed['template'] = 1

                        elif template == 1:

                            parsed['template'] = 2

                    x=x+6

                elif channel_id == 'fe' and channel_type == '73':

                    template = int(payload[x+4:x+6],16)

                    if template == 0:

                        parsed['template'] = 1

                    elif template == 1:

                        parsed['template'] = 2

                    x=x+6

                else:

                    logging.debug('BREAK')

                #x=x+6



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(milesight_DS3604)



# --- Source: milesight_EM300.py ---

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

import time

import json

import threading



class milesight_EM300():

    def __init__(self):

        self.name = 'milesight_EM300'



    def parse(self,data,device):

        logging.debug('WS301 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing') # 01755C03673401046865050000

            payload = data['payload']

            logging.debug(payload) # 01 75 5C 03 67 34 01 04 68 65 05 00 00

            x=0

            i=0

            for i in range(4):

                channel_id = payload[x:x+2]

                channel_type = payload[x+2:x+4]

                logging.debug('CHANNEL ID ' + str(channel_id))

                logging.debug('CHANNEL TYPE ' + str(channel_type))

                if channel_id == '01' and channel_type == '75':

                    parsed['battery'] = int(payload[x+4:x+6],16)

                    logging.debug('-------------------------- BATTERY ' + str(parsed['battery']))

                    x=x+6

                elif channel_id == '03' and channel_type == '67':

                    #parsed['temperature'] = payload[x+4:x+8]

                    channel_value = (int(payload[x+6:x+8],16) << 8) + int(payload[x+4:x+6],16)

                    parsed['temperature'] = (channel_value & 0xffff)/10

                    x=x+8

                    logging.debug('-------------------------- TEMPERATURE ' + str(parsed['temperature']))

                elif channel_id == '04' and channel_type == '68':

                    parsed['humidity'] = int(payload[x+4:x+6],16)/2

                    x=x+6

                    logging.debug('-------------------------- HUMIDITY ' + str(parsed['humidity']))

                elif channel_id == '05' and channel_type == '00':

                    channel_value = int(payload[x+4:x+6],16)

                    x=x+6

                    logging.debug('-------------------------- STATUS ' + str(channel_value))

                    if channel_value == 0:

                        parsed['status'] = 0

                    elif channel_value == 1:

                        parsed['status'] = 1

                    else:

                        logging.debug('UNSUPPORTED')

                else:

                    logging.debug('BREAK')

                #x=x+6



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(milesight_EM300)



# --- Source: milesight_EM320TH.py ---

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

import time

import json

import threading



class milesight_EM320TH():

    def __init__(self):

        self.name = 'milesight_EM320TH'



    def parse(self,data,device):

        logging.debug('EM320 TH Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            logging.debug(payload)

            x=0

            i=0

            for i in range(4):

                channel_id = payload[x:x+2]

                channel_type = payload[x+2:x+4]

                if channel_id == '01' and channel_type == '75':

                    parsed['battery'] = int(payload[x+4:x+6],16)

                    #logging.debug('-------------------------- BATTERY ' + str(parsed['battery']))

                    x=x+6

                elif channel_id == '03' and channel_type == '67':

                    #parsed['temperature'] = payload[x+4:x+8]

                    channel_value = (int(payload[x+6:x+8],16) << 8) + int(payload[x+4:x+6],16)

                    temperatureUint = (channel_value & 0xffff)

                    if temperatureUint > 32767 :

                        parsed['temperature'] = (temperatureUint - 65536) / 10

                    else:

                        parsed['temperature'] = temperatureUint / 10

                    x=x+8

                    #logging.debug('-------------------------- TEMPERATURE ' + str(parsed['temperature']))

                elif channel_id == '04' and channel_type == '68':

                    parsed['humidity'] = int(payload[x+4:x+6],16)/2

                    x=x+6

                    #logging.debug('-------------------------- HUMIDITY ' + str(parsed['humidity']))

                else:

                    logging.debug('BREAK')

                #x=x+6



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(milesight_EM320TH)



# --- Source: milesight_EM500PT100.py ---

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

import time

import json

import threading



class milesight_EM500PT100():

    def __init__(self):

        self.name = 'milesight_EM500PT100'



    def parse(self,data,device):

        logging.debug('milesight_EM500PT100 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            logging.debug(payload)

            x=0

            i=0

            for i in range(4):

                channel_id = payload[x:x+2]

                channel_type = payload[x+2:x+4]

                if channel_id == '01' and channel_type == '75':

                    parsed['battery'] = int(payload[x+4:x+6],16)

                    #logging.debug('-------------------------- BATTERY ' + str(parsed['battery']))

                    x=x+6

                elif channel_id == '03' and channel_type == '67':

                    #parsed['temperature'] = payload[x+4:x+8]

                    channel_value = (int(payload[x+6:x+8],16) << 8) + int(payload[x+4:x+6],16)

                    temperatureUint = (channel_value & 0xffff)

                    if temperatureUint > 32767 :

                        parsed['temperature'] = (temperatureUint - 65536) / 10

                    else:

                        parsed['temperature'] = temperatureUint / 10

                    x=x+8

                    #logging.debug('-------------------------- TEMPERATURE ' + str(parsed['temperature']))

                else:

                    logging.debug('BREAK')

                #x=x+6



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(milesight_EM500PT100)



# --- Source: milesight_UC501.py ---

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

import time

import json

import threading



class milesight_UC501():

    def __init__(self):

        self.name = 'milesight_UC501'



    def parse(self,data,device):

        logging.debug('UC501 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            logging.debug(payload)

            x=0

            i=0

            def convert_endian(var):

                    little_hex = bytearray.fromhex(var)

                    little_hex.reverse()

                    hex_string = ''.join(format(x, '02x') for x in little_hex)

                    return hex_string

            for i in range(3):

                channel_id = payload[x:x+2]

                channel_type = payload[x+2:x+4]

                logging.debug('CHANNEL ID ' + str(channel_id))

                logging.debug('CHANNEL TYPE ' + str(channel_type))

                if channel_id == '01' and channel_type == '75':

                    parsed['battery'] = int(payload[x+4:x+6],16)

                    logging.debug('BATTERY ' + str(parsed['battery']))

                if channel_id == '03' and channel_type != 'c8':

                    if channel_type == '00':

                        parsed['inputO1'] = int(payload[x+4:x+6],16)

                    elif channel_type == '01':

                        parsed['outputO1'] = int(payload[x+4:x+6],16)

                if channel_id == '04' and channel_type != 'c8':

                    if channel_type == '00':

                        parsed['inputO2'] = int(payload[x+4:x+6],16)

                    elif channel_type == '01':

                        parsed['outputO2'] = int(payload[x+4:x+6],16)

                if channel_id == '03' and channel_type == 'c8':

                    var = payload[x+4:x+12]

                    hex_string = convert_endian(var)

                    parsed['counter01'] = int(hex_string, 16)

                    logging.debug('counter01 ' + str(parsed['counter01']))

                if channel_id == '04' and channel_type == 'c8':

                    var = payload[x+4:x+12]

                    hex_string = convert_endian(var)

                    parsed['counter02'] = int(hex_string, 16)

                    logging.debug('counter02 ' + str(parsed['counter02']))

                if channel_id == '05':

                    var = payload[x+4:x+8]

                    hex_string = convert_endian(var)

                    parsed['ccy01'] = int(hex_string, 16) / 100

                    logging.debug('ccy ' + str(parsed['ccy01']))

                    var = payload[x+8:x+12]

                    hex_string = convert_endian(var)

                    parsed['min01'] = int(hex_string, 16) / 100

                    logging.debug('min ' + str(parsed['min01']))

                    var = payload[x+12:x+16]

                    hex_string = convert_endian(var)

                    parsed['max01'] = int(hex_string, 16) / 100

                    logging.debug('max ' + str(parsed['max01']))

                    var = payload[x+16:x+20]

                    hex_string = convert_endian(var)

                    parsed['avg01'] = int(hex_string, 16) / 100

                    logging.debug('avg ' + str(parsed['avg01']))

                if channel_id == '06':

                    var = payload[x+4:x+8]

                    hex_string = convert_endian(var)

                    parsed['ccy02'] = int(hex_string, 16) / 100

                    logging.debug('ccy ' + str(parsed['ccy02']))

                    var = payload[x+8:x+12]

                    hex_string = convert_endian(var)

                    parsed['min02'] = int(hex_string, 16) / 100

                    logging.debug('min ' + str(parsed['min02']))

                    var = payload[x+12:x+16]

                    hex_string = convert_endian(var)

                    parsed['max02'] = int(hex_string, 16) / 100

                    logging.debug('max ' + str(parsed['max02']))

                    var = payload[x+16:x+20]

                    hex_string = convert_endian(var)

                    parsed['avg02'] = int(hex_string, 16) / 100

                    logging.debug('avg ' + str(parsed['avg02']))

                ######################################################

                if channel_id == 'ff' and channel_type == '0e':

                    logging.debug('RS485')

                    parsed['modbus_chn_id'] = int(payload[x+4:x+6],16) - 6

                    package_type = int(payload[x+6:x+8],16)

                    data_type = package_type & 7

                    data_length = package_type >> 3

                    chn = 'chn' + str(parsed['modbus_chn_id'])

                    if data_type == 0:

                        parsed['channel_value'] = int(payload[x+8:x+10],16)

                    elif data_type == 1:

                        parsed['channel_value'] = int(payload[x+8:x+10],16)

                    elif data_type == 5: # 3

                        bytes = payload[x+8:x+14] # 00 00 00

                        logging.debug(bytes)

                        logging.debug(bytes[0])

                        logging.debug(bytes[1])

                        value = (bin(bytes[1]) << 8) + bin(bytes[0])

                else:

                    logging.debug('BREAK')

                x=x+6



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(milesight_UC501)



# --- Source: milesight_VS121.py ---

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

import time

import json

import threading



class milesight_VS121():

    def __init__(self):

        self.name = 'milesight_VS121'



    def parse(self,data,device):

        logging.debug('VS121 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            logging.debug(payload)

            x=0

            i=0

            parsed['region_0'] = 0

            parsed['region_1'] = 0

            parsed['region_2'] = 0

            parsed['region_3'] = 0

            parsed['region_4'] = 0

            parsed['region_5'] = 0

            parsed['region_6'] = 0

            parsed['region_7'] = 0

            parsed['region_8'] = 0

            parsed['region_9'] = 0

            parsed['region_10'] = 0

            parsed['region_11'] = 0

            parsed['region_12'] = 0

            parsed['region_13'] = 0

            parsed['region_14'] = 0

            parsed['region_15'] = 0

            for i in range(20):

                channel_id = payload[x:x+2]

                channel_type = payload[x+2:x+4]

                #logging.debug('CHANNEL ID ' + str(channel_id))

                #logging.debug('CHANNEL TYPE ' + str(channel_type))

                if channel_id == 'ff' and channel_type == '01':

                    parsed['protocolVersion'] = int(payload[x+4:x+6],16)

                    logging.debug('-------------------------- Protocol Version ' + str(parsed['protocolVersion']))

                    x=x+6

                elif channel_id == 'ff' and channel_type == '08':

                    parsed['serialNumber'] = payload[x+4:x+16]

                    x=x+16

                    logging.debug('-------------------------- Serial Number ' + str(parsed['serialNumber']))

                elif channel_id == 'ff' and channel_type == '09':

                    parsed['hardwareVersion'] = str(int(payload[x+4:x+6],16)) + '.' + str(int(payload[x+6:x+8],16))

                    x=x+8

                    logging.debug('-------------------------- Hardware Version ' + str(parsed['hardwareVersion']))

                elif channel_id == 'ff' and channel_type == '0a':

                    parsed['firmwareVersion'] = str(int(payload[x+4:x+6],16)) + '.' + str(int(payload[x+6:x+8],16)) + '.' + str(int(payload[x+8:x+10],16)) + '.' + str(int(payload[x+10:x+12],16))

                    x=x+12

                    logging.debug('-------------------------- Firmware Version ' + str(parsed['firmwareVersion']))

                elif channel_id == '04' and channel_type == 'c9':

                    parsed['people_counter_all'] = int(payload[x+4:x+6],16)

                    region_count = int(payload[x+6:x+8],16)

                    parsed['region_count'] = region_count

                    logging.debug('-------------------------- people_counter_all === ' + str(parsed['people_counter_all']))

                    #logging.debug('-------------------------- region_count === ' + str(parsed['region_count']))

                    region = int(payload[x+8:x+12],16)

                    index=1

                    for index in range(0,region_count):

                        tmp = "region_" + str(index+1)

                        test = (region >> index)

                        parsed[tmp] = (region >> index) & 1

                        logging.debug('-------------------------- region name === ' + str(tmp))

                        #logging.debug('-------------------------- test === ' + str(test))

                        logging.debug('-------------------------- number of people === ' + str(parsed[tmp]))

                    x=x+12

                elif channel_id == '05' and channel_type == 'cc':

                    parsed['in'] = int(payload[x+4:x+6],16)

                    parsed['out'] = int(payload[x+8:x+10],16)

                    x=x+12

                    logging.debug('-------------------------- IN ' + str(parsed['in']))

                    logging.debug('-------------------------- OUT ' + str(parsed['out']))

                elif channel_id == '06' and channel_type == 'cd':

                    parsed['max'] = int(payload[x+4:x+6],16)

                    x=x+6

                    logging.debug('-------------------------- Max ' + str(parsed['max']))

                #x=x+6



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(milesight_VS121)



# --- Source: milesight_WS101.py ---

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

import time

import json

import threading



class milesight_WS101():

    def __init__(self):

        self.name = 'milesight_WS101'



    def parse(self,data,device):

        logging.debug('WS101 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing') # 017510FF2E01

            payload = data['payload']

            logging.debug(payload) # 01 75 10 FF 2E 01

            x=0

            i=0

            for i in range(2):

                channel_id = payload[x:x+2]

                channel_type = payload[x+2:x+4]

                logging.debug('CHANNEL ID ' + str(channel_id))

                logging.debug('CHANNEL TYPE ' + str(channel_type))

                if channel_id == '01' and channel_type == '75':

                    parsed['battery'] = int(payload[x+4:x+6],16)

                    logging.debug('BATTERY ' + str(parsed['battery']))

                elif channel_id == 'ff' and channel_type == '2e':

                    channel_value = int(payload[x+4:x+6],16)

                    logging.debug('CHANNEL VALUE ' + str(channel_value))

                    if channel_value == 1:

                        parsed['press'] = 'Short'

                    elif channel_value == 2:

                        parsed['press'] = 'Long'

                    elif channel_value == 3:

                        parsed['press'] = 'Double'

                    else:

                        logging.debug('UNSUPPORTED')

                else:

                    logging.debug('BREAK')

                x=x+6



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(milesight_WS101)



# --- Source: milesight_WS156.py ---

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

import time

import json

import threading



class milesight_WS156():

    def __init__(self):

        self.name = 'milesight_WS156'



    def parse(self,data,device):

        logging.debug('WS156 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing') # 017564 FF34011800

            payload = data['payload']

            logging.debug(payload)

            x=0

            i=0

            for i in range(1):

                channel_id = payload[x:x+2]

                channel_type = payload[x+2:x+4]

                logging.debug('CHANNEL ID ' + str(channel_id))

                logging.debug('CHANNEL TYPE ' + str(channel_type))

                if channel_id == '01' and channel_type == '75':

                    parsed['battery'] = int(payload[x+4:x+6],16)

                    logging.debug('BATTERY ' + str(parsed['battery']))

                    x=x+1

                elif channel_id == 'ff' and channel_type == '34':

                    parsed['buttonNB'] = int(payload[x+4:x+6],16)

                    little_hex = bytearray.fromhex(payload[x+6:x+10])

                    little_hex.reverse()

                    parsed['LoRaD2D'] = ''.join(format(x, '02x') for x in little_hex)

                    x=x+10

                else:

                    logging.debug('BREAK')



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(milesight_WS156)



# --- Source: milesight_WS202.py ---

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

import time

import json

import threading



class milesight_WS202():

    def __init__(self):

        self.name = 'milesight_WS202'



    def parse(self,data,device):

        logging.debug('WS202 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            logging.debug(payload)

            x=0

            i=0

            for i in range(3):

                channel_id = payload[x:x+2]

                channel_type = payload[x+2:x+4]

                if channel_id == '01' and channel_type == '75':

                    parsed['battery'] = int(payload[x+4:x+6],16)

                elif channel_id == '03' and channel_type == '00':

                    channel_value = int(payload[x+4:x+6],16)

                    if channel_value == 0:

                        parsed['pirState'] = 0

                    elif channel_value == 1:

                        parsed['pirState'] = 1

                    else:

                        logging.debug('UNSUPPORTED')

                elif channel_id == '04' and channel_type == '00':

                    channel_value = int(payload[x+4:x+6],16)

                    if channel_value == 0:

                        parsed['daylightState'] = 'Nuit'

                    elif channel_value == 1:

                        parsed['daylightState'] = 'Jour'

                    else:

                        logging.debug('UNSUPPORTED')

                else:

                    logging.debug('BREAK')

                x=x+6



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(milesight_WS202)



# --- Source: milesight_WS301.py ---

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

import time

import json

import threading



class milesight_WS301():

    def __init__(self):

        self.name = 'milesight_WS301'



    def parse(self,data,device):

        logging.debug('WS301 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing') # 017564030001040001

            payload = data['payload']

            logging.debug(payload) # 01 75 64 03 00 01 04 00 01

            x=0

            i=0

            for i in range(3):

                channel_id = payload[x:x+2]

                channel_type = payload[x+2:x+4]

                logging.debug('CHANNEL ID ' + str(channel_id))

                logging.debug('CHANNEL TYPE ' + str(channel_type))

                if channel_id == '01' and channel_type == '75':

                    parsed['battery'] = int(payload[x+4:x+6],16)

                    logging.debug('BATTERY ' + str(parsed['battery']))

                elif channel_id == '03' and channel_type == '00':

                    channel_value = int(payload[x+4:x+6],16)

                    logging.debug('DOOR STATE ' + str(channel_value))

                    if channel_value == 0:

                        parsed['doorState'] = 0

                    elif channel_value == 1:

                        parsed['doorState'] = 1

                    else:

                        logging.debug('UNSUPPORTED')

                elif channel_id == '04' and channel_type == '00':

                    channel_value = int(payload[x+4:x+6],16)

                    logging.debug('INSTALL STATE ' + str(channel_value))

                    if channel_value == 0:

                        parsed['installState'] = 1

                    elif channel_value == 1:

                        parsed['installState'] = 0

                    else:

                        logging.debug('UNSUPPORTED')

                else:

                    logging.debug('BREAK')

                x=x+6



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(milesight_WS301)



# --- Source: milesight_WS50x.py ---

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

import time

import json

import threading

import datetime

import base64



class milesight_WS50x():

    def __init__(self):

        self.name = 'milesight_WS50x'



    def parse(self,data,device):

        logging.debug('Milesight WS50x Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = data['payload']

            logging.debug('Parsing')

            logging.debug(dataarray)

            i = 0

            j = 1

            while i < len(dataarray):

                channel_id = j

                channel_type = j

                channel_id = dataarray[i:i+2]

                channel_type = dataarray[i+2:i+4]

                # Voltage

                if channel_id == '03' and channel_type == '74':

                    var = dataarray[i+4:i+8]

                    little_hex = bytearray.fromhex(var)

                    little_hex.reverse()

                    hex_string = ''.join(format(x, '02x') for x in little_hex)

                    parsed['voltage'] = (int(hex_string, 16))*0.1

                    i=i+4

                # Active Power

                elif channel_id == '04' and channel_type == '80':

                    var = dataarray[i+4:i+12]

                    little_hex = bytearray.fromhex(var)

                    little_hex.reverse()

                    hex_string = ''.join(format(x, '02x') for x in little_hex)

                    hex_value = hex(int(hex_string, 16))

                    var = bin(int(hex_value, 16))[2:].zfill(8)

                    parsed['activePower'] = int(var,2)

                    i = i+8

                # Active Factor

                elif channel_id == '05' and channel_type == '81':

                    var = dataarray[i+4:i+6]

                    parsed['powerFactor'] = int(var, 16)

                    i=i+2

                # Power Consumption

                elif channel_id == '06' and channel_type == '83':

                    var = dataarray[i+4:i+12]

                    little_hex = bytearray.fromhex(var)

                    little_hex.reverse()

                    hex_string = ''.join(format(x, '02x') for x in little_hex)

                    hex_value = hex(int(hex_string, 16))

                    var = bin(int(hex_value, 16))[2:].zfill(8)

                    parsed['powerConsumption'] = int(var,2)

                    i = i+8

                # Current

                elif channel_id == '07' and channel_type == 'c9':

                    var = dataarray[i+4:i+8]

                    little_hex = bytearray.fromhex(var)

                    little_hex.reverse()

                    hex_string = ''.join(format(x, '02x') for x in little_hex)

                    hex_value = hex(int(hex_string, 16))

                    var = bin(int(hex_value, 16))[2:].zfill(8)

                    parsed['current'] = int(var,2)

                    i = i+4

                # Switch V1

                elif channel_id == 'ff' and channel_type == '29':

                    parsed['version'] = 'V1'

                    binary = bin(int(dataarray[i+4:i+6], 16))[2:].zfill(8)

                    parsed['switch3change'] = int(binary[1])

                    parsed['switch2change'] = int(binary[2])

                    parsed['switch1change'] = int(binary[3])

                    parsed['switch3'] = int(binary[5])

                    parsed['switch2'] = int(binary[6])

                    parsed['switch1'] = int(binary[7])

                    i = i+2

                # Switch V2

                elif channel_id == '08' and channel_type == '29':

                    parsed['version'] = 'V2'

                    binary = bin(int(dataarray[i+4:i+6], 16))[2:].zfill(8)

                    parsed['switch3change'] = int(binary[1])

                    parsed['switch2change'] = int(binary[2])

                    parsed['switch1change'] = int(binary[3])

                    parsed['switch3'] = int(binary[5])

                    parsed['switch2'] = int(binary[6])

                    parsed['switch1'] = int(binary[7])

                    i = i+2

                j=j+1

                i=i+1



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(milesight_WS50x)



# --- Source: milesight_WS51x.py ---

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

import time

import json

import threading

import datetime

import base64



class milesight_WS51x():

    def __init__(self):

        self.name = 'milesight_WS51x'



    def parse(self,data,device):

        logging.debug('Milesight WS51x Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = data['payload']

            logging.debug('Parsing')

            logging.debug(dataarray)

            i = 0

            j = 1

            while i < len(dataarray):

                channel_id = j

                channel_type = j

                channel_id = dataarray[i:i+2]

                channel_type = dataarray[i+2:i+4]

                # Voltage

                if channel_id == '03' and channel_type == '74':

                    var = dataarray[i+4:i+8]

                    little_hex = bytearray.fromhex(var)

                    little_hex.reverse()

                    hex_string = ''.join(format(x, '02x') for x in little_hex)

                    parsed['voltage'] = (int(hex_string, 16))*0.1

                    i=i+4

                # Active Power

                elif channel_id == '04' and channel_type == '80':

                    var = dataarray[i+4:i+12]

                    little_hex = bytearray.fromhex(var)

                    little_hex.reverse()

                    hex_string = ''.join(format(x, '02x') for x in little_hex)

                    hex_value = hex(int(hex_string, 16))

                    var = bin(int(hex_value, 16))[2:].zfill(8)

                    parsed['activePower'] = int(var,2)

                    i = i+8

                # Active Factor

                elif channel_id == '05' and channel_type == '81':

                    var = dataarray[i+4:i+6]

                    parsed['powerFactor'] = int(var, 16)

                    i=i+2

                # Power Consumption

                elif channel_id == '06' and channel_type == '83':

                    var = dataarray[i+4:i+12]

                    little_hex = bytearray.fromhex(var)

                    little_hex.reverse()

                    hex_string = ''.join(format(x, '02x') for x in little_hex)

                    hex_value = hex(int(hex_string, 16))

                    var = bin(int(hex_value, 16))[2:].zfill(8)

                    parsed['powerConsumption'] = int(var,2)

                    i = i+8

                # Current

                elif channel_id == '07' and channel_type == 'c9':

                    var = dataarray[i+4:i+8]

                    little_hex = bytearray.fromhex(var)

                    little_hex.reverse()

                    hex_string = ''.join(format(x, '02x') for x in little_hex)

                    hex_value = hex(int(hex_string, 16))

                    var = bin(int(hex_value, 16))[2:].zfill(8)

                    parsed['current'] = int(var,2)

                    i = i+4

                # State

                elif channel_id == '08' and channel_type == '70':

                    var = dataarray[i+4:i+6]

                    if var == '01' :

                        parsed['state'] = 1

                    else:

                        parsed['state'] = 0

                    i = i+2

                j=j+1

                i=i+1



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(milesight_WS51x)



# --- Source: milesight_WS522.py ---

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

import time

import json

import threading

import datetime

import base64



class milesight_WS522():

    def __init__(self):

        self.name = 'milesight_WS522'



    def parse(self,data,device):

        logging.debug('Milesight WS522 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = data['payload']

            logging.debug('Parsing')

            logging.debug(dataarray)

            i = 0

            j = 1

            while i < len(dataarray):

                channel_id = j

                channel_type = j

                channel_id = dataarray[i:i+2]

                channel_type = dataarray[i+2:i+4]

                # Voltage

                if channel_id == '03' and channel_type == '74':

                    var = dataarray[i+4:i+8]

                    little_hex = bytearray.fromhex(var)

                    little_hex.reverse()

                    hex_string = ''.join(format(x, '02x') for x in little_hex)

                    parsed['voltage'] = (int(hex_string, 16))*0.1

                    i=i+4

                    logging.debug(parsed['voltage'])

                # Active Power

                elif channel_id == '04' and channel_type == '80':

                    var = dataarray[i+4:i+12]

                    little_hex = bytearray.fromhex(var)

                    little_hex.reverse()

                    hex_string = ''.join(format(x, '02x') for x in little_hex)

                    hex_value = hex(int(hex_string, 16))

                    var = bin(int(hex_value, 16))[2:].zfill(8)

                    parsed['activePower'] = int(var,2)

                    i = i+8

                    logging.debug(parsed['activePower'])

                # Power Factor

                elif channel_id == '05' and channel_type == '81':

                    var = dataarray[i+4:i+6]

                    parsed['powerFactor'] = int(var, 16)

                    i=i+2

                    logging.debug(parsed['powerFactor'])

                # Power Consumption

                elif channel_id == '06' and channel_type == '83':

                    var = dataarray[i+4:i+12]

                    little_hex = bytearray.fromhex(var)

                    little_hex.reverse()

                    hex_string = ''.join(format(x, '02x') for x in little_hex)

                    hex_value = hex(int(hex_string, 16))

                    var = bin(int(hex_value, 16))[2:].zfill(8)

                    parsed['powerConsumption'] = int(var,2)

                    i = i+8

                    logging.debug(parsed['powerConsumption'])

                # Current

                elif channel_id == '07' and channel_type == 'c9':

                    var = dataarray[i+4:i+8]

                    little_hex = bytearray.fromhex(var)

                    little_hex.reverse()

                    hex_string = ''.join(format(x, '02x') for x in little_hex)

                    hex_value = hex(int(hex_string, 16))

                    var = bin(int(hex_value, 16))[2:].zfill(8)

                    parsed['current'] = int(var,2)

                    i = i+4

                    logging.debug(parsed['current'])

                # State

                elif channel_id == '08' and channel_type == '70':

                    var = dataarray[i+4:i+6]

                    if var == '01' :

                        parsed['state'] = 1

                    else:

                        parsed['state'] = 0

                    i = i+2

                    logging.debug(parsed['state'])

                elif channel_id == 'ff' and channel_type == '26':

                    var = dataarray[i+4:i+6]

                    if var == '01' :

                        parsed['powered'] = 1

                    else:

                        parsed['powered'] = 0

                    i = i+2

                    logging.debug(parsed['powered'])

                j=j+1

                i=i+1



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(milesight_WS522)



# --- Source: milesight_WS558.py ---

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

import time

import json

import threading

import datetime

import base64



class milesight_WS558():

    def __init__(self):

        self.name = 'milesight_WS558'



    def parse(self,data,device):

        logging.debug('Milesight WS558 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = data['payload']

            logging.debug('Parsing')

            logging.debug(dataarray)

            i = 0

            j = 1

            while i < len(dataarray):

                channel_id = j

                channel_type = j

                channel_id = dataarray[i:i+2]

                channel_type = dataarray[i+2:i+4]

                # Voltage

                if channel_id == '03' and channel_type == '74':

                    var = dataarray[i+4:i+8]

                    little_hex = bytearray.fromhex(var)

                    little_hex.reverse()

                    hex_string = ''.join(format(x, '02x') for x in little_hex)

                    parsed['voltage'] = (int(hex_string, 16))*0.1

                    i=i+4

                    # logging.debug(parsed['voltage'])

                # Active Power

                elif channel_id == '04' and channel_type == '80':

                    var = dataarray[i+4:i+12]

                    little_hex = bytearray.fromhex(var)

                    little_hex.reverse()

                    hex_string = ''.join(format(x, '02x') for x in little_hex)

                    hex_value = hex(int(hex_string, 16))

                    var = bin(int(hex_value, 16))[2:].zfill(8)

                    parsed['activePower'] = int(var,2)

                    i = i+8

                    # logging.debug(parsed['activePower'])

                # Power Factor

                elif channel_id == '05' and channel_type == '81':

                    var = dataarray[i+4:i+6]

                    parsed['powerFactor'] = int(var, 16)

                    i=i+2

                    # logging.debug(parsed['powerFactor'])

                # Power Consumption

                elif channel_id == '06' and channel_type == '83':

                    var = dataarray[i+4:i+12]

                    little_hex = bytearray.fromhex(var)

                    little_hex.reverse()

                    hex_string = ''.join(format(x, '02x') for x in little_hex)

                    hex_value = hex(int(hex_string, 16))

                    var = bin(int(hex_value, 16))[2:].zfill(8)

                    parsed['powerConsumption'] = int(var,2)

                    i = i+8

                    # logging.debug(parsed['powerConsumption'])

                # Current

                elif channel_id == '07' and channel_type == 'c9':

                    var = dataarray[i+4:i+8]

                    little_hex = bytearray.fromhex(var)

                    little_hex.reverse()

                    hex_string = ''.join(format(x, '02x') for x in little_hex)

                    hex_value = hex(int(hex_string, 16))

                    var = bin(int(hex_value, 16))[2:].zfill(8)

                    parsed['current'] = int(var,2)

                    i = i+4

                    # logging.debug(parsed['current'])

                # State

                elif channel_id == '08' and channel_type == '31':

                    byte2 = dataarray[i+6:i+8]

                    temp = bin(int(byte2, 16))[2:].zfill(8)

                    switchs = temp[::-1]

                    for x in range(0, 8):

                        switchTag = "switch" + str((int(x) + 1))

                        parsed[switchTag] = int(switchs[x])

                j=j+1

                i=i+1



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(milesight_WS558)



# --- Source: nanosenseE4000NG.py ---

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

import time

import json

import threading

from binascii import unhexlify



class nanosenseE4000NG():

    def __init__(self):

        self.name = 'nanosenseE4000NG'



    def parse(self,data,device):

        logging.debug('nanosenseE4000NG Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            if dataarray[0] == 0x00:

                logging.debug('There is nanosense E4000NG without capteurs')

                return data

            else:

                logging.debug('There is nanosense E4000NG with capteurs')

            parsed['co2-4'] = float(int(dataarray[1]))*19.6

            parsed['hum-4'] = float(int(dataarray[2]))*0.5

            parsed['temp-4'] = float(int(dataarray[3]))*0.2

            parsed['cov-4'] = float(int(hex( (dataarray[5]<<8) | dataarray[6] ),16))

            parsed['co2-3'] = float(int(dataarray[12]))*19.6

            parsed['hum-3'] = float(int(dataarray[13]))*0.5

            parsed['temp-3'] = float(int(dataarray[14]))*0.2

            parsed['cov-3'] = int(hex( (dataarray[16]<<8) | dataarray[17] ),16)

            parsed['co2-2'] = float(int(dataarray[23]))*19.6

            parsed['hum-2'] = float(int(dataarray[24]))*0.5

            parsed['temp-2'] = float(int(dataarray[25]))*0.2

            parsed['cov-2'] = int(hex( (dataarray[27]<<8) | dataarray[28] ),16)

            parsed['co2'] = float(int(dataarray[34]))*19.6

            parsed['hum'] = float(int(dataarray[35]))*0.5

            parsed['temp'] = float(int(dataarray[36]))*0.2

            parsed['cov'] = int(hex( (dataarray[38]<<8) | dataarray[29] ),16)

            parsed['co2-moy'] = (parsed['co2']+parsed['co2-2']+parsed['co2-3']+parsed['co2-4'])/4

            parsed['hum-moy'] = (parsed['hum']+parsed['hum-2']+parsed['hum-3']+parsed['hum-4'])/4

            parsed['temp-moy'] = (parsed['temp']+parsed['temp-2']+parsed['temp-3']+parsed['temp-4'])/4

            parsed['cov-moy'] = (parsed['cov']+parsed['cov-2']+parsed['cov-3']+parsed['cov-4'])/4

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(nanosenseE4000NG)



# --- Source: nanosenseEP5000L.py ---

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

import time

import json

import threading

from binascii import unhexlify



class nanosenseEP5000L():

    def __init__(self):

        self.name = 'nanosenseEP5000L'



    def parse(self,data,device):

        logging.debug('nanosenseEP5000L Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            # Presence Sensor

            binary1 = bin(int(payload[0:2],16))[2:]

            # Autonomy

            parsed['autonomy'] = int(payload[10:12],16)

            # RH

            parsed['RH'] = int(payload[16:18],16)*0.5

            # Temperature

            binary10 = bin(int(payload[18:22],16))[2:]

            binary10 = binary10.zfill(16)

            parsed['temperature'] = int(binary10[0:9],2)*0.1

            # PM

            binary11 = bin(int(payload[20:28],16))[2:]

            binary11 = binary11.zfill(32)

            parsed['PM10'] = int(binary11[1:10],2)

            parsed['PM2.5'] = int(binary11[10:19],2)

            parsed['PM1'] = int(binary11[19:28],2)

            # Noise

            binary14 = bin(int(payload[26:32],16))[2:]

            binary14 = binary14.zfill(24)

            parsed['averageNoise'] = int(binary14[4:11],2)

            parsed['picNoise'] = int(binary14[11:18],2)

            # CO2

            binary16 = bin(int(payload[30:34],16))[2:]

            binary16 = binary16.zfill(16)

            parsed['CO2'] = int(binary16[3:16],2)

            # TVOC

            parsed['TVOC'] = int(payload[34:38],16)

            # Formaldehyde

            parsed['formaldehyde'] = int(payload[38:42],16)*0.01

            # Benzene

            parsed['benzene'] = int(payload[42:46],16)*0.01

            # Sulphurous Odors

            parsed['sulphurousOdors'] = int(payload[46:48],16)

            # NOx

            parsed['NOx'] = int(payload[48:50],16)*2

            # Ozone

            parsed['ozone'] = int(payload[50:52],16)*2

            # Atmospheric Pressure

            binary27 = bin(int(payload[52:56],16))[2:]

            binary27 = binary27.zfill(16)

            parsed['atmosphericPressure'] = int(binary27[0:14],2)*0.1

            # Lux

            binary28 = bin(int(payload[54:58],16))[2:]

            binary28 = binary28.zfill(16)

            parsed['lux'] = int(binary28[6:16],2)*4

            # Light Color Temperature

            parsed['lightColorTemperature'] = int(payload[58:60],16)*23

            # Light Flickering

            parsed['lightFlickering'] = int(payload[60:62],16)

            # Health Index

            parsed['healthIndex'] = int(payload[62:64],16)

            # Cognitivity Index

            parsed['cognitivityIndex'] = int(payload[64:66],16)

            # Sleeping Index

            parsed['sleepingIndex'] = int(payload[66:68],16)

            # Throat Irritation Index

            parsed['throatIrritationIndex'] = int(payload[68:70],16)

            # Building Index

            parsed['buildingIndex'] = int(payload[70:72],16)

            # Virus Spreading Risk

            parsed['virusSpreadingRisk'] = int(payload[72:74],16)

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(nanosenseEP5000L)



# --- Source: netvox.py ---

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

import time

import json

import threading

from binascii import unhexlify



class netvox():

    def __init__(self):

        self.name = 'netvox'



    def parse(self,data,device):

        logging.debug('Netvox Received')

        parsed={}

        data['parsed'] = parsed

        dataarray = utils.hexarray_from_string(data['payload'])

        if (dataarray[1] == 0x12 or dataarray[1] == 0x02 or dataarray[2] == 0x1D or dataarray[2] == 0x7D) :

            logging.debug('Parsing R311A/R313A')

            try:

                if dataarray[2] == 0x01:

                    parsed['battery'] = int(dataarray[3])/10

                    parsed['status'] = int(dataarray[4])

            except Exception as e:

                logging.debug(str(e))

                logging.debug('Unparsable data')

        if dataarray[1] == 0x59:

            logging.debug('Parsing R719A')

            try:

                if dataarray[2] == 0x01:

                    parsed['battery'] = int(dataarray[3])/10

                    parsed['parkingstatus'] = int(dataarray[4])

                    parsed['radarstatus'] = int(dataarray[5])

                    parsed['power1'] = int(dataarray[8])

            except Exception as e:

                logging.debug(str(e))

                logging.debug('Unparsable data')

        if dataarray[1] == 0x69:

            logging.debug('Parsing R602A')

            try:

                if dataarray[2] == 0x01:

                    parsed['status'] = int(dataarray[5])

            except Exception as e:

                logging.debug(str(e))

                logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(netvox)



# --- Source: nexelec.py ---

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

import time

import json

import threading

import binascii

#from binascii import unhexlify



class nexelec():

    def __init__(self):

        self.name = 'nexelec'



    def parse(self,data,device):

        logging.debug('Nexelec Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            payload = data['payload']

            logging.debug('Parsing')

            if dataarray[0] == 0xA2:

                logging.debug('This is insafe+ Origin Lora')

                if dataarray[1] == 0x00:

                    logging.debug('This is status')

                    if dataarray[2] == 0x00:

                        parsed['hardware'] = 'C027A'

                    else:

                        parsed['hardware'] = 'N/A'

                    if dataarray[3] == 0x00:

                        parsed['software'] = 'S077A'

                    else:

                        parsed['hardware'] = 'N/A'

                    parsed['remainLife'] = int(hex(dataarray[4]),16)

                    binary5 = bin(int(str(dataarray[5])))[2:].zfill(8)

                    parsed['smoke'] = binary5[0:1]

                    parsed['temp'] = binary5[1:2]

                    parsed['bat1'] = 2000+ int(hex(dataarray[6]),16)*5

                    parsed['bat2'] = 2000+ int(hex(dataarray[7]),16)*5

                elif dataarray[1] == 0x03:

                    binary2 = bin(int(str(dataarray[2])))[2:].zfill(8)

                    parsed['smoke'] = binary2[0:1]

                    parsed['smokehush'] = binary2[1:2]

                    parsed['smoketest'] = binary2[2:3]

                    parsed['smokemaintenance'] = binary2[3:4]

                    parsed['smokehum'] = binary2[4:5]

                    parsed['smoketemp'] = binary2[5:6]

                    parsed['timesincemaint'] = int(hex(dataarray[3]),16)

                elif dataarray[1] == 0x04:

                    binary = str(bin(int(payload, 16))[2:])

                    parsed['daily_iaq_global'] = int(binary[16:19],2)

                    parsed['daily_iaq_source'] = int(binary[19:23],2)

                    parsed['daily_temp_min'] = int(payload[6:8],16) * 0.2

                    parsed['daily_temp_max'] = int(payload[8:10],16) * 0.2

                    parsed['daily_temp_avg'] = int(payload[10:12],16) * 0.2

                    parsed['daily_hum_min'] = int(payload[12:14],16) * 0.5

                    parsed['daily_hum_max'] = int(payload[14:16],16) * 0.5

                    parsed['daily_hum_avg'] = int(payload[16:18],16) * 0.5

                elif dataarray[1] == 0x05:

                    binary = str(bin(int(payload, 16))[2:])

                    parsed['iaq_global'] = int(binary[17:20],2)

                    parsed['iaq_source'] = int(binary[20:23],2)

                    parsed['iaq_dry'] = int(binary[23:26],2)

                    parsed['iaq_mould'] = int(binary[26:29],2)

                    parsed['iaq_dm'] = int(binary[29:32],2)

                    parsed['temperature'] = int(binary[32:41],2) * 0.1

                    parsed['humidity'] = int(binary[41:49],2) * 0.5

                elif dataarray[1] == 0x06:

                    binary = str(bin(int(payload, 16))[2:])

                    nb_mesure = int(payload[4:6],16)

                    start = 23+(nb_mesure*9)

                    end = 23+(nb_mesure*9)+9

                    logging.debug('nb_mesure:'+str(nb_mesure)+' start:'+str(start)+' end:'+str(end)+' value:'+binary[start:end])

                    parsed['temperature'] = int(binary[start:end],2) * 0.1

                elif dataarray[1] == 0x07:

                    binary = str(bin(int(payload, 16))[2:])

                    nb_mesure = int(payload[4:6],16)

                    start = 24+(nb_mesure*8)

                    end = 24+(nb_mesure*8)+8

                    logging.debug('nb_mesure:'+str(nb_mesure)+' start:'+str(start)+' end:'+str(end)+' binary:'+binary[start:end])

                    parsed['humidity'] = int(binary[start:end],2) * 0.5

            elif dataarray[0] == 0x72:

                logging.debug('This is insafe+ Carbon Real time data')

                binary = str(bin(int(payload, 16))[2:])

                parsed['CO2level'] = int(hex(dataarray[1]),16) * 20

                parsed['temperature'] = int(hex(dataarray[2]),16) * 0.2

                parsed['humidity'] = int(hex(dataarray[3]),16) * 0.5

                parsed['iaq_global'] = int(binary[32:35],2)

                parsed['iaq_source'] = int(binary[35:39],2)

                parsed['iaq_co2'] = int(binary[39:42],2)

                parsed['iaq_dry'] = int(binary[42:45],2)

                parsed['iaq_mould'] = int(binary[45:48],2)

                parsed['iaq_dm'] = int(binary[48:51],2)

                parsed['hci'] = int(binary[51:53],2)

            elif dataarray[0] == 0x73:

                logging.debug('This is insafe+ Carbon Product Status')

                binary = str(bin(int(payload, 16))[2:])

                parsed['battery_level'] = int(binary[8:10],2)

            elif dataarray[0] == 0x74:

                logging.debug('This is insafe+ Carbon Button Press')

                parsed['button'] = 1    

            elif dataarray[0] == 0x60:

                logging.debug('This is insafe+ Pilot Product Status')

                binary = str(bin(int(payload, 16))[2:])

                parsed['battery_level'] = int(binary[8:10],2)

            elif dataarray[0] == 0x61:

                logging.debug('This is insafe+ Pilot Real time data')

                binary = str(bin(int(payload, 16))[2:])

                parsed['temperature'] = int(hex(dataarray[1]),16) * 0.2

                parsed['humidity'] = int(hex(dataarray[2]),16) * 0.5

                parsed['iaq_global'] = int(binary[24:27],2)

                parsed['iaq_source'] = int(binary[27:31],2)

                parsed['iaq_dry'] = int(binary[31:34],2)

                parsed['iaq_mould'] = int(binary[34:37],2)

                parsed['iaq_dm'] = int(binary[37:40],2)

                parsed['hci'] = int(binary[40:42],2)

            elif dataarray[0] == 0x64:

                logging.debug('This is insafe+ Pilot Button Press')

                parsed['button'] = 1    

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(nexelec)



# --- Source: nexelec_air.py ---

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

import time

import json

import threading

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



#       Génère un downlink hex (port 56) en fonction du groupe :

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





# --- Source: nexelec_air_2.py ---

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

import time

import json

import threading

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

                    parsed['hardware_status'] = ['OK','Hardware fault'][gs] if gs < 2 else f'Reserved({gs})'

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



#       Génère un downlink hex (port 56) en fonction du groupe :



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



# --- Source: nke.py ---

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

import time

import json

import threading

from binascii import unhexlify



class nke():

    def __init__(self):

        self.name = 'nke'



    def parse(self,data,device):

        logging.debug('Nke Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            if dataarray[0] == 0x11:

                logging.debug('This is endpoint 0')

            if dataarray[1] == 0x0a:

                logging.debug('This is report attribute standard')

                binary = bin(int(str(dataarray[1])))[2:].zfill(8)

                if dataarray[2] == 0x04 and dataarray[3] == 0x02:

                    logging.debug('This is temperature measurement')

                    if dataarray[4] == 0x00 and dataarray[5] == 0x00:

                        logging.debug('This is real measurement')

                        parsed['temperature'] = int(hex( (dataarray[7]<<8) | dataarray[8] ),16)/100

                        logging.debug("Brut Value : " + str(parsed['temperature']))

                        if parsed['temperature'] > 100:

                            logging.debug('Negative value detected')

                            parsed['temperature'] = (655.35 - parsed['temperature'])*(-1)

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(nke)



# --- Source: nke_batch.py ---

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

import time

import json

import threading

from binascii import unhexlify

# from .batchnke import batchnke



class nke_batch():

    def __init__(self):

        self.name = 'nke_batch'



    def parse(self,data,device):

        structDict = {"nke_atmo": {

                                "size":3, 

                                "args": [{'taglbl': 0, "lblname": "temperature", 'resol': 1.0, 'sampletype': 7}, 

                                        {'taglbl': 1, "lblname": "humidity", 'resol': 1.0, 'sampletype': 6},

                                        {'taglbl': 2, "lblname": "pression", 'resol': 1.0, 'sampletype': 7},

                                        {'taglbl': 3, 'resol': 1.0, 'sampletype': 10},

                                        {'taglbl': 4, 'resol': 1.0, 'sampletype': 10},

                                        {'taglbl': 5, "lblname": "battery", 'resol': 1.0, 'sampletype': 6}]

                                },

                        "nke_celso": {

                                "size":1, 

                                "args": [{'taglbl': 0, "lblname": "temperature", 'resol': 10.0, 'sampletype': 7}, 

                                        {'taglbl': 1, "lblname": "temperature2", 'resol': 100.0, 'sampletype': 6}]

                                },

                        "nke_pulsesenso": {

                                "size":4, 

                                "args": [{'taglbl': 0, "lblname": "index1", 'resol': 1.0, 'sampletype': 10}, 

                                        {'taglbl': 1, "lblname": "index2", 'resol': 1.0, 'sampletype': 10}, 

                                        {'taglbl': 2, "lblname": "index3", 'resol': 1.0, 'sampletype': 10}, 

                                        {'taglbl': 3, "lblname": "state1", 'resol': 1.0, 'sampletype': 1}, 

                                        {'taglbl': 4, "lblname": "state2", 'resol': 1.0, 'sampletype': 1}, 

                                        {'taglbl': 5, "lblname": "state3", 'resol': 1.0, 'sampletype': 1}, 

                                        {'taglbl': 6, "lblname": "battery", 'resol': 100.0, 'sampletype': 6}, 

                                        {'taglbl': 7, "lblname": "multistate", 'resol': 1.0, 'sampletype': 6}]

                                },

                        "nke_indoor": {

                                "size":2, 

                                "args": [{'taglbl': 0, "lblname": "temperature", 'resol': 10.0, 'sampletype': 7}, 

                                        {'taglbl': 1, "lblname": "humidity", 'resol': 100.0, 'sampletype': 6},

                                        {'taglbl': 2, "lblname": "battery", 'resol': 1.0, 'sampletype': 6},

                                        {'taglbl': 3, "lblname": "open", 'resol': 1.0, 'sampletype': 1}]

                                }

                    }

        logging.debug('Nke_batch Received for device ' + str(device))

        parsed={}

        data['parsed'] = parsed

        try:

            if device in structDict:

                parser = structDict[device]

                result = batchnke.uncompress(parser['size'],parser['args'],data['payload'])

                logging.debug(str(result))

                if 'dataset' in result:

                    for datas in result['dataset']:

                        if 'data' in datas:

                            logging.debug(datas['data'])

                            value = datas['data']['value']

                            if datas['data']['label_name'] in ['temperature','humidity']:

                                value = datas['data']['value']/100

                            parsed[datas['data']['label_name']] = value

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(nke_batch)



# --- Source: nke_bob.py ---

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

import time

import json

import threading

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



# --- Source: nke_filpilote.py ---

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

import time

import json

import threading

from binascii import unhexlify



class nke_filpilote():

    def __init__(self):

        self.name = 'nke_filpilote'



    def parse(self,data,device):

        logging.debug('Nke Fil Pilote Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            payload = data['payload']

            logging.debug('Parsing')

            l = len(payload)

            state = payload[l - 1:]

            if state == '0':

                parsed['state'] = 'Comfort'

            elif state == '1':

                parsed['state'] = 'Economic'

            elif state == '2':

                parsed['state'] = 'Antifreeze'

            elif state == '3':

                parsed['state'] = 'Stop'

            elif state == '4':

                parsed['state'] = 'Comfort -1°C'

            elif state == '5':

                parsed['state'] = 'Comfort -2°C'

            else:

                parsed['state'] = 'ERROR'

            logging.debug('State .... ' + str(parsed['state']))

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(nke_filpilote)



# --- Source: nke_flasho.py ---

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

import time

import json

import threading

from binascii import unhexlify



class nke_flasho():

    def __init__(self):

        self.name = 'nke_flasho'



    def parse(self,data,device):

        logging.debug('Nke Flasho Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            payload = data['payload']

            logging.debug('Parsing')

            if dataarray[0] == 0x11:

                logging.debug('This is endpoint 0')

            if dataarray[1] == 0x0a:

                logging.debug('This is report attribute standard')

                parsed['COUNTER1'] = int(payload[14:22], 16)

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(nke_flasho)



# --- Source: nke_ino.py ---

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

import time

import json

import threading

from binascii import unhexlify



class nke_ino():

    def __init__(self):

        self.name = 'nke_ino'



    def parse(self,data,device):

        logging.debug('Nke Ino Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            payload = data['payload']

            logging.debug('Parsing')



            if payload[2:4] == '0a':

                logging.debug('Report attributes')

                cluser = payload[4:6] + payload[6:8]



                endPoint = payload[0:2]

                if endPoint == '11':

                    connectorPhase = 'Input1'

                elif endPoint == '31':

                    connectorPhase = 'Input2'

                elif endPoint == '51':

                    connectorPhase = 'Input3'

                elif endPoint == '71':

                    connectorPhase = 'Input4'

                elif endPoint == '91':

                    connectorPhase = 'Input5'

                elif endPoint == 'B1':

                    connectorPhase = 'Input6'

                elif endPoint == 'D1':

                    connectorPhase = 'Input7'

                elif endPoint == 'F1':

                    connectorPhase = 'Input8'

                elif endPoint == '13':

                    connectorPhase = 'Input9'

                elif endPoint == '33':

                    connectorPhase = 'Input10'

                logging.debug('End point : ' + connectorPhase)



                attributeID = payload[8:10] + payload[10:12]

                if attributeID == '0055':

                    dataType = 'PresentValue'

                elif attributeID == '0402':

                    dataType = 'Count'

                logging.debug('dataType : ' + dataType)



                attributeType = payload[12:14]

                logging.debug('attributeType : ' + attributeType)

                if attributeType == '10':

                    logging.debug('Binary Input State')

                    state = int(payload[14:], 16)

                    parsed['binaryInputState_' + connectorPhase] = state



                else:

                    logging.debug('Count State')

                    state = int(payload[14:], 16)

                    parsed['countState_' + connectorPhase] = state



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(nke_ino)



# --- Source: nke_intenso.py ---

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

import time

import json

import threading

from binascii import unhexlify



class nke_intenso():

    def __init__(self):

        self.name = 'nke_intenso'



    def parse(self,data,device):

        logging.debug('Nke Intenso Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            payload = data['payload']

            logging.debug('Parsing')

            if dataarray[0] == 0x31:

                logging.debug('This is endpoint for current')

            if dataarray[1] == 0x0a:

                logging.debug('This is report attribute standard')

                parsed['CURRENT'] = struct.unpack('!f', bytes.fromhex(payload[14:22]))[0]

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(nke_intenso)



# --- Source: nke_tic.py ---

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

import subprocess

import time

import os

import json

import threading

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









# --- Source: nke_torano.py ---

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

import time

import json

import threading

from binascii import unhexlify



class nke_torano():

    def __init__(self):

        self.name = 'nke_torano'



    def parse(self,data,device):

        logging.debug('Nke Torano Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            payload = data['payload']

            logging.debug('Parsing')



            logging.debug(payload[4:8])

            if payload[4:8] == '000c':

                logging.debug('Analog Input Report')

                parsed['AnalogInput'] = struct.unpack('!f', bytes.fromhex(payload[14:22]))[0]



            elif payload[4:8] == '0050':

                logging.debug('Configuration Report')

                parsed['battery'] = struct.unpack('!B', bytes.fromhex(payload[14:16]))[0]



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(nke_torano)



# --- Source: nke_triphaso.py ---

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

import time

import json

import threading

from binascii import unhexlify



class nke_triphaso():

    def __init__(self):

        self.name = 'nke_triphaso'



    def parse(self,data,device):

        logging.debug('Nke Triphaso Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            payload = data['payload']

            logging.debug('Parsing')



            if payload[2:4] == '0a':

                logging.debug('Report attributes')

                cluser = payload[4:6] + payload[6:8]

                connector = payload[0:2]



                if connector == '11':

                    logging.debug('Phase A')

                    connectorPhase = 'PhaseA'

                elif connector == '31':

                    logging.debug('Phase B')

                    connectorPhase = 'PhaseB'

                elif connector == '51':

                    logging.debug('Phase C')

                    connectorPhase = 'PhaseC'

                elif connector == '71':

                    logging.debug('Phase A+B+C')

                    connectorPhase = 'PhaseABC'



                if cluser == '800a':

                    logging.debug('Energy and power metering')

                    positiveActiveEnergy = int(payload[16:24],16)

                    parsed['positiveActiveEnergy_'+connectorPhase] = positiveActiveEnergy

                    negativeActiveEnergy = int(payload[24:32], 16)

                    parsed['negativeActiveEnergy_'+connectorPhase] = negativeActiveEnergy

                    positiveReactiveEnergy = int(payload[32:40], 16)

                    parsed['positiveReactiveEnergy_'+connectorPhase] = positiveReactiveEnergy

                    negativeReactiveEnergy = int(payload[40:48], 16)

                    parsed['negativeReactiveEnergy_'+connectorPhase] = negativeReactiveEnergy

                    positiveActivePower = int(payload[48:56], 16)

                    parsed['positiveActivePower_'+connectorPhase] = positiveActivePower

                    negativeActivePower = int(payload[56:64], 16)

                    parsed['negativeActivePower_'+connectorPhase] = negativeActivePower

                    positiveReactivePower = int(payload[64:72], 16)

                    parsed['positiveReactivePower_'+connectorPhase] = positiveReactivePower

                    negativeReactivePower = int(payload[72:80], 16)

                    parsed['negativeReactivePower_'+connectorPhase] = negativeReactivePower



                elif cluser == '800b':

                    logging.debug('Voltage an current metering')

                    voltage = int(payload[16:20], 16)/10

                    parsed['voltage_' + connectorPhase] = voltage

                    current = int(payload[20:24], 16)/10

                    parsed['current_' + connectorPhase] = current

                    angle = int(payload[24:28], 16) - 360

                    parsed['angleVoltageCurrent_' + connectorPhase] = angle



                elif cluser == '000f':

                    logging.debug('Binary Input State')

                    state = int(payload[14:16], 16)

                    parsed['binaryInputState_' + connectorPhase] = state



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(nke_triphaso)



# --- Source: occion.py ---

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

import time

import json

import threading



class occion():

    def __init__(self):

        self.name = 'occion'



    def parse(self,data,device):

        logging.debug('Occion Received')

        parsed={}

        data['parsed'] = parsed

        try:

            logging.debug('Parsing')

            payload = data['payload']

            parsed['battery'] = (int(payload[16:20], 16) - int("8000", 16)) / 100

            if payload[20:21] == "7" :

                value = int("8000", 16) - int(payload[20:24], 16)

                parsed['temperature'] = (value / 100)*(-1) 

            elif payload[20:21] == "8" :

                parsed['temperature'] = (int(payload[20:24], 16) - int("8000", 16)) / 100

            parsed['humidity'] = (int(payload[24:28], 16) - int("8000", 16)) / 100

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(occion)



# --- Source: PE6v2.py ---

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

import time

import json

import threading

from binascii import unhexlify



class PE6v2():

    def __init__(self):

        self.name = 'PE6v2'



    def parse(self,data,device):

        logging.debug('PE6v2 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            frameType = payload[0:2]

            if frameType == '01':

               parsed['headerType'] = 'Active energy index'

               parsed['headerUnit'] = 'kWh'

            elif frameType == '02':

               parsed['headerType'] = 'Reactive energy index'

               parsed['headerUnit'] = 'kvarh'

            offset = 2

            channelNb = 1



            CHANNEL_MODES = [ '', 'Mono-phase', 'Three-phase with neutral', 'Balanced three-phase with neutral', 'Three-phase without neutral', 'Balanced three-phase without neutral' ]



            def getChannelInfo(offset, channelNb):

                # Channel

               channel = bin(int(payload[offset:offset+2], 16))[2:].zfill(8)

               connecteurID = int(channel[0:3],2)

               voieID = int(channel[3:5],2)

               modeID = 'Mode-Connecteur' + str(connecteurID)

               # Mode

               parsed[modeID] = CHANNEL_MODES[int(channel[5:8],2)]

               # Connecteur

               parsed[connecteurID] = int(channel[0:3],2)

               offset = offset + 2

               # Index

               indexID = 'Index' + str(connecteurID) + '.' + str(voieID)

               little_hex = bytearray.fromhex(payload[offset:offset+8])

               little_hex.reverse()

               hex_string = ''.join(format(x, '02x') for x in little_hex)

               floatVal = struct.unpack('!f', bytes.fromhex(hex_string))[0]

               parsed[indexID] = round(floatVal,3)

               offset = offset + 8

               channelNb = channelNb + 1

               return offset,channelNb



            result, channelNb = getChannelInfo(offset, channelNb)

            nbConnecteur = int((len(dataarray)-1)/5)

            while(channelNb < nbConnecteur+1):

               result, channelNb = getChannelInfo(result,channelNb)



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(PE6v2)



# --- Source: quandify_cubicMeter.py ---

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

import time

import json

import threading



class quandify_cubicMeter():

    def __init__(self):

        self.name = 'quandify_cubicMeter'



    def parse(self,data,device):

        logging.debug('quandify_cubicMeter Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            logging.debug(payload)



            def decode_uplink(input):

                decoded = None

                if get_packet_type(input["fPort"]) == "periodicReport" or get_packet_type(input["fPort"]) == "alarmReport":

                    decoded = periodic_report_decoder(input["bytes"])

                return {

                    "data" : {

                        "type": get_packet_type(input["fPort"]),

                        "decoded" : decoded,

                        "hexBytes": to_hex_string(input["bytes"]),

                        "fport": input["fPort"],

                        "length": len(input["bytes"])

                    },

                    "warnings": [],

                    "errors": []

                }



            def get_packet_type(type):

                if type == 0:

                    return "ping"  # empty ping message

                elif type == 1:

                    return "periodicReport"  # periodic message

                elif type == 2:

                    return "alarmReport"  # same as periodic but pushed due to an urgent alarm

                else:

                    return "Unknown"



            def periodic_report_decoder(bytes):

                buffer = bytearray(bytes)

                data = buffer

                if len(bytes) < 28:

                    raise ValueError("payload too short")



                parsed['errorCode'] = data[4] if data[4] else "No Error"  # current error code > 419

                parsed['totalVolume'] = data[6]  # All-time aggregated water usage in litres

                parsed['leakStatus'] = get_leak_state(data[22])  # current water leakage state

                parsed['batteryStatus'] = decode_battery_status(data[23], data[24])  # current battery state

                parsed['waterTempMin'] = decode_temperature_C(data[25])  # min water temperature since last periodicReport

                parsed['waterTempMax'] = decode_temperature_C(data[26])  # max water temperature since last periodicReport

                parsed['ambientTemp'] = decode_temperature_C(data[27])  # current ambient temperature



            def to_hex_string(byte_array):

                return "".join(format(byte, "02X") for byte in byte_array)



            # Smaller water leakages only available when using Quandify platform API

            def get_leak_state(input):

                if input <= 2:

                    return "NoLeak"

                elif input == 3:

                    return "Medium"

                elif input == 4:

                    return "Large"

                else:

                    return "N/A"



            def decode_battery_status(input1, input2):

                level = 1800 + (input2 << 3)  # convert to status

                if level <= 3100:

                    return "LOW_BATTERY"

                else:

                    return "OK"



            def decode_temperature_C(input):

                return input * 0.5 - 20  # to °C



            def hex_to_bytes(hex_string):

                bytes_array = []

                for c in range(0, len(hex_string), 2):

                    bytes_array.append(int(hex_string[c:c+2], 16))

                return bytes_array



            input_data = {

                "fPort": 1,

                "bytes" : hex_to_bytes(payload)  # Example bytes, replace with actual data

            }



            result = decode_uplink(input_data)



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(quandify_cubicMeter)



# --- Source: rak2171.py ---

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

import time

import json

import threading

from binascii import unhexlify

from datetime import datetime



class rak2171():

    def __init__(self):

        self.name = 'rak2171'



    def parse(self,data,device):

        logging.debug('rak2171 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            payload = data['payload']

            logging.debug('Parsing')

            logging.debug(payload)



            if payload[0:2] == 'ca':

                logging.debug('Payload Type > No Location')

                parsed['payloadType'] = 'No location payload > GPS has no fix'

                parsed['messageID'] = int(payload[2:4],16)

                parsed['applicationID'] = int(payload[4:12],16)

                parsed['deviceID'] = int(payload[12:20],16)

                parsed['battery'] = int(payload[20:22],16)

                timestamp = int(payload[22:30], 16)

                dt_object = datetime.utcfromtimestamp(timestamp)

                parsed['time'] = dt_object.strftime('%Y-%m-%d %H:%M:%S')

                status = bin(int(payload[30:32],16))[2:].zfill(8)

                parsed['epo'] = status[7:8]

                parsed['charging'] = status[6:7]

                if status[4:6] == '00':

                    parsed['status'] = "Open the GPS fix"

                elif status[4:6] == '01':

                    parsed['status'] = "Locating"

                elif status[4:6] == '10':

                    parsed['status'] = "Successful"

                elif status[4:6] == '11':

                    parsed['status'] = "Failed"



            elif payload[0:2] == 'cb':

                logging.debug('Payload Type > Location')

                parsed['payloadType'] = 'Location payload > GPS has a fix'

                parsed['messageID'] = int(payload[2:4],16)

                parsed['applicationID'] = int(payload[4:12],16)

                parsed['deviceID'] = int(payload[12:20],16)

                parsed['longitude'] = int(payload[20:28],16)

                parsed['latitude'] = int(payload[28:36],16)

                parsed['accuracy'] = int(payload[36:38],16)

                parsed['gpsNumber'] = int(payload[38:40],16)

                parsed['battery'] = int(payload[40:42],16)

                timestamp = int(payload[42:50], 16)

                dt_object = datetime.utcfromtimestamp(timestamp)

                parsed['time'] = dt_object.strftime('%Y-%m-%d %H:%M:%S')

                if status[50:52] == '00':

                    parsed['status'] = "Open the GPS fix"

                elif status[50:52] == '01':

                    parsed['status'] = "Locating"

                elif status[50:52] == '10':

                    parsed['status'] = "Successful"

                elif status[50:52] == '11':

                    parsed['status'] = "Failed"



            elif payload[0:2] == 'cc':

                logging.debug('Payload Type > Send SOS')

                parsed['payloadType'] = 'Send SOS Payload'

                parsed['messageID'] = int(payload[2:4],16)

                parsed['applicationID'] = int(payload[4:12],16)

                parsed['deviceID'] = int(payload[12:20],16)

                parsed['longitude'] = int(payload[20:28],16)

                parsed['latitude'] = int(payload[28:36],16)



            elif payload[0:2] == 'cd':

                logging.debug('Payload Type > Cancel SOS')

                parsed['payloadType'] = 'Cancel SOS Payload'

                parsed['sos'] = 0

                parsed['messageID'] = int(payload[2:4],16)

                parsed['applicationID'] = int(payload[4:12],16)

                parsed['deviceID'] = int(payload[12:20],16)



            elif payload[0:2] == 'ce':

                logging.debug('Payload Type > 6-level alarm')

                parsed['payloadType'] = '6-level Sensitivity Alarm Payload'

                parsed['messageID'] = int(payload[2:4],16)

                parsed['applicationID'] = int(payload[4:12],16)

                parsed['deviceID'] = int(payload[12:20],16)

                if payload[20:22] == '1':

                    parsed['level'] = "Mild Vibration"

                elif payload[20:22] == '2':

                    parsed['level'] = "Violent Vibration"

                elif payload[20:22] == '3':

                    parsed['level'] = "Movement"

                elif payload[20:22] == '4':

                    parsed['level'] = "Mild Shaking"

                elif payload[20:22] == '5':

                    parsed['level'] = "Violent Shaking"

                elif payload[20:22] == '6':

                    parsed['level'] = "Fall"



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(rak2171)



# --- Source: rak7205.py ---

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

import time

import json

import threading

from binascii import unhexlify



class rak7205():

    def __init__(self):

        self.name = 'rak7205'



    def parse(self,data,device):

        logging.debug('rak7205 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            payload = data['payload']

            logging.debug('Parsing')

            while len(payload) > 4 :

                flag = payload[0:4]

                if flag == "0768":

                    parsed['humidity'] = int(payload[4:6], 16) * 0.5

                    payload = payload[6:];

                elif flag == "0673":

                    parsed['pressure'] = int(payload[4:8], 16) * 0.1

                    payload = payload[8:];

                elif flag == "0267":

                    parsed['temperature'] = int(payload[4:8], 16) * 0.1

                    payload = payload[8:];

                elif flag == "0188":

                    parsed['latitude'] = int(payload[4:10], 16) * 0.0001

                    parsed['longitude'] = int(payload[10:16], 16) * 0.0001

                    parsed['altitude'] = int(payload[16:22], 16) * 0.01

                    payload = payload[22:];

                elif flag == "0371":

                    parsed['accelerationx'] = int(payload[4:8], 16) * 0.0001

                    parsed['accelerationy'] = int(payload[8:12], 16) * 0.0001

                    parsed['accelerationz'] = int(payload[12:16], 16) * 0.01

                    payload = payload[16:];

                elif flag == "0402":

                    parsed['gas'] = int(payload[4:8], 16) * 0.01

                    payload = payload[8:];

                elif flag == "0802":

                    parsed['battery'] = round(int(payload[4:8], 16) * 0.01,2)

                    payload = payload[8:];

                elif flag == "0586":

                    payload = payload[16:];

                elif flag == "0902":

                    payload = payload[8:];

                elif flag == "0a02":

                    payload = payload[8:];

                elif flag == "0b02":

                    payload = payload[28:];

                else :

                    payload = payload[7:];

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(rak7205)



# --- Source: rakc15003.py ---

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

import time

import json

import threading

from binascii import unhexlify



class rakc15003():

    def __init__(self):

        self.name = 'rakc15003'



    def parse(self,data,device):

        logging.debug('rakc15003 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            payload = data['payload']

            logging.debug('Parsing')

            while len(payload) > 4 :

                flag = payload[2:4]

                if flag == "67":

                    if 'temperature' not in parsed:

                        parsed['temperature'] = int(payload[4:8], 16) * 0.1

                        payload = payload[8:]

                        continue

                    if 'temperature2' not in parsed:

                        parsed['temperature2'] = int(payload[4:8], 16) * 0.1

                        payload = payload[8:]

                        continue

                elif flag == "68":

                    parsed['humidity'] = int(payload[4:6], 16) * 0.5

                    payload = payload[6:]

                elif flag == "73":

                    parsed['pressure'] = int(payload[4:8], 16) * 0.1

                    payload = payload[8:]

                else:

                    break



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(rakc15003)



# --- Source: senlabM.py ---

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

import time

import json

import threading

from binascii import unhexlify



class senlabM():

    def __init__(self):

        self.name = 'senlabM'



    def parse(self,data,device):

        #02dc8e179c100000222a

        logging.debug('SenlabM Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            pulse=str(int(utils.to_hex_string([dataarray[-4],dataarray[-3],dataarray[-2],dataarray[-1]]),16))

            logging.debug('Pulse is ' + str(pulse))

            parsed['pulse']=pulse

            parsed['battery']=int(hex(dataarray[1]),16)/254*100

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(senlabM)



# --- Source: SHE_MIO_LORA_V2.py ---

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

import time

import json

import threading



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



# --- Source: uRadMonitor_A3.py ---

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

import time

import json

import threading



class uRadMonitor_A3():

    def __init__(self):

        self.name = 'uRadMonitor_A3'



    def parse(self,data,device):

        logging.debug('uRadMonitor_A3 Received')

        parsed={}

        data['parsed'] = parsed

        try:

            dataarray = utils.hexarray_from_string(data['payload'])

            logging.debug('Parsing')

            payload = data['payload']

            logging.debug(payload)

            parsed['id'] = payload[0:8]

            parsed['versionHW'] = int(payload[8:10],16)

            parsed['versionSW'] = int(payload[10:12],16)

            parsed['timestamp'] = int(payload[12:20],16)

            parsed['temperature'] = (int(payload[20:24],16))/100

            parsed['pression'] = int(payload[24:28],16) + 65535

            parsed['humidity'] = (int(payload[28:30],16))/2

            parsed['voc'] = (int(payload[30:36],16))/1000

            parsed['noise'] = (int(payload[36:38],16))/2

            parsed['CO2'] = int(payload[38:42],16)

            parsed['formaldehyde'] = int(payload[42:46],16)

            parsed['ozone'] = int(payload[46:50],16)

            parsed['PM1'] = int(payload[50:54],16)

            parsed['PM25'] = int(payload[54:58],16)

            parsed['PM10'] = int(payload[58:62],16)

        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(uRadMonitor_A3)



# --- Source: vega.py ---

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

import time

import json

import threading

from binascii import unhexlify



class vega():

    def __init__(self):

        self.name = 'vega'



    def parse(self,data,device):

        logging.debug('Vega Received')

        parsed={}

        data['parsed'] = parsed

        payload = data['payload']

        if device == "vega_si-11":

            try:

                dataarray = utils.hexarray_from_string(data['payload'])

                logging.debug('Parsing')

                if dataarray[0] == 0x01:

                    parsed['battery'] = int(dataarray[1])

                    parsed['temperature'] = int(dataarray[7])

                    parsed['input1'] = str(int(utils.to_hex_string([dataarray[11],dataarray[10],dataarray[9],dataarray[8]]),16))

                    parsed['input2'] = str(int(utils.to_hex_string([dataarray[15],dataarray[14],dataarray[13],dataarray[12]]),16))

                    parsed['input3'] = str(int(utils.to_hex_string([dataarray[19],dataarray[18],dataarray[17],dataarray[16]]),16))

                    parsed['input4'] = str(int(utils.to_hex_string([dataarray[23],dataarray[22],dataarray[21],dataarray[20]]),16))

            except Exception as e:

                logging.debug(str(e))

                logging.debug('Unparsable data')

        if device == "vega_si-11-REV2":

            try:

                dataarray = utils.hexarray_from_string(data['payload'])

                logging.debug('Parsing')

                if(len(dataarray) == 24):

                    if dataarray[0] in [0x00,0x01,0x02,0x03,0x04]:

                        parsed['battery'] = int(dataarray[1])

                        parsed['temperature'] = int(dataarray[6])

                        parsed['input1'] = str(int(utils.to_hex_string([dataarray[10],dataarray[9],dataarray[8],dataarray[7]]),16))

                        parsed['input2'] = str(int(utils.to_hex_string([dataarray[14],dataarray[13],dataarray[12],dataarray[11]]),16))

                        parsed['input3'] = str(int(utils.to_hex_string([dataarray[18],dataarray[17],dataarray[16],dataarray[15]]),16))

                        parsed['input4'] = str(int(utils.to_hex_string([dataarray[22],dataarray[21],dataarray[20],dataarray[19]]),16))

                        # --- Décodage du byte de configuration (dataarray[23]) ---

                        conf_byte = dataarray[23]



                        # Bit 0 : Confirmed uplinks

                        parsed['confirmed_uplink'] = '1' if (conf_byte & 0b00000001) else '0'



                        # Bits 1-3 : période de communication

                        period_code = (conf_byte >> 1) & 0b00000111

                        period_map = {

                            0b000: '5 minutes',

                            0b100: '15 minutes',

                            0b010: '30 minutes',

                            0b110: '1 hour',

                            0b001: '6 hours',

                            0b101: '12 hours',

                            0b011: '24 hours'

                        }

                        parsed['communication_period'] = period_map.get(period_code, 'unknown')



                        # Bits 4-7 : types d’entrée (0=pulse, 1=security)

                        parsed['input1_type'] = 'security' if (conf_byte & 0b00010000) else 'pulse'

                        parsed['input2_type'] = 'security' if (conf_byte & 0b00100000) else 'pulse'

                        parsed['input3_type'] = 'security' if (conf_byte & 0b01000000) else 'pulse'

                        parsed['input4_type'] = 'security' if (conf_byte & 0b10000000) else 'pulse'



            except Exception as e:

                logging.debug(str(e))

                logging.debug('Unparsable data')

        if device == "vega_td-11":

            try:

                dataarray = utils.hexarray_from_string(data['payload'])

                logging.debug('Parsing')

                if dataarray[0] == 0x01:

                    parsed['battery'] = int(dataarray[1])

                    parsed['temperature'] = int(utils.to_hex_string([dataarray[8],dataarray[7]]),16)/10

                    if parsed['temperature'] > 100:

                        parsed['temperature'] = (6553.5-parsed['temperature'])*-1

                    parsed['output'] = int(dataarray[11])

            except Exception as e:

                logging.debug(str(e))

                logging.debug('Unparsable data')

        if device == "vega_SMART-MC0101":

            try:

                dataarray = utils.hexarray_from_string(data['payload'])

                logging.debug('Parsing')

                if dataarray[0] == 0x01:

                    binary = str(bin(int(payload, 16))[2:])

                    parsed['battery'] = int(dataarray[1])

                    parsed['temperature'] = int(utils.to_hex_string([dataarray[4],dataarray[3]]),16)/10

                    parsed['open1'] = int(binary[48:49],2)

                    parsed['open2'] = int(binary[49:50],2)

            except Exception as e:

                logging.debug(str(e))

                logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(vega)



# --- Source: woMaster_LR144.py ---

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

import time

import json

import threading

from binascii import unhexlify



class woMaster_LR144():

    def __init__(self):

        self.name = 'woMaster_LR144'







    def parse(self,data,fPort):

        logging.debug('woMaster_LR144 Received')

        parsed={}

        data['parsed'] = parsed

        try:



            def convertHex(value):

               little_hex = bytearray.fromhex(value)

               little_hex.reverse()

               hex_string = ''.join(format(x, '02x') for x in little_hex)

               #logging.debug(hex_string)

               return hex_string



            def ascii_to_string(ascii_code):

                # Convert the ASCII code (hex format) to bytes, then decode to string

                byte_data = bytes.fromhex(ascii_code)

                return byte_data.decode('utf-8', errors='ignore').strip('\x00')  # 'ignore' skips invalid characters





            payload = data['payload']

            logging.debug("Fport is " + fPort)



            if fPort == '4':

                logging.debug('Hearbeat uplink') # 0a095704030285d10000e2

                # 05192200030a0000000000000000000000000000000000000000e2 (fport 4)

                # 0000501400000000e8033000 (fport 223)

                # 00007c1500000000e8032d00



            elif fPort == '223':

                if len(payload) == 24:

                    logging.debug('Remote control uplink')

                    parsed['currentOutput'] = int(convertHex(payload[0:4]),16)

                    parsed['voltageOutput'] = int(convertHex(payload[4:8]),16)/100

                    parsed['pwm5Vfrequency'] = int(convertHex(payload[8:12]),16)

                    parsed['pwm5VdutyCycle'] = int(convertHex(payload[12:16]),16)

                    parsed['pwm10Vfrequency'] = int(convertHex(payload[16:20]),16)

                    parsed['pwm10VdutyCycle'] = int(convertHex(payload[20:24]),16)



            if len(payload) == 24:

                logging.debug('Remote control uplink')

                parsed['currentOutput'] = int(convertHex(payload[0:4]),16)

                parsed['voltageOutput'] = int(convertHex(payload[4:8]),16)/100

                parsed['pwm5Vfrequency'] = int(convertHex(payload[8:12]),16)

                parsed['pwm5VdutyCycle'] = int(convertHex(payload[12:16]),16)

                parsed['pwm10Vfrequency'] = int(convertHex(payload[16:20]),16)

                parsed['pwm10VdutyCycle'] = int(convertHex(payload[20:24]),16)



        except Exception as e:

            logging.debug(str(e))

            logging.debug('Unparsable data')

        data['parsed'] = parsed

        return data



globals.COMPATIBILITY.append(woMaster_LR144)



# --- UNIFIED DECODER CLASS ---



# --- GENERIC DECODERS (JS REPLACEMENTS) ---




# --- GENERIC DECODERS (JS REPLACEMENTS) ---

class GenericIPSODecoder:
    def __init__(self):
        self.name = 'milesight_generic'

    def parse(self, data, device):
        payload_hex = data.get('payload', '')
        bytes_data = utils.hexarray_from_string(payload_hex)
        parsed = {}
        i = 0
        while i < len(bytes_data):
            try:
                channel_id = bytes_data[i]
                channel_type = bytes_data[i+1]
                i += 2
                if channel_id == 0xFF and channel_type == 0x01:
                    parsed['ipso_version'] = f"v{bytes_data[i]>>4}.{bytes_data[i]&0x0F}"
                    i += 1
                elif channel_id == 0xFF and channel_type == 0x09:
                    parsed['hardware_version'] = f"v{bytes_data[i]}.{bytes_data[i+1]>>4}"
                    i += 2
                elif channel_id == 0xFF and channel_type == 0x0A:
                    parsed['firmware_version'] = f"v{bytes_data[i]}.{bytes_data[i+1]}"
                    i += 2
                elif channel_type == 0x75:
                    parsed['battery'] = bytes_data[i]
                    i += 1
                elif channel_type == 0x67:
                    val = struct.unpack('<h', bytes(bytes_data[i:i+2]))[0]
                    parsed['temperature'] = val / 10.0
                    i += 2
                elif channel_type == 0x68:
                    parsed['humidity'] = bytes_data[i] / 2.0
                    i += 1
                elif channel_type == 0x7D:
                    parsed['co2'] = struct.unpack('<H', bytes(bytes_data[i:i+2]))[0]
                    i += 2
                elif channel_type == 0x73:
                    parsed['pressure'] = struct.unpack('<H', bytes(bytes_data[i:i+2]))[0] / 10.0
                    i += 2
                elif channel_type == 0x65:
                    parsed['illuminance'] = struct.unpack('<H', bytes(bytes_data[i:i+2]))[0]
                    i += 2
                elif channel_type == 0x88:
                    lat = struct.unpack('<i', bytes(bytes_data[i:i+4]))[0] / 1000000
                    lon = struct.unpack('<i', bytes(bytes_data[i+4:i+8]))[0] / 1000000
                    i += 8
                    parsed['latitude'] = lat
                    parsed['longitude'] = lon
                elif channel_type == 0x00:
                     parsed[f'digital_in_{channel_id}'] = bytes_data[i]
                     i += 1
                else: break
            except Exception as e:
                parsed['error_decoding'] = str(e)
                break
        data['parsed'] = parsed
        return data

globals.COMPATIBILITY.append(GenericIPSODecoder)

class GenericDraginoDecoder:
    def __init__(self):
        self.name = 'dragino_generic'
    def parse(self, data, device):
        payload_hex = data.get('payload', '')
        bytes_data = utils.hexarray_from_string(payload_hex)
        parsed = {'raw_data_count': len(bytes_data)}
        data['parsed'] = parsed
        return data
# globals.COMPATIBILITY.append(GenericDraginoDecoder)

# --- USER RESTORED DECODERS ---

class NexelecDecoder(BaseDecoder): 
    def decode_uplink(self, input_bytes):
        try:
            string_hex = self.bytes_to_string(input_bytes)
            octet_type_produit = int(string_hex[2:4], 16)
            octet_type_message = int(string_hex[4:6], 16)
            data = self.data_output(octet_type_message, string_hex)
            return {"data": data, "errors": None, "warnings": None}
        except Exception as e:
            return {"data": None, "errors": str(e), "warnings": "Erreur lors du decodage"}

    def decode_uplink_auto(self, input_data):
        try:
            input_bytes = self.identify_and_process_data(input_data)
            return self.decode_uplink(input_bytes)
        except Exception as e:
            return {"data": None, "errors": str(e), "warnings": "Erreur lors du traitement"}

    def data_output(self, octet_type_message, string_hex):
        if octet_type_message == 0x01: return self.periodic_data_output(string_hex)
        elif octet_type_message == 0x02: return {} # Placeholder
        elif octet_type_message == 0x06: return {} # Placeholder
        else: raise ValueError(f"Type de message inconnu : {octet_type_message}")

    def periodic_data_output(self, string_hex):
        octet_type_produit = int(string_hex[:2], 16)
        data_temperature = (int(string_hex[4:8], 16) >> 6) & 0x3FF
        data_humidity = int(string_hex[6:9], 16) & 0x3FF
        data_co2 = (int(string_hex[9:13], 16) >> 2) & 0x3FFF
        data_covt = int(string_hex[12:16], 16) & 0x3FFF
        data_luminosity = (int(string_hex[16:19], 16) >> 2) & 0x3FF
        avg_noise_value = (int(string_hex[18:21], 16) >> 2) & 0x7F
        peak_noise_value = (int(string_hex[20:23], 16) >> 3) & 0x7F
        occupancy_rate_value = int(string_hex[22:24], 16) & 0x7F

        return {
            "Fabricant": "Nexelec",
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

    def decode_temperature(self, value): return {"value": (value / 10) - 30, "unit": "C"} if value < 1023 else "Error"
    def decode_humidity(self, value): return {"value": value / 10, "unit": "%RH"} if value < 1023 else "Error"
    def decode_co2(self, value): return {"value": value, "unit": "ppm"} if value < 16383 else "Error"
    def decode_covt(self, value): return {"value": value, "unit": "ug/m3"} if value < 16383 else "Error"
    def decode_luminosity(self, value): return {"value": value * 5, "unit": "lux"} if value < 1023 else "Error"
    def decode_noise(self, value): return {"value": value, "unit": "dB"} if value != 127 else "Error"
    def type_of_product(self, o): return "Nexelec Device"

class WattecoDecoder(BaseDecoder):
    def decode_watteco(self, payload_hex: str) -> dict:
        try:
            header = payload_hex[:8].lower()
            if header == "110a0402":
                return {"Fabricant":"Watteco","Product_type": "THR", "temperature":{"value": int(payload_hex[-4:], 16)/100, "unit": "C"}}
            elif header == "110a0405":
                 return {"Fabricant":"Watteco" ,"Product_type": "THR", "humidity": {"value": int(payload_hex[-4:], 16)/100, "unit": "%RH"}}
            return {"Info": f"Header {header} handled by partial decoder"}
        except Exception as e:
            return {"erreur": str(e)}

# Wrapper classes
class UserNexelecWrapper(NexelecDecoder):
    def __init__(self): self.name = 'nexelec_user'
    def parse(self, data, device):
        payload_hex = data.get('payload', '')
        try:
            input_bytes = bytes.fromhex(payload_hex)
            res = self.decode_uplink(input_bytes)
            return {'parsed': res.get('data', {})}
        except Exception as e: return {'parsed': {'error': str(e)}}

class UserWattecoWrapper(WattecoDecoder):
    def __init__(self): self.name = 'watteco_user'
    def parse(self, data, device):
        return {'parsed': self.decode_watteco(data.get('payload', ''))}

globals.COMPATIBILITY.append(UserNexelecWrapper)
globals.COMPATIBILITY.append(UserWattecoWrapper)

# --- UNIFIED DECODER ---

class UnifiedDecoder:
    def __init__(self):
        self.drivers = {}
        self.analysis = {}
        self._load_drivers()
        self._load_analysis()

    def _load_drivers(self):
        print(f"🔌 Registering {len(globals.COMPATIBILITY)} internal drivers...")
        for cls in globals.COMPATIBILITY:
            try:
                instance = cls()
                name = getattr(instance, 'name', cls.__name__)
                self.drivers[name.lower()] = instance
                self.drivers[cls.__name__.lower()] = instance
            except Exception as e: pass

    def _load_analysis(self):
        try:
            with open('deveui_analysis.json', 'r', encoding='utf-8') as f:
                self.analysis = json.load(f)
        except: self.analysis = {}

    def find_driver(self, deveui):
        if not deveui: return None, "No DevEUI"
        clean = deveui.upper().replace("-", "").replace(":", "")

        # 0. User Custom Overrides
        # Try to detect if we should force user decoder based on manufacturer analysis
        manuf = self.analysis.get("manufacturers_by_prefix", {}).get(clean[:6], "")
        if not manuf: manuf = self.analysis.get("manufacturers_by_prefix", {}).get(clean[:7], "")

        if "NEXELEC" in manuf.upper() and "nexelec_user" in self.drivers:
            return self.drivers["nexelec_user"], "User Nexelec Decoder"
        if "WATTECO" in manuf.upper() and "watteco_user" in self.drivers:
            # Only if typical headers? Or just force it.
            return self.drivers["watteco_user"], "User Watteco Decoder"

        # 1. Look in analysis JSON for Model
        models = self.analysis.get("models_by_prefix", {})
        best = None
        for length in range(12, 5, -1):
            if clean[:length] in models:
                best = models[clean[:length]]
                break

        driver = None
        info = ""

        if best:
            target = best.lower().replace("-", "").replace(" ", "")
            for dname in self.drivers:
                if target in dname:
                    driver = self.drivers[dname]
                    info = f"Found driver for {best}"
                    break

        # 2. Manufacturer Fallback
        if not driver:
            if clean.startswith("24E124"): 
                driver = self.drivers.get("milesight_generic")
                info = "Fallback to Generic Milesight"
            elif clean.startswith("A84041"): 
                 driver = self.drivers.get("dragino_lht65")
                 info = "Fallback to Dragino"
            elif clean.startswith("868000"): 
                 driver = self.drivers.get("eastron_sdm630")
                 info = "Fallback to Eastron"

        return driver, info

    def decode_uplink(self, payload_hex, deveui=None):
        driver, info = self.find_driver(deveui)
        data = {'payload': payload_hex}
        parsed = {}
        if driver:
            try:
                res = driver.parse(data, None)
                parsed = res.get('parsed', {})
                parsed['_driver'] = driver.name
                parsed['_info'] = info
            except Exception as e:
                parsed = {"error": str(e), "driver": driver.name}
        else:
             parsed = {"error": "No driver found", "raw": payload_hex, "info": info}
        return parsed

jeedom_decoder = UnifiedDecoder()

 
 #   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
 
 #   R E C O V E R E D   B A T C H N K E   M O D U L E 
 
 #   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
 
 
 
 c l a s s   b a t c h n k e _ c o n s t a n t s : 
 
         S T _ U N D E F   =   0 
 
         S T _ B L   =   1 
 
         S T _ U 4   =   2 
 
         S T _ I 4   =   3 
 
         S T _ U 8   =   4 
 
         S T _ I 8   =   5 
 
         S T _ U 1 6   =   6 
 
         S T _ I 1 6   =   7 
 
         S T _ U 2 4   =   8 
 
         S T _ I 2 4   =   9 
 
         S T _ U 3 2   =   1 0 
 
         S T _ I 3 2   =   1 1 
 
         S T _ F L   =   1 2 
 
 
 
         B R _ H U F F _ M A X _ I N D E X _ T A B L E   =   1 4 
 
         N B _ H U F F _ E L E M E N T   =   1 6 
 
         N U M B E R _ O F _ S E R I E S   =   1 6 
 
 
 
         h u f f   =   [ 
 
                 [ 
 
                         { " s z " :   2 ,   " l b l " :   0 x 0 0 0 } , 
 
                         { " s z " :   2 ,   " l b l " :   0 x 0 0 1 } , 
 
                         { " s z " :   2 ,   " l b l " :   0 x 0 0 3 } , 
 
                         { " s z " :   3 ,   " l b l " :   0 x 0 0 5 } , 
 
                         { " s z " :   4 ,   " l b l " :   0 x 0 0 9 } , 
 
                         { " s z " :   5 ,   " l b l " :   0 x 0 1 1 } , 
 
                         { " s z " :   6 ,   " l b l " :   0 x 0 2 1 } , 
 
                         { " s z " :   7 ,   " l b l " :   0 x 0 4 1 } , 
 
                         { " s z " :   8 ,   " l b l " :   0 x 0 8 1 } , 
 
                         { " s z " :   1 0 ,   " l b l " :   0 x 2 0 0 } , 
 
                         { " s z " :   1 1 ,   " l b l " :   0 x 4 0 2 } , 
 
                         { " s z " :   1 1 ,   " l b l " :   0 x 4 0 3 } , 
 
                         { " s z " :   1 1 ,   " l b l " :   0 x 4 0 4 } , 
 
                         { " s z " :   1 1 ,   " l b l " :   0 x 4 0 5 } , 
 
                         { " s z " :   1 1 ,   " l b l " :   0 x 4 0 6 } , 
 
                         { " s z " :   1 1 ,   " l b l " :   0 x 4 0 7 } , 
 
                 ] , 
 
                 [ 
 
                         { " s z " :   7 ,   " l b l " :   0 x 0 6 f } , 
 
                         { " s z " :   5 ,   " l b l " :   0 x 0 1 a } , 
 
                         { " s z " :   4 ,   " l b l " :   0 x 0 0 c } , 
 
                         { " s z " :   3 ,   " l b l " :   0 x 0 0 3 } , 
 
                         { " s z " :   3 ,   " l b l " :   0 x 0 0 7 } , 
 
                         { " s z " :   2 ,   " l b l " :   0 x 0 0 2 } , 
 
                         { " s z " :   2 ,   " l b l " :   0 x 0 0 0 } , 
 
                         { " s z " :   3 ,   " l b l " :   0 x 0 0 2 } , 
 
                         { " s z " :   6 ,   " l b l " :   0 x 0 3 6 } , 
 
                         { " s z " :   9 ,   " l b l " :   0 x 1 b b } , 
 
                         { " s z " :   9 ,   " l b l " :   0 x 1 b 9 } , 
 
                         { " s z " :   1 0 ,   " l b l " :   0 x 3 7 5 } , 
 
                         { " s z " :   1 0 ,   " l b l " :   0 x 3 7 4 } , 
 
                         { " s z " :   1 0 ,   " l b l " :   0 x 3 7 0 } , 
 
                         { " s z " :   1 1 ,   " l b l " :   0 x 6 e 3 } , 
 
                         { " s z " :   1 1 ,   " l b l " :   0 x 6 e 2 } , 
 
                 ] , 
 
                 [ 
 
                         { " s z " :   4 ,   " l b l " :   0 x 0 0 9 } , 
 
                         { " s z " :   3 ,   " l b l " :   0 x 0 0 5 } , 
 
                         { " s z " :   2 ,   " l b l " :   0 x 0 0 0 } , 
 
                         { " s z " :   2 ,   " l b l " :   0 x 0 0 1 } , 
 
                         { " s z " :   2 ,   " l b l " :   0 x 0 0 3 } , 
 
                         { " s z " :   5 ,   " l b l " :   0 x 0 1 1 } , 
 
                         { " s z " :   6 ,   " l b l " :   0 x 0 2 1 } , 
 
                         { " s z " :   7 ,   " l b l " :   0 x 0 4 1 } , 
 
                         { " s z " :   8 ,   " l b l " :   0 x 0 8 1 } , 
 
                         { " s z " :   1 0 ,   " l b l " :   0 x 2 0 0 } , 
 
                         { " s z " :   1 1 ,   " l b l " :   0 x 4 0 2 } , 
 
                         { " s z " :   1 1 ,   " l b l " :   0 x 4 0 3 } , 
 
                         { " s z " :   1 1 ,   " l b l " :   0 x 4 0 4 } , 
 
                         { " s z " :   1 1 ,   " l b l " :   0 x 4 0 5 } , 
 
                         { " s z " :   1 1 ,   " l b l " :   0 x 4 0 6 } , 
 
                         { " s z " :   1 1 ,   " l b l " :   0 x 4 0 7 } , 
 
                 ] , 
 
         ] 
 
 
 
 #   - - - - - - - - - - - - - - - - - 
 
 #   B A T C H N K E   L O G I C 
 
 #   - - - - - - - - - - - - - - - - - 
 
 f r o m   c o l l e c t i o n s   i m p o r t   n a m e d t u p l e 
 
 i m p o r t   s t r u c t 
 
 f r o m   d a t e t i m e   i m p o r t   d a t e t i m e 
 
 i m p o r t   j s o n 
 
 i m p o r t   c t y p e s 
 
 
 
 T a g   =   n a m e d t u p l e ( " T a g " ,   " s i z e   l b l " ) 
 
 
 
 c l a s s   P r i n t e r : 
 
         d e f   _ _ i n i t _ _ ( s e l f ,   m u t e d = T r u e ) : 
 
                 s e l f . _ m u t e d   =   m u t e d 
 
         d e f   p r i n t ( s e l f ,   m e s s a g e ,   e n d = " \ n " ) : 
 
                 i f   n o t   s e l f . _ m u t e d : 
 
                         p r i n t ( m e s s a g e ,   e n d = e n d ) 
 
         d e f   m u t e ( s e l f ) :   s e l f . _ m u t e d   =   T r u e 
 
         d e f   u n m u t e ( s e l f ) :   s e l f . _ m u t e d   =   F a l s e 
 
 
 
 P   =   P r i n t e r ( m u t e d = T r u e ) 
 
 
 
 c l a s s   S z E r r o r ( E x c e p t i o n ) :   p a s s 
 
 
 
 c l a s s   B u f f e r : 
 
         d e f   _ _ i n i t _ _ ( s e l f ,   b y t e _ a r r a y ) : 
 
                 s e l f . i n d e x   =   0 
 
                 s e l f . a r r a y   =   b y t e _ a r r a y 
 
 
 
         d e f   n e x t _ s a m p l e ( s e l f ,   s a m p l e _ t y p e ,   n b _ b i t s ) : 
 
                 s r c _ b i t _ s t a r t   =   s e l f . i n d e x 
 
                 s e l f . i n d e x   + =   n b _ b i t s 
 
                 i f   s a m p l e _ t y p e   = =   b a t c h n k e _ c o n s t a n t s . S T _ F L   a n d   n b _ b i t s   ! =   3 2 : 
 
                         r a i s e   E x c e p t i o n ( f " M a u v a i s   s a m p l e   t y p e   ( { s a m p l e _ t y p e } ) " ) 
 
                 u 3 2   =   0 
 
                 n b y t e s   =   i n t ( ( n b _ b i t s   -   1 )   /   8 )   +   1 
 
                 n b i t s f r o m b y t e   =   n b _ b i t s   %   8 
 
                 i f   n b i t s f r o m b y t e   = =   0   a n d   n b y t e s   >   0 : 
 
                         n b i t s f r o m b y t e   =   8 
 
 
 
                 w h i l e   n b y t e s   >   0 : 
 
                         b i t _ t o _ r e a d   =   0 
 
                         w h i l e   n b i t s f r o m b y t e   >   0 : 
 
                                 i d x   =   s r c _ b i t _ s t a r t   > >   3 
 
                                 i f   s e l f . a r r a y [ i d x ]   &   ( 1   < <   ( s r c _ b i t _ s t a r t   &   0 x 0 7 ) ) : 
 
                                         u 3 2   | =   1   < <   ( ( n b y t e s   -   1 )   *   8   +   b i t _ t o _ r e a d ) 
 
                                 n b i t s f r o m b y t e   - =   1 
 
                                 b i t _ t o _ r e a d   + =   1 
 
                                 s r c _ b i t _ s t a r t   + =   1 
 
                         n b y t e s   - =   1 
 
                         n b i t s f r o m b y t e   =   8 
 
 
 
                 i f   s a m p l e _ t y p e   i n   ( b a t c h n k e _ c o n s t a n t s . S T _ I 4 , b a t c h n k e _ c o n s t a n t s . S T _ I 8 ,   b a t c h n k e _ c o n s t a n t s . S T _ I 1 6 , b a t c h n k e _ c o n s t a n t s . S T _ I 2 4 )   a n d   u 3 2   &   ( 
 
                         1   < <   ( n b _ b i t s   -   1 ) 
 
                 ) : 
 
                         f o r   i   i n   r a n g e ( n b _ b i t s ,   3 2 ) : 
 
                                 u 3 2   | =   1   < <   i 
 
                                 n b _ b i t s   + =   1 
 
                 
 
                 i f   s a m p l e _ t y p e   i n   ( b a t c h n k e _ c o n s t a n t s . S T _ I 4 , b a t c h n k e _ c o n s t a n t s . S T _ I 8 , b a t c h n k e _ c o n s t a n t s . S T _ I 1 6 ,   b a t c h n k e _ c o n s t a n t s . S T _ I 2 4 , b a t c h n k e _ c o n s t a n t s . S T _ I 3 2 )   a n d   u 3 2   &   ( 
 
                         1   < <   ( n b _ b i t s   -   1 ) 
 
                 ) : 
 
                       r e t u r n   c t y p e s . c _ l o n g ( u 3 2 ) . v a l u e 
 
                 r e t u r n   u 3 2 
 
 
 
         d e f   n e x t _ b i _ f r o m _ h i ( s e l f ,   h u f f _ c o d i n g ) : 
 
                 f o r   i   i n   r a n g e ( 2 ,   1 2 ) : 
 
                         l h u f f   =   s e l f . _ b i t s _ b u f 2 H u f f P a t t e r n ( i ) 
 
                         #   P a t c h i n g   a c c e s s   t o   c o n s t a n t s 
 
                         f o r   j   i n   r a n g e ( b a t c h n k e _ c o n s t a n t s . N B _ H U F F _ E L E M E N T ) : 
 
                                 i f   ( 
 
                                         b a t c h n k e _ c o n s t a n t s . h u f f [ h u f f _ c o d i n g ] [ j ] [ " s z " ]   = =   i 
 
                                         a n d   l h u f f   = =   b a t c h n k e _ c o n s t a n t s . h u f f [ h u f f _ c o d i n g ] [ j ] [ " l b l " ] 
 
                                 ) : 
 
                                         s e l f . i n d e x   + =   i 
 
                                         r e t u r n   ( i ,   j ) 
 
                 r a i s e   S z E r r o r 
 
 
 
         d e f   _ b i t s _ b u f 2 H u f f P a t t e r n ( s e l f ,   n b _ b i t s ) : 
 
                 s r c _ b i t _ s t a r t   =   s e l f . i n d e x 
 
                 s z   =   n b _ b i t s   -   1 
 
                 i f   l e n ( s e l f . a r r a y )   *   8   <   s r c _ b i t _ s t a r t   +   n b _ b i t s : 
 
                         r a i s e   E x c e p t i o n ( f " V e r i f y   t h a t   d e s t   b u f   i s   l a r g e   e n o u g h   (   { l e n ( s e l f . a r r a y ) } ,   { s r c _ b i t _ s t a r t } ,   { n b _ b i t s } ) " ) 
 
                 b i t t o r e a d   =   0 
 
                 p a t t e r n   =   0 
 
                 w h i l e   n b _ b i t s   >   0 : 
 
                         i f   s e l f . a r r a y [ s r c _ b i t _ s t a r t   > >   3 ]   &   ( 1   < <   ( s r c _ b i t _ s t a r t   &   0 x 0 7 ) ) : 
 
                                 p a t t e r n   | =   1   < <   ( s z   -   b i t t o r e a d ) 
 
                         n b _ b i t s   - =   1 
 
                         b i t t o r e a d   + =   1 
 
                         s r c _ b i t _ s t a r t   + =   1 
 
                 r e t u r n   p a t t e r n 
 
 
 
 c l a s s   F l a g : 
 
         d e f   _ _ i n i t _ _ ( s e l f ,   f l a g _ a s _ i n t ) : 
 
                 b i n _ s t r   =   f " { f l a g _ a s _ i n t : 0 8 b } " 
 
                 s e l f . c t s   =   i n t ( b i n _ s t r [ - 2 ] ,   2 ) 
 
                 s e l f . n o _ s a m p l e   =   i n t ( b i n _ s t r [ - 3 ] ,   2 ) 
 
                 s e l f . b a t c h _ r e q   =   i n t ( b i n _ s t r [ - 4 ] ,   2 ) 
 
                 s e l f . n b _ o f _ t y p e _ m e a s u r e   =   i n t ( b i n _ s t r [ : 4 ] ,   2 ) 
 
 
 
 c l a s s   S e r i e : 
 
         d e f   _ _ i n i t _ _ ( s e l f ) : 
 
                 s e l f . c o d i n g _ t y p e   =   0 
 
                 s e l f . c o d i n g _ t a b l e   =   0 
 
                 s e l f . c o m p r e s s _ s a m p l e _ n b   =   0 
 
                 s e l f . r e s o l u t i o n   =   N o n e 
 
                 s e l f . u n c o m p r e s s _ s a m p l e s   =   [ ] 
 
 
 
 c l a s s   M e a s u r e : 
 
         d e f   _ _ i n i t _ _ ( s e l f ,   t i m e s t a m p ) : 
 
                 s e l f . d a t a _ r e l a t i v e _ t i m e s t a m p   =   t i m e s t a m p 
 
                 s e l f . d a t a   =   M e a s u r e d D a t a ( ) 
 
 
 
 c l a s s   M e a s u r e d D a t a : 
 
         d e f   _ _ i n i t _ _ ( s e l f ) : 
 
                 s e l f . v a l u e   =   N o n e 
 
                 s e l f . l a b e l   =   N o n e 
 
 
 
 c l a s s   U n c o m p r e s s e d D a t a : 
 
         d e f   _ _ i n i t _ _ ( s e l f ) : 
 
                 s e l f . b a t c h _ c o u n t e r   =   0 
 
                 s e l f . b a t c h _ r e l a t i v e _ t i m e s t a m p   =   0 
 
                 s e l f . s e r i e s   =   [ S e r i e ( )   f o r   i   i n   r a n g e ( b a t c h n k e _ c o n s t a n t s . N U M B E R _ O F _ S E R I E S ) ] 
 
 
 
 c l a s s   b a t c h n k e : 
 
         @ s t a t i c m e t h o d 
 
         d e f   u n c o m p r e s s ( t a g s z ,   a r g _ l i s t ,   h e x _ s t r i n g ,   b a t c h _ a b s o l u t e _ t i m e s t a m p = N o n e ) : 
 
                 o u t   =   U n c o m p r e s s e d D a t a ( ) 
 
                 a r r a y   =   b a t c h n k e . h e x _ t o _ a r r a y ( h e x _ s t r i n g ) 
 
                 d a t a _ b u f f e r   =   B u f f e r ( a r r a y ) 
 
                 f l a g   =   F l a g ( d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 8 ,   8 ) ) 
 
                 c o u n t e r   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 8 ,   3 ) 
 
                 o u t . b a t c h _ c o u n t e r   =   c o u n t e r 
 
                 l t e m p 2   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 8 ,   1 )   #   d u m m y   r e a d ? 
 
                 a b s _ t i m e s t a m p   =   l a s t _ t i m e s t a m p   =   0 
 
                 i n d e x _ o f _ t h e _ f i r s t _ s a m p l e   =   0 
 
                 
 
                 f o r   i   i n   r a n g e ( f l a g . n b _ o f _ t y p e _ m e a s u r e ) : 
 
                         t a g   =   T a g ( s i z e = t a g s z ,   l b l = d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 8 ,   t a g s z ) ) 
 
                         i i   =   b a t c h n k e . f i n d _ i n d e x _ o f _ l b l ( a r g _ l i s t ,   t a g . l b l ) 
 
                         i f   i   = =   0 : 
 
                                 i n d e x _ o f _ t h e _ f i r s t _ s a m p l e   =   i i 
 
                                 t i m e s t a m p   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 8 ,   b a t c h n k e . b m _ s t _ s z ( b a t c h n k e _ c o n s t a n t s . S T _ U 3 2 ) ) 
 
                                 a b s _ t i m e s t a m p   =   t i m e s t a m p 
 
                                 o u t . s e r i e s [ i i ] . u n c o m p r e s s _ s a m p l e s . a p p e n d ( M e a s u r e ( t i m e s t a m p ) ) 
 
                         e l s e : 
 
                                 s z ,   b i   =   d a t a _ b u f f e r . n e x t _ b i _ f r o m _ h i ( 1 ) 
 
                                 i f   n o t   s z :   r a i s e   E x c e p t i o n ( " W r o n g   s z   f r o m   s z b i " ) 
 
                                 t   =   0 
 
                                 i f   b i   < =   b a t c h n k e _ c o n s t a n t s . B R _ H U F F _ M A X _ I N D E X _ T A B L E : 
 
                                         i f   b i   >   0 : 
 
                                                 t   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 3 2 ,   b i ) 
 
                                                 t   + =   a b s _ t i m e s t a m p   +   2   * *   b i   -   1 
 
                                         e l s e :   t   =   a b s _ t i m e s t a m p 
 
                                 e l s e : 
 
                                         t   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 3 2 ,   b a t c h n k e . b m _ s t _ s z ( b a t c h n k e _ c o n s t a n t s . S T _ U 3 2 ) ) 
 
                                 o u t . s e r i e s [ i i ] . u n c o m p r e s s _ s a m p l e s . a p p e n d ( M e a s u r e ( t ) ) 
 
                                 a b s _ t i m e s t a m p   =   t 
 
                         l a s t _ t i m e s t a m p   =   a b s _ t i m e s t a m p 
 
                         v   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( a r g _ l i s t [ i i ] [ " s a m p l e t y p e " ] ,   b a t c h n k e . b m _ s t _ s z ( a r g _ l i s t [ i i ] [ " s a m p l e t y p e " ] ) ) 
 
                         i f   a r g _ l i s t [ i i ] [ " s a m p l e t y p e " ]   = =   b a t c h n k e _ c o n s t a n t s . S T _ F L : 
 
                                 o u t . s e r i e s [ i i ] . u n c o m p r e s s _ s a m p l e s [ 0 ] . d a t a . v a l u e   =   b a t c h n k e . t o _ f l o a t ( v ) 
 
                         e l s e : 
 
                                 o u t . s e r i e s [ i i ] . u n c o m p r e s s _ s a m p l e s [ 0 ] . d a t a . v a l u e   =   v 
 
                         o u t . s e r i e s [ i i ] . u n c o m p r e s s _ s a m p l e s [ 0 ] . d a t a . l a b e l   =   t a g . l b l 
 
                         i f   n o t   f l a g . n o _ s a m p l e : 
 
                                 o u t . s e r i e s [ i i ] . c o d i n g _ t y p e   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 8 ,   2 ) 
 
                                 o u t . s e r i e s [ i i ] . c o d i n g _ t a b l e   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 8 ,   2 ) 
 
                 
 
                 i f   n o t   f l a g . n o _ s a m p l e : 
 
                         i f   f l a g . c t s : 
 
                                 n b _ s a m p l e _ t o _ p a r s e   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 8 ,   8 ) 
 
                                 l t i m e s t a m p _ c o d i n g   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 8 ,   2 ) 
 
                                 t i m e s t a m p _ c o m m o n   =   [ ] 
 
                                 f o r   i   i n   r a n g e ( n b _ s a m p l e _ t o _ p a r s e ) : 
 
                                         s z ,   b i   =   d a t a _ b u f f e r . n e x t _ b i _ f r o m _ h i ( l t i m e s t a m p _ c o d i n g ) 
 
                                         i f   n o t   s z :   r a i s e   E x c e p t i o n ( " s z " ) 
 
                                         i f   b i   < =   b a t c h n k e _ c o n s t a n t s . B R _ H U F F _ M A X _ I N D E X _ T A B L E : 
 
                                                 i f   i   = =   0 : 
 
                                                       t i m e s t a m p _ c o m m o n . a p p e n d ( o u t . s e r i e s [ i n d e x _ o f _ t h e _ f i r s t _ s a m p l e ] . u n c o m p r e s s _ s a m p l e s [ 0 ] . d a t a _ r e l a t i v e _ t i m e s t a m p ) 
 
                                                 e l s e : 
 
                                                         i f   b i   >   0 : 
 
                                                                 r a w   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 3 2 ,   b i ) 
 
                                                                 t i m e s t a m p _ c o m m o n . a p p e n d ( r a w   +   t i m e s t a m p _ c o m m o n [ i   -   1 ]   +   2   * *   b i   -   1 ) 
 
                                                         e l s e :   t i m e s t a m p _ c o m m o n . a p p e n d ( t i m e s t a m p _ c o m m o n [ i   -   1 ] ) 
 
                                         e l s e : 
 
                                                 t i m e s t a m p _ c o m m o n . a p p e n d ( d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 3 2 ,   b a t c h n k e . b m _ s t _ s z ( b a t c h n k e _ c o n s t a n t s . S T _ U 3 2 ) ) ) 
 
                                         l a s t _ t i m e s t a m p   =   t i m e s t a m p _ c o m m o n [ i ] 
 
 
 
                                 f o r   j   i n   r a n g e ( f l a g . n b _ o f _ t y p e _ m e a s u r e ) : 
 
                                         f i r s t _ n u l l _ d e l t a _ v a l u e   =   1 
 
                                         t a g   =   T a g ( s i z e = t a g s z ,   l b l = d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 8 ,   t a g s z ) ) 
 
                                         i i   =   b a t c h n k e . f i n d _ i n d e x _ o f _ l b l ( a r g _ l i s t ,   t a g . l b l ) 
 
                                         f o r   i   i n   r a n g e ( 0 ,   n b _ s a m p l e _ t o _ p a r s e ) : 
 
                                                 a v a i l a b l e   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 8 ,   1 ) 
 
                                                 i f   a v a i l a b l e : 
 
                                                         s z ,   b i   =   d a t a _ b u f f e r . n e x t _ b i _ f r o m _ h i ( o u t . s e r i e s [ i i ] . c o d i n g _ t a b l e ) 
 
                                                         i f   n o t   s z :   r a i s e   E x c e p t i o n ( " W r o n g   s z " ) 
 
                                                         c u r r e n t _ m e a s u r e   =   M e a s u r e ( 0 ) 
 
                                                         i f   b i   < =   b a t c h n k e _ c o n s t a n t s . B R _ H U F F _ M A X _ I N D E X _ T A B L E : 
 
                                                                 i f   b i   >   0 : 
 
                                                                         c u r r e n t _ m e a s u r e . d a t a . v a l u e   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 1 6 ,   b i ) 
 
                                                                         i f   o u t . s e r i e s [ i i ] . c o d i n g _ t y p e   = =   0 : 
 
                                                                                 i f   c u r r e n t _ m e a s u r e . d a t a . v a l u e   > =   2   * *   ( b i   -   1 ) : 
 
                                                                                         c u r r e n t _ m e a s u r e . d a t a . v a l u e   * =   a r g _ l i s t [ i i ] [ " r e s o l " ] 
 
                                                                                         c u r r e n t _ m e a s u r e . d a t a . v a l u e   + =   o u t . s e r i e s [ i i ] . u n c o m p r e s s _ s a m p l e s [ - 1 ] . d a t a . v a l u e 
 
                                                                                 e l s e : 
 
                                                                                         c u r r e n t _ m e a s u r e . d a t a . v a l u e   + =   1   -   2   * *   b i 
 
                                                                                         c u r r e n t _ m e a s u r e . d a t a . v a l u e   * =   a r g _ l i s t [ i i ] [ " r e s o l " ] 
 
                                                                                         c u r r e n t _ m e a s u r e . d a t a . v a l u e   + =   o u t . s e r i e s [ i i ] . u n c o m p r e s s _ s a m p l e s [ - 1 ] . d a t a . v a l u e 
 
                                                                         e l i f   o u t . s e r i e s [ i i ] . c o d i n g _ t y p e   = =   1 : 
 
                                                                                 c u r r e n t _ m e a s u r e . d a t a . v a l u e   + =   2   * *   b i   -   1 
 
                                                                                 c u r r e n t _ m e a s u r e . d a t a . v a l u e   * =   a r g _ l i s t [ i i ] [ " r e s o l " ] 
 
                                                                                 c u r r e n t _ m e a s u r e . d a t a . v a l u e   + =   o u t . s e r i e s [ i i ] . u n c o m p r e s s _ s a m p l e s [ - 1 ] . d a t a . v a l u e 
 
                                                                         e l s e : 
 
                                                                                 c u r r e n t _ m e a s u r e . d a t a . v a l u e   + =   2   * *   b i   -   1 
 
                                                                                 c u r r e n t _ m e a s u r e . d a t a . v a l u e   * =   a r g _ l i s t [ i i ] [ " r e s o l " ] 
 
                                                                                 c u r r e n t _ m e a s u r e . d a t a . v a l u e   =   o u t . s e r i e s [ i i ] . u n c o m p r e s s _ s a m p l e s [ - 1 ] . d a t a . v a l u e   -   c u r r e n t _ m e a s u r e . d a t a . v a l u e 
 
                                                                 e l s e : 
 
                                                                         i f   f i r s t _ n u l l _ d e l t a _ v a l u e : 
 
                                                                                 f i r s t _ n u l l _ d e l t a _ v a l u e   =   0 
 
                                                                                 c o n t i n u e 
 
                                                                         e l s e : 
 
                                                                                 c u r r e n t _ m e a s u r e . d a t a . v a l u e   =   o u t . s e r i e s [ i i ] . u n c o m p r e s s _ s a m p l e s [ - 1 ] . d a t a . v a l u e 
 
                                                         e l s e : 
 
                                                                 c u r r e n t _ m e a s u r e . d a t a . v a l u e   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( a r g _ l i s t [ i i ] [ " s a m p l e t y p e " ] ,   b a t c h n k e . b m _ s t _ s z ( a r g _ l i s t [ i i ] [ " s a m p l e t y p e " ] ) ) 
 
                                                         c u r r e n t _ m e a s u r e . d a t a _ r e l a t i v e _ t i m e s t a m p   =   t i m e s t a m p _ c o m m o n [ i ] 
 
                                                         o u t . s e r i e s [ i i ] . u n c o m p r e s s _ s a m p l e s . a p p e n d ( c u r r e n t _ m e a s u r e ) 
 
                         e l s e : 
 
                                 f o r   i   i n   r a n g e ( f l a g . n b _ o f _ t y p e _ m e a s u r e ) : 
 
                                         t a g   =   T a g ( s i z e = t a g s z ,   l b l = d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 8 ,   t a g s z ) ) 
 
                                         i i   =   b a t c h n k e . f i n d _ i n d e x _ o f _ l b l ( a r g _ l i s t ,   t a g . l b l ) 
 
                                         c o m p r e s s _ s a m p l e s _ n b   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 8 ,   8 ) 
 
                                         i f   c o m p r e s s _ s a m p l e s _ n b : 
 
                                                 l t i m e s t a m p _ c o d i n g   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 8 ,   2 ) 
 
                                                 f o r   j   i n   r a n g e ( c o m p r e s s _ s a m p l e s _ n b ) : 
 
                                                         c u r r e n t _ m e a s u r e   =   M e a s u r e ( 0 ) 
 
                                                         s z ,   b i   =   d a t a _ b u f f e r . n e x t _ b i _ f r o m _ h i ( l t i m e s t a m p _ c o d i n g ) 
 
                                                         i f   b i   < =   b a t c h n k e _ c o n s t a n t s . B R _ H U F F _ M A X _ I N D E X _ T A B L E : 
 
                                                                 i f   b i   >   0 : 
 
                                                                         t   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 3 2 ,   b i ) 
 
                                                                         c u r r e n t _ m e a s u r e . d a t a _ r e l a t i v e _ t i m e s t a m p   =   t   +   o u t . s e r i e s [ i i ] . u n c o m p r e s s _ s a m p l e s [ - 1 ] . d a t a _ r e l a t i v e _ t i m e s t a m p   +   2   * *   b i   -   1 
 
                                                                 e l s e : 
 
                                                                         c u r r e n t _ m e a s u r e . d a t a _ r e l a t i v e _ t i m e s t a m p   =   o u t . s e r i e s [ i i ] . u n c o m p r e s s _ s a m p l e s [ - 1 ] . d a t a _ r e l a t i v e _ t i m e s t a m p 
 
                                                         e l s e : 
 
                                                                 c u r r e n t _ m e a s u r e . d a t a _ r e l a t i v e _ t i m e s t a m p   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 3 2 ,   b a t c h n k e . b m _ s t _ s z ( b a t c h n k e _ c o n s t a n t s . S T _ U 3 2 ) ) 
 
                                                         i f   c u r r e n t _ m e a s u r e . d a t a _ r e l a t i v e _ t i m e s t a m p   >   l a s t _ t i m e s t a m p : 
 
                                                                 l a s t _ t i m e s t a m p   =   c u r r e n t _ m e a s u r e . d a t a _ r e l a t i v e _ t i m e s t a m p 
 
                                                         s z ,   b i   =   d a t a _ b u f f e r . n e x t _ b i _ f r o m _ h i ( o u t . s e r i e s [ i i ] . c o d i n g _ t a b l e ) 
 
                                                         i f   n o t   s z :   r a i s e   E x c e p t i o n ( " s z " ) 
 
                                                         i f   b i   < =   b a t c h n k e _ c o n s t a n t s . B R _ H U F F _ M A X _ I N D E X _ T A B L E : 
 
                                                                 i f   b i   >   0 : 
 
                                                                         c u r r e n t _ m e a s u r e . d a t a . v a l u e   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 1 6 ,   b i ) 
 
                                                                         i f   o u t . s e r i e s [ i i ] . c o d i n g _ t y p e   = =   0 : 
 
                                                                                 i f   c u r r e n t _ m e a s u r e . d a t a . v a l u e   > =   2   * *   ( b i   -   1 ) : 
 
                                                                                         c u r r e n t _ m e a s u r e . d a t a . v a l u e   * =   a r g _ l i s t [ i i ] [ " r e s o l " ] 
 
                                                                                         c u r r e n t _ m e a s u r e . d a t a . v a l u e   + =   o u t . s e r i e s [ i i ] . u n c o m p r e s s _ s a m p l e s [ - 1 ] . d a t a . v a l u e 
 
                                                                                 e l s e : 
 
                                                                                         c u r r e n t _ m e a s u r e . d a t a . v a l u e   + =   1   -   2   * *   b i 
 
                                                                                         c u r r e n t _ m e a s u r e . d a t a . v a l u e   * =   a r g _ l i s t [ i i ] [ " r e s o l " ] 
 
                                                                                         c u r r e n t _ m e a s u r e . d a t a . v a l u e   + =   o u t . s e r i e s [ i i ] . u n c o m p r e s s _ s a m p l e s [ - 1 ] . d a t a . v a l u e 
 
                                                                         e l i f   o u t . s e r i e s [ i i ] . c o d i n g _ t y p e   = =   1 : 
 
                                                                                 c u r r e n t _ m e a s u r e . d a t a . v a l u e   + =   2   * *   b i   -   1 
 
                                                                                 c u r r e n t _ m e a s u r e . d a t a . v a l u e   * =   a r g _ l i s t [ i i ] [ " r e s o l " ] 
 
                                                                                 c u r r e n t _ m e a s u r e . d a t a . v a l u e   + =   o u t . s e r i e s [ i i ] . u n c o m p r e s s _ s a m p l e s [ - 1 ] . d a t a . v a l u e 
 
                                                                         e l s e : 
 
                                                                                 c u r r e n t _ m e a s u r e . d a t a . v a l u e   + =   2   * *   b i   -   1 
 
                                                                                 c u r r e n t _ m e a s u r e . d a t a . v a l u e   * =   a r g _ l i s t [ i i ] [ " r e s o l " ] 
 
                                                                                 c u r r e n t _ m e a s u r e . d a t a . v a l u e   =   o u t . s e r i e s [ i i ] . u n c o m p r e s s _ s a m p l e s [ - 1 ] . d a t a . v a l u e   -   c u r r e n t _ m e a s u r e . d a t a . v a l u e 
 
                                                                 e l s e : 
 
                                                                         c u r r e n t _ m e a s u r e . d a t a . v a l u e   =   o u t . s e r i e s [ i i ] . u n c o m p r e s s _ s a m p l e s [ - 1 ] . d a t a . v a l u e 
 
                                                         e l s e : 
 
                                                                 c u r r e n t _ m e a s u r e . d a t a . v a l u e   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( a r g _ l i s t [ i i ] [ " s a m p l e t y p e " ] ,   b a t c h n k e . b m _ s t _ s z ( a r g _ l i s t [ i i ] [ " s a m p l e t y p e " ] ) ) 
 
                                                         o u t . s e r i e s [ i i ] . u n c o m p r e s s _ s a m p l e s . a p p e n d ( c u r r e n t _ m e a s u r e ) 
 
                 
 
                 g l o b a l _ t i m e s t a m p   =   0 
 
                 i f   n o t   l a s t _ t i m e s t a m p : 
 
                         g l o b a l _ t i m e s t a m p   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 3 2 ,   b a t c h n k e . b m _ s t _ s z ( b a t c h n k e _ c o n s t a n t s . S T _ U 3 2 ) ) 
 
                 e l s e : 
 
                         s z ,   b i   =   d a t a _ b u f f e r . n e x t _ b i _ f r o m _ h i ( 1 ) 
 
                         i f   n o t   s z :   r a i s e   E x c e p t i o n ( " s z " ) 
 
                         i f   b i   < =   b a t c h n k e _ c o n s t a n t s . B R _ H U F F _ M A X _ I N D E X _ T A B L E : 
 
                                 i f   b i   >   0 : 
 
                                         g l o b a l _ t i m e s t a m p   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 3 2 ,   b i ) 
 
                                         g l o b a l _ t i m e s t a m p   + =   l a s t _ t i m e s t a m p   +   2   * *   b i   -   1 
 
                                 e l s e :   g l o b a l _ t i m e s t a m p   =   l a s t _ t i m e s t a m p 
 
                         e l s e : 
 
                                   g l o b a l _ t i m e s t a m p   =   d a t a _ b u f f e r . n e x t _ s a m p l e ( b a t c h n k e _ c o n s t a n t s . S T _ U 3 2 ,   b a t c h n k e . b m _ s t _ s z ( b a t c h n k e _ c o n s t a n t s . S T _ U 3 2 ) ) 
 
                 o u t . b a t c h _ r e l a t i v e _ t i m e s t a m p   =   g l o b a l _ t i m e s t a m p 
 
                 r e t u r n   b a t c h n k e . f o r m a t _ e x p e c t e d _ u n c o m p r e s s _ r e s u l t ( o u t ,   a r g _ l i s t ,   b a t c h _ a b s o l u t e _ t i m e s t a m p ) 
 
 
 
         @ s t a t i c m e t h o d 
 
         d e f   f o r m a t _ e x p e c t e d _ u n c o m p r e s s _ r e s u l t ( o u t ,   a r g _ l i s t ,   b a t c h _ a b s o l u t e _ t i m e s t a m p ) : 
 
                 o u t p u t   =   { " b a t c h _ c o u n t e r " :   o u t . b a t c h _ c o u n t e r ,   " b a t c h _ r e l a t i v e _ t i m e s t a m p " :   o u t . b a t c h _ r e l a t i v e _ t i m e s t a m p } 
 
                 i f   b a t c h _ a b s o l u t e _ t i m e s t a m p :   o u t p u t [ " b a t c h _ a b s o l u t e _ t i m e s t a m p " ]   =   b a t c h _ a b s o l u t e _ t i m e s t a m p 
 
                 d a t a s e t   =   [ ] 
 
                 f o r   i n d e x ,   s e r i e   i n   e n u m e r a t e ( o u t . s e r i e s ) : 
 
                         f o r   s a m p l e   i n   s e r i e . u n c o m p r e s s _ s a m p l e s : 
 
                                 m e a s u r e   =   { 
 
                                         " d a t a _ r e l a t i v e _ t i m e s t a m p " :   s a m p l e . d a t a _ r e l a t i v e _ t i m e s t a m p , 
 
                                         " d a t a " :   { " v a l u e " :   s a m p l e . d a t a . v a l u e ,   " l a b e l " :   a r g _ l i s t [ i n d e x ] [ " t a g l b l " ] } , 
 
                                 } 
 
                                 i f   " l b l n a m e "   i n   a r g _ l i s t [ i n d e x ] :   m e a s u r e [ " d a t a " ] [ " l a b e l _ n a m e " ]   =   a r g _ l i s t [ i n d e x ] [ " l b l n a m e " ] 
 
                                 d a t a s e t . a p p e n d ( m e a s u r e ) 
 
                                 i f   b a t c h _ a b s o l u t e _ t i m e s t a m p : 
 
                                         m e a s u r e [ " d a t a _ a b s o l u t e _ t i m e s t a m p " ]   =   b a t c h n k e . c o m p u t e _ d a t a _ a b s o l u t e _ t i m e s t a m p ( 
 
                                                 b a t c h _ a b s o l u t e _ t i m e s t a m p ,   o u t . b a t c h _ r e l a t i v e _ t i m e s t a m p ,   s a m p l e . d a t a _ r e l a t i v e _ t i m e s t a m p 
 
                                         ) 
 
                 o u t p u t [ " d a t a s e t " ]   =   d a t a s e t 
 
                 r e t u r n   o u t p u t 
 
 
 
         @ s t a t i c m e t h o d 
 
         d e f   c o m p u t e _ d a t a _ a b s o l u t e _ t i m e s t a m p ( b a t ,   b r t ,   d r t ) : 
 
                 d ,   t   =   b a t . r s t r i p ( " Z " ) . s p l i t ( " T " ) 
 
                 Y ,   M ,   D   =   [ i n t ( x )   f o r   x   i n   d . s p l i t ( " - " ) ] 
 
                 h ,   m ,   s   =   t . s p l i t ( " : " ) 
 
                 s s ,   m s   =   s . s p l i t ( " . " ) 
 
                 f r o m _ t s   =   d a t e t i m e ( Y ,   M ,   D ,   i n t ( h ) ,   i n t ( m ) ,   i n t ( s s ) ,   i n t ( m s )   *   1 0 0 0 ) 
 
                 r e t u r n   ( d a t e t i m e . f r o m t i m e s t a m p ( f r o m _ t s . t i m e s t a m p ( )   -   ( b r t   -   d r t ) ) . i s o f o r m a t ( t i m e s p e c = " m i l l i s e c o n d s " )   +   " Z " ) 
 
 
 
         @ s t a t i c m e t h o d 
 
         d e f   i s _ h e x ( c ) : 
 
                 t r y : 
 
                         _   =   i n t ( c ,   1 6 ) 
 
                         r e t u r n   T r u e 
 
                 e x c e p t   V a l u e E r r o r :   r e t u r n   F a l s e 
 
 
 
         @ s t a t i c m e t h o d 
 
         d e f   h e x _ t o _ a r r a y ( h e x _ s t r i n g ) : 
 
                 f i l t e r e d   =   [ c   f o r   c   i n   h e x _ s t r i n g   i f   b a t c h n k e . i s _ h e x ( c ) ] 
 
                 o u t   =   [ ] 
 
                 i   =   0 
 
                 w h i l e   i   <   l e n ( f i l t e r e d ) : 
 
                         o u t . a p p e n d ( i n t ( f i l t e r e d [ i ]   +   f i l t e r e d [ i   +   1 ] ,   1 6 ) ) 
 
                         i   + =   2 
 
                 r e t u r n   o u t 
 
 
 
         @ s t a t i c m e t h o d 
 
         d e f   f i n d _ i n d e x _ o f _ l b l ( a r g _ l i s t ,   l a b e l ) : 
 
                 f o r   i ,   v a l u e   i n   e n u m e r a t e ( a r g _ l i s t ) : 
 
                         i f   v a l u e [ " t a g l b l " ]   = =   l a b e l :   r e t u r n   i 
 
                 r a i s e   E x c e p t i o n ( " C a n n o t   f i n d   i n d e x   i n   a r g _ l i s t " ) 
 
 
 
         @ s t a t i c m e t h o d 
 
         d e f   b m _ s t _ s z ( s t ) : 
 
                 i f   s t   >   b a t c h n k e _ c o n s t a n t s . S T _ I 2 4 :   r e t u r n   3 2 
 
                 i f   s t   >   b a t c h n k e _ c o n s t a n t s . S T _ I 1 6 :   r e t u r n   2 4 
 
                 i f   s t   >   b a t c h n k e _ c o n s t a n t s . S T _ I 8 :   r e t u r n   1 6 
 
                 i f   s t   >   b a t c h n k e _ c o n s t a n t s . S T _ I 4 :   r e t u r n   8 
 
                 i f   s t   >   b a t c h n k e _ c o n s t a n t s . S T _ B L :   r e t u r n   4 
 
                 i f   s t   >   b a t c h n k e _ c o n s t a n t s . S T _ U N D E F :   r e t u r n   1 
 
                 r e t u r n   0 
 
 
 
         @ s t a t i c m e t h o d 
 
         d e f   t o _ f l o a t ( n u m b e r ) : 
 
                 r e t u r n   s t r u c t . u n p a c k ( " > f " ,   n u m b e r . t o _ b y t e s ( 4 ,   " b i g " ) ) [ 0 ] 
 
 