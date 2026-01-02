import serial
from time import sleep
import datetime
import time
# import numpy as np

#- Le temps evolue normalement (heure reelle): theNow
#- LTARF varie entre HPH, HCH, HCE, HPE toutes les LTARF_DT 
#- RELAIS varie en chenillard ou ON/OFF toutes les RELAIS_DT 
#- On fixe des valeurs pour chaque periode tarifaire de :
#  . PAMoy:  Puissance active moyenne consommee 
#  . PRpMoy: Puissance reactive positive moyenne consommee
#  . PRnMoy: Puissance reactive negative moyenne consommee
#- A chaque iteration de flux on incremente les EAST, ERQ1 et ERQ4 
#  en fonction du temps passe est des valeurs de puissance active moyennes fixees ci-avant:
#  Exy_s += PxyMoy * (elapsed_time/3600)  


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

BeginDate = datetime.datetime.now()

# DATE = BeginDate
DATE = datetime.datetime(2000, 1, 1, 0, 0, 0)
DATE_lastDate = BeginDate

LTARF_DT       = 600 
LTARF_lastDate = BeginDate 
LTARF_idx      = 0
LTARF_array = [   "HPE",   "HCE",   "HPH",   "HCH",    "PM"]

# BEWARE on Linky EAST,EAIT,ERQx are unique summations independently of period (unlike PMEPMI or ICE or ...)
# Hence they are not dependent on period
EAST          = 10000.0 # Wh
ERQ1          =   100.0 # VArh
ERQ4          =   100.0 # VArh

#PAMoy_s       = [ 108000.0, 108000.0, 108000.0, 108000.0, 108000.0] # W
#PRpMoy_s      = [ 360000.0, 360000.0, 360000.0, 360000.0, 360000.0] # VAr
#PRnMoy_s      = [ 1, 1, 1, 1, 1] # VAr

PAMoy_s       = [ 36000.0, 36000.0, 36000.0, 36000.0, 36000.0] # W
PRpMoy_s      = [ 18000.0, 18000.0, 18000.0, 18000.0, 18000.0] # VAr
PRnMoy_s      = [ 1, 1, 1, 1, 1] # VAr

RELAIS_DT = 3
RELAIS_lastDate = BeginDate
RELAIS_state = 0
RELAIS_stateByte = 0x00

theNow     = datetime.datetime.now()

while True:
			
	theNowPrec = theNow
	theNow     = datetime.datetime.now()

	array = open(filename,'r').read().split('\n')
	#ser.write(b'\x02')
	#print ("<")
	
	for line in array:
		
		if(line == '>'):
			print (">")
			ser.write(b'\x03') 
			#sleep(0.0)
			
			# Delay must be set after end of frame !
			time.sleep (16.0 / 1000.0) # Spec: Should wait between 16 to 33 ms between "trames"
			
		elif(line == '<'):
			print ("<")
			ser.write(b'\x02')
			
		else:
			firstWord=line.split()[0]
			
			if (firstWord == 'DATE'):
				
				# To do calculations only once do it on Rx of any label. Here DATE.
				
				elapsed_time = theNow - theNowPrec
				elapsed_time = (elapsed_time.seconds * 1000.0) + (elapsed_time.microseconds / 1000.0) # In Milliseconds
				elapsed_time = elapsed_time / (3600.0 * 1000.0) # In Hours
				
				print ("elapsed_time (s): %f" % (elapsed_time ) )
				
				if (((theNow - LTARF_lastDate).seconds) >= LTARF_DT ):
					LTARF_idx = (LTARF_idx + 1) % len(LTARF_array)
					LTARF_lastDate = theNow 
					elapsed_time  = 0
						
				EAST  += (PAMoy_s [LTARF_idx] * elapsed_time)
				ERQ1  += (PRpMoy_s[LTARF_idx] * elapsed_time)
				ERQ4  += (PRnMoy_s[LTARF_idx] * elapsed_time)
				
				if (((theNow - RELAIS_lastDate).seconds) >= RELAIS_DT ):
									
					RELAIS_lastDate = theNow 
					
					# ON/OFF All:
					#------------
					#if (RELAIS_stateByte > 0) :
					#	RELAIS_stateByte = 0
					#else :
					#	RELAIS_stateByte = 7;
						
					# CHENILLARD: 
					# -----------
					RELAIS_state = (RELAIS_state + 1) % 4
					if (RELAIS_state == 0):
						RELAIS_stateByte = 0x00
					else:
						RELAIS_stateByte = 0x01 << (RELAIS_state - 1)
					
				line = "DATE\t%c%s\t" % ('E', theNow.strftime("%d%m%y%H%M%S"))
				line = line + "%c" % edf_checksum(line)
						
			elif (firstWord == 'LTARF'):
				line = "LTARF\t%s\t" % (LTARF_array[LTARF_idx]) 
				line = line + "%c" % edf_checksum(line)
				
			elif (firstWord == 'EAST'):
				line = "EAST\t%s\t" % ("%d" % (EAST)) 
				line = line + "%c" % edf_checksum(line)
				
			elif (firstWord == 'ERQ1'):
				line = "ERQ1\t%s\t" % ("%d" % (ERQ1)) 
				line = line + "%c" % edf_checksum(line)
				
			elif (firstWord == 'ERQ4'):
				line = "ERQ4\t%s\t" % ("%d" % (ERQ4)) 
				line = line + "%c" % edf_checksum(line)
				
			elif (firstWord == 'RELAIS'):
				line = "RELAIS\t%s\t" % ("%d" % (RELAIS_stateByte)) 
				line = line + "%c" % edf_checksum(line)
				
				
			ser.write(b'\x0A')	
			print ("%s" % line)
			ser.write(line.encode())
			ser.write(b'\x0D')
		
ser.close()