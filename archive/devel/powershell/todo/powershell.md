gpresult /H# Sammlung


http://legacy.python.org/dev/peps/pep-0008/#block-comments Sytle Guide

out-file: formatiert rtf powershell-intern, seh sehr langsam $all = @(‘some text’ * 20) * 1000000 schlecht: $all | out-file $file gut: Set-Content $file -value $all -encoding Unicode

generell: immer eher foreach loops verwenden als pipeline, die ist immer sehr langsam wenn es um eine große Zahl von Chunks geht schlecht: “Hello”| out-null gut : $null = “Hello” # 50x schneller

No Multi Threading, Spawn multiple PS exe’s: Start-Job 1 2 3, Wait-Job => Receiver-Job schlecht: serialisiert daten, no throttling, new process created per task


Kommentarketten

<code>
* Variablen in Kommentaren: Sometimes we need <count> to be less than zero.
Readme.txt, Script Hilfetext und Header in deutsch, Skripting (Funktionen, Kommentare, VariablenNamen) in englisch
* Generelle Funktionen in Module auslagern (Ablage: \\sbserver\Technik\Entwicklung\Tools)
* Nur User Skripte  benutzen Logging und Config Files, Daten aus Config Files können an Modulfunktionen übergeben werden
* Funktionen in Modulen sollten nur Daten bearbeiten (PipeIn / PipeOut) ohne UI und ohne kundenspezifische Konfiguration. Fehler werden als Exceptions an das aufrufende Skript zurückgegeben, wo dann die Fehlerausgabe statfindet.
* ini Dateien: als Textdateien verfassen oder als .ps1/.php Dateien wenn Konfigurationsdateien nur von Entwicklern benutzt werden
ini-Dateien sind auch von Nicht-Programmierern handhabbar

Werte von ini Dateien können in eine Variable eingelesen werden, dot-sourcing von Skriptdateien importiert Variablen direkt in den Namespace des aufrufenden Skriptes

* ausführbare config-files verleiten zum "schlampern"


* Variablen Test: immer bei import durchführen (an oberster Stelle), da Variablen später an verschiedenen Stellen im code genutzt werden können
* System Befehle: Optionen ausschreiben, Lang-Versionen verwenden wo möglich, Beispiel
if ! grep  --word-regexp --quiet -- "$PERCONA_MIRROR" /etc/apt/source.list; then
    echo "deb PERCONA_MIRROR $DISTRIBUTION main" >> /etc/apt/source.list
fi
Checkliste:
Logging
Exceptions, unset variables
Check: läuft prozess noch/schon
User Privilegien: Downgrade wo möglich




String mit Variablen - umgeht eine Menge Problem und ist klar lesbar
        $Comment    = 'Rsync started from {0}\{1}@{2}, {3}' -f (
            $env:userdomain,
            $env:username,
            $env:userdnsdomain.tolower(),
            (get-date -uFormat '%Y-%m-%d %H:%M:%S' )
        )






Einzah, Mehrzahl Arrays/Variablen
Kommentare: Auszeichnung von Variablen $JJKJK
Groß/KLeinschreibung
	CamelCase
	Funktionen: Verb-Noun für Funktionen bzw. Cmdlets (Get-Help) sowie Methoden und Eigenschaften
   Ziel: Human Readable
$ExampleHash.GetEnumerator()
$Array.Length

Funktionen: immer Einzahl bei Nouns, z.B. Get-Job
Immerm Mehrzahl für Array Parameter
Einzahl für Pipe Parameter



Kommentare
                    # Take care of finished jobs
                    if ($Job.State -eq 'Completed') {
                        Write-Debug('Receiving and removing job "{0}"' -f $Job.Name)
                        $Jobs.Started.Remove($Job)
                        $BucketJobs.Add($Job)
                    }
                    # Take care of timed-out jobs
                    else {


                    }


in jeder funtion
Set-StrictMode -version 2.0 einfügen

Modulweite Variablen ändern (Getestet: innerhalb einer psm Datei)
Fuktioniert ohne komplizierteres [REF]

BEGIN {
    $Script:Var1 = "ok"
    Start-Example
}
END {
    $Var1
}
function Start-Example() {
    $Script:Var1 = "fine"
}

# gibt "fine" aus



