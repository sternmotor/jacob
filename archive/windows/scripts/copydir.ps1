
function Copy-Dir {
<#
.SYNOPSIS
    Copy big directories slowly enough to be easy on USB controlers

.DESCRIPTION
    This script copies small files via standard "copy-item" Cmdlet, but bigger
    files are streamed chunk-wise. This keeps USB drive controlers from 
    stalling when copying big files.

.PARAMETER Source
    Source directory to be copied into -Target directory, mandatory parameter.
    Hand over string or "get-item" object.

.PARAMETER Target
    Directory where -Source directory is beeing copied into, mandatory 
    parameter.  Hand over string or "get-item" object.

.PARAMETER ChunkSize
    The size of buffer to use when copying the stream for big files
    Use a larger buffer to reduce progress indicator refresh interval and 
    potentially speed up copying. If you encounter the error "Unable to 
    determine the identity of domain.", try a smaller value.

    Optional parameter, defaults to 200MB

.PARAMETER StreamLimit
    Minimum size of files to be streamed, smaller files are copyied via 
    "copy-item" (faster).

    Optional parameter, defaults to 10MB.

.EXAMPLE
    CopyDir d:\testsource\content d:\testtarget -verbose

.LINK
    Copy-Item
#>
    [CmdletBinding()]Param(
        [Parameter(mandatory=$True)]
        [String]$SourcePath,

        [Parameter(mandatory=$True)]
        [String]$TargetPath,

        [uint64]$SourceSize=0,

        [uint64]$ChunkSize = 200MB,
        [uint64]$StreamLimit = 10MB
    )

    # Verbosity and script robustness
    Set-StrictMode -version 5.0
    if ( -not $PSBoundParameters.ContainsKey('ErrorAction') ) { $ErrorActionPreference = 'Stop' }
    if ($DebugPreference -eq 'Inquire') {$DebugPreference = 'Continue'}     # no confirmation in debug mode
    if ($DebugPreference -eq 'Continue') {$VerbosePreference = 'Continue'}  # debug option forces verbose

    Write-Debug('Copying "{0}" into "{1}"' -f ($SourcePath, $TargetPath))

    $SourceDir = Split-Path $SourcePath -Leaf
    $SourceBaseDir=  Split-Path $SourcePath -Parent


    # progress meter parameters
    $ProgressID = Get-Random -Minimum 1
    $GlobalActivity = 'Copying "{0}" into "{1}"' -f ($SourceDir, $TargetPath)
    Write-verbose(' * Starting copy process')

    try{
        $StopWatch = [system.diagnostics.stopwatch]::StartNew()
        Write-GlobalProgress -Bytes 0
        Push-Location -Path $SourceBaseDir #-StackName CopyDir
        $BytesComplete = Copy-DirRecursion -Target $TargetPath
        $StopWatch.Stop()
        msg-info('Completed: {0:N1} GB in {3:N0} sec ({1:N0} MB/s = {2:N0} GB/h)' -f (
                ($BytesComplete / 1GB),
                ($BytesComplete / 1MB / $StopWatch.Elapsed.TotalSeconds),
                ($BytesComplete / 1GB / $StopWatch.Elapsed.TotalHours),
                $StopWatch.Elapsed.TotalSeconds
            )
        )
        Write-Progress -Activity "Copy completed successfully" -Completed -ID $ProgressID
        Pop-Location #-StackName CopyDir
    }
    catch{
        # leave target directory anyway
        Pop-Location #-StackName CopyDir
        throw $_
    }
}


function Copy-DirRecursion () {
<#
    $TargetPath: subdir or file
    $BytesComplete: size done
#>
	[CmdletBinding()]Param (
        [Parameter(mandatory=$True)][String]$Target,
        [String]$TargetBase = $Target, # default for first loop
        [uint64]$BytesComplete =0
    )
    Set-StrictMode -version 5.0

    # handle files
    foreach ($Entry in (Get-ChildItem '.' )) {

        # handle sub directory
        if (Test-Path $Entry.FullName -PathType Container) {

            # handle target directory
            $TargetEntry = [io.path]::combine($Target,$Entry)
            $Null = New-Item -ItemType Directory $TargetEntry -Force

            # step into source directory, start copy 
            Push-Location $Entry -StackName CopyDirRecursion
            $BytesComplete = Copy-DirRecursion -Target $TargetEntry -TargetBase $TargetBase -Bytes $BytesComplete
            Pop-Location -StackName CopyDirRecursion
        }

        # copy small single file 
        elseif ($Entry.length -le $StreamLimit) {
            #Write-Debug('SMALL file: "{0}" > "{1}"' -f $Entry, $TargetPath)
            Copy-Item $Entry $Target
            $BytesComplete += $Entry.length
        }

        # stream big single file
        else {
            Write-GlobalProgress $BytesComplete
            msg-info('Streaming big file: {0} > {1}' -f ($Entry, $TargetPath))
            $TargetEntry = [io.path]::combine($Target,$Entry)
            $StreamParam = @{
                SourcePath = $Entry.FullName
                DestinationPath = $TargetEntry
                #DestinationName = ($TargetEntry.replace($TargetBase,'').trimstart('\'))
                DestinationName = (shorten-path -Path $Entry.FullName)
                ProgressParentID = $ProgressID
                FileSize = $Entry.Length
            }
            Copy-Stream @StreamParam
            $BytesComplete += $Entry.length
        }

    }

    # all files handled - write current global progress
    Write-GlobalProgress $BytesComplete
    return $BytesComplete
}





