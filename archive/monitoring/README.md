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
* master/ slave connection
* state: running and responding to network request
* backup/dump outdated
* expired certificates
* load per service
* network traffic per service
* info: Software version, manufacturer
