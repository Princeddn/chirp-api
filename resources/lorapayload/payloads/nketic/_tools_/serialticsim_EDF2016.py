import serial
from time import sleep
import datetime
# import numpy as np

def edf_checksum(line):
	chks = sum(map(ord, line))
	chks &= 0x3F
	chks += 0x20
	return chks

port = "com1"
speed =4800

#filename = "trame.txt"
#filename = "trame-PMEPMI.txt"

ser = serial.Serial(port, speed, bytesize=serial.SEVENBITS, timeout=None, xonxoff=0, rtscts=0, parity=serial.PARITY_EVEN,dsrdtr=False)

print ('\n*** Starting ***\n')

#print(array)

# Manage DATEPA1 changes for specific tests
datePA1 = datetime.datetime(2000, 1, 1, 0, 0, 0)
beginDate = datetime.datetime.now()
lastDatePA1 = beginDate
lastDatePTCOUR1 = beginDate
lastDatePTCOUR2 = beginDate
lastDateTARIFDYN = beginDate
lastDatePREAVIS = beginDate

DATEPA1_DT = 60 #----------- Specifer la periode
PA1_s = 0
EAP_s = 0
EAP_i = 0
ERplusP_s = 0
ERmoinsP_s = 0

PTCOUR1_DT = 80 #----------- Specifer la periode
dataPt = ["HPH", "HCH", "HCE", "HPE"]
dataTARIFDYN = ["ACTIF", "INACTIF"]

idx_PTCOUR1 = 0
idx_PTCOUR2 = 0
idx_TARIFDYN = 0
idx_TFDYN = 0

EaPmoins1_s = 0
ERplusPmoins1_s = 0
PS = 0

PTCOUR2_DT = 90 #----------- Specifer la periode 
EaPmoins1_s2 = 0

TARIFDYN_DT = 100 #----------- Specifer la periode 
TDYN1FD = 0
TDYN1FF = 0
TDYN2FD = 0
TDYN2FF = 0

PREAVIS_DT = 100 #----------- Specifer la periode
# PREAVIS_DU = 10
on_preavis = False

GoOn = True
while GoOn:
	GoOn = False # Execute once only the file
	theNow = datetime.datetime.now()
	
	array = open(filename,'r').read().split('\n')
	#ser.write(b'\x02')
	#print ("<")
	for line in array:
		
		if(line == '>'):
			print (">")
			ser.write(b'\x03') 
			sleep(0.5)
			
		elif(line == '<'):
			print ("<")
			ser.write(b'\x02')
			
		else:
			firstWord=line.split()[0]
			
			if (firstWord == 'DATE'):
				line = "DATE %s" % (theNow.strftime("%d/%m/%y %H:%M:%S"))
				line = line + " %c" % edf_checksum(line)
			
			elif (firstWord == 'DATEPA1'):
				PA1_s = (PA1_s + 100) % 32768
				if (((theNow - lastDatePA1).seconds) >= DATEPA1_DT ):
					datePA1 += datetime.timedelta(minutes = 10)
					lastDatePA1 = theNow
					PA1_s += 1
					EAP_s += 1
					EAP_i += 1
					ERplusP_s += 1
					ERmoinsP_s += 1
				line = "DATEPA1 %s" % (datePA1.strftime("%d/%m/%y %H:%M:%S"))
				line = line + " %c" % edf_checksum(line)
					
			elif (firstWord == 'PA1_s'):
				line = "PA1_s %dkW" % (PA1_s)
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
				if(((theNow -lastDatePTCOUR1).seconds) >= PTCOUR1_DT ):
					lastDatePTCOUR1 = theNow
					EaPmoins1_s += 1
					ERplusPmoins1_s += 1
					PS += 1
					idx_PTCOUR1 = (idx_PTCOUR1 + 1) % 4
				line = "PTCOUR1 %s" % (dataPt[idx_PTCOUR1]) 
				line = line + " %c" % edf_checksum(line)
					
			elif (firstWord == 'EaP-1_s'):
				line = "EaP-1_s %dkWh" % (EaPmoins1_s)
				line = line + " %c" % edf_checksum(line)
				
			elif (firstWord == 'ER+P-1_s'):
				line = "ER+P-1_s %dkvarh" % (ERplusPmoins1_s)
				line = line + " %c" % edf_checksum(line)
				
			elif (firstWord == 'PS'):
				line = "PS %dkVA" % (PS)
				line = line + " %c" % edf_checksum(line)
				
			elif (firstWord == 'PTCOUR2'):
				if(((theNow - lastDatePTCOUR2).seconds) >= PTCOUR2_DT ):
					lastDatePTCOUR2 = theNow
					EaPmoins1_s2 += 1
					idx_PTCOUR2 = (idx_PTCOUR2 + 1) % 4
				line = "PTCOUR2 %s" % (dataPt[idx_PTCOUR2]) 
				line = line + " %c" % edf_checksum(line)
				
			elif (firstWord == 'EaP-1_s2'):
				line = "EaP-1_s2 %dkWh" % (EaPmoins1_s2)
				line = line + " %c" % edf_checksum(line)
				
			elif (firstWord == 'TARIFDYN'):
				if(((theNow - lastDateTARIFDYN).seconds) >= TARIFDYN_DT ):
					lastDateTARIFDYN = theNow
					TDYN1FD = theNow
					TDYN1FF = theNow
					TDYN2FD = theNow
					TDYN2FF = theNow
					idx_TARIFDYN = (idx_TARIFDYN + 1) % 2
					idx_TFDYN = (idx_TFDYN + 1) % 4
				line = "TARIFDYN %s" % (dataTARIFDYN[idx_TARIFDYN]) 
				line = line + " %c" % edf_checksum(line)
					
			elif(firstWord == 'TDYN1FD'):
				#line = "TDYN1FD %s" % (theNow.strftime("%d/%m/%y %H:%M:%S") + "-%s" %(dataPt[idx_TFDYN]))
				line = "TDYN1FD 01/01/16 01:02:00" + "-%s" %(dataPt[idx_TFDYN])
				line = line + " %c" % edf_checksum(line)
					
			elif(firstWord == 'TDYN1FF'):
				line = "TDYN1FF %s" % (theNow.strftime("%d/%m/%y %H:%M:%S") + "-%s" %(dataPt[idx_TFDYN]))
				line = line + " %c" % edf_checksum(line)
			
			elif(firstWord == 'TDYN2FD'):
				line = "TDYN2FD %s" % (theNow.strftime("%d/%m/%y %H:%M:%S") + "-%s" %(dataPt[idx_TFDYN]))
				line = line + " %c" % edf_checksum(line)
					
			elif(firstWord == 'TDYN2FF'):
				line = "TDYN2FF %s" % (theNow.strftime("%d/%m/%y %H:%M:%S") + "-%s" %(dataPt[idx_TFDYN]))
				line = line + " %c" % edf_checksum(line)
			
			elif(firstWord == 'PREAVIS'):				
				if(((theNow - lastDatePREAVIS).seconds) >= PREAVIS_DT ): 
					on_preavis = not on_preavis
					lastDatePREAVIS = theNow
					
			if((on_preavis) or (firstWord != 'PREAVIS' )):
				ser.write(b'\x0A')	
				print ("%s" % line)
				ser.write(line.encode())
				ser.write(b'\x0D')
				
ser.close()