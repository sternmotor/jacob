#include <conio.h>
#include <ctype.h> 		//fÅr toupper
#include <stdlib.h>
#include <string.h>
#include <bios.h>            	//fÅr bioskey
#include <iostream.h>		//fÅr cout


void arabrom(char *);
void romarab(char *);

void input(char *);   		// Zeiger auf RÅckgabevariable
void abbruch(void);
void fehler(void);

char rom[4][9][5]  ={"M","MM","MMM","4xM","5xM","6xM","7xM","8xM","9xM",
			   "C","CC","CCC","CD","D","DC","DCC","DCCC","CM",
			   "X","XX","XXX","XL","L","LX","LXX","LXXX","XC",
			   "I","II","III","IV","V","VI","VII","VIII","IX"};

int romlaenge[4][9]={1,2,3,3,3,3,3,3,3,
			   1,2,3,2,1,2,3,4,2,
			   1,2,3,2,1,2,3,4,2,
			   1,2,3,2,1,2,3,4,2};

char rombuch[]   	 ="MDCLXVI";
long data[11][7]   ={100002,50003,10009,5005,1010,507,111,
			   100002,50003,10009,5005,1010,507,111,
			   1     ,1    ,10009,5005,1010,507,111,
			   1     ,1    ,10004,5005,1010,507,111,
			   1     ,1    ,1    ,5006,1010,507,111,
			   1     ,1    ,1    ,1   ,1006,507,111,
			   1     ,1    ,1    ,1   ,1   ,508,111,
			   1     ,1    ,1    ,1   ,1   ,1  ,108,
			   80005 ,30005,10004,5006,1010,508,111,
			   1     ,1    ,8007 ,3007,1006,508,111,
			   1     ,1    ,1    ,1   ,800 ,300,108};

/////////////////////////////////////////////////////////////////////////

void main(void)
{
clrscr();
cout << "\n\nUmrechnung rîmischer in arabische Zahlen und umgekehrt\n\nEntweder eine rîmische oder eine arabische Zahl (<3999) eingeben \n\n";

char eingabe[30];

while(1)
	{
	input(eingabe);
	if (eingabe[0] > 58) romarab(eingabe);
	else arabrom(eingabe);
	cout << "\n\n\nErneut: ";
	}
}

//////////////////////////////////////////////////////////////////////



void arabrom(char *eingabe)
{

int 	i,i2,i3;

char arab[]="....";

switch(strlen(eingabe))
	{
	case 1:	arab[3]=eingabe[0];
			break;
	case 2:	arab[2]=eingabe[0];
			arab[3]=eingabe[1];
			break;
	case 3: 	arab[1]=eingabe[0];
			arab[2]=eingabe[1];
			arab[3]=eingabe[2];
			break;
	case 4:	strcpy (arab,eingabe);
			break;
	default:	cout << "\n\nFrag mal einen Rîmer ...\n";
			return;
	}

cout << "\n\nIst rîmisch: ";
for (i=0;i<4;i++)
	{
	for (i2=0;i2<9;i2++)
		{
		if (arab[i]-49==i2)
			{
			for (i3=0;i3<=romlaenge[i][i2];i3++) cout << rom[i][i2][i3];
			cout << "\b";
			}
		}
	}
}




void romarab(char *eingabe)
{
int laenge=strlen(eingabe);

long 	zahl=0,
	r=0,
	c=0,
	p=0,
	n,
	d,
	i,i2;

for (i=0;i<laenge;i++)
	{
	for (i2=0;i2<7;i2++)
		if (eingabe[i]==rombuch[i2]) break;
	n=data[r][i2];
		if (n<2) {fehler();return;}
	if ((i2-p)==0)d=0;
		else d=1;
	c=(1-d)*(1+c);
		if (c>2) {fehler();return;}
	p=i2+1;
	zahl=zahl+int(n/100);
	r=(n-100*int(n/100))-1;
		if (r==0) break;
	}
cout << "\n\n\Ist arabisch: "  << zahl;
return;
}




void input(char* eingabe)
{
char 	erlaubt[]="1234567890IMXDCLV";

const int 	RECHTS=77,           	//unterstÅtzte Tasten
		LINKS =75,
		POS1  =71,
		ENDE  =79,
		RETURN=13,
		ESC   =27,
		BS    = 8,
		ENTF  =83,
		ALTF4 =107;
int 	i,i2,                                       	//Counter
	startX=wherex(),                              	//anfÑngliche Cursorposition
	startY=wherey(),                              	//anfÑngliche Cursorposition
	laenge=0,pos=0,                                 //relative Koordinaten
	tastew,tastel,						//Word,Lowbyte
	maxlaenge=30,                                  	//maximale EingabelÑnge
	laengeerl=strlen(erlaubt);                      //Menge der erlaubten Zeichen


while(1)
	{
	tastew=toupper(bioskey(0));
	tastel=tastew & 0xFF;

	switch(tastel)
	{
	case 0:
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
				abbruch();
			default:
			     	continue;
			}
		break;
	 case RETURN:
		if (laenge==0) abbruch();
		return;
	 case ESC:                           	    
		abbruch();
	 case BS:
		if (pos==0)  continue;
		for(i=pos-1;i <laenge;i++)
			eingabe[i]=eingabe[i+1];
		laenge--;
		pos--;
		break;
	}

	if (laenge>0)
		{
		if (eingabe[0]<58)          			//erstes Zeichen arabisch
			{
			maxlaenge=30;
			if (tastel>58) tastel=0;         	//reines arabisch !
			}
		if (eingabe[0]>58)
			{
			maxlaenge=6;
			if (tastel<58) tastel=0;          	//reines rîmisch !
			}
		}

	if (tastel != 0  && laenge < maxlaenge)            	//keine Bearbeitung fÅr nichtzugelassene EingabelÑnge; ASCII-Code < 128 (keine Sondertasten)
		{
		for (i=0;i<laengeerl;i++)
			{
			if (tastel==erlaubt[i])                  	//erlaubtes Zeichen ?
				{
				for(i2=laenge;i2 >= pos;i2--)     	//Text ab Cursor 1 nach rechts verschieben
					eingabe[i2+1]=eingabe[i2];
				eingabe[pos]=tastel;                     	//neue Eingabe einfÅgen
				laenge++;
				pos++;
				}
			}
		}
	eingabe[laenge]='\0';                                     	//StringlÑnge
	gotoxy(startX,startY);                                	//an Anfang gehen
	cout << eingabe;
	for(i=0;i<=30;i++) cout << " ";     				//Rest lîschen
	gotoxy(startX+pos,startY);                            	//Cursor setzen
	}
}


void fehler(void)
{
cout << "\n\n Falsche Eingabe !\n\n";
return;
}

void abbruch(void)
{
clrscr();
cout << "\n\nbye !\n\n";
exit(0);
}














