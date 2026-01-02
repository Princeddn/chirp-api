import serial
from time import sleep
# import numpy as np

port = "com2"
speed = 9600

#filename="PME-PMI_Test_Telereleve_C3_4_ModifPEG.log"
#filename = "trame.txt"
#filename = "LOGS-TIC\LinkyPalier0-NiceGrid\UneTrameSTDwCHKS.txt"
#filename = "LOGS-TIC\LinkyPalier0-NiceGrid\UneTrameSTD.txt"
filename = "LOGS-TIC\UneTrameSTDwCHKS.txt"
#filename = "LOGS-TIC\UneTrameSTD.txt"
# KO: filename = "LOGS-TIC\UneTrameSTDwCHKS-PM1surSTGE-KOPMdate.txt"
#filename = "LOGS-TIC\UneTrameSTDwCHKS-PM1surSTGE.txt"
#filename = "LOGS-TIC\UneTrameSTDwCHKS-PM1surSTGETri.txt"
#filename = "LOGS-TIC\UneTrameCJETest.txt"
#filename = "LOGS-TIC\UneTrameCBETriHC.txt"
#filename = "LOGS-TIC\UneTrameICETest.txt"
#filename = "trame2.txt"
#filename = "TEST_20160712-HCE_HPE-HPE_HCE_PREAVIS_PMs\ACTIONS-1-2-3A-3B-3C.txt"
#filename = "Test_TDYN_06_09_2016_17_15.log"

print ('\n*** Starting ***\n')
ser = serial.Serial(port, speed, bytesize=serial.SEVENBITS, timeout=None, xonxoff=0, rtscts=0, parity=serial.PARITY_EVEN,dsrdtr=False)


print ('\n*** Starting ***\n')

#print(array)
GoOn = True
while GoOn:
	# GoOn = False # Execute Once onle (comment to permanently repeat the input file
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
			print ("%s" % line)
			ser.write(b'\x0A')	
			ser.write(line.encode())
			ser.write(b'\x0D')
		
		

ser.close()