/*
 * Copyright (c) 2012, Watteco
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the Institute nor the names of its contributors
 *    may be used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE INSTITUTE AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE INSTITUTE OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 */

/**
 * \file
 * 		Binbary to TIC converter
 * \author
 *      P.E. Goudet <pe.goudet@watteco.com>
 */

/*============================ INCLUDE =======================================*/


#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#include "tic-formater.h"

#define FPRINTF(file, ...) { fprintf(file, __VA_ARGS__); fflush(file); }

static const char TIC_meter_type_str[TIC_NB_DESC_TYPE+1][13]={
	"MT_UNKNOWN",
	"MT_CT",
	"MT_CBEMM",
	"MT_CBEMM_ICC",
	"MT_CBETM",
	"MT_CJE",
	"MT_ICE",
	"MT_STD",
	"MT_PMEPMI",
	"MT_PMEPMI13",
	"MT_NULL",
	"MT_ICE_p",
	"MT_ICE_p1",
	"MT_END"
};


unsigned char tmpbuf[TIC_BIG_PACKED_BUF_SZ + 2];
char line_buf[2048];

// Global parameters for tictobin
TIC_meter_type_t meter_type;
unsigned char verbose, zcl_header_present;

//---------------------------------------------------------------------------
typedef enum {
  new_char=0,
  hex_tag,
  hex_msb
}InputStates;

#define HEX_TAG '$'
#define ISHEX(c) ((c>='0' && c<='9') || (c>='a' && c<='f')  || (c>='A' && c<='F'))
#define HEX2BYTE(c) ((c>='0' && c<='9') ? c - '0' : 10 + ((c>='a' && c<='f') ? c - 'a' : c -'A'))

signed short str2buf(char* str,  unsigned char *outBuf) {

	InputStates state=new_char;
	int outBufSz=0, i;
	char curr_char,curr_byte;
	char nohextag=0;

	if (str[0] != '$') {
		nohextag=1;
		state=hex_tag;
	}

	for (i=0;i < strlen(str); i++) {
		curr_char=str[i];
		switch (state) {
			case new_char:
				if (curr_char == HEX_TAG) {
					state=hex_tag;
				} else {
					outBuf[outBufSz]=curr_char; outBufSz++;
				}
				break;

			case hex_tag:
				if (curr_char == HEX_TAG) {
					outBuf[outBufSz]=curr_char; outBufSz++;
					state=new_char;
				} else {
					if (ISHEX(curr_char)) {
						curr_byte = HEX2BYTE(curr_char) << 4;
						state=hex_msb;
					} else {
						return (-1 * (i+1)) ;
					}
				}
				break;


			case hex_msb:
				if (ISHEX(curr_char)) {
					curr_byte += HEX2BYTE(curr_char);
					outBuf[outBufSz]=curr_byte; outBufSz++;
					state=(nohextag==1 ? hex_tag : new_char);
				} else {
					return (-1 * (i+1));
				}
				break;

			default:
				return  (-1 * (i+1));

		} // switch
	} // for strlen(inBuf)

	state = new_char; // reset parser for next parsing

	return outBufSz;
} // str2Buf()

//---------------------------------------------------------------------------
void print_usage(char * app_name) {
unsigned char i;
	FPRINTF(stderr,"\n");
	FPRINTF(stderr,
		"Usage: %s  [-h] [-mt meterType] [-z] [-v]\n"
		"Convert input serialized byte string (hex format supported($xx)) to a TIC string.\n",
		app_name);
	FPRINTF(stderr,
		"  -h :            Print current help and exit.\n"
		"  -nz :           No ZCL header present, olny binarized TIC string to deserialize and translate.\n\n"
		"  -mt meterType : ");

		for (i=0; i<(TIC_NB_DESC_TYPE + 1); i++) {
			if (i > 0) FPRINTF(stderr," | ");
			FPRINTF(stderr,"%s",TIC_meter_type_str[i]);
		}
	FPRINTF(stderr,"\n");
	FPRINTF(stderr,
		"                  Selected meter type: %s\n", TIC_meter_type_str[meter_type]);

	FPRINTF(stderr,
		"  -v :            Verbose mode giving info about conversion status.\n");
}

