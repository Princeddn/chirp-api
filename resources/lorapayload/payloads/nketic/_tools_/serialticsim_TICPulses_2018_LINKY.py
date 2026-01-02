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
	chks += 0x20 # Linky
	# chks += 0x0A # Autres
	return chks

port = "com2"
#should be Ok at : 
#  1200, 2400, 4800,9600 and 19200 for RS232 input
#  1200, 9600 for 50KHz input
speed =19200

filename = "LOGS-TIC\UneTrameSTDwCHKS.txt"

ser = serial.Serial(port, speed, bytesize=serial.SEVENBITS, timeout=None, xonxoff=0, rtscts=0, parity=serial.PARITY_EVEN,dsrdtr=False)

print ('\n*** Starting ***\n')

#print(array)

# Manage DATEPA1 changes for specific tests
beginDate = datetime.datetime.now()

LTARF_DT = 3 
LTARF_lastDate = beginDate
LTARF_array = ["HPH", "HCH", "HCE", "HPE"]
LTARF_idx = 0

ENERGS_DT = 3
ENERGS_lastDate = beginDate
ENERGS_EAST = 0
ENERGS_EAST_INC = 300
ENERGS_EAIT = 0
ENERGS_EAIT_INC = 10
ENERGS_ERQ1 = 0
ENERGS_ERQ1_INC = 3000

RELAIS_DT = 3
RELAIS_lastDate = beginDate
RELAIS_state = 0
RELAIS_stateByte = 0x00

# DATE_10MNDT = 600 # 10mn 600 secondes ==> pas d'acceleration du temps"
# DATE_10MNDT = 10 # 10mn en 10 secondes 
DATE_10MNDT = 3 # 10mn en 3 secondes 
# DATE = beginDate
DATE = datetime.datetime(2000, 1, 1, 0, 0, 0)
DATE_lastDate = beginDate

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
			sleep(0.0)
			
		elif(line == '<'):
			print ("<")
			ser.write(b'\x02')
			
		else:
			firstWord=line.split()[0]
			
			if (firstWord == 'DATE'):
				
				# To do calculations only once do it on Rx of any label. Here DATE.
				
				if (((theNow - DATE_lastDate).seconds) >= DATE_10MNDT ):
					DATE += datetime.timedelta(seconds = 600)
					DATE_lastDate = theNow
					
				if (((theNow - LTARF_lastDate).seconds) >= LTARF_DT ):
					LTARF_idx = (LTARF_idx) % len(LTARF_array)
					LTARF_lastDate = theNow 
				
				if (((theNow - RELAIS_lastDate).seconds) >= RELAIS_DT ):
									
					RELAIS_lastDate = theNow 
					
					# ON/OFF All:
					#------------
					if (RELAIS_stateByte > 0) :
						RELAIS_stateByte = 0
					else :
						RELAIS_stateByte = 7;
						
					# CHENILLARD: 
					# -----------
					# RELAIS_state = (RELAIS_state + 1) % 4
					# if (RELAIS_state == 0):
						# RELAIS_stateByte = 0x00
					# else:
						# RELAIS_stateByte = 0x01 << (RELAIS_state - 1)
						
				if (((theNow - ENERGS_lastDate).seconds) >= ENERGS_DT ):
					ENERGS_EAST = (ENERGS_EAST + ENERGS_EAST_INC)
					ENERGS_EAIT = (ENERGS_EAIT + ENERGS_EAIT_INC)
					ENERGS_ERQ1=  (ENERGS_ERQ1 + ENERGS_ERQ1_INC)
					ENERGS_lastDate = theNow 
					
				line = "DATE\t%c%s\t" % ('E', DATE.strftime("%d%m%y%H%M%S"))
				line = line + "%c" % edf_checksum(line)
						
			elif (firstWord == 'LTARF'):
				line = "LTARF\t%s\t" % (LTARF_array[LTARF_idx]) 
				line = line + "%c" % edf_checksum(line)
				
			elif (firstWord == 'RELAIS'):
				line = "RELAIS\t%s\t" % ("%d" % (RELAIS_stateByte)) 
				line = line + "%c" % edf_checksum(line)
				
			elif (firstWord == 'EAST'):
				line = "EAST\t%s\t" % ("%d" % (ENERGS_EAST)) 
				line = line + "%c" % edf_checksum(line)
				
			elif (firstWord == 'EAIT'):
				line = "EAIT\t%s\t" % ("%d" % (ENERGS_EAIT)) 
				line = line + "%c" % edf_checksum(line)
				
			elif (firstWord == 'ERQ1'):
				line = "ERQ1\t%s\t" % ("%d" % (ENERGS_ERQ1)) 
				line = line + "%c" % edf_checksum(line)
				
			ser.write(b'\x0A')	
			print ("%s" % line)
			ser.write(line.encode())
			ser.write(b'\x0D')
				
				
ser.close()