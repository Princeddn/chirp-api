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
 * 		TIC parser
 * \author
 *      P.E. Goudet <pe.goudet@watteco.com>
 */

/*============================ INCLUDE =======================================*/

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <ctype.h>

#include <time.h>

#include "tic-parser.h"

// PEG: if defined it stores PEG_DEBUG_SIZE last bytes received before tic_parser_reset
//#define PEG_DEBUG_INPUT 1
#ifdef PEG_DEBUG_INPUT
#define PEG_DEBUG_SIZE 240
static char test_buf[PEG_DEBUG_SIZE];
static i_test_buf=0;
#define PEG_DEBUG_INPUT_STORE {test_buf[i_test_buf]=c; i_test_buf=(i_test_buf+1)%PEG_DEBUG_SIZE;}
#define PEG_DEBUG_INPUT_RESET {for (i_test_buf = 0; i_test_buf < PEG_DEBUG_SIZE; i_test_buf++) test_buf[i_test_buf]=0xFF; i_test_buf=0;}
#else
#define PEG_DEBUG_INPUT_STORE
#define PEG_DEBUG_INPUT_RESET
#endif

#define HEX2BYTE(c) ((c>='0' && c<='9') ? c - '0' : 10 + ((c>='a' && c<='f') ? c - 'a' : c -'A'))
#define DEC2BYTE(c) ( c - '0' )

// Global variable used for parsing and temporary storage
// Currently these varables ar not stored in parser status to avoid to muche RAM memory usage
// when making multiple descriptors parsing during Meter type recognition process ...
static unsigned char istr;			  // Current string position
static unsigned char checksum,checksumprec,checksumprecprec;       // Current checksum calculation
static char field_label[STR_LABEL_SZ_MAX]; // Current input field_label string
static char field_value[STR_VALUE_SZ_MAX]; // Current input field_value string

// Thes Globals variables have only a local scope usage inside functions
// process_record_desc_only() or process_record_tic_buf()
static const TIC_expected_field_t * pt_expfields, * ice_p_pt_expfields, * ice_p1_pt_expfields;
static unsigned char nb_expfields,ice_p_nb_expfields,ice_p1_nb_expfields;
static unsigned char nf, ice_p_nf, ice_p1_nf;
static unsigned char max, process_it;
static unsigned char *ptr, *ptr2, tmp_uchar;
static unsigned char *	pt_tic_buf_buf;

// Expect following delim of record as first encountered in record
static unsigned char first_delim = '\0';

void (*tic_parser_frame_rx_handler)(TIC_parser_status_t * stat) = NULL;

//========================================================================
// Internal effective data buffer and status struct
static TIC_parser_status_t parser_status;
//========================================================================

//----------------------------------------------------------------------------
TIC_meter_type_t tic_parser_get_meter_type() {
	return(parser_status.pt_tic_descriptor->meter_type);
}
unsigned char tic_parser_get_group_found() {
	return(parser_status.one_group_found);
}
void tic_parser_set_group_found(unsigned char group_found_value) {
	parser_status.one_group_found = group_found_value;
}

//----------------------------------------------------------------------------
void tic_parser_set_frame_rx_handler(void (*f)(TIC_parser_status_t * stat)) {
	tic_parser_frame_rx_handler = f;
}

//----------------------------------------------------------------------------
void tic_parser_init(
	TIC_meter_descriptor_t * tic_desc,
	unsigned char chks_check,
	unsigned char strict,
	unsigned char nbfv) {
	// NOTICE: After init, reset is mandatory to start the parser !!!
//printf("TIC Parser INIT\n");
	// Init the buffers ptr initial positions : pt_tic_buf_space can be use as
	// single buffer with "pt_tic_buf" or triple buffer with "pt_tic_buf", "ice_p_pt_tic_buf" and "ice_p1_pt_tic_buf"
	parser_status.pt_tic_buf = parser_status.pt_tic_buf_space;
	parser_status.ice_p_pt_tic_buf = &(parser_status.pt_tic_buf_space[TIC_PACKED_BUF_SZ]);
	parser_status.ice_p1_pt_tic_buf = &(parser_status.ice_p_pt_tic_buf[TIC_UNPACKED_BUF_SZ]);

	// TODO: Find a good way to avoid Race condition when acting on parser status varables
	// Minimal try using an unsused state STOPPED
 	parser_status.parser_state=STOPPED;

	// Init parser parameters
	parser_status.pt_tic_descriptor = tic_desc;  //tic_get_current_meter_descriptor();
	parser_status.chksum_check = chks_check;
	parser_status.strict = strict;
	parser_status.nb_field_to_valid_frame = nbfv;

	// NOTICE: After init, reset is mandatory to start the parser !!!

	// Reset ICE p an p-1 desc sub parser only on init AND on contractual period change not to loose current informations
	// And set the unpacked bit of the descriptor

		// Note ICE P and P1 buffers : Set as an Unpacked buffer and uses only 8 byte descriptor
	vFTicBufInitFromHeaderValues(parser_status.ice_p_pt_tic_buf, 0, 0, aDESC_TYPE_VAR_BITS_FIELD, aTIC_DESC_NB_BYTES_ORIGINAL);
	vFTicBufInitFromHeaderValues(parser_status.ice_p1_pt_tic_buf, 0, 0, aDESC_TYPE_VAR_BITS_FIELD, aTIC_DESC_NB_BYTES_ORIGINAL);

}


