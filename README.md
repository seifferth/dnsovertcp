# DNS over TCP

Transform the local dns udp requests to tcp requests. This script is based
on an earlier version found at <https://github.com/dsheng/dnsovertcp>.

`dnsovertcp.py` is a standalone python script that will listen on a
local udp port and forward all dns requests to an upstream dns server
via tcp. The default behaviour of `dnsovertcp.py` is to forward all dns
requests from localhost 53/udp to localhost 53/tcp. Both ports as well as
the upstream server's address can be overridden by command line arguments
(see `./dnsovertcp.py --help` for further information). Furthermore, you
could use a tool like `socat` to accommodate even more complex rerouting
schemes, or you could use `ssh -L` to forward all upstream dns requests
through an ssh tunnel.

To check whether this script is working as intended, you might want to run
something like

    dig @localhost DOMAIN

## License

This project is licensed under an MIT license. For more information,
see the `LICENSE` file.
