# How to simulate web login via monitoring

Find login queries via Chrome or Firebug
Wichtig: Clear in dier Toolbar des Entwicklungsfensters auswählen, wenn eine Analyse durch ist
* im Chrome Browser F12 drücken, im debug-Fenster
    * Network > Headers > Haken setzen: preserve Log
* im Browser das Login nachvollziehen und beim Click auf "Login" folgendermassen analysieren:
* Im Debug-Fenster:
    * RequestURl > 1. Hop redirect  Code 302
    * Response: Location suchen, im Liste links suchen z.B. index.php und diese Seite aufsuchen/anclicken
        * General > 200 ok
            * Request Method POST:
            * Form Data > view Source  > das im Post eintragen
            * Hier POST auslesen
