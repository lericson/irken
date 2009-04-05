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
