#!/usr/bin/env python2
import curses
import logging
import socket
from .xbmcclient import XBMCClient
from .restclient import JsonRPC
import time

class Remote(object):
    MAPPING = {127: {'key': 'backspace'}, #backspace
               10: {'key': 'enter'}, #Enter
               32: {'key': 'space'}, #space
               44: {'key': 'menu'}, #,
               45: {'key': 'volume_down'}, #-
               47: {'macro': [{'api': {'command': 'GUI.ActivateWindow', 'window': 'home'}},
                              {'key': 'up'},
                              {'key': 'enter'},
                              {'text': 'Search: '}]}, #/
               48: {'action': 'mute'}, #0
               58: {'text': 'Enter text: '}, #:
               61: {'key': 'volume_up'}, #=
               63: {'macro': [{'api': {'command': 'Input.ExecuteAction', 'action':'filter'}},
                              {'key': 'enter'},
                              {'text': 'Filter: '}]}, #?
               97: {'action': 'FullScreen'},
               102: {'action': 'ActivateWindow(favourites)'}, #f
               104: {'action': 'ActivateWindow(home)'}, #f
               116: {'action': 'ActivateWindow(Videos, TvShowTitles)'}, #t
               118: {'action': 'ActivateWindow(Videos, MovieTitles)'}, #v
               105: {'key': 'i'}, #i
               109: {'action': 'ActivateWindow(Videos, MovieTitles)'}, #m
               111: {'action': 'OSD'}, #o
               114: {'action': 'reloadkeymaps'}, #r
               115: {'action': 'ActivateWindow(shutdownmenu)'}, #s
               120: {'key': 'Stop' }, #x
               curses.KEY_LEFT: {'key': 'left'}, #left
               curses.KEY_UP: {'key': 'up'}, #up
               curses.KEY_RIGHT: {'key': 'right'}, #right
               curses.KEY_DOWN: {'key': 'down'}, #Down
              }

    def __init__(self, host):
        hostname = socket.gethostname()
        self.remote = XBMCClient('PyRemote: %s' % hostname, ip=host)
        self.client = JsonRPC("http://%s:8080/jsonrpc" %host)
        self.remote.connect()

    def getCommand(self, code):
        return Remote.MAPPING.get(code)

    def command(self, code=None, command=None):
        if code and not command:
            command = self.getCommand(code)
        if not command:
            return False
        if 'action' in command:
            result = self.remote.send_action(command['action'])
            time.sleep(0.2)
        if 'key' in command:
            result = self.remote.send_keyboard_button(command['key'])
            time.sleep(0.1)
            self.remote.release_button()
        if 'api' in command:
            result = self.client.command(**command['api'])
            time.sleep(0.2)
        if 'macro' in command:
            result = list()
            for macro in command['macro']:
                result.append(self.command(command=macro))
        if 'text' in command:
            self.scr.addnstr(command['text'], len(command['text']))
            curses.echo()
            text = self.scr.getstr()
            curses.noecho()
            result = self.client.command('Input.SendText', text=text, done=True)


        logging.info("%s %s" % (command, result))
        return result


    def run(self, scr):
        self.scr = scr
        char = self.scr.getch()
        while char not in (3,113): #control + c and q
            self.command(char)
            logging.info(char)
            char = self.scr.getch()
