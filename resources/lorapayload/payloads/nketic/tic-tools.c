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
 * 		TIC tools for variable TIC frames management
 * \author
 *      P.E. Goudet <pe.goudet@watteco.com>
 */

/*============================ INCLUDE =======================================*/

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <ctype.h>

#include "tic-tools.h"

// ** Data management (very simplistic)
// TODO: really manage timestamps ... maybe heavy ?
const unsigned char	monthdays[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};

// TODO: Manage correct ICE atributes and formating
/*
 * Formats (Atributs ?) à prévoir pour ICE
- ICE -------
JJ/MM/AA HH/MM/SS : DATE       : Dates
xxxxxYkw     : PAX            : puissance moyennes actives
xxxxxxxkWh   : EA,EAp,EAp1    : Indexes energies actives
xxxxxxxkWh   : ERP,ERPp,ERPp1 : Indexes energies reactives positives
xxxxxxxkvarh : ERNp,ERNp1     : Indexes energies reactives negatives
xxxxxkW      : PS,PA          : Puissances actives
xxxxxkvar    : PREA           : Puissances reactives (Signées -32768/+32767)
xxxxxxV      : U              : Tension
xxx%         : KDC, KDCD      : Coefficient ...
xxxxx,xx     : TGPHI          : TG Phi Réel Positif/Negatif
*/

// BEWARE: Following array must be synchronized with "TIC_binary_type_t" definition(Cf. tic-tools.h)
const unsigned char TIC_binary_type_size[TYPE_END] = TIC_BINARY_TYPE_SIZE_ARRAY;

const char FMT_UNDEF[]     = "";

const char FMT_s[]     = "%s";
const char FMT_PREAVIS_PT[] = "TD-%s";
const char FMT_c[]     = "%c";
const char FMT_02X[]   = "%02X";
const char FMT_d[]     = "%d";
const char FMT_ld[]    = "%ld";

const char FMT_02d[]   = "%02d";
const char FMT_03d[]   = "%03d";
const char FMT_05d[]   = "%05d";
/*
const char FMT_07d[]   = "%07d";
const char FMT_09d[]   = "%09d";
*/
const char FMT_05ld[]  = "%05ld";
const char FMT_06ld[]  = "%06ld";
const char FMT_07ld[]  = "%07ld";
const char FMT_09ld[]  = "%09ld";

const char FMT_d_percent[] = "%d%%";

const char FMT_d_s[]    = "%ds";

const char FMT_d_kW[]    = "%dkW";
const char FMT_d_kvar[]  = "%dkvar";

const char FMT_05d_kwh[]   = "%05ldkwh";
const char FMT_ld_Wh[]   = "%ldWh";
const char FMT_05ld_Wh[]   = "%05ldWh";
const char FMT_05ld_varh[]   = "%05ldvarh";
const char FMT_ld_varh[]   = "%ldvarh";
const char FMT_ld_VAh[]   = "%ldVAh";

const char FMT_d_V[]       = "%dV";

const char FMT_d_kWh[]   = "%dkWh";
const char FMT_ld_kWh[]   = "%07ldkWh";
const char FMT_d_kvarh[] = "%dkvarh";
const char FMT_ld_kvarh[] = "%07ldkvarh";

const char FMT_05_2f[]      = "%05.2f";


// ** Unknown meter *******************************************************
// **************************************************************************
#define UNKNOWN_FIELDS_MAX_NUMBER 1
const TIC_expected_field_t UNKNOWN_expected_fields[UNKNOWN_FIELDS_MAX_NUMBER]={{"",0,0,FMT_UNDEF}};

// ** Compteur Linky : "TIC standard" frame *********************************
// **************************************************************************
#define STD_FIELDS_MAX_NUMBER 71
const TIC_expected_field_t STD_expected_fields[STD_FIELDS_MAX_NUMBER]=
{
	/* Should be ordened compared to real stream to optimize parsing (cf no_field which is not re-initialized )*/
	// Byte 0
	{"ADSC",    TYPE_CSTRING,0,FMT_s},
	{"VTIC",    TYPE_U8,0,FMT_02d},
	{"DATE",    TYPE_SDMYhms,0,FMT_UNDEF},
	{"NGTF",    TYPE_E_STD_CONTRAT,0,FMT_s},
	{"LTARF",   TYPE_E_STD_PT,0,FMT_s},
	{"EAST",    TYPE_U32,0,FMT_09ld},
	{"EASF01",  TYPE_U32,0,FMT_09ld},
	{"EASF02",  TYPE_U32,0,FMT_09ld},
	// Byte 1
	{"EASF03",  TYPE_U32,0,FMT_09ld},
	{"EASF04",  TYPE_U32,0,FMT_09ld},
	{"EASF05",  TYPE_U32,0,FMT_09ld},
	{"EASF06",  TYPE_U32,0,FMT_09ld},
	{"EASF07",  TYPE_U32,0,FMT_09ld},
	{"EASF08",  TYPE_U32,0,FMT_09ld},
	{"EASF09",  TYPE_U32,0,FMT_09ld},
	{"EASF10",  TYPE_U32,0,FMT_09ld},
	// Byte 2
	{"EASD01",  TYPE_U32,0,FMT_09ld},
	{"EASD02",  TYPE_U32,0,FMT_09ld},
	{"EASD03",  TYPE_U32,0,FMT_09ld},
	{"EASD04",  TYPE_U32,0,FMT_09ld},
	{"EAIT",    TYPE_U32,0,FMT_09ld},
	{"ERQ1",    TYPE_U32,0,FMT_09ld},
	{"ERQ2",    TYPE_U32,0,FMT_09ld},
	{"ERQ3",    TYPE_U32,0,FMT_09ld},
	// Byte 3
	{"ERQ4",    TYPE_U32,0,FMT_09ld},
	{"IRMS1",   TYPE_U16,0,FMT_03d},
	{"IRMS2",   TYPE_U16,0,FMT_03d},
	{"IRMS3",   TYPE_U16,0,FMT_03d},
	{"URMS1",   TYPE_U16,0,FMT_03d},
	{"URMS2",   TYPE_U16,0,FMT_03d},
	{"URMS3",   TYPE_U16,0,FMT_03d},
	{"PREF",    TYPE_U8,0,FMT_02d},
	// Byte 4
	{"PCOUP",   TYPE_U8,0,FMT_02d},
	{"SINSTS",  TYPE_U24,0,FMT_05ld},
	{"SINSTS1", TYPE_U24,0,FMT_05ld},
	{"SINSTS2", TYPE_U24,0,FMT_05ld},
	{"SINSTS3", TYPE_U24,0,FMT_05ld},
	{"SMAXSN",   TYPE_SDMYhmsU24,0,FMT_05ld},
	{"SMAXSN1",  TYPE_SDMYhmsU24,0,FMT_05ld},
	{"SMAXSN2",  TYPE_SDMYhmsU24,0,FMT_05ld},
	// Byte 5
	{"SMAXSN3",  TYPE_SDMYhmsU24,0,FMT_05ld},
	{"SMAXSN?1", TYPE_SDMYhmsU24,ATTRIBUTE_REGULAR_EXPR,FMT_05ld}, /* Notice : generic '?' because of '_' instead of '-' in ISKRA counter */
	{"SMAXSN1?1",TYPE_SDMYhmsU24,ATTRIBUTE_REGULAR_EXPR,FMT_05ld},
	{"SMAXSN2?1",TYPE_SDMYhmsU24,ATTRIBUTE_REGULAR_EXPR,FMT_05ld},
	{"SMAXSN3?1",TYPE_SDMYhmsU24,ATTRIBUTE_REGULAR_EXPR,FMT_05ld},
	{"SINSTI",  TYPE_U24,0,FMT_05ld},
	{"SMAXIN",  TYPE_SDMYhmsU24,0,FMT_05ld},
	{"SMAXIN-1",TYPE_SDMYhmsU24,0,FMT_05ld},
	// Byte 6
	{"CCASN",   TYPE_SDMYhmsU24,0,FMT_05ld},
	{"CCASN?1", TYPE_SDMYhmsU24,ATTRIBUTE_REGULAR_EXPR,FMT_05ld}, /* Notice : generic '?' because of '_' instead of '-' in ISKRA counter */
	{"CCAIN",   TYPE_SDMYhmsU24,0,FMT_05ld},
	{"CCAIN?1", TYPE_SDMYhmsU24,ATTRIBUTE_REGULAR_EXPR,FMT_05ld}, /* Notice : generic '?' because of '_' instead of '-' in ISKRA counter */
	{"UMOY1",   TYPE_SDMYhmsU16,0,FMT_03d},
	{"UMOY2",   TYPE_SDMYhmsU16,0,FMT_03d},
	{"UMOY3",   TYPE_SDMYhmsU16,0,FMT_03d},
	{"STGE",    TYPE_BF32xbe,0,FMT_UNDEF},
	// Byte 7
	{"DPM1",    TYPE_SDMYhmsU8,0,FMT_02d},
	{"FPM1",    TYPE_SDMYhmsU8,0,FMT_02d},
	{"DPM2",    TYPE_SDMYhmsU8,0,FMT_02d},
	{"FPM2",    TYPE_SDMYhmsU8,0,FMT_02d},
	{"DPM3",    TYPE_SDMYhmsU8,0,FMT_02d},
	{"FPM3",    TYPE_SDMYhmsU8,0,FMT_02d},
	{"MSG1",    TYPE_CSTRING,0,FMT_s},
	{"MSG2",    TYPE_CSTRING,0,FMT_s},
	// Byte 8
	{"PRM",     TYPE_CSTRING,0,FMT_s },
	{"RELAIS",  TYPE_BF8d,0,FMT_03d },
	{"NTARF",   TYPE_U8,0,FMT_02d },
	{"NJOURF",  TYPE_U8,0,FMT_02d },
	{"NJOURF+1",TYPE_U8,0,FMT_02d },
	{"PJOURF+1",TYPE_11hhmmSSSS,0,FMT_UNDEF },
	{"PPOINTE", TYPE_11hhmmSSSS,0,FMT_UNDEF }
};

// ** Concentrateur Teleport / Compteur Bleu Electronique CT/CBE ************
// **************************************************************************
#define CTCBE_FIELDS_MAX_NUMBER 36
const TIC_expected_field_t CTCBE_expected_fields[CTCBE_FIELDS_MAX_NUMBER]=
{
	/* Should be ordened compared to real stream to optimize parsing (cf no_field which is not re-initialized )*/
	// Byte 0
	{"ADIR1",   TYPE_U16,0,FMT_03d},
	{"ADIR2",   TYPE_U16,0,FMT_03d},
	{"ADIR3",   TYPE_U16,0,FMT_03d},
	{"ADCO",    TYPE_CSTRING,0,FMT_s},
	{"OPTARIF", TYPE_CSTRING,0,FMT_s},
	{"ISOUSC",  TYPE_U8,0,FMT_02d},
	{"BASE",    TYPE_U32,0,FMT_09ld},
	{"HCHC",    TYPE_U32,0,FMT_09ld},
	// Byte 1
	{"HCHP",    TYPE_U32,0,FMT_09ld},
	{"EJPHN",   TYPE_U32,0,FMT_09ld},
	{"EJPHPM",	TYPE_U32,0,FMT_09ld},
	{"BBRHCJB",	TYPE_U32,0,FMT_09ld},
	{"BBRHPJB",	TYPE_U32,0,FMT_09ld},
	{"BBRHCJW", TYPE_U32,0,FMT_09ld},
	{"BBRHPJW",	TYPE_U32,0,FMT_09ld},
	{"BBRHCJR", TYPE_U32,0,FMT_09ld},
	// Byte 2
	{"BBRHPJR", TYPE_U32,0,FMT_09ld},
	{"PEJP",    TYPE_U8,0,FMT_02d},
	{"GAZ",    	TYPE_U32,0,FMT_07ld},
	{"AUTRE",   TYPE_U32,0,FMT_07ld},
	{"PTEC",    TYPE_CSTRING,0,FMT_s},
	{"DEMAIN",  TYPE_CSTRING,0,FMT_s},
	{"IINST",   TYPE_U16,0,FMT_03d},
	{"IINST1",  TYPE_U16,0,FMT_03d},
	// Byte 3
	{"IINST2",	TYPE_U16,0,FMT_03d},
	{"IINST3",  TYPE_U16,0,FMT_03d},
	{"ADPS",    TYPE_U16,0,FMT_03d},
	{"IMAX",    TYPE_U16,0,FMT_03d},
	{"IMAX1",   TYPE_U16,0,FMT_03d},
	{"IMAX2",   TYPE_U16,0,FMT_03d},
	{"IMAX3",   TYPE_U16,0,FMT_03d},
	{"PMAX",    TYPE_U32,0,FMT_05ld},
	// Byte 4
	{"PAPP",    TYPE_U32,0,FMT_05ld},
	{"HHPHC",   TYPE_CHAR,0,FMT_c},
	{"MOTDETAT",TYPE_CSTRING,0,FMT_s},
	{"PPOT",    TYPE_U8,0,FMT_02X}
};


// ** Compteur Jaune Electronique *******************************************
// **************************************************************************
#define CJE_FIELDS_MAX_NUMBER 37
const TIC_expected_field_t CJE_expected_fields[CJE_FIELDS_MAX_NUMBER]=
{
	/* Should be ordened compared to real stream to optimize parsing (cf no_field which is not re-initialized )*/
	// Byte 0
	{"JAUNE",	TYPE_hmDM,0,FMT_UNDEF},		// {hh:mn:jj:mm}:pt:dp:abcde:kp
	{"JAUNE",	TYPE_CSTRING,ATTRIBUTE_IS_SUBFIELD,FMT_s},	// pt
	{"JAUNE",	TYPE_CSTRING,ATTRIBUTE_IS_SUBFIELD,FMT_s},  // dp
	{"JAUNE",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_05ld},	// abcde
	{"JAUNE",	TYPE_U8,ATTRIBUTE_IS_SUBFIELD,FMT_02d},		// kp
	{"ENERG",	TYPE_6U24,0,FMT_06ld},		// 111111:222222:...:666666
	{"ENERG",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_06ld},		// 222222
	{"ENERG",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_06ld},		// 333333
	// Byte 1
	{"ENERG",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_06ld},		// 444444
	{"ENERG",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_06ld},		// 555555
	{"ENERG",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_06ld},		// 666666
	{"PERCC",	TYPE_DMh,0,FMT_UNDEF},		// jj:mm:hh{:cg}
	{"PERCC",	TYPE_U8,ATTRIBUTE_IS_SUBFIELD,FMT_02d},		// cg
	{"PMAXC",	TYPE_4U24,0,FMT_05ld},		// 11111:22222:...:44444
	{"PMAXC",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_05ld},		// 22222
	{"PMAXC",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_05ld},		// 33333
	// Byte 2
	{"PMAXC",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_05ld},		// 44444
	{"TDEPA",	TYPE_4U24,0,FMT_05ld},		// 11111:22222:...:44444
	{"TDEPA",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_05ld},		// 22222
	{"TDEPA",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_05ld},		// 33333
	{"TDEPA",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_05ld},		// 44444
	{"PERCP",	TYPE_DMh,0,FMT_UNDEF},		// {jj:mm:hh}:cg
	{"PERCP",	TYPE_U8,ATTRIBUTE_IS_SUBFIELD,FMT_02d},		// cg
	{"PMAXP",	TYPE_4U24,0,FMT_05ld},		// 11111:22222:...:44444
	// Byte 3
	{"PMAXP",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_05ld},		// 22222
	{"PMAXP",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_05ld},		// 33333
	{"PMAXP",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_05ld},		// 44444
	{"PSOUSC",	TYPE_4U24,0,FMT_05ld},		// 11111:22222:...:44444
	{"PSOUSC",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_05ld},		// 22222
	{"PSOUSC",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_05ld},		// 33333
	{"PSOUSC",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_05ld},		// 44444
	{"PSOUSP",	TYPE_4U24,0,FMT_05ld},		// 11111:22222:...:44444
	// Byte 4
	{"PSOUSP",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_05ld},		// 22222
	{"PSOUSP",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_05ld},		// 33333
	{"PSOUSP",	TYPE_U24,ATTRIBUTE_IS_SUBFIELD,FMT_05ld},		// 44444
	{"FCOU",	TYPE_hm,0,FMT_UNDEF},		// {hh:mn}:dd
	{"FCOU",	TYPE_U8,ATTRIBUTE_IS_SUBFIELD,FMT_02d}		// dd
};

