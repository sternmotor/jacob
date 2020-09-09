# Linux python networking


Get hostname (plain/fqdn)
```python
import socket
socket.gethostname()
socket.getfqdn()
```

Determine if Ipv4 IP is public or private
```python
import struct       # for is_internal_ip
import socket       # for is_internal_ip

def is_private_ipv4(ip):
    """
    see http://stackoverflow.com/questions/691045/how-do-you-determine-if-an-ip-address-is-private-in-python
    using http://tools.ietf.org/html/rfc1918 and
     http://tools.ietf.org/html/rfc3330. If you have 127.0.0.1 you just need
     to & it with the mask (lets say 255.0.0.0) and see if the value matches
     any of the private network's network address. So using inet_pton you can
     do: 127.0.0.1 & 255.0.0.0 = 127.0.0.0
    """
    f = struct.unpack('!I',socket.inet_pton(socket.AF_INET,ip))[0]
    private = (
        [ 2130706432, 4278190080 ], # 127.0.0.0,   255.0.0.0   http://tools.ietf.org/html/rfc3330
        [ 3232235520, 4294901760 ], # 192.168.0.0, 255.255.0.0 http://tools.ietf.org/html/rfc1918
        [ 2886729728, 4293918720 ], # 172.16.0.0,  255.240.0.0 http://tools.ietf.org/html/rfc1918
        [ 167772160 , 4278190080 ], # 10.0.0.0,    255.0.0.0   http://tools.ietf.org/html/rfc1918
    )
    for net in private:
        if (f & net[1] == net[0]):
            return True
    return False
```
