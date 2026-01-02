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
 * 		TIC to binary converter
 * \author
 *      P.E. Goudet <pe.goudet@watteco.com>
 */

/*============================ INCLUDE =======================================*/


#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#include "tic-tools.h"
#include "tic-parser.h"
#include "tic-formater.h"
#include "ong-codec-tic.h"

static const char TIC_meter_type_str[TIC_NB_MANAGED_METER+1][13]={
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
	"MT_NULL"
};

unsigned char tmpbuf[TIC_BIG_PACKED_BUF_SZ];
unsigned char tmpbufrpt[TIC_BIG_PACKED_BUF_SZ];
unsigned char tmpbufrpt2[TIC_BIG_PACKED_BUF_SZ];

char test_buf[4096];

// Global parameters for tictobin
char **glb_argv;
TIC_meter_type_t meter_type;
unsigned char verbose, report_cfg, chks_check, strict, show_reformated_tic_frame,created_filtered_tic_request,  shifted_report;
unsigned char test_tabular_api;
int nbf_to_valid, report_instance;
long report_min, report_max;


//---------------------------------------------------------------------------
void print_usage(char * app_name) {
unsigned char i;
	fprintf(stderr,"\n");
	fprintf(stderr,
		"Usage: %s  [-h] [-mt meterType] [-v] [-nc] [-nfv n] [-r min/max] [-fr] [-srtf] \n"
		"Convert input TIC string to a serialized bytes string (hex format (000A0B...)).\n",
		app_name);
	fprintf(stderr,
		"  -h :            Print current help and exit.\n"
		"  -mt meterType : ");

		for (i=0; i<(TIC_NB_MANAGED_METER + 1); i++) {
			if (i > 0) fprintf(stderr," | ");
			fprintf(stderr,"%s",TIC_meter_type_str[i]);
		}
	fprintf(stderr,"\n");
	fprintf(stderr,
		"                  Selected meter type: %s\n", TIC_meter_type_str[meter_type]);

	fprintf(stderr,
		"  -v :            Verbose mode giving info about conversion status.\n"
		"  -nc:            Do not check checksum (Default checked).\n"
		"  -ns:            Not strcit: Allow ignoring undefined attributes.\n"
		"  -nfv n:         Number of received fields to valid a frame (Default %d).\n"
		"  -r|rs min/max:  Create ZCL reporting configuration frame.\n"
		"                  Using 'min'/'max' report period parameters\n"
		"                  min and max accept following syntaxes: xxx ou xxxs => seconds, xxxm => minutes\n"
		"                  use '-rs' if 'shifted report' needed (report on value before modification)\n"
		"  -ri instance:   Create ZCL reporting configuration frame from a specific report instance (virtual attribute).\n"
		"                  Ignored if -r|-rs option not present.\n"
		"  -fr:            Create filtered request frame.\n"
		"  -srtf:          Show reformated tic frame from serialised one\n"
		"  -tapi:          Test Tabular API \n",
		nbf_to_valid);
}

