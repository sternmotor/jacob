	 
#include <bios.h>
#include <conio.h>
#include <string.h>
#include <stdlib.h>               	// NUR FšR MAIN !
#include <graphics.h>
#include <svga16.h>
#include <dos.h>

void error(int);
	 
class gadget
	{
	private:
	int 	status,   	//Gadgetstatus: 0=untagged, 1=tagged
		posx,     	//Gadgetposition linke obere Ecke
		posy,
		sizex,     	//Gadgetgr”áe
		sizey,
		color,     	//Vordergrundfarbe
		shadow,    	//Vordergrundfarbe ein Farbton dunkler
		dark,       //dunkle Umrandung
		light;      //helle Umrandung

	char 	*text;
	void  far *buffer;	//Buffer, um Bild unter Gadget aufzunehmen
	void 	drawtagged();    	//Zeichenroutinen
	void	drawuntagged();

	public:
	gadget(char *t) 	//Konstruktor
		{
		text=new char[strlen(t)+1];
		strcpy(text,t);
		status=0;   
		sizex=textwidth(text)+8;
		sizey=textheight(text)+8;
		color=7;
		shadow=8;
		dark=0;
		light=15;
		}
   
	~gadget()         	//Destruktor
		{
		delete buffer;
		delete text;
		}

	void 	setcolors(int, int, int, int);
	void 	setsize(int sx,int sy); 
	void 	set(int status); 
	int 	get() {return(status);}
	int 	touch(int touchx,int touchy);
	void 	hide();
	void 	show(int posx,int posy);
	};



/////////////////////////////////////////////////////////////////////////////

void main()
{          
if (svga16on()) error(1);

setfillstyle(SOLID_FILL,1); 
	bar(640,480,0,0); 
line(0,0,200,400);

gadget gad1("Hallo !");

gad1.show(50,50);
gad1.set(1);
gad1.setsize(200,100);
gad1.show(110,300);
while(!kbhit()); 
svga16off();

}
///////////////////////////////////////////////////////////////////////////////////





int gadget::touch(int touchx, int touchy)
	{
	if ( 	(touchx >= posx) &&
		(touchx <= posx+sizex) &&
		(touchy >= posy) &&
		(touchy <= posy+sizey)  ) return(1);
	else return(0);
	}

void gadget::show(int pox, int poy)
	{
	posx=pox;
	posy=poy;

	delete buffer;
	if (!(buffer= new	far[imagesize(0,0,sizex,sizey)] )) error(2);
		else getimage(posx, posy, posx+sizex, posy+sizey, buffer);

	setfillstyle(SOLID_FILL,color); 
		bar(posx, posy, posx+sizex, posy+sizey); 

	setlinestyle(SOLID_LINE,1,1);
	if(!status) drawuntagged();
		else drawtagged();

	moveto(posx+ (sizex-textwidth(text))/2+1, 
		 posy+ (sizey-textheight(text))/2+1);
	outtext(text);
	}

void gadget::hide()
	{
	putimage(posx, posy, buffer, 0);
	}

void gadget::drawtagged()
	{
	setcolor(shadow);
		moveto(posx+sizex-2, posy+1);
		lineto(posx+1, posy+1);
		lineto(posx+1, posy+sizey-2);
	setcolor(dark);
		moveto(posx, posy+sizey);
		lineto(posx, posy);
		lineto(posx+sizex, posy);
	setcolor(light);
		moveto(posx+sizex, posy);
		lineto(posx+sizex, posy+sizey);
		lineto(posx, posy+sizey);
	}

void gadget::drawuntagged()
	{
	setcolor(shadow);
		moveto(posx, posy+sizey-1);
		lineto(posx+sizex-1, posy+sizey-1);
		lineto(posx+sizex-1, posy);
	setcolor(light);
		moveto(posx+sizex-1, posy);
		lineto(posx, posy);
		lineto(posx, posy+sizey-1);
	setcolor(dark);
		moveto(posx, posy+sizey);
		lineto(posx+sizex, posy+sizey);
		lineto(posx+sizex, posy);
	}
     
void 	gadget::setcolors(int col,int shad,int dar,int lig) 
	{
	color=col;
	shadow=shad;
	dark=dar;
	light=lig;
	}
     
void 	gadget::setsize(int sx,int sy) 
	{
	sizex=sx;
	sizey=sy;
	}
void 	gadget::set(int stat) {status=stat;}


void error(int number)
	{
	svga16off();
	cprintf("\n\n\n");
	switch(number)
		{
		case 1:	cprintf("Graphmode not available");
				break;
		case 2:	cprintf("Insufficient free Memory");
				break;
		}	
      exit(1);
	}

