# Coding Style Guide

Variable names for file pathes
* full path:  `pathname`
* directory where file resides: `path`
* file or directory name itself: `name`

# German
Ziel diese Guides ist, für die Erstellung von Skripten bei der fellowtech GmbH Vorgaben für einfache, aber skalierbare und wiederverwendbare Strukturen und Lösungen robusten und performanten Code konsistenten Stil und gute Lesbarkeit zu zeigen und als Basis für Verbessungen und Erweiterungen festzulegen.


## Generelle Hinweise
* Lesbarkeit geht vor Schreibgeschwindigkeit. Code muss wesentlich öfter gelesen als geschrieben werden.
* “Cleveres” Programmieren unter Ausnutzung von syntaktischen Abkürzungsmöglichkeiten einer Sprache ist der teure Weg.
* Skripte leben oft mehrere Jahre. Stell Dir vor, dass der Nächste auf Deinem Stuhl ein Psychopat ist und weiss wo Du wohnst
* Robuste Skripte, "atomic operations":  [David Pashley's Blog](http://www.davidpashley.com/articles/writing-robust-shell-scripts/)
* Jede Funktion erfüllt nach Möglichkeit nur eine Aufgabe

Einige Fragen, die sich zur Code-Beurteilung stellen lassen:
 *  Ist das Logging ausreichend, um später Fehler nachvollziehen zu können?
 *  Werden Skripte im Strict-Modus betrieben und zum Beispiel nicht gesetzte Variablen erkannt?
 *  Locking: Wird das Skript abgebrochen, wenn der Prozess noch oder schon läuft?
 *  Cleanup: wird nach gewollten oder ungewollten Skript-Abbrüchen aufgeräumt (Rückbau von Änderungen, Entfernen temporärer Dateien)?

## Planung neuer Skripte
Eine idealisierte Reihenfolge von Code-Bearbeitungsschritten, die verhindert, dass in operativen Schritten (Schritt 4) der Überblick verloren geht und die Codequalität fällt.

1. Einen einleitenden Hilfetext schreiben: Ziel/Verwendung des Scriptes Features, Optionen, Risiken, Parameter
2. Im Team: für jedes Modul und jede Funktion Schnittstellen und Funktionen definieren und als Modul/Funktionskommentare anlegen
3. Test-Ordner anlegen, der mit dem Script mitgeführt wird, dort im Laufe der Entwicklung für jedes beschriebene Feature ein Testscript hinterlegen. Das kann auch aus einer Zeile bestehen.
4. Funktionen mit Code füllen
5. Testen
6. Wenn das Skript zur Übergabe bereit ist, Beispiele aus dem Test-Ordner als Beispiele in der Hilfe einarbeiten

Wichtig ist, dass Code nicht ungetestet verbleibt und nach Möglichkeit Tests nach späteren Änderungen automatisiert wiederholt werden können.

In der Entwicklung (Teil 4 siehe oben ) sollte für jeden Skript-Block bzw. jede Funktion erst ein Grundgerüst beschrieben und kommentiert werden und erst dann in die Skript-Syntax abgestiegen werden. Kommentare sollen keine Übersetzung des Codes sein (das kann jeder Entwickler selbst) sondern Ergänzungen, die das zusammengefasste Ziel des Code-Abschnitts angeben.

Ein Beispiel in Pseudo-Code:

Datenfluss planen, Kommentare schreiben
```
## Take input either from given file or query zabbix for live data
```

Code schreiben
```
## Take input either from given file ...
if ( $InFile) {
    Start-FileQuery
}
## ... or query zabbix for live data
else{
    Start-ZabbixQuery $CONFIG.Server.ApiURL $CONFIG.Server.Timeout $Request
}
```


## Formatierungen und Sprache
### Sprache
Benutzerdokumentation in Conflunce ist immer in Deutsch, Entwickler-Dokumentation und Code grundsätzlich Englisch.

In der Programmierung wird in englischer Sprache gearbeitet (Code-Kommentare, `README.md`, Hilfetexte im Skript-Kopf), um Austauschbarkeit zu ermöglichen und fremden Code (Github) ohne sprachliche Brüche integrieren zu können. Zudem ist Code dann als Satz ohne Sprachwechsel lesbarer (`if (!exists(file)) panic()` vs `if (!exists(datei)) fehler()`)

### Meta-Inforamtionen
Folgende Meta-Informationen sollten im Kopfteil von Skripten, Funktionen und Klassen enthalten sein:

* Synopsis - Einzeiler was das Code tut
* Description - Detaillierte Beschreibung der Anwendung (falls nötig und nicht identisch mit Synopsis)
* Parameter und Optionen
* Rückgabewerte
* Examples - Vewendungsmöglichkeiten und Hinweise für die Anwendung

Wie diese Informationen definiert werden ist in jeder Sprache verschieden (z.B. als docblock, Definitionen im Code oder einfacher Kommentar), die angebotenen Möglichkeiten der Sprache sind zu nutzen.

### Kommentare
Platzierung von Kommentaren: Code-Zusammenfassungen über dem Code-Abschnitt, Programmier-Hinweise seitlich (Pseudo-Code):
```
## This comment describes what is achieved by the next lines
command1 $arg1 fcompx($arg2)   ## external module since fcom() does not support UTF-8
command2 $arg1
```
Führen durch if-then-else Strukturen und Schleifen (Pseudo-Code): Werden Kommentare zu z.Bsp. if, elseif, else Blöcken über die Wörter  "if, elseif, else " geschrieben, lassen diese sich aufgrund der Ausrückung sehr gut von Kommentaren innerhalb dieser Blöcke unterscheiden:

```
## Be sure to produce only apple juice by validating input
if ( $fruit = 'apple') {
    make 'applejuice'
}
## ... exit in case of bad input or ...
elsif ($fruit = 'potato' ) {
    exit 'Bad fruit "$fruit"!'
}
## ... skip production completely in case there are no fruits at all
else {
    continue
}
```

### Variablen- und Funktionsnamen
Diese Schreibweisen können nicht sprachübergreifend festgelegt werden. Sofern es keine Vorgaben für die Sprache (PHP: [PSR 1,2,12](https://www.php-fig.org/psr/), Python: [PEP8](https://www.python.org/dev/peps/pep-0008/)) gibt gelten folgende Regeln:

* Konstanten und Skript-Parameter: Grossbuchstaben und Unterstriche `$HOST_NAMES`
* Normale Variablen: CamelCase (`$NextHost`, `$MyCommand` )
* Funktionen: klein_mit_unterstrichen
* Schlüsselwörter, built-ins: Kleinbuchstaben (if, else, continue, break )
* An Array- und Hash-Variablen sollte ein "s" an den Namen angehängt werden um auszudrücken, dass diese Variable mehrere Werte aufnehmen kann. Für einfache Variablen sollte entsprechend die Einzahl verwendet werden. Ein Beispiel (Pseudo-Code):
```
for $Cloud in $Clouds; do
    echo "Nice cloud $Cloud"
done
```

### Befehlsparameter
Optionen ausschreiben, Lang-Versionen verwenden wo möglich, zum Beispiel (Pseudo-Code):
```
if ! grep  --word-regexp --quiet -- "$PERCONA_MIRROR" /etc/apt/source.list; then
    echo "deb PERCONA_MIRROR $DISTRIBUTION main" >> /etc/apt/sources.list
fi
```

### Bedingte Verzweigungen
Wichtig ist hier, den "default" Fall zu definieren auch wenn der nicht gebraucht wird (gegebenenfalls leer lassen). Damit wird deutlich gemacht, das dieser Fall nicht übersehen wurde sondern mit Absicht keine Aktion für den Default Fall definiert wurde. Ein Beispiel (Pseudo-Code):

```
case $Option in
    -h|--help)
        usage
        exit 0
     ;;
     *)
        ## nothing to do here
     ;;
 esac
```

## Anzeigen von Fortschritt und Fehlern
Textausgaben auf der Konsole sollten folgendermaßen angelegt werden, dass...
* Im Normalbetrieb sollten Fehler sofort auffallen, ohne von Fortschrittsmeldungen überdeckt zu werden
* Fortschritts-Anzeigen (Info-Meldungen) sowie Ausgaben von Skript-Details (Debug-Meldungen) zugeschaltet werden können
* Info-Meldungen und Debug-Meldungen nicht die Weiterleitung in Pipes und Datei-Umleitungen stören

Das kann folgendermassen erreicht werden:
* Der stdout-Kanal kann für Fortschrittsanzeigen verwendet werden, wenn die Ausgabe Fehlermeldungen nicht verdecken kann (Fortschrittsbalken, %-Zähler - _nicht_ zeilenweise (Beispiel: GIT-Befehle)).
* Standardmäßig laufen Skripte also ohne Ausgabe oder bei längerer Laufzeit mit einer kompakten Fortschrittsabzeige, welche Zeilen mit Fehlermeldungen nicht verdeckt.
* Fehler und Warnung werden über den stderr-Kanal ausgegeben  (Standard-Verhalten in allen Sprachen).
* der Fortschritt von Aktionen (Informationen für den Anwender) wird als verbose-Meldungen über den stderr-Kanal ausgegeben. Diese Ausgabe ist standardmäßig deaktiviert.
* Debug-Meldungen (Detail-Ausgaben zur Fehlersuche) werden über den stderr-Kanal ausgegeben. Diese Ausgabe ist standardmäßig deaktiviert


### Ausgabe-Kanäle
Es ergeben sich folgende Ausgabemöglichkeiten für Skripte und Module (siehe auch hier):

* stdout-Kanal
    * Datenausgabe
* stderr-Kanal
    * Debug: Detaillierte Informationen für Entwickler
    * Info/Verbose: Bestätigung, das Schritte erfolgreich durchgeführt wurden
    * Warning: Fehlermeldungen, welche nicht zu einem Skript-Anbruch führen
    * Error: Fehlermeldungen, welche zu einem Skript-Abbruch führen


### Fehlermeldungen
Es ist verbreitet, "Warnungen" als "leichte Fehler" relativ schwammig zu behandeln. Hier lässt sich eine sinnvolle Abgrenzung finden:

"Fehler" führen zu einem sofortigem Abbruch der Skriptausführung
Warnung werden angezeigt am Skript-Ende ausgewertet. Das Skript sollte mit einem Error-Status beendet werden, wenn Warnung aufgetreten sind.
So kann erreicht werden, das voneinander unabhänge Aktionen soweit wie möglich ausgeführt werden.

### Logging
Das Loggen in Text-Dateien oder das System-Log ist unter Unix-Systemen nicht nötig. Hier kann z.B. in einem Cron-Job durch den Aufruf des Skriptes in der Form (Pseudo-Code)

```
... script 2>&1 | logger --tag "MySCRIPT"
```
die komplette Skript-Ausgabe an das Syslog übergeben werden.

## ​Validierung von Daten
Eingabe-Daten müssen an einer Stelle im Skript verifiziert werden (wurde ein Integer oder ein Array übergeben?). Diese Validierung muss unmittelbar nach dem Datenempfang stattfinden, da Variablen später an verschiedenen Stellen tief im Code genutzt werden können.

## Funktionen und Module
Module stellen "Backend"-Funktionen für "Frontend"-Skripte. Das bedeutet, das nach Möglichkeit sämtliche Interfaces zu Benutzern, Dateien und Datenbanken im Skript geschrieben werden und die Funktionen in den Modulen nur Daten bearbeiten ohne Interface-Code mitzuschleppen. Erst dadurch werden Module wirklich austauschbar.

### Aufgaben für Skripte
* Validieren von Eingabe-Logik (Optionen und Parameter),
* Logging in Dateien,
* Einlesen von Konfig-Dateien,
* Einlesen von Dateien,
* Erstellen von Verbindungen zu Datenbank-Servern,
* Fehlerbehandlung (Skript-Exit)

### Aufgaben für Modul-Funktionen
* Validieren von Eingabe-Daten,
* Datenbank-Abfragen,
* Programm-Logik
* Rückgabe von Fehlern an das aufrufende Skript

## Objektorientierte Programmierung
> Tell, don't ask: Good OOP is about telling objects what you want done, not querying an object and acting on its behalf. Data and operations that depend on that data belong in the same object.

Objekte sollten also wiederverwendbare, komplexere Aktionen anbieten statt diese Logiken z.B. in Controllern oder Skripten jedes mal neu zu implementieren.

## Konfigurationen, Default Werte
* Updates bzw. Weiterentwicklung von Software bedeutet das sich Default Werte ändern können. Das Überschreiben beziehungsweise Festsetzen von Default Werten (zum Beispiel in Konfigurations-Dateien) verhindert diese Updates.
* Default Werte sind oft von den Entwicklern sorgfältig gewählt und sollten nur mit gutem Grund und in guter Einsicht in die Problematik geändert werden.
