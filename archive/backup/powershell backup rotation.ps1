function Filter-BadTimeStamps {
    <#
    .SYNOPSIS
    Helper for thinning out backup repositories - remove obsolete sessions

    .DESCRIPTION
    Filter a list of datetime objects, keep only the newest session in each 
    of given rotation schedule intervals.

    Rotation is specified as numbers of Minute, Hour, Day ... Year intervals
    where one session should be kept - see examples.

    .PARAMETER TimeStamps
    List of session datetime objects which should be filtered. Pipe input 
    and lists are supported. Expects datetime objects - convert from 
    directory names like
        
        $TimeStamp = "2017-11-14 23:11:00"
        [datetime]::parseexact($TimeStamp,"yyyy-MM-dd HH:mm:ss",$null)

    and back like

        $TestSession = (Get-Date).Addhours(-2)
        Get-Date -Date $TestSession -uFormat '%Y-%m-%d %H:%M:%S'

    .PARAMETER Minutes
    How much sessions to keep - minutes back from now. For each minute,
    only the newest session is kept. Optional parameter, default is 0.

    .PARAMETER Hours
    How much sessions to keep - hours back from now. For each hour,
    only the newest session is kept. Optional parameter, default is 0.

    .PARAMETER Days
    How much sessions to keep - days back from now. For each day,
    only the newest session is kept. Optional parameter, default is 0.

    .PARAMETER Weeks
    How much sessions to keep - weeks back from now. For each week,
    only the newest session is kept. Optional parameter, default is 0.

    .PARAMETER Months
    How much sessions to keep - months back from now. For each month,
    only the newest session is kept. Optional parameter, default is 0.

    .PARAMETER Years
    How much sessions to keep - years back from now. For each year,
    only the newest session is kept. Optional parameter, default is 0.

    .EXAMPLE
    $Sessions = @(
        (Get-Date).AddMinutes(-4),
        (Get-Date).AddMinutes(-5),
        (Get-Date).AddMinutes(-6),
        (Get-Date).AddHours(-2),
        (Get-Date).AddHours(-1),
        (Get-Date).AddHours(-2).AddMinutes(5),
        (Get-Date).AddDays(-5),
        (Get-Date).AddDays(-10),
        (Get-Date).AddDays(-12),
        (Get-Date).AddDays(-14),
        (Get-Date).AddDays(-3)
    )

    $Sessions | Filter-BadTimeStamps -Days 20 -Months 6 -Years 10
    Throw away every session but
      - the newest/newest session for each of the last 20 days,
      - the newest/newest session for each of the last 6 months,
      - the newest/newest session for each of the last 10 years

    .EXAMPLE
    $Sessions | Filter-BadTimeStamps -Years 5
    Throw away every session but
      - the newest/newest session for each of the last 5 years
    After running daily backups for 5 years, you have 4 december sessions and
    the backup of today which represents the newest session of this year.
    #>

    [CmdletBinding()]
    Param(
        [Parameter(Mandatory=$True, Position=0, ValueFromPipeline=$True)]
        [DateTime[]]$Sessions,
        [int]$Minutes = 0,
        [int]$Hours= 0,
        [int]$Days= 0,
        [int]$Weeks= 0,
        [int]$Months= 0,
        [int]$Years= 0
    )


    # Prepare script and session filter
    BEGIN {

        # Verbosity and script robustness
        Set-StrictMode -version 3.0
        if ( -not $PSBoundParameters.ContainsKey('ErrorAction') ) { $ErrorActionPreference = 'Stop' }
        if ($DebugPreference -eq 'Inquire') {$DebugPreference = 'Continue'}     # no confirmation in debug mode

        # current time
        $Now = Get-Date

        # container for input datetime objects
        $InputSessions = [System.Collections.ArrayList]@()

        # helper: determine when a given interval begins and ends
        function Get-Borders([String]$Name, [int]$Steps, [String]$StartFormat) {

            foreach ($Step in 0..$Steps) { if ($Step -gt 0) {

                # determine week interval  -use calendar functions
                if($Name -eq 'Week') {
                    $ThatDay = Get-Date -Date $Now.AddDays(7 * (1 - $Step)) -Hour 0 -Minute 0 -Second 0
                    $ThatWeekDay = $ThatDay.DayOfWeek.value__
                    $StartDate = $ThatDay.AddDays(-$ThatWeekDay + 1)
                    $StartDateString = Get-Date -Date $StartDate -uFormat '%Y-%m-%d %H:%M:%S'
                    $EndDate = $StartDate.AddDays(7).AddSeconds(-1)
                }

                # calculate minute, hour, day, month, year interval by applying format string
                else {
                    $ThatDate = Invoke-Expression ('$Now.Add{0}s(1 - $Step)' -f $Name)
                    $StartDateString = Get-Date -Date $ThatDate -uFormat $StartFormat
                    $StartDate =[datetime]::parseexact($StartDateString,"yyyy-MM-dd HH:mm:ss",$null)
                    $EndDate = Invoke-Expression ('$StartDate.Add{0}s(1).AddSeconds(-1)' -f $Name)
                }

                $EndDateString = Get-Date -Date $EndDate -uFormat '%Y-%m-%d %H:%M:%S'
                Write-Debug('{2} interval borders: "{0}" ... "{1}"' -f ($StartDateString, $EndDateString, $Name))
                New-Object PSObject -Property @{
                    Name = '{0}{1:00}' -f ($Name, $Step)
                    Oldest = $StartDate
                    Newest = $EndDate
                }
            }}
        }

        # calculate interval borders from input, sort by end date
        $Intervals = &{
            Get-Borders -Name 'Minute' -Steps $Minutes -Start '%Y-%m-%d %H:%M:00'
            Get-Borders -Name 'Hour' -Steps $Hours -Start '%Y-%m-%d %H:00:00'
            Get-Borders -Name 'Day' -Steps $Days -Start '%Y-%m-%d 00:00:00' 
            Get-Borders -Name 'Week' -Steps $Weeks
            Get-Borders -Name 'Month' -Steps $Months '%Y-%m-01 00:00:00'
            Get-Borders -Name 'Year' -Steps $Years -Start '%Y-01-01 00:00:00'
        } | Sort -Property Newest -Descending
    }

    # Prepare and collect input sessions
    PROCESS{

        foreach($Session in $Sessions) {
   
            # validate datetime: must not be younger than now
            if(($Now - $Session).TotalSeconds -lt 0) {
                $TimeStamp = Get-Date -Date $Session -uFormat '%Y-%m-%d %H:%M:%S'
                throw('Error: invalid session "{0}" - should be in the past' -f $TimeStamp)
            }

            # store session
            $Null = $InputSessions.add($Session)
        } 
    }

    # Filter collected input sessions
    END {

        # sort sessions - newest entry first
        $SessionObjects = foreach($Session in ($InputSessions | sort -Descending)) {
            Write-Debug('Got input timestamp "{0}"' -f $Session)
            New-Object PSObject -Property @{
                Label = (Get-Date -Date $Session -uFormat '%Y-%m-%d %H:%M:%S')
                Date = $Session
            }
        }

        # find good sessions (newest session which fit in any given interval)
        $GoodSessionDates = foreach ($Interval in $Intervals) {
            foreach($Session in $SessionObjects) {
                if(($Session.Date -ge $Interval.Oldest) -and ($Session.Date -le $Interval.Newest)) {
                    Write-Verbose('Got session "{1}" matching interval "{0}"' -f ($Interval.Name, $Session.Label))
                    $Session.Date
                    break
                }
            }
        }

        # return bad sesssion timestamps
        foreach($Session in $SessionObjects) {
            if($GoodSessionDates -notcontains $Session.Date) {
                Write-Verbose('Got obsolete session timestamp "{0}"' -f $Session.Label)
                $Session.Date
            }
        }
    }
}