<#see https://gallery.technet.microsoft.com/scriptcenter/Copy-Net-stream-data-using-a92cff37

$sourceStream = Open-FileStream "C:\Windows\memory.dmp"  
$destinationStream = Open-FileStream "C:\temp\old_memory.dmp" -FileMode OpenOrCreate -FileAccess ReadWrite  
$Stream = Copy-Stream $sourceStream $destinationStream -BufferSize 100mb -BufferFlushSize 50mb $sourceStream,$destinationStream
$Stream | Close-Stream -Dispose
#>

function Copy-Stream {
<#
.SYNOPSIS
    Copies one stream, such as a file, to another using buffered copying
    with progress indicators

.PARAMETER Source
    Source stream to copy data from
.PARAMETER Destination 
    Destination data stream to copy data to
.PARAMETER BufferSize
    The size of buffer to use when copying the stream.
    Use a larger buffer to reduce progress indicator refresh interval and potentially speed up copying.
    If you encounter the error "Unable to determine the identity of domain.", try a
    smaller value.
.PARAMETER BufferFlushSize
    Buffer threshold that if exceeded will cause the buffer to be explicitly flushed.
    If you encounter the error "Unable to determine the identity of domain.", try a
    smaller value. 

.EXAMPLE
    #Do a buffered file copy 
    sourceStream = Open-FileStream "C:\Windows\memory.dmp"
    $destinationStream = Open-FileStream "C:\temp\old_memory.dmp" -FileMode OpenOrCreate -FileAccess ReadWrite
    Copy-Stream $sourceStream $destinationStream -BufferSize 100mb -BufferFlushSize 50mb
    $sourceStream,$destinationStream | Close-Stream -Dispose

.NOTES
    Author: Tim Bertalot
#>

	[CmdletBinding()]Param (
        [Parameter(mandatory=$True)]
        [String]$SourcePath,

        [Parameter(mandatory=$True)]
        [String]$DestinationPath,

        [String]$DestinationName = $DestinationPath,

        [uint64]$BufferSize = 256MB,
		  
        [uint64]$BufferFlushSize = $BufferSize / 2,

        [Int]$ProgressParentID,
        [uint64]$ProgressCompleteSize,
        [uint64]$FileSize
    )

    # Verbosity and script robustness
    Set-StrictMode -version 5.0
    if ( -not $PSBoundParameters.ContainsKey('ErrorAction') ) { $ErrorActionPreference = 'Stop' }
    if ($DebugPreference -eq 'Inquire') {$DebugPreference = 'Continue'}     # no confirmation in debug mode
    if ($DebugPreference -eq 'Continue') {$VerbosePreference = 'Continue'}  # debug option forces verbose
          
    $Source = Open-FileStream $SourcePath
    $Destination = Open-FileStream $DestinationPath -FileMode OpenOrCreate -FileAccess ReadWrite  

    # determine file size if not given
    if(!$FileSize) {
        $FileSize = (Get-Item $SourcePath).length
    }

    $buffer = New-Object system.byte[] $BufferSize
    $bufferSinceFlush = 0
    $id = Get-Random -Minimum 0

    if (!$Source.CanRead) {
        throw "Cannot read from source stream"
    }
    elseif ($Source.Length -eq 0) {
        throw "The source stream is empty"
    }
    if(!$Destination.CanWrite) {
        throw "Cannot write to destination stream"
    }


    #For a FileStream type, the typical case would be to
    #have the copy done start to finish so the file pointers
    #need to be set to the beginning of the respective streams
    $Source.Position      = 0
    $Destination.Position = 0

    $ProgressParams = @{
        ID       = Get-Random -Minimum 1
        Activity = 'Streaming "{0}"' -f $DestinationName
        ParentID = $ProgressParentID 
    }

    try{
        #for a FileStream type, this will effectively delete the
        #contents of the file. 
        if ($Destination.SetLength) {
            $Destination.SetLength(0)
        }

        $BytesRead = 0;
              
        $totalChunks = [math]::Ceiling($Source.Length / $BufferSize)
        
        do {
            $thisChunk      = [math]::Ceiling(($Source.Position + 1) / $BufferSize)

            # update progress meter
            $StepProgressParams = @{
                PercentComplete = $thisChunk / $totalChunks * 100
                Status = 'Completed {0:N1} GB / {1:N1} GB' -f (($Source.Position / 1GB), ($FileSize / 1GB))
            }
            Write-Progress @ProgressParams @StepProgressParams


            $BytesRead = $Source.Read($buffer,0,$bufferSize)
            if ($BytesRead -gt 0) {
                $Destination.Write($buffer,0,$BytesRead);

                #If we meet or exceed the $BufferFlushSize, it causes a buffer flush
                if ($bufferSinceFlush -ge $BufferFlushSize) {
                    $Destination.Flush()
                    $bufferSinceFlush = 0
                }

                else {
                    $bufferSinceFlush += $Source.Length
                }
            }

            else {
                $Destination.Flush();
            }
            start-sleep 1
        } while ($BytesRead -gt 0) 

        # close streams
        $Source, $Destination| Close-Stream -Dispose
    } 
    catch {
        # close streams
        $Source, $Destination| Close-Stream -Dispose
        throw $_
    }

    Write-Progress @progressParams -Completed
}

