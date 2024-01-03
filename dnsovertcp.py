#!/usr/bin/env python3

import os, sys, socket, struct
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

class DNSHandler(DatagramProtocol):
    timeout   = 3

    def resolv_by_tcp(self,data):
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        try:
            sock.settimeout(self.timeout)
            sock.connect(('127.0.0.1', 53))
            sock.send(data)
            data = sock.recv(512)
            if len(data) < 10:
                raise 'Failt to receive data'
            return data[4:]
        except (IOError,socket.error,Exception) as e:
            pass
        finally:
            if sock:
               sock.close()

    def datagramReceived(self, data, address):
        reqid   = data[:2]
        domain  = data[12:data.find(b'\x00', 12)]
        sdata = b'%s\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00%s\x00\x00\x01\x00\x01' % (os.urandom(2), domain)
        sdata = struct.pack(b'>H',len(sdata)) + sdata
        rdata = self.resolv_by_tcp(sdata)
        if not rdata:
            rdata = '\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00'
            print('DNSServer failed to resolve', domain, file=sys.stderr)
        self.transport.write(reqid + rdata, address)

if __name__ == '__main__':
    reactor.listenUDP(53, DNSHandler(),interface='127.0.0.1')
    reactor.run()