// ** Interface Client Emeraude *********************************************
// **************************************************************************
#define ICE_FIELDS_MAX_NUMBER 45
const TIC_expected_field_t ICE_expected_fields[ICE_FIELDS_MAX_NUMBER]=
{
	/* Should be ordened compared to real stream to optimize parsing (cf no_field which is not re-initialized )*/
	// Byte 0
	{"CONTRAT",	TYPE_CSTRING,0,FMT_s},
	{"DATECOUR",TYPE_DMYhms,0,FMT_UNDEF},
	{"DATE",TYPE_DMYhms,0,FMT_UNDEF}, /* A la place de DATECOUR sur compteurs v2.4 */
	{"EA",		TYPE_U24,0,FMT_05ld_Wh},
	{"ERP",		TYPE_U24,0,FMT_05ld_varh},
	{"PTCOUR",	TYPE_CSTRING,0,FMT_s},
	{"PREAVIS",	TYPE_CSTRING,ATTRIBUTE_MULTI_OCCURENCE_FIELD,FMT_s},
	{"MODE",	TYPE_EMPTY,0,FMT_s},
	// Byte 1
	// TODO: Manage PAX format with a complémentary byte info see documentation
	//       Indicateur de puissance tronqué ?
	{"DATEPA1",	TYPE_DMYhms,0,FMT_UNDEF},
	{"PA1",		TYPE_U16,0,FMT_d_kW},
	{"DATEPA2",	TYPE_DMYhms,0,FMT_UNDEF},
	{"PA2",		TYPE_U16,0,FMT_d_kW},
	{"DATEPA3",	TYPE_DMYhms,0,FMT_UNDEF},
	{"PA3",		TYPE_U16,0,FMT_d_kW},
	{"DATEPA4",	TYPE_DMYhms,0,FMT_UNDEF},
	{"PA4",		TYPE_U16,0,FMT_d_kW},
	// Byte 2
	{"DATEPA5",	TYPE_DMYhms,0,FMT_UNDEF},
	{"PA5",		TYPE_U16,0,FMT_d_kW},
	{"DATEPA6",	TYPE_DMYhms,0,FMT_UNDEF},
	{"PA6",		TYPE_U16,0,FMT_d_kW},
    // Ce champs variable permet d'ignorer et "switcher" sur le descripteur ICE/Energie/Periode
	{"*p*",	TYPE_U24,ATTRIBUTE_ICE_pp1_FIELD,FMT_05ld},
	//{"*p*",	TYPE_U24,ATTRIBUTE_NOT_MANAGED_FIELD,FMT_05ld},
	{"KDC",		TYPE_U8,0,FMT_d_percent},
	{"KDCD",	TYPE_U8,0,FMT_d_percent},
	{"TGPHI",	TYPE_FLOAT,0,FMT_05_2f}, /* Optionnellement ici sur compteurs v2.4 */
	// Byte 3
	{"PSP",		TYPE_U16,0,FMT_d_kW},
	{"PSPM",	TYPE_U16,0,FMT_d_kW},
	{"PSHPH",	TYPE_U16,0,FMT_d_kW},
	{"PSHPD",	TYPE_U16,0,FMT_d_kW},
	{"PSHCH",	TYPE_U16,0,FMT_d_kW},
	{"PSHCD",	TYPE_U16,0,FMT_d_kW},
	{"PSHPE",	TYPE_U16,0,FMT_d_kW},
	{"PSHCE",	TYPE_U16,0,FMT_d_kW},
	// Byte 4
	{"PSJA",	TYPE_U16,0,FMT_d_kW},
	{"PSHH",	TYPE_U16,0,FMT_d_kW},
	{"PSHD",	TYPE_U16,0,FMT_d_kW},
	{"PSHM",	TYPE_U16,0,FMT_d_kW},
	{"PSDSM",	TYPE_U16,0,FMT_d_kW},
	{"PSSCM",	TYPE_U16,0,FMT_d_kW}, /* Optionnellement ici sur compteurs v2.4 */
	{"MODE",	TYPE_EMPTY,0,FMT_s},
	{"PA1MN",	TYPE_U16,0,FMT_d_kW},
	// Byte 5
	{"PA10MN",	TYPE_U16,0,FMT_d_kW},
	{"PREA1MN",	TYPE_I16,0,FMT_d_kvar},
	{"PREA10MN",TYPE_I16,0,FMT_d_kvar},
	{"TGPHI",	TYPE_FLOAT,0,FMT_05_2f},
	{"U10MN",	TYPE_U16,0,FMT_d_V}
};

#define ICE_p_FIELDS_MAX_NUMBER  (3 + 3 + (14*3))
const TIC_expected_field_t ICE_p_expected_fields[ICE_p_FIELDS_MAX_NUMBER]=
{
	//Byte 0
	{"DEBUTp",	TYPE_DMYhms,0,FMT_UNDEF,0},
	{"FINp",	TYPE_DMYhms,0,FMT_UNDEF,6},
	{"CAFp",	TYPE_U16,0,FMT_05d,12},

	{"DATEEAp",TYPE_DMYhms,ATTRIBUTE_NON_TIC_FIELD,FMT_UNDEF,14},
	{"EApP",	TYPE_U24,0,FMT_ld_kWh,20},
	{"EApPM",	TYPE_U24,0,FMT_ld_kWh,23},
	{"EApHCE",	TYPE_U24,0,FMT_ld_kWh,26},
	{"EApHCH",	TYPE_U24,0,FMT_ld_kWh,29},
	//Byte 1
	{"EApHH",	TYPE_U24,0,FMT_ld_kWh,32},
	{"EApHCD",	TYPE_U24,0,FMT_ld_kWh,35},
	{"EApHD",	TYPE_U24,0,FMT_ld_kWh,38},
	{"EApJA",	TYPE_U24,0,FMT_ld_kWh,41},
	{"EApHPE",	TYPE_U24,0,FMT_ld_kWh,44},
	{"EApHPH",	TYPE_U24,0,FMT_ld_kWh,47},
	{"EApHPD",	TYPE_U24,0,FMT_ld_kWh,50},
	{"EApSCM",	TYPE_U24,0,FMT_ld_kWh,53},
	// Byte 2
	{"EApHM",	TYPE_U24,0,FMT_ld_kWh,56},
	{"EApDSM",	TYPE_U24,0,FMT_ld_kWh,59},

	{"DATEERPp",TYPE_DMYhms,ATTRIBUTE_NON_TIC_FIELD,FMT_UNDEF,62},
	{"ERPpP",	TYPE_U24,0,FMT_ld_kvarh,68},
	{"ERPpPM",	TYPE_U24,0,FMT_ld_kvarh,71},
	{"ERPpHCE",	TYPE_U24,0,FMT_ld_kvarh,74},
	{"ERPpHCH",	TYPE_U24,0,FMT_ld_kvarh,77},
	{"ERPpHH",	TYPE_U24,0,FMT_ld_kvarh,80},
	// Byte 3
	{"ERPpHCD",	TYPE_U24,0,FMT_ld_kvarh,83},
	{"ERPpHD",	TYPE_U24,0,FMT_ld_kvarh,86},
	{"ERPpJA",	TYPE_U24,0,FMT_ld_kvarh,89},
	{"ERPpHPE",	TYPE_U24,0,FMT_ld_kvarh,92},
	{"ERPpHPH",	TYPE_U24,0,FMT_ld_kvarh,95},
	{"ERPpHPD",	TYPE_U24,0,FMT_ld_kvarh,98},
	{"ERPpSCM",	TYPE_U24,0,FMT_ld_kvarh,101},
	{"ERPpHM",	TYPE_U24,0,FMT_ld_kvarh,104},
	// Byte 4
	{"ERPpDSM",	TYPE_U24,0,FMT_ld_kvarh,107},

	{"DATEERNp",TYPE_DMYhms,ATTRIBUTE_NON_TIC_FIELD,FMT_UNDEF,110},
	{"ERNpP",	TYPE_U24,0,FMT_ld_kvarh,116},
	{"ERNpPM",	TYPE_U24,0,FMT_ld_kvarh,119},
	{"ERNpHCE",	TYPE_U24,0,FMT_ld_kvarh,122},
	{"ERNpHCH",	TYPE_U24,0,FMT_ld_kvarh,125},
	{"ERNpHH",	TYPE_U24,0,FMT_ld_kvarh,128},
	{"ERNpHCD",	TYPE_U24,0,FMT_ld_kvarh,131},
	// Byte 5
	{"ERNpHD",	TYPE_U24,0,FMT_ld_kvarh,134},
	{"ERNpJA",	TYPE_U24,0,FMT_ld_kvarh,137},
	{"ERNpHPE",	TYPE_U24,0,FMT_ld_kvarh,140},
	{"ERNpHPH",	TYPE_U24,0,FMT_ld_kvarh,143},
	{"ERNpHPD",	TYPE_U24,0,FMT_ld_kvarh,146},
	{"ERNpSCM",	TYPE_U24,0,FMT_ld_kvarh,149},
	{"ERNpHM",	TYPE_U24,0,FMT_ld_kvarh,152},
	{"ERNpDSM",	TYPE_U24,0,FMT_ld_kvarh,155}
	// Byte 6
};

#define ICE_p1_FIELDS_MAX_NUMBER (3 + 3 + (14*3))
const TIC_expected_field_t ICE_p1_expected_fields[ICE_p1_FIELDS_MAX_NUMBER]=
{
	//Byte 0
	{"DEBUTp1",	TYPE_DMYhms,0,FMT_UNDEF,0},
	{"FINp1",	TYPE_DMYhms,0,FMT_UNDEF,6},
	{"CAFp1",	TYPE_U16,0,FMT_05d,12},

	{"DATEEAp1",TYPE_DMYhms,ATTRIBUTE_NON_TIC_FIELD,FMT_UNDEF,14},
	{"EAp1P",	TYPE_U24,0,FMT_ld_kWh,20},
	{"EAp1PM",	TYPE_U24,0,FMT_ld_kWh,23},
	{"EAp1HCE",	TYPE_U24,0,FMT_ld_kWh,26},
	{"EAp1HCH",	TYPE_U24,0,FMT_ld_kWh,29},
	//Byte 1
	{"EAp1HH",	TYPE_U24,0,FMT_ld_kWh,32},
	{"EAp1HCD",	TYPE_U24,0,FMT_ld_kWh,35},
	{"EAp1HD",	TYPE_U24,0,FMT_ld_kWh,38},
	{"EAp1JA",	TYPE_U24,0,FMT_ld_kWh,41},
	{"EAp1HPE",	TYPE_U24,0,FMT_ld_kWh,44},
	{"EAp1HPH",	TYPE_U24,0,FMT_ld_kWh,47},
	{"EAp1HPD",	TYPE_U24,0,FMT_ld_kWh,50},
	{"EAp1SCM",	TYPE_U24,0,FMT_ld_kWh,53},
	// Byte 2
	{"EAp1HM",	TYPE_U24,0,FMT_ld_kWh,56},
	{"EAp1DSM",	TYPE_U24,0,FMT_ld_kWh,59},

	{"DATEERPp1",TYPE_DMYhms,ATTRIBUTE_NON_TIC_FIELD,FMT_UNDEF,62},
	{"ERPp1P",	TYPE_U24,0,FMT_ld_kvarh,68},
	{"ERPp1PM",	TYPE_U24,0,FMT_ld_kvarh,71},
	{"ERPp1HCE",TYPE_U24,0,FMT_ld_kvarh,74},
	{"ERPp1HCH",TYPE_U24,0,FMT_ld_kvarh,77},
	{"ERPp1HH",	TYPE_U24,0,FMT_ld_kvarh,80},
	// Byte 3
	{"ERPp1HCD",TYPE_U24,0,FMT_ld_kvarh,83},
	{"ERPp1HD",	TYPE_U24,0,FMT_ld_kvarh,86},
	{"ERPp1JA",	TYPE_U24,0,FMT_ld_kvarh,89},
	{"ERPp1HPE",TYPE_U24,0,FMT_ld_kvarh,92},
	{"ERPp1HPH",TYPE_U24,0,FMT_ld_kvarh,95},
	{"ERPp1HPD",TYPE_U24,0,FMT_ld_kvarh,98},
	{"ERPp1SCM",TYPE_U24,0,FMT_ld_kvarh,101},
	{"ERPp1HM",	TYPE_U24,0,FMT_ld_kvarh,104},
	// Byte 4
	{"ERPp1DSM",TYPE_U24,0,FMT_ld_kvarh,107},

	{"DATEERNp1",TYPE_DMYhms,ATTRIBUTE_NON_TIC_FIELD,FMT_UNDEF,110},
	{"ERNp1P",	TYPE_U24,0,FMT_ld_kvarh,116},
	{"ERNp1PM",	TYPE_U24,0,FMT_ld_kvarh,119},
	{"ERNp1HCE",TYPE_U24,0,FMT_ld_kvarh,122},
	{"ERNp1HCH",TYPE_U24,0,FMT_ld_kvarh,125},
	{"ERNp1HH",	TYPE_U24,0,FMT_ld_kvarh,128},
	{"ERNp1HCD",TYPE_U24,0,FMT_ld_kvarh,131},
	// Byte 5
	{"ERNp1HD",	TYPE_U24,0,FMT_ld_kvarh,134},
	{"ERNp1JA",	TYPE_U24,0,FMT_ld_kvarh,137},
	{"ERNp1HPE",TYPE_U24,0,FMT_ld_kvarh,140},
	{"ERNp1HPH",TYPE_U24,0,FMT_ld_kvarh,143},
	{"ERNp1HPD",TYPE_U24,0,FMT_ld_kvarh,146},
	{"ERNp1SCM",TYPE_U24,0,FMT_ld_kvarh,149},
	{"ERNp1HM",	TYPE_U24,0,FMT_ld_kvarh,152},
	{"ERNp1DSM",TYPE_U24,0,FMT_ld_kvarh,155}
	// Byte 6
};


