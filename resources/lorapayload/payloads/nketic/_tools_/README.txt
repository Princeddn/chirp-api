TIC frame conversion tools (CODEC)
==================================

"tictobin" : Tool to create binarized string from ASCII (ERDF) TIC datafow 
             This tool can also be used to create prorotypes of ZCL report
             configuration frame for TIC reporting.
"bintotic" : Tool to translate any incoming binarized frame to "readable" ASCII (ERDF) TIC format

These tools can be compiled :
- With embeded Makefile under linux. Please use Cgwin or MinGW under windows. (See Makefile Header comments)
- With coresponding codeblocks projects under CodeBlocks directory for debugging purpose

Exemples:
---------
1) Usage of tictobin to create report configuration (-r 1m/10m) and show reformated TIC frame with calculated CRCs (-srtf)
..........................................................................................................................
tictobin-WIN.exe -v -nc -nfv 2 -r 1m/10m -srtf
<
OPTARIF * x
ISOUSC 00 x
BASE 0 x
>
Frame received (36 bytes) from 'MT_CBEMM_ICC' meter !
Descriptor (2 bytes / 3 field(s)): 0270
Serialised binary TIC Data (9 bytes [Last Short: 9]): 02702a000000000000

UNCOMPRESSED DESCRIPTORS, Report configuration (47 bytes):
1106005400000041003c02582210000000000000000000000000000070100000000000000000000000000000102a00

ORIGINAL DESCRIPTOR TOO SMALL FOR REQUIRED FILTER !!

COMPRESSED DESCRIPTORS, Report configuration (19 bytes):
1106005400000041003c025806027022042a00
Reformated TIC frame :
<
OPTARIF * ?
ISOUSC 00 6
BASE 000000000 K
>

<
HCHC 0 x
HCHP 0 x
PAPP 50 x
>

2) Usage of bintotic to translate incomming ZCL TIC frame
.........................................................
$ ./bintotic -v
110A005700004147A9030D0E1213404445190510101325494E4143544946003030300019051010140058585800190510101E005858580030303000190510101E005858580019051010230058585800
>>>> New line received (079 byte(s)) <<<<
110A005700004147A9030D0E1213404445190510101325494E4143544946003030300019051010140058585800190510101E005858580030303000190510101E005858580019051010230058585800
Cluster ID/Attribute ID: 0x0057 / 0x0000
Received ZCL header (8 byte(s)): Report
Received serialized TIC frame (71 byte(s))
Received descriptor for MT_PMEPMI meter (9 byte(s)) : a9030d0e1213404445
Reformated TIC frame (206 byte(s))
<
DATE 25/05/16 16:19:37 >
TARIFDYN INACTIF _
ETATDYN1 000 Z
TDYN1FD 25/05/16 16:20:00-XXX =
TDYN1FF 25/05/16 16:30:00-XXX @
ETATDYN2 000 [
TDYN2FD 25/05/16 16:30:00-XXX ?
TDYN2FF 25/05/16 16:35:00-XXX F
>


Serial TIC simulator:
=====================
Thes are sample of what can be done to simulate TIC data flow on serial port.

prerequesites: python2.7 and pyserial 2.7 installed on a PC !!

Launch under Windows or Linux console:
python serialticsim.py
python serialticsim_with_BASE_PAPP_steps.py

The simulators simply use input "trame.txt" file with ETX and STX replaced by '>' and '<'.

[serialticsim_with_BASE_PAPP_steps.py]
- Add an example of Python script moduling PAPP or BASE


NOTES About ETIC usage:
- This script can be used to pilot directly the Energisme (etic) simulator
- Power supply of etic is 9 VDC 100 mA, with ground outside of connector