<#
General logger setup for whole module and setup script

watch like get-EventLog -LogName Application -Source 'Backup2USBHyperV' -Newest 10
#>

# LOGGING OPTIONS AND EVENTIDs -----------------------------------------------
$LogName = 'Application'
$LogSource = 'Backup2USBHyperV'

$MsgID = @{
    Unspecified     = 0000
    ModuleSetup     = 0001 # setup.ps1
    ModuleRemoved   = 0002
    WmiEventSetup   = 0010 # wmi-registrationn.ps1 
    WmiEventRemoved = 0011
    USBInsertEvent  = 0021 # wmi-event-handler.ps1
    USBRemoveEvent  = 0022
    USBHandlerOptionError = 0023
}


# PREPARE EVENTLOG CHANNEL ---------------------------------------------------

function install-logger() {
    # install logger

    # Verbosity and script robustness
    Set-StrictMode -version 2.0
    if ( -not $PSBoundParameters.ContainsKey('ErrorAction') ) { $ErrorActionPreference = 'Stop' }


    try {
        Get-EventLog -LogName $LogName -Source $LogSource -Newest 0 -EA 'stop'
    } 
    catch {
        # Check elevated privileges
        $CurrentIdentity = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent())
        if ($CurrentIdentity.IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator") -eq $False) {
            throw('Setting up the logger needs to run with elevated privileges!')
        }

        # Install logger
        New-EventLog -LogName $LogName -Source $LogSource
    }

    Write-Debug('Check logs like "Get-EventLog -LogName "{1}" -Source "{0}" -Newest 10"' -f (
            $LogSource, $LogName
        )
    )
}

function uninstall-logger() {
    # Remove logger application and all log entries from system

    # dummy function ... removing log and entries does not work
}

# PREPARE LOGGING FUNCTIONS --------------------------------------------------

function msg-info([String]$Message, [Int]$EventID=$MsgID.Unspecified) {
    Write-Verbose "$Message"
    Write-EventLog $LogName $LogSource $EventID 'Information' "$Message"
}
function msg-warn([String]$Message, [Int]$EventID=$MsgID.Unspecified) {
    Write-Error "$Message" -ErrorAction 'continue'
    Write-EventLog $LogName $LogSource $EventID 'Warning' "$Message"
}
function msg-error([String]$Message, [Int]$EventID=$MsgID.Unspecified) {
    Write-EventLog $LogName $LogSource $EventID 'error' "$Message"
    throw "$Message" 
}


