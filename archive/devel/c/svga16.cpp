#include <dos.h>
#include <stdio.h>
#include <bios.h>
#include <stdlib.h>
#include <conio.h>
#include <graphics.h>

typedef unsigned char byte;

byte  checkbit(byte arg,int number);

int  svga16on(void);		//schaltet in SVGA16-Modus, EGAVGA.Obj (von EGAVGA.bgi) muá eingebunden sein (z. B. "bgiobj egavga" , danach "tlib graphics +egavga.obj"
void svga16off(void);
void end(int);			//closegraph, bye, errorlevel
void cls();
void enter(int);             	//Cursor um int Buchstabenzeilen runter
void pos1(void);              //Cursor an Anfang

void clearkeyb(void);         //Tastaturpuffer l”schen
void outint(int);			//schreibt im SVGA-Modus integer
void outintxy(int,int,int);	//hier mit Koordinate
void outchar(char);
void outcharxy(int,int,char);




/////////////////////////////////////////////////////////////////////////////////////////////////////


void main(void)
{

if (svga16on()) exit(1);
outintxy(50,80,314);
getch();
cls();
getch();
enter(3);              //geht um int  Zeilen runter
outchar('A');
getch();

end(0);
}


////////////////////////////////////////////////////////////////////////////////////




byte checkbit(byte arg,int number)
{
unsigned char mask[8]={128,64,32,16,8,4,2,1};
if (arg & mask[number]) return(1);
return(0);
}



int svga16on(void)
{
int 	GraphDriver =9,
	GraphMode   =2,
	ErrorCode;

if(registerbgidriver(EGAVGA_driver) <0)
	{
      clrscr();
	cprintf("\n\nGraphics System Error: %s\n\n\n", grapherrormsg( ErrorCode ));
	return(1);
	}

initgraph( &GraphDriver, &GraphMode, "" );
ErrorCode = graphresult();					// Read result of initialization
if( ErrorCode != grOk )				     		// Error occured during init	
	{
      clrscr();
	cprintf("\n\nGraphics System Error: %s\n\n\n", grapherrormsg( ErrorCode ));
	return(1);
	}
settextjustify(LEFT_TEXT, TOP_TEXT);
return(0);
}


void svga16off(void)
{
closegraph();
}

void outint(int zahl)       
{
char buffer[14];
sprintf(buffer,"%d",zahl);
outtext(buffer);
return;
}

void outintxy(int x,int y,int zahl)
{
char buffer[14];
sprintf(buffer,"%d",zahl);
moveto(x,y);
outtext(buffer);
return;
}

void outchar(char zeichen)
{
char buffer[4];
sprintf(buffer,"%c",zeichen);
outtext(buffer);
return;
}

void outcharxy(int x,int y,char zeichen)
{
char buffer[4];
sprintf(buffer,"%c",zeichen);
moveto(x,y);
outtext(buffer);
return;
}

void cls()
{
clearviewport();
return;
}

void enter(int anzahl)
{
int 	h=textheight(" "),
	i;

moveto(0,gety());
for (i=0;i<anzahl;i++) moverel(0,h);
return;
}

void pos1(void)
{
moveto(0,gety());
return;
}

void end(int error)
{
closegraph();
clrscr();
cprintf("\n\nbye !\n\n");
exit(error);
}


void clearkeyb(void)
{
asm mov al,2
asm mov ah,0x0C
asm int 0x11
return;
}

