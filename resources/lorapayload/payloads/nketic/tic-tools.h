#ifndef _TIC_TOOLS_H_
#define _TIC_TOOLS_H_

#include <time.h>

#if ( STD_ZCL == 1 )

#if WITH_BATCH_REPORT==1
#include "zcl-batch-periodic-report.h"
#endif

#else

#if WITH_BATCH_REPORT==1
#include "zcd-batch-periodic-report.h"
#endif

#endif


// -- Character constants used to parse or format TIC Frames -------------------------------
#ifdef TIC_TOOLS_FAKE_ETX_STX
	// No ETX/STX for minimal-net or console line input test
	// TODO: Thes mode may cause dysfunctions .. think about it when viewing/testing results
	#define	STX				'<'
	#define	ETX				'>'
	#define EOT 			0x04 // '!' : Dangerous for test with CRC. Uncomment to test EOT
#else
	#define	STX				0x02 /* Start of stream */
	#define	ETX				0x03 /* End of stream */
	#define EOT 			0x04 /* End of transmission => interruption de transmission */
#endif

#define	LF				0x0A
#define	CR				0x0D
#define	DELIM			0x20
#define	DELIM_STD		0x09

// -- I16<=>I16 Big Endian conversions (ignoring compilator alignement) -------------------------------------
#define I16_TO_I16p(i16,i16p) { \
	i16p[1] = (i16 & 0xFF); \
	i16p[0] = (i16 >> 8 ) & 0xFF ; \
}

#define I16p_TO_I16(i16p,i16) { \
	i16  = i16p[0]; i16 <<= 8; \
	i16 += i16p[1]; \
}
// -- U16<=>U16 Big Endian conversions (ignoring compilator alignement) -------------------------------------
#define U16_TO_U16p(u16,u16p) { \
	u16p[1] = (u16 & 0xFF); \
	u16p[0] = (u16 >> 8 ) & 0xFF ; \
}

#define U16p_TO_U16(u16p,u16) { \
	u16  = u16p[0]; u16 <<= 8; \
	u16 += u16p[1]; \
}

// -- U32<=>U24 Big Endian conversions  (ignoring compilator alignement) -------------------------------------
#define U32_TO_U24p(u32,u24p) { \
	u24p[2] = (u32 & 0xFF); \
	u24p[1] = (u32 >> 8 ) & 0xFF ; \
	u24p[0] = (u32 >> 16) & 0xFF ; \
}

#define U24p_TO_U32(u24p,u32) { \
	u32  = u24p[0]; u32 <<= 8; \
	u32 += u24p[1]; u32 <<= 8; \
	u32 += u24p[2]; \
}

// -- U32<=>U32 Big Endian conversions (ignoring compilator alignement) -------------------------------------
#define U32_TO_U32p(u32,u32p) { \
	u32p[3] = (u32 & 0xFF); \
	u32p[2] = (u32 >> 8 ) & 0xFF ; \
	u32p[1] = (u32 >> 16) & 0xFF ; \
	u32p[0] = (u32 >> 24) & 0xFF ; \
}

#define U32p_TO_U32(u32p,u32) { \
	u32  = u32p[0]; u32 <<= 8; \
	u32 += u32p[1]; u32 <<= 8; \
	u32 += u32p[2]; u32 <<= 8; \
	u32 += u32p[3]; \
}

// -- FLT<=>FLT(MSP430) conversions (NOTE Depending on compilator/MCU alignement) -------------------------------------
#if ((defined(CPU_USE) && (CPU_USE==MSP430_DEVICE)) || defined(TIC_TOOLS_CODECS))
// BEWARE: Uses MPSP430 default endianess ....
#define FLT_TO_FLTp(flt,fltp) { \
	((unsigned char *)fltp)[3] = ((unsigned char *)&flt)[0]; \
	((unsigned char *)fltp)[2] = ((unsigned char *)&flt)[1] ; \
	((unsigned char *)fltp)[1] = ((unsigned char *)&flt)[2] ; \
	((unsigned char *)fltp)[0] = ((unsigned char *)&flt)[3] ; \
}
#define FLTp_TO_FLT(fltp,flt) { \
	((unsigned char *)&flt)[0] = ((unsigned char *)fltp)[3]; \
	((unsigned char *)&flt)[1] = ((unsigned char *)fltp)[2]; \
	((unsigned char *)&flt)[2] = ((unsigned char *)fltp)[1]; \
	((unsigned char *)&flt)[3] = ((unsigned char *)fltp)[0]; \
}
#else
	#error "TODO: implementation of float conversion for other MCU/compiler !!!"
