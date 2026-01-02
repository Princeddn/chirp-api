import serial
import math
from time import sleep
import datetime
# import numpy as np

def edf_checksum(line):
	chks = sum(map(ord, line))
	chks &= 0x3F
	chks += 0x20
	return chks
	
def lineFromfuncOfSeconds(field, func):
	VAL = eval (func)
	#if firstWord not in vars_dict:
	#	vars_dict[firstWord] = 0
	#VAL = VAL + vars_dict[firstWord] # does a exist in the current namespace
	line = firstWord + " %d" % VAL
	line = line + " %c" % edf_checksum(line)
	return line

port = "com2"
speed = 9600

#filename = "trame.txt"
filename = "LOGS-TIC\UneTrameCBETriHC.txt"
#filename = "LOGS-TIC\UneTrameCBETriTempo.txt"
#filename = "TEST_20160712-HCE_HPE-HPE_HCE_PREAVIS_PMs\ACTIONS-1-2-3A-3B-3C.txt"
#filename = "Test_TDYN_06_09_2016_17_15.log"

print ('\n*** Starting ***\n')
ser = serial.Serial(port, speed, bytesize=serial.SEVENBITS, timeout=None, xonxoff=0, rtscts=0, parity=serial.PARITY_EVEN,dsrdtr=False)

SINUSPERIOD = 60*60 #Seconds
NP = 0

theStart = datetime.datetime.now()
theNow = datetime.datetime.now()

vars_dict = {}
	
NbOver = 0 # 20 # Set to 0 for NO Over (depassement)
nOver = 0
doDepassement = False

print ('\n*** Starting ***\n')


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
			# sleep(0.5)
			# sleep(3)
			
		elif(line == '<'):
			print ("<")
			ser.write(b'\x02')
			if (( nOver >= NbOver ) or (NbOver == 0) ):
				nOver = 0
				doDepassement = False
			else:
				nOver = nOver + 1
				doDepassement = True
			
		elif (line != ""):
			sleep(0.1)
			doNotPrint=False
			firstWord=line.split()[0]
			if (not doDepassement):
				if (firstWord == 'BASE'):
					line = lineFromfuncOfSeconds(firstWord, 
						"100 + 100 * math.sin((2 * math.pi * %f) / %f )" % 
						((datetime.datetime.now() - theStart).seconds,SINUSPERIOD))
					
				if (firstWord == 'HCHC'):
					line = lineFromfuncOfSeconds(firstWord, 
						"100 + 100 * math.sin((2 * math.pi * %f) / %f )" % 
						((datetime.datetime.now() - theStart).seconds,SINUSPERIOD))
					
				if (firstWord == 'HCHP'):
					line = lineFromfuncOfSeconds(firstWord, 
						"200 + 200 * math.sin((2 * math.pi * %f) / %f )" % 
						((datetime.datetime.now() - theStart).seconds,SINUSPERIOD/2))
					
				if (firstWord == 'PAPP'):
					line = lineFromfuncOfSeconds(firstWord, 
						"200 + 200 * math.sin((10 * 2 * math.pi * %f) / %f )" % 
						((datetime.datetime.now() - theStart).seconds,SINUSPERIOD/2))
			else:
				if (firstWord == 'ADCO'):
					lineTmp = "ADIR1 %d" % nOver
					lineTmp = lineTmp + " %c" % edf_checksum(lineTmp)
					print (lineTmp)
					ser.write(b'\x0A')	
					ser.write(lineTmp.encode())
					ser.write(b'\x0D')
					
					lineTmp = "ADIR2 888"
					lineTmp = lineTmp + " %c" % edf_checksum(lineTmp)
					print (lineTmp)
					ser.write(b'\x0A')	
					ser.write(lineTmp.encode())
					ser.write(b'\x0D')
					
					lineTmp = "ADIR3 999"
					lineTmp = lineTmp + " %c" % edf_checksum(lineTmp)
					print (lineTmp)
					ser.write(b'\x0A')	
					ser.write(lineTmp.encode())
					ser.write(b'\x0D')

				if (firstWord != 'ADCO') and (firstWord != "IINST1") and (firstWord != "IINST2") and (firstWord != "IINST3"):
					doNotPrint=True
				
			if (not doNotPrint):
				print ("%s" % line)
				ser.write(b'\x0A')	
				ser.write(line.encode())
				ser.write(b'\x0D')
		
ser.close()