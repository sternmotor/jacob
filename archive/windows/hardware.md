## Inhaltsverzeichnis

{{ page.toc }}

## CodeSchnipsel

#### Allgemeine Informationen

<pre>Get-WmiObject -Class Win32_BIOS  # Bios Manufacturer Serial Version
Get-WmiObject -Class Win32_Processor  # Prozessor
Get-WmiObject -Class Win32_LogicalDisk -Filter "DriveType=3" -ComputerName . | Measure-Object -Property FreeSpace,Size -Sum # freee disk space</pre>

Anzahl CPU Cores (scheint nicht einfacher zu gehen ^^)

<pre>$Processors = Get-WmiObject -class win32_processor -Property 'NumberOfCores'
$CoreCounter = $Processors.NumberOfCores | Measure-Object -Sum
$CoreCounter.sum</pre>

#### OMSA

*   Siehe [OMSA Anleitungen](mks://localhost/Systeme/v1/10_IT-System_SC/10_Hardware/Server/DRAC,_OMSA/OMSA/Anleitungen "Systeme/v1/10_IT-System_SC/10_Hardware/Server/DRAC%2C_OMSA/OMSA/Anleitungen") und [Server Hardware Anleitungen](mks://localhost/Systeme/v1/10_IT-System_SC/10_Hardware/Server/Hardware/Anleitungen "Systeme/v1/10_IT-System_SC/10_Hardware/Server/Hardware/Anleitungen").

Dell Chassis Model

<pre>$ComputerSystem = Get-WmiObject win32_computersystem | select Model
$ComputerSystem.Model</pre>