#endif


// -------------------------------------------------------------------------------
// FIELD DESCRIPTORS and BUFFERS MANAGEMENT
// -------------------------------------------------------------------------------
// String and buffers sizes
//#define STR_VALUE_SZ_MAX	(43+2) //+2 For new Value parsing until CR // 13 // 43 ==> CJE avec le ENERG !!!
#define STR_VALUE_SZ_MAX	(98 + 2 + 2) // Mainly for Linky firlds NJOURF+1, PJOURF+1
#define STR_LABEL_SZ_MAX	(10)

// Fields descriptor sizes
#define aTIC_DESC_MAX_NB_BYTES	(16)
#define aTIC_DESC_MAX_NB_BITS	(8 * aTIC_DESC_MAX_NB_BYTES)
#define aTIC_DESC_NB_BYTES_ORIGINAL	(8) // Kept for compatibility management (compatipility management will have to be managed externally from wtc-tic-process API)
#define aTIC_DESC_NB_BITS_ORIGINAL	(8 * aTIC_DESC_NB_BYTES_ORIGINAL) // MUST be a multiple of 8 (1 byte)

// Managed fields descriptor types:
// In all case the first Byte of RAM for descriptor is a decriptor header
#define aDESC_TYPE_VAR_BITS_FIELD 0 /**< Variables Bitfield descriptor variable lenght bitfield allowing, compression (supression) of all 0 MSB bytes */
#define aDESC_TYPE_VAR_INDEX      1 /**< Variables Indexes descriptor Each byte after the header are an index of field sorted in increasing order (allowing to avoid parsing of already found fileds) */

// Depends on the typeS of meterS that the sensor must manage
// For now the ICE Meter presents the maximum possible size (Cf specifications)
#define TIC_FIELDS_UNPACKED_MAX_SIZE_BUF   160 /* taille max dans le cas des sub descripteurs ICE en accès absolu ! */
#define TIC_FIELDS_PACKED_MAX_SIZE_BUF     120 /* taille max dans le cas des descripteurs packed en général ! */
#define TIC_CRITERIA_PACKED_MAX_SIZE_BUF   14  /* taille max dans le cas des citères !  (disons une date (6 octets) + 2 U32 soit (8 octets) soit 14 octets*/
#define TIC_REPORT_PACKED_MAX_SIZE_BUF     52  /* taille max dans le cas d'un report (disons 2 dates et 10 U32 soit 52 octets) */

// -----------------------------------------------------------------------------------
// Note about size: Think +1  for allocation as last byte for currently used size in buffer
#define TIC_UNPACKED_BUF_SZ (aTIC_DESC_MAX_NB_BYTES + TIC_FIELDS_UNPACKED_MAX_SIZE_BUF)
#define TIC_PACKED_BUF_SZ (aTIC_DESC_MAX_NB_BYTES + TIC_FIELDS_PACKED_MAX_SIZE_BUF)
#define TIC_BIG_PACKED_BUF_SZ \
	((TIC_PACKED_BUF_SZ + TIC_UNPACKED_BUF_SZ + TIC_UNPACKED_BUF_SZ) + 70/* Added for TIC STD */)
// -------------------------------------------------------------------------------------
// Note: For TIC_STD 527 Byte packed required !!!
// => TIG_BIG_PACKED_BUF_SZ must be bigger than 537 bytes + 16 bytes desc ==> 553 Bytes
#if (TIC_BIG_PACKED_BUF_SZ < 553)
	#error Unsuficient space for Big TIC STD packet !!
#endif
// ------------------------------------------------------------------------------------

