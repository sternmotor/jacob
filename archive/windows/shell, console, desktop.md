# Windows server console and desktop usage

# PDF printer: PDF24
Download msi: https://de.pdf24.org/pdf-creator-download-start.html#msi

Setup for printing to downloads folder:

* PDF24 aufrufen > PDF Drucker Assistent > Einstellungen (unten im grauen Bereich)
    * Assistent: optional > PDF nach Speichern öffnen (falls ihr das wollt)
    * PDF Drucker
* Save automatically
* Profile: Beste Quality
* Activate "override existing"
* Deactivate Features
    * Fax
    * Fax Profil
    * Online Konverter
    * Online PDF Tools
    * Cloud Print
    * Embedded Browser

## Remote Desktop Server

Message to all users logged in currently
```
msg * 'my message'
```


## Explorer
This page was lifted from http://cpcug.org/user/clemenzi/technical/WinExplorer/CommandLineOptions.htm.
Parameters are separated by commas. Many combinations are allowed, but only a few examples are given.

Explorer.exe c:\                Open directory as a single pain of icons
Explorer.exe /e,c:\             Explore drive as 2 lists -
                                  directories on left & files on right
Explorer.exe /e,/root,c:\       Explore drive without showing other drives
Explorer.exe /n,/e,/select      Opens showing only drives
Explorer.exe /e,/idlist,%I,%L   From Folder\..\Explore in the registry
                                  %I - ID number
                                  %L - Long filename

Explorer.exe  /e,DriveOrDirectory
Explorer.exe  /e,/root,directory,sub-directory
Explorer.exe  /e,/root,directory,/select,sub-directory


