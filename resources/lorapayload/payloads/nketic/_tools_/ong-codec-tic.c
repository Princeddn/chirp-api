#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "ong-codec-tic.h"
#include "tic-tools.h"


// Currently selected meter descriptor ==> Frame format
static TIC_meter_descriptor_t * tic_descriptor;

void print_tbticelems(t_zcl_tic_elems *tbticelems)
{
	fprintf(stdout,"\ntbticelems: \n");

	fprintf(stdout,".nb_el: %d\n",tbticelems->nb_el);
	int i;

	for(i=0;i<tbticelems->nb_el;i++)
	{
		fprintf(stdout,".[%03d] %d %d\n",i,tbticelems->el_tab[i].el_num,tbticelems->el_tab[i].el_present);
		if(tbticelems->el_tab[i].el_present)
		{
			fprintf(stdout,"      -el_type: %d\n",tbticelems->el_tab[i].el_type);
			fprintf(stdout,"      -el_name: %s\n",tbticelems->el_tab[i].el_name);
			fprintf(stdout,"      -el_cfmt: %s\n",tbticelems->el_tab[i].el_cfmt);
			switch (tbticelems->el_tab[i].el_type) {

					case (TYPE_CSTRING):
						fprintf(stdout,"      -value: %s\n",tbticelems->el_tab[i].el_u.u_str);
					break;
					case (TYPE_CHAR):
					case (TYPE_U8):
						fprintf(stdout,"      -value: %u\n",tbticelems->el_tab[i].el_u.u_c);
					break;
					case (TYPE_U16):
					case (TYPE_I16):
						fprintf(stdout,"      -value: %u\n",tbticelems->el_tab[i].el_u.u_s);
					break;

					case (TYPE_U24):
						fprintf(stdout,"      -value: %li\n",tbticelems->el_tab[i].el_u.u_l);
					break;
					case (TYPE_6U24):
					case (TYPE_4U24):
					case (TYPE_U32):
						fprintf(stdout,"      -value: %li\n",tbticelems->el_tab[i].el_u.u_l);
					break;

					case (TYPE_FLOAT):
						fprintf(stdout,"      -value: %f\n",tbticelems->el_tab[i].el_u.u_f);
					break;

					case (TYPE_DMYhms):
						fprintf(stdout,"      -el_u: %02x %02x %02x %02x %02x %02x\n",	tbticelems->el_tab[i].el_u.u_dateDMYhms[0],
																						tbticelems->el_tab[i].el_u.u_dateDMYhms[1],
																						tbticelems->el_tab[i].el_u.u_dateDMYhms[2],
																						tbticelems->el_tab[i].el_u.u_dateDMYhms[3],
																						tbticelems->el_tab[i].el_u.u_dateDMYhms[4],
																						tbticelems->el_tab[i].el_u.u_dateDMYhms[5]);
					break;

					case (TYPE_hmDM):  // CJE counter cases: needing "sub-parsing": {hh:mn:jj:mm}:pt:dp:abcde:kp
						fprintf(stdout,"      -el_u: %02x %02x %02x %02x\n",	tbticelems->el_tab[i].el_u.u_datehmDM[0],
																				tbticelems->el_tab[i].el_u.u_datehmDM[1],
																				tbticelems->el_tab[i].el_u.u_datehmDM[2],
																				tbticelems->el_tab[i].el_u.u_datehmDM[3]);


					break;

					case (TYPE_DMh):  // CJE counter cases: needing "sub-parsing":  {jj:mm:hh}:cg
						fprintf(stdout,"      -el_u: %02x %02x %02x \n",	tbticelems->el_tab[i].el_u.u_dateDMh[0],
																			tbticelems->el_tab[i].el_u.u_dateDMh[1],
																			tbticelems->el_tab[i].el_u.u_dateDMh[2]);

					break;

					case (TYPE_hm):  // CJE counter cases: needing "sub-parsing":  {hh:mn}:dd
						fprintf(stdout,"      -el_u: %02x %02x\n",	tbticelems->el_tab[i].el_u.u_datehm[0],
																			tbticelems->el_tab[i].el_u.u_datehm[1]);
					break;
					default:
						fprintf(stdout,"      -error\n");
					break;
			}

		}
	}

}