Arrays anlegen
$array1 = @() # collection, hier können keine Werte per Add() oder Remove() geändert werden
        # was funktioniert ist $array1 += "lala", dabei wird eine Kopie des Arrays angelegt.
        # ineffizient und erlaubt immer noch kein remove()

besser:
$array2 = [System.Collections.ArrayList]@()
$Index = $array2.Add('lala')
$array2.Remove('lala')


Hashes, Arrays werden als einzelvariablen (Referenzen) übergeben. D.h.
$Hash2 = $Hash1
$Hash2.key1 = 'll' verändert $Hash1 !

Trennung: $Hash2 = $Has1.Clone()



function Is-IP ([String]$IpAddress) {
    # see http://www.orcsweb.com/blog/james/powershell-stuff-validating-an-ip-address-revisited/
    $ipObj = [System.Net.IPAddress]::parse($ipAddress)
    return [System.Net.IPAddress]::tryparse([string]$ipAddress, [ref]$ipObj)
}

# wait for single key press
    Write-Host -NoNewLine "Press any key to continue..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

function Is-Elevated(){
    # true if script is running in elevated environment
    $Private:UserIdentity  = [Security.Principal.WindowsIdentity]::GetCurrent()
    $Private:UserPrincipal = [Security.Principal.WindowsPrincipal]$UserIdentity
    $Private:AdminRole = [Security.Principal.WindowsBuiltInRole]'Administrator'
    return $UserPrincipal.IsInRole( $AdminRole )
}

Credenital Dialog Parameter Definition
param(
    [Parameter(Mandatory = $True)]
    [ValidateNotNull()]
    [System.Management.Automation.PSCredential]
    [System.Management.Automation.Credential()]
    $Credential = [System.Management.Automation.PSCredential]::Empty
)



jeweisl eine gute Methode von vielen Möglichkeiten

# powershell create directory if not exists
New-Item -type Directory -force $SSH_DIR

# schreibe UTF-8 INhalt in Datei
Set-Content "$SSH_CONFIG_FILE" $ssh_config  


DESIGN GUIDE
Wo möglich, parallel arbeiten lassen (runspaces)
Pipe für Arbeitsdaten nutzen, Remote Session Objekte als -Session Parameter/Array übergeben
Alle Variablen welche in Begin{} festgelegt und in Process{} oder End{} verwendet werden, in Grossbuchstaben "$BEISPIEL_VAR" schreiben
MODULE
Sammlungen von Funktionen und Daten zur Verwendung in Skripten

zulässige Ausgaben: Debug, Warning, Error, Exceptions (throw), keine Write-Host oder Write-Verbose
SCRIPTE
zulässige Meldungen: Debug, Verbose, Write-Host, Error, Exceptions





XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
Powershell Good Practice
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

TODO
Apple Design Guide => schnelle response
Style Guide einarbeiten (script formating)
Skript, Modul template
http://msdn.microsoft.com/en-us/library/ms714428(v=vs.85).aspx
howto texte
schreibe code so als ob der als nächster dranarbeitet ein gewalttätiger Psychopat ist der weis wo Du wohnst

Gerichtet an:
Produktivbetrieb: Sicherheit der Anwendung, Deutlichmachne von Fehlern, Perofrmance im verteilten Betrieb

Logging
Profile
Piping
Performance
Multithreading
External commands
Error handling
Snippets
Formatierungen


Wichtig: im Normalbetrieb keine Augaben ausser Warnungen und Fehler, Fortschrittsanzeigen (Text) sind  nach 2-3 maligen Ausfüher ovn Scripten langweiulig und dafür gib es -verbose parameter
=> keine Ausgaben von scripts, anfängerfehler rot und blau
=> wichtige Ausgaben loggen
=> Fortschritt per "Verbose" Anzeigen, Datenbearbeitung im einzlenen selbst per "Debug". Grund: Ruft ein Script 10 andere
auf kommen eine Menge Meldungen zusammen, die aus der Perspektive des übergeordeneten Scripts nicht wirklcih wichtig sein müssen.
Fehlermesldungen sind immer wichtig und sollten  nicht untergehen
Debug: Fehler im Script, Feherlsuche
Verbose: Fortschrittsanzeige: Texausgabe
Progress: Fortschrittsanzeige


