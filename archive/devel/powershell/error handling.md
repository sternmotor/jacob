# Error and exception handling

## General
Errors are critical exceptions leading to script stop/abort. Warnings notify about
errors which are either

1. not critical or
2. critical for overall script success but do not interfere with script
   execution following this error. Collect these exceptions and examine
   at end of script execution, throw exception then

Links:
* [Kevin Marquette](https://kevinmarquette.github.io/2017-04-10-Powershell-exceptions-everything-you-ever-wanted-to-know)

## Exception handling

Pattern for exception handling, for Cmdlets in `try{}` block it may be necessary
to add `-EA 'stop'` on order to reach `catch{}` block.

```
try {
    $Null = $RDServiceConfig.SetAllowTsConnections(1,1)
}
catch {
    switch -wildcard ( $_.FullyQualifiedErrorId ) {

        # WMI error setting access options
        'WMIMethodException' {
            Write-Warning(
                'Could not modify RDP settings - maybe due to domain restrictions'
            )
        }
        # Unknown error: re-throw exception
        Default {
            throw( $_ )
        }
    }
}
```

Re-throw with old exception as inner exception
```
catch {
    # ...
    throw [System.MissingFieldException]::new('Could not access field',$_.Exception)
    # ...
}
```

Retrieve all available Exceptions to help constructing ErrorRecord objects

```
$irregulars = 'Dispose|OperationAborted|Unhandled|ThreadAbort|ThreadStart|TypeInitialization'
[AppDomain]::CurrentDomain.GetAssemblies() | ForEach-Object {
    $_.GetExportedTypes() -match 'Exception' -notmatch $irregulars |
    Where-Object {
        $_.GetConstructors() -and $(
        $_exception = New-Object $_.FullName
        New-Object Management.Automation.ErrorRecord $_exception, ErrorID, OpenError, Target
        )
    } | Select-Object -ExpandProperty FullName
} 2> $null
```

## Error handling for remote sessions
When running remote sessions in parallel (as powershell jobs), all remote exceptions need to be catched. Otherwise, response data send back is getting cut and error display is messed up. Basically, parallel powershell remote operation is [fubar](https://en.wikipedia.org/wiki/FUBAR_(disambiguation)).

Here, `Invoke-PSH -Batch` is some script to call remote PSSessions in parallel and wait till all jobs are finished.
```
$Cmd = {
    try {
        $Null = Get-Service WsusService -EA 'stop'
        # fine, wsus is installed
        try{
            < commands to run in case wsus is installed> 2>&1
        }
        catch {
            Write-Error('Could not find install msi package!')
        }
    }
    catch {
        # do nothing, wsus is not installed
    }
}
$h | Invoke-PSH -Batch $Cmd
```