//---------------------------------------------------------------------------
void msg_dump(TIC_parser_status_t * stat,
	TIC_BUF_TYPE * msg,
	TIC_meter_descriptor_t * pt_mt_desc) {

	unsigned short i;
    unsigned int n;
	signed int nrptcfg;

	unsigned short buf_size = (
			pt_mt_desc->meter_type == MT_ICE || (pt_mt_desc->meter_type == MT_ICE_p) || (pt_mt_desc->meter_type == MT_ICE_p1) ?
			TIC_PACKED_BUF_SZ : TIC_BIG_PACKED_BUF_SZ);

	// Necessary to PACK the serialized frame if originally not packed (like for ICEp and ICEp1)
	n = tic_serialize( pt_mt_desc,
		tmpbuf,
		msg,
		(TIC_desc_t *)aTB_GET_DESC(msg),
		NULL,
		buf_size,
		((pt_mt_desc->meter_type == MT_ICE_p) || (pt_mt_desc->meter_type == MT_ICE_p1) ? 1 : 0), // Only case where buf is unpacked ICEp and ICEp1 from parser
		0);

	if (verbose) {
		fprintf(stdout, "Descriptor (%d bytes / %d field(s)): ",aGET_DESCPTR_SIZE(tmpbuf),tic_nb_fields_selected((TIC_desc_t *)aTB_GET_DESC(tmpbuf)));
		for (i=0; i<aGET_DESCPTR_SIZE(tmpbuf);i++) fprintf(stdout,"%02x",aTB_GET_DESC(tmpbuf)[i]); fprintf(stdout,"\n");
		fprintf(stdout, "Serialised binary TIC Data (%d bytes [Last Short: %d]): ",
				n,*((unsigned short *) &(tmpbuf[buf_size - TIC_SERIALIZED_SIZE_SIZE])));
		for (i=0; i<n;i++) fprintf(stdout,"%02x",tmpbuf[i]); fprintf(stdout,"\n");
	}

	if (created_filtered_tic_request) {
		if (verbose) {
			fprintf(stdout, "Serialised binary filtered request (%d bytes): ",n + 5);
		}
		fprintf(stdout,"1150%s",
						(pt_mt_desc->meter_type == MT_ICE ? "0053000000" :
						 (pt_mt_desc->meter_type == MT_ICE_p ? "0053000001" :
						  (pt_mt_desc->meter_type == MT_ICE_p1 ? "0053000002" :
						   ((pt_mt_desc->meter_type >= MT_CT) && (pt_mt_desc->meter_type <= MT_CBETM) ? "0054000000" :
						    (pt_mt_desc->meter_type == MT_CJE ? "0055000000" :
						    (pt_mt_desc->meter_type == MT_STD ? "0056000000" :
						    (((pt_mt_desc->meter_type == MT_PMEPMI) || (pt_mt_desc->meter_type == MT_PMEPMI13)) ? "0057000000" :
						     "??????????"))))))));
		for (i=0; i<aGET_DESCPTR_SIZE(tmpbuf);i++) fprintf(stdout,"%02x",tmpbuf[i]); fprintf(stdout,"\n");
	}


	if (report_cfg) {
		if ((report_instance > 1) &&
			 ((pt_mt_desc->meter_type == MT_ICE) ||(pt_mt_desc->meter_type == MT_ICE_p) || (pt_mt_desc->meter_type == MT_ICE_p1))
		   ) {
			fprintf(stderr,"%s Error: '-ri' option must be beetween [0,1] for ICE meters.\n", glb_argv[0]);
			print_usage(glb_argv[0]);
			exit(1);
		}
		if (report_instance > 5) {
			fprintf(stderr,"%s Error: '-ri' option must be beetween [0,5].\n", glb_argv[0]);
			print_usage(glb_argv[0]);
			exit(1);
		}

#define PRINT_RPT_HEADER \
if (nrptcfg > 255) { \
fprintf(stdout, "110600%02x00%02x%02x43%02x%02x%02x%02x%04x", \
		(pt_mt_desc->meter_type == MT_ICE ? 0x53 : \
		(pt_mt_desc->meter_type == MT_ICE_p ? 0x53 : \
		(pt_mt_desc->meter_type == MT_ICE_p1 ? 0x53 :  \
		((pt_mt_desc->meter_type >= MT_CT) && (pt_mt_desc->meter_type <= MT_CBETM) ? 0x54 : \
		(pt_mt_desc->meter_type == MT_CJE ? 0x55 : \
		(pt_mt_desc->meter_type == MT_STD ? 0x56 : \
		(((pt_mt_desc->meter_type == MT_PMEPMI) || (pt_mt_desc->meter_type == MT_PMEPMI13)) ? 0x57 : 0xFF))))))), \
		report_instance, \
		(pt_mt_desc->meter_type == MT_ICE_p ? 0x01 : \
		(pt_mt_desc->meter_type == MT_ICE_p1 ? 0x02 : 0x00)), \
		((unsigned short)report_min >> 8) & 0xFF, (unsigned short)report_min & 0xFF, \
		((unsigned short)report_max >> 8) & 0xFF, (unsigned short)report_max & 0xFF, \
		nrptcfg);\
} else { \
fprintf(stdout, "110600%02x00%02x%02x41%02x%02x%02x%02x%02x", \
		(pt_mt_desc->meter_type == MT_ICE ? 0x53 : \
		(pt_mt_desc->meter_type == MT_ICE_p ? 0x53 : \
		(pt_mt_desc->meter_type == MT_ICE_p1 ? 0x53 :  \
		((pt_mt_desc->meter_type >= MT_CT) && (pt_mt_desc->meter_type <= MT_CBETM) ? 0x54 : \
		(pt_mt_desc->meter_type == MT_CJE ? 0x55 : \
		(pt_mt_desc->meter_type == MT_STD ? 0x56 : \
		(((pt_mt_desc->meter_type == MT_PMEPMI) || (pt_mt_desc->meter_type == MT_PMEPMI13)) ? 0x57 : 0xFF))))))), \
		report_instance, \
		(pt_mt_desc->meter_type == MT_ICE_p ? 0x01 : \
		(pt_mt_desc->meter_type == MT_ICE_p1 ? 0x02 : 0x00)), \
		((unsigned short)report_min >> 8) & 0xFF, (unsigned short)report_min & 0xFF, \
		((unsigned short)report_max >> 8) & 0xFF, (unsigned short)report_max & 0xFF, \
		nrptcfg); \
}

		// 11 06 0053 0000 00 41 0002 000A 2B
		// ==> 13 bytes for ZCD report config header

		// First create Report criteria in tmpbuf according to serialized TIC Data
		nrptcfg = tic_serialize_report_criteria(pt_mt_desc,	tmpbufrpt, tmpbuf, buf_size, 0 /* tmpbuf is not unpacked */);
		if (shifted_report)	aSET_DESCPTR_SRPT_OR_LRVREQ(aTB_CRIT_GET_TRIG_DESC(tmpbufrpt),1);

		// UNCOMPRESSED ----------------------------------------------------------
		fprintf(stdout,
			"\nUNCOMPRESSED DESCRIPTORS, Report configuration (%d bytes): \n", nrptcfg + 13);
		fprintf(stdout,"!! USE ONLY ON v3.4 Post 11/2016 TIC PMEPMI Sensors !!\n");
		PRINT_RPT_HEADER;
		for (i=0; i<nrptcfg;i++) fprintf(stdout,"%02x",tmpbufrpt[i]); fprintf(stdout,"\n");

		// ORIGINAL --------------------------------------------------------------
		// use ORIGINAL SIZE in any case
		nrptcfg = cFTicCompressDesc((unsigned char*)aTB_CRIT_GET_FILTER_DESC(tmpbufrpt), tmpbufrpt2, aTIC_DESC_NB_BYTES_ORIGINAL);

		if (shifted_report)	{
			printf("\nORIGINAL DESCRIPTOR CAN'T MANAGE SHIFTED REPORTS !!\n");
		} else {
			if(nrptcfg >= 0){
				nrptcfg = tic_serialize( pt_mt_desc,
					(unsigned char*)aTB_CRIT_GET_TRIG_DESC(tmpbufrpt2), // Jump over the filter descriptor
					(unsigned char*)aTB_CRIT_GET_TRIG_DESC(tmpbufrpt),
					NULL, NULL,
					(buf_size - aGET_DESCPTR_SIZE(aTB_CRIT_GET_FILTER_DESC(tmpbufrpt2))),
					0, /* here source should never be packed (tmpbufrpt) */
					aTIC_DESC_NB_BYTES_ORIGINAL);
				if(nrptcfg > 0){
					nrptcfg += aTIC_DESC_NB_BYTES_ORIGINAL;
					// Set sizes part to 0 in original desscriptor
					aSET_DESCPTR_SIZE(aTB_CRIT_GET_TRIG_DESC(tmpbufrpt2), 0);
					aSET_DESCPTR_SIZE(aTB_CRIT_GET_FILTER_DESC(tmpbufrpt2), 0);
					fprintf(stdout,
						"\nORIGINAL DESCRIPTORS (8 Bytes), Report configuration (%d bytes): \n",nrptcfg + 13);
					PRINT_RPT_HEADER;
					for (i=0; i<nrptcfg;i++) fprintf(stdout,"%02x",tmpbufrpt2[i]); fprintf(stdout,"\n");
				} else printf("\nORIGINAL DESCRIPTOR TOO SMALL FOR REQUIRED CRITERIA !!\n");

			} else printf("\nORIGINAL DESCRIPTOR TOO SMALL FOR REQUIRED FILTER !!\n");
		}

		// COMPRESSED --------------------------------------------------------------
		cFTicCompressDesc((unsigned char*)aTB_CRIT_GET_FILTER_DESC(tmpbufrpt), tmpbufrpt2, 0);
		nrptcfg = tic_serialize( pt_mt_desc,
				(unsigned char*)aTB_CRIT_GET_TRIG_DESC(tmpbufrpt2),
				(unsigned char*)aTB_CRIT_GET_TRIG_DESC(tmpbufrpt),
				NULL,NULL,
				(buf_size - aGET_DESCPTR_SIZE(aTB_CRIT_GET_FILTER_DESC(tmpbufrpt2))),
				0, /* here source should never be packed (tmpbufrpt) */
				0
		);
		nrptcfg += aGET_DESCPTR_SIZE(aTB_CRIT_GET_FILTER_DESC(tmpbufrpt2));

		if (shifted_report)	aSET_DESCPTR_SRPT_OR_LRVREQ(aTB_CRIT_GET_TRIG_DESC(tmpbufrpt2),1);

		fprintf(stdout,
			"\nCOMPRESSED DESCRIPTORS, Report configuration (%d bytes): \n", nrptcfg + 13);
		fprintf(stdout,"!! USE ONLY ON v3.4 Post 11/2016 TIC PMEPMI Sensors !!\n");
		PRINT_RPT_HEADER;
		for (i=0; i<nrptcfg;i++) fprintf(stdout,"%02x",tmpbufrpt2[i]); fprintf(stdout,"\n");

	} // (report_cfg)

	// Reformating test
	if (show_reformated_tic_frame) {
		if (verbose) {
				fprintf(stdout, "Reformated TIC frame : \n");
		}

		tic_formater_init(pt_mt_desc) ;
		tic_formater_frame_put(test_buf, NULL, aTB_GET_DESC(tmpbuf),aTB_GET_BUF(tmpbuf));
		fprintf(stdout,"%s",test_buf);
	} //  (show_reformated_tic_frame)

	// Test TABULAR API //MPO test
	if (test_tabular_api == 1 ) {

#ifdef POINTER
		t_zcl_tic_elem	tbticelem[350];
#endif
		t_zcl_tic_elems tbticelems;
#ifdef POINTER
		tbticelems.el_tab=tbticelem;
		tbticelems.nb_el=sizeof(tbticelem)/sizeof(t_zcl_tic_elem);
#else
		tbticelems.nb_el=sizeof(tbticelems.el_tab)/sizeof(t_zcl_tic_elem);
#endif
		unsigned char	*ticdata	= (unsigned char *)tmpbuf;
		int		szticdata = n;
		TIC_meter_type_t type = pt_mt_desc->meter_type; //TODO
		int		i;

		for	(i = 0 ; i < tbticelems.nb_el ; i++)
			tbticelems.el_tab[i].el_present	= 0;

		int nbelem	= AwZclDecodeTic(NULL,NULL,(unsigned char*)ticdata,szticdata,type,&tbticelems);

		print_tbticelems(&tbticelems);

		unsigned char buf[300];
		int size= AwZclEncodeTic(NULL,buf,sizeof(buf),type/*not used*/,&tbticelems,nbelem);
		fprintf(stdout,"\n MPO\nresult: %d\n",size);
		if(size>0){
			for (i=0; i<size;i++) fprintf(stdout,"%02x",buf[i]); fprintf(stdout,"\n");
			fprintf(stdout,"\n");
		}

		fprintf(stdout, "Descriptor (%d bytes / %d field(s)): ",aGET_DESCPTR_SIZE(tmpbuf),tic_nb_fields_selected((TIC_desc_t *)aTB_GET_DESC(tmpbuf)));
		for (i=0; i<aGET_DESCPTR_SIZE(tmpbuf);i++) fprintf(stdout,"%02x",aTB_GET_DESC(tmpbuf)[i]); fprintf(stdout,"\n");
		for (i=0; i<n;i++) fprintf(stdout,"%02x",tmpbuf[i]); fprintf(stdout,"\n");

		fprintf(stdout,"\n TEST :	%d",!memcmp(buf,tmpbuf,n));

		size= AwZclEncodeTic(NULL,buf,30,type/*not used*/,&tbticelems,nbelem);
		fprintf(stdout,"result: %d\n",size);
		if(size>0){
			for (i=0; i<size;i++) fprintf(stdout,"%02x",buf[i]); fprintf(stdout,"\n");
		}
	}
}

