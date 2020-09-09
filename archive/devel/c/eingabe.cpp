/************************************************************************/
/*Input 10.02.97 by GMA							   	*/
/*Erlaubt die Eingabe definierter Zeichen und mit definierter LÑnge	*/
/*unter Verwendung von Sonder- und Umschalttasten (siehe  #define's  	*/
/*												*/
/*Beispiel:											*/
/*char erlaubt[]="1234567890";        //erlaubte Zeichen                */
/*char eingabe[7];                    //RÅckgabevariable                */
/*												*/
/*cout << "\n\n\nDie Eingabe:";                                         */
/*input(eingabe,erlaubt,6);      	//oder input(eingabe,"ABC",6);      */
/*												*/
/************************************************************************/



#include <bios.h>
#include <iostream.h>
#include <conio.h>
#include <string.h>
#include <stdlib.h>               	// NUR FöR MAIN !

#define	RECHTS 77           	//unterstÅtzte Tasten
#define	LINKS  75
#define	POS1   71
#define	ENDE   79
#define	RETURN 13
#define	ESC    27
#define	BS     8
#define	ENTF   83
#define	ALTF4  107
#define	EINF   128


void input(char*,char *,int);   	//Zeiger auf RÅckgabevariable, Zeiger auf erlaubt[],Maximale LÑnge 


void input(char* eingabe,char* erlaubt,int maxlaenge)
{

int 	i,i2,
	einfstat=0,                                     //EinfÅgetastenstatus, mu· wegen Bitoperation INT sein
	startX=wherex(),                              	//anfÑngliche Cursorposition
	startY=wherey(),                              	//anfÑngliche Cursorposition
	laenge=0,pos=0,
	tastew,tastel,                		    	//Word,Lowbyte
	laengeerl=strlen(erlaubt);                      //Menge der erlaubten Zeichen


while(1)
	{
	while(!bioskey(1))	   			//Taste (au·er Umschalttaste) gedrÅckt
		{
		einfstat=bioskey(2) & EINF;         			//Abfrage Umschalttasten, Bit 8 im Statusbyte gesetzt ?
		if(einfstat==EINF) _setcursortype(_SOLIDCURSOR);     	//EinfÅgen an, dicker Cursor
		if(einfstat==   0) _setcursortype(_NORMALCURSOR);     //EinfÅgen aus
		}


	tastew=bioskey(0);      			//Word
	tastel=tastew & 0xFF;                    	//Low-Byte
	switch(tastel)
	{
	case 0:                                	//High-Byte
		switch(tastew >> 8)   			    	//Scancode holen
			{
			case 	ENTF:
				if (pos==laenge) continue;
				for(i=pos;i <laenge;i++)
					eingabe[i]=eingabe[i+1];
				laenge--;
				break;
			case 	LINKS:
			     	if (pos > 0) pos--;
			     	break;
			case 	RECHTS:                        
			     	if (pos < laenge) pos++;
			     	break;
	 		case	POS1:
				pos=0;
				break;
	 		case 	ENDE:
				pos=laenge;
				break;
			case	ALTF4:
				eingabe[0]=ESC;              	//ESC-Code zurÅckgeben
				eingabe[1]='\0';
				return;
			default:
			     	continue;
			}
		break;
	 case RETURN:
		return;
	 case ESC:                           	    
		eingabe[0]=ESC;                                    	//ESC-Code zurÅckgeben
		eingabe[1]='\0';
		return;
	 case BS:
		if (pos==0)  continue;
		for(i=pos-1;i <laenge;i++)
			eingabe[i]=eingabe[i+1];
		laenge--;
		pos--;
		break;
	}

	if ((tastel != 0) && (laenge < maxlaenge))                       //keine Bearbeitung fÅr nichtzugelassene EingabelÑnge && ASCII-Code < 128 (keine Sondertasten)
		{
		for (i=0;i<laengeerl;i++)
			{
			if (tastel==erlaubt[i])               	    	//erlaubtes Zeichen ?
				{
				switch(einfstat)
					{
					case 0:                                  	//EinfÅgen aus
  						for(i2=laenge;i2 >= pos;i2--)     	//Text ab Cursor 1 nach rechts verschieben
							eingabe[i2+1]=eingabe[i2];
							eingabe[pos]=tastel;         	//neue Eingabe einfÅgen
						laenge++;
						pos++;
						break;
					case EINF:                         		//EinfÅgen an
						eingabe[pos]=tastel;
						if (pos == laenge) laenge++;
						pos ++;
						break;
                              }
				break;
				}
			}
		}

	eingabe[laenge]='\0';          					//StringlÑnge
	gotoxy(startX,startY);                                	//an Anfang gehen
	cout << eingabe << " ";                                     //String ausgeben und Rest lîschen (del)
	gotoxy(startX+pos,startY);                            	//Cursor setzen
	}
}

/////////////////////////////////////////////////////////////////////////////

void main()
{
//char erlaubt[]="abcdefghilklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
//char erlaubt[]="\_+-#!"ı$%&/()1234567890abcdefghilklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";

char erlaubt[]="1234567890";
char eingabe[7];

clrscr();
while(1)
	{
	cout << "\n\n\nDie Eingabe:";
	input(eingabe,erlaubt,8);
		if (eingabe[0]==27) exit(0);
	cout << "\n\n" << eingabe;
	}
}
