#  DNS

Avoid downtimes when switching DNS entries

Das DNS-Umstellungs-Problem habe ich immer folgendermassen umgangen (ohne Downtime):
1. Start: alte öffentliche IP, Dienste dahinter funktionieren, DNS verweist auf alte IP. Die neue öffentliche IP ist vorhanden
2. Vorbereitung: die Firewall wird so konfiguriert das die Dienste genau so wie mit der alten IP funktionieren und mit Fake-DNS Einträgen getestet
3. Umstellung: DNS Einträge umstellen so das diese auf die neue IP verweisen - jeder "Client" hat dann innerhalb von 48h Zugriff über die neue IP
4. Aufräumen: Nach 48h die alte IP / Firewall abräumen