// two byte (1 short) reserved at end of buffer (space) to store real current buffer size when serialized
#define TIC_SERIALIZED_SIZE_SIZE 2

typedef union {
	unsigned char  u8 [aTIC_DESC_MAX_NB_BYTES];
	unsigned short u16[aTIC_DESC_MAX_NB_BYTES / 2];
	unsigned long  u32[aTIC_DESC_MAX_NB_BYTES / 4];
} TIC_desc_t;



/**
 * \brief General TIC buffer data type
 *
 */
typedef unsigned char TIC_BUF_TYPE;


/**
 * \brief Manages one byte as header of descriptor field of TIC buffer
 *
 * Format DescriptorHeader byte is :
 * b7:    obsolete
 * b6:    shift_rpt or lrv_req depending of context (respectively "in report criteria", in "filter")
 * b5:    type
 * b4-b0: size
 *
 * IMPORTANT:
 * 	"type" field is only one bit defining either simple var bitfield ou var index field.
 *  For compatibility with previous revision, var bit fiels followed by a size of 0 as to be
 *  considered as former orginal fixed size bitfield of 8 Bytes.
 *  THE ORIGINAL format exception is not manage in the wtc-tic-process library,
 *  but MUST be managed in calling programs inputs/outputs(ZCL, tictobin, bintotic, ...)
 *  The only exception is tic_serialize that CAN force an historic desc creation
 *
 *  NOTE:
 *  Obsolete, ISUnpack, Type and Size are always managed as bitfield in a single byte.
 *  As used on radio
 *  Union type could not be used for Endianess garantee
 *
 */
#define aGET_DESCPTR_OBSOLETE(descPtr)  (((*(TIC_BUF_TYPE *)descPtr) & 0x80) == 0 ? 0 : 1)
#define aGET_DESCPTR_SRPT_OR_LRVREQ(descPtr) (((*(TIC_BUF_TYPE *)descPtr) & 0x40) == 0 ? 0 : 1) /* shifted report OR Last report value indicator */
#define aGET_DESCPTR_TYPE(descPtr)      (((*(TIC_BUF_TYPE *)descPtr) & 0x20) == 0 ? aDESC_TYPE_VAR_BITS_FIELD : aDESC_TYPE_VAR_INDEX)
#define aGET_DESCPTR_SIZE(descPtr)      ((*(TIC_BUF_TYPE *)descPtr) & 0x1F)


#define aSET_DESCPTR_OBSOLETE(descPtr,val) {if (val) (*(TIC_BUF_TYPE *)descPtr) |= 0x80; else (*(TIC_BUF_TYPE *)descPtr) &= ~0x80;}
#define aSET_DESCPTR_SRPT_OR_LRVREQ(descPtr,val) {if (val) (*(TIC_BUF_TYPE *)descPtr) |= 0x40; else (*(TIC_BUF_TYPE *)descPtr) &= ~0x40;}
#define aSET_DESCPTR_TYPE(descPtr,val)     {if (val) (*(TIC_BUF_TYPE *)descPtr) |= 0x20; else (*(TIC_BUF_TYPE *)descPtr) &= ~0x20;}
#define aSET_DESCPTR_SIZE(descPtr,val)     {(*(TIC_BUF_TYPE *)descPtr) &= ~0x1F; (*(TIC_BUF_TYPE *)descPtr) |= (val & 0x1F);}


#define aDESCPTR_HEADER_INIT_FROM_VALUES(descPtr, o, i, t, s) { \
	aSET_DESCPTR_OBSOLETE(descPtr,o); \
	aSET_DESCPTR_SRPT_OR_LRVREQ(descPtr,i); \
	aSET_DESCPTR_TYPE(descPtr,t); \
	aSET_DESCPTR_SIZE(descPtr,s); \
}

#define aTB_GET_DESC(tb) (tb)
#define aTB_GET_BUF(tb)  (&(tb[aGET_DESCPTR_SIZE(tb)]))

#define aTB_CRIT_GET_FILTER_DESC(tb) (tb)
#define aTB_CRIT_GET_TRIG_DESC(tb)   (&((tb)[aGET_DESCPTR_SIZE((tb))]))
#define aTB_CRIT_GET_TRIG_BUF(tb)    (&((aTB_GET_BUF((tb)))[aGET_DESCPTR_SIZE(aTB_GET_BUF((tb)))]))

