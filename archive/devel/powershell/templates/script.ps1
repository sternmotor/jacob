<#
.SYNOPSIS
    Get VM and update status for all machines running, currently
.DESCRIPTION
    Get VM and update status for all machines running, currently
.PARAMETER Standard
    If specified, servers in "OU=Windows,OU=Servers,..." AD OU are 
    checked for pending updates and the rest of servers is handled
    like unmanaged servers. Default is to check all servers which 
    are running and in any of "WSUS-FastUpdates" group or standard OU.
.PARAMETER Fast
    If specified, servers in "WSUS-FastUpdates" AD group are 
    checked for pending updates and the rest of servers is handled
    like unmanaged servers. Default is to check all servers which 
    are running and in any of "WSUS-FastUpdates" group or standard OU.
.EXAMPLE
    Get-WsusStatus -Fast
    Retrieves info about all vms and hyperv and checks servers in AD group
    "WSUS-FastUpdates" if there are pending updates
.LINK
    Start-WsusControl
    Start-WsusUpdates
    Get-WsusStatus
    New-LocalCredential
    Get-LocalCredential
#>

# COMMAND LINE PARAMETERS AND VALIDATIONS
    # Requires -Version 2.0
    [CmdletBinding()]Param(
        [Switch]$STANDARD,
        [Switch]$FAST,

        [Parameter(Mandatory=$True, Position=0)]
        [ValidateNotNullOrEmpty()]
        [String]$UserName
    )
    Set-StrictMode -version 2.0
    if ( -not $PSBoundParameters.ContainsKey('ErrorAction') ) { $ErrorActionPreference = 'Stop' }
    if ($DebugPreference -eq 'Inquire') {$DebugPreference = 'Continue'}     # no confirmation in debug mode
    if ($DebugPreference -eq 'Continue') {$VerbosePreference = 'Continue'}  # debug option forces verbose

    # Check elevated privileges
    $CurrentIdentity = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent())
    if ($CurrentIdentity.IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator") -eq $False) {
        throw('Script needs to run with elevated privileges!')
    }    
    
# CONSTANTS
    $SCRIPT_DIR = Split-Path $Script:MyInvocation.MyCommand.Path

# MODULES AND SNAPINS
    Import-Module ActiveDirectory -Verbose:$False
    Import-Module ConfigFiles     -Verbose:$False


# SCRIPT MAIN FUNCTION
function main() {
    needed_by_main 
}

# SCRIPT HELPER FUNCTIONS
function needed_by_main() {

}

# START SCRIPT
main
