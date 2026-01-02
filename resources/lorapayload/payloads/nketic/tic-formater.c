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
 * 		TIC formater
 * \author
 *      P.E. Goudet <pe.goudet@watteco.com>
 */

/*============================ INCLUDE =======================================*/

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <time.h>

#include "tic-formater.h"

// Currently selected meter descriptor ==> Frame format
static TIC_meter_descriptor_t * tic_descriptor;


static unsigned char checksum,checksumprec,checksumprecprec;
static unsigned long tmp_ulong;
static float tmp_float;
//static signed long tmp_long;
static unsigned short tmp_ushort;
static signed short tmp_short;

//----------------------------------------------------------------------------
// Must be called at least once before using tic_formater !!
void tic_formater_init(TIC_meter_descriptor_t * tic_desc) {
	tic_descriptor = tic_desc;
	checksum=0;checksumprec=0;checksumprecprec=0;
}

//----------------------------------------------------------------------------
// Return position in tic_buf buffer after field formated in the record

extern const char FMT_ld_kWh[];
extern const char FMT_ld_kvarh[];
const char * pt_var_fmt;
unsigned char * tic_formater_record_put(char * strbuf, unsigned char rec_num, unsigned char * filterDesc, unsigned char * tbdesc, unsigned char *pt_buf, unsigned char *doNotChangeOfField) {
	char *ptr;
	signed char max;
	char *tmpptr;
	unsigned char i;

	*doNotChangeOfField = 0;

	if (tic_descriptor->expected_fields[rec_num].attribute & ATTRIBUTE_IS_SUBFIELD) {
		// Can't format a full record from subfiled number !!
		// Thing should have been done with first field of multiple field record
		// do not do anything
		return(pt_buf);
	}

	ptr = strbuf;
	pt_var_fmt = NULL;
	max = 1;

	// first manage field label for all records
	ptr += sprintf(ptr, "%s%c",
		tic_descriptor->expected_fields[rec_num].label,
		(tic_descriptor->meter_type == MT_STD ? DELIM_STD : DELIM));

	switch (tic_descriptor->expected_fields[rec_num].type) {

		case (TYPE_CSTRING):
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) sprintf(ptr, "%s","");
			else {
				if (tic_descriptor->expected_fields[rec_num].attribute & ATTRIBUTE_MULTI_OCCURENCE_FIELD) {
					// Look for ',' and replace it by '\0' then print it
					if ((tmpptr = strchr((char *)pt_buf, ',')) != NULL) {
						*tmpptr='\0';
						*doNotChangeOfField = 1;
					}
				}
				sprintf(ptr, tic_descriptor->expected_fields[rec_num].fmt, pt_buf); pt_buf += strlen((char*)pt_buf) + 1;
			}
		break;

		case (TYPE_CHAR):
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) sprintf(ptr, "^"); // Not a checked value
			else { sprintf(ptr, tic_descriptor->expected_fields[rec_num].fmt, *pt_buf); pt_buf += 1;}
		break;


		case (TYPE_SDMYhmsU8):
			// "SAAMMJJhhmmss", Saison, Annee, Mois, Jour, heure, minute, seconde
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) sprintf(ptr, "^000000000000%c",DELIM_STD); // Not a checked value
			else {
				ptr+=sprintf(ptr, "%c%02d%02d%02d%02d%02d%02d%c",
					*(char *)(pt_buf),
					*(char *)(pt_buf+1),*(char *)(pt_buf+2),*(char *)(pt_buf+3),
					*(char *)(pt_buf+4),*(char *)(pt_buf+5),*(char *)(pt_buf+6),
					DELIM_STD);
				pt_buf += 7;
			}

		case (TYPE_BF8d):
		case (TYPE_U8):
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0)
				ptr+=sprintf(ptr, tic_descriptor->expected_fields[rec_num].fmt,0); // Not a checked value
			else {
				ptr+=sprintf(ptr, tic_descriptor->expected_fields[rec_num].fmt, *pt_buf); pt_buf += 1;
			}
		break;

		case (TYPE_11hhmmSSSS):
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) {
				for (i = 0; i < 11; i++) {
					ptr += sprintf(ptr, "NONUTILE");
					if (i < 10) ptr += sprintf(ptr, " ");
				}
			} else {
				for (i = 0; i < 11; i++) {
					if (*pt_buf == (unsigned char)0xFF) {
						ptr += sprintf(ptr, "NONUTILE");
						pt_buf += 1;
					} else {
						ptr += sprintf(ptr, "%02d%02d%02x%02x",
											*(pt_buf),*(pt_buf + 1),
											*(pt_buf+2),*(pt_buf + 3));
						pt_buf += 4;
					}
					if (i < 10) ptr += sprintf(ptr, " ");
				}
			}
		break;

		case (TYPE_SDMYhmsU16):
			// "SAAMMJJhhmmss", Saison, Annee, Mois, Jour, heure, minute, seconde
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) ptr += sprintf(ptr, "^000000000000%c",DELIM_STD); // Not a checked value
			else {
				ptr+=sprintf(ptr, "%c%02d%02d%02d%02d%02d%02d%c",
					*(char *)(pt_buf),
					*(char *)(pt_buf+1),*(char *)(pt_buf+2),*(char *)(pt_buf+3),
					*(char *)(pt_buf+4),*(char *)(pt_buf+5),*(char *)(pt_buf+6),
					DELIM_STD);
				 pt_buf += 7;
			}
		case (TYPE_U16):
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) sprintf(ptr, tic_descriptor->expected_fields[rec_num].fmt,0); // Not a checked value
			else {
				U16p_TO_U16(pt_buf, tmp_ushort);
				sprintf(ptr, tic_descriptor->expected_fields[rec_num].fmt, tmp_ushort); pt_buf += 2;
			}
		break;

		case (TYPE_I16):
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) sprintf(ptr, tic_descriptor->expected_fields[rec_num].fmt,0); // Not a checked value
			else {
				I16p_TO_I16(pt_buf, tmp_short);
				sprintf(ptr, tic_descriptor->expected_fields[rec_num].fmt, tmp_short); pt_buf += 2;
			}
		break;

		case (TYPE_U24CSTRING):
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) {
				ptr += sprintf(ptr, tic_descriptor->expected_fields[rec_num].fmt,0); // Not a checked value
				ptr += sprintf(ptr, "%s",""); // Not a checked value
			} else {
				U24p_TO_U32(pt_buf, tmp_ulong);
				ptr+=sprintf(ptr, tic_descriptor->expected_fields[rec_num].fmt, tmp_ulong);
				pt_buf += 3;
				ptr+=sprintf(ptr, "%s", pt_buf);
				pt_buf += strlen((char*)pt_buf) + 1;
			}
		break;

		case (TYPE_SDMYhmsU24):
			// "SAAMMJJhhmmss", Saison, Annee, Mois, Jour, heure, minute, seconde
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) ptr += sprintf(ptr, "^000000000000%c",DELIM_STD); // Not a checked value
			else {
				ptr+=sprintf(ptr, "%c%02d%02d%02d%02d%02d%02d%c",
					*(char *)(pt_buf),
					*(char *)(pt_buf+1),*(char *)(pt_buf+2),*(char *)(pt_buf+3),
					*(char *)(pt_buf+4),*(char *)(pt_buf+5),*(char *)(pt_buf+6),
					DELIM_STD);
				 pt_buf += 7;
			}
		case (TYPE_U24):
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) sprintf(ptr, tic_descriptor->expected_fields[rec_num].fmt,0); // Not a checked value
			else {
				U24p_TO_U32(pt_buf, tmp_ulong);
				sprintf(ptr,
					(pt_var_fmt == NULL ? tic_descriptor->expected_fields[rec_num].fmt : pt_var_fmt), tmp_ulong);
				pt_buf += 3;
			}
		break;

		case (TYPE_6U24): // CJE counter cases: needing "reformating" : 111111:222222:...:666666 or 11111:22222:...:44444
						  // Can have up to 4 or 6 ':' separated u24, to store in successive fields
			max += 2;
		case (TYPE_4U24):
			max += 3;
			do {
				if (ucFTicFieldGetBit(tbdesc,rec_num) != 0) {
					if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) {
						ptr += sprintf(ptr, tic_descriptor->expected_fields[rec_num].fmt,0); // Not a checked value
					} else {
						U24p_TO_U32(pt_buf, tmp_ulong);
						ptr += sprintf(ptr, tic_descriptor->expected_fields[rec_num].fmt, tmp_ulong);
						pt_buf+=3;
					}
				}
				// Step to next attribute
				rec_num++;	max--;
				if ((max == 2) &&
					(ucFTicFieldGetBit(tbdesc,rec_num+1) == 0) &&
					(ucFTicFieldGetBit(tbdesc,rec_num+1) == 0)) break; // Do not print lasts ':' if last 2 fields are empty
				if (max>0) ptr += sprintf(ptr, ":");
			} while ( (max>0) &&
					(tic_descriptor->expected_fields[rec_num].attribute & ATTRIBUTE_IS_SUBFIELD));
		break;

		case (TYPE_U32):
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) {
				sprintf(ptr, (pt_var_fmt == NULL ? tic_descriptor->expected_fields[rec_num].fmt : pt_var_fmt),0); // Not a checked value
			} else {
				U32p_TO_U32(pt_buf, tmp_ulong);
				sprintf(ptr,
					(pt_var_fmt == NULL ? tic_descriptor->expected_fields[rec_num].fmt : pt_var_fmt), tmp_ulong);
				pt_buf += 4;
			}
		break;

		case (TYPE_FLOAT):
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) {
				sprintf(ptr, (pt_var_fmt == NULL ? tic_descriptor->expected_fields[rec_num].fmt : pt_var_fmt),0.0); // Not a checked value
			} else {
				FLTp_TO_FLT(pt_buf, tmp_float);
				sprintf(ptr,
					(pt_var_fmt == NULL ? tic_descriptor->expected_fields[rec_num].fmt : pt_var_fmt), tmp_float);
				if ((ptr = strchr(ptr,'.')) != NULL) *ptr = ','; // Float decimal is comma for TIC float strings (TGPHI)
				pt_buf += 4;
			}
		break;

		case (TYPE_BF32xbe):
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) {
				sprintf(ptr, "00000000"); // Not a checked value
			} else {
				sprintf(ptr, "%02x%02x%02x%02x",
					*(unsigned char *)(pt_buf),*(unsigned char *)(pt_buf+1),
					*(unsigned char *)(pt_buf+2),*(unsigned char *)(pt_buf+3));
				 pt_buf += 4;
			}
		break;

		case (TYPE_HEXSTRING): {
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) {
				sprintf(ptr, "%s",""); // Not a checked value empty hex string
			} else {
				max = *pt_buf;pt_buf++;
				while (max > 0) {
					ptr += sprintf(ptr,"%02x",*pt_buf);
					pt_buf++; max--;
				}
			}
		}
		break;

		case (TYPE_SDMYhms):
			// "SAAMMJJhhmmss", Saison, Annee, Mois, Jour, heure, minute, seconde
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) sprintf(ptr, "^000000000000%c",DELIM_STD); // Not a checked value
			else {
				sprintf(ptr, "%c%02d%02d%02d%02d%02d%02d%c",
					*(char *)(pt_buf),
					*(char *)(pt_buf+1),*(char *)(pt_buf+2),*(char *)(pt_buf+3),
					*(char *)(pt_buf+4),*(char *)(pt_buf+5),*(char *)(pt_buf+6),
					DELIM_STD); // TODO: Check if horodatage simple with data size = 0 implies \t\t
				 pt_buf += 7;
			}
		break;

		case (TYPE_DMYhms):
			// "JJ/MM/AA HH/MM/SS"
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) sprintf(ptr, "00/00/00 00:00:00"); // Not a checked value
			else {
				sprintf(ptr, "%02d/%02d/%02d %02d:%02d:%02d",
					*(char *)(pt_buf)  ,*(char *)(pt_buf+1),*(char *)(pt_buf+2),
					*(char *)(pt_buf+3),*(char *)(pt_buf+4),*(char *)(pt_buf+5));
				pt_buf += 6;
			}
		break;

        case (TYPE_tsDMYhms): {
				// NEW encoding using Timestamp and periode tarifaire compression
				U32p_TO_U32(pt_buf, tmp_ulong);
				struct tm *tmptr = tic_get_tm_from_timestamp(tmp_ulong);

				ptr+=sprintf(ptr, "%02d/%02d/%02d %02d:%02d:%02d",
					tmptr->tm_mday , (tmptr->tm_mon + 1), tmptr->tm_year - (2000 - 1900),
					tmptr->tm_hour, tmptr->tm_min, tmptr->tm_sec);
				pt_buf += 4;
			}
		break;

        case (TYPE_DMYhmsCSTRING):
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) sprintf(ptr, "00/00/00 00:00:00-"); // Not a checked value
			else {

				ptr+=sprintf(ptr, "%02d/%02d/%02d %02d:%02d:%02d-",
					*(char *)(pt_buf)  ,*(char *)(pt_buf+1),*(char *)(pt_buf+2),
					*(char *)(pt_buf+3),*(char *)(pt_buf+4),*(char *)(pt_buf+5));
				pt_buf += 6;
				sprintf(ptr, "%s", pt_buf);
				pt_buf += strlen((char*)pt_buf) + 1;
			}
		break;

        case (TYPE_E_PT):
        case (TYPE_E_DIV):
        case (TYPE_E_CONTRAT):
        case (TYPE_E_STD_PT):
        case (TYPE_E_STD_CONTRAT): {
				// NEW encoding using enum compression
				ptr += sprintf(ptr,
					tic_descriptor->expected_fields[rec_num].fmt,
					tic_enum_uncompress(tic_descriptor->expected_fields[rec_num].type, pt_buf));
				pt_buf += tic_enum_len(pt_buf);
			}
		break;

        case (TYPE_U24_E_DIV):
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) {
				ptr += sprintf(ptr, tic_descriptor->expected_fields[rec_num].fmt,0); // Not a checked value
				ptr += sprintf(ptr, "%s",""); // Not a checked value
			} else {
				U24p_TO_U32(pt_buf, tmp_ulong);
				ptr+=sprintf(ptr, "%ld", tmp_ulong);
				pt_buf += 3;
				ptr += sprintf(ptr,	"%s", tic_enum_uncompress(TYPE_U24_E_DIV, pt_buf));
				pt_buf += tic_enum_len(pt_buf);
			}
        break;

        case (TYPE_tsDMYhms_E_PT): {
				// NEW encoding using Timestamp and periode tarifaire compression
				U32p_TO_U32(pt_buf, tmp_ulong);
				struct tm *tmptr = tic_get_tm_from_timestamp(tmp_ulong);

				ptr+=sprintf(ptr, "%02d/%02d/%02d %02d:%02d:%02d-",
					tmptr->tm_mday , (tmptr->tm_mon + 1), tmptr->tm_year - (2000 - 1900),
					tmptr->tm_hour, tmptr->tm_min, tmptr->tm_sec);
				pt_buf += 4;
				ptr += sprintf(ptr, "%s", tic_enum_uncompress(TYPE_E_PT, pt_buf));
				pt_buf += tic_enum_len(pt_buf);
			}
		break;

		case (TYPE_hmDM):  // CJE counter cases: needing "sub-parsing": {hh:mn:jj:mm}:pt:dp:abcde:kp
			if (ucFTicFieldGetBit(tbdesc,rec_num)){
				sprintf(ptr, "%02d:%02d:%02d:%02d:",pt_buf[0],pt_buf[1],pt_buf[2],pt_buf[3]); ptr += 12; pt_buf+=4;
			} else if (ucFTicFieldGetBit(filterDesc,rec_num)){
				ptr += sprintf(ptr, "00:00:00:00:");
			} else ptr += sprintf(ptr, "::::");
			rec_num++;

			if (ucFTicFieldGetBit(tbdesc,rec_num)){
				sprintf(ptr, "%s:",(char *)pt_buf); ptr += strlen((char*)pt_buf) + 1; pt_buf += strlen((char*)pt_buf) + 1;
			} else ptr += sprintf(ptr, ":");
			rec_num++;

			if (ucFTicFieldGetBit(tbdesc,rec_num)){
				sprintf(ptr, "%s:",(char *)pt_buf); ptr += strlen((char*)pt_buf) + 1; pt_buf += strlen((char*)pt_buf) + 1;
			} else ptr += sprintf(ptr, ":");
			rec_num++;

			if (ucFTicFieldGetBit(tbdesc,rec_num)){
				U24p_TO_U32(pt_buf, tmp_ulong);
				sprintf(ptr, "%05ld:", tmp_ulong); ptr += 6; pt_buf+=3;
			} else 	if (ucFTicFieldGetBit(filterDesc,rec_num)){
				ptr += sprintf(ptr, "00000:");
			} else ptr += sprintf(ptr, ":");
			rec_num++;

			if (ucFTicFieldGetBit(tbdesc,rec_num)){
				ptr += sprintf(ptr, "%02d",*pt_buf); pt_buf+=1;
			} else 	if (ucFTicFieldGetBit(filterDesc,rec_num)){
				ptr += sprintf(ptr, "00");
			}
		break;

		case (TYPE_DMh):  // CJE counter cases: needing "sub-parsing":  {jj:mm:hh}:cg
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) sprintf(ptr, "00:00:00:00"); // Not a checked value
			else {
				if (ucFTicFieldGetBit(tbdesc,rec_num)){
					sprintf(ptr, "%02d:%02d:%02d:",pt_buf[0],pt_buf[1],pt_buf[2]); ptr += 9; pt_buf+=3;
				} else if (ucFTicFieldGetBit(filterDesc,rec_num)){
					ptr += sprintf(ptr, "00:00:00:");
				} else ptr += sprintf(ptr, ":::");
				rec_num++;

				if (ucFTicFieldGetBit(tbdesc,rec_num)){
					sprintf(ptr, "%02d",*pt_buf); pt_buf+=1;
				} else if (ucFTicFieldGetBit(filterDesc,rec_num)){
					ptr += sprintf(ptr, "00");
				}
			}
		break;

		case (TYPE_hm):  // CJE counter cases: needing "sub-parsing":  {hh:mn}:dd
			if (ucFTicFieldGetBit(tbdesc,rec_num) == 0) sprintf(ptr, "00:00:00"); // Not a checked value
			else {
				if (ucFTicFieldGetBit(tbdesc,rec_num)){
					sprintf(ptr, "%02d:%02d:",pt_buf[0],pt_buf[1]); ptr += 6; pt_buf+=2;
				} else if (ucFTicFieldGetBit(filterDesc,rec_num)){
					ptr += sprintf(ptr, "00:00:");
				} else ptr += sprintf(ptr, "::");
				rec_num++;

				if (ucFTicFieldGetBit(tbdesc,rec_num)){
					ptr += sprintf(ptr, "%02d",*pt_buf); pt_buf+=1;
				} else if (ucFTicFieldGetBit(filterDesc,rec_num)){
					ptr += sprintf(ptr, "00");
				}
			}
		break;

		default:
			// Get out without any change neither put in buf if TYPE not recognized
			return pt_buf;
		break;
	};

