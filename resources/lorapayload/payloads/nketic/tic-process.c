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
 * 		TIC stream processor with timeout management
 * \author
 *      P.E. Goudet <pe.goudet@watteco.com>
 */

/*============================ INCLUDE =======================================*/

#include "contiki-conf.h"
#ifdef CL430_COMPILER
	#include <stdint.h>
	#include "io_cl430.h"
#elif (CPU_USE==ATMEGA_DEVICE)
	#include <io.h>
#endif

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#include "tic-process.h"
#include "tic-tools.h"

#if (WITH_PIN_TEST==1)
#include "wtc_pin_test.h"
#include "system/timer.h" // PEG: Should be in board.h, not already ported
#endif
	
long tic_last_buf_date = 0;
process_event_t tic_frame_event_message;

void (*tic_process_frame_rx_handler)(TIC_parser_status_t * stat) = NULL;

/*---------------------------------------------------------------------------*/
PROCESS(tic_process_process, "TIC process");
/*---------------------------------------------------------------------------*/
 
//============================================================================
void tic_process_set_frame_rx_handler(void (*f)(TIC_parser_status_t * stat)) {
	tic_process_frame_rx_handler = f;
}


//---------------------------------------------------------------------------
// Call back to manage a timeout of frame waiting => reseting the parser that could be "stucked" ?
struct ctimer tic_process_timeout;
static clock_time_t tic_event_seconds_timeout = TIC_EVENT_MINIMAL_SECOND_TIMEOUT; // default value
void handle_tic_process_timeout(void *ptr)
{
// printf("PARSER TIMEOUT !\n");
	tic_parser_reset();
	ctimer_set(&tic_process_timeout, tic_event_seconds_timeout * CLOCK_SECOND, handle_tic_process_timeout, NULL);
}

//---------------------------------------------------------------------------
// Set timeout for tic events in process
void tic_process_set_event_seconds_timeout(clock_time_t nb_seconds) {

	tic_event_seconds_timeout =
		(nb_seconds > TIC_EVENT_MINIMAL_SECOND_TIMEOUT ? nb_seconds : TIC_EVENT_MINIMAL_SECOND_TIMEOUT);

	if (! ctimer_expired(&tic_process_timeout)) // Restart timer with new time if running
		ctimer_set(&tic_process_timeout, tic_event_seconds_timeout * CLOCK_SECOND, handle_tic_process_timeout, NULL);
}

//---------------------------------------------------------------------------
// Call back for parser used to make longer processing "deferred"
void tic_parser_frame_rx_tic_buf(TIC_parser_status_t * stat) {
	process_post(&tic_process_process, tic_frame_event_message , (process_data_t)stat);
}

//---------------------------------------------------------------------------
void tic_process_reset(TIC_meter_type_t mt) {
	// se tic-tools.h for available meter types
				
	// MT_NULL: Meter type will be discovered with first valid frame
	// 1 : Validate TIC record on ending checksum
	// 2 : Validate a record if 2 recods at least are received
	mt = (((mt <= MT_NULL) && (mt >= MT_UNKNOWN)) ? mt : MT_NULL);
// printf("process reset: mt = %d\n",mt);	

	unsigned char ucBitsTICOptions;
	rom_read_TIC_options(&ucBitsTICOptions);
	tic_parser_init(tic_metertype_to_meterdesc(mt),
			((ucBitsTICOptions & 0x01) != 0),
			((ucBitsTICOptions & 0x02) != 0), 2);
	tic_parser_reset();	
}


/*---------------------------------------------------------------------------*/
PROCESS_THREAD(tic_process_process, ev, data)
{

	PROCESS_BEGIN();

	
	tic_frame_event_message = process_alloc_event();
	
	// Set the parser call back
	tic_parser_set_frame_rx_handler(tic_parser_frame_rx_tic_buf);
	
	// Start the Rx frame timeout timer
	ctimer_set(&tic_process_timeout, tic_event_seconds_timeout * CLOCK_SECOND, handle_tic_process_timeout, NULL);
	
	// Initially the parser will discover the meter type
	// Only reset if was not discovered by init waiting for TIC (Cf TIC_UART_initialize)
	if ((tic_parser_get_meter_type() >= MT_NULL) ||(tic_parser_get_meter_type() == MT_UNKNOWN))
		tic_process_reset(MT_NULL);

	while(1) {
		PROCESS_YIELD();
		if (ev == tic_frame_event_message) {
			tic_last_buf_date  = clock_seconds();

			if ( (((TIC_parser_status_t *)data)->parser_state == PEND_PROCESS) ||
				 (((TIC_parser_status_t *)data)->parser_state == PEND_PROCESS_ONE_GROUP) )	{


// A VIRER: Test durée de traitement en fin de trame
#if (WITH_PIN_TEST==1)
//	PINTESTx_ON(2);
#endif

				if (tic_process_frame_rx_handler != NULL) {

					if (((TIC_parser_status_t *)data)->parser_state == PEND_PROCESS)
						tic_add_calculated_fields((TIC_parser_status_t *)data);

					tic_process_frame_rx_handler((TIC_parser_status_t *)data);
				}
				tic_parser_reset();
				ctimer_set(&tic_process_timeout, tic_event_seconds_timeout * CLOCK_SECOND, handle_tic_process_timeout, NULL);

// A VIRER: Test durée de traitement en fin de trame
#if (WITH_PIN_TEST==1)
//	PINTESTx_OFF(2);
#endif



			} else {
				// Strange case where that should not occurs except if time_out  
				// during for PEND_PROCESS in tic_parser.c 
			}
		}
	} // while (1)

	PROCESS_END();

}