// ** Compteur PMEPMI : "TIC standard" frame *********************************
// **************************************************************************
#define PMEPMI_FIELDS_MAX_NUMBER 76
const TIC_expected_field_t PMEPMI_expected_fields[PMEPMI_FIELDS_MAX_NUMBER]=
{
	/* Should be ordened compared to real stream to optimize parsing (cf no_field which is not re-initialized )*/
	//Byte 0
	{"TRAME",   TYPE_E_DIV,0,FMT_s}, /* Uniquement Palier 2013 */
	{"ADS",     TYPE_HEXSTRING,0,FMT_UNDEF}, /* Uniquement Palier 2013 */
	{"MESURES1",TYPE_E_CONTRAT,0,FMT_s},
	{"DATE",    TYPE_DMYhms,0,FMT_UNDEF},
	{"EA_s",	TYPE_U24,0,FMT_ld_Wh},
	{"ER+_s",	TYPE_U24,0,FMT_ld_varh},
	{"ER-_s",   TYPE_U24,0,FMT_ld_varh},
	{"EAPP_s",	TYPE_U24,0,FMT_ld_VAh},
	//Byte 1
	{"EA_i",    TYPE_U24,0,FMT_ld_Wh},
	{"ER+_i",   TYPE_U24,0,FMT_ld_varh},
	{"ER-_i",   TYPE_U24,0,FMT_ld_varh},
	{"EAPP_i",	TYPE_U24,0,FMT_ld_VAh},
	{"PTCOUR1", TYPE_E_PT,0,FMT_s},
	{"TARIFDYN",TYPE_E_DIV,0,FMT_s},
	{"ETATDYN1",TYPE_E_PT,0,FMT_s},
	{"PREAVIS1",TYPE_E_PT,0,FMT_PREAVIS_PT},
    //Byte 2
    {"TDYN1CD", TYPE_tsDMYhms_E_PT,0,FMT_UNDEF},
    {"TDYN1CF", TYPE_tsDMYhms_E_PT,0,FMT_UNDEF},
    {"TDYN1FD", TYPE_tsDMYhms_E_PT,0,FMT_UNDEF},
    {"TDYN1FF", TYPE_tsDMYhms_E_PT,0,FMT_UNDEF},
	{"MODE",	TYPE_E_DIV,0,FMT_s},
	{"CONFIG",	TYPE_E_DIV,0,FMT_s},
	{"DATEPA1",	TYPE_DMYhms,0,FMT_UNDEF},
	{"PA1_s",	TYPE_U16,0,FMT_d_kW},
	// Byte 3
	{"PA1_i",	TYPE_U16,0,FMT_d_kW},
	{"DATEPA2",	TYPE_tsDMYhms,0,FMT_UNDEF},
	{"PA2_s",	TYPE_U16,0,FMT_d_kW},
	{"PA2_i",	TYPE_U16,0,FMT_d_kW},
	{"DATEPA3",	TYPE_tsDMYhms,0,FMT_UNDEF},
	{"PA3_s",	TYPE_U16,0,FMT_d_kW},
	{"PA3_i",	TYPE_U16,0,FMT_d_kW},
	{"DATEPA4",	TYPE_tsDMYhms,0,FMT_UNDEF},
	//Byte 4
	{"PA4_s",	TYPE_U16,0,FMT_d_kW},
	{"PA4_i",	TYPE_U16,0,FMT_d_kW},
	{"DATEPA5",	TYPE_tsDMYhms,0,FMT_UNDEF},
	{"PA5_s",	TYPE_U16,0,FMT_d_kW},
	{"PA5_i",	TYPE_U16,0,FMT_d_kW},
	{"DATEPA6",	TYPE_tsDMYhms,0,FMT_UNDEF},
	{"PA6_s",	TYPE_U16,0,FMT_d_kW},
	{"PA6_i",	TYPE_U16,0,FMT_d_kW},
	//Byte 5
	{"DebP",    TYPE_tsDMYhms,0,FMT_UNDEF},
	{"EAP_s",	TYPE_U24,0,FMT_d_kWh},
	{"EAP_i",  	TYPE_U24,0,FMT_d_kWh},
	{"ER+P_s",  TYPE_U24,0,FMT_d_kvarh},
	{"ER-P_s",  TYPE_U24,0,FMT_d_kvarh},
	{"ER+P_i",  TYPE_U24,0,FMT_d_kvarh},
	{"ER-P_i",  TYPE_U24,0,FMT_d_kvarh},
	{"DebP-1",  TYPE_tsDMYhms,0,FMT_UNDEF},
	//Byte 6
	{"FinP-1",  TYPE_tsDMYhms,0,FMT_UNDEF},
	{"EaP-1_s",	TYPE_U24,ATTRIBUTE_NOT_LBL_CASE_SENSITIVE,FMT_d_kWh}, // Found meter with a Upcase => A
	{"EaP-1_i",	TYPE_U24,ATTRIBUTE_NOT_LBL_CASE_SENSITIVE,FMT_d_kWh}, // Found meter with a Upcase => A
	{"ER+P-1_s",TYPE_U24,0,FMT_d_kvarh},
	{"ER-P-1_s",TYPE_U24,0,FMT_d_kvarh},
	{"ER+P-1_i",TYPE_U24,0,FMT_d_kvarh},
	{"ER-P-1_i",TYPE_U24,0,FMT_d_kvarh},
	{"PS",	    TYPE_U24_E_DIV,0,FMT_UNDEF},
	//Byte 7
	{"PREAVIS", TYPE_E_DIV,0,FMT_s},
	{"PA1MN",   TYPE_U16,0,FMT_d_kW},
	{"PMAX_s",	TYPE_U24_E_DIV,0,FMT_UNDEF},
	{"PMAX_i",	TYPE_U24_E_DIV,0,FMT_UNDEF},
	{"TGPHI_s",	TYPE_FLOAT,0,FMT_05_2f},
	{"TGPHI_i",	TYPE_FLOAT,0,FMT_05_2f},
	{"MESURES2",TYPE_E_CONTRAT,0,FMT_s},
	{"PTCOUR2",	TYPE_E_PT,0,FMT_s},
    //Byte 8
	{"ETATDYN2",TYPE_E_PT,0,FMT_s},
	{"PREAVIS2",TYPE_E_PT,0,FMT_PREAVIS_PT},
	{"TDYN2CD", TYPE_tsDMYhms_E_PT,0,FMT_UNDEF},
    {"TDYN2CF", TYPE_tsDMYhms_E_PT,0,FMT_UNDEF},
    {"TDYN2FD", TYPE_tsDMYhms_E_PT,0,FMT_UNDEF},
    {"TDYN2FF", TYPE_tsDMYhms_E_PT,0,FMT_UNDEF},
	{"DebP_2",  TYPE_tsDMYhms,0,FMT_UNDEF},
	{"EaP_s2",	TYPE_U24,ATTRIBUTE_NOT_LBL_CASE_SENSITIVE,FMT_d_kWh}, // Found meter with a Upcase => A
	//Byte 9
	{"DebP-1_2",TYPE_tsDMYhms,0,FMT_UNDEF},
	{"FinP-1_2",TYPE_tsDMYhms,0,FMT_UNDEF},
	{"EaP-1_s2",TYPE_U24,ATTRIBUTE_NOT_LBL_CASE_SENSITIVE,FMT_d_kWh}, // Found meter with a Upcase => A
	{"_DDMES1_",TYPE_U24,0,FMT_d_s}
};

// ** Table of managed meter types ****************************************
// **************************************************************************
const TIC_meter_descriptor_t tic_meter_descriptor[TIC_NB_DESC_TYPE] =
{
	{MT_UNKNOWN,	UNKNOWN_expected_fields,	UNKNOWN_FIELDS_MAX_NUMBER,0x01 /* Undef */},
	{MT_CT, 		CTCBE_expected_fields,		CTCBE_FIELDS_MAX_NUMBER,  0x08 /* ADCO */},
	{MT_CBEMM, 		CTCBE_expected_fields,		CTCBE_FIELDS_MAX_NUMBER,  0x08 /* ADCO */},
	{MT_CBEMM_ICC, 	CTCBE_expected_fields,		CTCBE_FIELDS_MAX_NUMBER,  0x08 /* ADCO */},
	{MT_CBETM, 		CTCBE_expected_fields,		CTCBE_FIELDS_MAX_NUMBER,  0x08 /* ADCO */},
	{MT_CJE,		CJE_expected_fields,		CJE_FIELDS_MAX_NUMBER,    0x01 /* JAUNE */},
	{MT_ICE,		ICE_expected_fields,		ICE_FIELDS_MAX_NUMBER,    0x07 /* CONTRAT | DATECOUR | DATE */},
	{MT_STD,		STD_expected_fields,		STD_FIELDS_MAX_NUMBER,    0x01 /* ADSC */},
	{MT_PMEPMI,		PMEPMI_expected_fields,		PMEPMI_FIELDS_MAX_NUMBER, 0x04 /* MESURES1 */},
	{MT_PMEPMI13,	PMEPMI_expected_fields,		PMEPMI_FIELDS_MAX_NUMBER, 0x02 /* ADS */},
	{MT_NULL,		NULL, 0}, // End of managed Meter Begin of complementary managed descriptor
	{MT_ICE_p,		ICE_p_expected_fields,		ICE_p_FIELDS_MAX_NUMBER,  0x01 /* DEBUTp */},
	{MT_ICE_p1,		ICE_p1_expected_fields,		ICE_p1_FIELDS_MAX_NUMBER, 0x01 /* DEBUTp1 */}
};


//==============================================================================
// ENUMERATION MANAGEMENT GENERALIZED FOR PMEPMI fields ------------------------

TABLE_E_COMMON_DECLARATION;
TABLE_E_DIV_DECLARATION;
TABLE_E_CONTRAT_DECLARATION;
TABLE_E_PT_DECLARATION;
TABLE_E_STD_CONTRAT_DECLARATION;
TABLE_E_STD_PT_DECLARATION;


//----------------------------------------------------------------------------
unsigned char tic_enum_len(unsigned char * the_enum) {
	unsigned char head = *the_enum;

	if (head & ENUM_IS_STRING_BIT) { // Enum is a string
		head &= ~ENUM_IS_STRING_BIT;
		return ((head > TABLES_E_MAX_STR_SZ ? TABLES_E_MAX_STR_SZ : head) + 1);
	}

	return 1;
}

int tic_enum_cmp(unsigned char * e1, unsigned char * e2) {
	// 0 enums are aquals, !=0 they are differents

	if (*e1 != *e2) return(0xFFFF); // Either the result will be result of memcmp (difference between first two different bytes)

	unsigned char head = *e1;

	if (head & ENUM_IS_STRING_BIT) { // Enum is a string
		head &= ~ENUM_IS_STRING_BIT;
		return (memcmp(e1,e2,head));
	}
	return 0; // if here they are equals and coded on on byte
}

unsigned char tic_enum_changed(unsigned char * crit, unsigned char * before, unsigned char * after) {
	// Verify if an enum as changed with following rule:
	// changed if changed and (after or before is crit or crit is ANY)
	// return 1 if accepted change, 0 either

	if (tic_enum_cmp(after,before)) {
		if (*crit == E_COMMON_ANY) return 1;
		if (tic_enum_cmp(crit,before) == 0) return 1; // Originally corresponding to criteria
		if (tic_enum_cmp(crit,after) == 0) return 1;  // Changed to criteria
	}

	return 0; // No accepted change

}

// Return index of string if found in table values
// table MUST BE lexicographically sorted in ascending order
static unsigned char _tic_enum_compress(
	unsigned char * pt_str,
	const char * table,
	const unsigned char table_sz,
	const unsigned char table_str_sz,
	unsigned char str_if_not_found,
	unsigned char *dest_buf ) {

	signed char /*min, max, */mid;
	signed char diff;

	// Lookup for enumerated common types ---------------------------
	for (mid = 0; mid < TABLE_E_COMMON_SZ; mid++) {
		if (strcmp((char *)TABLE_E_COMMON[mid],(char *)pt_str) == 0) {
			*dest_buf = mid;
			return 1;
		}
	}

	// Verify that available enum table exists
	if (table_sz == 0) {
		*dest_buf = E_COMMON_NOT_FOUND;
		return 1;
	}

	// Dichotomic lookup in table for real enumerated type ---------------------------
//	diff = 1;
//	min = 0; max = table_sz - 1;
//	while (diff && (min <= max)) {
//		mid = (max + min) / 2;
//		diff = strncmp((char*)(table + (mid * table_str_sz)), (char *)pt_str, table_str_sz);
//		if      (diff > 0) { max = mid - 1; }
//		else if (diff < 0) { min = mid + 1; }
//	}
	// No more dichotomic search to allow unsorted list so that new enums can be added at the end
	diff = 1;
	for (mid = 0; ((mid <= table_sz) && diff); mid++) {
		diff = strncmp((char*)(table + (mid * table_str_sz)), (char *)pt_str, table_str_sz);
	}
	// Process return values according to parameters
	if (diff == 0) {
		mid--;
		*dest_buf = mid + TABLE_E_COMMON_SZ; // All valids enum start after the standard E_COMMON
		return(1);
	}

	// Finally prepare for trimmed lookup of the string.
	// First identify trimed string:
	unsigned char * pt_str_start=pt_str;
	while ((*pt_str_start == ' ') && (*pt_str_start != '\0'))
		pt_str_start++;
	unsigned char * pt_str_tmp=pt_str_start;
	unsigned char * pt_str_end=pt_str_start;
	while (*pt_str_tmp != '\0') {
		if (*pt_str_tmp != ' ') {
			pt_str_end=pt_str_tmp+1;
		}
		pt_str_tmp++;
	}
	// Set end of string
	if (pt_str_start != pt_str_end) {
		*pt_str_end = '\0';
	}

	// New Dichotomic lookup of trimmed value in table for real enumerated type ---------------------------
//	diff = 1;
//	min = 0; max = table_sz - 1;
//	while (diff && (min <= max)) {
//		mid = (max + min) / 2;
//		diff = strncmp((char*)(table + (mid * table_str_sz)), (char *)pt_str_start, table_str_sz);
//		if      (diff > 0) { max = mid - 1; }
//		else if (diff < 0) { min = mid + 1; }
//	}

	// No more dichotomic search to allow unsorted list so that new enums can be added at the end
	diff = 1;
	for (mid = 0; ((mid <= table_sz) && diff); mid++) {
		diff = strncmp((char*)(table + (mid * table_str_sz)), (char *)pt_str_start, table_str_sz);
	}

	// Process return values according to parameters
	if (diff == 0) {
		mid--;
		*dest_buf = mid + TABLE_E_COMMON_SZ; // All valids enum start after the standard E_COMMON
		return(1);
	}

	if (! str_if_not_found) {
		*dest_buf = E_COMMON_NOT_FOUND;
		return(1);
	}

	// NOTE:
	//  If finally not found , we return exactly the original string, not the trimmed one
	//  Could choose to send the not trimmed one:
	//   Use pt_str either than pt_str_start and
	//   put back the last white blow)

	// Do not Put back last white in end of string
	//if (pt_str_start != pt_str_end) {
	//	*pt_str_end = ' ';
	//}

	// Return the original string in given buffer str_buf with correct Enum format
	dest_buf[0] = ENUM_IS_STRING_BIT; // Set is string for enum not found
	strcpy((char *)dest_buf + 1, (char *)pt_str_start);
	dest_buf[table_str_sz] = '\0';
	dest_buf[0] += strlen((char *)dest_buf + 1);
	return((dest_buf[0] & (~ENUM_IS_STRING_BIT)) + 1);

}

static unsigned char tmp_str[TABLES_E_MAX_STR_SZ]; // Memory permanent occupation : NOT very nice
static unsigned char * _tic_enum_uncompress(
		const char *table,
		const unsigned char table_sz,
		const unsigned char table_str_sz,
		unsigned char *the_enum) {
		unsigned char head = *the_enum;

	if (head & ENUM_IS_STRING_BIT) { // Enum is a string
		head &= ~ENUM_IS_STRING_BIT;
		head = (head > TABLES_E_MAX_STR_SZ ? TABLES_E_MAX_STR_SZ : head );
		// Beware that processor shoud process the value as soon as possible becaus it can be changed by following proceses
		strncpy((char *)tmp_str,(char*) (the_enum+1), head);
		tmp_str[head] = '\0';
		return(tmp_str);

	} else {
		if (head < TABLE_E_COMMON_SZ)
			return((unsigned char *)TABLE_E_COMMON[*the_enum]);
		else {
			head -= TABLE_E_COMMON_SZ;
			if (head < table_sz)
				return((unsigned char *)(table + (head * table_str_sz)));
			else
				return((unsigned char *)TABLE_E_COMMON[E_COMMON_NOT_FOUND]);
		}
	}
}