// TIC binary data management
// BEWARE: Following array must be synchronized/coherent with following "TIC_binary_type_t" enum
// BEWARE again: When 0 spécific cases must be managed in tic-tools.c (serialize, deserialise, etc ...)
#define TIC_BINARY_TYPE_SIZE_ARRAY {0,1,0,1,2,2,0,3,3,3,4,4,6,4,0,0,0,0,4,3,2,7,8,9,10,4,0,0,0,0,0,0,1}
typedef enum {
	TYPE_EMPTY = 0,
	TYPE_CHAR,
	TYPE_CSTRING,
	TYPE_U8,
	TYPE_U16,
	TYPE_I16,
	TYPE_U24CSTRING,
	TYPE_U24,
	TYPE_4U24,
	TYPE_6U24,
	TYPE_U32,
	TYPE_FLOAT,
	TYPE_DMYhms,
	TYPE_tsDMYhms,
	TYPE_DMYhmsCSTRING,
	TYPE_E_PT,
	TYPE_E_STD_PT,
	TYPE_tsDMYhms_E_PT,
	TYPE_hmDM,
	TYPE_DMh,
	TYPE_hm,
	TYPE_SDMYhms,
	TYPE_SDMYhmsU8,
	TYPE_SDMYhmsU16,
	TYPE_SDMYhmsU24,
	TYPE_BF32xbe,   /* Bitfield 32 bits heXa Big Endian */
	TYPE_HEXSTRING, /* displayed as hexadecimal string Stored as <Size>+<byte string> */
	TYPE_E_DIV,
	TYPE_U24_E_DIV,
	TYPE_E_CONTRAT,
	TYPE_E_STD_CONTRAT,
	TYPE_11hhmmSSSS, /* New type for PJOURF+1 / PPOINTE of Linky. */
					 /* 11 Blocs of 8 Bytes (hhmmSSSS) space separated values are compressed as follow */
	                 /* hh 1 byte Hour, mm 1 byte Minute, SSSS two bytes bitfield */
	                 /* Notes: */
	                 /* - Delta comparison: */
	                 /*   hh and mm are usual for delta comparison */
	                 /*   SSSS is compared as bitfield each bit set may trig an event if changed */
	                 /* - An unused field is defined as follow: */
					 /*   hh = 0xFF and No other bytes used in the binarized form */
			         /*   "NONUTILE" string in the TIC ASCII format */
	TYPE_BF8d, /* Bitfield de 8 bit with TIC decimal representation (0 à 255) */
	TYPE_END
} TIC_binary_type_t;



typedef struct {
	char label[STR_LABEL_SZ_MAX];
	TIC_binary_type_t type;
	unsigned char attribute;
	const char * fmt;
	unsigned char abs_pos;
} TIC_expected_field_t;

#define ATTRIBUTE_NORMAL 0x00
#define ATTRIBUTE_IS_SUBFIELD 0x01
#define ATTRIBUTE_NOT_MANAGED_FIELD 0x02
#define ATTRIBUTE_ICE_pp1_FIELD 0x04
#define ATTRIBUTE_NON_TIC_FIELD 0x08
#define ATTRIBUTE_REGULAR_EXPR 0x10
#define ATTRIBUTE_NOT_LBL_CASE_SENSITIVE 0x20
#define ATTRIBUTE_MULTI_OCCURENCE_FIELD 0x40 /* Like PREAVIS of ICE General */


#define EXCEPTION_VARIABLE_FIELD "!_vf_"


