#!/usr/bin/env python
# encoding: utf-8
import unittest
from irken.nicks import Mask
from irken.base import Connection
from irken.dispatch import CommonDispatchMixin, handler
from irken.encoding import EncodingMixin
from irken.utils import AutoRegisterMixin

class TestConnectionMixin(object):
    def __init__(self, *args, **kwds):
        super(TestConnectionMixin, self).__init__(*args, **kwds)
        # TODO Should be using a deque.
        self.sent_lines = []
        self.read_line = ""

    # Essential to have errors bubble up to unittest level.
    def handle_error(self): raise

    # I/O mixin part.
    def connect(self, address):
        self.connected_to = address

    def close(self):
        if self.sent_lines:
            raise ValueError("unread lines: %r" % (self.sent_lines,))

    def send_raw(self, line):
        self.sent_lines.append(line)

    def recv_raw(self):
        # Switcheroo.
        r, self.read_line = self.read_line, ""
        return r

bases = (AutoRegisterMixin, TestConnectionMixin, CommonDispatchMixin,
         EncodingMixin, Connection)
TestConnection = type("TestConnection", bases, {})

class IrkenTestCase(unittest.TestCase):
    # I would name this "test_class", but unittest thinks it's a test function
    # if I do, and that's damn hard to track down, so this has to do.
    irken_cls = TestConnection

    def assert_sent(self, line):
        self.assertEquals(self.conn.sent_lines.pop(0), line)

    def feed_lines(self, *lines):
        for line in lines:
            self.conn.read_line = line
            self.conn.run_once()

    def setUp(self):
        self.conn = self.irken_cls("tester")
        self.conn.autoregister = ("test-user", "Test User One")

    def tearDown(self):
        self.conn.close()

class IOTestCase(IrkenTestCase):
    def test_autoregister_connect(self):
        # We're doing both the simple connect test and the autoregister test
        # because having them split would mean not only two test cases, but
        # also two separate subclasses.
        self.conn.connect(("fake", 1234))
        self.assert_sent("USER test-user * * :Test User One\r\n")
        self.assert_sent("NICK tester\r\n")

    def test_io(self):
        self.conn.send_cmd(None, "HI", ())
        self.assert_sent("HI\r\n")
        self.conn.send_cmd(Mask.from_string("a!b@c"), "TEST", ("foo", "br bz"))
        self.assert_sent(":a!b@c TEST foo :br bz\r\n")

    def test_dispatch(self):
        self.conn.recv_cmd(None, "PING", ("Hello!",))
        self.assert_sent("PONG Hello!\r\n")
        self.conn.recv_cmd(Mask.from_string("some.server"), "PING", ())
        self.assert_sent("PONG\r\n")

    def test_encoding(self):
        # For the curious reader, it says:
        #   :Southern-liver!göran@south.se PRIVMSG :Tards over the Eastern Lake
        #   train eagle spotting.
        self.conn.send_cmd(Mask.from_string(u"Söderbo!göran@söder.se"),
                           "PRIVMSG",
                           (u"Åbäken över Östersjön övar örnåskådning.",))
        self.assert_sent(":S\xc3\xb6derbo!g\xc3\xb6ran@s\xc3\xb6der.se "
                         "PRIVMSG "
                         ":\xc3\x85b\xc3\xa4ken \xc3\xb6ver \xc3\x96stersj"
                         "\xc3\xb6n \xc3\xb6var \xc3\xb6rn\xc3\xa5sk"
                         "\xc3\xa5dning.\r\n")
        # TODO Test input, that is, UTF-8 -> unicode object.

class DispatchingTest(TestConnection):
    def __init__(self, *args, **kwds):
        super(DispatchingTest, self).__init__(*args, **kwds)
        self.called = []

    @handler("privmsg", "notice")
    def do_hypothetical_operation(self, cmd, target, text):
        self.called.append((1, cmd, target, text))
    @handler("privmsg", "notice")
    def do_hipogriph(self, cmd, target, text):
        self.called.append((2, cmd, target, text))

class DispatchingTestCase(IrkenTestCase):
    irken_cls = DispatchingTest

    def test_multi_dispatch_privmsg(self):
        m = Mask.from_string
        self.conn.recv_cmd(m("lericson"), "privmsg",
                           ("#toxik.fanclub", "Hello world!"))
        self.conn.called.sort()
        self.assertEquals(self.conn.called,
            [(1, {"source": m("lericson"), "command": "privmsg"},
                 "#toxik.fanclub", "Hello world!"),
             (2, {"source": m("lericson"), "command": "privmsg"},
                 "#toxik.fanclub", "Hello world!")])

    def test_multi_dispatch_notice(self):
        self.conn.recv_cmd(None, "NOTICE", ("foo", "bar"))
        self.conn.called.sort()
        self.assertEquals(self.conn.called,
            [(1, {"source": None, "command": "NOTICE"}, "foo", "bar"),
             (2, {"source": None, "command": "NOTICE"}, "foo", "bar")])

if __name__ == "__main__":
    unittest.main()
