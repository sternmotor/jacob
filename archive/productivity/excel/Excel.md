# Excel
## Navigation + Markieren

**STRG-Hoch-Runter** bis zum Ende von Werten, **+SHIFT** markiert dann

**STRG-Bildauf/Ab** Tabellenblätter wechseln	

**STRG-POS1** Spalte bis Anfang

## Editieren
**F2** Zellinhalt editieren

**STRG-1** Zahlenformat wechseln

**STRG-H** Suchen und Ersetzen

**ALT-ENTER** Zeilenumbruch

**SHIFT-F2** Kommentar einfügen oder bearbeiten

**SHIFT-F2** Kommentar einfügen

### Wert in Zellbereich eingeben
1. Zellbereich markieren (**SHIFT+STRG+Hoch/Runter**)
2. Inhalt schreiben (wird nur in erster Zelle angezeigt)
4. mit **STRG+ENTER** Eingabe abschließen

### Formel in Zelle auf Zellbereich anwenden
1. Zellinhalt kopieren
2. Zellbereich markieren (**SHIFT+STRG+Hoch/Runter**)
3. Zellinhalt einfügen

## Ansicht
**F8** Ribbon an/aus

## Formeln
**F4** $ - Variablen Fixierung an/aus

### SVerweis
Vorgehen:
Wertetabelle in Excel einfügen, markieren und Namen vergeben (z.B. "Horst"). Formel neben Zelle schreiben, bei Wertetabelle "Horst" einegeben. Dies spart das Einfügen von $..$.. .

    sverweis(
        <Wert der in Zelle und Wertetabelle übereinstimmen muss>;
        <$Werte$tabelle, Spalten 1-n>;
        <Spalte aus Wertetabelle 1-n>;
        Falsch()
    )