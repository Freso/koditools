#!/usr/bin/env python2
import dbus, gobject
import logging
from htmllib import HTMLParser
from formatter import AbstractFormatter, DumbWriter
from cStringIO import StringIO
from dbus.mainloop.glib import DBusGMainLoop
from .restclient import JsonRPC

def html2text(html):
    output = StringIO()
    writer = DumbWriter(output)
    p = HTMLParser(AbstractFormatter(writer))
    p.feed(html)
    return output.getvalue()



class Forwarder(object):
    def __init__(self, host):
        self._client = JsonRPC('http://%s:8080/jsonrpc' % host)
        DBusGMainLoop(set_as_default=True)
        self._bus = dbus.SessionBus()

    def run(self):
        self._bus.add_signal_receiver(self.receiveIM,
                        dbus_interface="im.pidgin.purple.PurpleInterface",
                        signal_name="ReceivedImMsg")

        loop = gobject.MainLoop()
        loop.run()

    def receiveIM(self, account, sender, message, conversation, flags):
        logging.info("Recevied msg from %s: %s" % (sender, message))
        self._client.command('GUI.ShowNotification', title='%s says' % sender, message=html2text(message))

