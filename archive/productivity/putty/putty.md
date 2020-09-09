# SSH


## Putty client setup


### Jumphost configuration

See [Bastion host setup](../ssh/bastion-host.md) - connecting to a Server behind a ssh relay/jump/bastion server may be set up like

* Check in CMD/Powershell if `plink.exe` is installed and executable in path (just enter `plink`)
* Configure Putty session
    * Session > Host Name `backend.example.net`
    * Session > Port 22
    * Connection > Data > Autologin username `proxy`
    * Connection > Proxy > Local
    * Connection > Proxy > Proxy hostname `ssh.fellowtech.com` 
    * Connection > Proxy > Port 22222
    * Connection > Proxy > Do DNS lookup "Yes"
    * Connection > Proxy > UserName `zabbix`
    * Connection > Proxy > Telnet command `plink -P %proxyport %user@%proxyhost -nc %host:%port`
    
    [Putty ProxyCommand Setup](putty-jumphost-config.jpg)
    
# TODO:
* Putty jump host screenshots