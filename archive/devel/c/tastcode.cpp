/*
Programm zur Tastaturabfrage
Es werden die verschiedenen Codes mit dem High- und Low-Byte von Bioskey(0)
ermittelt, der Status der Umschalttasten mit der Bitmaskierung des
Statusbytes (bioskey(2)).
Die Abfrage von F12 und F11 ist noch nicht implementiert.
Interressant ist vielleicht auch folgende Mîglichkeit zur Aufspaltung von High-
und Low-Byte.

union REGS Register;
Register.x.ax=tastew;
tastel=Register.h.al;
tasteh=Register.h.ah;

Der Zeichensatzcusor wird ausgeschaltet.


*****************************************************************************/


#include <bios.h>
#include <stdio.h>
#include <conio.h>
#include <stdlib.h>
#include <dos.h>     	     	//fÅr cursoroff/on


void init(void);
void exit (void);
void printbin (int byte);

/////////////////////////////////////////////////////////////////////////////

void main()
{
int 	tastew,                 	   	//Tasteword, low, high
	tastel,
	tasteh,      		
	tastestat,                    	//Tastaturstatus
	dummy;   				

init();

dummy=bioskey(2);                    	//Tastaturstatusbyte zur Bestimmung Umschaltetastenstatus

while(tastel!=27)                        	//Warten auf ESC
{

tastew=bioskey(0);                    	//16 Bit Tastaturcode
tastel=tastew & 255;                     	//Low-Byte (ASCII)
tasteh=tastew >> 8;				//High-Byte (Scancode)

tastestat=bioskey(2);                     //Umschalttaste gedrÅckt
if(tastestat != dummy)
	{
	printf("\n\nUmschalttaste gedrÅckt, Statusbyte dez: %d   hex: %X   bin: ",tastestat,tastestat);
	printbin(tastestat);
	printf("\n\n");
	}


printf("ASCII dez  hex  okt\tScancode dez  hex  okt\t  Word dez\t   Darstellung");
printf("\n      %d   %X   %o",tastel,tastel,tastel);
gotoxy(34,wherey());
printf("%d   %X   %o          %d\t   %c\n\n",tasteh,tasteh,tasteh,tastew,tastel);
}

}


/////////////////////////////////////////////////////////////////////////////


void printbin(byte)
{
int maske[8]={128,64,32,16,8,4,2,1},i;     		//Bitmasken fÅr BinÑrdarstellung
for (i=0;i<8;i++)
	{
	if (byte & maske[i]) printf ("1"); 	//die binÑre Stelle mit High-Bit wurde gefunden
	else printf("0");
	}
}


void init(void)
{
clrscr();

union REGS Register;     				//Cursor aus
Register.h.ah=1;
Register.h.ch=31;
Register.h.cl=32;
int86(0x10,&Register,&Register);

printf("\n\nProgramm zum Thema Tastaturabfrage. Probiere auch Umsch, CapsLock, NumLock\nund Scrollock (Anzeige nur in Verbindung mit Umschalttaste)\n");
printf("\n\nTaste drÅcken, Codes werden angezeigt. Abbruch mit <ESC>");
printf("\n\nASCII dez  hex  okt\tScancode dez  hex  okt\t  Word dez\t   Darstellung");
printf("\nESC : 27   1B   33\t\t 1    1    1           283           %c\n\n\n",27);
}





void exit(void)
{
union REGS Register;        				//Cursor an

Register.h.ah=1;
Register.h.ch=12;
Register.h.cl=13;
int86(0x10,&Register,&Register);
}

