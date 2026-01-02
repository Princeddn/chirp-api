#define	MAX_FIELDS_MAX_NUMBER	63
#include "tic-tools.h"
//#define POINTER
#ifdef POINTER
typedef	struct
{
	unsigned char	el_present;	// element present in frame
	unsigned char	el_num;		// elem num [0..CTCBE_FIELDS_MAX_NUMBER]
					// or [0..CJE_FIELDS_MAX_NUMBER]
					// or [0..ICE_FIELDS_MAX_NUMBER]
	unsigned char	el_type;	// elem type TYPE_U16,TYPE_CSTRING,...

	char		*el_name;	// elem name ("CONTRAT","DATECOUR",...)
	char		*el_cfmt;	// c format (printf(3))

	union				// depends on el_type
	{
		unsigned char	u_c;
		unsigned short	u_s;
		unsigned long	u_l;
		float			u_f;
		char			*u_str;	// null terminated c string
		char 			*u_dateDMYhms;// tableau de 6 octets
		char 			*u_datehmDM;// tableau de 4 octets
		char 			*u_dateDMh;// tableau de 3 octets
		char 			*u_datehm;// tableau de 2 octets
						// -> to msg->u_pack.m_data
	}	el_u;

}	t_zcl_tic_elem;


typedef	struct
{
	t_zcl_tic_elem *el_tab;
	unsigned int 	nb_el;

} t_zcl_tic_elems;
#else
typedef	struct
{
	unsigned char	el_present;	// element present in frame
	unsigned char	el_num;		// elem num [0..CTCBE_FIELDS_MAX_NUMBER]
					// or [0..CJE_FIELDS_MAX_NUMBER]
					// or [0..ICE_FIELDS_MAX_NUMBER]
	unsigned char	el_type;	// elem type TYPE_U16,TYPE_CSTRING,...

	char		el_name[STR_LABEL_SZ_MAX+1];	// elem name ("CONTRAT","DATECOUR",...)
	char		el_cfmt[11];	// c format (printf(3))

	union				// depends on el_type
	{
		unsigned char	u_c;
		unsigned short	u_s;
		unsigned long	u_l;
		float			u_f;
		char			u_str[STR_VALUE_SZ_MAX+1];	// null terminated c string
		char 			u_dateDMYhms[7];// tableau de 6 octets
		char 			u_datehmDM[5];// tableau de 4 octets
		char 			u_dateDMh[4];// tableau de 3 octets
		char 			u_datehm[3];// tableau de 2 octets
						// -> to msg->u_pack.m_data
	}	el_u;

}	t_zcl_tic_elem;


typedef	struct
{
	t_zcl_tic_elem el_tab[MAX_FIELDS_MAX_NUMBER];
	unsigned int nb_el;

} t_zcl_tic_elems;
#endif




int	AwZclDecodeTic(
		char *humanout, /*t_zcl_msg*/ void *msg,
		unsigned char *bin,int szbin,
		TIC_meter_type_t type,
		t_zcl_tic_elems *tbticelems
	);

int	AwZclEncodeTic(/*t_zcl_msg*/ void *msg,
		unsigned char *bin,int szmax,
		TIC_meter_type_t type,
		t_zcl_tic_elems *tbticelems,
		int nbelem);


void print_tbticelems(t_zcl_tic_elems *tbticelems);
