#!/usr/bin/env python
# coding: utf-8
"""Jag heter Hardy. Hardy Nilsson."""

import os
import re
import urlparse
import urllib2

from BeautifulSoup import BeautifulSoup

import irken
from irken.io import AsyncoreIO
from irken.dispatch import handler

class HardyNilsson(irken.Connection):
    greeting = filter(None, map(lambda v: v.strip().decode("utf-8"),
"""
det här är min tredje vecka på fredagsbilagan.
jag heter hardy. nilsson.
jag gör recensioner va. indierecensioner.
men jag har ju min egen tidning. mitt fanzine. common people.
jag ser eh common people som arenarockens antites.
common people är inte slitz.
common people är inte tracks.
common people är indie. indiepop.
""".split("\n")))
    allowable_domains = "youtube.com", "php.net"
    url_re = re.compile(r"\b(https?://.+?\..+?/.+?)(?:$| )", re.I)
    make_io = lambda self: AsyncoreIO(consumer=self.consume)

    @property
    def client_version(self):
        reffn = ".git/refs/heads/master"
        rv = "irken example bot"
        if os.path.exists(reffn):
            rev = open(reffn, "U").read().rstrip("\n")
            rv += " (master is %s)" % rev
        return rv

    @handler("irc cmd join")
    def say_greeting(self, cmd, target_name):
        if cmd.source == self:
            for line in self.greeting:
                self.send_cmd(None, "PRIVMSG", (target_name, line))

    @handler("irc cmd privmsg")
    def say_html_title(self, cmd, target_name, text):
        reply_to = self.lookup_prefix((target_name,))
        if reply_to == self:
            reply_to = cmd.source
        for url_text in self.url_re.findall(text):
            if self._is_allowed_url(url_text):
                title = self._get_title(url_text)
                self.send_cmd(None, "PRIVMSG", (reply_to.nick, title))

    def _is_allowed_url(self, url_text):
        url = urlparse.urlsplit(url_text)
        for allowed in self.allowable_domains:
            if len(url.netloc) > len(allowed):
                if url.netloc.endswith("." + allowed):
                    return True
            else:
                if url.netloc == allowed:
                    return True
        return False

    def _get_title(self, url):
        return BeautifulSoup(urllib2.urlopen(url)).title.string

def main(**opts):
    from example import main as main_real
    opts = dict(opts, nick="hardy", username="hnilsson", realname="Hardy Nilsson",
                address=("irc.lericson.se", 6667))
    return main_real(cls=HardyNilsson, **opts)

if __name__ == "__main__":
    main()
