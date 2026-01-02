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