//----------------------------------------------------------------------------
unsigned char tucTICErrLogBuf[TIC_ERR_BUF_SIZE];
unsigned short usTICErrLogBufCurrentSize = 0;
unsigned char err_log_clear_required = 1; // this message is processed only during tic_parser_reset if required
//----------------------------------------------------------------------------
/*
 *  /brief
 *  	Manage Error log for remote debugging ..
 *
 *  	04/2018: ADD REMOTE DEBUG CAPABILITY
 *  	Manage a specific buffer of errors firing reset for on site debug purpose
 *  	The Buffer will embeded the first encountered errors unitil full the stop recording
 *  	for eventual distant acces through specific ZCL command.
 *  	An other ZCL specific command must be used to clear this buffer
 *  	Format of buffer:
 *  	[0xAA<ErrCode><lastNFOK><StrSize><field_label + field_value [+ checksum]>0xBB]*
 *  	Notes:
 *  	- 0xAA et 0xBB en en-tête et terminateur car ce sont 2 caractères qui ont trés peu de chance de se retrouver dans le flux ?
*/
void vF_tic_parser_err_log(TICErrLogCodes_t ucErrCode)
{

	// First log eventual current data
	if (ucErrCode != TIC_ERR_NO_ERR)
	{
		if (usTICErrLogBufCurrentSize >= TIC_ERR_BUF_SIZE) return ;
		tucTICErrLogBuf[usTICErrLogBufCurrentSize]=0xAA; usTICErrLogBufCurrentSize++;

		if (usTICErrLogBufCurrentSize >= TIC_ERR_BUF_SIZE) return ;
		tucTICErrLogBuf[usTICErrLogBufCurrentSize]=ucErrCode; usTICErrLogBufCurrentSize++;

		if (usTICErrLogBufCurrentSize >= TIC_ERR_BUF_SIZE) return ;
		tucTICErrLogBuf[usTICErrLogBufCurrentSize]=parser_status.no_field; usTICErrLogBufCurrentSize++;

		if (usTICErrLogBufCurrentSize >= TIC_ERR_BUF_SIZE) return ;

		unsigned char posLen = usTICErrLogBufCurrentSize;
		usTICErrLogBufCurrentSize++;

		if (usTICErrLogBufCurrentSize >= TIC_ERR_BUF_SIZE) return ;
		unsigned char remain;
		unsigned char len;

		if (usTICErrLogBufCurrentSize >= TIC_ERR_BUF_SIZE) return ;
		remain = TIC_ERR_BUF_SIZE - usTICErrLogBufCurrentSize;
		len = strlen(field_label);
		len = (remain > len ? len : remain);
		strncpy((char*)&(tucTICErrLogBuf[usTICErrLogBufCurrentSize]), field_label, len);
		usTICErrLogBufCurrentSize += len;
		tucTICErrLogBuf[usTICErrLogBufCurrentSize] = first_delim; usTICErrLogBufCurrentSize++;
		tucTICErrLogBuf[posLen]=len;

		if (usTICErrLogBufCurrentSize >= TIC_ERR_BUF_SIZE) return ;
		remain = TIC_ERR_BUF_SIZE - usTICErrLogBufCurrentSize;
		len = strlen(field_value);
		len = (remain > len ? len : remain);
		strncpy((char *)&(tucTICErrLogBuf[usTICErrLogBufCurrentSize]), field_value,len);
		usTICErrLogBufCurrentSize += len;
		tucTICErrLogBuf[usTICErrLogBufCurrentSize] = first_delim; usTICErrLogBufCurrentSize++;
		tucTICErrLogBuf[posLen]+=len;

		if (ucErrCode == TIC_ERR_BAD_CHECKSUM) {
			if (usTICErrLogBufCurrentSize >= TIC_ERR_BUF_SIZE) return ;
			tucTICErrLogBuf[usTICErrLogBufCurrentSize]=checksum; usTICErrLogBufCurrentSize++;
		}

		if (usTICErrLogBufCurrentSize >= TIC_ERR_BUF_SIZE) return ;
		tucTICErrLogBuf[usTICErrLogBufCurrentSize]=0xBB; usTICErrLogBufCurrentSize++;
	}
}

/*
 *  /brief
 *  	Read part of the Err log buffer
 *  	BEWARE: pucDest MUST point on large enough space
 *
 */
unsigned short usF_tic_parser_err_log_cp_len_from(unsigned char * pucDest, unsigned short usLen, unsigned short usFrom )
{
	if (usFrom >= usTICErrLogBufCurrentSize)
	{
		pucDest[0]=0x00;
		usLen=1;
	}
	else
	{
		unsigned short usRemain = usTICErrLogBufCurrentSize - usFrom;
		if (usLen > usRemain) usLen = usRemain;
		memcpy(pucDest, &(tucTICErrLogBuf[usFrom]), usLen);
	}

	return usLen;
}

/*
 *  /brief
 *  	Clear current parser and reset process
 *
 */
void vF_tic_parser_err_log_clear()
{
	if (err_log_clear_required != 1) {
		err_log_clear_required = 1;
	}
}



void tic_parser_reset() {
	// TODO: Find a good way to avoid Race condition when acting on parser status variables
	// Minimal try using an unsused state STOPPED
//printf("TIC Parser RESET\n");
 	parser_status.parser_state=STOPPED;

	// Reset parser and init descriptor space for parser (packed buffer, VAR_BITFIELDS, MAX DESC size)
	vFTicBufInitFromHeaderValues(parser_status.pt_tic_buf, 0, 0, aDESC_TYPE_VAR_BITS_FIELD, aTIC_DESC_MAX_NB_BYTES);

	parser_status.pt_tic_buf_buf = aTB_GET_BUF(parser_status.pt_tic_buf);
	parser_status.no_field = 0;

	// Reset ICE p sub parser
	parser_status.ice_p_pt_tic_buf_buf = aTB_GET_BUF(parser_status.ice_p_pt_tic_buf);
	parser_status.ice_p_no_field = 0;
	parser_status.ice_p_block_initialised = 0;

	// Reset ICE p1 sub parser
	parser_status.ice_p1_pt_tic_buf_buf = aTB_GET_BUF(parser_status.ice_p1_pt_tic_buf);
	parser_status.ice_p1_no_field = 0;
	parser_status.ice_p1_block_initialised = 0;

	parser_status.tic_input_frame_size = 0;
	parser_status.tic_meter_type_discovered = 0;

	// Re-init record parsing
	istr = 0; checksum = 0; checksumprec = 0; checksumprecprec = 0;

	// Re-init meter discovering if needed
	if ((parser_status.pt_tic_descriptor == NULL) || (parser_status.pt_tic_descriptor->meter_type == MT_NULL)) {
		pt_expfields = NULL; nb_expfields = 0;
		ice_p_pt_expfields = NULL; ice_p_nb_expfields = 0;
		ice_p1_pt_expfields = NULL; ice_p1_nb_expfields = 0;
	}

 	first_delim = '\0';

	PEG_DEBUG_INPUT_RESET;

	parser_status.parser_state=PEND_STX;

}

