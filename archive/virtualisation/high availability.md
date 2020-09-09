# High Availability

## Quorum

* CEPH: By default, two Ceph OSD Daemons from different hosts must report to the Ceph Monitors that another Ceph OSD Daemon is down before the Ceph Monitors acknowledge that the reported Ceph OSD Daemon is down

* DRBD: The basic idea is that a cluster partition may only modify the replicated data set if the number of nodes that can communicate is greater then the half of the overall number of nodes. A node of such a partition has quorum. On the other hand a node does not have quorum needs to guarantee that the replicated data set it not touched, that it does not create a diverging data set.