Ausnahmen: text der für den Benutzer gedadcht ist per write-host ausgeben (z.B. ausgelesene Informationen)

Skripte:
Rufen Module auf
Haben Logging

Modulablage:
 ExportFunktionen: immer advanced functions (cmdlet)(gelisted in exports.ps1), der rest: einfache funktionen
 Module export functions: Verbosity Settings importieren, falls nicht gesetzt
 Export functions: in jeder ps1 Datei darf nur eine advanced function drin sein, die ps1 Datei trägt den gleichen Namen wie die exporttiete funktion (Anfangsbuchstaben groß Verb-Noun)
 andere funktionen können in eigenen .ps1 Dateien liegen, deren namen sind einzelne Begriffe in KLeinbuchstaben (z.B. "permissions.ps1", "exports.ps1"). funktionen, die in mehreren ExportFunktionen benutzt werden müssen ausgelagert werden

 permissions enthält funktionen read-permissions create-permissiondata => Noun fängt immer mit ps1 Namen an

* Kommentare über Blöcken: Ziel des Blocks angeben, nicht wiederholen was codiert wurde
 ..wedwd and ... wedwd or ...   

* Kommentare neben Funktionen: kurze Hinweise zum Code, warum das so geschrieben wurde oder Erklärung
[Beispiel] regexp Erklärungen im Block

* Einrückung {
}
* exception falls parameter nicht gesetz
* Module und Skripte:(exportierte) Hautpfunktionen immer als "Advanced function" schreiben,
  Hilfsfunktionen (zur Kapselung von Code) als normale Funktionen ohne CmdletBinding(). Vorteil: Verbose/debug settings etc.
  weclhe in der Hauptfunktion gesetzt werden, bleiben erhalten.  Hilef texte bleiben abrufbar, es macht also sinn ordentliche Hilfeetxte zu verfassen
 arguemnts: throw ArgumentException



StandardParameter
* PassThru: Gibt das neue oder geänderte Objekt zurück. Standardmäßig (d. h. wenn "-PassThru" nicht angegeben wird) wird vo
n diesem Cmdlet keine Ausgabe generiert.
* Path



        write-host ">>> MARKER1"
  write-host
        write-host ">>> MARKER2"
  write-host
        write-host ">>> MARKER3"
  write-host
        write-host ">>> MARKER4"
  write-host
        write-host ">>> MARKER5"


Powershell NTP GPO:
http://www.jhouseconsulting.com/2014/01/10/script-to-create-group-policy-objects-and-wmi-filters-to-manage-the-time-server-hierarchy-1153



temporäres verzeichnis:
[IO.Path]::GetTempFileName()



foreach, do .. while einschränken

MARK_CONSTANTS from begin()
Parameterübergabe: [] voranstellen - lesbarkeit, sicherheit, wenig aufwand

Erst Ziele finden: INhaltsverzeichnis und hilfe schreiben (team), dann vollprogrammieren
festlege: sofort umsetzbar/ TODO



PROFILE
# Powershell Profile
test-path $profile  # check if profile file exists
mkdir $( split-path $profile )

# Profiles
$Profile.AllUsersAllHosts
$Profile.AllUsersCurrentHost
$Profile.CurrentUserAllHosts
$Profile.CurrentUserCurrentHost

.\vim.exe -u $env:appdata\gVimPortable\Data\Settings\vimfiles\vimrc
copy-paste
"*y
"*p
set runtimepath+=/path/to/vimfiles



Funktionsnamen
verb-subtantiv, subtativ: Einzahl (ohne "s") am Ende

case sensitive/insensitive comparison: -ceq/ -eq = -ieq  -clike /-like = -ilike
-notlike -cnotlike

always use += -= *= /=


test object type

"hhh" -is [String]
23.4 -is [int]

size multipliers kb/mb/gb/tb/pb

Powershell colors:
255 255 236    0 0 0 0

 powershell get powershellversion
if($PSVersionTable.PSVersion.Major -lt 2) {
    Write-Warning "posh-git requires PowerShell 2.0 or better; you have version $($Host.Version)."
    return
}

