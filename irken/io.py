import socket

class SimpleSocketMixin(object):
    address_family = socket.AF_UNSPEC
    socket_type = socket.SOCK_STREAM

    def __init__(self, *args, **kwds):
        super(SimpleSocketMixin, self).__init__(*args, **kwds)
        self.in_buffer = ""

    def send_raw(self, data):
        self.socket.sendall(data)

    def recv_raw(self):
        """Read IRC data from socket.

        This will not always result in a command being processed; an incomplete
        line could be received and thus be buffered and run when completed.

        Calling this can block if the underlying socket's `recv` doesn't return
        immediately, as would be the case if no data is ready.

        This will not decode any incoming data, as the IRC RFC defines byte
        values for protocol parsing.
        """
        data = self.socket.recv(1 << 12)
        if not data:
            raise IOError("connection closed")
        self.in_buffer = self.consume(self.in_buffer + data)

    def connect(self, address):
        host, port = address
        addresses = socket.getaddrinfo(host, port, self.address_family,
                                       self.socket_type, 0, 0)
        # TODO Attempt next somehow?
        for af, st, prot, cnam, addr in addresses:
            sock = socket.socket(af, st, prot)
            sock.connect(addr)
            self.socket = sock
            break
