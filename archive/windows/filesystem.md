# Windows filesystem

## Path mangling

Join path names - more than one member allowed
```
[io.path]::combine(,,,)
```

Combine strings to path
```
$MountPoint = [io.path]::combine($WorkDir, 'mount', $DiskName)
```

## Create dummy files
Create big file filled with random data (no "sparse" files): Download [rdfc](http://www.bertel.de/software/rdfc/rdfc.zip)

```
D:\Install\rdfc.exe D:\Install\Klumpen_100GB.bin 100 GB
```


## Copy files

Robocopy recursive
```
robocopy /MIR /R:1 /W:1 D:\Rollout\MDT\DeploymentShare \\10.0.0.21\d$\Rollout\MDT\DeploymentShare
```

Using BITS - with progress bar

```
Import-Module BitsTransfer
Start-BitsTransfer -Source $Source -Destination $Destination -Description "Backup" -DisplayName "Backup"
```

Copy file buffered - with progress bar

```
function Copy-File {
    param( [string]$from, [string]$to)
    $ffile = [io.file]::OpenRead($from)
    $tofile = [io.file]::OpenWrite($to)
    Write-Progress -Activity "Copying file" -status "$from -> $to" -PercentComplete 0
    try {
        [byte[]]$buff = new-object byte[] 4096
        [int]$total = [int]$count = 0
        do {
            $count = $ffile.Read($buff, 0, $buff.Length)
            $tofile.Write($buff, 0, $count)
            $total += $count
            if ($total % 1mb -eq 0) {
                Write-Progress -Activity "Copying file" -status "$from -> $to" `
                   -PercentComplete ([int]($total/$ffile.Length* 100))
            }
        } while ($count -gt 0)
    }
    finally {
        $ffile.Dispose()
        $tofile.Dispose()
        Write-Progress -Activity "Copying file" -Status "Ready" -Completed
    }
}
```

Test disk speed 
Filesystem independant: 
* hdtune "Benchmark" Read Test. 
    * Standard: reading performance goes down while closing to inner disk spindle part
    * Straight line: Driver problem (hardware or software), not hdd

Flush Disk
```
Write-VolumeCache -Path $Volume.Path
```

## Handling driveletters and mount points

Add any drive letter
```
$Partition | Add-PartitionAccessPath -AssignDriveletter
```

Add given drive letter
```
$OccupiedDriveletters = Get-Volume | select -ExpandProperty Driveletter
if($OccupiedDriveletters -notcontains $NewDriveletter) {
    $Partition | Set-Partition -NewDriveletter $NewDriveletter -EA 'stop'
}
```

Remove drive letter TODO Volume.driveletter or Partition.driveletter???
```
$Partition | Remove-PartitionAccessPath -AccessPath ('{0}:' -f $Partition.Driveletter)
```

Set access path in file system
```
if(Test-Path "$MountPoint") {
    Remove-Item "$MountPoint" -Force
}
$Null = New-Item -ItemType directory "$MountPoint"
$Partition | Add-PartitionAccessPath -AccessPath "$MountPoint" -EA 'stop'
```

Remove access path in file system
```
$Partition | Remove-PartitionAccessPath -DiskId $DataPartition.DiskId $MountPoint -EA 'stop'
```

Clear used access pathes in file system (zombie mounts)

```
if($MountPoint.LinkType -eq 'Junction') {
    Write-Debug('clear-mountpoints(): leaving active junction "{0}" in place' -f $MountPoint.FullName)
}
else {
    Remove-Item -Path $MountPoint.FullName
}
```


## Encryption Truecrypt

Formatieren ohne Rescue CD Check
```
C:\Program Files\TrueCrypt\TrueCrypt Format.exe" /n
```

Truecrypt v7.1 wurde nie geknackt

## Encryption Bitlocker

Bitlocker uses so-called "protectors". Those can be the TPM, the TPM and the PIN together, or a password, or the startup key on USB or diskette, see [this good introduction](https://techstronghold.com/blogs/security/how-to-manage-and-configure-bitlocker-drive-encryption-powershell-and-bitlocker-on-windows-server-2012-r2)

Find pvolume to be encrpyted- as an example this is last volume on usb drive, here
```Powershell
$Partition = Get-Disk | where BusType -eq "USB" | Get-Partition | select -last 1
$BDEVolume = Get-BitlockerVolume | where MountPoint -like ("*Volume{0}*" -f
```

Encrpyt partition
```Powershell
$PlainPassword = 'xxxxx'
$SecureString = ConvertTo-SecureString "$PlainPassword" -AsPlainText -Force
$BDEVolume | Enable-Bitlocker -UsedSpaceOnly -EncryptionMethod XtsAes256 -PasswordProtector -Password $SecureString
```

Add a key file for automatic encrpytion - KeyPath is parent dir for key files

```Powershell
$KeyDir = 'D:\Backup\Test'
Add-BitLockerKeyProtector -RecoveryKeyProtector -RecoveryKeyPath $KeyDir  -mountpoint $BDEVolume.MountPoint
```

Decrpyt Partition by password

```Powershell
$BDEVolume = Get-BitLockerVolume | where KeyProtector
$SecureString = ConvertTo-SecureString "$Password" -AsPlainText -Force
$Null = $BDEVolume | UnLock-Bitlocker -Password $SecureString
```

Decrpyt Partition by stored key file - full path to key file needs to be examined
```Powershell
$KeyDir = 'D:\Backup\Test'
$BDEVolume = Get-BitLockerVolume | where KeyProtector
$Protector = $BDEVolume.KeyProtector | where KeyProtectorType -eq ExternalKey | select -last 1
$KeyFileName = '{0}.BEK' -f ($Protector.KeyProtectorId.trim('}').trim('{'))
$KeyFilePath = Join-Path $KeyDir $KeyFileName
$BDEVolume | Unlock-BitLocker -RecoveryKeyPath $KeyFilePath
}
```


## Path manipulation, globbing

Combine multiple path components to one path:
```
$MountPoint = [io.path]::combine($WorkingDir, 'BDEMount', $DiskName)
```

## Size and Space

Query capacity and free size without filtering in slow powershell pipe

```Powershell
Get-WmiObject -Query 'Select Size,FreeSpace FROM Win32_LogicalDisk WHERE DeviceID="C:"'
```


Recursively determine size of a directory
```Powershell
    $ComFS = New-Object -comobject Scripting.FileSystemObject
    [Long]$ComFS.GetFolder($Path).size
