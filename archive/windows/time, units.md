# Powershell Time, Date, Units, Numbers

## Timers
```
$StopWatch = [system.diagnostics.stopwatch]::StartNew()
# ...  some operation
$StopWatch.Stop()
$StopWatch.Elapsed.TotalSeconds
$StopWatch.Elapsed.TotalHours
```
## Date and Time

Get Timestamp
```
'{0:yyyy-MM-dd}_{0:HH-mm-ss}' -f (Get-Date)
```


## NTP setup
see [Network article]('network dns ssl.md')

## Codeschnipsel



Bei der Arbeit mit Powershell datetime Objekten werden folgende Platzhalter für die Formatierung von Ausgaben und Eingaben verwendet:

* `d`:     Day of month 1-31
* `dd`:    Day of month 01-31
* `ddd`:   Day of month as abbreviated weekday name
* `dddd`:  Weekday name
* `h`:     Hour from 1-12
* `H`:     Hour from 1-24
* `hh`:    Hour from 01-12
* `HH`:    Hour from 01-24
* `m`:     Minute from 0-59
* `mm`:    Minute from 00-59
* `M`:     Month from 1-12
* `MM`:    Month from 01-12
* `MMM`:   Abbreviated Month Name
* `MMMM`:  Month name
* `s`:     Seconds from 1-60
* `ss`:    Seconds from 01-60
* `t`:     A or P (for AM or PM)
* `tt`:    AM or PM
* `yy`:    Year as 2-digit
* `yyyy`:  Year as 4-digit
* `z`:     Timezone as one digit
* `zz`:    Timezone as 2-digit
* `zzz`:   Timezone
* `FFF`:   Hundertstel

#### Unix Time

Convert DateTime object to [unix time](https://en.wikipedia.org/wiki/Unix_time "https://en.wikipedia.org/wiki/Unix_time")
* Example data
    ```
    [DateTime]$DateTime = (Get-Date).AddHours(-1)  # example data: now - 1 hour
    ```

* Unix epoch is January 1st, 1970 at 12:00 AM (midnight) UTC
    ```
    [datetime]$Origin = '1970-01-01 00:00:00'
    ```

* `[Math]::Floor` is used, as Unix time is based on the number of whole seconds since the epoch.
Calculation is based on ticks (Int64), rather than seconds (Int32), to avoid the Year 2038 problem
    ```
    # A: Conversion to UTC epoch seconds
    [long][Math]::Floor(($DateTime.ToUniversalTime() - $Origin).Ticks / [timespan]::TicksPerSecond)
    # B: Conversion to local timezone's seconds
    [long][Math]::Floor(($DateTime - $Origin).Ticks / [timespan]::TicksPerSecond)
    ```

Convert [unix time](https://en.wikipedia.org/wiki/Unix_time "https://en.wikipedia.org/wiki/Unix_time") to DateTime:

```
[Int]$EpochSeconds = 1453342165
# Unix epoch is January 1st, 1970 at 12:00 AM (midnight) UTC
[datetime]$Origin = '1970-01-01 00:00:00'
$Origin.AddSeconds($EpochSeconds)
```

#### Startzeiten

Zeitpunkte in der Vergangenheit berechnen (`MaxAge` = Anzahl der Stunden, weche zurück gegangen werden soll)

```
StartTime = (Get-Date).AddHours(-$MaxAge)
```

#### Zeitstempel

DateTime Objekt in String umwandeln
```
$Session = (Get-Date).Addhours(-2)
Get-Date -Date $Session -uFormat '%Y-%m-%d %H:%M:%S'
```
```
2018-02-13 07:05:06
```

Zeitstempel String in DateTime umwandeln:
```
$TimeStamp = "2017-11-14 23:11:00"
[datetime]::parseexact($TimeStamp,"yyyy-MM-dd HH:mm:ss",$null)
```

```
Dienstag, 14. November 2017 23:11:00
```


Zeitstempel mit Millisekunden (`YYYY-MM-DD HH:MM:SS.FFF) - dieser :

    $SessionID = '{0}.{1:D3}' -f (      # 3 digits always
        (Get-Date -uFormat '%Y-%m-%d %H:%M:%S'),
        (get-date).millisecond          
    )

ergibt zum Beispiel `2014-09-19 13:03:22.072`
#### Kalender

Monatsberechnung
```Powershell
$startofmonth = Get-Date $date -day 1 -hour 0 -minute 0 -second 0
$endofmonth = (($startofmonth).AddMonths(1).AddSeconds(-1))
```


Kalenderwochen nach ISO-8601`-`Standard beginnen am Montag. Die erste Woche des Jahres ist jene mit 4 Tagen ( bzw. mit einem Donnerstag). `Max = 52,53`.

    Get-Date -uformat %V

#### Zufallszahlen

Zufallsdaten Kurz: <span style="line-height: 1.5;">Länge = 3, nur Ziffern. Kann für Session ID’s verwendet werden, alternativ siehe </span>[Zeitstempel Millisekunden](#ZeitstempelMillisekunden)<span style="line-height: 1.5;">.</span>

      $Rnd  = ( [Char[]]'0123456789' | Get-Random -Count 3 ) -Join ''

Zufallsdaten in Passwort Qualität: <span style="line-height: 1.5;">Länge = 16, Sonderzeichen und [a-zA-Z0-9]</span><span style="color: rgb(0, 52, 113); font-family: 'Lucida Console', Courier, monospace; font-size: 0.9em; line-height: 1.5; background-color: rgb(254, 254, 254);">      </span>

    [Char[]]$Chars = @(
      '~!@#$%^&*()_-+={}[]\|:;<>,.?/',
      'abcdefghijklmnopqrstuvwxyz',
      'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
      '0123456789'
    ) -Join ''

    [Int]$Length = 16
    $Password = ( $Chars | Get-Random -Count $Length ) -Join ''
    $Password
