import unittest
from irken.nicks import Mask
from irken.base import BaseConnection
from irken.dispatch import CommonDispatchMixin, Command, handler
from irken.encoding import EncodingMixin
from irken.utils import AutoRegisterMixin

class TestIO(object):
    def __init__(self):
        # TODO Should be using a deque.
        self.sent_lines = []
        self.read_line = ""

    def connect(self, address):
        self.connected_to = address

    def close(self):
        if self.sent_lines:
            raise ValueError("unread lines: %r" % (self.sent_lines,))
        if self.read_line:
            raise ValueError("unreceived lines: %r" % ([self.read_line],))

    def deliver(self, data):
        self.sent_lines.append(data)

    def receive(self, consumer):
        self.read_line = consumer(self.read_line + r)

class TestMixin(object):
    make_io = TestIO
    # Essential to have errors bubble up to unittest level.
    def handle_error(self): raise

bases = (AutoRegisterMixin, TestMixin, CommonDispatchMixin,
         EncodingMixin, BaseConnection)
TestConnection = type("TestConnection", bases, {})

class IrkenTestCase(unittest.TestCase):
    # I would name this "test_class", but unittest thinks it's a test function
    # if I do, and that's damn hard to track down, so this has to do.
    irken_cls = TestConnection
    nick = "tester"
    username = "test-user"
    realname = "Test User One"

    def assert_sent(self, line):
        self.assertEquals(self.conn.io.sent_lines.pop(0), line)

    def feed_lines(self, *lines):
        for line in lines:
            self.conn.consume(line)

    def setUp(self):
        reginfo = (self.username, self.realname)
        self.conn = self.irken_cls(self.nick, autoregister=reginfo)

    def tearDown(self):
        self.conn.io.close()