//---------------------------------------------------------------------------
void tic_frame_rx_tic_buf(TIC_parser_status_t * stat) {

	TIC_BUF_TYPE * msg = stat->pt_tic_buf;

	if (msg == NULL) {
		fprintf(stdout,"Error: stat->pt_tic_buf is NULL in tic_frame_rx_tic_buf(). \n");
	} else {

		if (verbose) {
			fprintf(stdout, "Frame received (%d bytes) from '%s%s' meter !\n",
				stat->tic_input_frame_size,
				(stat->tic_meter_type_discovered ? "discovered " : ""),
				TIC_meter_type_str[stat->pt_tic_descriptor->meter_type]);
		}

		// GENERAL TIC FRAME *************************************************
		msg_dump(stat,stat->pt_tic_buf,stat->pt_tic_descriptor);

		// ICE P & P1 TIC FRAMES *********************************************
		if (stat->pt_tic_descriptor->meter_type == MT_ICE) {

			if (verbose) fprintf(stdout, "ICE period P current data:\n");
			msg_dump(stat,stat->ice_p_pt_tic_buf,
				(TIC_meter_descriptor_t *)&(tic_meter_descriptor[MT_ICE_p]));

			if (verbose) fprintf(stdout, "ICE period P1 current data:\n");
			msg_dump(stat,stat->ice_p1_pt_tic_buf,
				(TIC_meter_descriptor_t *)&(tic_meter_descriptor[MT_ICE_p1]));
		}

		// TODO: Real original frame rebuild *********************************

	} // else msg == NULL

	// Frame processed => Allow new frame parsing
	tic_parser_reset();

}

//---------------------------------------------------------------------------
int main(int argc, char * argv[])
{
	int c;
	unsigned char i;
	unsigned char narg = 0;

	// save that for further error msg management
	glb_argv=argv;

	// Default working parameters
	test_tabular_api = verbose = report_cfg = show_reformated_tic_frame = created_filtered_tic_request = shifted_report = report_instance = 0;
	strict = 1; chks_check = 1; nbf_to_valid=6;
	meter_type = MT_CBEMM_ICC;

	// PARSE PARAMS ---------------------------------
	while (argc > 1) {
		argc--; narg++;
		if (strcmp(argv[narg],"-mt") == 0) {
			argc--; narg++;
			if (argc == 0) {
				fprintf(stderr,"%s Error: Option '-mt' needs an argument.\n", argv[0]);
				print_usage(argv[0]);
				return(1);
			} else {
				for (i=0; i<(TIC_NB_MANAGED_METER+1); i++)
					if (strcmp(TIC_meter_type_str[i], argv[narg]) == 0) break;
				if (i == (TIC_NB_MANAGED_METER+1)) {
					fprintf(stderr,"%s Error: '-mt' option argument is not valid.\n", argv[0]);
					print_usage(argv[0]);
					return(1);
				} else {
					meter_type = (TIC_meter_type_t)i;
				}
			}

		} else if  (strcmp(argv[narg],"-v") == 0) {
			verbose=1;

		} else if  (strcmp(argv[narg],"-nc") == 0) {
			chks_check=0;

		} else if  (strcmp(argv[narg],"-ns") == 0) {
			strict=0;

		} else if  (strcmp(argv[narg],"-srtf") == 0) {
			show_reformated_tic_frame=1;

		} else if  (strcmp(argv[narg],"-nfv") == 0) {
			argc--; narg++;
			if (argc == 0) {
				fprintf(stderr,"%s Error: Option '-nfv' needs an argument.\n", argv[0]);
				print_usage(argv[0]);
				return(1);
			} else {
				if (sscanf(argv[narg],"%d",&nbf_to_valid) != 1) {
					fprintf(stderr,"%s Error: '-nfv' option argument is not valid.\n", argv[0]);
					print_usage(argv[0]);
					return(1);
				}
			}

		} else if  (strcmp(argv[narg],"-ri") == 0) {
			argc--; narg++;
			if (argc == 0) {
				fprintf(stderr,"%s Error: Option '-ri' needs an argument.\n", argv[0]);
				print_usage(argv[0]);
				return(1);
			} else {
				if (sscanf(argv[narg],"%d",&report_instance) != 1) {
					fprintf(stderr,"%s Error: '-ri' option argument is not valid.\n", argv[0]);
					print_usage(argv[0]);
					return(1);
				}
			}


		} else if  ((strcmp(argv[narg],"-r") == 0) || (strcmp(argv[narg],"-rs") == 0)) {
			report_cfg=1;
			if (strcmp(argv[narg],"-rs") == 0) shifted_report = 1;
			argc--; narg++;
			if (argc == 0) {
				fprintf(stderr,"%s Error: '-r','-rs' options needs an argument.\n", argv[0]);
				print_usage(argv[0]);
				return(1);
			} else {
				char * ptrNext = argv[narg];
				report_min=strtol(ptrNext,&ptrNext,10);
				if (report_min < 0) {
					fprintf(stderr,"%s Error: '-r','-rs' options min must be > 0.\n", argv[0]); print_usage(argv[0]); return(1);
				}
				if (*ptrNext == 'm') {
					if (report_min > (long)0x7FFF) {
						fprintf(stderr,"%s Error: '-r','-rs' options min must be < 32767m .\n", argv[0]); print_usage(argv[0]); return(1);
					}
					report_min *= 60;
					ptrNext++;
				} else	if ((*ptrNext == 's') || (*ptrNext == '/')) {
					if (report_min/60 > (long)0x7FFF) {
						fprintf(stderr,"%s Error: '-r','-rs' options min must be < 32767m (1966020s).\n", argv[0]); print_usage(argv[0]); return(1);
					}
					if (*ptrNext == 's') ptrNext++;
				}
				if (*ptrNext != '/') {
					fprintf(stderr,"%s Error: '-r','-rs' unexpected char after min ('%c' should be '/') .\n", argv[0],*ptrNext); print_usage(argv[0]); return(1);
				}
				ptrNext++;

				report_max=strtol(ptrNext,&ptrNext,10);
				if (report_max < 0) {
					fprintf(stderr,"%s Error: '-r','-rs' options max must be > 0.\n", argv[0]); print_usage(argv[0]); return(1);
				}
				if (*ptrNext == 'm') {
					if (report_max > (long)0x7FFF) {
						fprintf(stderr,"%s Error: '-r','-rs' options max must be < 32767m .\n", argv[0]); print_usage(argv[0]); return(1);
					}
					report_max *= 60;
					ptrNext++;
				} else	if ((*ptrNext == 's') || (*ptrNext == '/')) {
					if (report_max/60 > (long)0x7FFF) {
						fprintf(stderr,"%s Error: '-r','-rs' options max must be < 32767m (1966020s) .\n", argv[0]); print_usage(argv[0]); return(1);
					}
					if (*ptrNext == 's') ptrNext++;
				}
				if (*ptrNext != '\0') {
					fprintf(stderr,"%s Error: '-r','-rs' unexpected char after max ('%c' should be end of parameter) .\n", argv[0],*ptrNext); print_usage(argv[0]); return(1);
				}

				// Finally set the correct binary value for report min/max in seconds
				if (report_min > (long)0x7FFF) {report_min = (report_min/60); report_min |= (long)0x8000; };
				if (report_max > (long)0x7FFF) {report_max = (report_max/60); report_max |= (long)0x8000; };

				if (report_min > report_max) {
					fprintf(stderr,"%s Error: options max must be greater or equal to min.\n", argv[0]); print_usage(argv[0]); return(1);
				}

			}

		} else if  (strcmp(argv[narg],"-fr") == 0) {
			created_filtered_tic_request=1;

		} else if  (strcmp(argv[narg],"-tapi") == 0) {
			test_tabular_api=1;

		} else if  (strcmp(argv[narg],"-h") == 0) {
			print_usage(argv[0]);
			return(0);

		} else {
			fprintf(stderr,"%s Error: Unexpected argument.\n", argv[0]);
			print_usage(argv[0]);
			return(1);

		}
	}

	fprintf(stderr, "** tictobin started **\n");
	fprintf(stderr, "** Please enter ASCII string (TIC meter data flow) \n");

	// DO THE JOB ---------------------------------
	tic_parser_init(tic_metertype_to_meterdesc(meter_type),chks_check,strict, nbf_to_valid);
	tic_parser_set_group_found(1);
	tic_parser_set_frame_rx_handler(tic_frame_rx_tic_buf);
	tic_parser_reset();

	// Permanently parse stdin
	while ((c = getchar()) != EOF) {
		tic_parser_input_char((char)c);
	}

	return(0);
}

