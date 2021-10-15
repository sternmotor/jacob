Galera Cluster Operation
========================


Set up replication
------------------ 

Pre-requisites

* Timeout 0 for mariadb service (`systemctl edit mariadb`)

	[Service]
	TimeoutSec=0

* Configs for cluster members: edit `/etc/my.cnf.d/galera.cnf`

	[galera]
	binlog_format=ROW
	default_storage_engine=innodb
	innodb_autoinc_lock_mode=2
	bind-address=0.0.0.0
	wsrep_on=ON
	wsrep_provider=/usr/lib64/galera/libgalera_smm.so
	wsrep_cluster_address="gcomm://10.22.5.4,10.22.5.5,10.22.5.6"

	## Galera Cluster Configuration
	wsrep_cluster_name="maria.example.com"

	## Galera Synchronization Configuration
	wsrep_sst_method=rsync

	## Galera Node Configuration
	wsrep_node_address="10.22.5.5"
	wsrep_node_name="maria05.example.com"

	# Optional setting
	wsrep_slave_threads=12

	# activate myisam replication
	wsrep_replicate_myisam = 1

Repair cluster
--------------

Master data must be  available on one server (backup). Check out [this][der_bode]

1. find last active member of cluster (new master) or recover from backup (see step 3)

	mysql -u root -Bse "show status like 'wsrep_last_committed';"

2. shut down all cluster members
3. disable cluster operation on master: edit `/etc/my.cnf.d/galera.cnf`

	wsrep_cluster_address="gcomm://"

4. enforce master data status on master:

	sed 's/^safe_to_bootstrap.*/safe_to_bootstrap: 1/' */var/lib/mysql/grastate.dat

5. start master

	galera_new_cluster # or "systemctl start mariadb" - this has been tested
	# wait
	systemctl stop mariadb

6. re-configure master for cluster operation: edit `/etc/my.cnf.d/galera.cnf`

	wsrep_cluster_address="gcomm://<server1><server2><server3>"


	systemctl start mariadb
	journalctl -fu mariadb
    mysql -Bse "SHOW STATUS LIKE 'wsrep%'"

7. re-initialise other galera nodes


	rm -f /var/lib/mysql/ib_logfile* /var/lib/mysql/grastate.dat /var/lib/mysql/GRA*.log
	systemctl start mariadb
	journalctl -fu mariadb
	

[der_bode]: https://www.der-bode.de/recover-eines-mariadb-galera-cluster
