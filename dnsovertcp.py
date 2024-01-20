#!/usr/bin/env python3

import os, sys, socket, struct
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from getopt import gnu_getopt as getopt

class DNSHandler(DatagramProtocol):
    def __init__(self, upstream: str='127.0.0.1', upstream_port: int=52,
                 timeout: int=3):
        self.upstream = upstream
        self.upstream_port = upstream_port
        self.timeout = timeout
        super().__init__()
    def resolv_by_tcp(self,data):
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        try:
            sock.settimeout(self.timeout)
            sock.connect((self.upstream, self.upstream_port))
            sock.send(data)
            data = sock.recv(512)
            if len(data) < 10:
                raise 'Failed to receive data'
            return data[4:]
        except (IOError, socket.error, Exception) as e:
            pass
        finally:
            if sock: sock.close()
    def datagramReceived(self, data, address):
        reqid   = data[:2]
        domain  = data[12:data.find(b'\x00', 12)]
        sdata = b'%s\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'\
                b'%s\x00\x00\x01\x00\x01' % (os.urandom(2), domain)
        sdata = struct.pack(b'>H',len(sdata)) + sdata
        rdata = self.resolv_by_tcp(sdata)
        if not rdata:
            rdata = b'\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00'
            print('DNSServer failed to resolve', domain, file=sys.stderr)
        self.transport.write(reqid + rdata, address)

_cli_help = """
Usage: dnsovertcp [-l PORT|-w TIMEOUT|-h] [DESTINATION [PORT]]

Positional Arguments:
    DESTINATION           Domain name or ip address of the upstream dns
                          server. (default: 127.0.0.1)
    PORT                  TCP port to connect to for dns requests against
                          the upstream server. (default: 53)
Further Options:
    -l PORT,              Local udp port to open for incoming dns requests.
        --listen PORT     (default: 53)
    -w TIMEOUT,           Maximum number of seconds to wait for the upstream
        --wait TIMEOUT    dns server to answer a query. (default: 3)
    -h, --help            Print this help message and exit.
""".lstrip()

if __name__ == '__main__':
    opts, args = getopt(sys.argv[1:], 'l:w:h', ['listen=', 'wait=', 'help'])
    listen_port = 53; timeout = 3; upstream = '127.0.0.1'; upstream_port = 53
    for k, v in opts:
        if k in ['-l', '--listen']:     listen_port = int(v)
        elif k in ['-w', '--wait']:     timeout = int(v)
        elif k in ['-h', '--help']:     print(_cli_help); exit(0)
    if len(args) > 2:
        print("Too many positional arguments", file=sys.stderr)
        exit(1)
    elif len(args) >= 1:
        upstream = args[0]
        if len(args) == 2: upstream_port = int(args[1])
    reactor.listenUDP(listen_port, DNSHandler(upstream = upstream,
                                              upstream_port = upstream_port,
                                              timeout = timeout),
                      interface='127.0.0.1')
    reactor.listenUDP(listen_port, DNSHandler(upstream = upstream,
                                              upstream_port = upstream_port,
                                              timeout = timeout),
                      interface='::1')
    reactor.run()
