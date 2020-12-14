FROM php:7.4-fpm-alpine 
LABEL Maintainer="Traso GmbH admin team <adminteam@traso.de>" \
      Description="PHP 7.4 for xMID, xIBE and xRES development based on Alpine Linux"

# INSTALL

RUN set -e && \
echo "**** install build packages ****" && \
    apk add --no-cache --upgrade \
        freetype-dev \
        gmp-dev \
        icu-dev \
        libjpeg-turbo-dev \
        libpng-dev \
        libzip-dev \
        libxml2-dev \
        oniguruma-dev \
        postgresql-dev \
        $PHPIZE_DEPS \
    && \
echo "**** compile php modules ****" && \
    docker-php-ext-install -j$(nproc) \
        bcmath \
        gd \
        gmp \
        intl \
        opcache \
        pcntl \
        pdo_pgsql \
        soap \ 
        xmlrpc \
        zip \
    && \
echo "**** install xdebug ****" && \
    pecl install xdebug && \
    docker-php-ext-enable xdebug \
    && \
echo "**** install tools ****" && \
    curl -sS https://getcomposer.org/installer \
    | php -- --install-dir=/usr/local/bin --filename=composer && \
    apk add --no-cache --upgrade \
        git \
        fcgi \
        shadow \
    && \
echo "**** removing build packages ****" && \
    apk del --purge $PHPIZE_DEPS 
    
# CONFIG
COPY . /
RUN set -e && \
chmod 0750 /entrypoint.sh && \
chown 0:0  /entrypoint.sh

# DOCKER INTEGRATION
ENTRYPOINT ["/entrypoint.sh"]
CMD ["php-fpm"]
HEALTHCHECK --interval=30s --timeout=5s CMD cgi-fcgi -bind -connect 127.0.0.1:9000

# vim: set ft=sh:ts=4:sw=4:
