#include <iostream.h>
#include <process.h>
#include <bios.h>
#include <string.h>
#include <ctype.h>

#define SCROLL 16
#define NUM    32
#define CAPS   64

int main(int argc,char *argv[])
{
if (!strcmp(argv[1],"CHECK") || !strcmp(argv[1],"check"))  	//Parameter CHECK oder check eingegeben
	{
	int stat=bioskey(2),			//Statusbyte
	    level;

	if (stat & SCROLL)
		{
		level=11;
		if (stat & NUM)  level += 1;
		if (stat & CAPS) level += 1;
		exit(level);
		}
	if (stat & CAPS)
		{
		level=22;
		if (stat & NUM)  level += 1;
		exit(level);
		}
	if (stat & NUM)
		{
		level=33;
		exit(level);
		}
      exit(0);
	}

cout << "\n\n";                     	//kein oder falsches Argument
cout << "Dieses Programm prft den Status der Scroll-, Caps- und\n";
cout << "Numlocktaste. Der Status wird ber den Errorlevel weitergegeben\n";
cout << "und kann mit z.B. <if errorlevel=22 goto Cd> verarbeitet werden.\n";
cout << "\n";
cout << "Dem Status entsprechen folgende Errorlevel:\n";
cout << "\n";
cout << "  	Scroll		Caps		Num\n\n";
cout << "Scroll	11		12		13\n";
cout << "Caps			22		23\n";
cout << "Num					33\n";
cout << "\n";
cout << "Zur Unterbindung dieses Textes <chktast CHECK> aufrufen\n\n";
exit(0);
}