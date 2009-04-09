import socket

class SimpleSocketIO(object):
    address_family = socket.AF_UNSPEC
    socket_type = socket.SOCK_STREAM

    def __init__(self, *args, **kwds):
        super(SimpleSocketIO, self).__init__(*args, **kwds)
        self.in_buffer_segs = []

    def send(self, data):
        self.socket.sendall(data)

    def receive(self, target):
        """Read IRC data from socket into *target*.

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
        self.in_buffer_segs.append(data)
        self.in_buffer = target(self.in_buffer)

    def _in_buffer_get(self):
        self.in_buffer_segs = ["".join(self.in_buffer_segs)]
        return self.in_buffer_segs[0]
    def _in_buffer_set(self, val):
        self.in_buffer_segs = [val]
    in_buffer = property(_in_buffer_get, _in_buffer_set)

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
        return addr

import asynchat

class AsyncoreIO(asynchat.async_chat):
    address_family = socket.AF_UNSPEC
    socket_type = socket.SOCK_STREAM

    def __init__(self, consumer, *args, **kwds):
        asynchat.async_chat.__init__(self)
        self.consumer = consumer
        self.in_buffer = []

    def collect_incoming_data(self, data):
        self.in_buffer.append(data)

    def found_terminator(self):
        self.in_buffer = [self.consumer("".join(self.in_buffer))]

    def connect(self, address):
        self.create_socket(self.address_family, self.socket_type)
        return asynchat.async_chat.connect(self, address)
