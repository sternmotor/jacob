# id and mem
name        = 'cpu'
memory      = 300      # MB

# network devices
vif         = [
    'vifname=cputestdelme0,bridge=bdmz',
    #'vifname=cputestdelme1,bridge=blan',
    #'vifname=cputestdelme2,bridge=bgate',
]

# disc drives
disk        = [
    'phy:/dev/vg0/cputestdelme-root,sda1,w',
    'phy:/dev/vg0/cputestdelme-usr,sda2,w' ,
    'phy:/dev/vg0/cputestdelme-var,sda3,w' ,
    'phy:/dev/vg0/cputestdelme-tmp,sda4,w' ,
    'phy:/dev/vg0/cputestdelme-swap,sda5,w',
    #'phy:/dev/vg0/cputestdelme-srv,sdd1,w',
]

# set to 0 to disable ext3 or drbd check
check_discs = 1

#cpus = '^0'
#vcpus = '7'

# execute initial check functions, set up kernel 
#execfile( "/etc/xen/scripts/start-vm" )

# ---------------------------------------------------------------------------
# COMMON XEN OPTIONS
# ---------------------------------------------------------------------------

on_poweroff = "destroy"
on_reboot   = "restart"
on_crash    = "restart"
root        = "/dev/sda1"
extra       = "console=/dev/tty1 xencons=tty"


# ---------------------------------------------------------------------------
# MAIN SCRIPT
# ---------------------------------------------------------------------------


DEBUG_MODE = False


import sys 
import os.path
prog_name = os.path.basename(sys.argv[0])
if not DEBUG_MODE and not prog_name == 'xm':
    raise StandardError( "Script is not called via 'xm' command - please make sure " 
        "this script is invoked from an xm_config which is enabled " 
        "to deal with the helper functions defined here. "
        "See examples in /etc/xen/scripts/start-vm (bottom of file)."
    )


# do all checks only at domain start up ...

start_mode = DEBUG_MODE and 'create' or sys.argv[1]

if start_mode == 'create':

	# initialize script
	import pt.virt.xen.vmstart as vmstart
	error_counter = 0 	# 0 means: no errors

	class VmStartError(BaseException):
		"""Errors checking vm start prerequisites"""

	# kernel 
	print 'Setting Kernel Version:'
	kernel_rev  = vmstart.get_kernel_version	
	kernel      = "/boot/vmlinuz-%s"    % kernel_rev 
	ramdisk     = "/boot/initrd.img-%s" % kernel_rev 
		
	# vm running?
	print 'Vm State:'
	if vmstart.is_running(name):
		raise VmStartError ( "Vm '%s' is running, already!" % name )
	else:
		print "   Vm stopped (ok)"

	# vifs, bridges
	print 'Network Interfaces:'
	try:
		vmstart.check_vifs(vif)
	except VmStartException, emsg:
		print emsg
		error_counter += 1

	# drives
	print 'Disc Drives:'
	try:
		vmstart.check_discs(disk, check_disc)
	except VmStartException, emsg:
		print emsg
		error_counter += 1

	# cpus
	print 'Cpu Cores:'
	try:
		cpus, vcpus = vmstart.check_cpus(cpus, vcpus)
		print "Starting on %s of assigned cores %s" % ( vcpus, cpus )
	except VmStartException, emsg:
		print emsg
		error_counter += 1

	# mem
	print 'Memory'
	try:
		vmstart.check_mem()
	except VmStartException, emsg:
		print emsg
		error_counter += 1

	# finally start ... 
	if error_counter == 0:
			print "\n[OK] Looks good, starting domain %s" % name
	# or break on errors
	else:
		raise StandardError( "\nStart aborted." )
	
# and leave xen alone otherwise
else:
	pass





raise BaseException
#-----------------------------------------------------------------------------
# xen starter functions for paravirtualized xen guests, usage examples:
# /etc/xen/xen-start-examples
#-----------------------------------------------------------------------------

import os
import subprocess
import sys 


print sys.argv

#-----------------------------------------------------------------------------
# functions
#-----------------------------------------------------------------------------

