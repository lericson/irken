# coding: utf-8

from irken.nicks import Mask
from irken.tests import IrkenTestCase

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

    def test_io_dispatch(self):
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