//----------------------------------------------------------------------------
unsigned char process_record_tic_buf(
	unsigned char rec_num,
	unsigned char **hndl_tic_buf_buf,
	const TIC_expected_field_t * expected_fields,
	unsigned char * tic_buf_desc_u8,
	unsigned char * pt_tic_buf_buf_origin ) {

	unsigned char offset = 0;
	char *endptr;
	char* debstr;

	unsigned long tmp_long;
	float tmp_float;
	unsigned short tmp_u16;
	signed short tmp_i16;


	// Decode and Store validated field in the field_buf buffer

	// hndl ptr access optimisation	and manage the absolute access case if pt_tic_buf_buf_origin != NULL
	pt_tic_buf_buf = (pt_tic_buf_buf_origin == NULL ?
		*hndl_tic_buf_buf :
		pt_tic_buf_buf_origin + expected_fields[rec_num].abs_pos);

// printf("process_record_tic_buf: %d : %s, type: %d\n",rec_num ,expected_fields[rec_num].label,expected_fields[rec_num].type);
	switch (expected_fields[rec_num].type) {

		case (TYPE_CSTRING):
			if (expected_fields[rec_num].attribute & ATTRIBUTE_MULTI_OCCURENCE_FIELD) {// Multiple field enconded for same
				if (ucFTicFieldGetBit(tic_buf_desc_u8,rec_num)) { // if set we already have a PREAVIS value set, this is an other one
					// Set a ',' instead of previous '\0'
					*(pt_tic_buf_buf-1)=',';
				}
			}
			strcpy((char *)pt_tic_buf_buf,field_value);
			pt_tic_buf_buf += strlen(field_value)+1; vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
		break;

		case (TYPE_CHAR):
			*(pt_tic_buf_buf) = *field_value; pt_tic_buf_buf++; vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
		break;

		case (TYPE_SDMYhmsU8):
			// "SYYMMDDHHMMSS<DELIM_STD>xx"
			*(pt_tic_buf_buf) = *field_value; pt_tic_buf_buf++;
			ptr = (unsigned char *)(field_value+1); max = 6;
			while (max > 0) {
				*(pt_tic_buf_buf) = (DEC2BYTE(*ptr) * 10); ptr++;
				*(pt_tic_buf_buf) += DEC2BYTE(*ptr);
				pt_tic_buf_buf += 1; ptr++; max--;
			}
			offset = 13;
		case (TYPE_BF8d):
		case (TYPE_U8):
			// TODO: Verify that scanf is not to power/time consumming
			// if yes, change this only case with a specificty on "PPOT" field_label.
			// if not sscanf could be genralized ==> easying format reading
			// (usage try here only because "PPOT" field is hexadecimal.)
			// !!!! Warning direct scanf on the pointer is wrong because of word alignment of scanf on MSP430/CCSV4
			// sscanf((field_value+offset),expected_fields[rec_num].fmt,&tmp_uchar);

			// PEG 20141002: Using it with TIC + 2S0 => Too much consumming
			// NOTA: sscanf uses AT LEAST 387 bytes in the stack
			// 	=> To dangerous and buggy without freeing more memory
			// So must process the following exception compared to default decimal conversion
			// FMT_02X[]   = "%02X";
			tmp_uchar = (unsigned char)
				strtol ((field_value+offset), &endptr ,
						( expected_fields[rec_num].fmt == FMT_02X ? 16 : 10));
			*pt_tic_buf_buf = tmp_uchar;
			pt_tic_buf_buf++; vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
		break;

		case (TYPE_11hhmmSSSS): {
			unsigned char i;
			ptr = (unsigned char *)(field_value);
			for (i=0;i<11;i++) {
				if (*ptr == 'N') {
					*(pt_tic_buf_buf) = (unsigned char)0xFF;
					pt_tic_buf_buf+=1;
					ptr+=8; // 8 octets de NONUTILE
				} else  {
					max = 2; // hh mm
					while (max > 0) {
						*(pt_tic_buf_buf) = (DEC2BYTE(*ptr) * 10); ptr++;
						*(pt_tic_buf_buf) += DEC2BYTE(*ptr); ptr++;
						pt_tic_buf_buf++; max--;
					}

					// "xxXX", 16 bit BitField in hexa Big endian
					max = 2;
					while (max > 0) {
						*(pt_tic_buf_buf) = (HEX2BYTE(*ptr) << 4); ptr++;
						*(pt_tic_buf_buf) += HEX2BYTE(*ptr); ptr++;
						pt_tic_buf_buf+=1; max--;
					}
				}
				if (i < 10) ptr++; // <Space>
			}
			vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
		}
		break;

		case (TYPE_SDMYhmsU16):
			// "SYYMMDDHHMMSS<DELIM_STD>xx"
			*(pt_tic_buf_buf) = *field_value; pt_tic_buf_buf++;
			ptr = (unsigned char *)(field_value+1); max = 6;
			while (max > 0) {
				*(pt_tic_buf_buf) = (DEC2BYTE(*ptr) * 10); ptr++;
				*(pt_tic_buf_buf) += DEC2BYTE(*ptr);
				pt_tic_buf_buf += 1; ptr++; max--;
			}
			offset = 13;
		case (TYPE_U16):
			tmp_u16 = (unsigned short) atoi(field_value + offset);
			U16_TO_U16p(tmp_u16,pt_tic_buf_buf); pt_tic_buf_buf += 2;
			vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
		break;

		case (TYPE_I16):
			tmp_i16 = (signed short) atoi(field_value);
			I16_TO_I16p(tmp_i16,pt_tic_buf_buf); pt_tic_buf_buf += 2;
			vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
		break;

		case (TYPE_U24CSTRING):
			//U24
			tmp_long = (unsigned long)strtol(field_value + offset,&debstr,10);
			U32_TO_U24p(tmp_long,pt_tic_buf_buf);
			pt_tic_buf_buf += 3;
			//CString
			strcpy((char *)pt_tic_buf_buf,debstr);
			pt_tic_buf_buf += strlen(debstr)+1;
			vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
		break;

		case (TYPE_SDMYhmsU24):
			// "SYYMMDDHHMMSS<DELIM_STD>xx"
			*(pt_tic_buf_buf) = *field_value; pt_tic_buf_buf++;
			ptr = (unsigned char *)(field_value+1); max = 6;
			while (max > 0) {
				*(pt_tic_buf_buf) = (DEC2BYTE(*ptr) * 10); ptr++;
				*(pt_tic_buf_buf) += DEC2BYTE(*ptr);
				pt_tic_buf_buf += 1; ptr++; max--;
			}
			offset = 13;
		case (TYPE_U24):
			tmp_long = (unsigned long)strtol(field_value + offset,NULL,10);
			U32_TO_U24p(tmp_long,pt_tic_buf_buf); pt_tic_buf_buf += 3; vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
		break;

		case (TYPE_6U24): // CJE counter cases: needing "sub-parsing" : 111111:222222:...:666666 or 11111:22222:...:44444
		case (TYPE_4U24): // Can have up to 4 or 6 ':' separated u24, to store in successive fields
			ptr = (unsigned char *)field_value;
			max = (expected_fields[rec_num].type == TYPE_6U24 ? 6 : 4);
			while ((*ptr != DELIM) && (*ptr != '\0') && (max > 0)) {
				ptr2 = ptr;
				// Find End of sub-field field_value
				while ((*ptr2 != DELIM) && (*ptr2 != ':') && (*ptr2 != '\0')) {ptr2++;};
			// printf("\nFound: %s\n", ptr);

				tmp_long = (unsigned long)strtol((const char *)ptr,NULL,10);
				U32_TO_U24p(tmp_long,pt_tic_buf_buf); pt_tic_buf_buf += 3;  vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
			// printf("Long = %ld %08lx %02x%02x%02x\n",tmp_long, tmp_long,*(pt_tic_buf_buf - 3),*(pt_tic_buf_buf - 2),*(pt_tic_buf_buf - 1));

				if (*ptr2 == ':') {
					ptr = ptr2 + 1; // Step to the possible start of next field
			// printf("\nNext: %s\n", ptr);
				} else {
					ptr = ptr2;
				}

				max--; // Decrease the expected number of sub-fields
				rec_num++;   // Increment the rec_num idx to immediatly jump over repeted expected fields
			}
		break;

		case (TYPE_U32):
			tmp_long = (unsigned long)strtol(field_value,NULL,10);
			U32_TO_U32p(tmp_long,pt_tic_buf_buf); pt_tic_buf_buf += 4;
			vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
		break;

		case (TYPE_FLOAT):
			if ((ptr2 = (unsigned char *)strchr(field_value,',')) != NULL) *ptr2 = '.'; // Float decimal is dot not coma for strtod (MSP430)
			tmp_float = (float)strtod(field_value,NULL); // Beware, we assume strtod accept '.' and not ',' (beware of that on specific computer configuration)
			FLT_TO_FLTp(tmp_float,pt_tic_buf_buf);
			pt_tic_buf_buf += 4;
			vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
		break;

		case (TYPE_BF32xbe):
			// "xxXXxxXX", 32 bit BitField in hexa Big endian
			ptr = (unsigned char *)(field_value); max = 4;
			while (max > 0) {
				*(pt_tic_buf_buf) = (HEX2BYTE(*ptr) << 4); ptr++;
				*(pt_tic_buf_buf) += HEX2BYTE(*ptr); ptr++;
				pt_tic_buf_buf++; max--;
			}
			vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
		break;

		case (TYPE_HEXSTRING):
			ptr = (unsigned char *)(field_value);
			max = strlen(field_value)/2;
			*(pt_tic_buf_buf) = max; pt_tic_buf_buf++;
			while (max > 0) {
				*(pt_tic_buf_buf) = (HEX2BYTE(*ptr) << 4); ptr++;
				*(pt_tic_buf_buf) += HEX2BYTE(*ptr); ptr++;
				pt_tic_buf_buf++; max--;
			}
			vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
		break;

		case (TYPE_SDMYhms):
			// "SYYMMDDHHMMSS"
			*(pt_tic_buf_buf) = *field_value; pt_tic_buf_buf++;
			ptr = (unsigned char *)(field_value+1); max = 6;
			while (max > 0) {
				*(pt_tic_buf_buf) = (DEC2BYTE(*ptr) * 10); ptr++;
				*(pt_tic_buf_buf) += DEC2BYTE(*ptr);
				pt_tic_buf_buf += 1; ptr++; max--;
			}
			vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
		break;

		case (TYPE_DMYhms):
			// "JJ/MM/AA HH/MM/SS"
			ptr = (unsigned char *)field_value; max = 6;
			while (max > 0) {
				*(pt_tic_buf_buf) = (char) atoi((const char *)ptr);
				pt_tic_buf_buf += 1; ptr += 3; max--;
			}
			vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
		break;

		case (TYPE_tsDMYhms): {
			// NEW encoding using Timestamp and periode tarifaire compression

			// "JJ/MM/AA HH/MM/SS"
			// Notice pt_tic_buf_buf temporary used to store DMYHMS bytes for next tic_get_timestamp_from_DMY_HMS_bytes() call
			ptr = (unsigned char *)field_value; max = 6;
			while (max > 0) {
				*(pt_tic_buf_buf) = (char) atoi((const char *)ptr);
				pt_tic_buf_buf += 1; ptr += 3; max--;
			}

			pt_tic_buf_buf -= 6; // Back to position to read DMYHMS and set timestamp
			tmp_long = (unsigned long)tic_get_timestamp_from_DMY_HMS_bytes(pt_tic_buf_buf);
			U32_TO_U32p(tmp_long, pt_tic_buf_buf);
			pt_tic_buf_buf += 4;
			vFTicFieldSetBit(tic_buf_desc_u8,rec_num);

		} break;

		case (TYPE_DMYhmsCSTRING):
			// "JJ/MM/AA HH/MM/SS-aaa"
			ptr = (unsigned char *)field_value; max = 6;
			while (max > 0) {
				*(pt_tic_buf_buf) = (char) atoi((const char *)ptr);
				pt_tic_buf_buf += 1; ptr += 3; max--;
			}
			//CString

			strcpy((char *)pt_tic_buf_buf,(char *)ptr);
			pt_tic_buf_buf += strlen((char *)ptr)+1;
			vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
		break;

		case (TYPE_E_PT):
        case (TYPE_E_DIV):
        case (TYPE_E_CONTRAT):
        case (TYPE_E_STD_PT):
        case (TYPE_E_STD_CONTRAT):
			// NOTA: jump over first chars if some are defined in format before real data
			// (here it can be "TD-")
			// Except string size is smaller (allows TD-* or * when used for criteria definition)
			ptr = (unsigned char *)strchr((char *)expected_fields[rec_num].fmt,'%');
			if (ptr != NULL) {
				if ((ptr - (unsigned char *)expected_fields[rec_num].fmt) <= strlen(field_value)) {
					ptr = (unsigned char *)field_value + (ptr - (unsigned char *)expected_fields[rec_num].fmt);
				} else ptr = (unsigned char *)field_value;
			} else ptr = (unsigned char *)field_value;
			pt_tic_buf_buf += (unsigned char) tic_enum_compress(expected_fields[rec_num].type, ptr, pt_tic_buf_buf);
			vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
		break;

        case (TYPE_U24_E_DIV):			//U24
			tmp_long = (unsigned long)strtol(field_value,&debstr,10);
			U32_TO_U24p(tmp_long,pt_tic_buf_buf);
			pt_tic_buf_buf += 3;
			// DIV
			pt_tic_buf_buf += (unsigned char) tic_enum_compress(TYPE_U24_E_DIV, (unsigned char *)debstr, pt_tic_buf_buf);
			vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
        break;

		case (TYPE_tsDMYhms_E_PT): {
			// NEW encoding using Timestamp and periode tarifaire compression

			// "JJ/MM/AA HH/MM/SS-aaa"
			// Notice pt_tic_buf_buf temporary used to store DMYHMS bytes for next tic_get_timestamp_from_DMY_HMS_bytes() call
			ptr = (unsigned char *)field_value; max = 6;
			while (max > 0) {
				*(pt_tic_buf_buf) = (char) atoi((const char *)ptr);
				pt_tic_buf_buf += 1; ptr += 3; max--;
			}

			pt_tic_buf_buf -= 6; // Back to position to read DMYHMS and set timestamp
			tmp_long = (unsigned long)tic_get_timestamp_from_DMY_HMS_bytes(pt_tic_buf_buf);
			U32_TO_U32p(tmp_long, pt_tic_buf_buf);
			pt_tic_buf_buf += 4;
			pt_tic_buf_buf += (unsigned char) tic_enum_compress(TYPE_E_PT, ptr, pt_tic_buf_buf);
			vFTicFieldSetBit(tic_buf_desc_u8,rec_num);

		} break;

		case (TYPE_hmDM):  // CJE counter cases: needing "sub-parsing": {hh:mn:jj:mm}:pt:dp:abcde:kp
			ptr = (unsigned char *)field_value;
			max = 8; // 8 sub fields to decode
			while (/*(*ptr != DELIM) && */(*ptr != '\0') && (max > 0)) {
				ptr2 = ptr;
				// Find End of sub-field field_value
				while (/*(*ptr2 != DELIM) && */(*ptr2 != ':') && (*ptr2 != '\0')) {ptr2++;};
				if (* ptr2 == ':') *ptr2 = '\0';
				// Conditional processing of sub parsed fields
				if (max > 4) { // processing hh:mn:jj:mm
					*pt_tic_buf_buf	= (char) atoi((const char *)ptr); pt_tic_buf_buf++; vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
				} else { // <=4: Use the possible format definition
					rec_num++;   // Increment the rec_num idx to immediatly jump over repeted expected fields
					switch (expected_fields[rec_num].type) {

						case (TYPE_CSTRING):
							strcpy((char *)pt_tic_buf_buf,(const char *)ptr); pt_tic_buf_buf += strlen((const char *)ptr)+1; vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
						break;

						case (TYPE_U24):
							tmp_long = (unsigned long)strtol((const char *)ptr,NULL,10);
							U32_TO_U24p(tmp_long,pt_tic_buf_buf); pt_tic_buf_buf += 3; vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
						break;

						case (TYPE_U8):
							*pt_tic_buf_buf = (char) atoi((const char *)ptr); pt_tic_buf_buf++; vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
						break;

						default:
						break;
					}
				}

				ptr = (ptr2 + 1); // Step to the possible start of next field
				max--; // Decrease the expected number of sub-fields
			}
		break;

		case (TYPE_DMh):  // CJE counter cases: needing "sub-parsing":  {jj:mm:hh}:cg
			ptr = (unsigned char *)field_value;
			max = 4; // 4 sub fields to decode
			while ((*ptr != DELIM) && (*ptr != '\0') && (max > 0)) {
				ptr2 = ptr;
				// Find End of sub-field field_value
				while ((*ptr2 != DELIM) && (*ptr2 != ':') && (*ptr2 != '\0')) {ptr2++;};
				if (* ptr2 == ':') *ptr2 = '\0';

				// Conditional processing of sub parsed fields
				if (max > 1) { // processing jj:mm:hh
					*pt_tic_buf_buf	= (char) atoi((const char *)ptr); pt_tic_buf_buf++; vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
				} else { // <=1: Use the possible format definition
					rec_num++;   // Increment the rec_num idx to immediatly jump over repeted expected fields
					switch (expected_fields[rec_num].type) {

						case (TYPE_U8):
							*pt_tic_buf_buf = (char) atoi((const char *)ptr); pt_tic_buf_buf++; vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
						break;

						default:
						break;
					}
				}
				ptr = (ptr2 + 1); // Step to the possible start of next field
				max--; // Decrease the expected number of sub-fields
			}
		break;

		case (TYPE_hm):  // CJE counter cases: needing "sub-parsing":  {hh:mn}:dd
			ptr = (unsigned char *)field_value;
			max = 3; // 3 sub fields to decode
			while ((*ptr != DELIM) && (*ptr != '\0') && (max > 0)) {
				ptr2 = ptr;
				// Find End of sub-field field_value
				while ((*ptr2 != DELIM) && (*ptr2 != ':') && (*ptr2 != '\0')) {ptr2++;};
				if (* ptr2 == ':') *ptr2 = '\0';

				// Conditional processing of sub parsed fields
				if (max > 1) { // processing jj:mm:hh
					*pt_tic_buf_buf	= (char) atoi((const char *)ptr); pt_tic_buf_buf++; vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
				} else { // <=1: Use the possible format definition
					rec_num++;   // Increment the rec_num idx to immediatly jump over repeted expected fields
					switch (expected_fields[rec_num].type) {

						case (TYPE_U8):
							*pt_tic_buf_buf = (char) atoi((const char *)ptr); pt_tic_buf_buf++; vFTicFieldSetBit(tic_buf_desc_u8,rec_num);
						break;

						default:
						break;
					}
				}
				ptr = (ptr2 + 1); // Step to the possible start of next field
				max--; // Decrease the expected number of sub-fields
			}
		break;

		default:
			// This case should never occur
		break;
	};

	// hndl ptr access optimisation
	*hndl_tic_buf_buf = pt_tic_buf_buf;

	return(rec_num);
}
//----------------------------------------------------------------------------
/*
char tmp_buf[256];
int tic_parser_input_char_TEST(unsigned char c) {
	// TODO: This interrupt funcion may become too long !!!!!!!

//parser_status.pt_tic_buf_buf[parser_status.tic_input_frame_size%TIC_FIELDS_MAX_SIZE_BUF] = c;
	tmp_buf[parser_status.tic_input_frame_size%255]=c;

	parser_status.tic_input_frame_size++; // evaluate original TIC frame size

	// Return code 0 anycase for now ...
	return(0);
}
*/
//----------------------------------------------------------------------------
// Add DATECOUR or DATE to the block buffer (last modification)
unsigned char ice_pp1_init_block(TIC_BUF_TYPE * pt_tic_buf,
	unsigned char ice_pp1_nf,
	unsigned char ice_pp1_block_initialised,
	unsigned char * tic_buf_desc_u8,
	unsigned char * tic_buf_buf) {

	unsigned char clear_bits_until;

	if ((ice_pp1_nf >3) && (ice_pp1_nf <18)) { // This field belongs to EAp[1] bloc
		if (ice_pp1_block_initialised == 3) return ice_pp1_block_initialised; // This block is already initialised
		ice_pp1_block_initialised = 3;
		tic_buf_buf += 14;
		clear_bits_until = 18;

	} else if ((ice_pp1_nf >18) && (ice_pp1_nf <33)) { // This field belongs to ERPp[1] bloc
		if (ice_pp1_block_initialised == 18) return ice_pp1_block_initialised;  // This block is already initialised
		ice_pp1_block_initialised = 18;
		tic_buf_buf += 62;
		clear_bits_until = 33;

	} else if ((ice_pp1_nf >33) && (ice_pp1_nf <48)) { // This field belongs to ERNp[1] bloc
		if (ice_pp1_block_initialised == 33) return ice_pp1_block_initialised; // This block is already initialised
		ice_pp1_block_initialised = 33;
		tic_buf_buf += 110;
		clear_bits_until = 48;

	} else {
		return(0); // Anormal case
	}

	if ((ptr = tic_get_value_at_index(tic_metertype_to_meterdesc(MT_ICE), pt_tic_buf, 1, 0)) == NULL) // Try with DATECOUR
		if ((ptr = tic_get_value_at_index(tic_metertype_to_meterdesc(MT_ICE), pt_tic_buf, 2, 0)) == NULL) // Try with DATE (v2.4)
			return(0);

	// Intialise buf at position
	//memset(tic_buf_buf,0x00,38);

	// TODO: Ci-dessous devrait être le bon code !!!
	// Intialise buf at position
	memset(tic_buf_buf,0x00,48);
	// Clear the corresponding bits
	while (ice_pp1_nf < clear_bits_until) {
		vFTicFieldClrBit(tic_buf_desc_u8,ice_pp1_nf);
		ice_pp1_nf++;
	}


	// Set block date
	memcpy(tic_buf_buf,ptr,6);
	// Set the bit for the correcponding date
	vFTicFieldSetBit(tic_buf_desc_u8,ice_pp1_block_initialised);

	return(ice_pp1_block_initialised);
}