/*!
 *
 * @brief parse une trame tic binaire et valorise un tableau de donnees avec
 * leur description en fonction du type de compteur; meme si t_zcl_tic_elem
 * contient son numero d'element, le tableau n'est pas compresse, chaque elem
 * se trouve a sa place. (un define par elem est peut etre necessaire)
 * @param humanout not used yet, will contain a human readable form of data
 * @param msg raw sensor message mapped to the driver t_zcl_msg structure
 * @param bin the tic data frame to decode
 * @param szbin size of tic data frame
 * @param cluster type
 * @param tbticelems table of elements to populate (allocted by caller)
 * @return < 0 si erreur, >= 0 le nombre de donnees
 *
 */
//BIN to TIC
int	AwZclDecodeTic(	char *humanout, /*t_zcl_msg*/ void *msg,unsigned char *bin,int szbin,TIC_meter_type_t type,t_zcl_tic_elems *tbticelems)
{
	fprintf(stdout,"\nAwZclDecodeTic\n");
	fprintf(stdout,"type:%d\n Message:",type);
	int k;
	for(k=0;k<szbin;k++)
		fprintf(stdout,"%02x",((unsigned char*) bin)[k]);

	unsigned char * tbdesc;
	unsigned char * pt_buf;
	unsigned char nfield;

	tic_descriptor=tic_metertype_to_meterdesc(type);

	tbdesc = aTB_GET_DESC(bin);
	pt_buf = aTB_GET_BUF(bin);

	nfield=tic_descriptor->expected_fields_number;
	fprintf(stdout,"\n nbitfield:%d\n",nfield);


	tbticelems->nb_el=0;
	char max;
	while (nfield-- > 0) {

		tbticelems->el_tab[tbticelems->nb_el].el_num=tbticelems->nb_el;
		tbticelems->el_tab[tbticelems->nb_el].el_present=!(!ucFTicFieldGetBit(tbdesc,tbticelems->nb_el));
		if (tbticelems->el_tab[tbticelems->nb_el].el_present != 0) {	// si element présent

			tbticelems->el_tab[tbticelems->nb_el].el_type=tic_descriptor->expected_fields[tbticelems->nb_el].type;
#ifdef POINTER
			tbticelems->el_tab[tbticelems->nb_el].el_name=(char*)tic_descriptor->expected_fields[tbticelems->nb_el].label;
			tbticelems->el_tab[tbticelems->nb_el].el_cfmt=(char*)tic_descriptor->expected_fields[tbticelems->nb_el].fmt;
#else
			strcpy(tbticelems->el_tab[tbticelems->nb_el].el_name,(char*)tic_descriptor->expected_fields[tbticelems->nb_el].label);
			strcpy(tbticelems->el_tab[tbticelems->nb_el].el_cfmt,(char*)tic_descriptor->expected_fields[tbticelems->nb_el].fmt);
#endif
			switch (tbticelems->el_tab[tbticelems->nb_el].el_type) {

				case (TYPE_CSTRING):
#ifdef POINTER
					tbticelems->el_tab[tbticelems->nb_el].el_u.u_str=(char*)pt_buf;
#else
					strcpy(tbticelems->el_tab[tbticelems->nb_el].el_u.u_str,(char*)pt_buf);
#endif
					pt_buf += strlen((char*)pt_buf) + 1;
				break;
				case (TYPE_CHAR):
				case (TYPE_U8):
					tbticelems->el_tab[tbticelems->nb_el].el_u.u_c=*pt_buf;pt_buf += 1;
				break;
				case (TYPE_U16):
				case (TYPE_I16):
					U16p_TO_U16(pt_buf,tbticelems->el_tab[tbticelems->nb_el].el_u.u_s);
					pt_buf += 2;
				break;

				case (TYPE_U24):
					U24p_TO_U32(pt_buf, tbticelems->el_tab[tbticelems->nb_el].el_u.u_l);
					pt_buf += 3;
				break;

				case (TYPE_6U24): // CJE counter cases: needing "reformating" : 111111:222222:...:666666 or 11111:22222:...:44444
								  // Can have up to 4 or 6 ':' separated u24, to store in successive fields
					U24p_TO_U32(pt_buf, tbticelems->el_tab[tbticelems->nb_el].el_u.u_l); pt_buf += 3;
					max = 5;
					while ( (max>0) &&
							(ucFTicFieldGetBit(tbdesc,tbticelems->nb_el+1) != 0)&&
							(tic_descriptor->expected_fields[tbticelems->nb_el+1].attribute & ATTRIBUTE_IS_SUBFIELD)
							 ) {

						// Step to next attribute
						tbticelems->nb_el++;
						tbticelems->el_tab[tbticelems->nb_el].el_present=!(!ucFTicFieldGetBit(tbdesc,tbticelems->nb_el));
						tbticelems->el_tab[tbticelems->nb_el].el_num=tbticelems->nb_el;
						tbticelems->el_tab[tbticelems->nb_el].el_type=tic_descriptor->expected_fields[tbticelems->nb_el].type;
			#ifdef POINTER
						tbticelems->el_tab[tbticelems->nb_el].el_name=(char*)tic_descriptor->expected_fields[tbticelems->nb_el].label;
						tbticelems->el_tab[tbticelems->nb_el].el_cfmt=(char*)tic_descriptor->expected_fields[tbticelems->nb_el].fmt;
			#else
						strcpy(tbticelems->el_tab[tbticelems->nb_el].el_name,(char*)tic_descriptor->expected_fields[tbticelems->nb_el].label);
						strcpy(tbticelems->el_tab[tbticelems->nb_el].el_cfmt,(char*)tic_descriptor->expected_fields[tbticelems->nb_el].fmt);
			#endif
						U24p_TO_U32(pt_buf, tbticelems->el_tab[tbticelems->nb_el].el_u.u_l);
						pt_buf+=3;
						max--;
					};
				break;

				case (TYPE_4U24):
					U24p_TO_U32(pt_buf, tbticelems->el_tab[tbticelems->nb_el].el_u.u_l); pt_buf += 3;
					max = 3;
					while ( (max>0) &&
							(ucFTicFieldGetBit(tbdesc,tbticelems->nb_el+1) != 0)&&
							(tic_descriptor->expected_fields[tbticelems->nb_el+1].attribute & ATTRIBUTE_IS_SUBFIELD)
							 ) {

						// Step to next attribute
						tbticelems->nb_el++;
						tbticelems->el_tab[tbticelems->nb_el].el_present=!(!ucFTicFieldGetBit(tbdesc,tbticelems->nb_el));
						tbticelems->el_tab[tbticelems->nb_el].el_num=tbticelems->nb_el;
						tbticelems->el_tab[tbticelems->nb_el].el_type=tic_descriptor->expected_fields[tbticelems->nb_el].type;
			#ifdef POINTER
						tbticelems->el_tab[tbticelems->nb_el].el_name=(char*)tic_descriptor->expected_fields[tbticelems->nb_el].label;
						tbticelems->el_tab[tbticelems->nb_el].el_cfmt=(char*)tic_descriptor->expected_fields[tbticelems->nb_el].fmt;
			#else
						strcpy(tbticelems->el_tab[tbticelems->nb_el].el_name,(char*)tic_descriptor->expected_fields[tbticelems->nb_el].label);
						strcpy(tbticelems->el_tab[tbticelems->nb_el].el_cfmt,(char*)tic_descriptor->expected_fields[tbticelems->nb_el].fmt);
			#endif
						U24p_TO_U32(pt_buf, tbticelems->el_tab[tbticelems->nb_el].el_u.u_l);
						pt_buf+=3;
						max--;
					};
				break;

				case (TYPE_U32):
					U32p_TO_U32(pt_buf,tbticelems->el_tab[tbticelems->nb_el].el_u.u_l);
					pt_buf += 4;

				break;

				case (TYPE_FLOAT):
					FLTp_TO_FLT(pt_buf,tbticelems->el_tab[tbticelems->nb_el].el_u.u_f);
					pt_buf += 4;

				break;

				case (TYPE_DMYhms):
					// "JJ/MM/AA HH/MM/SS"
#ifdef POINTER
					tbticelems->el_tab[tbticelems->nb_el].el_u.u_dateDMYhms=(char*)pt_buf;
#else
					memcpy(tbticelems->el_tab[tbticelems->nb_el].el_u.u_dateDMYhms,pt_buf,6);
#endif
					pt_buf += 6;
				break;

				case (TYPE_hmDM):  // CJE counter cases: needing "sub-parsing": {hh:mn:jj:mm}:pt:dp:abcde:kp
#ifdef POINTER
					tbticelems->el_tab[tbticelems->nb_el].el_u.u_datehmDM=(char*)pt_buf;
#else
					memcpy(tbticelems->el_tab[tbticelems->nb_el].el_u.u_datehmDM,pt_buf,4);
#endif
					pt_buf+=4;

					//field pt:dp
					for(max=0;max<2;max++)
					{
						tbticelems->nb_el++;
						tbticelems->el_tab[tbticelems->nb_el].el_num=tbticelems->nb_el;
						tbticelems->el_tab[tbticelems->nb_el].el_type=tic_descriptor->expected_fields[tbticelems->nb_el].type;
			#ifdef POINTER
						tbticelems->el_tab[tbticelems->nb_el].el_name=(char*)tic_descriptor->expected_fields[tbticelems->nb_el].label;
						tbticelems->el_tab[tbticelems->nb_el].el_cfmt=(char*)tic_descriptor->expected_fields[tbticelems->nb_el].fmt;
			#else
						strcpy(tbticelems->el_tab[tbticelems->nb_el].el_name,(char*)tic_descriptor->expected_fields[tbticelems->nb_el].label);
						strcpy(tbticelems->el_tab[tbticelems->nb_el].el_cfmt,(char*)tic_descriptor->expected_fields[tbticelems->nb_el].fmt);
			#endif
						if((tbticelems->el_tab[tbticelems->nb_el].el_present=!(!ucFTicFieldGetBit(tbdesc,tbticelems->nb_el))) != 0)
						{
#ifdef POINTER
							tbticelems->el_tab[tbticelems->nb_el].el_u.u_str=(char*)pt_buf;
#else
							strcpy(tbticelems->el_tab[tbticelems->nb_el].el_u.u_str,(char*)pt_buf);
#endif
							pt_buf += strlen((char*)pt_buf) + 1;
						}
					}
					//field abcde
					tbticelems->nb_el++;
					tbticelems->el_tab[tbticelems->nb_el].el_type=tic_descriptor->expected_fields[tbticelems->nb_el].type;
		#ifdef POINTER
					tbticelems->el_tab[tbticelems->nb_el].el_name=(char*)tic_descriptor->expected_fields[tbticelems->nb_el].label;
					tbticelems->el_tab[tbticelems->nb_el].el_cfmt=(char*)tic_descriptor->expected_fields[tbticelems->nb_el].fmt;
		#else
					strcpy(tbticelems->el_tab[tbticelems->nb_el].el_name,(char*)tic_descriptor->expected_fields[tbticelems->nb_el].label);
					strcpy(tbticelems->el_tab[tbticelems->nb_el].el_cfmt,(char*)tic_descriptor->expected_fields[tbticelems->nb_el].fmt);
		#endif
					tbticelems->el_tab[tbticelems->nb_el].el_num=tbticelems->nb_el;
					if((tbticelems->el_tab[tbticelems->nb_el].el_present=!(!ucFTicFieldGetBit(tbdesc,tbticelems->nb_el))) != 0)
					{
						U24p_TO_U32(pt_buf, tbticelems->el_tab[tbticelems->nb_el].el_u.u_l);
						pt_buf+=3;
					}

					//field kp
					tbticelems->nb_el++;
					tbticelems->el_tab[tbticelems->nb_el].el_type=tic_descriptor->expected_fields[tbticelems->nb_el].type;
		#ifdef POINTER
					tbticelems->el_tab[tbticelems->nb_el].el_name=(char*)tic_descriptor->expected_fields[tbticelems->nb_el].label;
					tbticelems->el_tab[tbticelems->nb_el].el_cfmt=(char*)tic_descriptor->expected_fields[tbticelems->nb_el].fmt;
		#else
					strcpy(tbticelems->el_tab[tbticelems->nb_el].el_name,(char*)tic_descriptor->expected_fields[tbticelems->nb_el].label);
					strcpy(tbticelems->el_tab[tbticelems->nb_el].el_cfmt,(char*)tic_descriptor->expected_fields[tbticelems->nb_el].fmt);
		#endif
					tbticelems->el_tab[tbticelems->nb_el].el_num=tbticelems->nb_el;
					if((tbticelems->el_tab[tbticelems->nb_el].el_present=!(!ucFTicFieldGetBit(tbdesc,tbticelems->nb_el))) != 0)
					{
						tbticelems->el_tab[tbticelems->nb_el].el_u.u_c=*pt_buf; pt_buf+=1;
					}
				break;

				case (TYPE_DMh):  // CJE counter cases: needing "sub-parsing":  {jj:mm:hh}:cg
#ifdef POINTER
					tbticelems->el_tab[tbticelems->nb_el].el_u.u_dateDMh=(char*)pt_buf;
#else
					memcpy(tbticelems->el_tab[tbticelems->nb_el].el_u.u_dateDMh,pt_buf,3);
#endif
					pt_buf+=3;
					//field cg
					tbticelems->nb_el++;
					tbticelems->el_tab[tbticelems->nb_el].el_type=tic_descriptor->expected_fields[tbticelems->nb_el].type;
		#ifdef POINTER
					tbticelems->el_tab[tbticelems->nb_el].el_name=(char*)tic_descriptor->expected_fields[tbticelems->nb_el].label;
					tbticelems->el_tab[tbticelems->nb_el].el_cfmt=(char*)tic_descriptor->expected_fields[tbticelems->nb_el].fmt;
		#else
					strcpy(tbticelems->el_tab[tbticelems->nb_el].el_name,(char*)tic_descriptor->expected_fields[tbticelems->nb_el].label);
					strcpy(tbticelems->el_tab[tbticelems->nb_el].el_cfmt,(char*)tic_descriptor->expected_fields[tbticelems->nb_el].fmt);
		#endif
					tbticelems->el_tab[tbticelems->nb_el].el_num=tbticelems->nb_el;
					if((tbticelems->el_tab[tbticelems->nb_el].el_present=!(!ucFTicFieldGetBit(tbdesc,tbticelems->nb_el))) != 0)
					{
						tbticelems->el_tab[tbticelems->nb_el].el_u.u_c=*pt_buf; pt_buf+=1;
					}
				break;

				case (TYPE_hm):  // CJE counter cases: needing "sub-parsing":  {hh:mn}:dd
#ifdef POINTER
					tbticelems->el_tab[tbticelems->nb_el].el_u.u_datehm=(char*)pt_buf; pt_buf+=2;
#else
					memcpy(tbticelems->el_tab[tbticelems->nb_el].el_u.u_datehm,pt_buf,2); pt_buf+=2;
#endif
					//field dd
					tbticelems->nb_el++;
					tbticelems->el_tab[tbticelems->nb_el].el_type=tic_descriptor->expected_fields[tbticelems->nb_el].type;
		#ifdef POINTER
					tbticelems->el_tab[tbticelems->nb_el].el_name=(char*)tic_descriptor->expected_fields[tbticelems->nb_el].label;
					tbticelems->el_tab[tbticelems->nb_el].el_cfmt=(char*)tic_descriptor->expected_fields[tbticelems->nb_el].fmt;
		#else
					strcpy(tbticelems->el_tab[tbticelems->nb_el].el_name,(char*)tic_descriptor->expected_fields[tbticelems->nb_el].label);
					strcpy(tbticelems->el_tab[tbticelems->nb_el].el_cfmt,(char*)tic_descriptor->expected_fields[tbticelems->nb_el].fmt);
		#endif
					tbticelems->el_tab[tbticelems->nb_el].el_num=tbticelems->nb_el;
					if((tbticelems->el_tab[tbticelems->nb_el].el_present=!(!ucFTicFieldGetBit(tbdesc,tbticelems->nb_el))) != 0)
					{
						tbticelems->el_tab[tbticelems->nb_el].el_u.u_c=*pt_buf; pt_buf+=1;
					}
				break;

				default:
					// Get out without any change neither put in buf if TYPE not recognized
					return -1;
				break;
			};

		} // if (ucFTicFieldGetBit(tbdesc,ifield) != 0)
		tbticelems->nb_el++;
	} // while (nfield-- > 0)

return tbticelems->nb_el;

}




