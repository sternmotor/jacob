# Monitoring Automatisation

## Self healing
* General cycle:
    * Automatisation configures Monitoring
    * Monitoring uses automatisation for fixing issues
    * Chatbot uses automatisation for fixing issues
* Links
    * https://www.lanline.de/cherwell-ki-automatisiert-service-prozesse
    * https://www.datacenter-insider.de/cherwell-bringt-kuenstliche-intelligenz-ins-service-management-a-710735/

## Monitoring Items

### Switches, Router

* List of connected macs for infrastructure mapping

### Devices
* `DeviceState`: Overall device state      
* `ConfigOptions`: Config errors     
* `PortStatus`: administrative status               
* `PortAlias`: for readiblity of monitoring events
* `PortTrafficOutbound`
* `PortTrafficInbound`
* `PortQueueLength`: Detect errors
* `PortPaketErrorsOutbound`
* `PortPaketErrorsInbound`
* `Info`: Version, Manufacturer, Firmware
* `Updates`: Detect missing updates
* `PowerConsumption`
* `Load`+ `RAM`

### Server OS
* `Backup`: outdated?
* `Reboot`: reboot required due to updates
* `Load`: mean of all cores and peak of single core
* `Traffic`
* `Logins`: active, offline, overall
* `Info`: version and name of os
* `Updates`: software updates missing (standard and security updates)
* `Free Storage`
* `Memory`, RAM + SWAP Usage

### Server hardware
* HD/ Fan/ PSU state
* Raid state


### Service Monitoring
* master/ slave / cluster connection
* ha elected master, quorum state
* state: running and responding to network request
* backup/dump outdated
* expired certificates
* load per service
* network traffic per service
* info: Software version, manufacturer



Monitoring Guidelines
---------------------

Don't alert if it doesn't die from it: If nobody needs to interact with the system as an "incident response" then this does not need to be alerted. May still be relevant for report
ing but this does not qulaify for a notification, in general.

Notification subject: make it easy readable, sortable and generally user-friendly - not debugging-friendly. Use OK / CRIT instead of PROBLEM / RECOVERY / FLAPPINGSTART / FLAPPINGSTOP

Split notification levels for 24/7 and office hour operation (only alert end-end errors 24/7, no component errors).

Monitoring sysztem requirements
------------------------
Proxies for sites, central server for management

Trend prediction - how long does this free disk space last and hysteresis - different limits for Problem and Recovery

Long time storage for reporting data and alerting data

Dashboard: 
* Groups and criticality/ number of failures in one spot
* Whats wrong with mails: error-prone - how to find the recovery mail for every problem?
