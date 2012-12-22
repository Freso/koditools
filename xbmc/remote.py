#!/usr/bin/env python2
import tty
import sys
import termios
import logging
from .xbmcclient import XBMCClient
from .restclient import JsonRPC
import time

def getch_():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

ESCAPEMAPPING = {68: 500, #left
                 65: 501, #up,
                 67: 502, #right
                 66: 503, #down
                }

def getch():
    logging.debug('Getting key')
    char = ord(getch_())
    if char == 27:
        getch_()
        char = ord(getch_())
        char = ESCAPEMAPPING.get(char, 0)
    logging.debug('Retreived key %s' % char)
    return char



class Remote(object):
    MAPPING = {127: {'key': 'backspace'}, #backspace
               13: {'key': 'enter'}, #Enter
               32: {'key': 'space'}, #space
               44: {'key': 'menu'}, #,
               45: {'key': 'volume_down'}, #-
               47: {'macro': [{'action': 'ActivateWindow(home)'},
                              {'key': 'up'},
                              {'key': 'enter'}]}, #/
               48: {'action': 'mute'}, #0
               61: {'key': 'volume_up'}, #=
               97: {'action': 'FullScreen'},
               102: {'action': 'ActivateWindow(favourites)'}, #f
               104: {'action': 'ActivateWindow(home)'}, #f
               116: {'action': 'ActivateWindow(Videos, TvShowTitles)'}, #t
               118: {'action': 'ActivateWindow(Videos, MovieTitles)'}, #v
               105: {'key': 'i'}, #i
               109: {'action': 'ActivateWindow(Videos, MovieTitles)'}, #m
               111: {'action': 'OSD'}, #o
               115: {'action': 'ActivateWindow(shutdownmenu)'}, #s
               120: {'key': 'Stop' }, #x
               500: {'key': 'left'}, #left
               501: {'key': 'up'}, #up
               502: {'key': 'right'}, #right
               503: {'key': 'down'}, #Down
              }
    def __init__(self, host):
        self.remote = XBMCClient('PyRemote', ip=host)
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
        if 'macro' in command:
            result = list()
            for macro in command['macro']:
                result.append(self.command(command=macro))
        logging.info("%s %s" % (command, result))
        return result


    def run(self):
        char = getch()
        while char not in (3,113): #control + c and q
            if not self.command(char):
                if char == 58: #this is a : we are gonna enter text now
                    print 'Enter text: ',
                    text = sys.stdin.readline()[:-1]
                    self.client.command('Input.SendText', text=text, done=True)
                else:
                    logging.info(char)

            char = getch()