# check if domain is running already
list = subprocess.Popen(
    [ "xm", "list", name ]              ,
    stdout = open( os.devnull, 'w' )    ,
    stderr = open( os.devnull, 'w' )    ,
)
if list.wait() == 0:
    raise StandardError( "Vm '%s' already running (check 'xm list')!" % name )


# kernel and init
kernel_rev = os.uname()[2]
try:
    kernel      = "%s-%s" % ( _kernel_pre, kernel_rev )
    ramdisk     = "%s-%s" % ( _initrd_pre, kernel_rev )
except NameError:
	pass


# network devices
print 'Network interfaces:'

def has_bridge(string):
    for item in string.split(','):
        if item.split('=')[0].strip() == 'bridge':
            return item.split('=')[1].strip()
    return False

for vif_def in vif:
    br =  has_bridge( vif_def )
    if br:
        print "   %s ..." % br,
        if os.system( " ip a s %s  > /dev/null 2>&1" %  br ) > 0:
            _error = True
            print "[EE] bridge '%s' does not exist!" % br
        else:
            print "ok"

# disc drives
def _check_ext3( os, disc_dev ):
    import subprocess
    fsck = subprocess.Popen(
        [ "/sbin/e2fsck", "-y", disc_dev ]  ,
        stdout = open( os.devnull, 'w' )    ,
        stderr = open( os.devnull, 'w' )    ,
    )
    ec  = fsck.wait()
    if ec == 8:
        # this ec is valid for mounted discs and for non-ext3 discs
        # check list of mounted devices
        lv = os.path.basename( disc_dev )
        vg = os.path.basename( os.path.dirname( disc_dev ) )
        mapper_disc_dev = "%s-%s" % ( vg, lv.replace( '-', '--' ) )
        for mount_line in open( '/etc/mtab', 'rw' ):
            if mapper_disc_dev in mount_line:
                # is mounted
                raise StandardError( "[EE] disc mounted in host system!" )
        else:
            print "No ext3 file system, skipping"
            return
 
    elif ec == 1 or ec == 2:
        print "2nd pass ...",
        fsck = subprocess.Popen(
            [ "/sbin/e2fsck", "-y", disc_dev ]  ,
            stdout = open( os.devnull, 'w' )    ,
            stderr = open( os.devnull, 'w' )    ,
        )
        ec  = fsck.wait()

    if ec == 0:
        print "ok"
        return
    else:
        _error = True
        print "[EE] error checking file system, ( e2fsck error code %s)" % ec
        return

print 'Disc Drives:'
for disc_def in disk:
    disc_type = disc_def.split(',')[0].split(':')[0].strip()
    disc_dev  = disc_def.split(',')[0].split(':')[1].strip()
    print "   %s ..." % disc_dev,
    # standard discs
    if disc_type == 'phy':
        if not os.path.exists( disc_dev ):
            _error = True
            print "[EE] disc device '%s' not found!" % disc_dev
        else:
            if check_discs == 1 or check_discs == '1':
                _check_ext3( os, disc_dev)
            else:
                print "present(ok), no check"

    # drbd devices
    elif disc_type == 'drbd':
        print "drbd device, skipping"
        continue
    elif disc_type == 'file':
    # check if file exists
        if not os.path.exists( disc_dev ):
            print "error: file '%s' not found!" % disc_dev
            _error = True
        else:
            print "file exists, ok"
    # other stuff
    else:
        print "unkown device type '%s',  error!" % disc_type
        _error = True


# available memory
print 'Memory:'
for line in os.popen( "xm info").readlines():
    if line.startswith('free_'):
        free_mem = line.split(':')[1].strip()
        break
print "   free mem: %sMB, need: %sMB ..." % ( free_mem, memory ),
if int(free_mem) - int(memory) > 0:
    print "ok"
else:
    print "[EE] not enough free mem!"
    _error = True


# final error handling
try:
    _error
except NameError:
    # no error defined
    print "\n[OK] Looks good, starting domain %s" % name
else:
    raise StandardError( "\nStart aborted." )

