import serial
from time import sleep
import datetime 
import time
# import numpy as np

#- Le temps evolue normalement (heure reelle): theNow
#- PTCOUR1 varie entre HPH, HCH, HCE, HPE toutes les PTCOUR1_DT 
#- On conserve les indices courants de chaque periode tarifaire utilisee
#- On initialise les indices de chaque periode tarifaire utilisee a diffrentes valeurs
#- On fixe des valeurs pour chaque periode tarifaire de :
#  . PAMoy:  Puissance active moyenne consommee => PA1_s,...,PA6_s
#  . PRpMoy: Puissance reactive positive moyenne consommee
#  . PRnMoy: Puissance reactive negative moyenne consommee
#- A chaque iteration de flux on incremente les EAP_s, ER+P_s, ER-P_s 
#  en fonction du temps passe est des valeurs de puissance active moyennes fixees ci-avant:
#  Exy_s += PxyMoy * (elapsed_time/3600)  


def edf_checksum(line):
	chks = sum(map(ord, line))
	chks &= 0x3F
	chks += 0x20
	return chks

port = "com2"
#should be Ok at : 
#  1200, 2400, 4800,9600 and 19200 for RS232 input
#  1200, 9600 for 50KHz input
speed = 19200

filename = "trame_PMEPMI_EDF.txt"

ser = serial.Serial(port, speed, bytesize=serial.SEVENBITS, timeout=None, xonxoff=0, rtscts=0, parity=serial.PARITY_EVEN,dsrdtr=False)

print ('\n*** Starting ***\n')

BeginDate = datetime.datetime.now()

# DATE = BeginDate
DATE = datetime.datetime(2000, 1, 1, 0, 0, 0)
DATE_lastDate = BeginDate

PTCOUR1_DT       = 3600
PTCOUR1_lastDate = BeginDate 
PTCOUR1_idx      = 0
PTCOUR1_array = [   "HPH",   "HPH",   "HPH",   "HPH",    "HPH"]

#Energies Td
TopTdMinutes = 10  # Minutes
EA_s         = 0.0 # Wh
ERp_s        = 0.0 # VArh
ERn_s        = 0.0 # VArh

#Energies PT
EAP_s         = [    10.0,   100.0,  1000.0,  2000.0,  6000.0] # kWh
ERpP_s        = [    10.0,    10.0,    10.0,    10.0,    10.0] # kVArh
ERnP_s        = [    20.0,    20.0,    20.0,    20.0,    20.0] # kVArh

# 1 minute (PA) et 10 minutes (ERp) 
PAMoy_s      = [ 36.0, 36.0, 36.0, 36.0, 36.0] # kW
PRpMoy_s     = [ 18.0, 18.0, 18.0, 18.0, 18.0] # kVAr

#PAMoy_s      = [ 72.0, 72.0, 72.0, 72.0, 72.0] # kW
#PRpMoy_s     = [ 72.0, 72.0, 72.0, 72.0, 72.0] # kVAr

# 6 secondes (PA) et 12 secondes (ERp) 
#PAMoy_s       = [ 600.0, 600.0, 600.0, 600.0, 600.0] # kW
#PRpMoy_s      = [ 300.0, 300.0, 300.0, 300.0, 300.0] # kVAr

# Simulation 60 kW 6 kVAr a poids 40 i/Wh et 40 i/VArh
#Attention: Cela va generer environ  1 impulsion toutes les 2,4 secondes ... 
#           le lissage va essayer de fonctionner mais cela ne sera pas parfait
#PAMoy_s       = [ 1500.0, 1500.0, 1500.0, 1500.0, 1500.0] # kW
#PRpMoy_s      = [  150.0,  150.0,  150.0,  150.0,  150.0] # kVAr

PRnMoy_s      = [  0.0,0.0, 0.0, 0.0, 0.0] # kVAr


