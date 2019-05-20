#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   PlayerList.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GObject

def color_parser(color):
    rgba = Gdk.RGBA()
    rgba.parse(color)
    return rgba


class PlayerList(Gtk.Frame):

    __gsignals__ = {
    "nueva-seleccion": (GObject.SignalFlags.RUN_LAST,
        None, (GObject.TYPE_PYOBJECT, ))}

    def __init__(self):

        GObject.GObject.__init__(self)

        self.override_background_color(Gtk.StateType.NORMAL, color_parser("#ffffff"))

        vbox = Gtk.VBox()
        self.lista = Lista()

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.lista)

        vbox.pack_start(scroll, True, True, 0)

        self.add(vbox)
        self.show_all()

        self.set_size_request(150, -1)

        self.lista.connect("nueva-seleccion", self.__re_emit_nueva_seleccion)

    def __re_emit_nueva_seleccion(self, widget, pista):
        self.emit('nueva-seleccion', pista)

    def __load_files(self, widget, items, tipo):
        if tipo == "load":
            self.lista.limpiar()
            self.emit("accion", False, "limpiar", False)

        if items:
            self.lista.agregar_items(items)

        else:
            self.emit('nueva-seleccion', False)

    def seleccionar_primero(self):
        self.lista.seleccionar_primero()

    def seleccionar_ultimo(self):
        self.lista.seleccionar_ultimo()

    def seleccionar_anterior(self):
        self.lista.seleccionar_anterior()

    def seleccionar_siguiente(self):
        self.lista.seleccionar_siguiente()

    def select_valor(self, path_origen):
        self.lista.select_valor(path_origen)

    def limpiar(self):
        self.lista.limpiar()

    def get_selected_path(self):
        """
        Devuelve el valor del path seleccionado.
        """
        modelo, _iter = self.lista.get_selection().get_selected()
        valor = self.lista.get_model().get_value(_iter, 2)
        return valor

    def get_items_paths(self):
        """
        Devuelve la lista de archivos en la lista.
        """
        filepaths = []
        model = self.lista.get_model()
        item = model.get_iter_first()

        self.lista.get_selection().select_iter(item)

        while item:
            filepaths.append(model.get_value(item, 2))
            item = model.iter_next(item)

        return filepaths


class Lista(Gtk.TreeView):

    __gsignals__ = {
    "nueva-seleccion": (GObject.SignalFlags.RUN_LAST,
        None, (GObject.TYPE_PYOBJECT, ))}

    def __init__(self):

        GObject.GObject.__init__(self, model=Gtk.ListStore(
            GdkPixbuf.Pixbuf,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING))

        self.override_background_color(Gtk.StateType.NORMAL, color_parser("#ffffff"))
        self.set_property("rules-hint", True)
        self.set_headers_clickable(False)
        self.set_headers_visible(False)

        self.permitir_select = True
        self.valor_select = False
        self.ultimo_select = False

        self.__setear_columnas()

        self.get_selection().set_select_function(
            self.__selecciones, self.get_model())

        self.show_all()

    def __selecciones(self, selection, model, path, is_selected, user_data):
        """
        Cuando se selecciona un item en la lista.
        """
        if not self.permitir_select:
            return True

        _iter = self.get_model().get_iter(path)
        valor = self.get_model().get_value(_iter, 2)

        if self.valor_select != valor:
            self.valor_select = valor

            GObject.timeout_add(3, self.__select,
                self.get_model().get_path(_iter))

        return True

    def __select(self, path):
        if self.ultimo_select != self.valor_select:
            self.emit('nueva-seleccion', self.valor_select)
            self.ultimo_select = self.valor_select

        self.scroll_to_cell(path)
        return False

    def __setear_columnas(self):
        self.append_column(self.__construir_columa_icono('', 0, True))
        self.append_column(self.__construir_columa('Archivo', 1, False))
        self.append_column(self.__construir_columa('', 2, False))

    def __construir_columa(self, text, index, visible):
        render = Gtk.CellRendererText()
        render.set_property("background", "#ffffff")
        render.set_property("foreground", "#000000")

        columna = Gtk.TreeViewColumn(text, render, text=index)
        columna.set_sort_column_id(index)
        columna.set_property('visible', visible)
        columna.set_property('resizable', False)
        columna.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        return columna

    def __construir_columa_icono(self, text, index, visible):
        render = Gtk.CellRendererPixbuf()
        render.set_property("cell-background", "#ffffff")

        columna = Gtk.TreeViewColumn(text, render, pixbuf=index)
        columna.set_property('visible', visible)
        columna.set_property('resizable', False)
        columna.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        return columna

    def __ejecutar_agregar_elemento(self, elementos):
        if not elementos:
            self.permitir_select = True
            self.seleccionar_primero()
            self.get_toplevel().set_sensitive(True)
            return False

        texto, path = elementos[0]
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, 140, -1)

        self.get_model().append([pixbuf, texto, path])
        elementos.remove(elementos[0])
        GObject.idle_add(self.__ejecutar_agregar_elemento, elementos)
        return False

    def limpiar(self):
        self.permitir_select = False
        self.get_model().clear()
        self.valor_select = False
        self.ultimo_select = False
        self.permitir_select = True

    def agregar_items(self, elementos):
        """
        Recibe lista de: [texto para mostrar, path oculto] y
        Comienza secuencia de agregado a la lista.
        """
        self.get_toplevel().set_sensitive(False)
        self.permitir_select = False
        GObject.idle_add(self.__ejecutar_agregar_elemento, elementos)

    def seleccionar_siguiente(self, widget=None):
        modelo, _iter = self.get_selection().get_selected()
        try:
            self.get_selection().select_iter(
                self.get_model().iter_next(_iter))

        except:
            self.seleccionar_primero()

        return False

    def seleccionar_anterior(self, widget=None):
        modelo, _iter = self.get_selection().get_selected()
        try:
            path = self.get_model().get_path(_iter)
            path = (path[0] - 1, )

            if path > -1:
                self.get_selection().select_iter(
                    self.get_model().get_iter(path))

        except:
            self.seleccionar_ultimo()

        return False

    def seleccionar_primero(self, widget=None):
        self.get_selection().select_path(0)

    def seleccionar_ultimo(self, widget=None):
        model = self.get_model()
        item = model.get_iter_first()
        _iter = None

        while item:
            _iter = item
            item = model.iter_next(item)

        if _iter:
            self.get_selection().select_iter(_iter)

    def select_valor(self, path_origen):
        model = self.get_model()
        _iter = model.get_iter_first()
        valor = model.get_value(_iter, 2)

        while valor != path_origen:
            _iter = model.iter_next(_iter)
            valor = model.get_value(_iter, 2)

        if _iter:
            self.get_selection().select_iter(_iter)