unsigned char tic_enum_compress(TIC_binary_type_t type, unsigned char * pt_str, unsigned char *dest_buf) {
	if  ((type == TYPE_E_PT) || (type == TYPE_tsDMYhms_E_PT))
		return (_tic_enum_compress(pt_str, (char*)TABLE_E_PT,  TABLE_E_PT_SZ,  TABLE_E_PT_STR_MAX_SZ,  1, dest_buf));

	else if ((type == TYPE_E_DIV) || (type == TYPE_U24_E_DIV))
		return (_tic_enum_compress(pt_str, (char*)TABLE_E_DIV, TABLE_E_DIV_SZ, TABLE_E_DIV_STR_MAX_SZ, 1, dest_buf));

	else if (type == TYPE_E_CONTRAT)
		return (_tic_enum_compress(pt_str, (char*)TABLE_E_CONTRAT, TABLE_E_CONTRAT_SZ, TABLE_E_CONTRAT_STR_MAX_SZ, 1, dest_buf));

	else if (type == TYPE_E_STD_PT)
		return (_tic_enum_compress(pt_str, (char*)TABLE_E_STD_PT, TABLE_E_STD_PT_SZ, TABLE_E_STD_PT_STR_MAX_SZ, 1, dest_buf));

	else if (type == TYPE_E_STD_CONTRAT)
		return (_tic_enum_compress(pt_str, (char*)TABLE_E_STD_CONTRAT, TABLE_E_STD_CONTRAT_SZ, TABLE_E_STD_CONTRAT_STR_MAX_SZ, 1, dest_buf));

	else {
		// Not correct enum type do nothing
	}
	return (0);
}

unsigned char * tic_enum_uncompress(TIC_binary_type_t type, unsigned char * the_enum) {
	if ((type == TYPE_E_PT) || (type == TYPE_tsDMYhms_E_PT))
		return(_tic_enum_uncompress((char*)TABLE_E_PT,  TABLE_E_PT_SZ,  TABLE_E_PT_STR_MAX_SZ, the_enum));

	else if ((type == TYPE_E_DIV) || (type == TYPE_U24_E_DIV))
		return(_tic_enum_uncompress((char*)TABLE_E_DIV, TABLE_E_DIV_SZ, TABLE_E_DIV_STR_MAX_SZ, the_enum));

	else if (type == TYPE_E_CONTRAT)
		return(_tic_enum_uncompress((char*)TABLE_E_CONTRAT, TABLE_E_CONTRAT_SZ, TABLE_E_CONTRAT_STR_MAX_SZ, the_enum));

	else if (type == TYPE_E_STD_PT)
		return(_tic_enum_uncompress((char*)TABLE_E_STD_PT, TABLE_E_STD_PT_SZ, TABLE_E_STD_PT_STR_MAX_SZ, the_enum));

	else if (type == TYPE_E_STD_CONTRAT)
		return(_tic_enum_uncompress((char*)TABLE_E_STD_CONTRAT, TABLE_E_STD_CONTRAT_SZ, TABLE_E_STD_CONTRAT_STR_MAX_SZ, the_enum));

	else {
		// Not correct enum type do nothing
	}
	tmp_str[0] = '\0';
	return(tmp_str);
}

// END OF ENUMERATION MANAGEMENT GENERALIZED FOR PMEPMI fields -----------------
//==============================================================================

static time_t tic_time_stamp_ref = 0;

//----------------------------------------------------------------------------
// Get a common reference timestamp that can be encodeby a two digit year
time_t tic_get_timestamp_ref() {

    if (tic_time_stamp_ref == 0) { // Calculate it once only to optimize processing times
        struct tm mytm;

        // Evaluate 01/01/2000 00:00:00 timestamp as reference for TIC
        mytm.tm_mday  = 1; /* day of the month - [1,31]  */
        mytm.tm_mon   = 0; /* months since January - [0,11]  */
        mytm.tm_year  = 2000 - 1900; /* years since 1900 for mktime */
        mytm.tm_hour  = 0; /* hours after the midnight   - [0,23]  */
        mytm.tm_min   = 0; /* minutes after the hour     - [0,59]  */
        mytm.tm_sec   = 0; /* seconds after the minute   - [0,59]  */
        mytm.tm_isdst = 0; /* Daylight Savings Time flag */

        tic_time_stamp_ref = mktime(& mytm);
    }

	return (tic_time_stamp_ref);
}

//----------------------------------------------------------------------------
// Create a timestamp from DMYHMS byte buffer
// Notice : Timezone and DST not managed on MSP430. Hence we encodes DMYHMS dates as if they were UTC and non DST !!!
// the objective is only to get back a DMYHMS (or tm *) to correctly decode a meter date
time_t tic_get_timestamp_from_DMY_HMS_bytes(unsigned char * date_buf) {

	struct tm mytm;
	time_t mytime;

	mytm.tm_mday = *date_buf; date_buf++; /* day of the month - [1,31]  */
	mytm.tm_mday += (mytm.tm_mday == 0 ? 1 : 0);
	mytm.tm_mon  =  *date_buf; date_buf++; /* months since January - [0,11]  */
	mytm.tm_mon  -= (mytm.tm_mon > 0 ? 1 : 0);
	mytm.tm_year =  *date_buf; date_buf++;
	// Note about criteria definition the delta period is period beetween the date and 01/01/2000 00:00:00
	// ==> 00/00/00 00:00:00 or 01/01/00 00:00:00 ==> NO Delta
	// ==> 00/00/00 00:01:00 or 01/01/00 00:01:00 ==> 1 minute delta
	mytm.tm_year += 2000 - 1900;                     /* years since 1900 for mktime */
	mytm.tm_hour  = *date_buf; date_buf++;  /* hours after the midnight   - [0,23]  */
	mytm.tm_min   = *date_buf; date_buf++;  /* minutes after the hour     - [0,59]  */
	mytm.tm_sec   = *date_buf; date_buf++; ; /* seconds after the minute   - [0,59]  */
	mytm.tm_isdst = 0;    /* Daylight Savings Time flag */

	mytime = mktime(& mytm);
	mytime -= tic_get_timestamp_ref(); // nb seconds since 01/01/2000

	return (mytime);
}


//----------------------------------------------------------------------------
// Create back a struct tm from time_t comming from tic_get_timestamp_from_DMY_HMS_bytes()
// Notice : Timezone and DST not managed on MSP430. Hence we encodes DMYHMS dates as if they were UTC and non DST !!!
// the objective is only to get back a DMYHMS (or tm *) to correctly decode a meter date
struct tm * tic_get_tm_from_timestamp(unsigned long tmp_ulong) {
	tmp_ulong += tic_get_timestamp_ref() + 3600; //TODO: find a way to beter manage this 1h shift due to TZ and DST of running computer
	return (gmtime((time_t *)&tmp_ulong ));
}

//----------------------------------------------------------------------------
// Use to calculate all timeouts relative to TIC Frame réception
unsigned short tic_frame_rx_expected_max_size(TIC_meter_type_t mt){
	return( mt == MT_CT ? 160 :
		  ( mt == MT_CBEMM ? 200 :
		  ( mt == MT_CBEMM_ICC ? 200 :
		  ( mt == MT_CBETM ? 300 :
		  ( mt == MT_CJE ? 350 :
		  ( mt == MT_ICE ? 1100 :
		  ( mt == MT_STD ? 800 :
		  ( mt == MT_PMEPMI ? 1400 :
		  ( mt == MT_PMEPMI13 ? 1400 :
		  ( 1400 /* Max of all types for all other cases MT_UNKNOWN MT_NULL */))))))))));
}

//----------------------------------------------------------------------------
TIC_meter_type_t tic_mt_and_aidx_to_mt(TIC_meter_type_t meter_type, unsigned short uiAttrIdx) {
	// Manage ICE case wher 3 different attributes exists (2 virtual meter types)
	return(meter_type != MT_ICE ? meter_type :
		(uiAttrIdx % 3 == 0 ? MT_ICE :
			(uiAttrIdx % 3 == 1 ? MT_ICE_p : MT_ICE_p1)));
}

//----------------------------------------------------------------------------
TIC_meter_descriptor_t * tic_metertype_to_meterdesc(TIC_meter_type_t mt){
	return (TIC_meter_descriptor_t *) (mt < MT_END ? &(tic_meter_descriptor[mt]) :  NULL );
};

//----------------------------------------------------------------------------
void tic_set_expfields_on_label(const TIC_expected_field_t ** hndl_expfields, unsigned char * nb_expfields, char * label) {
	unsigned char ndesc = 0, nf = 0;
	const TIC_expected_field_t * pt_expfields = NULL;

	while ((ndesc < TIC_NB_MANAGED_METER)) {
//printf("ndesc:%d, ",ndesc);
		if (pt_expfields != tic_meter_descriptor[ndesc].expected_fields) {
			pt_expfields = tic_meter_descriptor[ndesc].expected_fields;
			*nb_expfields = tic_meter_descriptor[ndesc].expected_fields_number;

//printf("*nb_expfields:%d, nf: ",*nb_expfields);
			for (nf = 0; (nf < (5 < *nb_expfields ? 5 : *nb_expfields)); nf++) { /* Should be found in first 5 fields !! */
//printf("%d (%s==%s) ,",nf,pt_expfields[nf].label,label);
				if (strcmp(pt_expfields[nf].label,label) == 0) break;
			}
			if (nf < (5 < *nb_expfields ? 5 : *nb_expfields)) break;
		}
		ndesc++;
//printf("\n");
	}
	if (ndesc == TIC_NB_MANAGED_METER) {
		pt_expfields = NULL; *nb_expfields = 0;
	}
	*hndl_expfields = pt_expfields;
}

//----------------------------------------------------------------------------
void rt_find_meter_desc(TIC_meter_type_t * mt_finder, const TIC_expected_field_t * pt_expfields, unsigned char field_number) {

	// This first to manage quickly the DELIM_STD exception in CHKS calculation Cf tic-parser.c/
	if (pt_expfields == NULL) {
		*mt_finder = MT_UNKNOWN;

	} else if ((*mt_finder == MT_UNKNOWN) || (*mt_finder == MT_NULL) ) {

		if      (tic_meter_descriptor[0].expected_fields == pt_expfields) *mt_finder = MT_UNKNOWN;
		else if (tic_meter_descriptor[1].expected_fields == pt_expfields) *mt_finder = MT_CT;
		else if (tic_meter_descriptor[5].expected_fields == pt_expfields) *mt_finder = MT_CJE;
		else if (tic_meter_descriptor[6].expected_fields == pt_expfields) *mt_finder = MT_ICE;
		else if (tic_meter_descriptor[7].expected_fields == pt_expfields) *mt_finder = MT_STD;
		else if (tic_meter_descriptor[8].expected_fields == pt_expfields) *mt_finder = MT_PMEPMI;

	} else if ((*mt_finder == MT_CT) || (*mt_finder == MT_CBEMM)) { // Find more precisely the meter type in taht case (CT, CBEMM, CBEMM-ICC, CBETM)
		if      (field_number == 22) *mt_finder = MT_CBEMM;      // ADCO (b3), IINST(b22)
		else if (field_number == 23) *mt_finder = MT_CBETM;      // ADCO (b3), IINST1(b23)  (Pour accepter alerte ou trame nomale)
		else if (field_number == 32) *mt_finder = MT_CBEMM_ICC;  // ADCO (b3), PAPP(b32)

	} else if (*mt_finder == MT_PMEPMI) {  // Find more precisely the meter type in thatt case (2010 or 2013)
		if      ((field_number == 0) || (field_number == 1)) *mt_finder = MT_PMEPMI13;  // TRAME (b0), ADS (b1)
	}

};

//----------------------------------------------------------------------------
unsigned char tic_str_compute_checksum(char * strbuf) {
	unsigned char chks=0;
	while (*strbuf != '\0') {chks += *strbuf;
//printf("%c.%c[%02x] ",*strbuf,(chks & 0x3F)+ 0x20,(chks & 0x3F)+ 0x20);
		strbuf++;
	}
//printf("\n");
	chks &= 0x3F;
	chks += 0x20;
	return (chks);
}

/* Optimized version to count bit in a bit field  --------------*/
/* Unsing Lookup table (uses 256 more bytes in flash) */
static const unsigned char BitsSetTable256[256] =
{
#define B2(n) n,     n+1,     n+1,     n+2
#define B4(n) B2(n), B2(n+1), B2(n+1), B2(n+2)
#define B6(n) B4(n), B4(n+1), B4(n+1), B4(n+2)
    B6(0), B6(1), B6(1), B6(2)
};


//----------------------------------------------------------------------------
unsigned char tic_nb_fields_selected(TIC_desc_t *desc) {
	unsigned char nbf = 0, i;

	if (aGET_DESCPTR_TYPE(desc) == aDESC_TYPE_VAR_BITS_FIELD) {
		i=aGET_DESCPTR_SIZE(desc);
		if (i>0) {
			i--; // Remove header from list of byte to parse (i is number of bytes to parse)
/*
			// ---------------- Simplest way to count bits using existing API (ucFTicFieldGetBit) ... Very/Too long (1 ms) !
			i *= 8; // i becomes Nbr of bits
			while (i > 0) {
				if (ucFTicFieldGetBit((TIC_BUF_TYPE *)desc, i-1)) nbf++;
				i--;
			};
*/
/*
			// ----------------- More compact way ... still a bit long (100 us)!
			unsigned int c; // c accumulates the total bits set in v
			while (i > 0) {
				unsigned char v = ((TIC_BUF_TYPE *)desc)[i];
				for (; v; v >>= 1) {
				  nbf += v & 1;
				}
				i--;
			};
*/
			// ----------------- Fastest way with lookup tables (less than 30 us) !
			while (i > 0) {
				nbf += BitsSetTable256[((TIC_BUF_TYPE *)desc)[i]];
				i--;
			};

		}

	} else {
		nbf = aGET_DESCPTR_SIZE(desc) - 1;
	}
	return (nbf);
}

//----------------------------------------------------------------------------
unsigned char * tic_get_value_at_index(TIC_meter_descriptor_t * pt_tic_descriptor,
	TIC_BUF_TYPE *tb,
	unsigned char idx,
	unsigned char src_is_unpacked) {

	// Return a pointer to the value at index if it exists

	if (tb == NULL) return NULL;

	unsigned char * tbbuf = aTB_GET_BUF(tb);

	unsigned char ifield = 0, type;

	if (idx >= pt_tic_descriptor->expected_fields_number) return NULL;

	while (idx > 0) {
		if ((src_is_unpacked) || (ucFTicFieldGetBit(aTB_GET_DESC(tb), ifield) != 0)) {

			type = pt_tic_descriptor->expected_fields[ifield].type;
			if (type == TYPE_U24CSTRING) {
				tbbuf +=  3;
				tbbuf += strlen((char *)tbbuf) + 1;

			} else if (type == TYPE_CSTRING) {
				tbbuf +=  strlen((char *)tbbuf) + 1;

			} else if (type == TYPE_HEXSTRING) {
				tbbuf += *tbbuf + 1;

			} else if(type == TYPE_DMYhmsCSTRING){
 			    tbbuf +=  6;
				tbbuf +=  strlen((char *)tbbuf) + 1;

			} else if ((type == TYPE_E_PT) || (type == TYPE_E_DIV) || (type == TYPE_E_CONTRAT) || (type == TYPE_E_STD_PT) || (type == TYPE_E_STD_CONTRAT)) {
				tbbuf +=  tic_enum_len(tbbuf);

			} else if (type == TYPE_U24_E_DIV) {
				tbbuf += 3;
				tbbuf += tic_enum_len(tbbuf);

			} else if (type == TYPE_tsDMYhms_E_PT) {
				tbbuf += 4;
				tbbuf += tic_enum_len(tbbuf);

			} else if (type < TYPE_END) {
				tbbuf += TIC_binary_type_size[type];

			} else{				// This case should never occurs

			} // (type == ...)

		} // if (ucFTicFieldGetBit(tbdesc,ifield) != 0)
		ifield++; idx--;
	}// while (ifield < idx)

	return((ucFTicFieldGetBit(aTB_GET_DESC(tb),ifield) != 0) ? tbbuf : NULL);
}


