PHP Administration
==================

Multi-Version Setup
-------------------

Centos 7 installation of multiple PHP versions, PHP 7.2 as default

* enable remi

        yum install -y epel-release yum-utils
        yum install -y http://rpms.remirepo.net/enterprise/remi-release-7.rpm
        

* install php versions

        for i in 72 73 74; do
            sudo yum-config-manager --enable remi-php$i
            sudo yum install -y php php-common php-fpm
            sudo yum install -y \
                php-bcmath \
                php-cli \
                php-gd \
                php-gmp \
                php-intl \
                php-json \
                php-mbstring \
                php-mcrypt \
                php-mysqlnd \
                php-opcache \
                php-pdo \
                php-pear \
                php-pecl-apc \
                php-pecl-memcache \
                php-pecl-memcached \
                php-pgsql \
                php-xml \
                php-xmlrpc \
                php-zstd

            sudo yum install -y php${i}-mod_php
            sudo ln -s /opt/remi/php73/root/lib64/httpd/modules/libphp7.so /etc/httpd/modules/libphp73.so
        done


* set default php version

        yum-config-manager --enable remi-php72

Check default version

    php -v