// -------------------------------------------------------------------------------
// MULTIPLE METER TYPES MANAGEMENT
// -------------------------------------------------------------------------------
typedef enum {
	MT_UNKNOWN=0,
	MT_CT,			// Concentrateur Teleport
	MT_CBEMM,		// Compteur Bleu Electronique Monophasé Multitarif
	MT_CBEMM_ICC,	// Compteur Bleu Electronique Monophasé  Multitarif extension ICC
	MT_CBETM,		// Compteur Bleu Electronique Triphasé Multitarif
	MT_CJE,			// Compteur Jaune
	MT_ICE,			// Compteur Clientelle Emeraude
	MT_STD,			// Compteur TIC Standar	d (Linky)
	MT_PMEPMI,		// Compteur TIC PMEPMI (2010)
	MT_PMEPMI13,	// Compteur TIC PMEPMI (2013)
	MT_NULL,	    // Specific NULL meter type (used for delimiting end of meter type and used for search)

    // Following descriptors are used to manage specifique Energies values for ICE
	MT_ICE_p,      // Compteur Clientelle Emerqude: Energies Period P extract
	MT_ICE_p1,     // Compteur Clientelle Emerqude: Energies Period P-1 extract

	MT_END
} TIC_meter_type_t;

typedef struct {
	const TIC_meter_type_t meter_type;
	const TIC_expected_field_t * expected_fields;
	const unsigned char expected_fields_number;
	const unsigned char first_mandatory_fields_set;
}TIC_meter_descriptor_t;

#define TIC_NB_DESC_TYPE (MT_END)
#define TIC_NB_MANAGED_METER (MT_NULL)


//----------------------------------------------------------------------------
// Some ENUM management CONSTANTS
#define E_COMMON_NOT_FOUND  0 // An undefined enum, used to identify not found enum
#define E_COMMON_ANY        1 // A special index used for "any change" in check_change delta
#define E_COMMON_NO_CHECK   2 // A special index used for "no check" in check_change delta

extern const TIC_meter_descriptor_t tic_meter_descriptor[TIC_NB_DESC_TYPE];

//----------------------------------------------------------------------------
// Various TIC management functions
//----------------------------------------------------------------------------

//----------------------------------------------------------------------------
// ENUMERATED FILEDS management
//----------------------------------------------------------------------------

