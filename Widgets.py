#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

from EventTraductor.EventTraductor import MousemotionTraduce
from EventTraductor.EventTraductor import Traduce_button_press_event
from EventTraductor.EventTraductor import Traduce_button_release_event

def color_parser(color):
    rgba = Gdk.RGBA()
    rgba.parse(color)
    return rgba

class Escenario(Gtk.DrawingArea):

    __gsignals__ = {
    "new-size": (GObject.SignalFlags.RUN_LAST,
        None, (GObject.TYPE_PYOBJECT, )),
    "mouse-enter": (GObject.SignalFlags.RUN_LAST,
        None, (GObject.TYPE_BOOLEAN, ))}

    def __init__(self):

        GObject.GObject.__init__(self)

        self.override_background_color(Gtk.StateType.NORMAL, color_parser("#000000"))

        self.set_events(Gdk.EventType.EXPOSE |
            #Gdk.KEY_PRESS | Gdk.KEY_RELEASE |
            #Gdk.EventMask.KEY_RELEASE_MASK | Gdk.EventMask.KEY_PRESS_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.POINTER_MOTION_HINT_MASK |
            Gdk.EventMask.BUTTON_MOTION_MASK | Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK
            | Gdk.EventMask.ENTER_NOTIFY_MASK)

        self.connect("size-allocate", self.__size_request)
        self.connect("draw", self.__draw_cb)

        self.connect("button_press_event", self.__button_press_event)
        self.connect("button_release_event", self.__button_release_event)
        self.connect("motion-notify-event", self.__mouse_motion)
        self.connect("enter-notify-event", self.__mouse_enter)
        self.connect("leave-notify-event", self.__mouse_leave)

        self.show_all()

    def __mouse_enter(self, widget, event):
        self.emit("mouse-enter", True)

    def __mouse_leave(self, widget, event):
        self.emit("mouse-enter", False)

    def __button_press_event(self, widget, event):
        try:
            if self.get_toplevel().juego:
                Traduce_button_press_event(event,
                    self.get_allocation(),
                    self.get_toplevel().juego.RESOLUCION_INICIAL)
        except:
            # Para Sugar
            if self.get_toplevel().interfaz.juego:
                Traduce_button_press_event(event,
                    self.get_allocation(),
                    self.get_toplevel().interfaz.juego.RESOLUCION_INICIAL)

        return False

    def __button_release_event(self, widget, event):
        try:
            if self.get_toplevel().juego:
                Traduce_button_release_event(event,
                    self.get_allocation(),
                    self.get_toplevel().juego.RESOLUCION_INICIAL)
        except:
            # Para Sugar
            if self.get_toplevel().interfaz.juego:
                Traduce_button_release_event(event,
                    self.get_allocation(),
                    self.get_toplevel().interfaz.juego.RESOLUCION_INICIAL)
        return False

    def __mouse_motion(self, widget, event):
        try:
            if self.get_toplevel().juego:
                MousemotionTraduce(event,
                    self.get_allocation(),
                    self.get_toplevel().juego.RESOLUCION_INICIAL)
        except:
            # Para Sugar
            if self.get_toplevel().interfaz.juego:
                MousemotionTraduce(event,
                    self.get_allocation(),
                    self.get_toplevel().interfaz.juego.RESOLUCION_INICIAL)
        return False

    def __size_request(self, widget, event):
        rect = self.get_allocation()
        self.emit("new-size", (rect.width, rect.height))

    def __draw_cb(self, widget, event):
        rect = self.get_allocation()
        self.emit("new-size", (rect.width, rect.height))