theNow          = datetime.datetime.now()	
elapsed_time_td_prec = (theNow.minute % TopTdMinutes) * 60 + theNow.second

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
			time.sleep (16 / 1000.0) # Spec: Should wait beetween 16 to 33 ms between "trames"
			
		elif(line == '<'):
			print ("<")
			ser.write(b'\x02')
			
		else:
			firstWord=line.split()[0]
			
			if (firstWord == 'DATE'):
					
				line = "DATE %s" % (theNow.strftime("%d/%m/%y %H:%M:%S"))
				line = line + " %c" % edf_checksum(line)
				
				# To do calculations only once do it on Rx of any label. Here DATE.
				
				# Evaluate time since last frame
				elapsed_time = theNow - theNowPrec
				elapsed_time = (elapsed_time.seconds * 1000.0) + (elapsed_time.microseconds / 1000.0) # In Milliseconds
				elapsed_time = elapsed_time / (3600.0 * 1000.0) # In Hours
				
				print ("elapsed_time (s): %f" % (elapsed_time ) )
				
				# Simulate periods PT ===================================
				if (((theNow - PTCOUR1_lastDate).seconds) >= PTCOUR1_DT ):
					PTCOUR1_idx = (PTCOUR1_idx + 1) % len(PTCOUR1_array)
					PTCOUR1_lastDate = theNow 
					elapsed_time_PT  = 0
				else:
					elapsed_time_PT  = elapsed_time
				
				# Evaluate Energies period PT ==============================
				
				EAP_s[PTCOUR1_idx]  += (PAMoy_s [PTCOUR1_idx] * elapsed_time_PT)
				ERpP_s[PTCOUR1_idx] += (PRpMoy_s[PTCOUR1_idx] * elapsed_time_PT)
				ERnP_s[PTCOUR1_idx] += (PRnMoy_s[PTCOUR1_idx] * elapsed_time_PT)
				
				# Evaluate Energies Td ===================================
				# Elapsed Time since start of tenth of minutes
				elapsed_time_td = (theNow.minute % TopTdMinutes) * 60 + theNow.second
				
				# 10 minutes ended => reset energy Td
				if (elapsed_time_td < elapsed_time_td_prec):
					EA_s  = 0
					ERp_s = 0
					ERn_s = 0
					elapsed_time_td_prec = 0
			
				#print ("elapsed_time_td_prec (s): %f" % elapsed_time_td_prec )
				#print ("elapsed_time_td (s): %f" % elapsed_time_td )
					
				#EA_s  += (PAMoy_s [PTCOUR1_idx] * (elapsed_time_td - elapsed_time_td_prec)/3600) * 1000
				#ERp_s += (PRpMoy_s[PTCOUR1_idx] * (elapsed_time_td - elapsed_time_td_prec)/3600) * 1000
				#ERn_s += (PRnMoy_s[PTCOUR1_idx] * (elapsed_time_td - elapsed_time_td_prec)/3600) * 1000
					
				EA_s  += (PAMoy_s [PTCOUR1_idx] * 1000.0 * (elapsed_time)) 
				ERp_s += (PRpMoy_s[PTCOUR1_idx] * 1000.0 * (elapsed_time))
				ERn_s += (PRnMoy_s[PTCOUR1_idx] * 1000.0 * (elapsed_time))
	
				elapsed_time_td_prec = elapsed_time_td
				
			elif (firstWord == 'EA_s'):
				line = "EA_s %dWh" % (EA_s)
				line = line + " %c" % edf_checksum(line)
				
			elif (firstWord == 'ER+_s'):
				line = "ER+_s %dvarh" % (ERp_s)
				line = line + " %c" % edf_checksum(line)
				
			elif (firstWord == 'ER-_s'):
				line = "ER-_s %dvarh" % (ERn_s)
				line = line + " %c" % edf_checksum(line)
						
			elif (firstWord == 'PTCOUR1'):
				line = "PTCOUR1 %s" % (PTCOUR1_array[PTCOUR1_idx]) 
				line = line + " %c" % edf_checksum(line)
				
			elif (firstWord == 'EAP_s'):
				line = "EAP_s %dkWh" % (EAP_s[PTCOUR1_idx])
				line = line + " %c" % edf_checksum(line)
				
			elif (firstWord == 'ER+P_s'):
				line = "ER+P_s %dkvarh" % (ERpP_s[PTCOUR1_idx])
				line = line + " %c" % edf_checksum(line)
					
			elif (firstWord == 'ER-P_s'):
				line = "ER-P_s %dkvarh" % (ERnP_s[PTCOUR1_idx])
				line = line + " %c" % edf_checksum(line)
				
			ser.write(b'\x0A')	
			print ("%s" % line)
			ser.write(line.encode())
			ser.write(b'\x0D')

ser.close()