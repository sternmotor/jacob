# Powershell data handling


## Random strings, Passwords

```
function Create-AutoPW ([int]$PWLength, [float]$SpecialsRatio=0.2){
    # create clear text password proposal

    if (-not $PWLength) {
        $PWLength=$DEFAULT_PW_LENGTH
    }
    Add-Type -AssemblyName System.Web
    # Specials = number of non-aplphanumeric characters, here one third
    $Specials = [int] $PWLength * $SpecialsRatio
    [System.Web.Security.Membership]::GeneratePassword($PWLength, $Specials)
}
```

## Output

Display data in GUI table with interactive sort and filter options
```
$Data | Out-Grid
```

Pattern for displaying objects with custom headers and units
```
BEGIN {
    $DisplayObjects = [System.Collections.ArrayList]@()
}

PROCESS {
    # collect input data from pipe and arrays
    foreach($D in $Disks) {
        $DisplayObjects.add($D)
    }
}

END {
    $Properties = @(
        @{Name = 'Number'     ;Expr = {$PSItem.DiskNumber}},
        @{Name = 'Name'       ;Expr = {$PSItem.FriendlyName}},
        @{Name = 'Mount'      ;Expr = {$PSItem.DataVolume.Driveletter}},
        @{Name = 'Type'       ;Expr = {$PSItem.Type}},
        @{Name = 'Encryption' ;Expr = {$PSItem.Encryption}},
        @{Name = 'Lock'       ;Expr = {$PSItem.LockStatus}},
        @{Name = 'Serial'     ;Expr = {$PSItem.SerialNumber}},
        @{Name = 'Size'       ;Expr = {'{0} GB' -f ([math]::Round($PSItem.Size/1GB,0))}},
        @{Name = 'Health'     ;Expr = {$PSItem.HealthStatus}},
        @{Name = 'Operational';Expr = {$PSItem.OperationalStatus}}
    )
    $DisplayObjects | format-table -wrap -autosize $Properties
}
```

### Strings, Text
Take a path and limit each path element to three characters except the last one
```
function shorten-path([String]$Path, [uint64]$Length=3, [String]$Sep='\') {
    $Entry = Split-Path $Path -Leaf
    $ParentDir =  Split-Path $Path -Parent

    $ShortElements = foreach ($Element in $ParentDir.split($Sep)) {
        #$len=[math]::min($Length, $Element.Length)
        #$len
        try {
            $Element[0..($Length-1)] -Join ''
        }
        catch{
            $Element
        }
    }
    return Join-Path ($ShortElements -Join $Sep) $Entry
}
```


In Powershell können Objekte nicht direkt in Zeichenfolgen eingebettet werden, zum Beispiel funktioniert folgender Code **nicht**:

<pre>$SomeArray = 45, 42, 1, 6
"This array is $SomeArray.Count elements in size"
</pre>

Daher wird in Powershell enheitlich folgende Schreibweise verwendet:

<pre>$SomeArray = 45, 42, 1, 6
'This array is {0} elements in size' -f $SomeArray.Count
</pre>

Ein weiterer Vorteil dieser leicht umständlichen Schreibweise ist, das Variablen und Ausdrücke mehrzeilig angegeben werden können:

<pre>'Hallo dieser Text beinhaltet die Objekt-Eigenschaften "{0}" und "{1}"' -f (
    'Bernd',
    (Get-AdUser -Name Bernd).Birthdate
)
</pre>

