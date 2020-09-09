<#
.SYNOPSIS
    Module definition file
.DESCRIPTION
    This is the public API for module cmdlets, functions and variables. Here,
    everything from *.ps1 files with this directory is getting imported and
    a defined subset is exported to the importer's namespace.
#>

# Import all ps1 files from $ScriptDir into module namespace
    if ($PSVersiontable.PSVersion.Major -le 2) {
        $PSScriptRoot = Split-Path -parent $Script:MyInvocation.MyCommand.Path # script scope!
    }
    . "$PSScriptRoot/config.ps1"   # read config first
    Get-ChildItem "$PSScriptRoot" -recurse -include '*.ps1' -exclude 'config.ps1' | foreach {. $_.FullName}

# Function and variable names to be exported into importing session
    Export-ModuleMember -function Start-WSUSControl
    Export-ModuleMember -function Start-WSUSUpdates
    Export-ModuleMember -function Get-WSUSStatus
    Export-ModuleMember -function New-LocalCredential
    Export-ModuleMember -function Get-LocalCredential
    # Export-ModuleMember -variable 
    # Export-ModuleMember -alias
    # Export-ModuleMember -function

