# DNS over TCP

Transform the local dns udp requests to tcp requests. This script is based
on an earlier version found at <https://github.com/dsheng/dnsovertcp>.

`dnsovertcp.py` is a standalone python script that will listen on
localhost port 53/udp in order to forward all dns requests to localhost
port 53/tcp. To attach port 53/tcp to an actual dns server, you could
use a tool like `socat`, or you could use `ssh -L` to reroute all dns
requests through an ssh tunnel.

To check whether this script is working as intended, you might want to run
something like

    dig @localhost DOMAIN

## License

This project is licensed under an MIT license. For more information,
see the `LICENSE` file.
