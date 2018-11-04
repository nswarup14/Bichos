#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   JAMediaReproductor.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

import os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gst

GLib.threads_init()
Gst.init(None)


class Player(GObject.GObject):

    __gsignals__ = {
    "endfile": (GObject.SignalFlags.RUN_LAST,
        None, [])}

    def __init__(self):

        GObject.GObject.__init__(self)

        self.player = None
        self.bus = None

        self.player = Gst.ElementFactory.make("playbin", "player")

        fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
        autoaudio = Gst.ElementFactory.make("autoaudiosink", "autoaudio")
        self.player.set_property('video-sink', fakesink)
        self.player.set_property('audio-sink', autoaudio)

        self.bus = self.player.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message', self.__on_mensaje)
        self.bus.enable_sync_message_emission()
        self.bus.connect('sync-message', self.__sync_message)

    def __sync_message(self, bus, message):
        if message.type == Gst.MessageType.LATENCY:
            self.player.recalculate_latency()

        elif message.type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            pass

    def __on_mensaje(self, bus, message):
        if message.type == Gst.MessageType.EOS:
            self.emit("endfile")

        elif message.type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            pass

    def __play(self):
        self.player.set_state(Gst.State.PLAYING)

    def __pause(self):
        self.player.set_state(Gst.State.PAUSED)

    def stop(self):
        self.player.set_state(Gst.State.NULL)

    def load(self, uri):
        if not uri:
            return
        if os.path.exists(uri):
            direccion = "file://" + uri
            self.player.set_property("uri", direccion)
            self.__play()
        return False

    def set_volumen(self, volumen):
        self.player.set_property('volume', volumen / 10)

    def get_volumen(self):
        return self.player.get_property('volume') * 10
