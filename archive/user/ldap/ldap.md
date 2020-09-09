The RTC configuration is stored in the /etc/ldap/slapd.d/ directory. The slapd server's configuration can be modified by changing the configuration entries in the special RTC DIT cn=config with the tools in the ldap-utils package (ldapadd, ldapmodify, et cetera), but it is also possible to edit the files in the  /etc/ldap/slapd.d/ directory and restarting slapd.

# lesen
  * man ldapmodify
  * https://help.ubuntu.com/community/OpenLDAPServer
  * samba pdc: http://wiki.samba.gr.jp/mediawiki/index.php?title=How_to_build_Samba_PDC_(squeeze)


#################
ldapadd  = ldapmodify -a
-D bind to dn
-W prompt for password
-w use password on command line
-y use passwordfile 

olc=openldap config

# Syntax:
ldapmodify << CHANGE
dn: cn=Modify Me,dc=example,dc=com
changetype: modify
replace: mail
mail: modme@example.com
-
add: title
title: Grand Poobah
-
add: jpegPhoto
jpegPhoto:< file:///tmp/modme.jpeg
-
delete: description
-
CHANGE

# will replace the contents of the "Modify Me" entry's mail attribute with the value "modme@exam‐ ple.com",  add  a  title of "Grand Poobah", and the contents of the file "/tmp/modme.jpeg" as a jpegPhoto, and completely remove the description attribute.

changetype's
modify 
delete


The default RTC installation will create two DITs: the RTC DIT (cn=config) and a starter DIT (default: dc=WG.srservers.net)
###############################
configure RTC DIT / Basic setup
###############################

dpkg-reconfigure -plow slapd

/etc/ldap/ldap.conf
BASE    dc=example,dc=com
URI ldap://ldaps1.example.com/

# display cn=config:
ldapsearch -LLLQY EXTERNAL -H ldapi:/// -b cn=config

# add db indexes (run only once)
ldapmodify -QY EXTERNAL -H ldapi:/// << DB_INDEXES
dn: olcDatabase={1}hdb,cn=config
changetype: modify
add: olcDbIndex
olcDbIndex: uid eq
-
add: olcDbIndex
olcDbIndex: cn eq
-
add: olcDbIndex
olcDbIndex: ou eq
-
add: olcDbIndex
olcDbIndex: dc eq
DB_INDEXES


# create root passwd for use in olcRootPW
slappasswd -h {MD5}

ldapmodify -QY EXTERNAL -H ldapi:/// << INIT_VALUES
# set log level to stats etc, see http://www.rjsystems.nl/en/2100-d6-openldap-provider.php
dn: cn=config
changetype: modify
replace: olcLogLevel
olcLogLevel: stats
SE    dc=sr4,dc=srservers,dc=net
URI ldap://localhost/
dn: olcDatabase={1}hdb,cn=config
# data dir ldap dir is changed on the fly
# remove obsolete ldap data dir like
# # rm -rf /var/lib/ldap
replace: olcDbDirectory
olcDbDirectory: /srv/ldap

# set config root dn
dn: olcDatabase={0}config,cn=config
changetype: modify
replace: olcRootDN
olcRootDN: cn=admin,cn=config

# config root passwd
dn: olcDatabase={0}config,cn=config
changetype: modify
replace: olcRootPW
olcRootPW: {MD5}TRJlxLRlUq/W5i+izEzYBw==
INIT_VALUES

# add schemata's
# siehe auch http://wiki.ubuntuusers.de/OpenLDAP


ldapadd -QY EXTERNAL -H ldapi:/// -f /etc/ldap/schema/cosine.ldif
ldapadd -QY EXTERNAL -H ldapi:/// -f /etc/ldap/schema/inetorgperson.ldif
ldapadd -QY EXTERNAL -H ldapi:/// -f /etc/ldap/schema/nis.ldif 
ldapadd -QY EXTERNAL -H ldapi:/// -f /etc/ldap/schema/openldap.ldif 

