#include <conio.h>
#include <dos.h>          //fÅr cursoroff/on

void cursoroff(void);
void cursoron (void);


/////////////////////////////////////////////////////////////////////////////

void main()
{
clrscr();
cprintf("\n\n\nBitte zweimal Taste drÅcken");
cursoroff();
getch();
cursoron();
getch();
}

////////////////////////////////////////////////////////////////////////////
void cursoroff(void)
{
union REGS Register;

Register.h.ah=1;
Register.h.ch=31;
Register.h.cl=32;
int86(0x10,&Register,&Register);
}


void cursoron(void)
{
union REGS Register;

Register.h.ah=1;
Register.h.ch=12;
Register.h.cl=13;
int86(0x10,&Register,&Register);
}

