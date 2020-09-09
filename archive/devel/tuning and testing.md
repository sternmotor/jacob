# Tuning von Anwendungen
Beispiel: Änderung an MySQL Server Konfiguration
* Änderungen sollten methodisch getestet werden. Nicht messbare Änderungen (ohne Testumgebung, parallele Änderungen an mehreren Parametern) sind weitgehend sinnfrei.
* Änderungen sind meistens nur feststellbar, wenn tatsächlich ein Engpass besteht. Dieser kann in der Entwicklung künstlich erzeugt werden, um anzunehmende Produktiv-Lasten zu simulieren. Besteht produktiv kein Engpass, sollte nicht getunt werden.
* Änderungen können per [Versionsverwaltung](../Systeme/Versionsverwaltung.md) erfasst und nachvollziehbar sowie umkehrbar gemacht werden
