====== Python Script Snippets ======

===== Script Structures, Error Handling =====
===== Data Structures and Logic, Math =====
===== Text Files, Unicode, Strings and Regexp =====
===== Filesystem, Date, Time =====
===== Config and Command Line Options =====
==== Config file comments ====

How to format comments, defaults and explanations for config file items
<file>
#
# Set config file format version.
#
ConfigFileVersion = "2.0"

#
# Enable or disable support for user profiles:
#
# 1: Enabled. The NX server allows the NX session to start
#    according to the set of rules specified for the system
#    or on a per-user basis.
#
# 0: Disabled. The NX server starts the session without apply-
#    ing any rules.
#
# The administrator can configure access to applications and nodes
# by creating a specific profile for the NX system, which will be
# applied to any user starting a session on this server, or by def-
# ining profiles on a per-user basis. Any profile consists of a set
# of rules specifying what the user can or can't do in the session.
#
#EnableUserProfile = "0"
</file>
===== Logging, Mail and Messages =====
===== System Command Execution =====
===== Daemon, Threads, Parallel Processing =====
===== Databases, Net, RPC, Users, Groups =====