/*!
 *
 * @brief a partir d'une table d'element encode la frame binaire pour
 * selectionner le reporting en fonction de filter utilisateur
 * @param msg raw sensor message mapped to the driver t_zcl_msg structure
 * @param bin the tic data frame to encode
 * @param szmax max size of tic data frame
 * @param cluster type
 * @param tbticelem table of elements to report (allocted by caller)
 * @return < 0 si erreur, >= 0 taille de l'encodage de la partie tic data
 *
 */
//TIC to BIN
int	AwZclEncodeTic(/*t_zcl_msg*/ void *msg,
		unsigned char *bin,int szmax,
		TIC_meter_type_t type,
		t_zcl_tic_elems *tbticelems,
		int nbelem)
{

	fprintf(stdout,"\nAwZclEncodeTic\n");
	fprintf(stdout,"type:%d\n",type);

	//tic_descriptor=tic_metertype_to_meterdesc(type);
	unsigned char * tic_buf_desc_u8 = aTB_GET_DESC(bin);
	unsigned char * pt_tic_buf_buf  = aTB_GET_BUF(bin);


	memset(bin,0,szmax);
	int i;
	for(i=0;i<nbelem;i++){
		if(tbticelems->el_tab[i].el_present)
		{
			switch (tbticelems->el_tab[i].el_type) {

				case (TYPE_CSTRING):
					if((pt_tic_buf_buf-bin+strlen(tbticelems->el_tab[i].el_u.u_str))>szmax) return -1;
					strcpy((char *)pt_tic_buf_buf,tbticelems->el_tab[i].el_u.u_str);
					pt_tic_buf_buf += strlen(tbticelems->el_tab[i].el_u.u_str)+1;
					vFTicFieldSetBit(tic_buf_desc_u8,tbticelems->el_tab[i].el_num);

				break;

				case (TYPE_CHAR):
					if((pt_tic_buf_buf-bin+1)>szmax) return -1;
					*(pt_tic_buf_buf) = tbticelems->el_tab[i].el_u.u_c; pt_tic_buf_buf++;
					vFTicFieldSetBit(tic_buf_desc_u8,tbticelems->el_tab[i].el_num);
				break;

				case (TYPE_U8):
					if((pt_tic_buf_buf-bin+1)>szmax) return -1;
					*(pt_tic_buf_buf) = tbticelems->el_tab[i].el_u.u_c;
					pt_tic_buf_buf++; vFTicFieldSetBit(tic_buf_desc_u8,tbticelems->el_tab[i].el_num);
				break;

				case (TYPE_U16):
					if((pt_tic_buf_buf-bin+2)>szmax) return -1;
					U16_TO_U16p(tbticelems->el_tab[i].el_u.u_s,pt_tic_buf_buf); pt_tic_buf_buf += 2;
					vFTicFieldSetBit(tic_buf_desc_u8,tbticelems->el_tab[i].el_num);
				break;

				case (TYPE_I16):
					if((pt_tic_buf_buf-bin+2)>szmax) return -1;
					I16_TO_I16p(tbticelems->el_tab[i].el_u.u_s,pt_tic_buf_buf); pt_tic_buf_buf += 2;
					vFTicFieldSetBit(tic_buf_desc_u8,tbticelems->el_tab[i].el_num);
				break;

				case (TYPE_U24):
					if((pt_tic_buf_buf-bin+3)>szmax) return -1;
					U32_TO_U24p(tbticelems->el_tab[i].el_u.u_l,pt_tic_buf_buf); pt_tic_buf_buf += 3;
					vFTicFieldSetBit(tic_buf_desc_u8,tbticelems->el_tab[i].el_num);
				break;

				case (TYPE_6U24): // CJE counter cases: needing "sub-parsing" : 111111:222222:...:666666 or 11111:22222:...:44444
				case (TYPE_4U24): // Can have up to 4 or 6 ':' separated u24, to store in successive fields
					if((pt_tic_buf_buf-bin+3)>szmax) return -1;
					U32_TO_U24p(tbticelems->el_tab[i].el_u.u_l,pt_tic_buf_buf); pt_tic_buf_buf += 3;
					vFTicFieldSetBit(tic_buf_desc_u8,tbticelems->el_tab[i].el_num);
				break;

				case (TYPE_U32):
					if((pt_tic_buf_buf-bin+4)>szmax) return -1;
					U32_TO_U32p(tbticelems->el_tab[i].el_u.u_l,pt_tic_buf_buf); pt_tic_buf_buf += 4;
					vFTicFieldSetBit(tic_buf_desc_u8,tbticelems->el_tab[i].el_num);
				break;

				case (TYPE_FLOAT):
					if((pt_tic_buf_buf-bin+4)>szmax) return -1;
					FLT_TO_FLTp(tbticelems->el_tab[i].el_u.u_f,pt_tic_buf_buf); pt_tic_buf_buf += 4;
					vFTicFieldSetBit(tic_buf_desc_u8,tbticelems->el_tab[i].el_num);
				break;

				case (TYPE_DMYhms):
					if((pt_tic_buf_buf-bin+6)>szmax) return -1;
					memcpy(pt_tic_buf_buf,tbticelems->el_tab[i].el_u.u_dateDMYhms,6);
					vFTicFieldSetBit(tic_buf_desc_u8,tbticelems->el_tab[i].el_num);
					pt_tic_buf_buf += 6;
				break;

				case (TYPE_hmDM):  // CJE counter cases: needing "sub-parsing": {hh:mn:jj:mm}:pt:dp:abcde:kp
					if((pt_tic_buf_buf-bin+4)>szmax) return -1;

					memcpy(pt_tic_buf_buf,tbticelems->el_tab[i].el_u.u_datehmDM,4);
					vFTicFieldSetBit(tic_buf_desc_u8,tbticelems->el_tab[i].el_num);
					pt_tic_buf_buf += 4;
				break;

				case (TYPE_DMh):  // CJE counter cases: needing "sub-parsing":  {jj:mm:hh}:cg
					if((pt_tic_buf_buf-bin+3)>szmax) return -1;
					memcpy(pt_tic_buf_buf,tbticelems->el_tab[i].el_u.u_dateDMh,3);
					vFTicFieldSetBit(tic_buf_desc_u8,tbticelems->el_tab[i].el_num);
					pt_tic_buf_buf += 3;
				break;

				case (TYPE_hm):  // CJE counter cases: needing "sub-parsing":  {hh:mn}:dd
					if((pt_tic_buf_buf-bin+2)>szmax) return -1;
					memcpy(pt_tic_buf_buf,tbticelems->el_tab[i].el_u.u_datehm,2);
					vFTicFieldSetBit(tic_buf_desc_u8,tbticelems->el_tab[i].el_num);
					pt_tic_buf_buf += 2;
				break;

				default:
					// This case should never occur
				break;
			};
		}
	}
	return (pt_tic_buf_buf-bin);
}


//
//
///*!
// *
// * @brief return the name of a tic element
// */
//char	*AwZclNameTicElem(int type,int num)
//{
//}
//
///*!
// *
// * @brief return the number of a named tic element
// */
//int	AwZclNumTicElem(int type,char *name)
//{
//}

