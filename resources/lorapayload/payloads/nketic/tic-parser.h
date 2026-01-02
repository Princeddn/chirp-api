#ifndef _TIC_PARSER_H_
#define _TIC_PARSER_H_

#include "tic-tools.h"

typedef enum
{
	PEND_STX,
	PEND_LF,
	PEND_LABEL,
	PEND_VALUE,
	PEND_CHECKSUM,
	PEND_CR,
	PEND_PROCESS,
	STOPPED,
	PEND_PROCESS_ONE_GROUP
} TIC_parser_states_t;


typedef struct
{
	// Variable used for Meter type search if needed (Cf
	TIC_meter_type_t mt_finder;

	// Currently selected meter descriptor ==> Frame format
	TIC_meter_descriptor_t * pt_tic_descriptor;

	// Other working parameters
	unsigned char chksum_check;
	unsigned char strict; // Dos not allow jumping over unexpected/undefined attributes
	unsigned char nb_field_to_valid_frame;

	// Space for parsed data
	TIC_BUF_TYPE pt_tic_buf_space[TIC_BIG_PACKED_BUF_SZ + 2];

    // General buffer start position : Must be inited pointing on pt_tic_buf_space
	TIC_BUF_TYPE *pt_tic_buf;

    // Sub buffers ICE case : Must be inited pointing on pt_tic_buf_space
	TIC_BUF_TYPE *ice_p_pt_tic_buf;
	TIC_BUF_TYPE *ice_p1_pt_tic_buf;

	// Current parser state information
	unsigned char one_group_found;    // Since PMEPMI (many baud rates) start waiting for a valid GROUP before waiting for a full TIC FRAME
	TIC_parser_states_t parser_state; // Current parser state
	unsigned char *pt_tic_buf_buf;    // Current free position in tic_buffer storage
	unsigned char no_field;           // Current field in descriptor

	// Sub parser state ICE case
	unsigned char *ice_p_pt_tic_buf_buf;    // Current free position in tic_buffer storage
	unsigned char ice_p_no_field;           // Current field in descriptor
	unsigned char ice_p_block_initialised;  // Current state of Energy/period block parsing

	unsigned char *ice_p1_pt_tic_buf_buf;   // Current free position in tic_buffer storage
	unsigned char ice_p1_no_field;       	// Current field in descriptor
	unsigned char ice_p1_block_initialised;  // Current state of Energy/period block parsing

	// Used/Updated on end of frame completion
	unsigned char tic_meter_type_discovered;
	unsigned short tic_input_frame_size;
} TIC_parser_status_t;

//----------------------------------------------------------------------------
// Get the current meter-type
TIC_meter_type_t tic_parser_get_meter_type();
unsigned char tic_parser_get_group_found();
void tic_parser_set_group_found(unsigned char group_found_value);

//----------------------------------------------------------------------------
// The call back function for frame recpetion must be initialized by the client
void tic_parser_set_frame_rx_handler(void (*f)(TIC_parser_status_t * stat));

//----------------------------------------------------------------------------
// TIC input parsing management
void tic_parser_init(
	TIC_meter_descriptor_t * tic_desc,
	unsigned char chks_check,
	unsigned char strict,
	unsigned char nbfv);
void tic_parser_reset();
void tic_parser_set_chksum_check(unsigned char chks_check);
void tic_parser_set_nb_field_to_valid(unsigned char nbf);

int tic_parser_input_char(unsigned char c);



//----------------------------------------------------------------------------
// New 04/2018
// MANAGE Err Log for remote debugging
typedef enum {
	TIC_ERR_NO_ERR = 0,
	TIC_ERR_UNEXPECTED_LABEL,
	TIC_ERR_BAD_CHECKSUM,
	TIC_ERR_EOT,
	TIC_ERR_BAD_EOL,
	TIC_ERR_NOT_ENOUGH_FIELDS,
	TIC_ERR_MISSING_MANDATORY,
	TIC_ERR_MISSING_RX_HANDLER,
	TIC_ERR_LABEL_TOO_LONG,
	TIC_ERR_VALUE_TOO_SHORT,
	TIC_ERR_VALUE_TOO_LONG
} TICErrLogCodes_t;

#define TIC_ERR_BUF_SIZE  200
void vF_tic_parser_err_log(TICErrLogCodes_t ucErrCode);
unsigned short usF_tic_parser_err_log_cp_len_from(unsigned char * pucDest, unsigned short usLen, unsigned short usFrom );

#endif //  _TIC_PARSER_H_
