# Networking


## NIC Configuration

strip down nic config for iSCSI operation: Ethernet Adapter > Properties
* enable ipv4 and LLDP only
* IPv4: set IP and netmask only - no dns, !no gateway
* IPv4: Disable "Append parent suffix ..."
* IPv4: Disable "Register ... in DNS"
* IPv4: Disable "Netbios over TCP/IP"
* Configure > Advanced > Property VLAN ID "1003"


## RDG RDS

RDG connection setup
* Allgemein
    * local rds server address (DNS resolvable at rdg server)
    * DOMAIN\Username
* Erweitert 
    * Public address of RDG site
    * yes, ignore for local connections
    * yes, separate gateway auth

## Firewall

Turn Firewall on /off in Powershell

    Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False
    Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True

Turn Firewall on /off via CMD

    netsh advfirewall set allprofiles state off
    netsh advfirewall set allprofiles state on

Set up firewall policy
```
$Enable_HTTPS_Params = @{
    'DisplayName' = "Windows Remote Management (HTTPS-In)"
    'Name' = "Windows Remote Management (HTTPS-In)"
    'Profile' = 'Any'
    'LocalPort' = 5986
    'Protocol' = 'TCP'
}
$Null = New-NetFirewallRule @Enable_HTTPS_Params
```

## Tools

Powershell v2 wget functionality:

```
$url = 'https://github.com/PowerShell/Win32-OpenSSH/releases/latest/'
$request = [System.Net.WebRequest]::Create($url)
$request.AllowAutoRedirect=$false
$response=$request.GetResponse()
$([String]$response.GetResponseHeader("Location")).Replace('tag','download') + '/OpenSSH-Win64.zip'  
```
	
Powershell v5 wget functionality:
```
(new-object Net.WebClient).DownloadFile("http://the.earth.li/~sgtatham/putty/latest/x86/putty.exe", "putty.exe")
```
	
Ping: `Test-Connection` is very slow, faster: .NET:

```
Ping = New-Object System.Net.Networkinformation.ping
Ping.send("141.1.1.1")
```


	
## DHCP