//==============================================================================
// ENUMERATION MANAGEMENT GENERALIZED FOR PMEPMI fields ------------------------
// Allow enumeration not found, with string restitution if required
#define ENUM_IS_STRING_BIT  (unsigned char)0x80
// ----------------------------------------------------------------------------
#define TABLE_E_COMMON_MAX_STR_SZ (3+1)
#define TABLE_E_COMMON_DECLARATION const char TABLE_E_COMMON[][TABLE_E_COMMON_MAX_STR_SZ]= {"!?!", "*", ""};
#define TABLE_E_COMMON_SZ (sizeof(TABLE_E_COMMON) / TABLE_E_COMMON_MAX_STR_SZ)
// ----------------------------------------------------------------------------
// NOTE: Tables MUST BE Lexicographically ordered !!
//
// Note: Could add some new elements in enums
//  Since dichotomic seach inside enums has been removed
//  BUT starting/existing part of the lists must always be preserved
// ----------------------------------------------------------------------------
#define TABLE_E_DIV_STR_MAX_SZ (8+1)
#define TABLE_E_DIV_DECLARATION const char TABLE_E_DIV[][TABLE_E_DIV_STR_MAX_SZ]= \
{ \
 "  ACTIF","ACTIF","CONSO","CONTROLE","DEP","INACTIF","PROD","TEST","kVA","kW"  \
};
#define TABLE_E_DIV_SZ (sizeof(TABLE_E_DIV) / TABLE_E_DIV_STR_MAX_SZ)
// ----------------------------------------------------------------------------
#define TABLE_E_CONTRAT_STR_MAX_SZ (10+1)
#define TABLE_E_CONTRAT_DECLARATION const char TABLE_E_CONTRAT[][TABLE_E_CONTRAT_STR_MAX_SZ]= \
{ \
 "BT 4 SUP36", "BT 5 SUP36", "HTA 5     ", "HTA 8     ", \
 "TJ EJP    ", "TJ EJP-HH ", "TJ EJP-PM ", "TJ EJP-SD ", "TJ LU     ", \
 "TJ LU-CH  ", "TJ LU-P   ", "TJ LU-PH  ", "TJ LU-SD  ", "TJ MU     ", \
 "TV A5 BASE", "TV A8 BASE" \
};
#define TABLE_E_CONTRAT_SZ (sizeof(TABLE_E_CONTRAT) / TABLE_E_CONTRAT_STR_MAX_SZ)
// ----------------------------------------------------------------------------
#define TABLE_E_PT_STR_MAX_SZ (3+1)
#define TABLE_E_PT_DECLARATION const char TABLE_E_PT[][TABLE_E_PT_STR_MAX_SZ]=\
{ \
 " ? ", \
 "000", "HC", "HCD", "HCE", "HCH", "HH", "HH ", "HP", "HP ", \
 "HPD", "HPE","HPH", "JA", "JA ",  "P","P  ", "PM",   "PM ", "XXX" \
}
#define TABLE_E_PT_SZ (sizeof(TABLE_E_PT) / TABLE_E_PT_STR_MAX_SZ)
//================================================================================================
// Below added in October 2018: as finally PT and CONTRAT are really different for Linky Standards
// Full list of possible values for NGTF and LTARF() have beeb required from Linky Labs
// Add necessary enums when knowns
// ----------------------------------------------------------------------------
#define TABLE_E_STD_PT_STR_MAX_SZ (16+1)
#define TABLE_E_STD_PT_DECLARATION const char TABLE_E_STD_PT[][TABLE_E_STD_PT_STR_MAX_SZ]=\
{ \
 " ? ", \
 "000", "HC", "HCD", "HCE", "HCH", "HH", "HH ", "HP", "HP ", \
 "HPD", "HPE","HPH", "JA", "JA ",  "P","P  ", "PM",   "PM ", "XXX", \
 "INDEX NON CONSO","BASE","HEURE CREUSE","HEURE PLEINE","HEURE NORMALE","HEURE POINTE", \
 "HC BLEU","BUHC","HP BLEU","BUHP","HC BLANC","BCHC","HP BLANC","BCHP", "HC ROUGE","RHC","HP ROUGE","RHP", \
 "HEURE WEEK-END" \
/* Todo: Add necessary Enums when known */ \
}
#define TABLE_E_STD_PT_SZ (sizeof(TABLE_E_STD_PT) / TABLE_E_STD_PT_STR_MAX_SZ)
// ----------------------------------------------------------------------------
#define TABLE_E_STD_CONTRAT_STR_MAX_SZ (16+1)
#define TABLE_E_STD_CONTRAT_DECLARATION const char TABLE_E_STD_CONTRAT[][TABLE_E_STD_CONTRAT_STR_MAX_SZ]=\
{ \
 "BT 4 SUP36", "BT 5 SUP36", "HTA 5     ", "HTA 8     ", \
 "TJ EJP    ", "TJ EJP-HH ", "TJ EJP-PM ", "TJ EJP-SD ", "TJ LU     ", \
 "TJ LU-CH  ", "TJ LU-P   ", "TJ LU-PH  ", "TJ LU-SD  ", "TJ MU     ", \
 "TV A5 BASE", "TV A8 BASE", \
 "BASE","H PLEINE-CREUSE","HPHC","HC","HC et Week-End","EJP","PRODUCTEUR" \
/* Todo: Add necessary Enums when known */ \
}
#define TABLE_E_STD_CONTRAT_SZ (sizeof(TABLE_E_STD_CONTRAT) / TABLE_E_STD_CONTRAT_STR_MAX_SZ)
// ----------------------------------------------------------------------------

// TODO: Beware to change below if another enum string can become bigger
#define TABLES_E_MAX_STR_SZ TABLE_E_STD_CONTRAT_SZ

// ----------------------------------------------------------------------------
// ENUM management functions
// ----------------------------------------------------------------------------
unsigned char   tic_enum_len(unsigned char * the_enum); /*< len of Enum withe header */
int             tic_enum_cmp(unsigned char * e1, unsigned char * e2); /*< 0 if no difference !0 either */
unsigned char   tic_enum_changed(unsigned char * crit, unsigned char * before, unsigned char * after); /*< 1 if there was an accepted change beetween before and after according Criteria */
unsigned char   tic_enum_compress  (TIC_binary_type_t type, unsigned char * pt_str, unsigned char *dest_buf); /*< Compress a string to a specific enumerated type */
unsigned char * tic_enum_uncompress(TIC_binary_type_t type, unsigned char * the_enum);/*< uncompress enum to corresponding string */
// END OF ENUMERATION MANAGEMENT GENERALIZED FOR PMEPMI fields -----------------
//==============================================================================

