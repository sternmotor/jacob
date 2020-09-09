#include <dos.h>
#include <stdio.h>
#include <bios.h>
#include <stdlib.h>
#include <conio.h>
#include <graphics.h>
#include <svga16.h>


int  Mreset(void);  		//RÅckgabe: 0:kein Maustreiber gefunden, 2=2Tastenmaus, 3=3Tastenmaus
void Mshow(void);		
void Mhide(void);
void Mmove (int x1,int x2);
void Mrange(int x1,int x2,int x3,int x4);
void Mhiderange(int x1,int x2,int x3,int x4);
void Mspeed(int,int,int);	//x,y: Anzahl der Mickeys, die 8 Pixels enstprechen (horz/vert), tresh=Schwelle, ab der speed verdoppelt wird (keine Reakton bei 0)       
void Mcursor(int);        	//0=normal, 1=wait,2=Fadenkreuz
int  ML(void);               	//Linke Maustaste, =TRUE, wenn gedrÅckt
int  MM(void);
int  MR(void);
int  MX(void);                //RÅckgabe: absolute Mauskoordinate
int  MY(void);
int  MXrel(void);         	//RÅckgabe: relative Mauskoordinate
int  MYrel(void);


/////////////////////////////////////////////////////////////////////////////////////////////////////


void main(void)
{

if (svga16on()) exit(1);

Mreset();  
Mshow();
getch();
Mhide();
getch();
Mshow();
getch();
Mmove(70,130);
getch();
Mrange(30,30,200,200);
getch();
Mreset();
Mshow();
Mhiderange(30,30,200,200);
getch();
Mreset();
Mshow();
Mspeed(3,3,0);
getch();

setfillstyle(SOLID_FILL,0);
while(!bioskey(1))
	{
	outintxy(40,20,ML());
	outintxy(40,30,MM());
	outintxy(40,40,MR());
	outintxy(40,50,MX());
	outintxy(40,60,MY());
	outintxy(40,70,MXrel());
	outintxy(40,80,MYrel());
	delay(10);
      bar(0,0,200,200);
	}


Mcursor(1);
getch();
Mcursor(2);
getch();
Mcursor(0);
getch();     
end(0);
}


////////////////////////////////////////////////////////////////////////////////////





int Mreset(void)
{
unsigned int stat;

asm mov ax,0 				// Funktionsnummer fÅr Mausreset                     
asm int 33h
asm mov stat,ax
if(stat!=0xFFFF) return(0);		//keine Maus im System ?
asm mov stat,bx				//Anzahl Mausknîpfe
return (stat);
} 


void Mshow(void)
{
asm mov ax,1   				// Funktionsnummer zum sichtbar machen der Maus
asm int 33h
}

void Mhide(void)
{
asm mov ax,2   				// Funktionsnummer zum Verstecken der Maus          
asm int 33h
}


void Mmove(int x1,int x2) 		     
{
asm mov ax,4 				// Funktionsnummer zum Bewegen des Maus-Cursors        
asm mov cx,x1
asm dec cx
asm mov dx,x2
asm dec dx
asm int 33h
}

void Mrange(int x1,int x2,int x3,int x4)
{
asm 	{
	mov ax,7 			 	// Funktionsnummer fÅr horizontalen Bewegungsbereich   
	mov cx,x1 				
	dec cx				// Handler arbeitet immer mit Wert -1               
	mov dx,x3
	dec dx
	int 33h
	mov ax,8 				// Funktionsnummer fÅr vertikalen Bewegungsbereich     
	mov cx,x2
	dec cx
	mov dx,x4
	dec dx
	int 33h
	}
}


void Mhiderange(int x1,int x2,int x3,int x4)   	//Bereich, in dem die Maus unsichtbar ist
{
asm 	{
	mov ax,10h 					// Funktionsnummer fÅr Ausschlu·bereich definieren 
	mov cx,x1
	dec cx 
	mov dx,x2
	dec dx
	mov si,x3
	dec si
	mov di,x4
	dec di
	int 0x33
	}
}


