import serial
from time import sleep
import datetime
# import numpy as np

#- DATE date courante
#- LTARF varie entre HPH, HCH, HCE, HPE toutes les LTARF_DT 
#- RELAIS varie Contacts virtuels 1,2,3 alternativement toutes les RELAIS_DT
#- ENEGIES varies: : +15 sur  EAST, +150 sur EAIT, +1500 sur ERQ1 (tous % 32768) tous les ENERGS_DT

def edf_checksum(line):
	chks = sum(map(ord, line))
	chks &= 0x3F
	# chks += 0x20 # Linky
	chks += 0x20
	return chks

port = "com2"
#should be Ok at : 
#  1200, 2400, 4800,9600 and 19200 for RS232 input
#  1200, 9600 for 50KHz input
speed =1200

filename = "LOGS-TIC\UneTrameCBETriHC.txt"

ser = serial.Serial(port, speed, bytesize=serial.SEVENBITS, timeout=None, xonxoff=0, rtscts=0, parity=serial.PARITY_EVEN,dsrdtr=False)

print ('\n*** Starting ***\n')

#print(array)

# Manage DATEPA1 changes for specific tests
beginDate = datetime.datetime.now()

PTEC_DT = 10
PTEC_lastDate = beginDate
PTEC_array = ["HCHC", "HCHP"]
PTEC_idx = 0

ENERGS_DT = 1
ENERGS_lastDate = beginDate
ENERGS_HCHC = 123456789
ENERGS_HCHC_INC = 10
ENERGS_HCHP = 999999999 
ENERGS_HCHP_INC = 0

theNow = datetime.datetime.now()

while True:

	theNowPrec = theNow
	theNow = datetime.datetime.now()
	
	array = open(filename,'r').read().split('\n')
	#ser.write(b'\x02')
	#print ("<")
	for line in array:
		
		if(line == '>'):
			print (">")
			ser.write(b'\x03') 
			sleep(0.05)
			
		elif(line == '<'):
			print ("<")
			ser.write(b'\x02')
			
		else:
			firstWord=line.split()[0]
			
			if (firstWord == 'ADCO'):
					
				if (((theNow - PTEC_lastDate).seconds) >= PTEC_DT ):
					PTEC_idx = (PTEC_idx + 1) % len(PTEC_array)
					PTEC_lastDate = theNow 
				
				if (((theNow - ENERGS_lastDate).seconds) >= ENERGS_DT ):
					ENERGS_HCHC = (ENERGS_HCHC + ENERGS_HCHC_INC)
					ENERGS_HCHP = (ENERGS_HCHP + ENERGS_HCHP_INC)
					ENERGS_lastDate = theNow 
						
			elif (firstWord == 'PTEC'):
				line = "PTEC %s" % (PTEC_array[PTEC_idx]) 
				line = line + " %c" % edf_checksum(line)
				
			elif (firstWord == 'HCHC'):
				line = "HCHC %s" % ("%d" % (ENERGS_HCHC)) 
				line = line + " %c" % edf_checksum(line)
				
			elif (firstWord == 'HCHP'):
				line = "HCHP %s" % ("%d" % (ENERGS_HCHP)) 
				line = line + " %c" % edf_checksum(line)
				
			ser.write(b'\x0A')	
			print ("%s" % line)
			ser.write(line.encode())
			ser.write(b'\x0D')
				
				
ser.close()