//---------------------------------------------------------------------------------------------------
// Since PMEPMI (many baud rates) start waiting for a valid GROUP before waiting for a full TIC FRAME
// this function is a minimal state machine to verify that at least one EDF GROUP of information is OK (bytes content and CRC)
// Should return 1 if a frame must be processed
int tic_parser_find_group(unsigned char c) {

	static unsigned char last_char;

	PEG_DEBUG_INPUT_STORE

	// Important because only parser_reset used outside setting then start waiting LF and not STX on Group wait
	if (parser_status.parser_state == PEND_STX) parser_status.parser_state = PEND_LF;

	// Character processing according to state
	switch (parser_status.parser_state) {
		case (PEND_LF):
			if (c == LF) {
				parser_status.parser_state = PEND_CR;
				checksumprecprec = checksumprec = checksum = 0;
				last_char ='\0';
			}
		break;

		case (PEND_CR):
			if (c == CR) { // End of GROUP estimate and verify checksum

				#ifdef TIC_PARSER_NO_CHECKSUM
					checksumprec = last_char; // Fake validation of checksum
				#else
				if (parser_status.chksum_check) {
					checksumprec     &= 0x3F;  checksumprec    += 0x20;
					checksumprecprec &= 0x3F; checksumprecprec += 0x20;
				} else {
					checksumprec = last_char;
				}
				#endif

				if ((last_char == checksumprec) || (last_char == checksumprecprec)) { // Check sum OK: Set
					parser_status.parser_state = PEND_PROCESS_ONE_GROUP;
					parser_status.one_group_found = 1;   // Indicate that one group could be found in parser status
					if (tic_parser_frame_rx_handler != NULL) { // NOta: This function is not used during UART init (process not started)
						tic_parser_frame_rx_handler(&parser_status);
						return(1); // successfull return 1 will awake the device
					}
				}

			} else if (((c < 0x20) || (c > 0x7E)) && (c != DELIM_STD)) { // BAD char
				// back waiting for new GROUP,
				if (c == LF) { // Accept immediatly LF as a new group starting
					parser_status.parser_state = PEND_CR;
					checksumprecprec = checksumprec = checksum = 0;

				} else { // Else start waiting LF
					parser_status.parser_state = PEND_LF;
				}
			} else{ // Normal char cumulate for checksum estimations
				checksumprecprec=checksumprec;
				checksumprec=checksum;
				checksum += c;
				last_char = c;
			}
		break;

		default: // Do not do anything here in others cases
		break;
	}
	return(0); // Any case return 0 (not used)
}

