# show all log entries

# Requires -Version 5.0
[CmdletBinding()]Param(
    [Int]$MaxEntries=10 
)
Set-StrictMode -version 5.0
$ErrorActionPreference = 'Stop'
$VerbosePreference = 'Continue' # force verbose operation
if ($DebugPreference -eq 'Inquire') {$DebugPreference = 'Continue'}

# Define path to module powershell files
$TestDir = Split-Path $Script:MyInvocation.MyCommand.Path
$ModuleDevDir = Split-Path -parent $TestDir
$ModuleDir = Join-Path $ModuleDevDir 'module' 

# Load functions - simulate module loading
. $ModuleDir\logging.ps1
Get-EventLog -LogName $LogName -Source $LogSource -Newest $MaxEntries

