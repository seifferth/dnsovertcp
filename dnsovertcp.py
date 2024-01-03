#!/usr/bin/env python3

import os, socket, struct
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

class DNSHandler(DatagramProtocol):
    timeout   = 3
    max_cache_size = 1500
    cache = {}

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
        cache   = self.cache
        timeout = self.timeout
        if len(cache) > self.max_cache_size:
            cache.clear()
        reqid   = data[:2]
        domain  = data[12:data.find(b'\x00', 12)]
        if domain in cache:
            return self.transport.write(reqid + cache[domain],address)
        sdata = b'%s\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00%s\x00\x00\x01\x00\x01' % (os.urandom(2), domain)
        sdata = struct.pack(b'>H',len(sdata)) + sdata
        rdata = self.resolv_by_tcp(sdata)
        if rdata:
            cache[domain] = rdata
        else:
            #No result for this domain
            list_domain = list(domain)
            i = domain[0]+1
            while i < len(domain):
               list_domain[i]='.'
               i += domain[i]+1

            print('DNSServer failed to resolve %s',''.join(list_domain[1:]))
            rdata = '\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00'
        self.transport.write(reqid + rdata, address)

if __name__ == '__main__':
    reactor.listenUDP(53, DNSHandler(),interface='127.0.0.1')
    reactor.run()
