#include <iostream.h>
#include <conio.h>
#include <process.h>
#include <stdlib.h>

void main(int argc,char *argv[])
{

if (argc ==1 || argv[1] == "?" || argv[1] == "/?")
	{
	cout << "\n\nUsage: Message <Start x> <Start y> <BackColor> <TextColor> <Text>\n\n";
	cout <<     "               Startposition x should not be more than 80,\n";
	cout <<     "               Startposition y should not be more than 25\n";
	cout <<     "               Number of Colors is between 0 and 15 (read 'help menucolor')\n\n";
	exit (1);
	}
if (argc > 6) exit(1);
if (atof(argv[1]) > 80) exit(1);
if (atof(argv[2]) > 25) exit(1);
if (atof(argv[3]) > 15)exit(1);
if (atof(argv[4]) > 15)exit(1);
clrscr();
textbackground(atoi(argv[3]));
textcolor(atoi(argv[4]));
gotoxy(atoi(argv[1]),atoi(argv[2]));
cprintf("%s",argv[5]);
exit(0);
}
