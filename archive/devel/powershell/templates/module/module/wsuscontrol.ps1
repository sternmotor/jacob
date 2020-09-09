<#
Functions orchestrating all updates on hyperv virtual machines and hyperv itself,
see README.md
#>

function Get-WsusStatus {
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
    .NOTES
        Gunnar Mann 25.07.2017
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
    [CmdletBinding()]Param(
        [Switch]$STANDARD,
        [Switch]$FAST
    )
    Set-StrictMode -version 2.0
    $ErrorActionPreference = 'Stop'
    if ($DebugPreference -eq 'Inquire') {$DebugPreference = 'Continue'}
    if ($DebugPreference -eq 'Continue') {$VerbosePreference = 'Continue'}

    <# get list of installed servers
    $LocalServers contains info about hyperv and vms like:

        HostName  VmID                                 Running  PDC VmName        Update
        --------  ----                                 -------  --- ------        ------
        hyperv1                                                                   standard
        dc1tmrelo 0a4cdae1-b35b-4e53-963a-2819d1320c68    True True dc1tmrelo     standard
                  cce42899-ebd5-405c-9fb2-158f1fb730fa    True      win 7
                  45f0e354-e9ae-4adf-9efc-6f5ae54b388d   False      somelinux
        fp1       d12a41fd-7706-4e09-aa8b-1c3f21778e93    True      fp1           fast
        mngt      ea7c68e4-ace2-4a56-a054-4097e819fe4d    True      mngt          standard
    #>
    #$LocalServers = list-vms
    #----- debug
    #$LocalServers | Export-CSV 'localservers.scv'
    $LocalServers = Import-CSV 'localservers.scv'
    $UpdateServers = get-updateservers $LocalServers
    #----- debug

    # check update status for update servers, add info to already collected info
    $ServerCredentialCSV = 'C:\Program Files\domain-wsus\vm-cred.csv'
    $ServerCred = Get-LocalCredential "$ServerCredentialCSV"
    $CMD = {hostname}
    run $UpdateServers $CMD $ServerCred -Wait | select ServerName, Result
}

function get-UpdateServers($AllServers) {
    # for update candidates according to FAST /STANDARD options, get number of pending updates

    if (($FAST -and $STANDARD) -or (-not $FAST -and -not $STANDARD)) {
        $AllServers | where Update
    }
    elseif ($STANDARD) {
        $AllServers | where Update -eq 'standard'
    }
    elseif ($FAST) {
        $AllServers | where Update -eq 'fast'
    }
    else {
        throw('Internal script logic error in filter-UpdateServers()')
    }
}


