import serial
from time import sleep
import datetime
# import numpy as np

#- DATEPA1 varie de 10min en 10min toutes les DATEPA1_DT :  DATE date courante , et +1 sur  PA1_s, EAP_s, EAP_i, ER+P_s, ER-P_s, 
#- PTCOUR1 varie entre HPH, HCH, HCE, HPE toutes les PTCOUR1_DT : et +1 sur  EaP-1_s, ER+P-1_s, PS et Set DebP to DATEPA1
#- PTCOUR2 varie entre HPH, HCH, HCE, HPE toutes les PTCOUR2_DT : et +1 sur  EaP-1_s2
#- PREAVIS DEP apparait toutes le PREAVIS_DT pendant PREAVIS_DU puis disparait
#- TARIFDYN varie de ACTIF a INACTIF toutes les TARIFDYN_DT
#  et TDYN1FD,TDYN1FF,TDYN2FD,TDYN2FF contiennent tous la date courante
#- Creation de periodes de depassement pendant HPH et HCE, pour tester le champ virtuel _DDMES1_

def edf_checksum(line):
	chks = sum(map(ord, line))
	chks &= 0x3F
	chks += 0x20
	return chks

port = "com2"
#should be Ok at : 
#  1200, 2400, 4800,9600 and 19200 for RS232 input
#  1200, 9600 for 50KHz input
speed =19200

filename = "trame_PMEPMI_EDF.txt"

ser = serial.Serial(port, speed, bytesize=serial.SEVENBITS, timeout=None, xonxoff=0, rtscts=0, parity=serial.PARITY_EVEN,dsrdtr=False)

print ('\n*** Starting ***\n')

BeginDate = datetime.datetime.now()

# DATE_10MN_DT = 600 # 10mn 600 secondes ==> pas d'acceleration du temps"
# DATE_10MN_DT = 10 # 10mn en 10 secondes 
DATE_10MN_DT = 30 # 10mn en 30 secondes 
# DATE = BeginDate
DATE = datetime.datetime(2000, 1, 1, 0, 0, 0)
DATE_lastDate = BeginDate

PTCOUR1_DT = 5 
PTCOUR1_lastDate = BeginDate
PTCOUR1_array = ["HPE", "HCE", "HPH", "HCH", "PM"]
PTCOUR1_idx = 0

ENERGS_DT = 5
ENERGS_lastDate = BeginDate
EAP_s = 0
EAP_s_INC = 2
EAP_i = 0
EAP_i_INC = 1
ERplusP_s = 0 
ERplusP_s_INC = 2
ERmoinsP_s = 0
ERmoinsP_s_INC = 2


theNow = datetime.datetime.now()

while True:

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
				
				if (((theNow - DATE_lastDate).seconds) >= DATE_10MN_DT ):
					DATE += datetime.timedelta(seconds = 600)
					DATE_lastDate = theNow
					
				if (((theNow - PTCOUR1_lastDate).seconds) >= PTCOUR1_DT ):
					PTCOUR1_idx = (PTCOUR1_idx + 1) % len(PTCOUR1_array)
					PTCOUR1_lastDate = theNow 
						
				if (((theNow - ENERGS_lastDate).seconds) >= ENERGS_DT ):
					EAP_s += EAP_s_INC
					EAP_i += EAP_i_INC
					ERplusP_s += ERplusP_s_INC
					ERmoinsP_s += ERmoinsP_s_INC
					ENERGS_lastDate = theNow 
					
				line = "DATE %s" % (DATE.strftime("%d/%m/%y %H:%M:%S"))
				line = line + " %c" % edf_checksum(line)
				
			elif (firstWord == 'EAP_s'):
				line = "EAP_s %dkWh" % (EAP_s)
				line = line + " %c" % edf_checksum(line)
				
			elif (firstWord == 'EAP_i'):
				line = "EAP_i %dkWh" % (EAP_i)
				line = line + " %c" % edf_checksum(line)
				
			elif (firstWord == 'ER+P_s'):
				line = "ER+P_s %dkvarh" % (ERplusP_s)
				line = line + " %c" % edf_checksum(line)
					
			elif (firstWord == 'ER-P_s'):
				line = "ER-P_s %dkvarh" % (ERmoinsP_s)
				line = line + " %c" % edf_checksum(line)
						
			elif (firstWord == 'PTCOUR1'):
				line = "PTCOUR1 %s" % (PTCOUR1_array[PTCOUR1_idx]) 
				line = line + " %c" % edf_checksum(line)
				
			ser.write(b'\x0A')	
			print ("%s" % line)
			ser.write(line.encode())
			ser.write(b'\x0D')
ser.close()