#if WITH_BATCH_REPORT==1
bm_sample_type_t tic_br_type_at_index(TIC_expected_field_t * expected_fields,unsigned char fid) {

	// TODO: Allow Managing Enums Types and new tsDMYhms in batches
	// For enums manges like U8 only (if string only tsring size will be used 'string lost in batches)
	// For tsDMYhms: manage has U32

	switch (expected_fields[fid].type) {

		case (TYPE_U8):	return(ST_U8);
		case (TYPE_U16): return(ST_U16);
		case (TYPE_I16): return(ST_I16);
		case (TYPE_U24CSTRING): return(ST_U24);
		case (TYPE_U24): return(ST_U24);
		case (TYPE_tsDMYhms): return(ST_U32);// New allow Timestamp batch
		case (TYPE_U32): return(ST_U32);
		case (TYPE_DMYhms): return(ST_U32); // New case : try to manage date with virtual GMT timestamp
		case (TYPE_FLOAT) : return(ST_FL);

		// New Allow batch on first Byte of enums
		case (TYPE_E_PT):
		case (TYPE_E_DIV):
		case (TYPE_E_CONTRAT):
        case (TYPE_E_STD_PT):
        case (TYPE_E_STD_CONTRAT):
			return(ST_U8);

		default:
			return(ST_UNDEF);

	} // switch (expected_fields[j].type)
}

// st = ST_UNDEF not a managed type for Batch report
// return NULL if value was not available
void * tic_br_sample_and_type_at_index(TIC_meter_descriptor_t * pt_tic_descriptor,
	TIC_BUF_TYPE *tb,
	unsigned char idx,
	bm_sample_t *s,
	bm_sample_type_t *st,
	unsigned char tb_is_unpacked) {

	unsigned char * value;

	// Process conversion to sample type data usable by batch report

	value = tic_get_value_at_index(pt_tic_descriptor,tb,idx,tb_is_unpacked);

	switch (pt_tic_descriptor->expected_fields[idx].type) {

		case (TYPE_U8):
			*st = ST_U8;
			if (value == NULL) return(NULL);
			s->u8 = *((unsigned char*)value);
			return(&(s->u8));

		case (TYPE_U16):
			*st = ST_U16;
			if (value == NULL) return(NULL);
			U16p_TO_U16(value,s->u16);
			return(&(s->u16));

		case (TYPE_I16):
			*st = ST_I16;
			if (value == NULL) return(NULL);
			I16p_TO_I16(value,s->i16);
			return(&(s->i16));

		case (TYPE_U24):
			*st = ST_U32;
			if (value == NULL) return(NULL);
			U24p_TO_U32(value,s->u32);
			return(&(s->u32));

		case (TYPE_tsDMYhms): // New allow Timestamp batch
		case (TYPE_U32):
			*st = ST_U32;
			if (value == NULL) return(NULL);
			U32p_TO_U32(value,s->u32);
			return(&(s->u32));

		case (TYPE_DMYhms): // New case : try to manage date with virtual GMT timestamp
			// TODO: if OK expand to other date types ???
			*st = ST_U32;
			if (value == NULL) return(NULL);
			// Value point on a DMYHMS byte array convert it to timestamp (U32) for compressed batch reports
			s->u32 = tic_get_timestamp_from_DMY_HMS_bytes(value);
			return(&(s->u32));

		// TODO: Allow Managing Enums Types and new tsDMYhms in batches
		// For enums manges like U8 only (if string only tsring size will be used 'string lost in batches)
		// For tsDMYhms: manage has U32

		// New Allow batch on first Byte of enums
		case (TYPE_E_PT):
		case (TYPE_E_DIV):
		case (TYPE_E_CONTRAT):
        case (TYPE_E_STD_PT):
        case (TYPE_E_STD_CONTRAT):
			*st = ST_U8;
			if (value == NULL) return(NULL);
			s->u8 = *((unsigned char*)value);
			return(&(s->u8));

		case (TYPE_FLOAT):
			*st = ST_FL;
			if (value == NULL) return(NULL);
			FLTp_TO_FLT(value,s->fl);
			return(&(s->fl));

		default:
			*st = ST_UNDEF; // For all Types not scalar hence not yet managed ... TODO ;O)
			return(NULL);
	} // switch (expected_fields[j].type)

	// return NULL; // Sample read and type OK
}



#endif
//-------------------------------------------------------------
//TOUPPER FONCTION for STRING:

int strcmp_nocasesensitive(const char *s1, const char *s2)
{
    for ( ; (toupper(*(unsigned char *)s1) == toupper(*(unsigned char *)s2)); s1++, s2++)
    if (*s1 == '\0')
        return 0;
    return ((toupper(*(unsigned char *)s1) < toupper(*(unsigned char *)s2)) ? -1 : +1);
}

//----------------------------------------------------------------------------
unsigned char tic_generic_string_match(unsigned char * sgen,unsigned char * s) {
	// Only first parameter string can embed '?' to indicate any character once
	// Only first parameter string can embed '*' to indicate any character zero or many
	// TODO: manage a "despecializator '\' to allow the characters '?' and '*'
	//       Beware that reserved space for this can of string could be doubled
	// TODO: The algorithm is very basic when * is found it only look for the last occurence
	//       of next char in s ... algorithm should be reccursive but not really adapted to
	//       enbeded programms
	// return 1 sgen match s 0 either
	unsigned char *tmp;
	while ((*sgen != '\0') && (*s != '\0')) {
		if (*sgen == '*') {
			// Pass any other * char
			while ((*sgen != '\0') && (*sgen == '*')) sgen++;
			// Find last occurence of new sgen in current s
			tmp = NULL;
			while (*s != '\0') {
				if ((*sgen == '?') ||(*s == *sgen)) tmp = s;
				s++;
			}
			if (tmp != NULL) {
				s = tmp; sgen++;
				if (*s != '\0') s++;
			}
		} else {
			if (!((*sgen == '?') || (*sgen == *s))) return(0);
			sgen++;s++;
		}
	}

	// Pass any * terminating genric string
	while ((*sgen != '\0') && (*sgen == '*')) sgen++;

	if (*sgen != '\0') return (0);
	if (*s != '\0')    return (0);

	return (1);

}

//----------------------------------------------------------------------------
static inline unsigned char tic_check_u8array_change(
	unsigned char *tbb, unsigned char *aft, unsigned char *bef, unsigned char sz)
{
	unsigned char i;
	for (i = 0; i < sz; i++) { // if any bit, defined in criteria byte stream, has changed in byte stream
		if ((*bef ^ *aft) & *tbb) {
			return(1); // Field changed get out with changed !
		} // if tbbuf is a criterion
		bef++;aft++;tbb++;
	} // for
	return(0);
}

//----------------------------------------------------------------------------
static inline unsigned char tic_check_u8datearray_change(
    unsigned char *tbb, unsigned char *aft, unsigned char *bef, unsigned char sz)
{
    unsigned char i;
    for (i = 0; i < sz; i++) { // For all date fields one is enough to trig
        if ((*tbb != (unsigned char) (0xFF)) &&
            (*tbb != (unsigned char) (0x00))){
            if ((*bef != *aft) && ((*aft % *tbb) == 0)){ // different and multiple of criterion
                return(1); // Field changed get out with changed !
            }
        } // if tbbuf is a criterion
        bef++;aft++;tbb++;
    } // for
    return(0);
}

