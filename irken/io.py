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

class BufferSegmentStringer(object):
    def __init__(self, name):
        self.name = name

    def _get_target(self, instance):
        return getattr(instance, self.name)

    def __get__(self, instance, owner=None):
        target = self._get_target(instance)
        target[:] = ["".join(target)]
        return target[0]
        
    def __set__(self, instance, value):
        self._get_target(instance)[:] = [value]

class SimpleSocketIO(BaseSocketIO):
    def __init__(self):
        self.in_buffer_segs = []
        self.out_buffer_segs = []

    in_buffer = BufferSegmentStringer("in_buffer_segs")
    out_buffer = BufferSegmentStringer("out_buffer_segs")

    def make_socket(self, af, st, prot):
        self.socket = socket.socket(af, st, prot)

    def connect_socket(self, addr):
        self.socket.connect(addr)

    def deliver(self, data):
        self.out_buffer_segs.append(data)
        send_data = self.out_buffer
        n_bytes = self.socket.send(send_data)
        if not n_bytes:
            raise IOError("short write to endpoint")
        # Useless as send_data will always equivate to "" after the loop is
        # done. But it makes the code less "intra-reliant".
        remains = send_data[n_bytes:]
        self.out_buffer = remains
        return remains

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
            raise IOError("short read from endpoint")
        self.in_buffer_segs.append(data)
        self.in_buffer = target(self.in_buffer)

    def run(self, consumer):
        while True:
            while self.out_buffer:
                self.deliver(self.out_buffer)
            self.receive(consumer)

from select import select

class SelectIO(SimpleSocketIO):
    def deliver(self, data):
        self.interact(out=data)

    def receive(self, consumer):
        self.interact(consumer=consumer)

    def interact(self, out=None, consumer=None, timeout=None):
        mkr = lambda: [self.socket] if consumer else []
        mkw = lambda: [self.socket] if out else []
        mkx = lambda: []
        mka = lambda: (mkr(), mkw(), mkx())
        r, w, x = mka()
        while any((r, w, x)):
            sets = mka()
            if not any(sets):
                break
            r, w, x = select(*(sets + (timeout,)))
            if r:
                super(SelectIO, self).receive(consumer)
            if w:
                out = super(SelectIO, self).deliver(out)

    def run(self, consumer):
        while True:
            self.interact(out=self.out_buffer, consumer=consumer)

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