//----------------------------------------------------------------------------
// TIMESTAMP management
time_t tic_get_timestamp_ref();
time_t tic_get_timestamp_from_DMY_HMS_bytes(unsigned char * date_buf);
struct tm * tic_get_tm_from_timestamp(unsigned long tmp_ulong);


unsigned short tic_frame_rx_expected_max_size(TIC_meter_type_t mt);
TIC_meter_type_t tic_mt_and_aidx_to_mt(TIC_meter_type_t meter_type, unsigned short uiAttrIdx);
TIC_meter_descriptor_t * tic_metertype_to_meterdesc(TIC_meter_type_t mt);

void tic_set_expfields_on_label(const TIC_expected_field_t ** hndl_expfields, unsigned char * nb_expfields, char * label);

/**
 * \brief Find meter descriptor according pt_expected_fields and current field found.
 *
 * It is a running algorithm finding progressively meterdesc
 * Note: NOT REENTRANT function (using a static) only used in tic_parser !!!
 * pt_expfields == NULL case must be used to initialise rt_find_meter_desc search
 * Must be called with found field_number that may precise the meter type
 *
 * \param [IN/OUT] mt_finder Ptr on current meter type the pointed value will change during meter type search
 * \param [IN ]    pt_expfields Ptr on current expected fields (should had be found during parsing of first received label)
 * \param [IN ]    field_number the last field number found that is used for meter identification
 *
 */
// d_number);
void rt_find_meter_desc(TIC_meter_type_t * mt_finder, const TIC_expected_field_t * pt_expfields, unsigned char field_number);

unsigned char tic_str_compute_checksum(char * strbuf);
unsigned char tic_nb_fields_selected(TIC_desc_t * desc);
unsigned char * tic_get_value_at_index(TIC_meter_descriptor_t * pt_tic_descriptor,
				TIC_BUF_TYPE *tb,
				unsigned char idx,
				unsigned char src_is_unpacked);

#if WITH_BATCH_REPORT==1
bm_sample_type_t tic_br_type_at_index(
	TIC_expected_field_t * expected_fields,
	unsigned char fid);

void * tic_br_sample_and_type_at_index(TIC_meter_descriptor_t * pt_tic_descriptor,
	TIC_BUF_TYPE *tb,
	unsigned char idx,
	bm_sample_t *s,
	bm_sample_type_t *st,
	unsigned char tb_is_unpacked);
#endif


int strcmp_nocasesensitive(const char *s1, const char *s2);

unsigned char tic_generic_string_match(unsigned char * sgen,unsigned char * s);
unsigned char tic_check_changes(TIC_meter_descriptor_t * pt_tic_descriptor,
				TIC_BUF_TYPE *tbcrit,
				TIC_BUF_TYPE *tbbefore,unsigned char tbbefore_unpacked,
				TIC_BUF_TYPE *tbafter,unsigned char tbafter_unpacked,
				TIC_desc_t * result);

signed short tic_serialize(TIC_meter_descriptor_t * pt_tic_descriptor,
	unsigned char* buf,
	TIC_BUF_TYPE *tb,
	TIC_desc_t * desc_filter,
	TIC_desc_t * desc_filter_or,
	short buf_size,
	unsigned char src_is_unpacked,
	char forceBitFieldAndSize);

signed short tic_serialize_report_criteria(TIC_meter_descriptor_t * pt_tic_descriptor,
	unsigned char* buf,
	TIC_BUF_TYPE *tb,
	short buf_size,
	unsigned char tb_is_unpacked);

// Added for corresponding specific conversion in tic-parser.c
extern const char FMT_02X[];

