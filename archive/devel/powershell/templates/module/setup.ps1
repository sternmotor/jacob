<#
.SYNOPSIS
    Install, remove or test an installable module.
.DESCRIPTION
    Specify "-Install" or "-Uninstall" or "-Test" to handle installation
    of this module and binaries to system path.
    
    Furthermore, a logging handler for this module is installed, watch this 
    like specified in example. An "eventlog.ps1" file is created in module
    dir dynamically so the logging functions here are available in script,
    too.
.PARAMETER ModuleName
    Name of module (where to install). This is an optional parameter.
.PARAMETER BinDir
    Directory where binaries get copied to - should be in systems $env:Path.
    If not specified, binary files are copied to "C:\Program Files\Tools".
.PARAMETER ModuleBaseDir
    Directory where this modules gets copied to - should be in powershells
    $env:PSModulePath. If not specified, the module directory is copied to 
    "C:\Program Files\WindowsPowerShell\Modules"
.PARAMETER Install
    Install module and binary files to systems' path.
    * copy bin/* to C:\Program Files\Tools (must be callable cmd files)
    * remove old module stuff and copy module files and README.md to 
      C:\Program Files\WindowsPowerShell\Modules
.PARAMETER UnInstall
    Remove module and binary files from systems' path.
    * remove old module from C:\Program Files\WindowsPowerShell\Modules
    * look up bin files, remove from C:\program files\tools (remove binaries 
      present in module's bin dir from "BinDir")
.PARAMETER Test
    Run all test files under "tests" dir here, collect errors
.PARAMETER ScriptDir
    By default, all files are copied from path relative to dir where this setup 
    script is located. You may change this optionally.
.EXAMPLE
    Get-EventLog -Logname Install -LogSource Backup2USBHyperV -Newest 10 
    Check latest entries in module event log
.LINK
#>

# SCRIPT OPTIONS -------------------------------------------------------------

    # Requires -Version 2.0
    [CmdletBinding()]
    Param(
        [String]$BinDir = 'C:\Program Files\Tools',
        [String]$ModuleBaseDir = 'C:\Program Files\WindowsPowerShell\Modules',
        [String]$ModuleName = 'Backup2USBHyperV', 
        [Switch]$Uninstall,
        [Switch]$Install,
        [Switch]$Test,
        [String]$ScriptDir = (Split-Path $Script:MyInvocation.MyCommand.Path)
    )

# MAIN LOOP AND CONSTANTS ----------------------------------------------------

    $EventIDs = @{
        Installed = 101
        UnInstalled = 102
    }

function main {    
    <#Analyse command line options, start functions, log progress#>

    $Source = @{
        bin = (Join-Path "$ScriptDir" 'bin')
        module = (Join-Path "$ScriptDir" 'module')
        tests = (Join-Path "$ScriptDir" 'tests')
    }
    $Target = @{
        bin = $BinDir
        module = (Join-Path "$ModuleBaseDir" "$ModuleName")
    }

    if ($Install) {
        start-uninstall $Source $Target
        start-install $Source $Target
    }
    elseif ($Uninstall) {
        start-uninstall $Source $Target
    }
    elseif ($Test) {
        start-tests $Source.tests
    }
    else {
        throw('Whats up? Specify "-Install" or "-Uninstall" or "-Test"!')
    }
}


# FUNCTIONS ------------------------------------------------------------------

function start-install($Source, $Target) {
    # copy bin
    if (Get-ChildItem $Source.bin) {
        log-info('Installing executables from "bin" dir at path "{0}"' -f $Target.bin)
        $Null = New-Item -path $Target.bin -itemtype directory -force
        Get-ChildItem $Source.bin | Copy-Item -Destination $Target.bin -Recurse
    }
    else{
        Write-Debug('No software found in source dir "{0}"' -f $Source.bin)
    }

    # copy module 
    if (Get-ChildItem $Source.module) {
        log-info('Installing powershell "module" files at path "{0}"' -f $Target.module)
        $Null = New-Item -path $Target.module -itemtype directory -force
        Get-ChildItem $Source.module | Copy-Item -Destination $Target.module -Recurse
    }
    else{
        Write-Debug('No powershell module files found in source dir "{0}"' -f $Source.module)
    }
}

function start-uninstall($Source, $Target) {
    # parse all entries in source bin dir, remove from target bin dir
    log-info('Removing executables of this module from directory "{0}"' -f $Target.bin)
    foreach ($FileName in (Get-ChildItem $Source.bin)) {
        $TargetPath = Join-Path $Target.bin "$FileName"
        if (Test-Path $TargetPath) {
            Write-Debug('Deleting "{0}"' -f $TargetPath)
            Remove-Item $TargetPath 
        }
    }

    log-info('Removing powershell module installed at path "{0}"' -f $Target.module)
    if (Test-Path $Target.module) {
        Remove-Item $Target.module -Force -Recurse
    }
}

function start-tests([String]$TestDir) {
    log-info('Running *.ps1 files under "{0}"' -f $TestDir)
}

# PREPARE LOGGING AND OUTPUT, CALL MAIN FUNCTION -----------------------------

    # Check elevated privileges
    $CurrentIdentity = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent())
    if ($CurrentIdentity.IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator") -eq $False) {
        throw('Script needs to run with elevated privileges!')
    }

    # Script robustness
    Set-StrictMode -version 2.0
    if ( -not $PSBoundParameters.ContainsKey('ErrorAction') ) { $ErrorActionPreference = 'Stop' }

    # Fix verbosity options
    if ($DebugPreference -eq 'Inquire') {$DebugPreference = 'Continue'}     # no confirmation in debug mode
    if ($DebugPreference -eq 'Continue') {$VerbosePreference = 'Continue'}  # debug option forces verbose

    # Set up logging
    if (-not [Diagnostics.EventLog]::SourceExists($ModuleName)) {
        New-EventLog -LogName 'Application' -Source $ModuleName
    }
    function log-info([String]$Message, [Int]$EventID=0001) {
        Write-Verbose "$Message"
        Write-EventLog 'Application' $ModuleName $EventID 'Information' "$Message"
    }
    function log-warn([String]$Message, [Int]$EventID=0001) {
        Write-Error "$Message" -ErrorAction 'continue'
        Write-EventLog 'Application' $ModuleName $EventID 'Warning' "$Message"
    }
    function log-error([String]$Message, [Int]$EventID=0001) {
        Write-EventLog 'Application' $ModuleName $EventID 'error' "$Message"
        throw "$Message" 
    }

    # Import modules and snapins


    # Start main function
    main
