# Functions, cmdlets, classes

## Script environment


`#Requires` statements: a script can include more than one #Requires statement.
The `#Requires` statements can appear on any line in a script but must be the first item on a line in a script.

```
#Requires -Version 3.0
#Requires -Modules ...
#Requires -RunAsAdministrator
```

## Pipeline input script pattern

Accept pipeline input or array input
```
Param(    
    [Parameter(
            Position=0,
            Mandatory=$True,
            ValueFromPipeline=$True,
            ValueFromPipelineByPropertyName=$True
        )
    ]
    [Object[]]$VM    
)

BEGIN {
    # preparations for all VM loops
    $VMNames = [System.Collections.ArrayList]@()
}

PROCESS {
    foreach($CurrentVM in $VM) {
        $VMNames.add($CurrentVM.Name)
        ...
        $SingleResult   # pipe out results for each loop
        ...
    }
}

END{
    # handle data from all loops
    if ($VMNames.len -eq 0 ) {          # <<< pseudo-code
        throw 'No VMs in pipeline'
    }
}
```

## Function and Cmdlet parameters

Parameter validation for Cmdlets
```
Param(
    ...
    [ValidatePattern('(?-i:^[a-z]+$)')]
    [ValidateSet(
        'laptop',
        'desktop',
        IgnoreCase=$True
    )]
    [String[]]$HardwareType
    ...
)
```

Standard mandatory parameters
```
[CmdletBinding()]Param(
    [Parameter(Mandatory=$True)]
    [String]$Path
)
```

Mandatory parameters with useful error display

```
[CmdletBinding()]Param(
    ...
    [String]$Path=$( throw(
        'Start-Backup(): Missing -Path parameter, try providing it or run',
        'Start-ServerBackup or Start-USBRotation instead!'
    ))
    ...
)
```

Catch command line parameters with no option
```
[CmdletBinding()]Param(
    [Parameter(ValueFromRemainingArguments=$True)]
    $RemainingParam
)
```

Handling over long lists of parameters to functions (splatting)

```
$Params = @{
    NameSpace = 'root\virtualization\v2'
    Class = 'MSVM_ComputerSystem'
}
Get-WmiObject @Params -Filter 'ElementName="ex1"'
```

## Verbosity and Debug messages

Avoid confirm messages in debug mode, set error action preference
```
Set-StrictMode -version 2.0

if ( -not $PSBoundParameters.ContainsKey('ErrorAction') ) { $ErrorActionPreference = 'Stop' }
if ($DebugPreference -eq 'Inquire') {$DebugPreference = 'Continue'}
```

Copy verbose and debug from caller
* Caller:
    ```
    $BackupMailParams = @{
        Verbose =$PSCmdlet.MyInvocation.BoundParameters['verbose']
        Debug =$PSCmdlet.MyInvocation.BoundParameters['debug']
    }
    Initialize-BackupMail @BackupMailParams
    ```
* "Child" Cmdlet: do nothing
* Maybe better: `((Get-PSCallStack)[1].Arguments`


## Check for elevated permissions
