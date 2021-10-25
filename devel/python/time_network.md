# get default gateway

    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                # If not default route or not RTF_GATEWAY, skip it
                continue

            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))




# get time from ntp server (fast!)


    from socket import AF_INET, SOCK_DGRAM
    import socket
    import struct
    import time

    def getNTPTime(host = "de.pool.ntp.org"):
        """get ntp time in epoch seconds """


        port = 123
        buf = 1024
        address = (host,port)
        msg = '\x1b' + 47 * '\0'

        # reference time (in seconds since 1900-01-01 00:00:00)
        TIME1970 = 2208988800 # 1970-01-01 00:00:00

        # connect to server
        client = socket.socket( socket.AF_INET, socket.SOCK_DGRAM)
        client.sendto(msg.encode('utf-8'), address)
        msg, address = client.recvfrom( buf )

        t = struct.unpack( "!12I", msg )[10]
        return t - TIME1970

    offset = getNTPTime() - time.time())

# retrieve established tcp connections

    def list_established_connections():
        with open('/proc/net/tcp', 'r') as proc_net:
            for line in proc_net.readlines()[1:]:
                s = line.split()[1:4]
                yield s[0].split(':') + [s[2]] # local add/port only

    for hex_addr, hex_port, state in list_established_connections():
        if int(state, 16) is 1:
            # split hex address into octets
            ip_octets = []
            while hex_addr:
                ip_octets.insert(0, str(int(hex_addr[:2], 16)))
                hex_addr = hex_addr[2:]

            # concentate ip, convert hex port
            print('.'.join(ip_octets), int(hex_port, 16))
