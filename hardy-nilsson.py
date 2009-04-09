#!/usr/bin/env python
"""Jag heter Hardy. Hardy Nilsson."""

import os
import re
import urlparse
import urllib2
from BeautifulSoup import BeautifulSoup
import irken
from irken.dispatch import handler

class HardyNilsson(irken.Connection):
    allowable_domains = "youtube.com", "php.net"
    url_re = re.compile(r"\b(https?://.+?\..+?/.+?)(?:$| )", re.I)

    @property
    def client_version(self):
        reffn = ".git/refs/heads/master"
        rv = "irken example bot"
        if os.path.exists(reffn):
            rev = open(reffn, "U").read().rstrip("\n")
            rv += " (master is %s)" % rev
        return rv

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

irken.logging(level=irken.LOG_DEBUG)
bot = HardyNilsson(nick="hardy-nilsson",
                   autoregister=("hardy-nilsson", "Hardy Nilsson"))
bot.connect(("irc.lericson.se", 6667))
bot.run()
