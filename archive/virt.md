# Virtualisierungsthemen Traso

## VmPlacement

Kriterien siehe INFRA-520

* RAM +/- 10%
* HDD Platz +/-10%
* min. CPU Cores (nur echte Kerne, +/- 15%
* wenn db01 darf kein weiterer db01 laufen
* keine weitere Maschine des Kunden sollten auf dem Server laufen
* Nicht vmhost06, vmhost07, vmhost-cXX
* Optional, wahrscheinlich Quatsch:
	* Auslastung des Servers priorisieren: CPU
		* 04:00 - 09:00	Morning
		* 09:00 - 16:00	Daytime
		* 16:00 - 22:00 Evening
		* 22:00 - 04:00 Night


## VmShift

VM auf entfernten Host übertragen

* LVMs entfernt anlegen
* Source VM stoppen, DRDB anlegen, VM starten
* DRDB sync LVM
* Source VM stoppen
* Target DRDB entfernen
* Target VM starten



	
