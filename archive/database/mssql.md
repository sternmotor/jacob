# MS SQL Administration


Connect to local system database (SQL Management Object):

```Powershell
$null = [System.Reflection.Assembly]::LoadWithPartialName("Microsoft.SqlServer.Smo")
$sqlServer = new-object ("Microsoft.SqlServer.Management.Smo.Server")"(local)"
```

Query backups sessions

*   Name: `$sqlDatabase.name`
*   Letzte Sicherung: `$sqlDatabase.LastBackupDate`