//---------------------------------------------------------------------------
int main(int argc, char * argv[])
{
	signed short n;
	short zcl_header_size=0;
	unsigned short attribute_id, cluster_id;
	unsigned char i, process_it;
	unsigned char narg = 0;
	unsigned char * pt_start = NULL;
	TIC_meter_type_t mt=MT_UNKNOWN;


	// Default working parameters
	verbose = 0;
	meter_type = MT_CBEMM_ICC;
	zcl_header_present = 1;

	// PARSE PARAMS ---------------------------------
	while (argc > 1) {
		argc--; narg++;
		if (strcmp(argv[narg],"-mt") == 0) {
			argc--; narg++;
			if (argc == 0) {
				FPRINTF(stderr,"%s Error: Option '-mt' needs an argument.\n", argv[0]);
				print_usage(argv[0]);
				return(1);
			} else {
				for (i=0; i<(TIC_NB_DESC_TYPE+1); i++)
					if (strcmp(TIC_meter_type_str[i], argv[narg]) == 0) break;
				if (i == (TIC_NB_DESC_TYPE+1)) {
					FPRINTF(stderr,"%s Error: '-mt' option argument is not valid.\n", argv[0]);
					print_usage(argv[0]);
					return(1);
				} else {
					meter_type = (TIC_meter_type_t)i;
				}
			}

		} else if  (strcmp(argv[narg],"-v") == 0) {
			verbose=1;

		} else if  (strcmp(argv[narg],"-nz") == 0) {
			zcl_header_present=0;

		} else if  (strcmp(argv[narg],"-h") == 0) {
			print_usage(argv[0]);
			return(0);

		} else {
			FPRINTF(stderr,"%s Error: Unexpected argument.\n", argv[0]);
			print_usage(argv[0]);
			return(1);

		}
	}

	FPRINTF(stderr, "** bintotic started **\n");
	FPRINTF(stderr, "** Please enter hexadecimal string (TIC read response, report or report config) \n");

	// DO THE JOB ---------------------------------
	// Permanently parse stdin
	while ((gets(line_buf)) != NULL) {

		n = str2buf(line_buf,  tmpbuf);
		pt_start = tmpbuf;
		zcl_header_size=0;
		process_it=1;

		if (verbose) {
				FPRINTF(stdout, "\n>>>> New line received (%03d byte(s)) <<<<\n",n );
				FPRINTF(stdout, "%s\n", line_buf);
		}


		if (n < 0) {
			FPRINTF(stderr,"Invalid hexadecimal string !\n");
			process_it = 0;
		}

		if (! zcl_header_present) {
			mt = meter_type;

		} else {
			// Extract ZCL headers
			// Response meter type: $11 $01 $00$53 $00$01 $00 $20 $04
			// Response:   $11 $01 $00$53 $00$00 $00 $41 $xx
			// Report:     $11 $0A $00$53 $00$00     $41 $xx
			// Cfg report:
			//   response: $11 $09 $00$53 $00 $00 $00$00 $41 $00$02 $00$0a $xx
			//   request : $11 $06 $00$53 $00 $00$00     $41 $00$02 $00$0a $xx
			//
			//   Note si $41 ==> $xx et Si $43 ==> $xxxx
			//
			// ou $xx = taille du byte string

			cluster_id   = (((unsigned short)tmpbuf[2]) << 8) + tmpbuf[3];

			if ((tmpbuf[0] == 0x11) && (tmpbuf[1] == 0x01) &&
			    ((tmpbuf[3] == 0x53)||(tmpbuf[3] == 0x54)||(tmpbuf[3] == 0x55)||(tmpbuf[3] == 0x56)||(tmpbuf[3] == 0x57)) &&
				(tmpbuf[4] == 0x00) && (tmpbuf[5] == 0x03)) {
				if (verbose) {
					FPRINTF(stdout,"ZCL TIC Meter type: %s  \n",TIC_meter_type_str[tmpbuf[8]]);
				}
				process_it = 0;

			} else if ((tmpbuf[0] == 0x11) && (tmpbuf[1] == 0x01)) {
				zcl_header_size=9;
				attribute_id = (((unsigned short)tmpbuf[4]) << 8) + tmpbuf[5];

			} else if ((tmpbuf[0] == 0x11) && (tmpbuf[1] == 0x0A)) {
				zcl_header_size=8;
				attribute_id = (((unsigned short)tmpbuf[4]) << 8) + tmpbuf[5];

			} else if ((tmpbuf[0] == 0x11) && (tmpbuf[1] == 0x09)) {
				zcl_header_size=14;
				attribute_id = (((unsigned short)tmpbuf[6]) << 8) + tmpbuf[7];
				if (verbose) {
					FPRINTF(stdout,"ZCL report config response: ");
					FPRINTF(stdout,(tmpbuf[9]  & 0x80 ? "%dm" : "%ds"), (((unsigned short) (tmpbuf[9]  & 0x7F)) << 8) + tmpbuf[10]);
					FPRINTF(stdout,"/");
					FPRINTF(stdout,(tmpbuf[11] & 0x80 ? "%dm" : "%ds"), (((unsigned short) (tmpbuf[11] & 0x7F)) << 8) + tmpbuf[12]);
					FPRINTF(stdout,"\n");
				}

			} else if ((tmpbuf[0] == 0x11) && (tmpbuf[1] == 0x06)) {
				zcl_header_size=13;
				attribute_id = (((unsigned short)tmpbuf[5]) << 8) + tmpbuf[6];
				if (verbose) {
					FPRINTF(stdout,"ZCL report config request: ");
					FPRINTF(stdout,(tmpbuf[8]  & 0x80 ? "%dm" : "%ds"), (((unsigned short) (tmpbuf[8]  & 0x7F)) << 8) + tmpbuf[9]);
					FPRINTF(stdout,"/");
					FPRINTF(stdout,(tmpbuf[10] & 0x80 ? "%dm" : "%ds"), (((unsigned short) (tmpbuf[10] & 0x7F)) << 8) + tmpbuf[11]);
					FPRINTF(stdout,"\n");
				}

			} else if (tmpbuf[0] == 0x11) {
				FPRINTF(stderr,"ZCL Frame does not contain TIC data.\n");
				process_it = 0;

			}  else {
				FPRINTF(stderr,"Error: Not a ZCL frame received !\n");
				process_it = 0;
			}

			if (process_it) {
				if      ((cluster_id == 0x0053) && ((attribute_id >> 8) <= 1 ) && ((attribute_id & 0x00FF) == 00 ) ) { mt = MT_ICE; }
				else if ((cluster_id == 0x0053) && ((attribute_id >> 8) <= 1 ) && ((attribute_id & 0x00FF) == 01 ) ) { mt = MT_ICE_p;}
				else if ((cluster_id == 0x0053) && ((attribute_id >> 8) <= 1 ) && ((attribute_id & 0x00FF) == 02 ) ) { mt = MT_ICE_p1;}
				else if ((cluster_id == 0x0054) && ((attribute_id >> 8) <= 5 ) && ((attribute_id & 0x00FF) == 00 ) ) { mt = MT_CBEMM;}
				else if ((cluster_id == 0x0055) && ((attribute_id >> 8) <= 5 ) && ((attribute_id & 0x00FF) == 00 ) ) { mt = MT_CJE;}
				else if ((cluster_id == 0x0056) && ((attribute_id >> 8) <= 5 ) && ((attribute_id & 0x00FF) == 00 ) ) { mt = MT_STD;}
				else if ((cluster_id == 0x0057) && ((attribute_id >> 8) <= 5 ) && ((attribute_id & 0x00FF) == 00 ) ) { mt = MT_PMEPMI;}
				else {
					FPRINTF(stderr,"Error: Unmanaged Cluster ID/Attribute ID!\n");
					process_it = 0;
				}

				if (verbose) {
					FPRINTF(stderr,"Cluster ID/Attribute ID: 0x%04x / 0x%04x\n", cluster_id, attribute_id);
				}
			}
		}

		zcl_header_size+=(tmpbuf[7]==0x43 ? 1 : 0); // si 0x43 ==> taille sur 2 octets
		pt_start += zcl_header_size;

		if (process_it) {

			if (mt == MT_NULL) {
				FPRINTF(stderr,"Error: Can't process with MT_NULL meter type !\n");
				process_it = 0;
			}

			if (mt == MT_UNKNOWN) {
				FPRINTF(stderr,"Error: Can't process with MT_UNKNOWN meter type !\n");
				process_it = 0;
			}
		}

		if (process_it) {
			unsigned char converted = 0;
			// Necessary input frame conversion for compatibility of following processings if original header
			if (zcl_header_size==14 || zcl_header_size==13 || zcl_header_size==15) {
				converted = ucTICDescPtrConvertFromOriginalHeader(aTB_CRIT_GET_FILTER_DESC(pt_start));
				converted |= ucTICDescPtrConvertFromOriginalHeader(aTB_CRIT_GET_TRIG_DESC(pt_start));
			} else {
				converted = ucTICDescPtrConvertFromOriginalHeader(aTB_GET_DESC(pt_start));
			}

			if (verbose) {

				if (converted) {
					FPRINTF(stdout, "Header converted from ORIGINAL.\n");
				}

				if (zcl_header_size)
					FPRINTF(stdout, "Received ZCL header (%d byte(s)): %s \n",
						zcl_header_size,
						(zcl_header_size==9 ? "Response" :
						 (zcl_header_size==8 ? "Report"  :
						  (zcl_header_size==13 ?"Config request" : "Config response"))));
				FPRINTF(stdout, "Received serialized TIC frame (%d byte(s)) \n", n - zcl_header_size);
				if (zcl_header_size==14 || zcl_header_size==13) {

					FPRINTF(stdout, "Received filter descriptor for %s meter (%d byte(s)) : ",
						TIC_meter_type_str[mt], aGET_DESCPTR_SIZE(aTB_CRIT_GET_FILTER_DESC(pt_start)));
					for (i=0; i<aGET_DESCPTR_SIZE(aTB_CRIT_GET_FILTER_DESC(pt_start));i++)
						FPRINTF(stdout,"%02x",aTB_CRIT_GET_FILTER_DESC(pt_start)[i]);
					FPRINTF(stdout,"\n");

					FPRINTF(stdout, "Received criteria descriptor for %s meter (%d byte(s)) : ",
						TIC_meter_type_str[mt], aGET_DESCPTR_SIZE(aTB_CRIT_GET_TRIG_DESC(pt_start)));
					for (i=0; i<aGET_DESCPTR_SIZE(aTB_CRIT_GET_TRIG_DESC(pt_start));i++)
						FPRINTF(stdout,"%02x",aTB_CRIT_GET_TRIG_DESC(pt_start)[i]);

				} else {
					FPRINTF(stdout, "Received descriptor for %s meter (%d byte(s)) : ",
						TIC_meter_type_str[mt], aGET_DESCPTR_SIZE(aTB_GET_DESC(pt_start)));
					for (i=0; i<aGET_DESCPTR_SIZE(aTB_GET_DESC(pt_start));i++)
						FPRINTF(stdout,"%02x",aTB_GET_DESC(pt_start)[i]);
				}
				FPRINTF(stdout,"\n");
			}

			tic_formater_init(tic_metertype_to_meterdesc(mt)) ;

			if (zcl_header_size==14 || zcl_header_size==13) { // Case read or write report cofiguration 2 descriptors, filter and criteria + data
				tic_formater_frame_put(line_buf,
					aTB_CRIT_GET_FILTER_DESC(pt_start),
					aTB_CRIT_GET_TRIG_DESC(pt_start),
					aTB_CRIT_GET_TRIG_BUF(pt_start));

			} else { // Usual case only one descriptor available
				tic_formater_frame_put(line_buf,
					NULL,
					aTB_GET_DESC(pt_start),
					aTB_GET_BUF(pt_start));
			}

			if (verbose) {
				FPRINTF(stdout, "Reformated TIC frame (%d byte(s))\n", (int)strlen(line_buf) );
			}
			FPRINTF(stdout,"%s",line_buf);
		}
	}

	return(0);
}

