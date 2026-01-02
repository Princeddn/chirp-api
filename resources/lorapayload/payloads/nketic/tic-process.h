#ifndef _TIC_PROCESS_H_
#define _TIC_PROCESS_H_

#include "contiki.h"
#include "tic-parser.h"

#define TIC_EVENT_MINIMAL_SECOND_TIMEOUT 600 // Minimal number of second of timeout before concluding process broken

//----------------------------------------------------------------------------
// Set the timeout on event waiting
void tic_process_set_event_seconds_timeout(clock_time_t nb_seconds);
// The call back function for frame recpetion must be initialized by the client
void tic_process_set_frame_rx_handler(void (*f)(TIC_parser_status_t * stat));
// Function used to reset the reception process with eventually a new meter_type
// By default metertype is MT_NULL at startup 
// and the meter is type discovered  after first received frame
void tic_process_reset(TIC_meter_type_t mt);

PROCESS_NAME(tic_process_process);

#endif //  _TIC_PROCESS_H_