//--------------------------------------------------------------------------------
// New descriptor and buffer management functions, since compressable descriptor
//--------------------------------------------------------------------------------
/**
 * \brief Init buffer according to passed Descriptor header
 *
 * This function may process the 3 types of descriptors:
 * aDESC_TYPE_BITS_FIELD, aDESC_TYPE_VAR_BITS_FIELD and aDESC_TYPE_VAR_INDEX
 *
 * \param [IN] ba Buffer of bits or indexes to process
 * \param [IN] dh Descriptor header used for initialisation
 *
 */
void vFTicBufInitFromHeader(TIC_BUF_TYPE *ba, TIC_BUF_TYPE dh);

/**
 * \brief Init buffer according to passed Descriptor header values
 *
 * \param [IN] ba Buffer of bits or indexes to process
 * \param [IN] obsolete Indicate if buffer is obsolete
 * \param [IN] isunpack Indicate if buffer is isunpack
 * \param [IN] type Indicate buffer is type
 * \param [IN] size Indicate buffer is size
 *
 */
void vFTicBufInitFromHeaderValues(TIC_BUF_TYPE *ba,
		unsigned char obsolete,	unsigned char isunpack,
		unsigned char type, unsigned char size);
/**
 * \brief Test if a bit is set in a byte string or list of bit indexes
 *
 * This function may process the 3 types of descriptors:
 * aDESC_TYPE_BITS_FIELD, aDESC_TYPE_VAR_BITS_FIELD and aDESC_TYPE_VAR_INDEX
 *
 * \param [IN] ba Buffer of bits or indexes to process
 * \param [IN] fnum field num to test
 *
 * \return
 *    0 : Bit at position is not set
 * 	  -1: Bit at position is set
 *
 */
unsigned char ucFTicFieldGetBit(TIC_BUF_TYPE *ba,unsigned char fnum);

/**
 * \brief Set a bit in bitfield or list of bit indexes
 *
 * This function may process the 3 types of descriptors:
 * aDESC_TYPE_BITS_FIELD, aDESC_TYPE_VAR_BITS_FIELD and aDESC_TYPE_VAR_INDEX
 *
 * The
 *
 * \param [IN] ba Buffer of bits or indexes to process
 * \param [IN] fnum field num to test
 *
 */
void vFTicFieldSetBit(TIC_BUF_TYPE *ba,unsigned char fnum);

/**
 * \brief Set a bit in bitfield or list of bit indexes
 *
 * This function may process the 3 types of descriptors:
 * aDESC_TYPE_BITS_FIELD, aDESC_TYPE_VAR_BITS_FIELD and aDESC_TYPE_VAR_INDEX
 *
 * The
 *
 * \param [IN] ba Buffer of bits or indexes to process
 * \param [IN] fnum field num to test
 *
 */
void vFTicFieldClrBit(TIC_BUF_TYPE *ba,unsigned char fnum);

/**
 * \brief Compress decriptor if possible from IN to OUT
 *
 * IN and OUT must be allocated outside AND must be differents buffers
 *
 * \param [IN] bin Descriptor ptr to process
 * \param [IN] bout Point on Resulting Descriptor
 * \param [IN] forceBitFieldAndSize Force bitfield of required size in bout (not really compressed)
 *
 * return -1 if error
 */
signed char cFTicCompressDesc(TIC_BUF_TYPE *bin,TIC_BUF_TYPE *bout, unsigned char forceBitFieldAndSize);

/**
 * \brief Modify header to a correct new header if the client application has sent an original Descriptor (8 Byte withour size)
 *
 * Conversion is done only it an original Descriptor is in dh Ptr
 *
 * \param [IN ] dh Ptr on descriptor header taht has to be converted
 *
 * return 1 if conversion done
 *        0 if conversion not needed
 */
unsigned char ucTICDescPtrConvertFromOriginalHeader(TIC_BUF_TYPE *ba);

/**
 * \brief Find last field num that exists in descriptor
 *
 * \param [IN ] bin Ptr on descriptor header
 *
 * return >=0 Last field in descriptor
 *        <0 No field selected
 */
signed short iFTicGetLastField(TIC_BUF_TYPE *bin);



#endif // _TIC_TOOLS_H_
