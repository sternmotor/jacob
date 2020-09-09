
extern int 	far checksvga(void);         	//SVGA-Initialisierung
extern int 	far checkpaging(void);		//erlaubt Grafikkarte Paging in der Auflîsung?
extern int 	far checkxms(void);          	//Himem-Check
extern int 	far checkcpu(void);		//CPU mindestens 386
extern int 	far checkmouse(void);    	//Maus da?
extern void far initmouse(void);


extern void far palshow(void);       	//zeigt die gesamte 256-Palette an
extern void far palcol(int nr,int r,int g,int b);		//setzt einzelne Palettenfarben


extern void far gifload(PixelMode mode, int xloc, int yloc, const char *name);


extern void far drwint(PixelMode mode,int fcolr,int bcolr,int wert,int x,int y);
extern void far drwchar(PixelMode mode,int fcolr,int bcolr,char zeichen,int x,int y);

extern int  far d3tod2(int disteye,int centx, int centy, int points, D3Point far *in, D2Point far *out);
	/*Parameter: Entf. Nullpunkt-Betrachter (in Punkten)                   */
	/*Anzahl Punkte, 3D-Inputfeld, 2D-Outputfeld *RÅckgabe: 1=ok 0=Fehler  */


extern void far clearkeyb(void);         //Tastaturpuffer lîschen
