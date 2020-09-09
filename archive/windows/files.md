# Windows file handling
Grep
```
Get-Content "$InFilePath" | where {$_ -notmatch "$SearchString" } > "$OutFilePath"
```

Convert file to UTF8
```
$TempFile = [System.IO.Path]::GetTempFileName()
[System.Io.File]::ReadAllText($FileName) | Out-File -FilePath "$TempFile" -Encoding Utf8
mv "$TempFile" "$FileName"
```

Read binary file as base64
```
function alltogether{
 $SourcePath = (Resolve-Path "7345.19060.ashx.pdf").ProviderPath

 # test1: pipe
 $InputStream  = New-FileReadStream $SourcePath
 $OutputStream = New-FileWriteStream "out5.pdf"
 Convert-StreamToBase64 $InputStream 9000 | Convert-Base64ToStream -OutputStream $OutputStream -Verbose

 # test2: no pipe
 $InputStream  = New-FileReadStream $SourcePath
 $OutputStream = New-FileWriteStream "out5.pdf"
 $base64 = Convert-StreamToBase64 $InputStream 9000
 Convert-Base64ToStream $base64 -OutputStream $OutputStream -Verbose
}

function Convert-StreamToBase64($InputStream, [Int]$BufferSize=(3 * 256 *  1024)){
 # Read binary data from powershell $InputStream (e.g. Process.StandardOutput or file stream )
 # Convert this chunks to base64 ascii texts, write out single base64 strings

 $ReadBuffer = New-Object byte[] $BufferSize
 $Reader = New-Object System.IO.BinaryReader($InputStream)

 # run stream reader
 try{
  do {
   $BytesRead = $Reader.BaseStream.Read($ReadBuffer, 0, $BufferSize)
   [Convert]::ToBase64String($ReadBuffer, 0, $BytesRead) # output: base64string
  } while ($BytesRead -eq $BufferSize)
 }
 finally {
  $Reader.Close()
  $InputStream.Dispose()
 }
}

function Convert-Base64ToStream {
 # Read base64 ascii chunks, decode and write to binary $OutputStream
 # (e.g. Process.StandardInput or file stream )
 [CmdletBinding()]
 param(
  [Parameter( Mandatory = $True, ValueFromPipeline = $True)][String[]]$Base64Chunks,
  [Parameter( Mandatory = $True)]$OutputStream
 )
 BEGIN {
  $Writer = New-Object System.IO.BinaryWriter($OutputStream)
  $ChunkCounter=0
  $ByteCounter=0
 }
 PROCESS {
  foreach ($Chunk in $Base64Chunks) {
   try {
    $Bytes = [Convert]::FromBase64String($Chunk)
    $Writer.write($Bytes)
   }
   catch {
    # re-throw exception after cleanup
    $Writer.Close()
    $OutputStream.Dispose()
       throw $_
   }
   $ChunkCounter += 1
   $ByteCounter  += $Bytes.length
  }
 }
 END{
  $Writer.Close()
  $OutputStream.Dispose()
  Write-Verbose( "Wrote $ChunkCounter base64 chunks to given outputstream, length: $ByteCounter bytes")
 }
}

function New-FileReadStream($Path) {
 # Create stream source, here: open a single file for reading

    return New-Object System.IO.FileStream (
  "$Path", [IO.FileMode]::Open,
  [IO.FileAccess]::Read,
  [IO.FileShare]::Read
 )
}

function New-FileWriteStream($Path) {
 # Create stream target, here: open a single file for writing
 return New-Object System.IO.FileStream (
  $Path,
  [IO.FileMode]::Create,  # Create new file and open it for read and write
  [IO.FileAccess]::Write,
  [IO.FileShare]::None
 )
}
```