#    # samba, zarafa ldif:
    #    aptitude install samba-doc
    #    zcat /usr/share/doc/samba-doc/examples/LDAP/samba.schema.gz > /etc/ldap/schema/samba.schema
    #    apt-get remove samba-doc
    mkdir tmp/ldif_output -p
    cd tmp

cat << CONVERT_CONF > schema_convert.conf
include         /etc/ldap/schema/corba.schema
include         /etc/ldap/schema/core.schema
include         /etc/ldap/schema/cosine.schema
include         /etc/ldap/schema/duaconf.schema
include         /etc/ldap/schema/dyngroup.schema
include         /etc/ldap/schema/inetorgperson.schema
include         /etc/ldap/schema/java.schema
include         /etc/ldap/schema/misc.schema
include         /etc/ldap/schema/nis.schema
include         /etc/ldap/schema/openldap.schema
include         /etc/ldap/schema/ppolicy.schema
include         /etc/ldap/schema/collective.schema
include         /etc/ldap/schema/zarafa.schema
CONVERT_CONF

# asc-compressed fuer /etc/ldap/schema/zarafa.schema
QlpoOTFBWSZTWQ3FILgAE3n_kdgwAEBE53_wP-f_8H____AEAABAAAhgCT99A15XMUFABEAAAoCnwjUm
po8oBoGEAADQyGQaAAADhppkYjCaYCGATTCMExMhpkaGgGp6EJioMmTTTCAADCAZAAAAh6lUyYExNMAm
BMTAAABMAAQRKTKTGqemoPSD1GjT0TQaADI9TQ9Q9T1NB6gRJE0ETEaJkZMplMmNDU0ek2SMhpkBoP7H
u5Zf-VDTAKnbd83Z5tOBmSIJSaCnUpE2McqxDXBVSitdNens04bdhOuyEjiMSeEh8koPOqhE96fQcl5-
Wc7J5i5T6svP6pjLGWenryxcz1z1tjH8keB3wKBDiHTGMIyEPRBCCFEZCRJEO8w4h54XO7u_P8Kq0Cfp
e9z8zQ6M68ayoMQq0saWveXlV9CieCieC2AcQI_BaAuDgNaXn2yUBc6vvBD4lA9YfJ9Dt9tBvhqMCt3p
9UKgyIQkk1M8AYi6jgRKBJhCJYx-rBjq9iZVaDJ1EsACAEEzZwCJRIJENbdlp3kDjRa2nIvyuVsbGeW4
w5Zy-Xz435mmcXiCJyrs_fB85mWYKnzpGFCEz4JWRpVo_WdUwzUJqCyD3uxWoUE0g6gYCaB32jPpYKxa
wiEEEkKLbnLZi07nZ2N7EO7f1F90N5ORvRD9QA7r7cTRp2d2DhERe0AwRbVWgsGUKLJV9d4KBGRCDIS5
xKJKg3GOHRQrbmwGKX30yoqeKKkgEijGRYkikSEjIyGHhBc1l768Ho8vD5_D5qWuwStaUPbIBIjJJAoE
ILUGRaUSIlSDJM1UKCnEpqqkmRcEMAhRZAalYoqAYISCAVagFJKJa1ACRi3EakKSQqqhShJMWTGPKtsN
FuB1cjywv23ZhrACyMFgJAjEUDZVfYRIEhChEDOIhtBBwiFUqbrAh9tlV4KJyq8QU2rPO9o0RRTBDda4
CWCIQgIRtagRLghhRJrcEMZGQJM6USjRRJ8AA5MA-4BPaIn4gh9gXUondNYCakzG_D3Ah9V0boFfbQkK
RJ8zkPQjd8VEo-QxcKhu-83qJuEuZ6qJFHIFyBDgomRrzATeFgtOQLXsLFQSENEr3pxBbAhfiC6mD-gL
ySwAHR6ZI5DZRKXCPyo9QJ9VjZyUTUF-AIdORk7ENjmtz3fTgldHwntqU_UCGx7YSEISSBCeCO8BN5RS
dIdGQdHPVRKBdF-tGjmAswnn7CUFoHM4bkbHcvoBCK_cdwIaDg_IEMkfWeALS9h5L5k0DeDA_EFpa5dM
mQIdabkpdQQ2BD8AE0WPb6_hcZ2UFShkKJEQhFIEFiRBgQWEInj6fSSTp8jIzLQ5Ao6j-mT7zC4MIOco
W43-kCARgCnb1umGCgbB44GO5rxHRN0F_Sby8CA6jMWN5261A6g5wcgbkIX_QDiXa2iNVEoCwu0IXprM
hbOgMv5aHQNzU3ZrcMhPKLJqBi-dUhnagNTmFHjLFqPnsUXYGUIhm8KXYfoQjYbya3DBlv4Ht74YJKBD
qles4FcMzv8PiHrrLtKcbUG-2pRfluNTXMFsgXLUjc-T7D0ELnzBuPcf8A2NjG7YrTwOVjMYdpwLu8N4
GFzBJsU9PaGFohtbLe-7bKZd4by7bt3E7ZsG-URtRTeUVKZCQDzAkDs53WwcCMI7QkITG8qxU2JzCB3P
5b-xgIZpxDxXwBRyBscsnkWEwNI5AviC3OfprJGyA7QhbkdRTZPpIZfKUy9i17Rou4C_oSuoEK7pUwci
_ZcOv5ltM18g4mvA8_2npudy7HxGAPTzLByOYwOkOO3AjRQRG7ucAmQceIdJpxxxCMCvI3mTwrQznRIJ
l1jyA9GXeF9GiiWXoCjEO8oaA9aU8juMw0MYhzNQaDfuObWx0dEI8SBRWhRrZyKOpC6O3LR4QKtLDQ2L
kxYrIlyxX2Gv1lguG8rBYR0NB32Z-hkesF2MnJdCTJLAlJfQTidshLfKvXQHk1DXoJg8Tq9sGBfoCrDD
z_Ho6Lu9EqQpY9asIjPYPn3nWAGeDqDoA2XpTIzzg7UMOZ4g5dwodUgV85wLFsE7SWoPRYSrwNxBkZCQ
hCRgxHkYAFwKN70kotpAAwaSweGdnA4q4ZghlxQoXDzXfqp1mv5fX7PFkN67EDgGsKE39jVQJKDlJTx5
Et2XxbSHdKYl8EDJIbkfU5mH7tDBBXpD3BxRgBT7IXDjKGoM9RCjNLrDptRsa97cLPkjk2wdHTB7alFH
x-fxtpfBei5Y4Z54KtgDPQALpfggOELAlnAW4Ahl0TeukSi1jLVuUXJk4Yt3R4k7GMBCqR3OkKfLQbgi
WS8EMW_lmNHaFYZQwg82SxUCwnvFKB4j0pkB2wP-9oIbg4nampE-Zc-oDJoSqDd2ukOOkvapVNFFB5Ht
siE7us3HvVfTZ1BPZgBEBBhgAAQFUBUBgQYYZBhgBmYAAYYBgICLTVEVP8XckU4UJANxSC4A


    slaptest -f schema_convert.conf -F ldif_output
    find .
    vi ./ldif_output/cn=config/cn=schema/cn={7}zarafa.ldif
    # change the lines at the top of the file (Remove the {xx} things, make it look like the following)
        dn: cn=zarafa,cn=schema,cn=config
        ...
        cn: zarafa
    # And Remove the following lines at the bottom of that file
        structuralObjectClass: olcSchemaConfig
        entryUUID: 506bb32c-c232-102e-81c9-e11e06f59dd0
        creatorsName: cn=config
        createTimestamp: 20100312145015Z
        entryCSN: 20100312145015.702589Z#000000#000#000000
        modifiersName: cn=config
        modifyTimestamp: 20100312145015Z
    ldapadd -x -D "cn=admin,cn=config" -f ./ldif_output/cn=config/cn=schema/cn={7}zarafa.ldif -W

    # das selbe nochmal mit ./ldif_output/cn=config/cn=schema/cn={6}samba.ldif