//----------------------------------------------------------------------------
unsigned char tic_check_changes(TIC_meter_descriptor_t * pt_tic_descriptor,
	TIC_BUF_TYPE *tbcrit,
	TIC_BUF_TYPE *tbbefore,unsigned char tbbefore_unpacked,
	TIC_BUF_TYPE *tbafter, unsigned char tbafter_unpacked,
	TIC_desc_t * desc_result ) {

	// Return fields that are changed in the desc_result descriptor ONLY if not NULL (NULL alow faster check change processing)

	unsigned char * tbbuf  = aTB_GET_BUF(tbcrit);
	unsigned char * result = NULL;

	unsigned char ifield = 0;
	unsigned char nfield=pt_tic_descriptor->expected_fields_number;

	unsigned long delta;

	unsigned char sz;
	unsigned char nb_field_changed = 0;
	unsigned char changed = 0;

	// If NULL no space allocated for result bitsring we do nothing in result (most of the time not used to gain RAM memory and speed)
	if (desc_result) result = desc_result->u8;
	if (result) {
		aDESCPTR_HEADER_INIT_FROM_VALUES(result,
				0, 0, aDESC_TYPE_VAR_BITS_FIELD, aTIC_DESC_MAX_NB_BYTES);
	}

	unsigned char *before, *after;
	unsigned long tbb;

	while (nfield-- > 0) {
		if (ucFTicFieldGetBit(aTB_GET_DESC(tbcrit),ifield) != 0) {
			before = tic_get_value_at_index(pt_tic_descriptor, tbbefore,ifield,tbbefore_unpacked);
			after  = tic_get_value_at_index(pt_tic_descriptor, tbafter,ifield,tbafter_unpacked);
			// For TYPE_CSTRING we make comparison of containt with criteria to validate trigger on field appearing or desappering
			// For all others type if field criteria is set and if field appear or desappear a report is triggered (without checking criteria)
			// Cf else of follwing if
			if (((before != NULL ) && (after  != NULL )) ||
				(((before != NULL ) || (after  != NULL )) &&
				 (pt_tic_descriptor->expected_fields[ifield].type == TYPE_CSTRING))){
				// If the values to compare exists, compare them

				switch (pt_tic_descriptor->expected_fields[ifield].type) {
					case (TYPE_CSTRING):
						// Generic string comparison according to specifications
						// For string comparison we allow one of string empty to see if after or previous was a value that can set a trigger
						changed = ((before == NULL ) || (after  == NULL )); // One of both should be != NULL then strcmp not needed to say there is a difference
						if (! changed) changed = strcmp ((char*)after,(char*)before);

						if (changed) { // If string has changed in other case no comparison needed

							if (pt_tic_descriptor->expected_fields[ifield].attribute & ATTRIBUTE_MULTI_OCCURENCE_FIELD) {
								unsigned char *tmpptr;
								// Multiple field may be encoded for same label (ICE PREAVIS case)
								// Look for field between ',' use it to check if value has appeared or deasappeared from TIC flow
								changed = 0;
								while ((*tbbuf != '\0') && (!changed)) {

									// Set trigger separator to '\0' if exists
									if ((tmpptr = (unsigned char *)strchr((char *)tbbuf, ',')) != NULL) { *tmpptr='\0'; }

									if (strcmp((char *)tbbuf,"*") == 0) {// In that case any change will valid a report
										if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++; changed = 1;

									} else { // In that case we have to check if generic expression has appeared or deseapeared in the read concatened fields
										unsigned char *tmpptr2;
										unsigned char inbefore = 0, inafter = 0;

										if (before != NULL)
											while ((*before != '\0') && (!inbefore)) { // Test if cuurent trigger is in before
												// Set before separator to '\0' if exists
												if ((tmpptr2 = (unsigned char *)strchr((char *)before, ',')) != NULL) { *tmpptr2='\0'; }
												if (tic_generic_string_match(tbbuf,before)) { // test if required string is in before
													inbefore=1;
												}
												if (tmpptr2 != NULL) { *tmpptr2=','; before = tmpptr2+1; }
												else before +=  strlen((char*)before); // need to go on End Of String to terminate While
											}

										if (after != NULL)
											while ((*after != '\0') && (!inafter)) {  // Test if cuurent trigger is in after
												// Set after separator to '\0' if exists
												if ((tmpptr2 = (unsigned char *)strchr((char *)after, ',')) != NULL) { *tmpptr2='\0'; }
												if (tic_generic_string_match(tbbuf,after)) { // test if required string is in before
													inafter=1;
												}
												if (tmpptr2 != NULL) { *tmpptr2=','; after = tmpptr2+1; }
												else after +=  strlen((char*)after); // need to go on End Of String to terminate While
											}

										if (inafter != inbefore) { // Test if required string as desappeared or appeared
											if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++; changed = 1;
										}

									}

									// Back trigger separator to ',' and prepare to check next trigger value
									if (tmpptr != NULL) { *tmpptr=','; tbbuf = tmpptr+1; }
									else tbbuf +=  strlen((char*)tbbuf); // need to go on End Of String to terminate While

								} // while ((*tbbuf != '\0') && (!changed))

							} else { // Not an ATTRIBUTE_MULTI_OCCURENCE_FIELD (usual comparison)
								// Test if after or before = criterion string (not ATTRIBUTE_MULTI_OCCURENCE_FIELD)
								unsigned char inbefore = 0, inafter = 0;
								if (strcmp((char *)tbbuf,"*") == 0) { // In that case any change will valid a report
									if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;

								} else { // In that case a report is set only if the criteria value as appeared or desappeared
									if (before != NULL) inbefore = tic_generic_string_match(tbbuf,before);
									if (after  != NULL) inafter = tic_generic_string_match(tbbuf,after);
									if (inafter != inbefore) { // Test if required string as desappeared or appeared
										if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;
									}
								}
							}
						} //if (changed) { // If string has changed in other case no comparison needed

						tbbuf +=  strlen((char*)tbbuf) + 1;

					break;

					case (TYPE_CHAR):
						// Generic character comparison according to specifications
						if ( ((*tbbuf == '?') || (*tbbuf == *before) || (*tbbuf == *after)) &&
						     (*after != *before) &&
						     (*tbbuf != '^')) { if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;}
						tbbuf +=  1;
					break;


					case (TYPE_SDMYhmsU8):
						if ( ((*tbbuf == '?') || (*tbbuf == *before) || (*tbbuf == *after)) &&
						     (*after != *before) &&
						     (*tbbuf != '^') ) {
							if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;
							tbbuf += 1 + 6 + 1;
							break;
						} else {
							tbbuf++; after++; before++;
							if (tic_check_u8datearray_change(tbbuf, after, before, 6) != 0) {
								if (result) vFTicFieldSetBit(result,ifield);nb_field_changed++;
								tbbuf += 6 + 1;
								break;
							}
						}
						tbbuf += 6; after += 6; before += 6;
					case (TYPE_U8):
						if ( (*((unsigned char*)tbbuf) != (unsigned char) (0xFF)) &&
							 (*((unsigned char*)tbbuf) != (unsigned char) (0x00)) ){
							delta = (
							 (*((unsigned char*)before) > *((unsigned char*)after)) ?
							 (*((unsigned char*)before) - *((unsigned char*)after)) :
							 (*((unsigned char*)after) - *((unsigned char*)before))
							);
							if (delta > *((unsigned char*)tbbuf))
								{if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;}
						}
						tbbuf += 1;
					break;

					case (TYPE_11hhmmSSSS): {
						unsigned char i, fieldChanged = 0;
						for(i=0;i<11;i++) {
							if (*tbbuf == 0xFF) { // ==> Pas de test sur les valeurs
								tbbuf++;
								before += (*before == (unsigned char)0xFF ? 1 : 4);
								after  += (*after  == (unsigned char)0xFF ? 1 : 4);
							} else { // Delta is set for bloc
								if (*before == (unsigned char)0xFF) { // Case check something configured and before was empty
									before += 1;
									if (*after != (unsigned char)0xFF) {
										fieldChanged=1; after += 4;
									} else {
										after += 1;
									}

								} else if (*after == (unsigned char)0xFF) { // Case check something configured and after was empty
									after += 1;
									if (*before != (unsigned char)0xFF) {
										if (result) vFTicFieldSetBit(result,ifield);nb_field_changed++;
										before += 4;
									} else {
										before += 1;
									}

								} else { // Delta, before and after are set
									if (tic_check_u8datearray_change(tbbuf, after, before, 2) != 0) { // Test hhmm
										if (result) vFTicFieldSetBit(result,ifield);nb_field_changed++;
									} else { // if no change on hh mm check SSSS bitfield
										// Test U16 bit field
										unsigned short tbb;
										unsigned short bef, aft;
										// Below is necessary to avoid (short) alignement errors with simple casts
										U16p_TO_U16((before + 2),bef);
										U16p_TO_U16((after  + 2),aft);
										U16p_TO_U16((tbbuf  + 2),tbb);
										if (tbb & (bef ^ aft)) {
											if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;
										}
									}
									tbbuf += 4; after += 4; before += 4;
								} // Delta, before and after are set
							}  // Delta is set for bloc
						} // for(i=0;i<11;i++)
						if ((result) && (fieldChanged))
							vFTicFieldSetBit(result,ifield);nb_field_changed++;
					}
					break;

					case (TYPE_SDMYhmsU16):
						if ( ((*tbbuf == '?') || (*tbbuf == *before) || (*tbbuf == *after)) &&
						     (*after != *before) &&
						     (*tbbuf != '^') ) {
							if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;
							tbbuf += 1 + 6 + 2;
							break;
						} else {
							tbbuf++; after++; before++;
							if (tic_check_u8datearray_change(tbbuf, after, before, 6) != 0) {
								if (result) vFTicFieldSetBit(result,ifield);nb_field_changed++;
								tbbuf += 6 + 2;
								break;
							}
						}
						tbbuf += 6; after += 6; before += 6;
					case (TYPE_U16): {
						unsigned short tbb;
						U16p_TO_U16(tbbuf,tbb);
						if ((tbb != (unsigned short) (0xFFFF)) &&
							(tbb != (unsigned short) (0x0000))) {
							unsigned short bef, aft;
							U16p_TO_U16(before,bef);
							U16p_TO_U16(after,aft);
							delta = ( (bef > aft) ? (bef - aft) : (aft - bef) );
							if (delta > tbb){if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;}
						}
						tbbuf += 2;
					}
					break;

					case (TYPE_I16): {
						unsigned short tbb;
						U16p_TO_U16(tbbuf,tbb);
						if ((tbb != (unsigned short) (0xFFFF)) &&
							(tbb != (unsigned short) (0x0000))) {
							unsigned short bef, aft;
							I16p_TO_I16(before,bef);
							I16p_TO_I16(after,aft);
							delta = ( (bef > aft) ? (bef - aft) : (aft - bef) );
							if (delta > tbb){if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;}
						}
						tbbuf += 2;
					}
					break;

					case (TYPE_U24CSTRING):
						// Test U24 Changes
						U24p_TO_U32(tbbuf,tbb);
						if ((tbb != (unsigned long) (0xFFFFFF)) &&
							(tbb != (unsigned long) (0x000000))) {
							unsigned long bef, aft;
							U24p_TO_U32(before,bef);
							U24p_TO_U32(after,aft);
							delta = ( (bef > aft) ? (bef - aft) : (aft - bef) );
							if (delta > tbb ){
								if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;
							} else {
								// test Cstring changes
								// Generic string comparison according to specifications
								after+=3; before+=3;
								if ((strcmp ((char*)after,(char*)before) != 0)) { // If string has changed
									// Test if after or before = criterion string
									if (tic_generic_string_match((tbbuf+3),before)) {
										if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;
									} else if (tic_generic_string_match((tbbuf+3),after)) {
										if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;
									}
								}
							}
						}
						tbbuf += 3;
						tbbuf +=  strlen((char*)tbbuf) + 1;

					break;

					case (TYPE_SDMYhmsU24):
						if ( ((*tbbuf == '?') || (*tbbuf == *before) || (*tbbuf == *after)) &&
						     (*after != *before) &&
						     (*tbbuf != '^') ) {
							if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;
							tbbuf += 1 + 6 + 3;
							break;
						} else {
							tbbuf++; after++; before++;
							if (tic_check_u8datearray_change(tbbuf, after, before, 6) != 0) {
								if (result) vFTicFieldSetBit(result,ifield);nb_field_changed++;
								tbbuf += 6 + 3;
								break;
							}
						}
						tbbuf += 6; after += 6; before +=6;
					case (TYPE_4U24):
					case (TYPE_6U24):
					case (TYPE_U24): {
						unsigned long tbb;
						U24p_TO_U32(tbbuf,tbb);
						if ((tbb != (unsigned long) (0xFFFFFF)) &&
							(tbb != (unsigned long) (0x000000))) {
							unsigned long bef, aft;
							U24p_TO_U32(before,bef);
							U24p_TO_U32(after,aft);
							delta = ( (bef > aft) ? (bef - aft) : (aft - bef) );
							if (delta > tbb ){if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;}
						}
						tbbuf += 3;
					}
					break;

					case (TYPE_U32):{
						unsigned long tbb;
						U32p_TO_U32(tbbuf,tbb);
						if ((tbb != (unsigned long) (0xFFFFFFFF)) &&
							(tbb != (unsigned long) (0x00000000))) {
							unsigned long bef, aft;
							U32p_TO_U32(before,bef);
							U32p_TO_U32(after,aft);
							delta = ( (bef > aft) ? (bef - aft) : (aft - bef) );
							if (delta > tbb){if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;}
						}
						tbbuf += 4;
					}
					break;

					case (TYPE_FLOAT):{
						float tbb;
						FLTp_TO_FLT(tbbuf,tbb);
						if (tbb != 0.0) {
							float bef, aft;
							FLTp_TO_FLT(before,bef);
							FLTp_TO_FLT(after,aft);
							float deltaf = ( (bef > aft) ? (bef - aft) : (aft - bef) );
							if (deltaf > tbb){if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;}
						}
						tbbuf += 4;
					}
					break;

					case (TYPE_BF32xbe): {
						unsigned long tbb;
						unsigned long bef, aft;
						// Below is necessary to avoid (short) alignement errors with simple casts
						U32p_TO_U32(before,bef);
						U32p_TO_U32(after,aft);
						U32p_TO_U32(tbbuf,tbb);
						if (tbb & (bef ^ aft)) {
							if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;
						}
						tbbuf += 4;
					}
					break;

					case (TYPE_BF8d):{
						unsigned char tbb;
						unsigned char bef, aft;
						bef = *before;
						aft = *after;
						tbb = *tbbuf;
						if (tbb & (bef ^ aft)) {
							if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;
						}
						tbbuf += 1;
					}
					break;

					case (TYPE_HEXSTRING):
						sz = tbbuf[0];
						// Note: Considered different if size is different
						if (*after != *before) {
							vFTicFieldSetBit(result,ifield);nb_field_changed++;
							tbbuf += (tbbuf[0] +1);
							break;
						} else {
							if (sz > *after) sz = *after; // Check only smaller common part of
							if (sz > 0) { // Do not check if no byte to check
								if (tic_check_u8array_change(tbbuf+1, after+1, before+1, sz) != 0) {// check any changed bit required
									if (result) vFTicFieldSetBit(result,ifield);nb_field_changed++;
									tbbuf += (tbbuf[0]+1);
									break;
								}
							}
						}
					break;

					case (TYPE_SDMYhms):
						if ( ((*tbbuf == '?') || (*tbbuf == *before) || (*tbbuf == *after)) &&
						     (*after != *before) &&
						     (*tbbuf != '^') ) {
							if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;
							tbbuf += 1 + 6;
							break;
						}
						tbbuf += 1; after += 1; before +=1;

					case (TYPE_DMYhms):
						sz = 6; goto lbl_process_date_field;

					case (TYPE_tsDMYhms):
						// NEW encoding using Timestamp
						// like U32 comparaison
						U32p_TO_U32(tbbuf,tbb);
						delta = 0;
						if ((tbb != (unsigned long) (0xFFFFFFFF)) &&
							(tbb != (unsigned long) (0x00000000))) {
							unsigned long bef, aft;
							U32p_TO_U32(before,bef);
							U32p_TO_U32(after,aft);
							delta = ( (bef > aft) ? (bef - aft) : (aft - bef) );
						}
						tbbuf += 4;
						if (delta > tbb){
							if (result) vFTicFieldSetBit(result,ifield);
							nb_field_changed++;
						}
					break;

					case (TYPE_DMYhmsCSTRING):
						sz = 6;
						if (tic_check_u8datearray_change(tbbuf, after, before, sz) != 0) {
							if (result) vFTicFieldSetBit(result,ifield);nb_field_changed++;
							tbbuf += sz;
						} else {
							tbbuf += sz;
							after += sz; before +=sz;
							// Generic string comparison according to specifications
							if ((strcmp ((char*)after,(char*)before) != 0)) { // If string has changed
								// Test if after or before = criterion string
								if (tic_generic_string_match(tbbuf,before)) {
									if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;
								} else if (tic_generic_string_match(tbbuf,after)) {
									if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;
								}
							}
						}
						tbbuf +=  strlen((char*)tbbuf) + 1;
					break;

					case (TYPE_E_PT):
					case (TYPE_E_DIV):
					case (TYPE_E_CONTRAT):
			        case (TYPE_E_STD_PT):
			        case (TYPE_E_STD_CONTRAT):
						if (tic_enum_changed(tbbuf,before, after))  {
							vFTicFieldSetBit(result,ifield);
							nb_field_changed++;
						}
						tbbuf +=  tic_enum_len(tbbuf);

					break;

					case (TYPE_U24_E_DIV):
						// Test U24 Changes
						U24p_TO_U32(tbbuf,tbb);
						delta = 0;
						if ((tbb != (unsigned long) (0xFFFFFF)) &&
							(tbb != (unsigned long) (0x000000))) {
							unsigned long bef, aft;
							U24p_TO_U32(before,bef);
							U24p_TO_U32(after,aft);
							delta = ( (bef > aft) ? (bef - aft) : (aft - bef) );
						}
						tbbuf += 3;	after += 3; before += 3;
						if (delta > tbb){
							if (result) vFTicFieldSetBit(result,ifield);
							nb_field_changed++;
						} else {
							if (tic_enum_changed(tbbuf, before, after))  {
								vFTicFieldSetBit(result,ifield);
								nb_field_changed++;
							}
						}
						tbbuf +=  tic_enum_len(tbbuf);
					break;

					case (TYPE_tsDMYhms_E_PT):
						// NEW encoding using Timestamp and periode tarifaire compression
						// like U32 comparaison
						U32p_TO_U32(tbbuf,tbb);
						delta = 0;
						if ((tbb != (unsigned long) (0xFFFFFFFF)) &&
							(tbb != (unsigned long) (0x00000000))) {
							unsigned long bef, aft;
							U32p_TO_U32(before,bef);
							U32p_TO_U32(after,aft);
							delta = ( (bef > aft) ? (bef - aft) : (aft - bef) );
						}
						tbbuf += 4;	after += 4; before += 4;
						if (delta > tbb){
							if (result) vFTicFieldSetBit(result,ifield);
							nb_field_changed++;
						} else {
							if (tic_enum_changed(tbbuf, before, after))  {
								vFTicFieldSetBit(result,ifield);
								nb_field_changed++;
							}
						}
						tbbuf +=  tic_enum_len(tbbuf);
					break;

					case (TYPE_hmDM):
						sz = 4; goto lbl_process_date_field;
					case (TYPE_DMh):
						sz = 3; goto lbl_process_date_field;
					case (TYPE_hm):
						sz = 2;
lbl_process_date_field:
						if (tic_check_u8datearray_change(tbbuf, after, before, sz) != 0) {
							if (result) vFTicFieldSetBit(result,ifield);nb_field_changed++;
						}
						tbbuf += sz;
					break;


					default:
						// This case should never occurs
					break;
				} // switch (expected_fields[j].type)

			} else { // The field is not present either in after or before but not in both
				// The report will be requested anyway for this field change
				// Notice: that if the field has deseapered, the report will be done without this field !
				if ((before != NULL ) || (after  != NULL )) {
					if (result) vFTicFieldSetBit(result,ifield); nb_field_changed++;
				}
			}// else if (after != NULL )

		} // if (ucFTicFieldGetBit(tbdesc,ifield) != 0)
		ifield++;
	}  // while (nfield-- > 0)

	return(nb_field_changed);
}