See [DHCP Howto's](mks://localhost/Systeme/v1/10_IT-System_SC/20_Systeme/Rollen_und_Dienste/DHCP/Anleitungen "Systeme/v1/10_IT-System_SC/20_Systeme/Rollen_und_Dienste/DHCP/Anleitungen")

### NIC

Find machine ip (where default gw traffic runs through)

```
$MainInterface = Get-WmiObject Win32_NetworkAdapterConfiguration -filter "IpEnabled = TRUE" | Where DefaultIPGateway
$MainInterface.IPAddress[0]
```

### System Name

Retrieve FQDN
```
[System.Net.Dns]::GetHostByName(($env:computerName)).HostName
```

Set FQDN

```
function Set-PrimaryDnsSuffix { # http://poshcode.org/2958
    param([string]$Suffix)

    # http://msdn.microsoft.com/en-us/library/ms724224(v=vs.85).aspx
    $ComputerNamePhysicalDnsDomain = 6

    Add-Type -TypeDefinition @"
    using System;
    using System.Runtime.InteropServices;

    namespace ComputerSystem {
        public class Identification {
            [DllImport("kernel32.dll", CharSet = CharSet.Auto)]
            static extern bool SetComputerNameEx(int NameType, string lpBuffer);

            public static bool SetPrimaryDnsSuffix(string suffix) {
                try {
                    return SetComputerNameEx($ComputerNamePhysicalDnsDomain, suffix);
                }
                catch (Exception) {
                    return false;
                }
            }
        }
    }
"@

[ComputerSystem.Identification]::SetPrimaryDnsSuffix($Suffix)
}

function Set-DnsFQDN {
    Param(
        [String]$HostName,
        [String]$DnsSuffix = (throw('Specify Dns suffix like <dnsdomain>.<tld>'))
    )
    Rename-Computer -NewName "$HostName" -Force
    Set-PrimaryDnsSuffix = "$DnsSuffix"
}
Set-FQDN -HostName 'hyperv1' -DnsSuffix 'gilching.testv2.fellowtech.com'
```

### SSL

See [Crypt algorithm provider list](https://msdn.microsoft.com/en-us/library/windows/desktop/bb931354(v=vs.85).aspx)


Check if certificate is in store

```
$DnsName = 'test.example.com'
if (Get-ChildItem 'Cert:\LocalMachine\MY' | where Subject -eq "CN=$DnsName") { $True }
```

Powershell v5 strong ECDH encryption, compatibility problems: see [Blog](https://ammarhasayen.com/2015/02/04/sha-2-support-migrate-your-ca-from-csp-to-ksp/ "https://ammarhasayen.com/2015/02/04/sha-2-support-migrate-your-ca-from-csp-to-ksp/")

```
$CreateArgs= @{
    NotAfter = [DateTime]::Now.AddDays(3650)
    KeyExportPolicy = 'Exportable'
    KeyUsage = 'DataEncipherment', 'DigitalSignature'
    CertStoreLocation = 'Cert:\LocalMachine\MY'   # Cert:\CurrentUser\MY
    DnsName = (([System.Net.Dns]::GetHostByName(($env:ComputerName))).HostName), $env:ComputerName, 'localhost'
    HashAlgorithm = 'SHA512' 
    KeyAlgorithm = 'ECDSA_nistP384' # P384 is equivalent to 7680bit RSA keys
}
New-SelfSignedCertificate @CreateArgs
```

Powershell v5, full compatible but weak encryption (for ad servers,  "RSA is the only algorithm supported by legacy CSPs" 

```
$CreateArgs= @{
    NotAfter = [DateTime]::Now.AddDays(3650)
    CertStoreLocation = 'Cert:\LocalMachine\MY'   # Cert:\CurrentUser\MY
    DnsName = (([System.Net.Dns]::GetHostByName(($env:ComputerName))).HostName), $env:ComputerName, 'localhost'
    HashAlgorithm = 'SHA512' 
    KeyAlgorithm = 'RSA' # RSA is the only algorithm supported by legacy CSPs (ADFS Server) 
    KeyLength = 2048
}
New-SelfSignedCertificate @CreateArgs
```


Move certificate to other store (Powershell 5, `Move-Item` does not work because `$cert.PSPath` needs to be adapted)

```
$Cert = Get-ChildItem "$KeyStore" | select -first 1
$SrcStore = Get-Item -Path 'Cert:\LocalMachine\MY'
$SrcStore.open("ReadWrite")
$SrcStore.remove($Cert)
$SrcStore.close()
$DstStore = Get-Item -Path 'Cert:\LocalMachine\Some Other Location'
$DstStore.open("ReadWrite")
$DstStore.add($Cert)
$DstStore.close()
```


Powershell v2: create self-signed "sha1" certicate (store under Certificates(Local Computer) > Personal > Certificates = `CertStoreLocation "Cert:\LocalMachine\WinRMSelfSigned"`)

```
function New-LegacySelfSignedCert{
    Param (
        [string]$KeyLocation = "Cert:\LocalMachine\MY",
        [string]$SubjectName = (([System.Net.Dns]::GetHostByName(($env:computerName))).HostName),
        [int]$ValidDays = 3650,
        [int]$KeyLength = 2048
    )

    # create private key
    $name = New-Object -COM "X509Enrollment.CX500DistinguishedName.1"
    $name.Encode("CN=$SubjectName", 0)

    $key = New-Object -COM "X509Enrollment.CX509PrivateKey.1"
    $key.ProviderName = "Microsoft RSA SChannel Cryptographic Provider"
    $key.KeySpec = 1
    $key.Length = $KeyLength
    # Allow Write NT AUTHORITY\SYSTEM, BUILTIN\Administrators, NT AUTHORITY\NETWORK SERVICE
    $key.SecurityDescriptor = "D:PAI(A;;0xd01f01ff;;;SY)(A;;0xd01f01ff;;;BA)(A;;0x80120089;;;NS)"
    $key.MachineContext = 1
    $key.Create()

    $serverauthoid = New-Object -COM "X509Enrollment.CObjectId.1"
    $serverauthoid.InitializeFromValue("1.3.6.1.5.5.7.3.1")
    $ekuoids = New-Object -COM "X509Enrollment.CObjectIds.1"
    $ekuoids.Add($serverauthoid)
    $ekuext = New-Object -COM "X509Enrollment.CX509ExtensionEnhancedKeyUsage.1"
    $ekuext.InitializeEncode($ekuoids)

    # create the cvs and a self-signed certificate
    $cert = New-Object -COM "X509Enrollment.CX509CertificateRequestCertificate.1"
    $cert.InitializeFromPrivateKey(2, $key, "")
    $cert.Subject = $name
    $cert.Issuer = $cert.Subject
    $cert.NotBefore = (Get-Date).AddDays(-1)
    $cert.NotAfter = $cert.NotBefore.AddDays($ValidDays)
    $cert.X509Extensions.Add($ekuext)
    $cert.Encode()

    # install certificate to key store
    $enrollment = New-Object -COM "X509Enrollment.CX509Enrollment.1"
    $enrollment.InitializeFromRequest($cert)
    $certdata = $enrollment.CreateRequest(0)
    $enrollment.InstallResponse(2, $certdata, 0, "")

    # Return the last installed certificate
    Get-ChildItem "$KeyLocation" | Sort-Object NotBefore -Descending | Select -First 1
}
```

## Time Sync (NTP)

NTP setup in windows domain, single source:
* PDC and network devices sync time with firewall
* clients sync time with PDC

HyperV servers: sync time to PDC, disable wall clock sync for all vms. Vm systems should sync to PDC, directly.

Configure time sync for domain members
```
w32tm /config /update /syncfromflags:manual,domhier /manualpeerlist:"ptbtime1.ptb.de,0x9 ptbtime2.ptb.de,0x9 ptbtime3.ptb.de,0x9 de.pool.ntp.org,0x9" 
stop-service w32time
start-service w32time
```

(Re)sync time: sync needs to run without timeout or error messages. 
```
w32tm /resync
```

Check time server and connectivity
```
mode 150,50
w32tm /stripchart /computer:de.pool.ntp.org /samples:5 /dataonly
```

Check if domain server has NTP enabled... first line of output must be like `*HAS_TIMESRV*` 
```
nltest /SC_QUERY:<domain name> 
```

Reset of NTP setup  - after this, time is synced with CMOS-Clock, again
```
Stop-Service w32time
w32tm /unregister
w32tm /register
Start-Service w32time
```

NTP service

`Start-Service w32tm: (w32time) bla bla cannot be started on computer . bla`:
* get better error message via `net start w32time`
* do not run `cmd /C sc config w32time type= own` - service needs to be of type `shared` as-is
* only solution so far is a reboot. the corresponding process group has all important services as dependency so killing them of is close to reboot, anyway


Domain members: re-connect to pdc in case connection has been dropped (e.g. after changing network connection type)

```
net time \\<PDC-Adresse> /set
w32tm /resync /rediscover
```

Windows clients need some time to take over time setup and sync with PDC, depending on initial drift.

Get sync status and setup
```
w32tm /query /peers 
w32tm /query /configuration
w32tm /query /status 
```

Next command shows source _of last successful sync_, this may be different to actual source configuration
```
w32tm /query /source 
```
