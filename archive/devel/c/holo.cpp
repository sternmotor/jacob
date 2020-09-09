#include <conio.h>
#include <process.h>
#include <dos.h>
#include <bios.h>

#define SET 1
#define DEL 0

void cursor(int stat);

void  setbit(int bit,int task);    	// 0-11;kontinuierliche Folge der Daten/Steueradressen, setzen=1; lîschen=0
int  	getbit(int bit);           	// 0-1 ;   -||-               der Statusadressen, return ist 0 oder 1

int 	PORTBASE,                                 	//Datenregisteradresse als Basis der Status- und Steueradresse
	COMPORT[5]={0,0x3BC,0x378,0x278,0x2BC};  		//Portadressen 1-4

int	setbyte[8]={  1,  2,  4,  8, 16, 32, 64,128},  	//Bitmasken zum Setzen der Bits
	delbyte[8]={254,253,251,247,239,223,191,127};  	//Bitmasken zum Lîschen der Bits



/////////////////////////////////////////////////////////////////////////////

void main(void)
{
register int i;   	//schnelle ZÑhlvariable
int flag=-1;

clrscr();
cursor(SET);
cprintf("\n\n\n Zum Abbrechen eine Taste drÅcken");

PORTBASE=COMPORT[2];       	//paralleler  Port ist Com2

for(i=9;i>-1;i--) setbit(i,DEL);

for (i=0;(!bioskey(1));i=i+flag)
	{
	setbit(i,SET);
	delay(35);
	setbit(i,DEL);
	if(i==9 || i==0) flag=-1*flag;
	delay(5);
	}
}


/////////////////////////////////////////////////////////////////////////////



void setbit(int bit,int task)
{
if(bit < 8) 							//Datenregister
	{
	int  delb=delbyte[bit],         	      	//Bitmaske aufnehmen
	     setb=setbyte[bit];
	asm	{
		mov dx,PORTBASE
		in  al,dx
		}
	if (task==DEL) asm  and  al,delb;             	//Oder-VerknÅpfung mit Bitmaske
	if (task==SET) asm  or   al,setb;
	}
if(bit > 7) 							//Steuerregister
	{
	int  delb=delbyte[bit-8],         	      	//Bitmaske aufnehmen
	     setb=setbyte[bit-8];
	asm	{
		mov dx,PORTBASE                           //Steuerregisteradresse liegt 2 hîher als die Datenregisteradresse (s.u.)
            add dx,2
		in  al,dx
		}
	if (task==DEL) asm  or  al,setb;                //Steuerregister, Bits 0,1,3 sind invertiert
	if (task==SET) asm  and al,delb;
	}
if(bit == 10) 							//Bit 2 am Steuerregister nicht invertiert
	{
	int  delb=delbyte[2],         	      	//Bitmaske aufnehmen
	     setb=setbyte[2];
	asm	{
		mov dx,PORTBASE
            add dx,2
		in  al,dx
		}
	if (task==DEL) asm  and al,delb;                //Oder-VerknÅpfung mit Bitmaske
	if (task==SET) asm  or  al,setb;
	}
asm	out dx,al; 					    		//Ausgabe an Port
cursor(DEL);
return;
}

                           

int getbit(int bit)
{   /*
unsigned char	flags;
asm	{
	mov dx,STATREG
	in  al,dx
	mov flags,al
	}      */
return(0);
}

void cursoroff(void)
{
union REGS Register;

Register.h.ah=1;
int86(0x10,&Register,&Register);
}


void cursor(int stat)
{

union REGS Register;

Register.h.ah=1;

if (stat)
	{
	Register.h.ch=12;
	Register.h.cl=13;
	}
else	{
      Register.h.ch=31;
	Register.h.cl=32;
	}

int86(0x10,&Register,&Register);
}


