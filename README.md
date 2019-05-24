# Jacob

Jacob is "Just another Admin Cook Book" - a collection of snippets and some useful rules
for daily admin's work, centered on
* network infrastructure and devices
* servers: ubuntu linux and windows server
* monitoring: zabbix
* automatisation: ansible, puppet
* virtualization and high availability: hyperv, docker, drbd, cephalopods

## Markdown, Syntax

Write everything in [Github markdown style](https://help.github.com/articles/basic-writing-and-formatting-syntax)

### Code and Output

Three backticks: \`\`\`

* language specfications: bash, python, perl, posh, php
```markdown
    ```python
    import shutil
    ```
```

```python
import shutil
```

Code and output: put code and output into two code sections without any text in between (code is always preceded by a small text intrducing what the next lines do)
```markdown
    Convert time strings

    ```python
    import time
    import datetime
    a = 'Sun Jan  4 14:12:45 2009'
    datetime.datetime(*time.strptime( a )[0:6])
    ```

    ```bash
    2009-01-04 14:12:00
    ```


    Time object to seconds

    ```python
    time_iso.strftime( DateTimeObject )
    ```

    ```
    1231074720
    ```
```

### Key Strokes
Document key strokes as follows:

* CTRL-a = Control Key + simultaneously a
* CTRL-A = Control Key + SHIFT + a (all simultenously)
* CTRL-a a = Control Key + simultaneously a, release and press a again

### Document formatting

Table of contents

```markdown
## Table of Contents
[Headers](#headers)
[Lists](#lists)


<a name="headers"/>
## Headers

<a name="lists"/>
## Lists
```

Code


See above ... code sections must follow a short text or "edit `filepath`"
line. Thus it is possible to distinguish output section directly following
code from code listing itself, easily.

# Computer Wiki

## Content Overview
* Excel
* MathCad
* Solidworks
* Sketchup
* Word

# Admin Wiki

Collection of working and tested administration knowledge

## Content Overview
In each section, multiple languages may used (e.g. linux - you will find


* `automatisation`: ansible, puppet
* `database` mysql mssql administration incl. backup
* `devel`: bash python powershell snippets and programming guide
    * `bash` directory like python
    * `styleguide.md`: general scripting guide
    * `python`: python programming guides
        * `template`: module and script template
        * `data.md`: data and variables handling
        * `errors.md`: error- and exception handling
        * `functions.md`: functions and parameter handling, classes
        * `ifthenwhile.md`: control structures
        * `io.md`: input, output of files, text, sound
        * `proc.md`: processes, threads
        * `regexp.md`: regular expressions
        * `styleguide.md`: code formatting guide, python specific
        * `cli.md`: command line user interfaces / command line processing, verbosity setup
        * `config.md`: config file handling
    * `powershell` directory like python
* `email`: groupware, exchange, postfix, dovecot, ssl (link to web section), backup, contacts, calendar
* `equipment`: user stuff: phone, fax, printer, dsl provider, desktop hardware (see network)
* `linux`: very os-specific topics, small snippets (bash)
    * `antix`, `debian`, `fluxbox`, `ssh`, `gentoo`: big special topics
    * `backup.md`
    * `files.md`
    * `filesystem.md`: drbd, lvm, ext4, acl, encryption
    * `hardware.md`: udev, kernel options, hardware info
    * `logging.md`
    * `network.md`: ssh, netcat, tcpdump
    * `os.md`: init system, kernel, modules, service setup, chroot, hardening
    * `python` python administration guides for linux servers
        * link to python-programming
        * `backup.md`
        * `files.md`
        * `filesystem.md`: drbd, lvm, ext4, acl
        * `hardware.md`: udev, kernel options
        * `logging.md`
        * `os.md`: init system, kernel, modules, service setup, packages, upgrade
        * `network.md`: ssh, netcat
    	* `users.md` : users, groups, ad, ldap, kerberos
        * `time-date-units.md`
    * `shell, console, desktop`: Keyboard shortcuts, console configuration, user profile
    * `time-date-units.md`
* `macos`: very os-specific topics
    * `shell, console`: Keyboard shortcuts, console configuration
    * `desktop`: user profile
    * `filesystem.md`: permissions in file system
    * `shell, console, desktop`: Keyboard shortcuts, console configuration, user profile
* `monitoring`: zabbix, checkmk recipies
* `network`: bridging, vpns, triangle routing, firewalls, direct radio, wlan, ipv6
* `productivity`: setup and usage of desktop software and tools like putty, vim, filezilla, wget, jira, git, github, link to fluxbox
* `storage`: filesystems, sharing and storage: webdav, seafile, inotify sync, dfs, cephfs
* `team`: admin team work: best practices in dealing with problems and team work 
* `user`: rbac, user directories, active directory, identity management, kerberos, ldap, SSO
* `virtualisation`: docker, hyperv, xen, proxmox
* `web`: web servers, reverse proxy, ssl
* `windows`: very windows-specific topics (powershell, screenshots)
    * `backup.md`
    * `users.md` : users, groups, ad, kerberos
    * `files.md`
    * `filesystem.md`: ntfs, ntfs permissions, encryption
    * `hardware.md`: hardware info
    * `logging.md`
    * `os.md`: packages, chocolatey, service, environment
    * `network.md`: powershell winrm, rds, rdg
    * `time-date-units.md`
    * `shell, console, desktop`: Keyboard shortcuts, console configuration, user profile

### Corresponding GIT repositories
    * admin: top level of structure above
    * fluxbox
    * linux
    * windows
    * macos
    * scripts
    * seafile


## Style Guide

### Rules
* as far as possible, include system or application version under which code snippets have been tested

### Example names

* network: `example.net`
* servers:
    * `backend`: some server behind proxy or gateway
    * `gate`: gateway server(s) in dmz: proxies for mail, web, ssh, vpn
* users:
    * `Bernd Blast` = `BBL` = `bernd.blast`

## Github Extensions
Some projects which make this collection more Wiki-like:
* [Table of Contents](https://github.com/Mottie/GitHub-userscripts/wiki/GitHub-table-of-contents)
* [collapse markdown](https://github.com/Mottie/GitHub-userscripts/wiki/GitHub-collapse-markdown)
