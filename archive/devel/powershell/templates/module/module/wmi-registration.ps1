function Enable-USBWatcher {
    <#
    wmi event is registered in current powershell session, only
    permanent wmi event subscriptions: https://learn-powershell.net/2013/08/14/powershell-and-events-permanent-wmi-event-subscriptions/
    permanenent wmi event handlers are registered in the WMI repositiory
    unregister wmi event like Unregister-Event "USBRemoved"

    watch like get-EventLog -LogName Application -Source 'Backup2USB' -Newest 3

    # find all registered event filters like: 
        Get-WMIObject -Namespace root\Subscription -Class __EventFilter
        Get-WMIObject -Namespace root\Subscription -Class CommandLineEventConsumer
        Get-WMIObject -Namespace root\Subscription -Class  __FilterToConsumerBinding
    #>


    # SCRIPT SETUP, CONSTANTS ------------------------------------------------

    # Command line options and constants
    [CmdletBinding()]
    Param(
        [String]$LogName = 'Application',
        [String]$LogSource = 'Backup2USBHyperV',
        [String]$WmiInstance = 'Win32_LogicalDisk',
        [Int]$WmiDriveType=2,
        [Int]$WmiCollectInterval=5,
        [String]$ActionScriptName = 'Backup2USBHandler.ps1',
        [String]$ScriptDir = (Split-Path $Script:MyInvocation.MyCommand.Path)
    )

    # PREPARE LOGGING AND OUTPUT ---------------------------------------------

    # Check elevated privileges
    $CurrentIdentity = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent())
    if ($CurrentIdentity.IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator") -eq $False) {
        throw('Script needs to run with elevated privileges!')
    }

    # Verbosity and script robustness
    Set-StrictMode -version 2.0
    if ( -not $PSBoundParameters.ContainsKey('ErrorAction') ) { $ErrorActionPreference = 'Stop' }
    if ($DebugPreference -eq 'Inquire') {$DebugPreference = 'Continue'}     # no confirmation in debug mode
    if ($DebugPreference -eq 'Continue') {$VerbosePreference = 'Continue'}  # debug option forces verbose

    # MAIN -------------------------------------------------------------------

    # Query for finding all Wmi instances of watched stuff
    $EventQuery = "within {2} where TargetInstance ISA '{0}' and TargetInstance.DriveType = {1}" -f (
        $WmiInstance, $WmiDriveType, $WmiCollectInterval
    )

    # Powershell script to be called from event handler
    $ActionScript = Join-Path $ScriptDir $ActionScriptName

    # HandlerName used for identifying wmi events in lower functions
    $HandlerName = $LogSource

    # register event filters for insert, remove and modify
    remove-registration -Type 'Insert'
    remove-registration -Type 'Remove'
    remove-registration -Type 'Modify'

    create-registration -Type 'Insert' -WmiEvent '__instanceCreationEvent'     
    create-registration -Type 'Remove' -WmiEvent '__instanceDeletionEvent'     
    create-registration -Type 'Modify' -WmiEvent '__instanceModificationEvent' 
}

function Disable-USBWatcher {
    <#See Install-USBWatcher#>


    # SCRIPT SETUP, CONSTANTS ----------------------------------------------------

    # Command line options and constants
    [CmdletBinding()]
    Param(
        [String]$LogName = 'Application',
        [String]$LogSource = 'Backup2USBHyperV',
        [String]$ScriptDir = (Split-Path $Script:MyInvocation.MyCommand.Path)
    )

# PREPARE LOGGING AND OUTPUT, CALL MAIN FUNCTION -----------------------------

    # Check elevated privileges
    $CurrentIdentity = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent())
    if ($CurrentIdentity.IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator") -eq $False) {
        throw('Script needs to run with elevated privileges!')
    }

    # Verbosity and script robustness
    Set-StrictMode -version 2.0
    if ( -not $PSBoundParameters.ContainsKey('ErrorAction') ) { $ErrorActionPreference = 'Stop' }
    if ($DebugPreference -eq 'Inquire') {$DebugPreference = 'Continue'}     # no confirmation in debug mode
    if ($DebugPreference -eq 'Continue') {$VerbosePreference = 'Continue'}  # debug option forces verbose

    # Query for finding all Wmi instances of watched stuff
    $EventQuery = "within {2} where TargetInstance ISA '{0}' and TargetInstance.DriveType = {1}" -f (
        $WmiInstance, $WmiDriveType, $WmiCollectInterval
    )

    # powershell script to be called from event handler
    $ActionScript = Join-Path $ScriptDir $ActionScriptName

    # HandlerName used for identifying wmi events
    $HandlerName = $LogSource

    # register event filters for insert, remove and modify
    remove-registration -Type 'Insert'
    remove-registration -Type 'Remove'
    remove-registration -Type 'Modify'
}


# HELPER FUNCTIONS -----------------------------------------------------------


function create-registration([String]$Type, [String]$WmiEvent) {
    <#
    Register WMI Event watcher, Action handler and bind both togehter 
    so each event launches Action. Prior to this, registered events are cleared
    #>

    $WmiID = "$HandlerName$Type"


    $FilterParams = @{
        Class = '__EventFilter'
        Namespace = 'root\subscription'
        Arguments = @{
            Name = '{0}Filter' -f $WmiID
            EventNameSpace = 'root\cimv2'
            QueryLanguage = 'WQL'
            Query = "select * from $WmiEvent $EventQuery"
        }
    }

    # see consumers here: https://msdn.microsoft.com/en-us/library/aa384749(v=vs.85).aspx
    $CmdLine = 'powershell.exe -NonInteractive -NoProfile -File "{0}" -Action {1}' -f ($ActionScript, $Type)
    Write-Debug('Command line: {0}' -f $CmdLine)
    $ConsumerParams = @{
        Class = 'CommandLineEventConsumer'
        Namespace = 'root\subscription'
        Arguments = @{
            Name = '{0}Action' -f $WmiID
            RunInteractively='false'
            CommandLineTemplate="$CmdLine"
        }
    }

    # Binding overview https://learn-powershell.net/2013/08/14/powershell-and-events-permanent-wmi-event-subscriptions/
    $BindingParams = @{
        Class = '__FilterToConsumerBinding'
        Namespace = 'root\subscription'
        Arguments = @{
            Filter = (Set-WmiInstance @FilterParams)
            Consumer = (Set-WmiInstance @ConsumerParams)
        }
    }

    $ConsumerBinding = Set-WmiInstance @BindingParams
    msg-info "Registered USB plug handlers for $HandlerName $Type action ($CmdLine)" $MsgID.WmiEventSetup
}

function remove-registration([String]$Type) {
    <#
    Register WMI Event watcher, Action handler and bind both togehter 
    so each event launches Action. Prior to this, registered events are cleared
    #>

    $WmiID = "$HandlerName$Type"

    # cleanup event filter
    _unregister '__FilterToConsumerBinding' "Filter = ""__EventFilter.Name='${WmiID}Filter'""" 
    _unregister 'CommandLineEventConsumer'  "Name='${WmiID}Action'" 
    _unregister '__EventFilter'             "Name='${WmiID}Filter'" 
    msg-info "Unregistered USB plug handlers for $HandlerName $Type action" $MsgID.WmiEventRemoved
}

function _unregister($WmiClass, $WmiFilter) {

    Write-Debug('Removing Wmi Object "{0}", class "{1}"' -f ($WmiFilter, $WmiClass))
    $GetWmiParams = @{
        Namespace = 'root\subscription'
        Class = $WmiClass
        Filter = $WmiFilter
    }
    Get-WmiObject @GetWmiParams | Remove-WmiObject
}