get file encoding
function Get-FileEncoding($Path) {
    $bytes = [byte[]](Get-Content $Path -Encoding byte -ReadCount 4 -TotalCount 4)

    if(!$bytes) { return 'utf8' }

    switch -regex ('{0:x2}{1:x2}{2:x2}{3:x2}' -f $bytes[0],$bytes[1],$bytes[2],$bytes[3]) {
        '^efbbbf'   { return 'utf8' }
        '^2b2f76'   { return 'utf7' }
        '^fffe'     { return 'unicode' }
        '^feff'     { return 'bigendianunicode' }
        '^0000feff' { return 'utf32' }
        default     { return 'ascii' }
    }
}



Performance:

read file not line-wise but in one chunk:

$text = Get-Content $file -ReadCount 0
foreach ($line in $text) {...}

out-file: formatiert rtf powershell-intern, seh sehr langsam
$all = @('some text' * 20) * 1000000
schlecht: $all | out-file $file
gut: Set-Content $file -value $all -encoding Unicode

generell: immer eher foreach loops verwenden als pipeline, die  ist immer sehr langsam  wenn es um eine große Zahl von Chunks geht
schlecht: "Hello"| out-null
gut     : $null = "Hello"   # 50x schneller


No Multi Threading, Spawn multiple PS exe's:
 Start-Job 1 2 3, Wait-Job => Receiver-Job
 schlecht: serialisiert daten, no throttling, new process created per task

 => gut zu verwenden wenn keine daten zurückgesendet werden bzw. lässt sich verbessern der umfang der zurückzusendenden daten minimiret wird

Real Multithreading mit Runspace Pools
    Process Throttle, no data serialisation

 $throttlelimit = 10
 $iss = initialsessionstate
 $pool = [runspacefactor]
 $Pool.open()
www.powershell.com
script library/misc
demofiles_multithreading

 $code = {}
 $newpowershell = [Powershell]::Create().AddScript($code)
 $handle = $newpowershell.begininvoke() # ! whichtig begininvoke not invoke





F7: Befehlshistory
F8: zeigt nicht einfach den zuletzt eingegebenen Befehl, sondern berücksichtigt die schon eingegebenen Zeichen
TAB: funkioniert auch für Commandlets und Parameter
STRG Left/Right: Wortweise
STRG Ende: Zeile ab Cursor bis Ende löschen
STRG Pos1: Zeile ab Cursor bis Anfang löschen

PS> echo "dir1" "dir2" > dirs
PS> foreach ($a in cat dirs) {mkdir $a}

# loop over dictionary items
foreach( $item in $w.'AD Servers'.GetEnumerator() ) {$item.value}
$w.'AD Servers'.GetEnumerator() | ForEach-Object { $_.value }

$myHereString = @'
some text with "quotes" and variable names $printthis
some more text
'@

Eigener ErrorRecord:
        # --------------------------------------------------------------------
  # Create an ErrorRecord  object to be thrown an caller (for obtaining position info )
        # --------------------------------------------------------------------
  $exception = New-Object InvalidOperationException "Dummy"                              
  $errorCategory = [Management.Automation.ErrorCategory]::InvalidOperation
  $DummyErrorRecord = New-Object Management.Automation.ErrorRecord $exception, 'Dummy', $errorCategory, 'Dummy'


# get error categories
[System.Management.Automation.ErrorCategory].getmembers() | where-object { $_.IsStatic } | foreach{ $_.Name } | foreach { [System.Management.Automation.ErrorCategory]::$_.value__ }



Use Write-Output + Write-Verbose, not Write-Host (which breaks Automation)


powershell templates
cmdlet  + module
simple function
script



# write background cmdlet
Define an asJob switch parameter so that the user can decide whether to run the cmdlet as a background job.
Create an object that derives from the Job class. This object can be a custom job object or a job object provided by Windows PowerShell, such as a PSEventJob object.
In a record processing method, add an if statement that detects whether the cmdlet should run as a background job.
For custom job objects, implement the job class.
Return the appropriate objects, depending on whether the cmdlet is run as a background job.




