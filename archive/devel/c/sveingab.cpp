/************************************************************************/
/*Input f�r SVGA-Modi 01.04.97 by GMA					   	*/
/*Erlaubt die Eingabe definierter Zeichen und mit definierter L�nge	*/
/*unter Verwendung von Sonder- und Umschalttasten (siehe  #Define's)  	*/
/*                                                                      */
/*Hat die Variable Eingabe bei Funktionsaufruf einen Inhalt, wird dieser*/
/*angezeigt und kann evtl. sofort durch BS oder DEL gel�scht werden     */
/*												*/
/*Beispiel:											*/
/*char erlaubt[]="1234567890";        //erlaubte Zeichen                */
/*char eingabe[7];                    //R�ckgabevariable                */
/*strcpy(eingabe,"Hi !");                                               */
/*												*/
/*	outtext ("Die Eingabe:");                                         */
/*	setcolor(11);                                                     */
/*	input(eingabe,erlaubt,20,4);  //input(eingabe,erlaubt,        	*/
/*                                    erster text,max.Laenge,           */
/*						  Cursorfarbe) 				*/
/*						                                    */
/*		if (eingabe[0]==27) exit(0);                                */
/*	moverel(-1*getx(),16);                                            */
/*	outtext (eingabe);                                                */
/*												*/
/************************************************************************/



#include <bios.h>
#include <conio.h>
#include <string.h>
#include <stdlib.h>               	// NUR F�R MAIN !
#include <graphics.h>
#include <svga16.h>
#include <dos.h>

#define	RECHTS 77           	//unterst�tzte Tasten
#define	LINKS  75
#define	POS1   71
#define	ENDE   79
#define	RETURN 13
#define	ESC    27
#define	BS     8
#define	ENTF   83
#define	ALTF4  107
#define	EINF   128

void input(char*,char *,int,int);   	//Zeiger auf R�ckgabevariable, Zeiger auf erlaubt[],Maximale L�nge,Cursorfarbe




/////////////////////////////////////////////////////////////////////////////

void main()
{
char erlaubt[]="1234567890abcdefghilklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";

if (svga16on()) exit(1);
setcolor(15);

char eingabe[20];
strcpy(eingabe,"Hallo Wixer");
while(1)
	{
	moverel(-1*getx(),24);
	setcolor(4);
	outtext ("Die Eingabe:");
	setcolor(11);
	input(eingabe,erlaubt,20,4);
		if (eingabe[0]==27) exit(0);
	moverel(-1*getx(),16);
	outtext (eingabe);
	}
svga16off();

}

/////////////////////////////////////////////////////////////////////////////////////



















void input(char* eingabe,char* erlaubt,int maxlaenge,int curcolor)
{
int 	i,i2,
	einfstat=0,                                     //Einf�getastenstatus, mu� wegen Bitoperation INT sein
	startx=getx(),                              	//anf�ngliche Cursorposition
	starty=gety(),                              	//anf�ngliche Cursorposition
	laenge=strlen(eingabe),                         //wenn als eingabe bereits Text �bergeben wurde, diesen erfassen
	pos=strlen(eingabe),
	first=1,						     	//Z�hler f�r 1. Durchgang (hierin mu� DEL gedr�ckt werden, 
									//um in Eingabe �bergebenen Text zu l�schen)
	tastew,tastel,                		    	//Word,Lowbyte
	laengeerl=strlen(erlaubt),                      //Menge der erlaubten Zeichen
	csizex=textwidth (" "),                         //Buchstabengr��e
	csizey=textheight(" "),
	color=getcolor();  				     	//vorher gesetzte Zeichenfarb
										
void 	far *imagebuf;                                  //Buffer f�r Snapshot des zu �berschreibenden Bildschirmbereichs
	int	size=imagesize(0,0,startx+maxlaenge*csizex+csizex,csizey);    	//genug Heap ?
	if ((imagebuf=malloc(size)) ==NULL)
		{
		closegraph();
		cprintf ("\n\nNicht genug Heap-Speicher !\n\n");
		exit(1);
		}
	else getimage(0,starty,startx+maxlaenge*csizex+csizex,starty+csizey,imagebuf);


while(1)
	{
	putimage(0,starty,imagebuf,0);

	while(!bioskey(1))
		{
		einfstat=bioskey(2) & EINF;       	     	//Abfrage Umschalttasten, Bit 8 im Statusbyte gesetzt ?
		setcolor(color);
		moveto(startx,starty);                 	//an Anfang gehen
		outtext (eingabe);                        //Ausgabe Textstring

     		setcolor(curcolor);                       //Cursor malen
      	moveto(startx+pos*csizex,starty);
		if((einfstat==EINF) && (pos < laenge))   	//Einf�gen an, X als Cursor
			outtext("X");
		else  outtext("_"); 				//Einf�gen aus
		delay(10);                                //Wartezeit, um Flimmern zu verhindern
		}                                   

	tastew=bioskey(0);      			//Word
	tastel=tastew & 0xFF;                    	//Low-Byte
	switch(tastel)
	{
	case 0:
		switch(tastew >> 8)   			    	//Scancode holen
			{
			case 	ENTF:
				if (first=1)
					{
					eingabe[0]='\0';       //mit eingabe �bergebenen Text l�schen
					laenge=pos=0;
					continue;
					}
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
				eingabe[0]=ESC;        	//ESC-Code zur�ckgeben
				eingabe[1]='\0';
				free(imagebuf);
				return;
			}
		break;
	 case RETURN:
		free(imagebuf);
		return;
	 case ESC:                           	    
		eingabe[0]=ESC;                   	//ESC-Code zur�ckgeben
		eingabe[1]='\0';
		free(imagebuf);
		return;
	 case BS:
		if (first=1)
			{
			eingabe[0]='\0';       //mit eingabe �bergebenen Text l�schen
			laenge=pos=0;
			continue;
			}
		if (pos==0)  continue;
		for(i=pos-1;i <laenge;i++)
			eingabe[i]=eingabe[i+1];
		laenge--;
		pos--;
		break;
	}
	first=0;

	if ((tastel != 0) && (laenge < maxlaenge))   	//keine Bearbeitung f�r nichtzugelassene Eingabel�nge && ASCII-Code < 128 (keine Sondertasten)
		{
		for (i=0;i<laengeerl;i++)
			{
			if (tastel==erlaubt[i])             //erlaubtes Zeichen ?
				{
				switch(einfstat)
					{
					case 0:                                  	//Einf�gen aus
  						for(i2=laenge;i2 >= pos;i2--)     	//Text ab Cursor 1 nach rechts verschieben
							eingabe[i2+1]=eingabe[i2];
							eingabe[pos]=tastel;         	//neue Eingabe einf�gen
						laenge++;
						pos++;
						break;
					case EINF:                         		//Einf�gen an
							eingabe[pos]=tastel;
						if (pos == laenge) laenge++;
						pos ++;
						break;
                              }
				break;
				}
			}
		}
	}
}