```

Get volume of a given file path

```Powershell
$Volume = Get-Volume -FilePath $TargetPath
$Volume.FileSystemLabel
```



Show free space under path - find mounted volume, return free space
```Powershell
function Get-FreeSpace($Path) {

    # find volume matching path by filtering volume name - take best match
    $Volumes = Get-WMIObject -query "select name,freespace from win32_volume"
    $Matches = foreach($Volume in $Volumes){
        if($Path.startswith($Volume.Name)) {
            $Volume
        }
    }
    # take best match, return free space property
    $Volume = $Matches | sort -Property Name | select -last 1

    return $Matches | sort -Property Name | select -last 1 | select -ExpandProperty FreeSpace
}
```





## Codeschnipsel

#### Festplatten-Füllstände

Festplatten-Füllstände aller Windows Server ermitteln

*   Login auf dem remoting.ft.local, Powershell-Verbindungen zu allen Windows Servern erstellen. Das dauert im ersten Durchlauf 5 Minuten.

<pre>Import-Module Remoting
Import-Module Zabbix
$Cmd = { Get-WMIObject Win32_LogicalDisk -Filter "DriveType=3" }
$Hosts = Find-Zabbix Host -Group "*Windows Server*" -IB
$FormatParams = @(
    @{Label="Host"; Expression={$_.SessionName}; width=30},
    @{Label="Drive"; Expression={$_.DeviceID}; width=10},
    @{Label="Size [GB]"; Expression={$_.Size / 1GB}; Format="0.0"; width=10},
    @{Label="Free [GB]" ; Expression={$_.FreeSpace/1GB} ; Format="0.0" ; width=10},
    @{Label="Free [%]" ; Expression={$_.FreeSpace * 100 /$_.Size}; Format="0" ; width=10}
)
$Hosts | Invoke-PSH -Batch $Cmd | Format-Table $FormatParams
</pre>

*   <span>Um die Ausgabe in eine Excel Tabelle zu bekommen, eignet sich Export-CSV nicht da die Berechnungnen aus `Format-Table` nicht übernommen werden können. Stattdessen sollte die Ausgabe in eine Textdatei umgeleitet werden, damit ändert sich die letzte Zeile auf</span>

<pre>$Hosts | Invoke-PSH -Batch $Cmd | Format-Table $FormatParams > drives.txt</pre>

*   Diese Textdatei `drives.txt` kann nun in Excel importiert werden:
    *   Inhalt in Zwischenablage kopieren
    *   Excel öffnen
    *   Text in 1\. Spalte einfügen
    *   Menü Daten
        *   Text in Spalten konvertieren

#### Pfad-Manipulationen, Globbing

BaseName, DirName, Extension

<pre><span class="pun">[</span><span class="pln">io</span><span class="pun">.</span><span class="pln">path</span><span class="pun">]::</span><span class="typ">GetFileNameWithoutExtension</span><span class="pun">(</span><span class="str">"c:\temp\myfile.txt"</span><span class="pun">) # myfile
[<span class="pun">[</span><span class="pln">io</span><span class="pun">.</span><span class="pln">path</span><span class="pun">]::</span>GetFileName<span>(String)</span>](https://msdn.microsoft.com/de-de/library/system.io.path.getfilename%28v=vs.110%29.aspx)
<span>[<span class="pun">[</span><span class="pln">io</span><span class="pun">.</span><span class="pln">path</span><span class="pun">]::</span>GetDirectoryName<span>(String)</span> ](https://msdn.microsoft.com/de-de/library/system.io.path.getdirectoryname%28v=vs.110%29.aspx)[<span class="pun">[</span><span class="pln">io</span><span class="pun">.</span><span class="pln">path</span><span class="pun">]::</span>GetTempFileName<span>()</span> ](https://msdn.microsoft.com/de-de/library/system.io.path.gettempfilename%28v=vs.110%29.aspx)[<span class="pun">[</span><span class="pln">io</span><span class="pun">.</span><span class="pln">path</span><span class="pun">]::</span>GetTempPath<span>()</span>](https://msdn.microsoft.com/de-de/library/system.io.path.gettemppath%28v=vs.110%29.aspx)</span></span>
</pre>

Globbing: Schleife über alle `SOMLinks.xml` Dateien in Unterverzeichnissen:

<pre>$MarkerFiles = Get-Item $ExportDir\*\SOMLinks.xml
foreach ($GPOExportDirMarker in $MarkerFiles) {
    Write-Verbose('Removing existing export "{0}"' -f $GPOExportDir)
}         
</pre>

#### Navigation

Aktuelles Verzeichnis - wo bin ich?

<pre>Split-Path $MyInvocation.MyCommand.Path</pre>

UNC Pfad erzeugen - manche Programme und NET Klassen arbeiten nicht mit Laufwerksbuchstaben

<pre>$UserDir = "\\$env:COMPUTERNAME\c$\Users\user1"
</pre>

#### Ein- und Ausgabe

[grep -A|B|C](http://linux.die.net/man/1/grep "http://linux.die.net/man/1/grep") : wird per `select-string -Context` erreicht:

<pre>| select-string -pattern "netfx3" -Context 4,4</pre>

CSV Export und Import

*   Eigentlich trivial, per `export-csv` erzeugte CSV-Dateien lassen sich jedoch nicht per Doppelklick in Excel öffnen (falscher Delimiter) und Umlaute werden nicht korrekt angezeigt. Besser:

<pre>ls | Export-Csv -Delimiter ';' -NoTypeInformation -Encoding UTF8 -Path "S:\Systeme\v1\Repository\PSM\zabbix\v1 alpha\Test\enc.csv"
</pre>

*   der Import unter Powershell 2.0 unterstützt kein UTF8, hier müssen eigene Scripte verwendet oder Powershell 3.0+ verwendet werden. Eine Umsetzung befindet sich im PSM Repository unter `S:\Systeme\v1\Repository\PSM\textfiles`.
*   Unter  Powershell 3.0+ funktioniert

<pre>Import-Csv -Delimiter ';' -Encoding UTF8 -Path "S:\Systeme\v1\Repository\PSM\zabbix\v1 alpha\Test\enc.csv"</pre>

#### Dateien anlegen, entfernen

Temp Dir auslesen - hier können Arbeits-Dateien abgelegt werden

<pre>$env:TEMP</pre>

<span style="line-height: 1.5;">Temp File anlegen - d</span><span style="line-height: 1.5;">ie Datei wird sofort erstellt. Unter Windows 7 wird die Datei in </span>`%LocalAppData%`<span style="line-height: 1.5;"> angelegt.</span>

<pre>$TempFile = [System.IO.Path]::GetTempFileName()
...
Remove-Item -Force $TempFile</pre>

Temp Directory anlegen mit festem Namen

<pre>$TempDir = Join-Path -Path ([System.IO.Path]::GetTempPath()) -ChildPath 'Sample_cNtfsPermissionEntry'</pre>

Temp Directory anlegen mit zufälligem Namen

<pre>$TempDir = Join-Path -Path ([System.IO.Path]::GetTempPath()) -ChildPath ([Guid]::NewGuid().Guid)</pre>

Datei in UTF8 konvertieren

    $TempFile = [System.IO.Path]::GetTempFileName()
    [System.Io.File]::ReadAllText($FileName) | Out-File -FilePath "$TempFile" -Encoding Utf8
    mv "$TempFile" "$FileName"

Verknüpfungen anlegen: <span style="line-height: 1.5;">siehe</span> [Unterseite](mks://localhost/Abteilungen/Entwicklung/Executive/Tools/Windows/Powershell/Administration/Dateisystem_und_Dateien/Windows-Verknüpfung_erstellen "Abteilungen/Entwicklung/Executive/Tools/Windows/Powershell/Administration/Dateisystem_und_Dateien/Windows-Verknüpfung_erstellen")

#### Verzeichnisse anlegen, entfernen

<pre>New-Item -path "C:\winpe_x86\mount" -type directory</pre>

#### Netzlaufwerke

Netzlaufwerk verbinden

<pre>$Credential = Get-Credential
$Net = New-Object -ComObject WScript.Network
$RemoteAddress = '172.25.0.101'
$Net.MapNetworkDrive($Null, "\\$RemoteAddress\C$", $False, $Credential.UserName, $Credential.GetNetworkCredential().password)
<span style="font-size: 12px;">explorer "\\$RemoteAddress\C$\Users\Administrator\Documents"</span></pre>

<div><span style="font-size: 12px;">`$IPC` verbinden: </span>`<span style="font-size: 12px;">$Net.MapNetworkDrive($Null, "\\$RemoteAddress", $False ...</span>`</div>

#### Berechtigungen setzen

Spezielle Benutzer und Gruppen:

<pre>$HomeDirOwner = '{0}\{1}' -f ($env:userdomain, $env:username)
$Everyone = (New-Object System.Security.Principal.SecurityIdentifier('S-1-1-0'))
$MachineAccount = "NT AUTHORITY\SYSTEM"
$Administrators = "BUILTIN\Administrators"</pre>

ACL aufbauen und Berechtugungen unter `$PATH` setzen -  <span style="color:#ff8c00;">nicht rekursiv!</span>

<pre>$Allowed = "BUILTIN\Administrators", "NT AUTHORITY\SYSTEM"
$ProtectFromParentInheritance=$True
$KeepInheritedPermissions=$False # ignored in case DisableInheritFromParent=$False
$ACL = Get-ACL $PATH
$ACL.SetAccessRuleProtection($ProtectFromParentInheritance,$KeepInheritedPermissions)
$Null = $ACL.access | foreach {$ACL.RemoveAccessRule($_)}   # clear ACLs
foreach ($Entry in $Allowed) {
    $Permission  = @(
        "$Entry",
        [System.Security.AccessControl.FileSystemRights]"FullControl",
        [System.Security.AccessControl.InheritanceFlags]"ContainerInherit, ObjectInherit",
        [System.Security.AccessControl.PropagationFlags]"InheritOnly",
        [System.Security.AccessControl.AccessControlType]"Allow"       
    )
    $Rule = New-Object System.Security.AccessControl.FileSystemAccessRule $Permission
    $ACL.AddAccessRule($Rule)
}
Set-ACL $PATH $ACL
</pre>

## Alternative IO Bibliotheken

Siehe [Technet-Beitrag](http://social.technet.microsoft.com/wiki/contents/articles/12179.net-powershell-path-too-long-exception-and-a-net-powershell-robocopy-clone.aspx "http://social.technet.microsoft.com/wiki/contents/articles/12179.net-powershell-path-too-long-exception-and-a-net-powershell-robocopy-clone.aspx"): Andere IO-Bibliotheken erlauben die Verwendung langer Datei-Pade unter Powershell sowie schnelleren Zugriff auf das NTFS Dateisystem. Siehe Projekt [Filename too long Powershell](https://jira.fellowtech.de/issues/?jql=text%20~%20%22filename%20too%20long%22 "https://jira.fellowtech.de/issues/?jql=text%20~%20%22filename%20too%20long%22").Hier wird am Beispiel der QuickIO Bibliothek gezeigt, wie das aussehen kann:

*   Download der QuickIO Bibliothek von der [Projektseite](https://quickio.codeplex.com/releases/view/611706 "https://quickio.codeplex.com/releases/view/611706")
*   Verwendung in Powershell:

<pre># Load dll
$ScriptDir = Split-Path $Script:MyInvocation.MyCommand.Path
$DLLPath  = "$ScriptDir\QuickIOLib\NET35\SchwabenCode.QuickIO.dll"
$DLL =[Reflection.Assembly]::LoadWithPartialName($DLLPath)

# Example: get directory size
    [SchwabenCode.QuickIO.QuickIODirectory]::GetStatistics('C:\windows')

# Example: copy file - needs UNC pathes
    $basedir = "\\$env:COMPUTERNAME\c$\Users\xxx\Documents\QuickIO"
    [SchwabenCode.QuickIO.QuickIOFile]::Copy( "$basedir\testfile", "$basedir\testfile2" )

# Example: retrieve help for copy method
    [SchwabenCode.QuickIO.QuickIOFile]::Copy
</pre>


# Permissions

## Berechtigungen

Kombinationen aus "Übernehmen für" und der Checkbox in der GUI vs. Powershell-Flags

<pre style="margin-left: 40px;">[http://camillelemouellic.blog.com/2011/07/22/powershell-security-descriptors-inheritance-and-propagation-flag-possibilities/](http://camillelemouellic.blog.com/2011/07/22/powershell-security-descriptors-inheritance-and-propagation-flag-possibilities/ "http://camillelemouellic.blog.com/2011/07/22/powershell-security-descriptors-inheritance-and-propagation-flag-possibilities/")</pre>

Beschreibung der Einzelberechtigungen

<pre style="margin-left: 40px;">[http://msdn.microsoft.com/de-de/library/system.security.accesscontrol.filesystemrights%28v=vs.110%29.aspx](http://msdn.microsoft.com/de-de/library/system.security.accesscontrol.filesystemrights%28v=vs.110%29.aspx "http://msdn.microsoft.com/de-de/library/system.security.accesscontrol.filesystemrights%28v=vs.110%29.aspx")</pre>

 Rechte

<pre style="margin-left: 40px;">AppendData
ChangePermissions
CreateDirectories
CreateFiles
Delete
DeleteSubdirectoriesAndFiles
ExecuteFile
FullControl
ListDirectory
Modify
Read
ReadAndExecute
ReadAttributes
ReadData
ReadExtendedAttributes
ReadPermissions
Synchronize
TakeOwnership
Traverse
Write
WriteAttributes
WriteData
WriteExtendedAttributes
</pre>

Flags für Inherit

<pre style="margin-left: 40px;">ContainerInherit (the ACE is inherited by child containers, like subfolders in container)
ObjectInherit (the ACE is inherited by child objects, like files in container)
None
</pre>

Flags für Propagation

<pre style="margin-left: 40px;">InheritOnly (the ACE is propagated to all child objects)
NoPropagateInherit (the ACE is not propagated to child objects)
None</pre>

### Write-Only Verzeichnis

![writeonly1.png](/@api/deki/files/1556/=writeonly1.png)![writeonly2.png](/@api/deki/files/1557/=writeonly2.png)