* Re-run input parameter check, catch this exception
 (found exception full name via



 BEGIN {
  # handle input parameters
  # set $Path, value assigned here runs through param() check above
  $DefaultConfigDir =  Join-Path "$BestVersionDir" 'config'
  try {
   if ( -not $Path) {$Path = $DefaultConfigDir }
  }
  Catch [System.Management.Automation.ValidationMetadataException]{
   throw( "Could not find default config dir ""$DefaultConfigDir""")
  }


$info.Target = try {Split-Path $info.TargetPath -Leaf } catch { 'n/a'}

@echo off
shutdown /t 0 /s /f

# DNS-Suffix der AD-Domäne ermitteln
$dnsroot = '@' + (Get-ADDomain).dnsroot   

* find duplicates in hashes
    $Private:Duplicates = $ParentConfig.keys | where {$NewConfig.ContainsKey($_)}
    write-Debug( 'Overriding old value(s) "{0}" ' -f ($Duplicates -join ', ')  )

* netlogon pfad ausgeben lassen

get-wmiobject -class win32_share | where {$_.Name -like 'netlogon'} | foreach{$_.Path}



TOOLS
Verzeichnis rekursiv alle Ordner angeben
Get-ChildItem -recurse | Foreach{ if ( $_.PsIsContainer) { $_.FullName }  }
fl = format-List
test-path # check if file exists
mkdir $( split-path $profile )

GPO
gpupdate /force /target:computer


Datum abrufen
Get-PSSession | foreach {Invoke-Command -Session $_ -ScriptBlock { '{0,-35}: {1}' -f (("$env:computername.$env:userdnsdomain").tolower(), (date)) } }



1. Einrichtung der lokalen Konsole
get-service winrm  # muss auf "Running" stehen
Enable-PSRemoting –force
set-item wsman:localhost\client\trustedhosts "192.168.*,10.*,172.*"

2. Interaktive Verbindung (remote Session)
enter-pssession  192.168.1.8 -credential Administrator
enter-pssession  10.0.128.25 -credential ServerAdmin
...
exit

3. Befehl remote ausführen
Peer enable: enable-psremoting -force

invoke-command -computername <IP> { <CMD> }

Passwörter speichern
By default, only the same user account (and on the same computer) is able to decrypt the protected data.
siehe
* http://geekswithblogs.net/Lance/archive/2007/02/16/106518.aspx
* http://powershell.org/wp/2013/11/24/saving-passwords-and-preventing-other-processes-from-decrypting-them/comment-page-1/

$user = "Administrator"
$addr = "10.0.128.25"
$password_file = "$user@$addr.passwd"

$pass_enc = Read-Host -AsSecureString "Enter a password" | convertfrom-securestring | out-file "$password_file"
# $passwordfile now contains encrypted password hash
$secure_string = cat "$password_file" | convertto-securestring
$cred = new-object -typename System.Management.Automation.PSCredential -argumentlist $user,$secure_string

Test:
enter-pssession $addr -credential $cred




Service Start Stop
http://blogs.technet.com/b/heyscriptingguy/archive/2014/04/04/build-a-tool-that-uses-constrained-powershell-endpoint.aspx

Netzwlaufwerk verbinden, mount
$User = 'Gunnar.Mann'
$Cred = Get-Credential -Credential $User
#$Cred = Get-Credential
#$User = $Cred.UserName.SubString(1)
net use \\sbserver\Technik $Cred.GetNetworkCredential().Password /user:$User
# !! wenn hier Systemfehler 1320 o.ä. auftritt, ist \\sbserver im Windows Cache
# verkrampft, Rechner neustarten
ls \\sbserver\Technik




cat dirs | ForEach{mkdir $_} # xargs
'why:me'.split(':')[0] # echo "why:me" | cut -d ':' -f1
'why/not'.Replace('/', '\')
$host.ui.rawui
$host.ui.rawui.ForegroundColor = "Yellow"
$host.ui.rawui.WindowTitle = "Meine Konsole"

get-date -uFormat "%Y-%m-%d %H:%M:%S"
fqdn: "$env:computername.$env:userdnsdomain".tolower()







Own Comandlets
nur lokale Skripte:
set-executionpolicy RemoteSigned -Force
Skripte aufd Netzlaufwerken
set-executionpolicy bypass


get Caller variable in module Scope
   $CallerPref = $Config.Cmdlet.SessionState.PSVariable.Get('VerbosePreference')
   Set-Variable -Scope 1 -Name $CallerPref.Name -Value $CallerPref.Value -Force    
   # or
   $CallerPref.VerbosePreference

# usernaem @ fqdn
  $CurrentUser = '{0}\{1}@{2}.{3}' -f (
  :w $env:userdomain, $env:username, $env:computername, $env:userdnsdomain
  ).tolower()


# piping
"hghg", "jhjh" | script.ps1
wird bei ValueFromPipeline=$True in jede  PROCESS{} Schleife einzeln übergeben

script.ps1 -HostName "ghgh", "jhjh" wird als array an jede PROCESS{} Schleife übergeben und muss dort per
    foreach ($HostName in $HostNames) {       
  write-Host $HostName
  write-Host "---"
 }


performance:
 Invoke-Command -Session (Get-PSSession) -ScriptBlock { ls c:\ }
 NICHT (langsam): foreach  $Session in Get-PSSession) {Invoke-Command -Session $Session -ScriptBlock { ls c:\ } }
 NICHT (langsam): Get-PSSession | foreach { Invoke-Command -Session $_ -ScriptBlock { ls c:\ } }
=> soviel wie möglich mit arrays als übergabeparameter arbeiten, ist wesentlich schneller als eine Pipe


Read file in script dir:
# Get list of Servers from config file
$ScriptDir = Split-Path $script:MyInvocation.MyCommand.Path
$Servers   = Read-Config (Join-Path $ScriptDir 'example.ini')


  # Copy preference settings from caller script
  if ( -not $PSBoundParameters.ContainsKey('Verbose') ) {
   Set-Variable -Force 'VerbosePreference' $PSCmdlet.GetVariableValue('VerbosePreference')
  }
  if ( -not $PSBoundParameters.ContainsKey('Debug'  ) ) {
   Set-Variable -Force 'DebugPreference'   $PSCmdlet.GetVariableValue('DebugPreference')
  }
  $ErrorActionPreference = 'Stop'
  if ($DebugPreference -eq 'Inquire') {$DebugPreference = 'Continue'}



==============================================================================  
Windows Links
==============================================================================
Alternatively you can create symbolic links with the mklink and junction tools.  

==============================================================================
Gruppenrichtlinie importieren
==============================================================================

cmd als Adminstrator ausführen
gpmc.msc

Gruppenrichtlinienobjekte links click, rechtsclick
neue REichtlinie
ft-Computer und Server (Basiseinstellungen)
Einstellungen importieren
Bearbeiten > Einstellungen > Systemsteuerung > Lokale Benutzer
  FTCloud entfernen, hinzufügen > ... > DOM\Domänen-Admins

Auf Gruppenrichtlinienobjekte licken, rechts auswählem, auf hwa.local ziehen = mit Domäne verknüpfen

Aktualisieren:
gpupdate /force /Target:Computer && gpresult /r


Powershell FunktionsParameter:
https://www.simple-talk.com/dotnet/.net-tools/down-the-rabbit-hole--a-study-in-powershell-pipelines,-functions,-and-parameters/

Exceptions
catch{
 $_.Exception.GetType().FullName
}


try catch else
try{
 ...
 $Found = $True
}
catch{
 ...
}
if ($Found) {
 # else
 ...
}

Scriptblock

a) $SB = { ... }
b) $SB = [scriptblock]::Create("...")
c) $SB = {
 param()
 BEGIN()
 PROCESS()
 END()
}

$result = & {...}

Array per Referenz übergeben

function ja([Ref]$TestArray) {
 $TestArray.Value += "hallo"
}

ja [Ref]$TestArray





# über Hash iterieren
  foreach ($Server in $NewServers.GetEnumerator()) {

  }


performance:
Invoke-Command -Session (Get-PSSession) -ScriptBlock { ls c:\ }
NICHT (langsam): foreach  $Session in Get-PSSession) {Invoke-Command -Session $Session -ScriptBlock { ls c:\ } }
NICHT (langsam): Get-PSSession | foreach { Invoke-Command -Session $_ -ScriptBlock { ls c:\ } }


Variablentypen

[Int]
[Array]
[HashTable]
[String]
[System.Management.Automation.Runspaces.PSSession]
[System.Management.Automation.ScriptBlock]
[Ref]






Exceptions


Parameter
-PassThru erst wenn dieser Switch  speizifizerit ist, Werte ausgeben - sonst überschütten die Daten den Bildschirm und
Warnungen und Fehler gehen verloren

</code>
