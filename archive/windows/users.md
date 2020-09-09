# Windows Users, Groups, AD, Kerberos

Copy AD User Account to other user
```
function Copy-ADUser ([String]$OldUserName, [String]$NewUserName, [System.Security.SecureString]$NewPassword) {
    $UserInstance = Get-ADUser -Identity $OldUserName
    $OldUserDN = $UserInstance.DistinguishedName
    $OldUserParentDN = $OldUserDN.split(',')[1..$OldUserDN.split(',').length] -Join ','
    $OldUserDomain = $UserInstance.UserPrincipalName.split('@')[1]
    $NewUserParams = @{
        SamAccountName=  $NewUserName.tolower()
        Name = "$NewUserName"
        Instance = $UserInstance
        Path = $OldUserParentDN
        AccountPassword = $NewPasswordSecureString
        UserPrincipalName = ('{0}@{1}' -f ($NewUserName.tolower(), $UserInstance.UserPrincipalName.split('@')[1]))
        Description = 'some user'
    }
    New-ADUser @NewUserParams   
}
Set-ADAccountPassword $NewUserName -NewPassword (ConvertTo-SecureString -String $NewPassword -AsPlainText -Force)
```



Get domain info via AD Feature
```
Import-Module ActiveDirectory
$Domain = Get-ADDomain -Current LocalComputer
$Domain.DnsRoot  # firma.local
$Domain.Name     # firma
$Domain.DistinguishedName # CN=firma,CN=local
```