# cn=config anzeigen (alles andere ausgefiltert)
ldapsearch -LLLQY EXTERNAL -H ldapi:/// -b cn=config "(|(cn=config)(olcDatabase={1}hdb))"


# display cn=config with added schemas:
ldapsearch -LLLQY EXTERNAL -H ldapi:/// -b cn=config

# display admin passwords and dn entries
ldapsearch -LLLQY EXTERNAL -H ldapi:/// -b  cn=config  dn olcRootDN olcRootPW

###############################
configure Starter DIT / Basic setup
###############################


# create root passwd for use in olcRootPW
slappasswd -h {MD5}

# vorhandenen Starter DIT anpassen
ldapmodify -QY EXTERNAL -H ldapi:/// << STARTER_VALUES
dn: olcDatabase={1}hdb,cn=config
changetype: modify
# suffix
replace: olcSuffix
olcSuffix: dc=exchange,dc=secu-ring,dc=de
-
# root id für zarafa domain
replace: olcRootDN
olcRootDN: cn=admin,dc=exchange,dc=secu-ring,dc=de
-
# root pw für zarafa domain
replace: olcRootPW
olcRootPW: {MD5}TRJlxLRlUq/W5i+izEzYBw==
STARTER_VALUES

# Neuen DIT eintragen in db
mkdir /srv/ldap/exchange
chown openldap:openldap /srv/ldap/exchange
ldapadd -Y EXTERNAL -H ldapi:/// << STARTER_DIT
dn: olcDatabase=hdb,cn=config
objectClass: olcDatabaseConfig
objectClass: olcHdbConfig
olcDatabase: hdb
olcDbDirectory: /srv/ldap
olcSuffix: dc=exchange,dc=secu-ring,dc=de
olcAccess: {0}to attrs=userPassword,shadowLastChange by self write by anonymous auth by  dn="cn=admin,dc=exchange,dc=secu-ring,dc=de" write by * none
olcAccess: {1}to dn.base="" by * read
olcAccess: {2}to * by self write by dn="cn=admin,dc=exchange,dc=secu-ring,dc=de" write by * read
olcLastMod: TRUE
olcRootDN: cn=admin,dc=exchange,dc=secu-ring,dc=de
olcRootPW: {MD5}TRJlxLRlUq/W5i+izEzYBw==
olcDbCheckpoint: 512 30
olcDbConfig: {0}set_cachesize 0 2097152 0
olcDbConfig: {1}set_lk_max_objects 1500
olcDbConfig: {2}set_lk_max_locks 1500
olcDbConfig: {3}set_lk_max_lockers 1500
olcDbIndex: objectClass eq
STARTER_DIT


# Neuen Dit und admin user erstellen
# This base entry does not exist.Create it?
ldapadd -x -D cn=admin,dc=exchange,dc=secu-ring,dc=de -W << CREATE_BASE_ENTRY
# organisation
dn: dc=exchange,dc=secu-ring,dc=de
objectClass: dcObject
objectClass: organization
o: zarafa_secu-ring
dc: exchange
description: Tree root

# admin
dn: cn=admin,dc=exchnage,dc=secu-ring,dc=de
objectClass: simpleSecurityObject
objectClass: organizationalRole
cn: admin
userPassword: {MD5}TRJlxLRlUq/W5i+izEzYBw==
description: LDAP administrator
CREATE_BASE_ENTRY

# sicher stellen dass phpldapamdinconfig.php das admin pw enthaelt (bind pw)!


# Tree anzeigen:
ldapsearch -LLLQY EXTERNAL -H ldapi:/// -b dc=exchange,dc=secu-ring,dc=de
slapcat
