# include <stdio.h>
# include <conio.h>
# include <stdlib.h>

void main()
{
int store[180],cnt1,cnt2,max;
char frage;
while(1)
	{
	clrscr();
	for (cnt1=0;cnt1<180;cnt1++) store[cnt1]=0;
	printf("Berechnung aller Primzahlen bis:");
	scanf ("%d",&max);
	if (max>180) continue;

	for (cnt1=2;cnt1<=max;cnt1++)
		{
		if (!store[cnt1])
			{
			for (cnt2=cnt1*cnt1;cnt2<=max;cnt2=cnt2+cnt1)
			store[cnt2]=1;
			}
		if (!store[cnt1])               //store[cnt1] vielleicht ge„ndert...
			{
			printf("\n%d",cnt1);
			}
		}
	printf("\n\nNochmal  ?");
	frage=getch();
	if (frage=='j') continue;
	exit(0);
	}
}