AD auslesen: find PDC (no activedirectory module needed:
```
[DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain().PDCRoleOwner.Name
```

AD auslesen: Verwendung von adisearcher, wenn kein Powershell ActiveDirectory Modul verfügbar ist:

```
$ADSearch = [adsisearcher]"displayname=ft-firmenkontakt"
$ADUser = $ADSearch.FindOne()
# [adsisearcher]"" | get-member # find all methods and properties
```

* see for query details http://www.zytrax.com/books/ldap/ape/
* see adsisearcher examples: http://www.jaapbrasser.com/wp-content/uploads/2012/11/Adsisearcher-Examples.txt

Get groups where user is in, recursively
```
$SamAccountName = "Max.Mustermann"
$AccountDN = ([ADSISEARCHER]"samaccountname=$SamAccountName").Findone().Properties.DistinguishedName
$AccountGroups = ([ADSISEARCHER]"member:1.2.840.113556.1.4.1941:=$ADObjectDN").FindAll()
$AccountGroupProps = $AccountGroups | select -ExpandProperty Properties
```



Als Member eigene AD Domain auslesen

```Powershell
$DomainDN = ([ADSI]"LDAP://rootDSE").defaultNamingContext
$Domain = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()
$PDCHost= [Net.DNS]::GetHostEntry( $Domain.PdcRoleOwner.Name )
AD Gruppe leeren: sieht aufwendig aus - für das remoting müssen aber alle Fehler abgefangen werden

$Cmd = {
    $ADGroup = "app-basic-QuickTime"
    try {
        Import-Module ActiveDirectory -EA 'stop'
        try {
            $Members = Get-ADGroupMember "$AdGroup" -EA 'stop'
            if ( $Members) {
                if ($Members.count -gt 0) {
                    'Removing {0} members from group "{1}"' -f ( $Members.count, $ADGroup)
                    $Members | ForEach-Object {Remove-ADGroupMember "$ADGroup" $_ -Confirm:$false -EA 'stop'}
                }
                else {
                    'No Members'
                }
            }
            else {
                'No Members'
            }
        }
        catch {
            '[EE] group "{0}" not found' -f $ADGroup
        }
    }
    catch {
        '[EE] Could not import AD module, check groups manually!'
    }
    '-------------------------------'
}
$h | ip -b $Cmd
```

Anmeldungen von Benutzer aus AD auslesen:

```Powershell
$MSGs = Get-EventLog -LogName Security -InstanceId 4776 | select Message

function convert_syslogmessage($Text) {
 $Lines = $Text -split [environment]::NewLine
 foreach ($Line in $Lines) {
  if ($Line.startswith("Anmeldekonto" ) ) {
   $Account = $Line.split(':')[1].trim()
  }
  if ($Line.startswith("Arbeitsstation" ) ) {
   $Machine = $Line.split(':')[1].trim()
  }
 }

 # filter bad accounts
 if ($Account.endswith('$')) {
  return
 }

 # return powershell object
 New-Object PSObject -Property @{
 Account = $Account
 Machine = $Machine
 }
}

$AccountsMachines = foreach (  $msg in $MSGs ) {
 if ($msg.Message -notlike "*RDS*"){
  convert_syslogmessage($msg.Message)
 }
}

$AccountsMachines | sort
$AccountsMachines | where {$_.Account -like "*gora*"}
Gruppe in bestimmter OU anlegen

$Cmd = {
    try {
        import-module ActiveDirectory
        $path = Get-ADOrganizationalUnit -Filter {Name -like "*Anwendungen*"}
        $Null = new-AdGroup -Name "app-basic-FreePDF" -GroupScope 0 -GroupCategory 1 -Path $path -Description "ft: auf Computern dieser Gruppe wird die Anwendung installiert, Benutzer dieser Gruppe dürfen die Anwendung nutzen"
    }
    catch {
        write-host $Error[0]
    }
}
```

## Credentials und Passwörter


### Storing credentials or passwords in files

This is donw using[DPAPI](https://msdn.microsoft.com/en-us/library/ms995355.aspx) functions - plain and easy. Encrypted strings can be decrpyted from same user on same machine, only.
Alternatively, use windows password vault (Credential locker) - see below


Credential erzeugen und ablegen: Benutzernamen und Passwort sicher in eine CSV-Datei exportieren (ohne Klartext-Passwörter).

```Powershell
$Credential = Get-Credential
$CredentialExport = New-Object PSObject -Property @{
    Domain   = $Credential.UserName.split('\')[0]
    Username = $Credential.UserName.split('\')[1]
    Password = ($Credential.Password | ConvertFrom-SecureString)
}
$CredentialExport | Export-Csv "admin-credential.csv"
```

Credential auslesen: Benutzernamen und Passwort aus CSV-Datei importieren (ohne Klartext-Passwörter)

```Powershell
$CredentialImport = Import-Csv "admin-credential.csv"
$Username = '{0}\{1}' -f ($CredentialImport.Domain, $CredentialImport.Username)
$Password = $CredentialImport.Password | ConvertTo-SecureString
$Credential = New-Object System.Management.Automation.PSCredential -ArgumentList $UserName, $Password
```

Store plain text (e.g. password) in file as encoded string.

```Powershell
$PlainText = 'test'
$Path = 'crypt.txt'
$String = ConvertTo-SecureString "$PlainText" –asplaintext –force | ConvertFrom-SecureString
Set-Content $Path $String
```

Read plain text string (e.g. password) from encoded string in file - works only for same user on same machine as creator
```Powershell
$Path = 'crypt.txt'
$SecureString = Get-Content $Path | ConvertTo-SecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureString)
[System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
```



Dekodieren: Benutzernamen `$UserName` und Klartext-Passwort `$PlainPass`  aus Credential Objekt `$Credential` auslesen

```Powershell
$UserName = $Credential.UserName
$PlainPass = $Credential.GetNetworkCredential().password
```

Kodieren: Credential Objekt aus Benutzernamen `$UserName` und Passwort `$PlainPass` erstellen

```Powershell
return New-Object System.Management.Automation.PSCredential (
    "$UserName",
    ( ConvertTo-SecureString "$PlainPass" -AsPlainText -Force )
)
```

### Storing credentials in windows password vault

This storage is as safe as DPAPI above but the password vault = credential locker
works domain-wide. Accessible only for user that stored the credentials.

See [Powershell "Credman" Impementation](https://gallery.technet.microsoft.com/scriptcenter/PowerShell-Credentials-d44c3cde).

However, there are other techniques you can use, and this was the subject of a talk I gave at this year's PowerShell Summit: https://www.youtube.com/watch?v=Ta2hQHVKauo . The short version is, use certificates to encrypt your passwords, and distribute the certificate (with its private key) to any user who you want to be able to run the script.


## Admin-Rechte
Passwort des lokalen Adminstrator-Accounts neu setzen:

```Powershell
$ComputerName = hostname
$UserName = 'administrator'
$Password ='xxxxxx'

$UserObject = [adsi]('WinNT://{0}/{1}, user' -f ($ComputerName, $UserName) )
$UserObject.psbase.invoke("SetPassword", $Password)
$UserObject.psbase.CommitChanges()
```
Check if current user has elevated privileges

```Powershell
$CurrentIdentity = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent())
if ($CurrentIdentity.IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator") -eq $False) {
    throw('Script needs to run with elevated privileges!')
}   
```

Scriptblock "$Code" mit Admin-Rechten ausführen (per UAC) - nicht als SYSTEM-Benutzer - NICHT GETESTET

```Powershell
function Start-ElevatedCode{
  param([ScriptBlock]$Code)
  Start-Process-FilePath powershell.exe -VerbRunAs -ArgumentList $Code
}​
```

Script als SYSTEM Benutzer ausführen, optional im Hintergrund:

```Powershell
function start-systemcmd([Scriptblock]$CMD, [Switch]$Wait=$True) {
    <#
    Run command as NT AUTHORITY\SYSTEM. Creates a scheduled task calling
    "powershell.exe -command ..." and runs this task immediately.
    Afterwards, this task is removed.

    TODO: Hand over parameters to scriptblock
    #>

    # constants for readability
    $TASK_RUNNING_STATE = 4
    $QUEUED_TASK_RESULT = 267045
    $RUNAS_USER = 'NT AUTHORITY\SYSTEM'

    ## register task
    $TaskHandler = New-Object -ComObject Schedule.Service
    $TaskHandler.connect()
    $TaskDefinition = $TaskHandler.NewTask(0)

    # define task and action
    $TaskDefinition.RegistrationInfo.Description = "Temporary Task"
    $Action = $TaskDefinition.Actions.Create(0)
    $Action.Path = "powershell"
    $Action.Arguments = "-noprofile -nologo -noninteractive -command $CMD"

    # next three lines: task should be deleted right after execution, boubndary values are dummy
    $TaskDefinition.Settings.DeleteExpiredTaskAfter =  "PT0S"  # PT0S== remove task after run
    $Trigger = $TaskDefinition.Triggers.Create(8) # Creates a "At System Startup" trigger
    $Trigger.StartBoundary = [datetime]::Now.AddSeconds(2).ToString('s')
    $Trigger.EndBoundary = [datetime]::Now.AddSeconds(3).ToString('s')

    # register task, start it immediately
    $TaskFolder=$TaskHandler.GetFolder('\')
    $RegisteredTask = $TaskFolder.RegisterTaskDefinition( $Null, $TaskDefinition, 6, $RUNAS_USER, $Null, 1 )
    $Null = $RegisteredTask.Run($Null)

    # wait till task is finished
    if ($Wait -eq $True) {
        # start task immediately and wait till finished
        while (($RegisteredTask.State -eq $TASK_RUNNING_STATE) -or ($RegisteredTask.LastTaskResult -eq $QUEUED_TASK_RESULT)) {
            Start-Sleep -MilliSeconds 100
        }
        return $RegisteredTask.LastTaskResult # return exit code
    }
}
```
Test:

```Powershell
$CMD = {
    sleep 1
    whoami > c:\delme.txt
}
start-systemcmd $CMD -Wait:$True
```


# adsisearcher

# Search for all users in the domain, using PowerShell v1 syntax
$Searcher = New-Object DirectoryServices.DirectorySearcher
$Searcher.Filter = '(objectcategory=user)'
$Searcher.FindAll().Count

# Search for all users in the domain using [adsisearcher] type accelerator, PowerShell v2 syntax
([adsisearcher]'(objectcategory=user)').FindAll().Count

# Search for administrator and display its properties
([adsisearcher]'(samaccountname=administrator)').FindOne()
([adsisearcher]'(samaccountname=administrator)').FindOne().properties

# Display pwdlastset parameter of Administrator
$ADSIAdmin = ([adsisearcher]'(samaccountname=administrator)').FindOne()
$ADSIAdmin.properties.pwdlastset

# [adsisearcher] always returns arrays, to retrieve the correct data index into the array
$ADSIAdmin.properties.pwdlastset.GetType()
$ADSIAdmin.properties.pwdlastset[0].GetType()

# Use the DateTime .NET Class to convert the FileTime to a DateTime object
[DateTime]::FromFileTime($ADSIAdmin.properties.pwdlastset[0])

# Search for a computer account, samaccountname includes dollar sign
([adsisearcher]'(samaccountname=jbdc01)').FindOne()
([adsisearcher]'(samaccountname=jbdc01$)').FindOne()

# Search for all users that do not have homedirectory attribute set
([adsisearcher]'(!homedirectory=*)').FindAll()
([adsisearcher]'(&(objectcategory=user)(!homedirectory=*))').FindAll()
([adsisearcher]'(&(objectcategory=user)(!homedirectory=*))').FindAll().Count

# Update the homedirectory attribute for every user that currently lacks one
([adsisearcher]'(&(objectcategory=user)(!homedirectory=*))').FindAll() |
ForEach-Object {
    $CurrentUser = [adsi]$_.Path
    $CurrentUser.homedirectory = "\\JBDC01\Home\$($CurrentUser.samaccountname)"
    $CurrentUSer.SetInfo()
}

# No users should be returned when we re-run this query
([adsisearcher]'(&(objectcategory=user)(!homedirectory=*))').FindAll().Count

# To view the Homedirectory of a random user this example can be executed
([adsisearcher]'(&(objectcategory=user)(homedirectory=*))').FindAll() |
Get-Random | ForEach-Object {
    "Name: $($_.properties.name)"
    "Home: $($_.properties.homedirectory)"
}

# Displays the homedirectory attribute of the current administrator
[adsi]'LDAP://jbdc01.jb.com/CN=Administrator,CN=Users,DC=jb,DC=com'
([adsi]'LDAP://jbdc01.jb.com/CN=Administrator,CN=Users,DC=jb,DC=com').homedirectory


# Utilize ADSI to read information from the domain
[adsi]''
$Domain = [adsi]'LDAP://DC=jb,DC=com'
$Domain | Select-Object -Property *
$Domain.Properties
$Domain.Properties.minPwdLength
$Domain.Properties.whenCreated
$Domain.Properties.fsMORoleOwner

# Search for all computer objects in the Domain Controllers OU
$Searcher = New-Object DirectoryServices.DirectorySearcher
$Searcher.Filter = '(objectcategory=computer)'
$Searcher.SearchRoot = 'LDAP://OU=Domain Controllers,DC=jb,DC=com'
$Searcher.FindAll()

# Display the homedirectory attribute of the administrator user on all available domain controllers. This can be used to have a detailed look at attributes and to verify they have been correctly replicated
(New-Object adsisearcher([adsi]'LDAP://OU=Domain Controllers,DC=jb,DC=com','(objectcategory=computer)')).FindAll() |
ForEach-Object {
    $HashProp = @{ Server = $_.Properties.dnshostname[0]
                   HomeDir = ([adsi]"LDAP://$($_.properties.dnshostname)/CN=Administrator,CN=Users,DC=jb,DC=com").homedirectory[0]
                   }
    New-Object -TypeName PSCustomObject -Property $HashProp
}

# Create an OU
$Domain = [adsi]'LDAP://DC=jb,DC=com'
$CreateOU = $Domain.Create('OrganizationalUnit','OU=NewOUinRootofDomain')
$CreateOU.SetInfo()

# Create Group in OU
$CurrentOU = [adsi]"LDAP://OU=NewOUinRootofDomain,DC=jb,DC=com"
$CreateGroup = $CurrentOU.Children.Add('CN=HappyUsers', 'Group')
$CreateGroup.CommitChanges()

# Update the samaccount name of the group
$CreateGroup.samaccountname = 'happyusers'
$CreateGroup.CommitChanges()

# Create user
$CreateUser = $CurrentOU.Children.Add('CN=JaapBrasser', 'User')
$CreateUser.CommitChanges()

# Delete user
$NewUser = [adsi]"LDAP://CN=JaapBrasser,OU=NewOUinRootofDomain,DC=jb,DC=com"
$NewUser.DeleteTree()

# Create user
$CreateUser = $CurrentOU.Children.Add('CN=JaapBrasser', 'User')
$CreateUser.CommitChanges()

# Update user attributes
$NewUser = [adsi]"LDAP://CN=JaapBrasser,OU=NewOUinRootofDomain,DC=jb,DC=com"
$NewUser.Put('sAMAccountName','jaapbrasser')
$NewUser.Put('givenname','Jaap')
$NewUser.Put('sn','Brasser')
$NewUser.Put('displayname','Jaap Brasser')
$NewUser.Put('description','Account created using ADSI')
$NewUser.Put('userprincipalname','JaapBrasser@jb.com')
$NewUser.SetInfo()

# Set password and enable account
$NewUser.SetPassword('Secret01')
$NewUser.psbase.InvokeSet('AccountDisabled',$false)
$NewUser.SetInfo()

# Add user to group
$NewGroup = [adsi]"LDAP://CN=HappyUsers,OU=NewOUinRootofDomain,DC=jb,DC=com"
$NewGroup.Add($NewUser.Path)

# Shortened version of adding a user to a group using ADSI
([adsi]'LDAP://CN=TestGroup,CN=Users,DC=jb,DC=com').Add($NewUser.Path)

#Ambiguous Name Resolution this can be used to query LDAP
([adsisearcher]'(anr=jaap*)').FindAll()
([adsisearcher]'(anr=jaap*)').FindAll()[1].properties

# Display the attributes of the jaapbrasser AD account
([adsisearcher]'(samaccountname=jaapbrasser)').FindAll()
([adsisearcher]'(samaccountname=jaapbrasser)').FindOne().Properties.memberof
([adsisearcher]'(samaccountname=jaapbrasser)').FindOne().Properties.memberof[0]
([adsisearcher]'(samaccountname=jaapbrasser)').FindOne().Properties.memberof[1]

# Delete the OU and all of its contents
$CurrentOU.DeleteTree()