// printf("strbuf: %s\n",strbuf);

	// Checksum calculation
	//checksum = 'x';
    if (tic_descriptor->meter_type == MT_STD) {
		ptr = strbuf + strlen(strbuf);
		sprintf(ptr, "%c",DELIM_STD);
		checksum = tic_str_compute_checksum(strbuf);
		ptr +=1;
		sprintf(ptr, "%c%c",checksum,LF);
	} else {
		checksum = tic_str_compute_checksum(strbuf);
		ptr = strbuf + strlen(strbuf);
		sprintf(ptr, "%c%c%c",DELIM,checksum,LF);
	}
//printf("<%s>\n",strbuf);
	return(pt_buf);
}

//----------------------------------------------------------------------------
// Basic example needing Big Output buffer .. could be rewritten for specific application use case
void tic_formater_frame_put(char* buf, unsigned char * filterDesc, unsigned char * tbdesc, unsigned char * tbbuf) {

	int ifield;
	int nfield;
	unsigned char doNotChangeOfField=0;

	ifield=0;
	nfield=tic_descriptor->expected_fields_number;


	sprintf(buf, "%c%c",STX,LF); buf += strlen(buf);

	while (nfield - ifield > 0) {
		doNotChangeOfField = 0;

		// Find if we are on a not empty fields group has we may have to print part of it if some of thes fields exists ?
		unsigned char filled_fields_group = 0;
		unsigned char ifield_tmp = ifield;
		if (!(tic_descriptor->expected_fields[ifield_tmp].attribute & ATTRIBUTE_IS_SUBFIELD)) {
			ifield_tmp++;
			while ((tic_descriptor->expected_fields[ifield_tmp].attribute & ATTRIBUTE_IS_SUBFIELD) &&
					(!filled_fields_group )){
				filled_fields_group =  (ucFTicFieldGetBit(tbdesc,ifield_tmp) != 0 ? 0x01 : 0x00);
				filled_fields_group += (ucFTicFieldGetBit(filterDesc,ifield) != 0 ? 0x02 : 0x00);
				ifield_tmp++;
			}
			if ((ifield_tmp - ifield > 1) && (!filled_fields_group )) {
				// We were really on a filed with subfields. test if the "father" had data
				filled_fields_group =  (ucFTicFieldGetBit(tbdesc,ifield)     != 0 ? 0x01 : 0x00);
				filled_fields_group += (ucFTicFieldGetBit(filterDesc,ifield) != 0 ? 0x02 : 0x00);
			}
		}

		if ((ucFTicFieldGetBit(tbdesc,ifield) != 0) ||
			(filled_fields_group) ||
			(ucFTicFieldGetBit(filterDesc,ifield) != 0)) {
			tbbuf = tic_formater_record_put(buf, ifield, filterDesc, tbdesc, tbbuf, &doNotChangeOfField);
			buf += strlen(buf);

		} // if (ucFTicFieldGetBit(tbdesc,ifield) != 0)

		// Pass to next field, jumping over subfields if there was some
		if (! doNotChangeOfField) {
			if (filled_fields_group) ifield = ifield_tmp;
			else ifield++;
		}

	} // while (nfield-- > 0)

	sprintf(buf, "%c%c",ETX,LF); buf += strlen(buf);
};

