# Requires -Version 5.0
[CmdletBinding()]Param()
Set-StrictMode -version 5.0
$ErrorActionPreference = 'Stop'
$VerbosePreference = 'Continue' # force verbose operation
if ($DebugPreference -eq 'Inquire') {$DebugPreference = 'Continue'}


# Define path to module powershell files
$TestDir = Split-Path $Script:MyInvocation.MyCommand.Path
$ModuleDevDir = Split-Path -parent $TestDir
$ModuleDir = Join-Path $ModuleDevDir 'module' 

# Load functions - simulate module loading
. $ModuleDir\usb-eventhandler.ps1
. $ModuleDir\logging.ps1

# verify script breaks in case two options are given
try {
    Initialize-Backup2USB -Remove -Insert
    throw('Test must fail for both -remove and -insert option given')
}
catch {
    Write-Verbose('OK')
}


# verify script breaks in case no options are given
try {
    Initialize-Backup2USB 
    throw('Test must fail for in case none of -remove or -insert option is given')
}
catch {
    Write-Verbose('OK')
}

# start initialize functions
Initialize-Backup2USB -Insert
Initialize-Backup2USB -Remove