function Open-FileStream {
<#
.SYNOPSIS
    Opens a .Net FileStream
    
.PARAMETER FileMode
    Any option from the enumeration System.IO.FileMode which indicates the
    file mode.
    The default is "Open" which will only open existing files, not create the file on your behalf. 
.PARAMETER FileAccess
    An option from the System.IO.FileAccess enum that indicates whether the 
    filestream should be opened for reading and/or writing.  
    The default is read only.

.EXAMPLE
    $sourceStream = Open-FileStream "C:\Windows\memory.dmp"
    $destinationStream = Open-FileStream "C:\temp\old_memory.dmp" -FileMode OpenOrCreate -FileAccess ReadWrite
    Copy-Stream $sourceStream $destinationStream -BufferSize 100mb -BufferFlushSize 50mb
    $sourceStream,$destinationStream | Close-Stream -Dispose

.OUTPUTS
    [System.IO.FileStream]

.NOTES
    Author: Tim Bertalot
#> 
	
	[CmdletBinding(  
		SupportsShouldProcess   = $true,
		ConfirmImpact           = "Low",
		DefaultParameterSetName = ""
	)]
	
	[OutputType([System.IO.FileStream])] #OutputType is supported in 3.0 and above
	 
	param
	(
		[Parameter(
			HelpMessage						= "Enter the path of the file to open",
			Mandatory                       = $true,
            Position						= 0,
			ValueFromPipeline				= $true,
			ValueFromPipelineByPropertyName = $true
	  	)]
		[ValidateNotNull()]
        [Alias("FullName")]
		[System.IO.FileInfo[]]
		$Path,

        [ValidateNotNull()]
        [System.IO.FileMode]
        $FileMode = [System.IO.FileMode]::Open,
		
		[ValidateNotNull()]
        [System.IO.FileAccess]
        $FileAccess = [System.IO.FileAccess]::Read,

        [ValidateNotNull()]
        [System.IO.FileShare]
        $FileShare = [System.IO.FileShare]::Read
	)
    

	begin {
Set-StrictMode -version 5.0
	
	}
	
	process {
		foreach ($item in $Path) {
            if ($PSCmdlet.ShouldProcess("$item.FullName","Open as $FileAccess")) {
                new-object System.IO.FileStream $item.FullName,$FileMode,$FileAccess,$FileShare
            }
		}
	}
	
	end {
		
	}
}



