# HyperV 2016+


## VM management

Wait until VM is started (network ping ok):
```
# obtain vm ip address (windows)
$NIC = $VM.NetworkAdapters | where IPAddresses | select -first 1
$Address = $NIC.IPAddresses[0]

# wait for successful ping
$Pinger = New-Object System.Net.Networkinformation.ping

while ($True) {
    Write-Debug('Trying to ping address "{0}"' -f $Address)
    $Response = $Pinger.send($Address)
    if ($Response.Status -eq 'Success') {
        break        
    }
    else {
        Write-Debug( 'Could not reach host "{0}", waiting before retry' -f $Address)
        sleep $PING_DELAY
    }
}
```




## VHDx access problems

In case hyperv complains about other process locking some VHDx drive, removing and re-insterting the drives to the virtual machine  helps. The error message is misleading.

### HyperV

Powershell Befehle direkt in virtueller Maschine laufen lassen: [Powershell Direct](https://blogs.technet.microsoft.com/virtualization/2015/05/14/powershell-direct-running-powershell-inside-a-virtual-machine-from-the-hyper-v-host "https://blogs.technet.microsoft.com/virtualization/2015/05/14/powershell-direct-running-powershell-inside-a-virtual-machine-from-the-hyper-v-host")

*   There are no network/firewall requirements or configurations.
*   It works regardless of Remote Management configuration.
*   HyperV and Virtual Machines need to be Windows 10/ Server 2016
*   You need to be running as Hyper-V Administrator

[KVP](https://technet.microsoft.com/en-us/library/dn798287(v=ws.11).aspx "https://technet.microsoft.com/en-us/library/dn798287(v=ws.11).aspx") Abfrage von VM OS Parametern (IP, Hostname) - eine Liste verfügbarer Properties: [hier](https://msdn.microsoft.com/en-us/library/cc136850(v=vs.85).aspx "https://msdn.microsoft.com/en-us/library/cc136850(v=vs.85).aspx")

<pre>$vmName = "dc1tmrelo"
$Property = "FullyQualifiedDomainName"

$vm = Get-WmiObject -Namespace root\virtualization\v2 -Class Msvm_ComputerSystem -Filter "ElementName='$vmName'"

$KVPItems = $vm.GetRelated("Msvm_KvpExchangeComponent").GuestIntrinsicExchangeItems
foreach ($KVPItem in $KVPItems) {
    $GuestExchangeItemXml = ([XML]$KVPItem).SelectSingleNode(
        "/INSTANCE/PROPERTY[@NAME='Name']/VALUE[child::text()='$Property']"
    )
    if ($GuestExchangeItemXml -ne $null) {
        $Prop = $GuestExchangeItemXml.SelectSingleNode(
            "/INSTANCE/PROPERTY[@NAME='Data']/VALUE/child::text()"
        )
        $Prop.Value
    }
}
</pre>


## Migration V2 VM > V1 VM (Linux VM)

1. Export VM on HyperV 2016
2. Copy VHDx files from exported VM, convert to VHD file
```Powershell
Convert-VHD xxx.vhdx xxx.vhd
Remove-Item xxx.vhdx
```
3. Create new virtual VM
    * Type Generation 1
    * Start Medium: some rescue CD (Debian-based - e.g. [GRML](https://grml.org))
4. Edit VM:
    * add `root.vhd` and `data.vhd`
    * adjust VLAN, virtual processors, integration services, start and stop action
5. Boot rescue CD
6. Enable networking
7. Mount root drive to `/mnt`, enable networking (and ssh into rescue system)
```bash
fdisk -l # find root drive
mount /dev/sda2 /mnt
cp /mnt/etc/network/interfaces /etc/networking
/etc/init.d/networking restart
```
8. Prepare chroot system for adapting grub
```bash
mount -o rbind /dev  /mnt/dev
mount -t sysfs /sys  /mnt/sys
mount -t proc  /proc /mnt/proc
mount -o bind  /run  /mnt/run
cp /proc/mounts      /mnt/etc/mtab
```
9. Replace EFI grub by standard grub
```bash
chroot /mnt
apt-get remove grub-efi-amd64
apt-get install grub2  # ignore error when installing boot loader
grub-install /dev/sda --force
update-grub
exit
systemctl poweroff
```
10. Configure VM: remove virtual CD, adjust bios

# Powershell direct

https://blogs.technet.microsoft.com/virtualization/2015/05/14/powershell-direct-running-powershell-inside-a-virtual-machine-from-the-hyper-v-host/


# VSS Production snapshots

## HyperV 2016 Backup of Windows VM

Hint: as of now, `get-vmsnapshot` does not show if a snapshot is `production` or `standard`. Thus, some tests are shown to proove if snapshot vss action took place.

## Preparation
### HyperV VM configuration
* VSS integration service must be running
* Checkpoint config: Production snapshot, only. Standard disabled completely (in order to get proper error handling in case there is a problem with VSS in VM

After enabling vss support in VM, reboot of VM is needed
```
$VM = Get-VM -Name MyVM
$VM| Enable-VMIntegrationService -Name 'VSS'                    
$VM| Set-VM -CheckpointType 'ProductionOnly'
```

### VM configuration(inside)
Integration services must be installed, `Hyper-V Volume Shadow Copy Requestor` service running
```
Get-Service vmicvss
```   

## Test

Disable VSS Requestor in VM:

```
stop-service vmicvss
```

Try to create a snapshot at HyperV:

```
$VM = Get-VM -Name MyVM
$VM | Checkpoint-VM -Snapshotname test-prod
```

Results in error like

```
Checkpoint-VM : Checkpoint operation failed.
Production checkpoints cannot be created.
```

Enable vss again in VM
```   
start-service vmicvss
```

taking snapshot on HyperV should be successfull

```
$VM = Get-VM -Name MyVM
$VM | Checkpoint-VM -Snapshotname test-prod
```

## Create Backup on HyperV

```
$VM = Get-VM -Name MyVM
$SnapShotName = 'USBBackup-{0}' -f $VM.Name
Checkpoint-VM $VM -SnapshotName $SnapShotName               # create vss snapshot
Export-VMSnapshot $VM -Name $SnapShotName -Path D:\Export   # export frozen vm state
$VM | Get-VMSnapshot -Name $SnapShotName | Remove-VMSnapshot # remove snapshot
```

# KVP

Ein einfacher key.-value exchange mit laufenden Servern: http://windowsitpro.com/hyper-v/get-values-hyper-v-host-about-virtual-machine-kvp


Read KVP from Windows guest - write keys ans values to `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Virtual Machine\Guest` there and read from hyperv like:

```Powershell
$VM='myvm'

# get vm wmi object
$QueryParam = @{
    NameSpace = 'root\virtualization\v2'
    Class = 'MSVM_ComputerSystem'
    Filter = ("ElementName='{0}'" -f $VM)
}
$WmiVM = Get-WmiObject @QueryParam


# retrieve guest key-value values, collect in $GuestKVObj
$VmProperties = $WmiVM.GetRelated("Msvm_KvpExchangeComponent")
$GuestKVObj = New-Object PSObject
foreach ($Instance in $VmProperties.GuestExchangeItems) {
    $Properties = [XML]$Instance `
        | select -ExpandProperty INSTANCE `
        | select -ExpandProperty PROPERTY

    $AddMemberParams = @{
        NotePropertyName  = $Properties | where NAME -eq 'Name' | select -ExpandProperty VALUE
        NotePropertyValue = $Properties | where NAME -eq 'Data' | select -ExpandProperty VALUE
    }
    $GuestKVObj | Add-Member @AddMemberParams
}
$GuestKVObj
```

Beispiele für Abfragewerte: https://msdn.microsoft.com/en-us/library/cc136850(v=vs.85).aspx

Funktioniert wohl auch mit Ubuntu Servern:
* See [Overview](https://technet.microsoft.com/en-us/library/dn798287(v=ws.11).aspx) and [list of request options](https://msdn.microsoft.com/en-us/library/cc136850(v=vs.85).aspx)
* for retrieving network interface parameters, check `Msvm_GuestNetworkAdapterConfiguration`

```
function read-kvp {
    # example:  read-kvp $vm -p FullyQualifiedDomainName, OSMajorVersion

    Param(
        [Parameter(mandatory=$True)]
        [String]$VMName,

        # check https://msdn.microsoft.com/en-us/library/cc136850(v=vs.85).aspx
        [Parameter(mandatory=$True)]
        [ValidateSet(
            'FullyQualifiedDomainName',
            'OSBuildNumber',    # Kernel version
            'OSMajorVersion',   # 16.04, 10
            'OSName',           # Ubuntu, Windows 10 Pro
            IgnoreCase=$False
        )]
        [String[]]$Property
    )

    $QueryParam = @{
        NameSpace = 'root\virtualization\v2'
        Class = 'MSVM_ComputerSystem'
        Filter = ("ElementName='{0}'" -f $VMName)
    }
    $WmiVM = Get-WmiObject @QueryParam


    $VmProperties = $WmiVM.GetRelated("Msvm_KvpExchangeComponent").GuestIntrinsicExchangeItems
    foreach($VmProperty in $VmProperties) {
        foreach($RequestProperty in $Property) {
            $Selector = "/INSTANCE/PROPERTY[@NAME='Name']/VALUE[child::text()='{0}']" -f $RequestProperty
            $GuestExchangeItemXml = ([XML]$VmProperty).SelectSingleNode($Selector)
            if($GuestExchangeItemXml) {
                $Selector = "/INSTANCE/PROPERTY[@NAME='Data']/VALUE/child::text()"
                $RequestProperty
                $GuestExchangeItemXml.SelectSingleNode($Selector).Value
            }
        }
    }
}
```



# Linux

VSS service

- Is the hv_vss_daemon service running? (run "ps aux | grep -i vss")
# apt-get update
# apt-get install --install-recommends linux-virtual-lts-xenial
# apt-get install --install-recommends linux-tools-virtual-lts-xenial linux-cloud-tools-virtual-lts-xenial


## Key Value explained

https://www.altaro.com/hyper-v/key-value-pair-data-exchange-3-linux/

ls -la /var/lib/hyperv


.kvp_pool_0: When an administrative user or an application in the host sends data to the guest, the daemon writes the message to this file. It is the equivalent of HKLM\SOFTWARE\Microsoft\Virtual Machine\External on Windows guests. From the host side, the related commands are ModifyKvpItems, AddKvpItems, and RemoveKvpItems. The guest can read this file. Changing it has no useful effect.
.kvp_pool_1: The root account can write to this file from within the guest. It is the equivalent of HKLM\SOFTWARE\Microsoft\Virtual Machine\Guest on Windows guests. The daemon will transfer messages up to the host. From the host side, its messages can be retrieved from the GuestExchangeItems field of the WMI object.
.kvp_pool_2: The daemon will automatically write information about the Linux guest into this file. However, you never see any of the information from the guest side. The host can retrieve it through the GuestIntrinsicExchangeItems field of the WMI object. It is the equivalent of the HKLM\SOFTWARE\Microsoft\Virtual Machine\Auto key on Windows guests. You can’t do anything useful with the file on Linux.
.kvp_pool_3: The host will automatically send information about itself and the virtual machine through this file. You can read the contents of this file, but changing it does nothing useful. It is the equivalent of the HKLM\SOFTWARE\Microsoft\Virtual Machine\Guest\Parameter key on Windows guests.
.kvp_pool_4: Virtual Machine\Guest\Parameter


512 bytes for the key. The key is a sequence of non-null bytes, typically interpreted as char. According to the documentation, it will be processed as using UTF8 encoding. After the characters for the key, the remainder of the 512 bytes is padded with null characters.
2,048 bytes for the value. As with the key, these are non-null bytes typically interpreted as char. After the characters for the value, the remainder of the 2,048 bytes is padded with null characters.



```python
# see https://www.altaro.com/hyper-v/key-value-pair-data-exchange-3-linux/

KVP_FILE = '/var/lib/hyperv/.kvp_pool_1'


def read_kvp_worker(kvp_path):
    """worker for read_kvp() - read binary kvp data as key, value pairs"""

    with open(kvp_path, 'rb') as kvp_file:

        while True:
            key = kvp_file.read(512)
            val = kvp_file.read(2048)

            if key:
                yield key.decode().strip('\0'), val.decode().strip('\0')
            else:
                break


def read_kvp(kvp_path=KVP_FILE):
    """Concentate dictionary from kvp data"""

    return {k:v for k, v in read_kvp_worker(kvp_path)}


def write_kvp(data_dict, kvp_path=KVP_FILE):
    """Write dictionary data to kvp file"""

    # validate input data
    for k, v in data_dict.items():
        if len(k) > 512 or len(v) > 2048:
            raise ValueError(
                'Bad input "{}:{}" - max len for key is 512, for value 2048'
                ''.format(k,v)
            )

    # write out as binary
    with open(KVP_FILE, 'wb') as kvp_file:
        for key, val in data_dict.items():

            padded_key = key.ljust(512, '\0')
            padded_val = val.ljust(2048, '\0')

            kvp_file.write(padded_key.encode())
            kvp_file.write(padded_val.encode())


kvp = read_kvp()
new_kvp = {'status3' : 'okidoki'}
kvp.update(new_kvp)
write_kvp(kvp)
```
