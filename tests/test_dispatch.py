from irken.dispatch import Command, handler
from irken.tests import TestConnection, IrkenTestCase

class DispatchingTest(TestConnection):
    def __init__(self, *args, **kwds):
        super(DispatchingTest, self).__init__(*args, **kwds)
        self.called = []

    @handler("irc cmd privmsg", "irc cmd notice")
    def do_hypothetical_operation(self, cmd, target, text):
        self.called.append((1, cmd, target, text))
    @handler("irc cmd privmsg", "irc cmd notice")
    def do_hipogriph(self, cmd, target, text):
        self.called.append((2, cmd, target, text))

class DispatchingTestCase(IrkenTestCase):
    irken_cls = DispatchingTest

    def test_multi_dispatch_privmsg(self):
        source = self.conn.lookup_prefix(("lericson",))
        cmd = Command(u"irc cmd privmsg", source=source)
        self.conn.dispatch(cmd, "#toxik.fanclub", "Hello world!")
        self.conn.called.sort()
        self.assertEquals(self.conn.called,
            [(1, cmd, "#toxik.fanclub", "Hello world!"),
             (2, cmd, "#toxik.fanclub", "Hello world!")])

    def test_multi_dispatch_notice(self):
        cmd = Command(u"irc cmd notice", source=None)
        self.conn.dispatch(cmd, "foo", "bar")
        self.conn.called.sort()
        self.assertEquals(self.conn.called,
            [(1, cmd, "foo", "bar"),
             (2, cmd, "foo", "bar")])
