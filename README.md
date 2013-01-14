# XBMC Tools

This contains some tools to play with XBMC written in python

## xbmcremote

A CLI tool to control XBMC
Uses keyboard to control XBMC all keys will be sent as is to XBMC and will be passed trough keymaps.xml
Exceptions are the arrows keys which will be used for navigation.

### Config ~/.config/xbmctools/remote.conf

Used to configure shortcuts to actions http://wiki.xbmc.org/index.php?title=Action_IDs
Or remap keys to others or configure macros

The config file should have a section called keybindings.
The key represents the key you want to bind (either numeric acsii value or the character itself or KEY_CHARACTER (can be used for numbers)).
The value should be a json string containing the action that should be performmed

`
[keybindings]
f = {"action": "ActivateWindow(favourite)"} # map f key to open favourites
v = {"key": "m"} # remap key v to m
`

## xbmcpidgin

Forwards message from pidgin to the notification system of XBMC