//----------------------------------------------------------------------------
signed short tic_serialize(TIC_meter_descriptor_t * pt_tic_descriptor,
	unsigned char* bufdest,
	TIC_BUF_TYPE *tbsrc,
	TIC_desc_t * desc_filter,
	TIC_desc_t * desc_filter_or,
	short buf_size,
	unsigned char src_is_unpacked,
	char forceBitFieldAndSize) {

	// Serialize "tbsrc" into "bufdest". May compress descriptor if possible
	// Historic 8 Bytes bitfield decriptor can be forced if forceBitFieldAndSize is != 0

	// NULL desc_filter can be passed to avoid filtering input buffer

	// If Serialized result to big for buf size => return -1

	// return size of serialized buffer inside buf included 8 desc bytes
	// Only existing and validated filed through filter field bit are returned

	// THIS IS IMPLEMENTED TO TRY TO GET IT ARCHITECTURE AGNOSTIC (endianess)

	// Now possible to serialize a TIC buffer from an "UNPACKED" TIC Buffer source

	unsigned char * tbbuf;
	unsigned char * tmpbuf;
	unsigned char ifield;
	unsigned char nfield;
	unsigned char len, type;

	unsigned char * filter = NULL;
	unsigned char * filter_or = NULL;

	short cur_buf_size = buf_size - TIC_SERIALIZED_SIZE_SIZE; // Reserve two bytes to store effective size of buffer at the end

	tbbuf  = aTB_GET_BUF(tbsrc);
	tmpbuf = bufdest;

	if (desc_filter != NULL) filter = desc_filter->u8;
	if (desc_filter_or != NULL) filter_or = desc_filter_or->u8;



#define FILTERS_GET_BIT(IFI) \
	(filter == NULL && filter_or == NULL ? 1 : \
		(ucFTicFieldGetBit(filter,IFI) ?   1 : \
			ucFTicFieldGetBit(filter_or,IFI)))


	//---------------------------------------------------------------------------------------------------
	// First estimate resulting descriptors size depending on new descriptor compression specifications
	signed short  iLastFieldNum = -1;
	unsigned short uiBitFieldSize, uiVarIndexSize = 1;
	ifield=0;
	nfield=pt_tic_descriptor->expected_fields_number;
	while (nfield-- > 0) {
		if (ucFTicFieldGetBit(aTB_GET_DESC(tbsrc),ifield) != 0)
			if (FILTERS_GET_BIT(ifield)) {
				// Evaluate BITFIELD DESC size
				iLastFieldNum = ifield;
				// Evaluate VARINDEX DESC size
				uiVarIndexSize++;
			}

		ifield++;
	}
	nfield=iLastFieldNum+1;
	uiBitFieldSize = (nfield / 8) + ((nfield % 8) > 0 ? 1 : 0); // Calculate the resulting number of necessary bytes to encode until "last field"
	uiBitFieldSize++; // Add 1 byte of header part

	//---------------------------------------------------------------------------------------------------
	// Prepare descriptor according to smallest size directly in dest buffer
	// Avoid usage of an other buffer to prepare desc
	aSET_DESCPTR_OBSOLETE(tmpbuf,0);
	if ((aGET_DESCPTR_SRPT_OR_LRVREQ(tbsrc)) || ((filter != NULL) ? aGET_DESCPTR_SRPT_OR_LRVREQ(filter) : 0)) {
		aSET_DESCPTR_SRPT_OR_LRVREQ(tmpbuf,1); // Set eventual  SHIFTED or LRV bit if exists
	} else {
		aSET_DESCPTR_SRPT_OR_LRVREQ(tmpbuf,0);
	}

	if (forceBitFieldAndSize) { //
		if (uiBitFieldSize > forceBitFieldAndSize) return -1; // Impossible to store desc in ORIGINAL Size (8)
		uiBitFieldSize = forceBitFieldAndSize;
		aSET_DESCPTR_TYPE(tmpbuf, aDESC_TYPE_VAR_BITS_FIELD);
		aSET_DESCPTR_SIZE(tmpbuf, uiBitFieldSize);  // For original format will have to be set to 0 before at the end
		cur_buf_size -= uiBitFieldSize;
		tmpbuf += uiBitFieldSize;

	} else	if (uiBitFieldSize < uiVarIndexSize) { // Var bitfield size selected/best
		aSET_DESCPTR_TYPE(tmpbuf, aDESC_TYPE_VAR_BITS_FIELD);
		aSET_DESCPTR_SIZE(tmpbuf, uiBitFieldSize);
		cur_buf_size -= uiBitFieldSize;
		tmpbuf += uiBitFieldSize;

	} else { // Var indexes selected/best
		if (uiVarIndexSize > aTIC_DESC_MAX_NB_BYTES) return -1;  // Impossible to store desc in current max desc size
		aSET_DESCPTR_TYPE(tmpbuf, aDESC_TYPE_VAR_INDEX);
		aSET_DESCPTR_SIZE(tmpbuf, uiVarIndexSize);
		cur_buf_size -= uiVarIndexSize;
		tmpbuf += uiVarIndexSize;
	}

	// Initialize all Descriptor remaining descriptor (memset to 0 or set indexes ti 0xFF)
	vFTicBufInitFromHeader(bufdest, *bufdest);

	//---------------------------------------------------------------------------------------------------
	// Now parse all necessary fields to serialize
	ifield=0; // nfield was recalculated before just for necessary number of fields to parse
	while (nfield-- > 0) {
		if (ucFTicFieldGetBit(aTB_GET_DESC(tbsrc),ifield) != 0) {

			if (src_is_unpacked)
				tbbuf = aTB_GET_BUF(tbsrc) + (pt_tic_descriptor->expected_fields[ifield].abs_pos);

			type = pt_tic_descriptor->expected_fields[ifield].type;

			if (type == TYPE_U24CSTRING) {
				len = 3;
				if (FILTERS_GET_BIT(ifield)) {
					// Manage u24 part
					cur_buf_size -= len; if (cur_buf_size < 0) return -1;
					memcpy((char *)tmpbuf,(char *)tbbuf,len);
					vFTicFieldSetBit(aTB_GET_DESC(bufdest),ifield);
					tmpbuf += len;
					tbbuf += len;
					// now manage Cstring
					len = strlen((char *)tbbuf) + 1;
					cur_buf_size -= len; if (cur_buf_size < 0) return -1;
					strcpy((char *)tmpbuf,(char *)tbbuf);
					tmpbuf += len;
					tbbuf += len /* at the end len is tring len */;
				} else {
					tbbuf += len;
					tbbuf += strlen((char *)tbbuf) + 1;
				}

			} else if (type == TYPE_DMYhmsCSTRING) {
				len = 6;
				if (FILTERS_GET_BIT(ifield)) {
					// Manage Date part
					cur_buf_size -= len; if (cur_buf_size < 0) return -1;
					memcpy((char *)tmpbuf,(char *)tbbuf,len);
					vFTicFieldSetBit(aTB_GET_DESC(bufdest),ifield);
					tmpbuf += len;
					tbbuf += len;
					// now manage Cstring
					len = strlen((char *)tbbuf) + 1;
					cur_buf_size -= len; if (cur_buf_size < 0) return -1;
					strcpy((char *)tmpbuf,(char *)tbbuf);
					tmpbuf += len;
					tbbuf += len ;//  at the end len is tring len
				} else {
					tbbuf += len;
					tbbuf += strlen((char *)tbbuf) + 1;
				}

			} else if (type == TYPE_CSTRING) {
				len = strlen((char *)tbbuf) + 1;
				if (FILTERS_GET_BIT(ifield)) {
					// Terminate if data overload result buffer
					cur_buf_size -= len; if (cur_buf_size < 0) return -1;
					strcpy((char *)tmpbuf,(char *)tbbuf);
					vFTicFieldSetBit(aTB_GET_DESC(bufdest),ifield);
					tmpbuf += len;
				}
				tbbuf +=  len;

			} else if (type == TYPE_HEXSTRING) {
				len = (*tbbuf) + 1;
				if (FILTERS_GET_BIT(ifield)) {
					// Terminate if data overload result buffer
					cur_buf_size -= len; if (cur_buf_size < 0) return -1;
					memcpy((char *)tmpbuf,(char *)tbbuf,len);
					vFTicFieldSetBit(aTB_GET_DESC(bufdest),ifield);
					tmpbuf += len;
				};
				tbbuf += len;

			} else if ((type == TYPE_E_PT) || (type == TYPE_E_DIV) || (type == TYPE_E_CONTRAT) || (type == TYPE_E_STD_PT) || (type == TYPE_E_STD_CONTRAT) ||
					   (type == TYPE_tsDMYhms_E_PT) || (type == TYPE_U24_E_DIV)) {

				if (type == TYPE_tsDMYhms_E_PT) len = 4 + tic_enum_len(tbbuf + 4);
				else if (type == TYPE_U24_E_DIV) len = 3 + tic_enum_len(tbbuf + 3);
				else len = tic_enum_len(tbbuf);

				if (FILTERS_GET_BIT(ifield)) {
					// Terminate if data overload result buffer
					cur_buf_size -= len; if (cur_buf_size < 0) return -1;
					memcpy((char *)tmpbuf,(char *)tbbuf,len);
					vFTicFieldSetBit(aTB_GET_DESC(bufdest),ifield);
					tmpbuf += len;
				};
				tbbuf += len;

			} else if (type == TYPE_11hhmmSSSS) {
				unsigned char i;
				unsigned char * tmp_tbbuf = tbbuf;
				len = 0;
				for(i=0;i<11;i++) {
					if (*tmp_tbbuf == (unsigned char)0xFF) { // ==> Pas de valeur pour ce bloc
						tmp_tbbuf++;
						len++;
					} else { // Delta is set for bloc
						tmp_tbbuf += 4;
						len += 4;
					}
				}
				if (FILTERS_GET_BIT(ifield)) {
					memcpy((char *)tmpbuf,(char *)tbbuf,len);
					vFTicFieldSetBit(aTB_GET_DESC(bufdest),ifield);
					tmpbuf += len;
				}
				tbbuf += len;

			} else if (type < TYPE_END) {
				len = TIC_binary_type_size[type];
				if (FILTERS_GET_BIT(ifield)) {
					// Terminate if data overload result buffer
					cur_buf_size -= len; if (cur_buf_size < 0) return -1;
					memcpy((char *)tmpbuf,(char *)tbbuf,len);
					vFTicFieldSetBit(aTB_GET_DESC(bufdest),ifield);
					tmpbuf += len;
				};
				tbbuf += len;

			} else {
				// This case should never occurs
			} // if (type == ...)

		} // if (ucFTicFieldGetBit(tbdesc,ifield) != 0)
		ifield++;
	} // while (nfield-- > 0)

	// Set the size of the frame at the end of buffers
	*((unsigned short *)&(bufdest[buf_size - TIC_SERIALIZED_SIZE_SIZE])) = (unsigned short) (tmpbuf - bufdest);

	return(tmpbuf - bufdest);

#undef FILTERS_GET_BIT
}


//----------------------------------------------------------------------------
static inline unsigned char tic_check_u8datearray_criteria(
	unsigned char *tbb, unsigned char sz)
{
	unsigned char i;
	for (i = 0; i < sz; i++) { // For all date fields one is enough to trig
		if ((*tbb != (unsigned char) (0xFF)) &&
		    (*tbb != (unsigned char) (0x00))){
			return(1); // Field criteria requested !
		} // if tbbuf is a criterion
		tbb++;
	} // for
	return(0);
}

//----------------------------------------------------------------------------
signed short tic_serialize_report_criteria(TIC_meter_descriptor_t * pt_tic_descriptor,
	unsigned char* buf,
	TIC_BUF_TYPE *tb,
	short buf_size,
	unsigned char tb_is_unpacked) {

	// TODO : make some verifications according to buf_size !!!

	// return size of serialized buffer inside buf included 8 desc bytes
	// Only existing and validated filed through filter field bit are returned

	// THIS IS IMPLEMENTED TO TRY TO GET IT ARCHITECTURE AGNOSTIC (endianess)
	// Note: This function is olny used for TIC criteria creation in tic2bibn or tic2crit
	// - Allocated space for resulting buffer muste be big enough
	// - Compression of descriptors (filter and criteria) is not done !!
	// - Decriptors use VarBitField with maximum descriptor size

	unsigned char * tbbuf;
	unsigned char * tmpbuf;
	unsigned char ifield;
	unsigned char nfield;
	unsigned char len,sz;

	unsigned char * criteria;
	unsigned char * filter;

	tbbuf  = aTB_GET_BUF(tb);

	filter   = (unsigned char*)aTB_CRIT_GET_FILTER_DESC(buf);
	vFTicBufInitFromHeaderValues(filter, 0, 0, aDESC_TYPE_VAR_BITS_FIELD, aTIC_DESC_MAX_NB_BYTES);

	criteria = (unsigned char*)aTB_CRIT_GET_TRIG_DESC(buf);
	vFTicBufInitFromHeaderValues(criteria, 0, 0, aDESC_TYPE_VAR_BITS_FIELD, aTIC_DESC_MAX_NB_BYTES);

	tmpbuf   = (unsigned char*)aTB_CRIT_GET_TRIG_BUF(buf);

	ifield=0;
	nfield=pt_tic_descriptor->expected_fields_number;

	while (nfield-- > 0) {
		if (ucFTicFieldGetBit(aTB_GET_DESC(tb),ifield) != 0) {

			if (tb_is_unpacked)
				tbbuf = aTB_GET_BUF(tb) + (pt_tic_descriptor->expected_fields[ifield].abs_pos);

			switch (pt_tic_descriptor->expected_fields[ifield].type) {
				case (TYPE_CSTRING):
					len = strlen((char *)tbbuf) + 1;
				    if (*(char *)tbbuf != '\0') {
						strcpy((char *)tmpbuf,(char *)tbbuf);
						vFTicFieldSetBit(criteria,ifield);
						tmpbuf += len;
				    };
				    vFTicFieldSetBit(filter,ifield);
					tbbuf +=  len;
				break;

				case (TYPE_CHAR):
				    if ( (*((unsigned char*)tbbuf) != '^') ){
						*tmpbuf = *tbbuf;
						vFTicFieldSetBit(criteria,ifield);
						tmpbuf += 1;
				    };
					vFTicFieldSetBit(filter,ifield);
				    tbbuf += 1;
				break;


				case (TYPE_SDMYhmsU8): {
					sz= 1 + 6 + 1;
					if ( *((unsigned char*)tbbuf)  != '^') {
					} else 	if (tic_check_u8datearray_criteria(tbbuf+1,6) != 0) {
					} else	{
						unsigned long tbb;
						U16p_TO_U16((tbbuf + 1 + 6),tbb);
						if ((tbb != (unsigned long) (0xFF)) &&
							(tbb != (unsigned long) (0x00))) {
						} else { sz = 0;}
					}
					if (sz) {
						vFTicFieldSetBit(criteria,ifield);
						memcpy((char *)tmpbuf,(char *)tbbuf, sz);
						tmpbuf += sz;
					};
					vFTicFieldSetBit(filter,ifield); tbbuf += 1 + 6 + 1;
				} break;

				case (TYPE_U8):
				    if ( (*((unsigned char*)tbbuf) != (unsigned char) (0xFF)) &&
						 (*((unsigned char*)tbbuf) != (unsigned char) (0x00)) ){
						*tmpbuf = *tbbuf;
						vFTicFieldSetBit(criteria,ifield);
						tmpbuf += 1;
				    };
					vFTicFieldSetBit(filter,ifield);
				    tbbuf += 1;
				break;

				case (TYPE_11hhmmSSSS): {
					unsigned char i, hasCriteria = 0;
					unsigned char * tmp_tbbuf = tbbuf;
					for(i=0;i<11;i++) {
						if (*((unsigned char*)tmp_tbbuf) == (unsigned char)0xFF) { // ==> Pas de valeur pour ce bloc
							tmp_tbbuf++;
						} else { // Delta is set for bloc
							if (memcmp(tmp_tbbuf, "\0\0\0\0", 4) != 0)
								hasCriteria = 1;
							tmp_tbbuf += 4;
						}
					}
					len = (tmp_tbbuf - tbbuf);
					if (hasCriteria) {
						vFTicFieldSetBit(criteria,ifield);
						memcpy((char *)tmpbuf,(char *)tbbuf, len);
					}
					tmpbuf += len;
					tbbuf = tmp_tbbuf;
					vFTicFieldSetBit(filter,ifield);
				}
				break;

				case (TYPE_SDMYhmsU16): {
					sz= 1 + 6 + 2;
					if ( *((unsigned char*)tbbuf)  != '^') {
					} else 	if (tic_check_u8datearray_criteria(tbbuf+1,6) != 0) {
					} else	{
						unsigned long tbb;
						U16p_TO_U16((tbbuf + 1 + 6),tbb);
						if ((tbb != (unsigned long) (0xFFFF)) &&
							(tbb != (unsigned long) (0x0000))) {
						} else { sz = 0;}
					}
					if (sz) {
						vFTicFieldSetBit(criteria,ifield);
						memcpy((char *)tmpbuf,(char *)tbbuf, sz);
						tmpbuf += sz;
					};
					vFTicFieldSetBit(filter,ifield); tbbuf += 1 + 6 + 2;
				} break;

				case (TYPE_I16):
				case (TYPE_U16): {
					unsigned short tbb;
					U16p_TO_U16(tbbuf,tbb);
					if ((tbb != (unsigned short) (0xFFFF)) &&
						(tbb != (unsigned short) (0x0000))) {
						memcpy((char *)tmpbuf,(char *)tbbuf,2);
						vFTicFieldSetBit(criteria,ifield);
						tmpbuf += 2;
				    };
					vFTicFieldSetBit(filter,ifield);
				    tbbuf += 2;
				} break;

				case (TYPE_SDMYhmsU24): {
					sz= 1 + 6 + 3;
					if ( *((unsigned char*)tbbuf)  != '^') {
					} else 	if (tic_check_u8datearray_criteria(tbbuf+1,6) != 0) {
					} else	{
						unsigned long tbb;
						U24p_TO_U32((tbbuf + 1 + 6),tbb);
						if ((tbb != (unsigned long) (0xFFFFFF)) &&
							(tbb != (unsigned long) (0x000000))) {
						} else { sz = 0;}
					}
					if (sz) {
						vFTicFieldSetBit(criteria,ifield);
						memcpy((char *)tmpbuf,(char *)tbbuf, sz);
						tmpbuf += sz;

					};
					vFTicFieldSetBit(filter,ifield); tbbuf += 1 + 6 + 3;
				} break;

				case (TYPE_4U24):
				case (TYPE_6U24):
				case (TYPE_U24): {
					unsigned long tbb;
					U24p_TO_U32(tbbuf,tbb);
					if ((tbb != (unsigned long) (0xFFFFFF)) &&
						(tbb != (unsigned long) (0x000000))) {
						memcpy((char *)tmpbuf,(char *)tbbuf,3);
						vFTicFieldSetBit(criteria,ifield);
						tmpbuf += 3;
				    };
					vFTicFieldSetBit(filter,ifield);
				    tbbuf += 3;
				} break;

				case (TYPE_U32):{
					unsigned long tbb;
					U32p_TO_U32(tbbuf,tbb);
					if ((tbb != (unsigned long) (0xFFFFFFFF)) &&
						(tbb != (unsigned long) (0x00000000))) {
						memcpy((char *)tmpbuf,(char *)tbbuf,4);
						vFTicFieldSetBit(criteria,ifield);
						tmpbuf += 4;
				    };
					vFTicFieldSetBit(filter,ifield);
				    tbbuf += 4;
				} break;

				case (TYPE_FLOAT):{
					float tbb;
					FLTp_TO_FLT(tbbuf,tbb);
					if (tbb != 0.0) {
						memcpy((char *)tmpbuf,(char *)tbbuf,4);
						vFTicFieldSetBit(criteria,ifield);
						tmpbuf += 4;
					};
					vFTicFieldSetBit(filter,ifield);
					tbbuf += 4;
				} break;

				case (TYPE_BF32xbe): {
					if (*((unsigned long*)tbbuf) != (unsigned long) (0x00000000)) {
						memcpy((char *)tmpbuf,(char *)tbbuf,4);
						vFTicFieldSetBit(criteria,ifield);
						tmpbuf += 4;
					}
					vFTicFieldSetBit(filter,ifield);
					tbbuf += 4;
				}
				break;

				case (TYPE_BF8d):{
				    if (*tbbuf != (unsigned char) (0x00)){
						*tmpbuf = *tbbuf;
						vFTicFieldSetBit(criteria,ifield);
						tmpbuf += 1;
				    };
					vFTicFieldSetBit(filter,ifield);
				    tbbuf += 1;
				}
				break;

				case (TYPE_HEXSTRING): {
					if (*tbbuf != 0) { // Criteria dded only if not an empty string
						memcpy((char *)tmpbuf,(char *)tbbuf,(*tbbuf) + 1);
						vFTicFieldSetBit(criteria,ifield);
						tmpbuf += (*tbbuf) +1;
					}
					vFTicFieldSetBit(filter,ifield);
					tbbuf += (*tbbuf) +1;
				}
				break;

				case (TYPE_SDMYhms):
					sz= 1 + 6;
					if ( *((unsigned char*)tbbuf)  != '^') {
					} else 	if (tic_check_u8datearray_criteria(tbbuf+1,6) != 0) {
					} else { sz = 0;};
					if (sz) {
						vFTicFieldSetBit(criteria,ifield);
						memcpy((char *)tmpbuf,(char *)tbbuf,sz);
						tmpbuf += sz;
					}
					vFTicFieldSetBit(filter,ifield);
					tbbuf += 1 + 6;
				break;

				case (TYPE_DMYhms):
					sz = 6;
					goto lbl_process_date_field1;


				case (TYPE_tsDMYhms): {
					// NEW encoding using Timestamp
					unsigned long tbb;
					U32p_TO_U32(tbbuf,tbb);
					if ( ((tbb != (unsigned long) (0xFFFFFFFF)) &&
						  (tbb != (unsigned long) (0x00000000))
						 )
						){
						memcpy((char *)tmpbuf,(char *)tbbuf,4);
						vFTicFieldSetBit(criteria,ifield);
						tmpbuf += 4;
					};
					vFTicFieldSetBit(filter,ifield);
					tbbuf += 4;
				} break;

				case (TYPE_DMYhmsCSTRING):
					sz = 6;
					len = strlen((char *)tbbuf+sz)+1;
					if ((tic_check_u8datearray_criteria(tbbuf, sz) != 0) || (len > 1)){
						vFTicFieldSetBit(criteria,ifield);
						memcpy((char *)tmpbuf,(char *)tbbuf,sz+len);
						tmpbuf += sz+len;
					}
					vFTicFieldSetBit(filter,ifield);
					tbbuf += (sz+len);
				break;

				case (TYPE_E_PT):
				case (TYPE_E_DIV):
				case (TYPE_E_CONTRAT):
		        case (TYPE_E_STD_PT):
		        case (TYPE_E_STD_CONTRAT):
					len = tic_enum_len(tbbuf);
					if (*(tbbuf) != E_COMMON_NO_CHECK) {
						memcpy((char *)tmpbuf,(char *)tbbuf,len);
						vFTicFieldSetBit(criteria,ifield);
						tmpbuf += len;
					}
					vFTicFieldSetBit(filter,ifield);
					tbbuf += len;
				break;

				case (TYPE_U24_E_DIV): {
					// NEW encoding using Timestamp and periode tarifaire compression
					unsigned long tbb;
					len = 3 + tic_enum_len(tbbuf + 3);
					U24p_TO_U32(tbbuf,tbb);
					if ( ((tbb != (unsigned long) (0xFFFFFF)) &&
						  (tbb != (unsigned long) (0x000000))
						 ) ||
						 (*(tbbuf+3) != E_COMMON_NO_CHECK)
						){
						memcpy((char *)tmpbuf,(char *)tbbuf,len);
						vFTicFieldSetBit(criteria,ifield);
						tmpbuf += len;
					};
					vFTicFieldSetBit(filter,ifield);
					tbbuf += len;
				}
				break;

				case (TYPE_tsDMYhms_E_PT): {
					// NEW encoding using Timestamp and periode tarifaire compression
					unsigned long tbb;
					len = 4 + tic_enum_len(tbbuf + 4);
					U32p_TO_U32(tbbuf,tbb);
					if ( ((tbb != (unsigned long) (0xFFFFFFFF)) &&
						  (tbb != (unsigned long) (0x00000000))
						 ) ||
						 (*(tbbuf+4) != E_COMMON_NO_CHECK)
						){
						memcpy((char *)tmpbuf,(char *)tbbuf,len);
						vFTicFieldSetBit(criteria,ifield);
						tmpbuf += len;
					};
					vFTicFieldSetBit(filter,ifield);
					tbbuf += len;
				} break;

				case (TYPE_U24CSTRING):
					sz = 3;
					unsigned long tbb;
					U24p_TO_U32(tbbuf,tbb);
					len = strlen((char *)tbbuf+sz)+1;
					if (((tbb != (unsigned long) (0xFFFFFF)) &&
						 (tbb != (unsigned long) (0x000000))
						) ||
						(len > 1)
					   ) {
						memcpy((char *)tmpbuf,(char *)tbbuf, len+sz);
						vFTicFieldSetBit(criteria,ifield);
						tmpbuf += len+sz;
					}
					vFTicFieldSetBit(filter,ifield);
					tbbuf += (len+sz);

				break;

				case (TYPE_hmDM):
					sz = 4; goto lbl_process_date_field1;
				case (TYPE_DMh):
					sz = 3; goto lbl_process_date_field1;
				case (TYPE_hm):
					sz = 2;
lbl_process_date_field1:
					if (tic_check_u8datearray_criteria(tbbuf, sz) != 0) {
						vFTicFieldSetBit(criteria,ifield);
						memcpy((char *)tmpbuf,(char *)tbbuf,sz);
						tmpbuf += sz;
					}
					vFTicFieldSetBit(filter,ifield);
					tbbuf += sz;

				break;

				default:
					// This case should never occurs
				break;
			} // switch (expected_fields[j].type)
		} // if (ucFTicFieldGetBit(tbdesc,ifield) != 0)
		ifield++;
	} // while (nfield-- > 0)

	// Set the size of the frame at the end of buffers
	*((unsigned short *)&(buf[buf_size - TIC_SERIALIZED_SIZE_SIZE])) = (unsigned short) (tmpbuf - buf);

	return(tmpbuf - buf);
}

