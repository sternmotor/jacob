Windows OS 
==========

Repair
------

Speedup slow windows

* temporarily disable antivir software, then:
	1. remove all unneeded software, reboot
	2. run ccleanup 
	3. check for broken windows files:

        sfc /scannow

	4. repair broken windows files

        DISM /Online /Cleanup-Image /RestoreHealth

* re-enable antivir software
* other scan options:
	* standard scan

        DISM /Online /Cleanup-Image /CheckHealth

	* deep scan

        DISM /Online /Cleanup-Image /ScanHealth
  	 

Software
--------

Install/ remove windows feature

    Install-WindowsFeature -IncludeManagementTools SNMP-Service
    Remove-WindowsFeature SNMP-Service

Install packages via [chocolatey](https://chocolatey.org/)
TODO:
* ccleaner

    Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    choco upgrade chocolatey

    $System = @(
        '7zip',
        'treesizefree',
        'cmder'
    )

    $Work = @(
        'filezilla',
        'powershell',
        'sysinternals',
        'truecrypt',
        'vim',
        'notepadplusplus.commandline',
        'notepadplusplus'
        'teamviewer'
    )

    $Desktop = @(
        'firefox',
        'googlechrome',
        'seafile-client',
        'thunderbird',
        'vlc',
    )

    foreach($Pkg in ($System + $Work + $Desktop)) {
        choco install --yes --acceptlicense --limit-output --ignore-checksums $Pkg
        #choco upgrade $Pkg
    }


Windows Defender
----------------

Setzen und Entfernen von Pfad-Ausnahmen

    Get-MpPreference | select -ExpandProperty ExclusionPath
    #ExclusionPath                                 : {\\jarvis\repository\backup-disaster\HyperV Backup\module, C:\Program
    #                                                Files\WindowsPowerShell\Modules\HyperVBackup, C:\Program
    #                                                Files\WindowsPowerShell\Modules\HyperVBackup\wmievent.ps1}
    $ep = Get-MpPreference | select -ExpandProperty ExclusionPath
    Remove-MpPreference -ExclusionPath $ep
    Set-MpPreference -ExclusionPath $ep

Setzen und Entfernen von Prozess/Exe-Ausnahmen

    get-command powershell.exe | select -ExpandProperty Source 
    Set-MpPreference -ExclusionProcess 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
     
    Get-MpPreference | select -ExpandProperty ExclusionProcess
    # C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
    $pr = Get-MpPreference | Select -ExpandProperty ExclusionProcess
    Remove-MpPreference -ExclusionProcess $pr


Scheduled Tasks
---------------

Install scheduled task

    $Exe = 'powershell.exe'
    $Arg = '-NoP -Command "Start-Transcript C:\ProgramData\hypervbackupiscsi.log; Import-Module HyperVBackup; Start-Backup -Path d:\backup -verbose -debug"'
    $Params = @{
        TaskName    = "HyperV Backup iSCSI"
        Description = "Nightly HyperV VM export"
        Action      = New-ScheduledTaskAction -Execute "$Exe" -Argument "$Arg"
        Trigger     = New-ScheduledTaskTrigger -Daily -At 1am
        Settings    = New-ScheduledTaskSettingsSet -Compatibility Win8 -Hidden -RestartCount 0
        User        = "System"
        RunLevel    = "Highest"
    }
    Register-ScheduledTask @Params

Remove scheduled tasks

    Unregister-ScheduledTask -TaskName MyTask



Drivers
-------

gpo

    gpupdate /force /target:computer

## Environment variables

List of essential variables
* `ALLUSERSPROFILE` :  `%SystemDrive%\ProgramData`
* `APPDATA` :	 	   `%HOMEDRIVE%\Users\%USERNAME%\AppData\Roaming`
* `ClientName` :	   `Terminal servers only - the ComputerName of a remote host.`
* `COMPUTERNAME` :	   `<computername>`
* `ERRORLEVEL` :	   `The current ERRORLEVEL value, automatically set when a program exits.`
* `HOMEDRIVE` :		   `C:`
* `HOMEPATH` :		   `\Users\%USERNAME%`
* `LOCALAPPDATA` :	   `%HOMEDRIVE%\Users\{username}\AppData\Local`
* `LOGONSERVER` :	   `\\{domain_logon_server}`
* `PATH` :             `PATH `
* `PSModulePath` :	   `%SystemRoot%\system32\WindowsPowerShell\v1.0\Modules\`
* `Public` :	 	   `%HOMEDRIVE%\Users\Public`
* `USERDOMAIN` :	   `<AD Domain>`
* `USERNAME` :		   `<icke>`
* `USERPROFILE` :	   `%HOMEDRIVE%\Users\%USERNAME%`
* `SYSTEMDRIVE` :	   `C:`
* `SYSTEMROOT` :       `%SystemDrive%\Windows`



## Inhaltsverzeichnis

{{ page.toc }}

## Codeschnipsel

#### Software Installation

Download and install [Chocolatey](https://chocolatey.org/packages "https://chocolatey.org/packages") packages:

<pre>Invoke-WebRequest https://chocolatey.org/install.ps1 -UseBasicParsing | Invoke-Expression
choco install --yes --acceptlicense --limit-output --ignore-checksums git vim
refreshenv</pre>

#### <span style="line-height: 1.5;">Allgemeine Informationen</span>

Betriebssystem-Version

<pre>(Get-WmiObject -Query "SELECT Caption FROM win32_operatingsystem").Caption
</pre>

<div>

Uptime ( <span style="color: rgb(119, 119, 119); line-height: 1.5; background-color: rgb(254, 254, 254);">TimeSpan object)</span>

<pre>$WMIQuery = Get-WmiObject -Query "SELECT LastBootupTime FROM win32_operatingsystem"
$BootTime = $WMIQuery.ConvertToDateTime($WMIQuery.LastBootUpTime)
(Get-Date) - $BootTime      
</pre>

</div>

Boottime (DateTime Object)

<pre>$WMIQuery = Get-WmiObject -Query "SELECT LastBootupTime FROM win32_operatingsystem"
$WMIQuery.ConvertToDateTime($Query.LastBootUpTime)</pre>

Installationsdatum (für Vergleiche mit anderen Zeitstempeln)

<div class="line number1 index0 alt2">

<pre>[system.management.managementdatetimeconverter]::ToDateTime(
    (Get-WmiObject win32_operatingsystem | select Installdate).InstallDate
)</pre>

</div>

x86/64Bit

<pre>(Get-WmiObject -Query "SELECT OSArchitecture FROM win32_operatingsystem").OSArchitecture</pre>

Installierte Hotfixes (dauert ein bisschen)

<pre>Get-WmiObject -Class Win32_QuickFixEngineering </pre>

ServicePack Info

<pre>Get-WmiObject Win32_OperatingSystem | Select BuildNumber,BuildType,OSType,ServicePackMajorVersion,ServicePackMinorVersion</pre>

Alle Umgebungsvariablen anzeigen

<pre>Get-ChildItem Env:</pre>

#### Powershell Installation

.NET Framework 3.5 installieren (2008R2)

<pre>Import-Module Servermanager
Add-WindowsFeature NET-Framework
exit</pre>

Alternativ kann die Setup-Datei [hier](http://download.microsoft.com/download/2/0/e/20e90413-712f-438c-988e-fdaa79a8ac3d/dotnetfx35.exe "http://download.microsoft.com/download/2/0/e/20e90413-712f-438c-988e-fdaa79a8ac3d/dotnetfx35.exe") heruntergeladen und installiert werden (ca. 240MB). 

<div class="errormsg systemmsg" id="sessionMsg">

<div class="inner">

*   .NET Features sind erst in einer neu erstellten Session verfügbar (remote oder lokal), daher das `exit`

</div>

</div>

.NET Framework überprüfen

<pre>Get-WindowsFeature -name  "NET-*"
</pre>

> <div>Display Name                                            Name</div>
> 
> <div>------------                                            ----</div>
> 
> <div>[X] .NET Framework 3.5.1-Features                       NET-Framework</div>
> 
> <div>    [X] .NET Framework 3.5.1                            NET-Framework-Core</div>
> 
> <div>    [X] WCF-Aktivierung                                 NET-Win-CFAC</div>
> 
> <div>        [X] HTTP-Aktivierung                            NET-HTTP-Activation</div>
> 
> <div>        [X] Nicht-HTTP-Aktivierung                      NET-Non-HTTP-Activ</div>

<span style="line-height: 1.5;">Powershell Version  überprüfen</span>

<pre>(Get-Host).version</pre>

#### Prozesse und Dienste

Dienste auslesen, welche den Starttyp "Automatisch" haben aber nicht laufen

<pre>$WMIQueryParams = @{
    Class = 'Win32_service'
    Filter = "StartMode='auto' and not State='Running'"
    Property = 'Caption','Name', 'StartMode', 'State' # include filter properties
}
Get-WmiObject @WMIQueryParams | Select Name, Caption</pre>

Prozesse zu Diensten zuordnen: <span style="line-height: 1.5;">Prozesse können von mehreren Diensten benutzt werden. Alle Dienste auflisten, welche zu einer `ProcessID` gehören:</span>

<pre>$ProcessID = 704
Get-WmiObject win32_service  | where { $_.ProcessID -eq $ProcessID } | select Name, State</pre>

Dienste beenden und Start-Modus auf "manuell" setzen

<pre>$Service = "wuauserv"
Set-Service $Service -startupType disabled
Stop-Service $Service
</pre>

#### Feature Installation

<pre>Import-Module servermanager
Add-WindowsFeature WinRm-IIS-Ext</pre>

#### Registry

Eintrag aktualisieren

<pre>$RegUpdate = @{
    Path = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Virtualization'
    Type = 'String'     # REG_SZ = String
}
Set-ItemProperty @RegUpdate -Name 'DefaultExternalDataRoot' -Value "$BaseDir"
Set-ItemProperty @RegUpdate -Name 'DefaultVirtualHardDiskPath' -Value ("{0}Virtual Hard Disks" -f $BaseDir)</pre>

#### Geplante Aufgaben

COM Schnittstelle für die Verwaltung geplanter Aufgaben unter Powershell 2.0\. Beschreibungen für Result Codes gibt es [hier](https://msdn.microsoft.com/en-us/library/windows/desktop/aa383604(v=vs.85).aspx "https://msdn.microsoft.com/en-us/library/windows/desktop/aa383604(v=vs.85).aspx").

Geplante Aufgaben können für das Ausführen von Aufgaben mit erhöhten Rechten angewendet werden, siehe [hier](mks://localhost/Abteilungen/Entwicklung/Executive/Tools/Windows/Powershell/Administration/Benutzer,_Gruppen,_Rechte#Admin-Rechte_.2F_Elevated_Priveleges "Abteilungen/Entwicklung/Executive/Tools/Windows/Powershell/Administration/Benutzer%2C_Gruppen%2C_Rechte#Admin-Rechte_.2F_Elevated_Priveleges").

<pre>$TaskHandler = New-Object -ComObject Schedule.Service
$TaskHandler.connect()
$TaskFolder=$TaskHandler.GetFolder('\')
# GetTasks(1): get all tasks including those which are hidden, otherwise 0
$Tasks = $TaskFolder.GetTasks(1)

$Tasks | select name
$XmlData = $Tasks | foreach {([Xml]$_.Xml).Task}
foreach ($Data in $XMLData ) { $Data.RegistrationInfo.Author   }
$Task1Config.Settings

# User Typ auslesen, unter welchem der Task läuft - hierblei bleibt COM Datenstruktur erhalten. LogonType 3 = Domain User, 5=SYSTEM, 4=other
foreach ($Task in $Tasks) {$Task.Definition.Principal.LogonType}</pre>

Das Einrichten eines Powershell Skriptes als geplanten Tasks funktioniert in Powershell 2 alternativüber die alte "SCHTASKS.EXE". Dabei muss Powershell.exe mit dem Skript als Parameter aufgerufen werden. Wichtig ist hier Die korrekte Verschachtelung von '' innheralb von "":

*   Beispiele:

<pre>schtasks /CREATE /SC hourly /MO 2  /TN "Zabbix LSI Raid Discoverer" /TR "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -noprofile -executionpolicy Unrestricted -file 'C:\Program Files (x86)\Zabbix Agent\scripts\raid_discovery.ps1'"
schtasks /CREATE /SC minute /MO 10 /TN "Zabbix LSI Raid Checker"    /TR "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -noprofile -executionpolicy Unrestricted -file 'C:\Program Files (x86)\Zabbix Agent\scripts\raid_trapper_checks.ps1'"</pre>

*   Dabei sollte innerhalb von Skripten schtasks mit `2>&1` aufgerufen werden. Damit generieren Ausgaben in den Fehlerkanal echte Powershell Exceptions

#### Drucker

Übersicht über installierte Drucker

<pre>Get-WmiObject -Class Win32_Printer | Select-Object -Property Name, DriverName, Portname, SystemName, Comment, PrintProcessor, Shared, ShareName | export-csv C:\temp\DruckerÜbersicht.txt
</pre>