/e  List (explorer) view, Show large icons if missing (Open view)  
/root  Sets the top level folder.  
/select  Specifies that the directory should be selected without displaying its contents.  
/idlist,%I  Expects an ID/handle. May help with cacheing. By itself, opens the desktop as icons.  
/inproc  Stops display of window (I don't know why this is useful)  
/n Always opens a new window, even if the selected folder is already open.

## Taskleiste
Ihr habt ein Programm aus der Taskleiste einmal gestartet z.B. den Internet Explorer. Nun wollt ihr ein zweitesmal das Programm starten. Klickt auf das Symbol in der Taskleiste mit gedrückter SHIFT-Taste noch einmal und schon öffnet sich das  Programm zum zweiten Mal.

## Keyboard shortcuts

Long List: [here](https://support.microsoft.com/de-de/help/12445/windows-keyboard-shortcuts)
* `C-H`: Search & Replace
* `C-F`: Search
* `CTRL + SHIFT + ESC`: Task Manager
* `WIN + I`: Settings
* `WIN + L`: Log out
* `WIN + D` + `ALT-F4`: Log out any way
* `WIN + CTRL + D`: New virtual desktop
* `WIN + CTRL + Left/Right`: Switch virtual desktop
* `WIN + CTRL + F4`: Close virtual desktop

## Management consoles

* [http://www.primemsp.com/content/msc_shortcuts.aspx]

| Admin Applet	     |       Command |
|--------------------|---------------|
|AD Domains and Trusts       | domain.msc |
|Active Directory Management | admgmt.msc |
|AD Sites and Services       | dssite.msc |
|AD Users and Computers      | dsa.msc |
|ADSI Edit                   | adsiedit.msc |
|Authorization manager       | azman.msc |
|Certification Authority Management | certsrv.msc |
|Certificate Templates       | certtmpl.msc |
|Cluster Administrator       | cluadmin.exe |
|Computer Management         | compmgmt.msc |
|Component Services      | comexp.msc |
|Configure Your Server   | cys.exe |
|Device Manager      | devmgmt.msc |
|DHCP Management      | dhcpmgmt.msc |
|Disk Defragmenter   | dfrg.msc |
|Disk Manager   | diskmgmt.msc |
|Distributed File System | dfsgui.msc |
|DNS Management | dnsmgmt.msc |
|Event Viewer | eventvwr.msc |
|Indexing Service Management | ciadv.msc |
|IP Address Manage | ipaddrmgmt.msc |
|Licensing Manager | llsmgr.exe |
|Local Certificates Management | certmgr.msc |
|Local Group Policy Editor | gpedit.msc |
|Local Security Settings Manager | secpol.msc |
|Local Users and Groups Manager | lusrmgr.msc |
|Network Load balancing | nlbmgr.exe |
|Performance Monitor | perfmon.msc |
|PKI Viewer | pkiview.msc |
|Public Key Management | pkmgmt.msc |
|Quality of Service Control Management | acssnap.msc |
|Remote Desktop | tsmmc.msc |
|Remote Storage Administration | rsadmin.msc |
|Removable Storage | ntmsmgr.msc |
|Removable Storage Operator Requests | ntmsoprq.msc |
|Routing and Remote Access Manager | rrasmgmt.msc |
|Resultant Set of Policy | rsop.msc |
|Schema management | schmmgmt.msc |
|Services Management | services.msc |
|Shared Folders | fsmgmt.msc |
|SID Security Migration | sidwalk.msc |
|Telephony Management | tapimgmt.msc |
|Terminal Server Configuration | tscc.msc |
|Terminal Server Licensing | licmgr.exe |
|Terminal Server Manager | tsadmin.exe |
|Teminal Services RDP	| MSTSC  |
|Teminal Services RDP to Console	| mstsc /v:[serve ] /console	  |
|UDDI Services Managment | uddi.msc |
|Windows Mangement Instumentation | wmimgmt.msc |
|WINS Server manager | winsmgmt.msc |



# Powershell

Command Prompt für lange Verzeichnisnamen
```
function Global:prompt {"$PWD`n> "}
```

## Inhaltsverzeichnis

{{ page.toc }}

## Codeschnipsel

### Powershell

Warnungen (bekannte Fehler, welche nicht zum Abbruch führen) in rot als Einzeiler schreiben:
```Powershell
[Console]::ForegroundColor = 'red'
[Console]::Error.WriteLine($Message)
[Console]::ResetColor()
```

Powershell Objekte in sortierbarer GUI ausgeben

<pre>...  | Out-GridView</pre>

Powershell Objekt in voller Breite ausgeben

<pre>...  | ft  | out-string -width 4000</pre>

Datei in Clipboard kopieren

<pre>function Set-ClipBoard([string]$Text) {
    Add-Type -AssemblyName System.Windows.Forms
    $TextBox = New-Object System.Windows.Forms.TextBox
    $TextBox.Multiline = $False
    $TextBox.Text = $Text
    $TextBox.SelectAll()
    $TextBox.Copy()
}</pre>

#### Cmd

CMD Fehler als Powershell `$Error` ausgeben

*   `2>&1` am Ende des Befehls bewirkt, das Fehlermeldungen als Powershell Exceptions ausgewertet werden und sich damit den globalen Fehlerbehandlungs-Einstellungen folgen. Die Verwendung eines Powershell-Arrays läßt die saubere Auswertung von Leerzeichen zu.

<pre>$KEYGEN_OPTIONS = @(
    '-t', $KEY_TYPE,
    '-f', $PRIVATE_KEY_FILE,
    '-C', $COMMENT,
    '-b', $BIT_LENGTH,
    '-N', '""'
)
# ...
& $KEYGEN_EXE $KEYGEN_OPTIONS 2>&1</pre>

Powershell Code in cmd Skript ausführen - diesen Code als `test.cmd` abspeichern, testen mit zum Beispiel `test.cmd arg1 arg2 arg3`

<pre>@@:: This prolog allows a PowerShell script to be embedded in a .CMD file.
@@:: Any non-PowerShell content must be preceeded by "@@"
@@setlocal
@@set POWERSHELL_BAT_ARGS=%*
@@if defined POWERSHELL_BAT_ARGS set POWERSHELL_BAT_ARGS=%POWERSHELL_BAT_ARGS:"=\"%
@@PowerShell -Command Invoke-Expression $('$args=@(^&{$args} %POWERSHELL_BAT_ARGS%);'+[String]::Join(';',$((Get-Content '%~f0') -notmatch '^^@@'))) & goto :EOF

ls c:
foreach ($arg in $args) {
    Write-Host( $arg )
}</pre>

### Windows Default Shell

#### Bash Subsystem

Siehe [hier](https://digitalfora.blogspot.de/2016/08/enable-windowsoptionalfeature-feature.html "https://digitalfora.blogspot.de/2016/08/enable-windowsoptionalfeature-feature.html")

#### Server Core

Bei Server Core Installationen ist nach dem Login per RDP die Default-Shell die CMD. Läßt sich angelehnt nach [dieser Anleitung](http://www.darkoperator.com/blog/2013/1/10/set-powershell-as-your-default-shell-in-windows-2012-core.html "http://www.darkoperator.com/blog/2013/1/10/set-powershell-as-your-default-shell-in-windows-2012-core.html") auf Powershell abändern:

<pre># Use C# to leverage the Win32API
$definition = @"
using System;
using System.Runtime.InteropServices;  
namespace Win32Api {
    public class NtDll { 
        [DllImport("ntdll.dll", EntryPoint="RtlAdjustPrivilege")] 
        public static extern int RtlAdjustPrivilege(
            ulong Privilege, bool Enable, bool CurrentThread, ref bool Enabled
        );
    }
}
"@

Add-Type -TypeDefinition $definition -PassThru
$bEnabled = $false

# Enable SeTakeOwnershipPrivilege
$res = [Win32Api.NtDll]::RtlAdjustPrivilege(9, $true, $false, [ref]$bEnabled)

# Take ownership of the registry key
$key = [Microsoft.Win32.Registry]::LocalMachine.OpenSubKey('SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\AlternateShells', [Microsoft.Win32.RegistryKeyPermissionCheck]::ReadWriteSubTree,[System.Security.AccessControl.RegistryRights]::takeownership)
$acl = $key.GetAccessControl()
$acl.SetOwner([System.Security.Principal.NTAccount]"Administrators")

# Set Full Control for Administrators
$rule = New-Object System.Security.AccessControl.RegistryAccessRule("Administrators","FullControl", "Allow")
$acl.AddAccessRule($rule)
[void]$key.SetAccessControl($acl)

# Create Registry Value
[void][Microsoft.Win32.Registry]::SetValue($key,"90000",'powershell.exe -noexit -command "& {set-location $env:userprofile; clear-host}"') 
</pre>

### Powershell Konsole

#### Tasta​turkürzel

*   CTRL Rechts, Links: Wortweise
*   CTRL Pos1,Ende: Löschen bis Zeilenanfang/ Ende
*   F8: Anfang eines Befehls tippen + F8: Befehl wird in History gesucht
*   Copy/Paste: Linke Maustaste: Markieren, Rechte Maustaste: Kopieren, Rechte Masutaste: Einfügen

#### Konfiguration des Konsole-Fensters

Befehlszeilenbuffer, Optionen

*   Cursorgrösse: groß
*   Puffergröße auf 999 setzen (“History” für Pfeiltasten, nicht `Get-History`)
*   Anzahl der Puffer: 1 (Tiefe der Pufferung für “Nested Shells”)
*   Quickedit Modus, EinfügeModus aktivieren

Schriftart

*   Schriftart `Consolas 14pt`

​Farben

*   Farbschema hell (“[Monokai](http://www.colourlovers.com/palette/1718713/Monokai "http://www.colourlovers.com/palette/1718713/Monokai")”). Die folgende Tabelle enthät auch Putty Farbewerte, die in der Powershell Konsole nicht verwendet werden.

<table border="1" cellpadding="1" cellspacing="1" style="table-layout: fixed; border-collapse: collapse; border-style: solid; border-width: 1px;">

<thead>

<tr>

<th>Anwendung</th>

<th>RGB</th>

<th>Hex</th>

</tr>

</thead>

<tbody>

<tr>

<td>Fenstertext</td>

<td>

`39 40 34`

</td>

<td>

`#272822`

</td>

</tr>

<tr>

<td>

Fensterhintergrund

</td>

<td>

`248 248 242`

</td>

<td>`#F8F8F2`</td>

</tr>

<tr>

<td>Bold Foreground</td>

<td>`253 151 31 `</td>

<td> </td>

</tr>

<tr>

<td>Bold Background</td>

<td>`248 248 242`</td>

<td>`#F8F8F2`</td>

</tr>

<tr>

<td>Cursor (grün)</td>

<td><font color="#003471" face="Lucida Console, Courier, monospace"><span style="font-size: 10.8px; line-height: 16.2px;">166 226 46</span></font></td>

<td> </td>

</tr>

</tbody>

</table>

#### Alternative Konsolen-Programme

*   Als Alternative zur “normalen” Powershell kann die Powershell ISE verwendet werden. Vorteilhaft ist die Unterstützung von UTF-8 und CTRL-X|C|V, nachteilig ist sind lange Startzeiten und langsames Scrollen bei Textausgaben.
*   Einen guten Mittelweg geht das "ConEMU" Projekt - nach dem Abspecken der Original Installation hat man hier einen kleinen schnellen Terminal-Emulator zur Verfügung, welcher 256 Farben unterstützt. 

#### Verknüpfungen zu Befehlen und Remote Verbindungen

Powershell - Verbindungen zu Remote Servern lassen sich bequem per Verknüpfung ablegen:

*   Beliebigen Ordner öffnen, in welchem die Verküpfung abgelegt werden soll
*   Rechtsklick > Neu > Verknüpfung, dort folgenden Eintrag hinterlegen und anpassen:

<pre>%SystemRoot%\syswow64\WindowsPowerShell\v1.0\powershell.exe -NoProfile -NoExit -Command Enter-PSSession 10.0.0.21 -Credential Administrator -UseSSL -SessionOption (New-PSSessionOption -SkipCACheck -SkipRevocationCheck -SkipCNCheck)</pre>

*   Abschließend die Verknüpfung umbenennen auf z.B. `<User>@remoting.ft.local`
