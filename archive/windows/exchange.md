# Mail, Exchange Handling

## Email Client
```
function Send-MyMail{
    # send-backupmail "test3" "tesstmessage"
    Param(
        [String]$Subject,
        [String]$Message,
        [String]$Attachment,
        [String[]]$Receivers=@('user@company.com'),
        [String]$SMTPAddr = 'mailrelay.company.com',
        [String]$SMTPUser = 'relay_user',
        [String]$SMTPPass = 'xxx',
        [String]$SMTPPort = 587,
        [Switch]$StartTLS = $False
    )

    Set-StrictMode -version 2.0

    # assemble mail system parameters
    $MailSystemParams = @{
        SmtpServer = $SMTPAddr
        Credential = New-Object System.Management.Automation.PSCredential(
            $SMTPUser,
            ($SMTPPass | ConvertTo-SecureString -asPlainText -Force)
        )
        Port = $SMTPPort
        Encoding = [System.Text.Encoding]::UTF8
        UseSSL = $StartTLS
    }

    $MailMessageParams = @{
        To = $Receivers
        From = $Sender
        Subject = $Subject
        Body = $Message
        BCC = 'developer@company.com'
    }

    # send mail
    if($Attachment) {
        Send-MailMessage @MailMessageParams @MailSystemParams -Attach $Attachment
    }
    else {
        Send-MailMessage @MailMessageParams @MailSystemParams
    }
}
```

# other
Einfache SMTP Mail ohne Authentifizierung, der Body-Text wird aus zeilenweise angegebenen Array-Elementen zusammengesetzt.

Powershell 2.0

<pre># establish mail server connection
function Create-SmtpClient( [String]$Server, [Int]$Port=25, [Boolean]$UseSSL=$False, [String]$Username=$Null, [String]$Password=$Null ) {
    # Initialise .NET Mailer
    $SMTPClient = New-Object Net.Mail.SmtpClient($Server, $Port)
    $SMTPClient.EnableSSL = $UseSSL
    if ( $Username ) {
        $SMTPClient.Credentials = New-Object System.Net.NetworkCredential($CredUser, $CredPassword)
    }
    return $SMTPClient
}
$SmtpClient = Create-SmtpClient mail.ft.local 25

# specify mail and send it
$EmailFrom = "Company IT Administration <admin@company.de>"
$EmailTo   = "someone@company.de"
$Subject   = "Test mail subject"
$Body    =  @(
    'Hello',
    'Some Message',
    '',
    'Kind regards',
    'your admin'
) -Join [Environment]::Newline
$SmtpClient.Send($EmailFrom, $EmailTo, $Subject, $Body)</pre>

Powershell 3.0+

<pre>$MailConnection = @{       
    SmtpServer = "mail.ft.local"
    Encoding   = [System.Text.Encoding]::UTF8
    # Port=[Int], UseSSL=[Boolean], Credential=[PSCredential], BodyAsHtml=[Boolean]
    # Credential:
    #$PasswordHash= ConvertTo-SecureString "PlainTextPassword" -AsPlainText -Force
    #$Credential = New-Object System.Management.Automation.PSCredential ("username", $PasswordHash)
}

$MailMessage = @{
    From    = "Company IT Administration <admin@company.de>"
    To      = "someone@company.de"
    Subject = "Test mail subject"
    Body    =  @(
        'Hello',
        'Some Message',
        '',
        'Kind regards',
        'your admin'
    ) -Join [Environment]::Newline
    # Cc, Bcc
}
Send-MailMessage @MailConnection @MailMessage</pre>

### Exchange

Accounts, die mindestens eine externe (nicht ....@pwc.local) Adresse haben (primär oder als alias)

<pre>foreach ($Mailbox in (Get-Mailbox)) {
    $Addresses = $Mailbox.EmailAddresses | where {$_.PrefixString -like 'SMTP' -and -not $_.AddressString.endswith('@pwc.local')}
    if ($Addresses) {
        New-Object PsObject -Property @{
            DisplayName = $Mailbox.DisplayName
            Addresses = (($Addresses | foreach {$_.AddressString} ) -join ';')
        }
    }
}
</pre>

MessageLog GridView:

<pre>Get-MessageTrackingLog | Out-Gridview
</pre>

List/Filter Mail Transport:

<pre>$Messages = Get-MessageTrackingLog -sender backup@tmrelo.local -resultsize unlimited | sort -property timestamp
# -sender
# -recipients
$Messages
$Messages | where EventID -eq deliverfail | fl *</pre>

Mitglieder einer dynamischen Verteilergruppe anzeigen

<pre>Get-DynamicDistributionGroup # zeigt alle dynamischen Verteiler

$Bernd = Get-DynamicDistributionGroup "Verteilername s.o."
Get-Recipient -RecipientPreviewFilter $Bernd.RecipientFilter</pre>

2008R2: Login auf Exchange Konsole aus Powershell heraus

<pre>. 'C:\Program Files\Microsoft\Exchange Server\V14\bin\RemoteExchange.ps1'
connect-exchangeserver -auto
</pre>

<div class="errormsg systemmsg" id="sessionMsg">

<div class="inner">

*   Funktioniert derzeit nur lokal, per Remoting funktioniert das Login nicht.

</div>

</div>
