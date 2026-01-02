#ifndef _TIC_FORMATER_H_
#define _TIC_FORMATER_H_

#include "tic-tools.h"

//----------------------------------------------------------------------------
// TIC input processor management
void tic_formater_init(TIC_meter_descriptor_t * tic_descriptor);
unsigned char * tic_formater_record_put(char * strbuf, unsigned char rec_num, unsigned char * filterDesc, unsigned char * tbdesc, unsigned char *pt_buf, unsigned char *doNotChangeOfField);
void tic_formater_frame_put(char* strbuf, unsigned char * filterDesc, unsigned char * tbdesc, unsigned char * tbbuf);

#endif //  _TIC_FORMATER_H_
