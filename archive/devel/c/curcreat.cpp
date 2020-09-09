
 44, 45,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
 43, 44, 45, 45,255,255,255,255,255,255,255,255,255,255,255,255,
255, 43, 44, 45, 45, 45,255,255,255,255,255,255,255,255,255,255,
255, 43, 43, 44, 45, 45, 45, 45,255,255,255,255,255,255,255,255,
255,255, 43, 43, 44, 45, 45, 45, 45, 45,255,255,255,255,255,255,
255,255, 43, 43, 43, 44, 45, 45, 45, 45, 45, 45,255,255,255,255,
255,255,255, 43, 43, 43, 44, 45, 45, 45, 45, 45, 45, 45,255,255,
255,255,255, 43, 43, 43, 43, 42, 42, 42, 42, 42, 42, 42, 44, 43,
255,255,255,255, 43, 43, 43, 42, 42, 42, 42, 42, 42, 42, 42,255,
255,255,255,255, 43, 43, 43, 42, 42, 42, 42, 42, 42, 42,255,255,
255,255,255,255,255, 43, 43, 42, 42, 42, 42, 42, 42,255,255,255,
255,255,255,255,255, 43, 43, 42, 42, 42, 42, 42,255,255,255,255,
255,255,255,255,255,255, 43, 42, 42, 42, 42,255,255,255,255,255,
255,255,255,255,255,255, 43, 42, 42, 42,255,255,255,255,255,255,
255,255,255,255,255,255,255, 42, 42,255,255,255,255,255,255,255,
255,255,255,255,255,255,255, 42,255,255,255,255,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,

abxxxxxxxxxxxxxx
cabbxxxxxxxxxxxx
xcabbbxxxxxxxxxx
xccabbbbxxxxxxxx
xxccabbbbbxxxxxx
xxcccabbbbbbxxxx
xxxcccabbbbbbbxx
xxxccccdddddddac
xxxxcccddddddddx
xxxxcccdddddddxx
xxxxxccddddddxxx
xxxxxccdddddxxxx
xxxxxxcddddxxxxx
xxxxxxcdddxxxxxx
xxxxxxxddxxxxxxx
xxxxxxxdxxxxxxxx
xxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxx












in der 16x24 - Matrix sind die Farben von 0 bis 255 enthalten, 
jede Zahl muá dabei um 2 erh”ht werden (suspekt...)


          MOUSECURSORSET

            PROTOTYPE

            extern void far mousecursorset (MouseCursor far *mousecursor)

            INPUT

            mousecursor - MouseCursor pointer to mouse cursor data

            OUTPUT

            no value returned

            USAGE

            MOUSECURSORSET defines the cursor according to the data in the
            MouseCursor structure.  The hot spot for the cursor is set by
            mousecursor.hotspotx, mousecursor.hotspoty.  The values for
            mousecursor.hotspotx and mousecursor.hotspoty must be within
            the cursor.  Valid mousecursor.hotspotx values are from 0 to
            15 and mousecursor.hotspoty ranges from 0 to 23.

            SEE ALSO

            MOUSECURSORDEFAULT, MOUSEENTER, MOUSESHOW

            EXAMPLE

            /*
             * enable,show mouse, and switch to a different mouse cursor
             */

            #include <stdlib.h>
            #include <conio.h>
            #include "svgacc.h"

            void main(void)
            {
               int vmode;

               MouseCursor bigmousecursor = {
                 1,1,

0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,
0,15,15,0,0,255,255,255,255,255,255,255,255,255,255,255,
0,15,15,15,15,0,0,0,255,255,255,255,255,255,255,255,
0,15,15,15,15,15,15,15,0,0,255,255,255,255,255,255,
0,15,15,15,15,15,15,15,15,15,0,0,0,255,255,255,
0,15,15,15,15,15,15,15,15,15,15,15,15,0,0,255,
0,15,15,15,15,15,15,15,15,15,15,15,15,15,0,255,
0,15,15,15,15,15,15,15,15,15,15,15,0,0,255,255,
0,15,15,15,15,15,15,15,15,15,15,0,255,255,255,255,
0,15,15,15,15,15,15,15,15,0,0,255,255,255,255,255,
0,15,15,15,15,15,15,15,15,0,255,255,255,255,255,255,
0,15,15,15,15,15,0,15,15,15,0,255,255,255,255,255,
0,15,15,15,15,0,0,15,15,15,0,255,255,255,255,255,
0,15,15,0,0,255,255,0,15,15,15,0,255,255,255,255,
0,15,0,255,255,255,255,0,15,15,15,0,255,255,255,255,
0,0,255,255,255,255,255,255,0,15,15,15,0,255,255,255,
255,255,255,255,255,255,255,255,255,0,15,15,15,0,255,255,
255,255,255,255,255,255,255,255,255,0,15,15,15,0,255,255,
255,255,255,255,255,255,255,255,255,255,0,15,15,15,0,255,
255,255,255,255,255,255,255,255,255,255,255,0,15,15,15,0,
255,255,255,255,255,255,255,255,255,255,255,0,15,15,15,0,
255,255,255,255,255,255,255,255,255,255,255,255,0,15,15,0,
255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,
255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255
               };

               vmode = videomodeget();
               if ( !whichvga() )
                 exit(1);
               if ( whichmem() < 512)
                 exit(1);
               if ( !whichmouse())
                 exit(1);
               res640();
               mouseenter();
               drwstring(1,7,0,"press a key to return to default
            cursor",0,0);
               mousecursorset(bigmousecursor);
               mouseshow();
               getch();
               mousecursordefault();
               drwstring(1,7,0,"press a key to end
            ",0,0);
               getch();
               mousehide();
               mouseexit();
               videomodeset(vmode);
               exit(0);
            }