Siehe auch [Zahlen](/Abteilungen/Entwicklung/Executive/Tools/Windows/Powershell/Programmierung/Daten_und_Variablen#Berechnungen.2C_Zahlen "Abteilungen/Entwicklung/Executive/Tools/Windows/Powershell/Programmierung/Daten_und_Variablen#Berechnungen.2C_Zahlen")<span style="line-height: 1.5;">.</span>

Mehrzeilige Texte (Multiline): Platzhalter müssen nicht in der selben Zeile stehen wie Werte, Zeilen müssen durch "," getrennt werden.

<pre>Write-Verbose(
    '* Generating Putty SSH key. In the dialog following hitting "OK",',
    'set comment "{0}" and hit "Save private key" (no password).',
    'Fill in location "{1}", close Dialog.' -f ($COMMENT, $PUTTY_PPK_FILE)
)</pre>

Zeilenumbruch einfügen: s<span style="line-height: 1.5;">oll ein Array aus Strings als Text mit Zeilenumbrüchen ausgegeben werden, nicht </span>``n`<span style="line-height: 1.5;"> verwenden da dieser Ausdruck schlecht zu lesen und nicht portabel ist. Stattdessen:</span>

<pre>$ZabbixServerErrors -Join [Environment]::NewLine</pre>

Umwandlung von `Tim, Tom Zack, Finn Zick` in  `"Tim", "Tom Tom Zack", "Finn Zick"` (<span style="line-height: 1.5;">Listen als Text ausgeben, jedes Item in “” eingeschlossen, Komma getrennt. Das sieht sehr aufwendig aus, ermöglicht aber professionell wirkende Ausgaben)</span><span style="color: rgb(119, 119, 119); line-height: 1.5; background-color: rgb(254, 254, 254);"> </span>

<pre>$Users = 'Tim', 'Tom Zack', 'Finn Zick'
( $Users | foreach {  '"{0}"' -f $_ } )  -Join ', '</pre>

<span>String einkürzen: Sollen lange Strings ausgegeben werden wo kein Platz ist, können diese hiermit eingekürzt werden (in der Mitte des gekürzten Strings wird </span>`" ... "`<span> eingefügt)</span>

<pre>function shorten-string([string]$string, [int]$maxlength, $separator='.') {
    # cut string begin and end so it fit's into maxlength
    # make maxlength uneven number for "..." instead of ".."

    if ($string.length -le $maxlength) {
        return $string
    }
    else {
        $BeginEndLength= [int](($Maxlength-5)/2)
        $SeparatorLength = $MaxLength - (2 * $BeginEndlength) -2
        return '{0} {1} {2}' -f (
            $String.substring(0,$BeginEndLength),
            ($Separator * $Separatorlength),
            $String.substring(($String.length-$BeginEndLength), $BeginEndLength)
        )
    }
}
</pre>

Umwandeln von Strings in Hash Strings: siehe [Quelle](https://gallery.technet.microsoft.com/scriptcenter/Get-StringHash-aa843f71 "https://gallery.technet.microsoft.com/scriptcenter/Get-StringHash-aa843f71")

<pre>$StringBuilder = New-Object System.Text.StringBuilder
$Alg = [System.Security.Cryptography.HashAlgorithm]::Create('MD5')
foreach ($HashPart in $Alg.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($IDString))) {
    $Null = $StringBuilder.Append($HashPart.ToString("x2").toupper())
}
$StringBuilder.ToString()</pre>

### Zahlen

Formatieren von Zahlenangaben

*   Float: 5 Nachkommastellen

    <pre>'{0:N5}' -f 23.2 # 23.2000
    </pre>

*   Integer: 3 führende Nullen

    <pre>'{0:D3}' -f 34  # 034</pre>

* round numbers
[math]::round

Mathematische Funktionen auflisten:

<pre>[math].GetMethods() | Select -Property Name -Unique | sort</pre>

Wert hexadezimal ausgeben:

<pre>'{0:X}' -f $Decimal</pre>

Zahlen menschlich lesbar ausgeben:

<pre>function human_readable([int]$Size){
    # return ham readbale string for size value ... 3.1 TB, 404.5 MB
    if ($Size -gt 1TB) { return "{0:n1} TB" -f ($Size / 1TB) }
    if ($Size -gt 1GB) { return "{0:n1} GB" -f ($Size / 1GB) }
    if ($Size -gt 1MB) { return "{0:n1} MB" -f ($Size / 1MB) }
    if ($Size -gt 1KB) { return "{0:n1} KB" -f ($Size / 1KB) }
    return '{0} B' -f $Size
}
human_readable 3424233</pre>

### Arrays

Collections (`@()`)sind die Standard-Array-Konstrukte in Powershell, welche einige lustige Eigenschaften haben:

*   werden in Einzelwerte (String/Zahl) umgewandelt, sobald nur noch ein Element enthalten ist. <span style="line-height: 1.5;">Das läßt sich umgehen, indem die Werte in </span>`@()`<span style="line-height: 1.5;"> eingefasst werden.</span>
*   <span style="line-height: 1.5;">sind nicht erweiterbar, b</span>ei der Verwendung des `+=` Operators wird eine Kopie des rechten Arrays angelegt (ineffizient). Es gibt keinen `-=` Operator, `Remove()` ist nicht anwendbar.

Besser: ArrayLists verwenden:

<pre>$Array = [System.Collections.ArrayList]@()
$Array.add(34, 'err')</pre>

Umwandlung eines Arrays in eine ArrayList:

<pre class="brush: powershell; title: ; notranslate" title="">$ArrayList = [System.Collections.ArrayList]$Array
</pre>

Array Typ feststellen

<pre>$Array -is [Array]
</pre>

Element aus ArrayList entfernen

<pre>$Arraylis.remove(<element>)
</pre>

Letztes Element

<pre>$Array[-1]</pre>

Alles ausser erstem Element

<pre>$Array[1..($Array.length -1)]</pre>

Alles ausser letzem Element

<pre>$Array[0..($Array.length -2)]</pre>

Array Operationen an Strings

<pre>[Char[]]'smhdw' -Join ', '   # > "s, m, h, d, w"
</pre>

### Hashtables (Dictionaries)

HashTables bestehen aus Key=Value Paaren.

Die Keys in Hash-Tables müssen nicht in Anführungszeichen gesetzt werden, String-Values allerdings schon. Komplexe Ausdrücke für Values müssen in `()` eingeschlossen werden. Key-value Paare müssen durch NewLines oder ';' voneinander getrennt werden. Beispiele:

<pre>$NewDict= @{
    StartNew = @{ EventID = 2; EntryType = 'Information' }
    Key2 = 'Val1 ...'
    Key3 = (Get-Date)
}</pre>

<span style="line-height: 1.5;">Abruf der Werte:</span>

<pre><span style="line-height: 1.5;">​$NewDict['StartNew']['EventID']</span> </pre>

Key - Wert anhand Value auslesen:

<pre class="lang-bsh prettyprint prettyprinted"><span class="pln">$Hashtable</span><span class="pun">.</span><span class="typ">GetEnumerator</span><span class="pun">()</span><span class="pun">|</span> <span class="pln">Where</span> <span class="pun">{</span> <span class="pln">$_</span><span class="pun">.</span><span class="typ">Value</span><span class="pun">-</span><span class="pln">eq</span> <span class="str">"True"</span><span class="pun">}</span></pre>

#### Hashtable Typ feststellen

<pre>$a -is [HashTable]</pre>

### PS Objekte

Siehe auch [Objekte, Piping, Selects](mks://localhost/Abteilungen/Entwicklung/Executive/Tools/Windows/Powershell/Programmierung/Ein-_und_Ausgabe#Objekte.2C_Piping.2C_Select "Abteilungen/Entwicklung/Executive/Tools/Windows/Powershell/Programmierung/Ein-_und_Ausgabe#Objekte.2C_Piping.2C_Select").

## Special variables
see https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_automatic_variables?view=powershell-5.1


## Special variables
see https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_automatic_variables?view=powershell-5.1

Check:

    * `$Args`: array of the undeclared parameters and/or parameter values that are passed to a function, script, or script block
    * `$Error`: array of error objects that represent the most recent errors
    * `$Foreach`: enumerator (not the resulting values) of a ForEach loop
    * `$Input`: enumerator that enumerates all input that is passed to a function
    * `$LastExitCode`: exit code of the last Windows-based program that was run.
    * `$Matches`: works with the -match and -notmatch operators. When you submit scalar input to the -match or -notmatch operator, and either one detects a match, they return a Boolean value and populate the $Matches automatic variable with a hash table of any string values that were matched
    * `$MyInvocation:`: PSScriptRoot, PsCommandPath
    * `$PsBoundParameters`: dictionary of the parameters that are passed to a script or function and their current values
    * `$PsCommandPath`: full path and file name of the script that is being run
    * `$Psitem`: current object in the pipeline object
    * `$PsScripRroot`: directory from which a script is being run.
    * `$Pwd`: path object that represents the full path of the current directory
    * `$StackTrace`: stack trace for the most recent error.


## Filter
See [4sysops introduction](https://4sysops.com/archives/the-powershell-filter-2/) - for bigger
data, use `PROCESS` construct over `foreach($File in $INPUT) {...}`. The `PROCESS` construct
works comparable to python `yield`.


* slow function example, collecting all data first
```
function myFunction {
    ForEach ($File in $Input) {
         $File
    }
}
Get-ChildItem C:\ -Recurse -ErrorAction SilentlyContinue | myFunction
```

* matching filter construct (much faster) - the filter instantly produces output
```
function myFilter {
    PROCESS {
        $PSItem
    # bla bla then "break"
    }
}
Get-ChildItem C:\ -Recurse -ErrorAction SilentlyContinue | myFilter
```

* example xml filter(runs for each pipe object)
```
function Import-CimXml {
    BEGIN{
        $Collector = @{}
    }

    PROCESS {
        # Create new object from xml input, linewise
        $CimXml = [Xml]$PSItem

        # Iterate over the data and pull out just the value name and data for each entry
        $Collector.Add(
            $CimXml.SelectNodes("/INSTANCE/PROPERTY[@NAME='Name']").Value,
            $CimXml.SelectNodes("/INSTANCE/PROPERTY[@NAME='Data']").Value
        )
    }
    END{
        return New-Object PSObject -Property $Collector
    }
}
$WmiVM.GetRelated("Msvm_KvpExchangeComponent").GuestIntrinsicExchangeItems | Import-CimXML
```