//--------------------------------------------------------------------------------
// New descriptor and buffer management functions, since compressable descriptor
//--------------------------------------------------------------------------------
void vFTicBufInitFromHeader(TIC_BUF_TYPE *ba, TIC_BUF_TYPE dh) {
	TIC_BUF_TYPE type=aGET_DESCPTR_TYPE(&dh);
	TIC_BUF_TYPE size=aGET_DESCPTR_SIZE(&dh);

	if (type == aDESC_TYPE_VAR_BITS_FIELD) { // Bit fields case setting
		memset(&ba[1], 0x00,size - 1);

	} else if (type == aDESC_TYPE_VAR_INDEX) { // Index case setting
		int i;
		// Notice 0xFF used to define an UNDEFINED index
		for (i=1; i < size; i++) ba[i] = 0xFF;

	}

	ba[0] = dh; // Set Header part
}

void vFTicBufInitFromHeaderValues(TIC_BUF_TYPE *ba,
		unsigned char obsolete,	unsigned char is_shifted_or_lrv,
		unsigned char type, unsigned char size) {

	if (type == aDESC_TYPE_VAR_BITS_FIELD) { // Bit fields case setting
		memset(ba, 0x00, size);

	} else if (type == aDESC_TYPE_VAR_INDEX) { // Index case setting
		int i;
		// Notice 0xFF used to define an UNDEFINED index
		for (i=1; i < size; i++) ba[i] = 0xFF;

	}
	// Set header
	aDESCPTR_HEADER_INIT_FROM_VALUES(ba,obsolete,is_shifted_or_lrv,type,size);
}

unsigned char ucFTicFieldGetBit(TIC_BUF_TYPE *ba,unsigned char fnum) {
	// TODO: Very slow API. MAY HAVE TO BE OPTIMIZED contextually wher it is used
	// ie: Avoiding multiple indirection [], and initialisations aGET*, and type test, when not needed

	if (ba == NULL) return 0;

	TIC_BUF_TYPE type=aGET_DESCPTR_TYPE(ba);
	TIC_BUF_TYPE size=aGET_DESCPTR_SIZE(ba);

	if (type == aDESC_TYPE_VAR_BITS_FIELD) { // Bit fields case setting

		if ((size -1) - (((unsigned char)fnum)>>3) < 1) return 0; // fnum after end of descriptor

		return ((ba)[(size -1) - (((unsigned char)fnum)>>3)]  &  (((unsigned char)(0x01)) << (((unsigned char)fnum)%8)));

	} else if (type == aDESC_TYPE_VAR_INDEX) { // Index case setting
		int i;
		for (i=1; i < size; i++) if (ba[i] == fnum) return (1); // Bit is set
		return(0); // Not found, bit not set

	}
	return (0); // Unexpected case (Should not occur) !!!
}

void vFTicFieldSetBit(TIC_BUF_TYPE *ba,unsigned char fnum) {

	if (ba != NULL) {

		TIC_BUF_TYPE type=aGET_DESCPTR_TYPE(ba);
		TIC_BUF_TYPE size=aGET_DESCPTR_SIZE(ba);

		if (type == aDESC_TYPE_VAR_BITS_FIELD) { // Bit fields case setting

			if (! ((size -1) - (((unsigned char)fnum)>>3) < 1)) // Not fnum after end of descriptor
				(ba)[(size -1) - (((unsigned char)fnum)>>3)] |=  (((unsigned char)(0x01)) << (((unsigned char)fnum)%8)); // Set bit at right position

		} else if (type == aDESC_TYPE_VAR_INDEX) { // Index case setting

			int i;
			for (i=1; i < size; i++) if (ba[i] == 0xFF) { // Set value in the first free slot
				ba[i] = fnum;
				break;
			}
		}
	}
}

void vFTicFieldClrBit(TIC_BUF_TYPE *ba,unsigned char fnum) {

	if (ba != NULL) {

		TIC_BUF_TYPE type=aGET_DESCPTR_TYPE(ba);
		TIC_BUF_TYPE size=aGET_DESCPTR_SIZE(ba);

		if (type == aDESC_TYPE_VAR_BITS_FIELD) { // Bit fields case setting

			if (! ((size -1) - (((unsigned char)fnum)>>3) < 1)) // Not fnum after end of descriptor
				(ba)[(size -1) - (((unsigned char)fnum)>>3)] &=  ~(((unsigned char)(0x01)) << (((unsigned char)fnum)%8)); // Set bit at right position

		} else if (type == aDESC_TYPE_VAR_INDEX) { // Index case setting

			int i;
			for (i=1; i < size; i++) if (ba[i] == fnum) { // Set value in the first free slot
				ba[i] = 0xFF;
				break;
			}
		}
	}
}

signed char cFTicCompressDesc(TIC_BUF_TYPE *bin,TIC_BUF_TYPE *bout, unsigned char forceBitFieldAndSize) {

	//---------------------------------------------------------------------------------------------------
	// First estimate resulting descriptors size depending on new descriptor compression specifications
	signed short lastFieldNum = -1;
	unsigned short nbByteBitField = 0, nbByteVarIndex = 0;
	unsigned char nbBitBitfield, ifield=0;

	if (aGET_DESCPTR_TYPE(bin) == aDESC_TYPE_VAR_BITS_FIELD) {
		nbBitBitfield=(aGET_DESCPTR_SIZE(bin) -1) * 8; // Parse all bits of bytes of decriptor

		while (nbBitBitfield-- > 0) {
			if (ucFTicFieldGetBit(aTB_GET_DESC(bin),ifield) != 0) {
				// Evaluate BITFIELD DESC size
				lastFieldNum = ifield;
				// Evaluate VARINDEX DESC size
				nbByteVarIndex++;
			}
			ifield++;
		}

	} else { /* aDESC_TYPE_VAR_INDEX */
		nbByteVarIndex = aGET_DESCPTR_SIZE(bin) - 1;

		if ( nbByteVarIndex > 0) {
			lastFieldNum = bin[nbByteVarIndex];
		}

	}

	nbBitBitfield  = lastFieldNum+1;
	nbByteBitField = (nbBitBitfield / 8) + ((nbBitBitfield % 8) > 0 ? 1 : 0); // Calculate the resulting number of necessary bytes to encode until "last field"
	nbByteVarIndex++; nbByteBitField++; // Add 1 byte of header part

	//---------------------------------------------------------------------------------------------------
	// Then compress decriptor from bin to bout using the smaller one
	aSET_DESCPTR_OBSOLETE(bout, aGET_DESCPTR_OBSOLETE(bin));
	aSET_DESCPTR_SRPT_OR_LRVREQ(bout, aGET_DESCPTR_SRPT_OR_LRVREQ(bin));
	if (forceBitFieldAndSize) { //
		if (nbByteBitField > forceBitFieldAndSize) return -1; // Impossible to store desc in ORIGINAL Size (8)
		nbByteBitField = forceBitFieldAndSize;
		aSET_DESCPTR_TYPE(bout, aDESC_TYPE_VAR_BITS_FIELD);
		aSET_DESCPTR_SIZE(bout, nbByteBitField);  // For original format will have to be set to 0 before at the end

	} else if (nbByteBitField < nbByteVarIndex) { // Var bitfield size selected/best
		aSET_DESCPTR_TYPE(bout, aDESC_TYPE_VAR_BITS_FIELD);
		aSET_DESCPTR_SIZE(bout, nbByteBitField);

	} else {
		aSET_DESCPTR_TYPE(bout, aDESC_TYPE_VAR_INDEX);
		aSET_DESCPTR_SIZE(bout, nbByteVarIndex);
	}

	// Initialize all Descriptor remaining descriptor (memset to 0 or set indexes ti 0xFF)
	vFTicBufInitFromHeader(bout, *bout);

	//---------------------------------------------------------------------------------------------------
	// Now set all bits in bout decriptor
	ifield=0; // nfield was recalculated before just for necessary number of fields to parse
	while (nbBitBitfield-- > 0) {
		if (ucFTicFieldGetBit(aTB_GET_DESC(bin),ifield) != 0) {
			vFTicFieldSetBit(aTB_GET_DESC(bout),ifield);
		}
		ifield++;
	}

	return 0;
}

unsigned char ucTICDescPtrConvertFromOriginalHeader(TIC_BUF_TYPE *ba) {
	// Acept conversion olny if is a VarBitField with 0 length is an original BitField
	// In thant conversion it is not "necessary" to convert folowwing fields
	TIC_BUF_TYPE type=aGET_DESCPTR_TYPE(ba);
	TIC_BUF_TYPE size=aGET_DESCPTR_SIZE(ba);

	if (type == aDESC_TYPE_VAR_BITS_FIELD)
		if (size == 0)  {
			aSET_DESCPTR_SIZE(ba,aTIC_DESC_NB_BYTES_ORIGINAL);
			return(1);
		}
	// No conversion needed (the client has sent a correct frame to interpret)
	return(0);
}

//----------------------------------------------------------------------------
signed short iFTicGetLastField(TIC_BUF_TYPE *bin) {
	signed short lastFieldNum = -1;
	unsigned char nbBitBitfield, ifield=0;

	if (aGET_DESCPTR_TYPE(bin) == aDESC_TYPE_VAR_BITS_FIELD) {
		nbBitBitfield=(aGET_DESCPTR_SIZE(bin) -1) * 8; // Parse all bits of bytes of decriptor

		while (nbBitBitfield-- > 0) {
			if (ucFTicFieldGetBit(aTB_GET_DESC(bin),ifield) != 0) {
				// Evaluate BITFIELD DESC size
				lastFieldNum = ifield;
			}
			ifield++;
		}

	} else { /* aDESC_TYPE_VAR_INDEX */
		if ( aGET_DESCPTR_SIZE(bin) > 0) lastFieldNum = bin[aGET_DESCPTR_SIZE(bin) - 1];

	}
	return(lastFieldNum);
}




