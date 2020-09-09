# Apache Konfiguration


Maintenance page 

Page display is switched on by renaming html file from e.g. `maintenance-inactive.html` to `maintenance-active.html`
* Modul
```
a2enmod rewrite
```
* VHost
```
...
RewriteEngine On
# maintenance page in case it exists and client ips match
RewriteCond /var/www/website/maintenance-active.html -f
RewriteCond %{REQUEST_URI} !^/(maintenance-active.html)/
RewriteCond %{REMOTE_ADDR} !^(172\.31\.248\.13|172\.30\.1\.205)$
RewriteRule ^ /maintenance-active.html [L]
...
# RewriteCond %{REQUEST_URI} ^/$
```

Page itself may look like this simple html `<webroot>/maintenance-active.html`:
```
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
  <head>
    <title>Maintenance till 1 p.m.</title>
    <style>
        body {
            width: 60em;
            margin: 0 auto;
            font-family: Tahoma, Verdana, Arial, sans-serif;
            background-color: #272822;
            color: #F8F8F2;
        }
    </style>
    <meta name="msapplication-TileColor" content="#ffffff">
    <meta name="theme-color" content="#ffffff">
  </head>
  <body>
    <div>&nbsp;</div>
    <div>&nbsp;</div>
    <div>&nbsp;</div>
    <div>Das System steht aufgrund von Wartungsarbeiten bis 13 Uhr nicht zur
    Verf&uuml;gung. Wir bitten um Ihr Verst&auml;ndnis.</div>
    <div>&nbsp;</div>
    <div>Online system is currently being maintained. Please try again at 1 p.m. (CEST).</div>
  </body>
</html>
```