//----------------------------------------------------------------------------
// Should return 1 if a frame must be processed
static char savedDEBUTp[6] = {0x00,0x00,0x00,0x00,0x00,0x00};
int tic_parser_input_char(unsigned char c) {

	//---------------------------------------------------------------------------------------------------
 	// Since PMEPMI (many baud rates) start waiting for a valid GROUP before waiting for a full TIC FRAME
	if (! parser_status.one_group_found) return(tic_parser_find_group(c));
	//---------------------------------------------------------------------------------------------------

	// Here start real TIC parsing
	PEG_DEBUG_INPUT_STORE;

	// TODO: When used as interrupt this function may become too long !!!!!!!

	if (parser_status.parser_state > PEND_CR) { // (STOPPED) || (PEND_PROCESS) || (PEND_PROCESS_ONE_GROUP)
		// Ignore any incomming bytes when parser stopped or PEND_PROCESS
		return(0);
	};

	if (c == EOT) {
		// EOT is interrupt of transmission
		// Reject full current frame in case it arrives
		vF_tic_parser_err_log(TIC_ERR_EOT);
		tic_parser_reset();
		return(0);
	}

	parser_status.tic_input_frame_size++; // evaluate original TIC frame size

	// Character processing according to state ... Only switch cases until end of function
	switch (parser_status.parser_state) {

		case (PEND_STX):
			if (c == STX) {
				//tic_parser_reset();
			 	if (err_log_clear_required) {
			 		//memset(tucTICErrLogBuf, 0, TIC_ERR_BUF_SIZE) ;
			 		usTICErrLogBufCurrentSize = 0;
			 		err_log_clear_required = 0;
			 	}

				parser_status.tic_input_frame_size=1; // Add first STX after size zeroed by parser_reset
				parser_status.parser_state = PEND_LF;
			}
		break;

		case (PEND_CR): // Accept either CR/LF or only LF between lines
		case (PEND_LF):
			if ((c == LF) || (c == CR)) {
				parser_status.parser_state = PEND_LABEL; istr = 0; checksum=0;

			} else {
				// Reject full current frame as only CR or LF expected
				vF_tic_parser_err_log(TIC_ERR_BAD_EOL);
				tic_parser_reset();
			}
		break;

		case (PEND_LABEL):
			if (c == LF) {
				// Just ignore surely a LF following CR
				// Reminder: "Processing Appli as end of frame allow ignoring ICE4Q producer quadrants
			} else if ((c == ETX) || (strncmp("Appli",field_label,5) == 0)) {

				field_label[0]='\0';
				// Call for end of frame call back if at least one field was found
				// TODO: Could control a more the packet validity according to
				// EDF specifications
				// Small frame validity control: accept data only if more than x fields are received
				// Accepts short frames CBETM_CT ! ==> To be manage by client application (Cf EDF specifications)
//printf("ETX received with %d field(s)!\n",tic_nb_fields_selected(aTB_GET_DESC(parser_status.pt_tic_buf)));
				if (tic_nb_fields_selected((TIC_desc_t *)aTB_GET_DESC(parser_status.pt_tic_buf)) < parser_status.nb_field_to_valid_frame) {
					// Prepare for next frame
					vF_tic_parser_err_log(TIC_ERR_NOT_ENOUGH_FIELDS);
					tic_parser_reset();

				} else { // process Normal End of frame ETX with valid fields
					// Set lock on ressource until processed
					parser_status.parser_state = PEND_PROCESS;
					if ((pt_expfields != NULL) &&
						((parser_status.pt_tic_descriptor == NULL) ||
						 (parser_status.pt_tic_descriptor->meter_type == MT_NULL))) {

						// Expected fields list could be found, get effective tic_descriptor
						parser_status.pt_tic_descriptor = tic_metertype_to_meterdesc(parser_status.mt_finder);
						parser_status.tic_meter_type_discovered = 1;
					}


#ifndef TIC_TOOLS_CODECS
					// PEG PALLIATIF Problème de réception ?????
					// Constaté plus particulièrement sur flux ICE avec apparition/disparition de PREAVIS DEP
					// et report sur cette apparition AVEC un MIN programmé à 1 minute.
					// Le parser peut rouver un groupe correcte après le STX après avoir sauté plusieurs
					// groupes en réception ???? Ne devrait pas être possible. Il doit y avoir un bug dans l'algo
					// de réception caractère par caractère ???
					// ATTENTION IL NE FAUT METTRE CE PALIATIF QUAND ON COMPILE POUR tictobin et bintotic

					// On a trouvé le champ donc le premier champ obligatoire de chaque type de compteur doit exister
					// Si ce n'est pas le cas on refuse le traitement et on ré-initialise le parser
					// On test que le premier bit théorique obligatoire pour un compteur  est défini)

					if (!((parser_status.pt_tic_buf[aTIC_DESC_MAX_NB_BYTES-1]) &
							parser_status.pt_tic_descriptor->first_mandatory_fields_set)) { // Verify presence of a bit in first mandatory field set

						// mandatory field not set Prepare for next frame
						vF_tic_parser_err_log(TIC_ERR_MISSING_MANDATORY);
						tic_parser_reset();
					} else
#endif
					{

						// Finally Set the size of the frame at the end of buffers
						//--------------------------------------------------------
						if (parser_status.pt_tic_descriptor->meter_type != MT_ICE) { // Generaly meters use only one buffer (except ICE)
							// In this case the full buffer is used for a single big frame
							// Notice that for these possibles big frames (> 256) a two byte integer will be used ! (Cf -1)
							*((unsigned short *) & (parser_status.pt_tic_buf[TIC_BIG_PACKED_BUF_SZ - TIC_SERIALIZED_SIZE_SIZE])) =
								 (unsigned short) (parser_status.pt_tic_buf_buf - parser_status.pt_tic_buf);
						}else {
							// In this case the buffer is separated in 3 blocks
							*((unsigned short *) & (parser_status.pt_tic_buf[TIC_PACKED_BUF_SZ - TIC_SERIALIZED_SIZE_SIZE])) = (unsigned short) (parser_status.pt_tic_buf_buf - parser_status.pt_tic_buf);
							*((unsigned short *) & (parser_status.ice_p_pt_tic_buf[TIC_UNPACKED_BUF_SZ - TIC_SERIALIZED_SIZE_SIZE])) = (unsigned short) (parser_status.ice_p_pt_tic_buf_buf - parser_status.ice_p_pt_tic_buf);
							*((unsigned short *) & (parser_status.ice_p1_pt_tic_buf[TIC_UNPACKED_BUF_SZ - TIC_SERIALIZED_SIZE_SIZE])) = (unsigned short) (parser_status.ice_p1_pt_tic_buf_buf - parser_status.ice_p1_pt_tic_buf);
						}


	// printf("Frame received !\n");
						if (tic_parser_frame_rx_handler != NULL) {
							tic_parser_frame_rx_handler(&parser_status);

							return(1);
						} else {
							// Prepare for next frame
							//vF_tic_parser_err_log(TIC_ERR_MISSING_RX_HANDLER);
							tic_parser_reset();
						}
					} // Validated frame processed
				}

			} else { /* Not EOTX */
				checksum += c;
    //printf("%c(%d)(%02x)=(%d)(%02x) ",c,c,c,checksum,checksum);

				if ((c == DELIM) || (c == DELIM_STD)) {
					first_delim = c;
					field_label[istr]='\0';

//printf("\nl: %s\n",field_label);
					parser_status.parser_state = PEND_VALUE; istr=0;

				} else if ((istr < (STR_LABEL_SZ_MAX -1)) &&
						   (c != LF) && (c != CR) && (c != STX) && (c != ETX))  {
					field_label[istr++] = c;

				} else {
					field_label[istr++]='\0';
					// Reject full current frame
					vF_tic_parser_err_log(TIC_ERR_LABEL_TOO_LONG);
					tic_parser_reset();
				}

			}
		break;

		case (PEND_VALUE):
			if ((c == LF) || (c == CR)) {
				if(istr < 2 ){ // Set from 3 to 2 to accept empty string since CRC is now in field_value at this moment
					vF_tic_parser_err_log(TIC_ERR_VALUE_TOO_SHORT);
					tic_parser_reset();
				} else {

					// MT_STD Case the last DELIM_STD is included in checksum calculation
					checksum = (first_delim == DELIM_STD ? checksumprec : checksumprecprec);

					field_value[istr-2]='\0';

//printf("FIN Value: l: %s, v: %s , Chks = %c (%02x) c = %c (%02x)\n",field_label, field_value,(checksum & 0x3F) + 0x20,(checksum & 0x3F) + 0x20,c,c);

					c = field_value[istr-1];

					#ifdef TIC_PARSER_NO_CHECKSUM
						checksum = c; // Fake validation of checksum
					#else
						if (parser_status.chksum_check) {
							checksum &= 0x3F; checksum += 0x20;
//printf("A) l: %s, v: %s , Chks = %c (%02x)\n",field_label, field_value,checksum,checksum);
						} else {
							checksum = c;
//printf("B) l: %s, v: %s , Chks = %c (%02x)\n",field_label, field_value,checksum,checksum);
						}
					#endif


#define PARSER_NOT_FOUND 0
#define PARSER_PROCESS_GENERAL_FIELD 1
#define PARSER_IGNORE_FIELD 2
#define PARSER_PROCESS_ICE_P_FIELD 3
#define PARSER_PROCESS_ICE_P1_FIELD 4

// printf("\nc==checksum: %c == %c\n", c,checksum);
					if (c==checksum) {
//printf("l: %s, v: %s , Chks = %c (%02x), c = %c (%02x)\n",field_label, field_value,checksum,checksum,c,c);
						// TODO: process validated input field
						process_it = PARSER_NOT_FOUND;

						// if needed, try to find right list of expected fields according to first received field_label
						//---------------------------------------------------------------------------------------------
						if (pt_expfields == NULL) {
							if ((parser_status.pt_tic_descriptor == NULL) ||
								(parser_status.pt_tic_descriptor->meter_type == MT_NULL)) {
								parser_status.mt_finder = MT_UNKNOWN; // Reinit meter finder
								tic_set_expfields_on_label(&pt_expfields, &nb_expfields, field_label);
							} else {
								pt_expfields = parser_status.pt_tic_descriptor->expected_fields;
								nb_expfields = parser_status.pt_tic_descriptor->expected_fields_number;
							}
							// Validate pointers to correct expected sub fields
							if (pt_expfields == tic_meter_descriptor[MT_ICE].expected_fields) {
								ice_p_pt_expfields = tic_meter_descriptor[MT_ICE_p].expected_fields;
								ice_p_nb_expfields = tic_meter_descriptor[MT_ICE_p].expected_fields_number;
								ice_p1_pt_expfields = tic_meter_descriptor[MT_ICE_p1].expected_fields;
								ice_p1_nb_expfields = tic_meter_descriptor[MT_ICE_p1].expected_fields_number;
							}
						}

						// Recherche du label
						// BEWARE: This label search bet on ordered records according to specifications (EDF)
						//-----------------------------------------------------------------------------------
						for (nf = parser_status.no_field; ((nf < nb_expfields) && (!process_it)); nf++) {

							if (pt_expfields[nf].attribute & ATTRIBUTE_NOT_MANAGED_FIELD) {
								// The "not managed" field could be a generic string, so use generic comparison
								if (tic_generic_string_match((unsigned char *)(pt_expfields[nf].label),(unsigned char *)field_label)) {
									process_it = PARSER_IGNORE_FIELD;
								}

							} else if (pt_expfields[nf].attribute & ATTRIBUTE_ICE_pp1_FIELD) {
								if (tic_generic_string_match((unsigned char *)(pt_expfields[nf].label),(unsigned char *)field_label)) {
									if (tic_generic_string_match((unsigned char *)"*1*",(unsigned char *)field_label)) {
										// Find field_label in Period P minus 1 case
										for (ice_p1_nf = parser_status.ice_p1_no_field; ((ice_p1_nf < ice_p1_nb_expfields) && (!process_it)); ice_p1_nf++) {
											if (ice_p1_pt_expfields[ice_p1_nf].attribute & ATTRIBUTE_NOT_MANAGED_FIELD) {
												// The "not managed" field could be a generic string, so use generic comparison
												if (tic_generic_string_match((unsigned char *)(ice_p1_pt_expfields[nf].label),(unsigned char *)field_label)) {
													process_it = PARSER_IGNORE_FIELD;
												}

											} else if (strcmp(ice_p1_pt_expfields[ice_p1_nf].label,field_label) == 0) {
												process_it = PARSER_PROCESS_ICE_P1_FIELD;
											}
										}
										ice_p1_nf--;
									} else {
										// Find field_label in Period P case
										for (ice_p_nf = parser_status.ice_p_no_field; ((ice_p_nf < ice_p_nb_expfields) && (!process_it)); ice_p_nf++) {
											if (ice_p_pt_expfields[ice_p_nf].attribute & ATTRIBUTE_NOT_MANAGED_FIELD) {
												// The "not managed" field could be a generic string, so use generic comparison
												if (tic_generic_string_match((unsigned char *)(ice_p_pt_expfields[nf].label),(unsigned char *)field_label)) {
													process_it = PARSER_IGNORE_FIELD;
												}

											} else if (strcmp(ice_p_pt_expfields[ice_p_nf].label,field_label) == 0) {
												process_it = PARSER_PROCESS_ICE_P_FIELD;

											}
										}
										ice_p_nf--;
									}
								}

							} else if (pt_expfields[nf].attribute & ATTRIBUTE_REGULAR_EXPR) {
								if (tic_generic_string_match((unsigned char *)(pt_expfields[nf].label),(unsigned char *)field_label)) {
									process_it = PARSER_PROCESS_GENERAL_FIELD;
								}

							} else if (pt_expfields[nf].attribute & ATTRIBUTE_NOT_LBL_CASE_SENSITIVE) {

								if (strcmp_nocasesensitive((char*)pt_expfields[nf].label,field_label) == 0) {
									process_it = PARSER_PROCESS_GENERAL_FIELD;
								}
							} else if (strcmp(pt_expfields[nf].label,field_label) == 0) {
								process_it = PARSER_PROCESS_GENERAL_FIELD;

							}
						} // for
						nf--;

#ifndef TIC_TOOLS_CODECS
						// PEG PALLIATIF Problème de réception ?????
						// Constaté plus particulièrement sur flux ICE avec apparition/disparition de PREAVIS DEP
						// et report sur cette apparition AVEC un MIN programmé à 1 minute.
						// Le parser peut rouver un groupe correcte après le STX après avoir sauté plusieurs
						// groupes en réception ???? Ne devrait pas être possible. Il doit y avoir un bug dans l'algo
						// de réception caractère par caractère ???
						// ATTENTION IL NE FAUT METTRE CE PALIATIF QUAND ON COMPILE POUR tictobin et bintotic
						if ((process_it != PARSER_NOT_FOUND) &&  (nf > 3)) {
							// On a trouvé le champ donc le premier champ obligatoire de chaque type de compteur doit exister
							// Si ce n'est pas le cas on refuse le traitement et on ré-initialise le parser
							// Tous les compteurs doivent avoir au moins un bit parmis les 4 premiers de défini)
							if (!((parser_status.pt_tic_buf[aTIC_DESC_MAX_NB_BYTES-1]) & 0x0F)) {
								process_it = PARSER_NOT_FOUND; // Then the parser will be rested
							}
						}
#endif

						// Process the identified received record
						//---------------------------------------
						if (process_it==PARSER_PROCESS_GENERAL_FIELD) {  // ***************************************

							// Make necessary real time meter type search if needed

							if ((parser_status.pt_tic_descriptor == NULL) ||
								(parser_status.pt_tic_descriptor->meter_type == MT_NULL)) {
								rt_find_meter_desc(&(parser_status.mt_finder), pt_expfields, nf);
							}
							parser_status.no_field = process_record_tic_buf(
									nf,
									&(parser_status.pt_tic_buf_buf),
									pt_expfields,
									aTB_GET_DESC(parser_status.pt_tic_buf),
									NULL);

						} else if (process_it==PARSER_IGNORE_FIELD) {  // *****************************************
							// Must Jump over (accept) currently parsed field
							// but stay on current expected field, has there could be multiple
							parser_status.no_field = nf;

						} else if (process_it==PARSER_PROCESS_ICE_P_FIELD) {  // *********************************
							// Add DATECOUR or DATE to the ice period p1 buffer (last modification)
							if (ice_p_nf > 3) {
								parser_status.ice_p_block_initialised =
									ice_pp1_init_block(parser_status.pt_tic_buf,
				    					ice_p_nf,
				    					parser_status.ice_p_block_initialised,
										aTB_GET_DESC(parser_status.ice_p_pt_tic_buf),
										aTB_GET_BUF(parser_status.ice_p_pt_tic_buf));
							}

							// Manage differents ICE period p subfields fields
							parser_status.ice_p_no_field = process_record_tic_buf(
									ice_p_nf,
									&(parser_status.ice_p_pt_tic_buf_buf),
									ice_p_pt_expfields,
									aTB_GET_DESC(parser_status.ice_p_pt_tic_buf),
									aTB_GET_BUF(parser_status.ice_p_pt_tic_buf));


							// If DEBUTp has changed erase all ICEp and ICEp1 fields has they are no more sync'ed with contactual period
							// erase all currently set values
							if (ice_p_nf == 0) {
								if (memcmp(aTB_GET_BUF(parser_status.ice_p_pt_tic_buf), savedDEBUTp, 6) != 0) {
									// initi descriptor on contractual period change
									// Set all bit of ICEp and ICEp1 descriptors to 0 except first byte header and DEBUTp's bit which should have just been set
									memset((aTB_GET_DESC(parser_status.ice_p_pt_tic_buf)+1),0x00,aTIC_DESC_NB_BYTES_ORIGINAL-1);
									memset((aTB_GET_DESC(parser_status.ice_p1_pt_tic_buf)+1),0x00,aTIC_DESC_NB_BYTES_ORIGINAL-1);
									// Set back first bit (DEBUTp)
									vFTicFieldSetBit(aTB_GET_DESC(parser_status.ice_p_pt_tic_buf),0);
									// Then set new savecDEBUTp
									memcpy(savedDEBUTp, aTB_GET_BUF(parser_status.ice_p_pt_tic_buf), 6);
								}
							}

							// Continue main parsing on current label
							parser_status.no_field = nf;

						} else if (process_it==PARSER_PROCESS_ICE_P1_FIELD) {  // *********************************
							// Add DATECOUR or DATE to the ice period p1 buffer (last modification)
							if (ice_p1_nf > 3) {
								parser_status.ice_p1_block_initialised =
									ice_pp1_init_block(parser_status.pt_tic_buf,
				    					ice_p1_nf,
				    					parser_status.ice_p1_block_initialised,
										aTB_GET_DESC(parser_status.ice_p1_pt_tic_buf),
										aTB_GET_BUF(parser_status.ice_p1_pt_tic_buf));
							}

							// Manage differents ICE period p1 subfields fields
							parser_status.ice_p1_no_field = process_record_tic_buf(
									ice_p1_nf,
									&(parser_status.ice_p1_pt_tic_buf_buf),
									ice_p1_pt_expfields,
									aTB_GET_DESC(parser_status.ice_p1_pt_tic_buf),
									aTB_GET_BUF(parser_status.ice_p1_pt_tic_buf));

							// Continue main parsing on current label
							parser_status.no_field = nf;
						}

						if (!process_it) {
							if (parser_status.strict){
								vF_tic_parser_err_log(TIC_ERR_UNEXPECTED_LABEL);
								tic_parser_reset();
							}else {
								// Not rigorous parser just ignore unknown field
								// And do not move current "parser_status.no_field";
								parser_status.parser_state = PEND_LABEL;
								istr = 0; checksum=0;
							}
						} else {
							parser_status.parser_state = PEND_LABEL;
							istr = 0; checksum=0;
						}

					} else { // (c==checksum)
						// Reject full current frame !!
						vF_tic_parser_err_log(TIC_ERR_BAD_CHECKSUM);
						tic_parser_reset();
// printf(", chks: KO\n");
					}
				} // !(istr < 3 )


			} else if ((istr < (STR_VALUE_SZ_MAX -1)) /*&& (c != STX) && (c != ETX)*/) {
				checksumprecprec=checksumprec;
				checksumprec=checksum;
				checksum += c;
// printf("%c(%d)(%02x)=(%d)(%02x) ",c,c,c,checksum,checksum);
				field_value[istr++] = c;

//printf("l: %s, v: %s , Chks = %c (%02x) c = %c (%02x)\n",field_label, field_value,(checksum & 0x3F) + 0x20,(checksum & 0x3F) + 0x20,c,c);

			} else { // Too long value string
				// Reject full current frame
				vF_tic_parser_err_log(TIC_ERR_VALUE_TOO_LONG);
				tic_parser_reset();
			};
		break;
		default:
		   // Should not get here
		break;

	} // switch (parser_status.parser_state)
	// Return code 0 anycase for now ...
	return(0);
}

