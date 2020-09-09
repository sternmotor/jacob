

extern int  far 	Mreset(void);  		//1=Maus installiert  0=nicht gefunden 
extern void far 	Mshow(void);
extern void far 	Mhide(void);
extern void far 	Mmove (int x1,int x2);
extern void far 	Mrange(int x1,int x2,int x3,int x4);
extern void far 	Mhiderange(int x1,int x2,int x3,int x4);
extern void far 	Mspeed(int x1,int x2);
extern void far 	Mcursor(int);          	//0=normal,1=Text 2=Wait
extern int  far 	ML(void);              	//Linke Maustaste, =1, wenn gedrÅckt
extern int  far 	MM(void);
extern int  far 	MR(void);
extern int  far 	MX(void);               //RÅckgabe: Mauskoordinate
extern int  far 	MY(void);


