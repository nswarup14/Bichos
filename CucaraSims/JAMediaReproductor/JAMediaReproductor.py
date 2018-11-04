#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   JAMediaReproductor.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

import os
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gst

from JAMediaBins import JAMedia_Audio_Pipeline
from JAMediaBins import JAMedia_Video_Pipeline

PR = False

GLib.threads_init()


class JAMediaReproductor(GObject.GObject):

    __gsignals__ = {
    "endfile": (GObject.SignalFlags.RUN_LAST,
        None, []),
    "estado": (GObject.SignalFlags.RUN_LAST,
        None, (GObject.TYPE_STRING,)),
    "newposicion": (GObject.SignalFlags.RUN_LAST,
        None, (GObject.TYPE_INT,)),
    "video": (GObject.SignalFlags.RUN_LAST,
        None, (GObject.TYPE_BOOLEAN,)),
    "loading-buffer": (GObject.SignalFlags.RUN_LAST,
        None, (GObject.TYPE_INT, )),
        }

    def __init__(self, ventana_id):

        GObject.GObject.__init__(self)

        self.nombre = "JAMediaReproductor"

        self.video = False
        self.ventana_id = ventana_id
        self.progressbar = True
        self.estado = None
        self.duracion = 0.0
        self.posicion = 0.0
        self.actualizador = False
        self.player = None
        self.bus = None

        self.player = Gst.ElementFactory.make("playbin2", "player")
        self.player.set_property("buffer-size", 50000)

        self.audio_bin = JAMedia_Audio_Pipeline()
        self.video_bin = JAMedia_Video_Pipeline()

        self.player.set_property('video-sink', self.video_bin)
        self.player.set_property('audio-sink', self.audio_bin)

        self.bus = self.player.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message', self.__on_mensaje)
        self.bus.enable_sync_message_emission()
        self.bus.connect('sync-message', self.__sync_message)

    def __sync_message(self, bus, message):
        if message.type == Gst.MessageType.ELEMENT:
            if message.structure.get_name() == 'prepare-xwindow-id':
                message.src.set_xwindow_id(self.ventana_id)

        elif message.type == Gst.MessageType.STATE_CHANGED:
            old, new, pending = message.parse_state_changed()

            if self.estado != new:
                self.estado = new

                if new == Gst.State.PLAYING:
                    self.emit("estado", "playing")
                    self.__new_handle(True)

                elif new == Gst.State.PAUSED:
                    self.emit("estado", "paused")
                    self.__new_handle(False)

                elif new == Gst.State.NULL:
                    self.emit("estado", "None")
                    self.__new_handle(False)

                else:
                    self.emit("estado", "paused")
                    self.__new_handle(False)

        elif message.type == Gst.MessageType.TAG:
            taglist = message.parse_tag()
            datos = taglist.keys()
            if 'video-codec' in datos:
                if self.video == False or self.video == None:
                    self.video = True
                    self.emit("video", self.video)

        elif message.type == Gst.MessageType.LATENCY:
            self.player.recalculate_latency()

        elif message.type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            if PR:
                print "JAMediaReproductor ERROR:"
                print "\t%s" % err
                print "\t%s" % debug
            self.__new_handle(False)

    def __on_mensaje(self, bus, message):
        if message.type == Gst.MessageType.EOS:
            self.__new_handle(False)
            self.emit("endfile")

        elif message.type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            if PR:
                print "JAMediaReproductor ERROR:"
                print "\t%s" % err
                print "\t%s" % debug
            self.__new_handle(False)

        elif message.type == Gst.MessageType.BUFFERING:
            buf = int(message.structure["buffer-percent"])
            if buf < 100 and self.estado == Gst.State.PLAYING:
                self.emit("loading-buffer", buf)
                self.__pause()

            elif buf > 99 and self.estado != Gst.State.PLAYING:
                self.emit("loading-buffer", buf)
                self.__play()

    def __play(self):
        self.player.set_state(Gst.State.PLAYING)

    def __pause(self):
        self.player.set_state(Gst.State.PAUSED)

    def __new_handle(self, reset):
        if self.actualizador:
            GLib.source_remove(self.actualizador)
            self.actualizador = False

        if reset:
            self.actualizador = GLib.timeout_add(500, self.__handle)

    def __handle(self):
        if not self.progressbar:
            return True

        duracion = self.player.query_duration(Gst.Format.TIME)[0] / Gst.SECOND
        posicion = self.player.query_position(Gst.Format.TIME)[0] / Gst.SECOND

        pos = posicion * 100 / duracion

        if self.duracion != duracion:
            self.duracion = duracion

        if pos != self.posicion:
            self.posicion = pos
            self.emit("newposicion", self.posicion)

        return True

    def pause_play(self):
        if self.estado == Gst.State.PAUSED or self.estado == Gst.State.NULL \
            or self.estado == Gst.State.READY:
            self.__play()

        elif self.estado == Gst.State.PLAYING:
            self.__pause()

    def rotar(self, valor):
        self.video_bin.rotar(valor)

    def set_balance(self, brillo=False, contraste=False,
        saturacion=False, hue=False, gamma=False):
        self.video_bin.set_balance(brillo=brillo, contraste=contraste,
            saturacion=saturacion, hue=hue, gamma=gamma)

    def get_balance(self):
        return self.video_bin.get_balance()

    def stop(self):
        self.__new_handle(False)
        self.player.set_state(Gst.State.NULL)
        self.emit("newposicion", 0)

    def load(self, uri):
        if not uri:
            return

        self.duracion = 0.0
        self.posicion = 0.0
        self.emit("newposicion", self.posicion)
        self.emit("loading-buffer", 100)

        if os.path.exists(uri):
            direccion = "file://" + uri
            self.player.set_property("uri", direccion)
            self.progressbar = True
            self.__play()

        else:
            if Gst.uri_is_valid(uri):
                self.player.set_property("uri", uri)
                self.progressbar = False
                self.__play()

        return False

    def set_position(self, posicion):
        if not self.progressbar:
            return

        if self.duracion < posicion:
            return

        if self.duracion == 0 or posicion == 0:
            return

        posicion = self.duracion * posicion / 100

        event = Gst.Event.new_seek(
            1.0, Gst.Format.TIME,
            Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE,
            Gst.SeekType.SET, posicion * 1000000000,
            Gst.SeekType.NONE, self.duracion * 1000000000)

        self.player.send_event(event)

    def set_volumen(self, volumen):
        self.player.set_property('volume', volumen / 10)

    def get_volumen(self):
        return self.player.get_property('volume') * 10
