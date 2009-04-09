import socket

class BaseSocketIO(object):
    address_family = socket.AF_UNSPEC
    socket_type = socket.SOCK_STREAM

    def connect(self, address):
        host, port = address
        addresses = socket.getaddrinfo(host, port, self.address_family,
                                       self.socket_type, 0, 0)
        # TODO Attempt next somehow?
        for af, st, prot, cnam, addr in addresses:
            self.make_socket(af, st, prot)
            self.connect_socket(addr)
            break
        else:
            raise ValueError("no address found for %r" % (address,))
        return addr

class SimpleSocketIO(BaseSocketIO):
    def __init__(self):
        self.in_buffer_segs = []

    def make_socket(self, af, st, prot):
        self.socket = socket.socket(af, st, prot)

    def connect_socket(self, addr):
        self.socket.connect(addr)

    def deliver(self, data):
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

import asyncore
import asynchat

class AsyncoreIO(BaseSocketIO, asynchat.async_chat):
    address_family = socket.AF_UNSPEC
    socket_type = socket.SOCK_STREAM

    def __init__(self, *args, **kwds):
        self.consumer = kwds.pop("consumer", None)
        asynchat.async_chat.__init__(self, conn=kwds.pop("conn", None))
        self.set_terminator("\n")
        super(AsyncoreIO, self).__init__(*args, **kwds)
        self.in_buffer = []

    def collect_incoming_data(self, data):
        self.in_buffer.append(data)

    def found_terminator(self):
        self.in_buffer = [self.consumer("".join(self.in_buffer))]

    def make_socket(self, af, st, prot):
        # NOTE Can't use create_socket because I want my prot set.
        self.socket = socket.socket(af, st, prot)
        self.socket.setblocking(0)
        self.set_socket(self.socket)

    def connect_socket(self, address):
        asynchat.async_chat.connect(self, address)

    def deliver(self, data):
        self.push(data)

    def receive(self, target):
        # This is sort of shady. :-)
        self.consumer = target
        self.run_forever()

    def run_forever(self):
        asyncore.loop()

    def handle_error(self):
        raise
