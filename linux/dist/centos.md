# CentOS

## OS cleanup

    journalctl --vacuum-time=7d
    yum clean all
    package-cleanup -y --oldkernels --count=2
    package-cleanup --cleandupes
    # rpm --rebuilddb
    abrt-cli rm /var/spool/abrt/*
    yum install -y ca-certificates ssh bash
    yum --security -y update
    systemctl restart rsyslog


## Kernel

Restrict number of installed kernels to 2:

    if ! grep -q "installonly_limit=2" /etc/yum.conf; then
        echo "installonly_limit=2" >> /etc/yum.conf
    fi
    package-cleanup -y --oldkernels --count=2


Update Centos7 to UEK Oracle LTS kernel

```
cat << 'REPO_END' > /etc/yum.repos.d/uek-olx.repo
[ol7_UEKR6]
name=Latest Unbreakable Enterprise Kernel Release 6 for Oracle Linux $releasever ($basearch)
baseurl=https://yum.oracle.com/repo/OracleLinux/OL7/UEKR6/$basearch/
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-oracle
gpgcheck=1
enabled=1
REPO_END
curl -o /etc/pki/rpm-gpg/RPM-GPG-KEY-oracle https://yum.oracle.com/RPM-GPG-KEY-oracle-ol7
yum install https://yum.oracle.com/repo/OracleLinux/OL7/developer/UEKR6/x86_64/getPackage/linux-firmware-20200124-999.4.git1eb2408c.el7.noarch.rpm
yum install kernel-uek btrfs-progs btrfs-progs-devel
```

Update to mainline kernel

    sudo rpm --import https://www.elrepo.org/RPM-GPG-KEY-elrepo.org
    sudo rpm -Uvh http://www.elrepo.org/elrepo-release-7.0-3.el7.elrepo.noarch.rpm
    sudo yum --enablerepo=elrepo-kernel install -y kernel-ml


## Packages

Cleanup - recovers from several troubles

    yum clean all
    package-cleanup --cleandupes
    rpm --rebuilddb

Reinstall all packages (in case of interrupted yum run where libs have size "0")

    yum reinstall "*"


Fix bad mirror (example: `centos-gluster38`)

    yum install -y yum-utils --disablerepo=centos-gluster38
    yum-config-manager --save --setopt=centos-gluster38.skip_if_unavailable=true

Searching for a package with binary name

    yum whatprovides */ls

Installing epel package which cannot be found by `yum search <pkg>`

    yum --enablerepo=epel install ncdu

CentOS 8 Problem with outdated package repositories

    sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
    sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' \
    /etc/yum.repos.d/CentOS-*


## build rpm

install packages

    yum install -y rpmdevtools gcc gcc-c++ xz libtool make bzip2

set up directory structure like

    rpmbuild/
        BUILD
        BUILD/grub-2.04
        SOURCES
        SOURCES/grub-2.04.tar.gz
        SPECS
        SPECS/grub.spec
        SRPMS
        BUILDROOT
        BUILDROOT/grub-2.04-1.el7.x86_64
        RPMS

compile package into rpm: edit `rpmbuild/SPECS/grub.spec`

    Name:           grub
    Version:        2.04
    Release:        1%{?dist}
    Summary:        Grand Unified Bootloader for CentOS

    License:        GNU General Public License
    URL:            https://www.gnu.org/software/grub/index.html
    Source0:        grub-2.04.tar.gz

    BuildRequires:  gcc


    %description
    Installs boot loader to lvm volumes with no partition table. Static build.

    %prep
    %setup -q


    %build
    %configure --prefix='/' --target=x86_64 --disable-werror --with-platform=efi
    make  CHOST="x86_64-pc-linux-gnu" SHARED=0 CC='gcc -static' -j $(( $(nproc) + 1 )) || /bin/true


    %install
    rm -rf $RPM_BUILD_ROOT
    %make_install


    %files




## Network config

Server vmhost bridge for some VM

* edit `/etc/sysconfig/network-scripts/ifcfg-br1217`

    DEVICE=br1217
    ONBOOT=yes
    TYPE=Bridge
    BOOTPROTO=static
    NAME=br1217

* edit `/etc/sysconfig/network-scripts/ifcfg-vlan1217`

    VLAN=yes
    DEVICE=vlan1217
    PHYSDEV=team0
    VLAN_ID=1217
    BOOTPROTO=none
    ONBOOT=yes
    BRIDGE=br1217


* load networking - do not restart "networking" service on vmhosts!

    ifup vlan1217
    ifup br1217

Server VM

* edit `/etc/sysconfig/network-scripts/ifcfg-eth0`

    DEVICE=eth0
    IPV6INIT=no
    BOOTPROTO=static
    ONBOOT=yes
    IPADDR=192.168.103.27
    PREFIX=24
    GATEWAY=192.168.103.254

* reload networking

    systemctl restart network
    systemctl restart sshd
