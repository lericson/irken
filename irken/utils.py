from irken.nicks import nickname

class NicknameMixin(object):
    def _set_nick(self, value):
        value = nickname(value)
        if hasattr(self, "_nick"):
            if value != self.nick:
                self.send_cmd(None, "NICK", (value,))
        else:
            self._nick = value
    def _get_nick(self): return getattr(self, "_nick", "*")
    nick = property(_get_nick, _set_nick)
    
class AutoRegisterMixin(object):
    def __init__(self, *args, **kwds):
        if "autoregister" in kwds:
            self.autoregister = kwds.pop("autoregister")
        super(AutoRegisterMixin, self).__init__(*args, **kwds)

    def connect(self, *args, **kwds):
        rv = super(AutoRegisterMixin, self).connect(*args, **kwds)
        user, real = self.autoregister
        self.send_cmd(None, "USER", (user, "*", "*", real))
        self.send_cmd(None, "NICK", (self.nick,))
        return rv

from functools import partial

class DebugMixin(object):
    def _do_cmd(name, prefix, command, args):
        parts = (name, prefix or "", command, args or [])
        print "%s: prefix=%r, command=%s, args=%r" % parts
    recv_cmd = staticmethod(partial(_do_cmd, "recv"))
    send_cmd = staticmethod(partial(_do_cmd, "send"))
    del _do_cmd