function Close-Stream {
<#
.SYNOPSIS
    Flushes and closes a .Net stream

.PARAMETER Stream
    Dot Net stream to close
.PARAMETER Dispose
    Switch for finishing the stream cleanup by calling dispose
.PARAMETER PassThrough
    Indicates that the stream should be returned and the caller
    will handle the unmanaged resource disposal.

.EXAMPLE
    $sourceStream = Open-FileStream "C:\Windows\memory.dmp"
    $destinationStream = Open-FileStream "C:\temp\old_memory.dmp" -FileMode OpenOrCreate -FileAccess ReadWrite
    Copy-Stream $sourceStream $destinationStream -BufferSize 100mb -BufferFlushSize 50mb
    $sourceStream,$destinationStream | Close-Stream -Dispose

.NOTES
    Author: Tim Bertalot
#>

	[CmdletBinding(  
        SupportsShouldProcess   = $false,
        ConfirmImpact           = "low",
        DefaultParameterSetName = ""
    )]

    param (
        [parameter(
            Mandatory         = $true,
            ValueFromPipeline = $true
        )]
        [ValidateNotNullOrEmpty()]
        [System.IO.Stream]
        $Stream,

        [switch]
        $Dispose,

        [Alias("PassThru")]
        [switch]
        $PassThrough
    )

    process {
    Set-StrictMode -version 5.0
        #there is no Open property, so making the assumption that if 
        #any of these are true, that the file is indeed open
        if ($Stream.CanRead -or $Stream.CanSeek -or $Stream.CanWrite) {
            #if the stream has the standard methods available, 
            #which should always be the case 
            if ($Stream.Flush) { $Stream.Flush() }
            if ($Stream.Close) { $Stream.Close() }
            else { Write-Error "Stream cannot be closed as the method is not available" }
        }

        if ($Dispose -and $Stream.Dispose) {
            #Turn errors into non-terminating
            try { $Stream.Dispose() }
            catch { Write-Error "Unable to dispose of stream resources" } 
        }
        elseif ($PassThrough) {
            #the caller still responsible for calling Dispose
            $Stream
        }
    }
}


function Write-GlobalProgress ($BytesComplete) {
    # helper: write progress message
    Set-StrictMode -version 5.0

    $PercentComplete = $BytesComplete / $SourceSize * 100
    $Message = 'Completed: {0:N1} GB / {1:N1} GB with {2:N0} MB/s (= {3:N0} GB/h)' -f (
        ($BytesComplete / 1GB), 
        ($SourceSize / 1GB),
        ($BytesComplete / 1MB / $StopWatch.Elapsed.TotalSeconds),
        ($BytesComplete / 1GB / $StopWatch.Elapsed.TotalHours)
    )

    $ProgressParam = @{
        PercentComplete = [uint64][math]::min(100,$PercentComplete)
        ID = $ProgressID
        Activity = $GlobalActivity
        Status = $Message
    }
    Write-Progress @ProgressParam
}


function shorten-path([String]$Path, [uint64]$Length=5, [String]$Sep='\') {
    # take a path and limit each path element to three characters except the last one
    Set-StrictMode -version 5.0

    $Entry = Split-Path $Path -Leaf
    $ParentDir =  Split-Path $Path -Parent

    $ShortElements = foreach ($Element in $ParentDir.split($Sep)) {
        try {
            # provoke index error in case element is shorter than length
            $Null = $Element[0..($Length -1)] 
            
            # build new element name
            ($Element[0..($Length-3)] -Join '') + '..'
        }
        catch{
            $Element
        }
    }
    return Join-Path ($ShortElements -Join $Sep) $Entry
}


# copy via robocopy
function RoboCopyDirRecursion($Path, $TargetBase, $LogFile) {
<#
Motivation for this script: https://answers.microsoft.com/en-us/windows/forum/windows_7-hardware/usb-drive-disconnect-during-large-transfer-also/95edcf8e-3bc8-4e35-befd-9850aa5224d2


$Source = 'D:\Backup\USB-Disks\USB Server HYPERV1 Disk\hyperv1.mds.local\2018-03-08_13-01-08'
$Target = 'D:\Backup\USB-Disks\USB Rotation Disk 003 HYPERV1\hyperv1.mds.local\1x'
Copy-Dir $Source $Target


Runs robocopy in unbuffered mode, directory-wise (for progress notifcations)
    $Path: subdir or file
    $Complete: size done
#>

    # copy this dir non-recursive
    $RelPath = $Path | resolve-path -Relative
    $TargetPath = Join-Path $TargetBase $RelPath
    $Null = New-Item -ItemType Directory -Path $TargetPath -Force
    msg-info('Directory "{0}"' -f $RelPath)
    $Null = robocopy  "$RelPath" "$TargetPath" /NDL /NFL /SEC /PURGE /Z /J /R:1 /W:1 /UNILOG+:$LogFile
    if($LastExitCode -gt 8){
        throw('Robocopy exited with bad exit code {0}' -f $LastExitCode)
    }
    else {
        Start-Sleep -MilliSeconds 200

        # handle directory entries
        $SubDirs = Get-ChildItem -Directory $Path
        foreach ($Dir in $SubDirs) {
            RoboCopyDirRecursion $Dir.FullName $TargetBase $LogFile
        }
    }
}


function Get-DirSize([String]$Path) {
    ## determine source file size (local only)- maybe faster?
    #$ComFS = New-Object -comobject Scripting.FileSystemObject
    #$SourceSize = [uint64]$ComFS.GetFolder('.').size

    # determine source file size (works on UNC path)
    $DirInfo = Get-ChildItem $Path -Recurse | Measure-Object -Property Length -Sum
    return $DirInfo.Sum
}