void Mspeed(int x1,int x2,int tresh)  		//x,y: Anzahl der Mickeys, die 8 Pixels enstprechen (horz/vert), tresh=Schwelle, ab der speed verdoppelt wird (keine Reakton bei 0)        
{
/*
asm mov ax,0Fh	 			// Funktionsnummer fÅr Mausgeschwindigkeit einstellen
asm mov cx,x1				// Anzahl der horizontalen Mickeys                   
asm mov dx,x2				// Anzahl der vertikalen Mickeys                     
asm int 0x33
*/
asm mov ax,1Bh
asm mov bx,x1
asm mov cx,x2
asm mov dx,tresh
}

void Mcursor(int type)
{
int 	off,seg,
	x1,x2;        	     	//Buffer fÅr aktuelle Cursorposition

unsigned int cursor1[32] = 
	{0xe01f,0xe01f,0xe01f,0xc00f,0x8007,0x3,0x3,0x1,
	0x3,0x3,0x8007,0xc00f,0xe01f,0xe01f,0xe01f,0xffff,
	0x0,0xfc0,0xfc0,0x1020,0x2110,0x4108,0x4108,0x410c,
	0x4208,0x4408,0x2010,0x1020,0xfc0,0xfc0,0x0,0x0};

unsigned char cursor2[64]={                                        	//64rer
	31,248,15,240,7,224,3,192,1,128,0,0,0,0,128,1,
	0,0,0,0,0,0,1,128,3,192,7,224,15,240,31,248,
	0,0,64,2,96,6,112,14,120,30,124,62,62,124,0,0,
	0,0,62,124,124,62,120,30,112,14,96,6,64,2,0,0};

switch(type)
	{
	case	0:
		Mreset();
		Mshow();
		return;
	case 	1:
		off=FP_OFF((char far *)cursor1);     	//Offset-Adresse der Cursor-Daten
		seg=FP_SEG((char far *)cursor1);     	//Segment-Adresse der Cursor-Daten
		break;
	case	2:
		off=FP_OFF((char far *)cursor2);     	//Offset-Adresse der Cursor-Daten
		seg=FP_SEG((char far *)cursor2);     	//Segment-Adresse der Cursor-Daten
		break;
	default:
      	return;
	}


asm	{
	mov ax,9	  	// Neuer Cursor		
	mov bx,8
	mov cx,1
	mov dx,off    
	mov es,seg    
	int 33h

	mov ax,03h		// alte Position in x1 und x2 speichern
	int 33h
	mov x1,cx
	mov x2,dx

	mov ax,4 	    	// Funktionsnummer zum Bewegen des Maus-Cursors (bzw.aktivieren)       
	mov cx,x1
	dec cx
	mov dx,x2
	dec dx
	int 33h
	}
return;
}

//Zur Mausabfrage: es wird kein Interrupt-Verfahren, sondern Polling angewendet. Rechenzeit wird sowieso verwendet, und die kurzen schnellen Routinen 
//lassen sich mit den kurzen Namen wie "unidirektionale" Integer-Variablen verwenden. 

int ML(void)                           	//Linker Mausknopf (1/0)
{
unsigned int stat;
asm mov ax,03h
asm int 33h
asm and bx,1
asm mov stat,bx
return(stat);
}

int MM(void)                              //Mittlerer Mausknopf (1/0)
{
unsigned int stat;
asm mov ax,03h
asm int 33h
asm and bx,4
asm mov stat,bx
if(stat) return(1);
return(0);
}

int MR(void)                              //Rechter Mausknopf (1/0)
{
unsigned int stat;
asm mov ax,03h
asm int 33h
asm and bx,2
asm mov stat,bx
if(stat) return(1);
return(0);
}

int MX(void)
{
unsigned int stat;
asm mov ax,03h
asm int 33h
asm mov stat,cx
return(stat);
}

int MY(void)
{
unsigned int stat;
asm mov ax,03h
asm int 33h
asm mov stat,dx
return(stat);
}

int MXrel(void)
{
unsigned int stat=0;
asm mov ax,0bh
asm int 33h
asm mov stat,cx
return(stat);
}

int MYrel(void)
{
unsigned int stat=0;
asm mov ax,0bh
asm int 33h
asm sar dx,1
asm mov stat,si
return(stat);
}
