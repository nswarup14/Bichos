#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import gc
import os

gc.enable()
pygame.font.init()
import JAMGlobals as VG


class JAMLabel(pygame.sprite.Sprite):

    def __init__(self, texto):

        pygame.sprite.Sprite.__init__(self)

        """
        No se Puede Crear una Etiqueta sin Texto.
        """
        self.separador = 5
        self.sprite_texto = None
        self.image = None
        self.rect = None
        self.posicion = (0, 0)

        self.imagen = {"origen": None, "tamanio": None}
        self.texto = {"tipo": pygame.font.get_default_font(),
            "tamanio": 20, "color": VG.get_negro(), "texto": texto}
        self.font_from_file = None
        self.base = {"tamanio": None, "color": None}
        self.borde = {"grosor": None, "color": None}
        self.contenedor = {"base": self.base, "borde": self.borde}
        self.JAMObjects = {"Imagen": self.imagen, "Texto": self.texto,
            "Contenedor": self.contenedor}

        self.Reconstruye_JAMlabel(["texto"])

    # ------------- GETS ------------------------
    def get_tamanio(self):
        return (self.rect.w, self.rect.h)

    def get_posicion(self):
        return (self.rect.x, self.rect.y)

    def get_text(self):
        """
        Devuelve la cadena de Texto que contiene JAMLabel.
        """
        return str(self.texto["texto"])

    # ---------- SETEOS -------------------------
    def set_imagen(self, origen=None, tamanio=None):
        """
        Setea la Imagen en JAMLabel. -1 para quitarla.
        """
        if origen == -1:
            self.imagen["origen"] = None
            self.imagen["tamanio"] = None
            self.Reconstruye_JAMlabel(["texto"])
            return
        cambios = False
        if origen and origen != self.imagen["origen"]:
            self.imagen["origen"] = origen
            cambios = True
        if tamanio and tamanio != self.imagen["tamanio"]:
            self.imagen["tamanio"] = tamanio
            cambios = True
        if cambios:
            self.Reconstruye_JAMlabel(["imagen"])

    def set_text(self, tipo=None, tamanio=None, color=None, texto=None):
        """
        Setea el Texto en JAMLabel. "" para quitarlo.
        """
        cambios = False
        if tipo and tipo != self.texto["tipo"]:
            self.texto["tipo"] = tipo
            cambios = True
        if tamanio and tamanio != self.texto["tamanio"]:
            self.texto["tamanio"] = tamanio
            cambios = True
        if color and color != self.texto["color"]:
            self.texto["color"] = color
            cambios = True
        if texto and texto != self.texto["texto"]:
            self.texto["texto"] = texto
            cambios = True
        if cambios:
            if self.texto["tipo"] and self.texto["tamanio"] and \
                self.texto["color"] and self.texto["texto"]:
                self.Reconstruye_JAMlabel(["texto"])

    def set_contenedor(self, colorbas=None, grosor=None, colorbor=None):
        """
        Setea los Colores del Contenedor de JAMLabel.
        """
        cambios = False
        if colorbas == -1:
        # Deshabilita relleno
            self.contenedor["base"]["color"] = None
            colorbas = None
            cambios = True
        if colorbor == -1 or grosor < 1:
        # Deshabilita borde
            self.contenedor["borde"]["grosor"] = None
            self.contenedor["borde"]["color"] = None
            colorbor = None
            grosor = None
            cambios = True
        if colorbas and colorbas != self.contenedor["base"]["color"]:
            self.contenedor["base"]["color"] = colorbas
            cambios = True
        if grosor and grosor != self.contenedor["borde"]["grosor"]:
            self.contenedor["borde"]["grosor"] = grosor
            cambios = True
        if colorbor and colorbor != self.contenedor["borde"]["color"]:
            self.contenedor["borde"]["color"] = colorbor
            cambios = True
        if cambios:
            self.Reconstruye_JAMlabel(["contenedor"])

    def set_posicion(self, punto=None):
        """
        Setea la posición de JAMLabel en la pantalla.
        """
        if type(punto) == tuple and len(punto) == 2 and \
            type(punto[0]) == int and type(punto[1]) == int:
            self.rect.x, self.rect.y = (punto)
            self.posicion = punto

    # ----------- CONSTRUCCION -------------------
    def Reconstruye_JAMlabel(self, cambios):
        """
        Cada vez que se setea algo, se reconstruye JAMLabel
        con sus nuevos valores.
        """
        if not self.sprite_texto:
            self.sprite_texto = self.construye_texto()
        superficie = self.sprite_texto
        if "texto" in cambios:
        # si se modificó el texto
            self.sprite_texto = self.construye_texto()
            superficie = self.sprite_texto

        if self.imagen["origen"]:
        # si hay una imagen
            superficie = self.concatenar(superficie, self.construye_imagen())

        if self.contenedor["base"]["color"] and \
            self.contenedor["base"]["tamanio"] and not self.imagen["origen"]:
            sprite_relleno = self.construye_relleno()
            superficie = VG.pegar_imagenes_centradas(
                superficie, sprite_relleno)

        if self.contenedor["borde"]["grosor"]:
            superficie = self.construye_borde(superficie)

        self.image = superficie
        self.rect = self.image.get_rect()
        self.set_posicion(self.posicion)  # seteo automático de posición

    # ------ TEXTO
    def construye_texto(self):
        """
        Devuelve una Superficie con la Imagen del Texto.
        """
        string_to_render = ""
        fuente = pygame.font.Font(
            pygame.font.match_font(self.texto["tipo"],
            True, False), self.texto["tamanio"])
        if self.font_from_file:
            fuente = pygame.font.Font(
            self.font_from_file, self.texto["tamanio"])
        string_to_render = unicode(str(self.texto["texto"]).decode("utf-8"))
        imagen_fuente = fuente.render(
            string_to_render, 1, (self.texto["color"]))
        self.contenedor["base"]["tamanio"] = (
            imagen_fuente.get_size()[0] + self.separador * 2,
            imagen_fuente.get_size()[1] + self.separador * 2)
        return imagen_fuente

    def set_font_from_file(self, direccion_archivo, tamanio=None):
        """
        Setea la fuente desde un archivo.
        """
        cambios = False
        try:
            if os.path.isfile(direccion_archivo):
                self.font_from_file = direccion_archivo
                cambios = True
        except:
            pass
        if type(tamanio) == int:
            self.texto["tamanio"] = tamanio
            cambios = True
        if cambios:
            self.Reconstruye_JAMlabel(["texto"])

    # ------ IMAGEN
    def construye_imagen(self):
        """
        Carga una imagen.
        """
        if self.imagen["tamanio"]:
            w, h = self.imagen["tamanio"]
            if w < 20:
                w = 20
            if h < 20:
                h = 20
            self.imagen["tamanio"] = (w, h)
        else:
            imagen = pygame.image.load(self.imagen["origen"])
            self.imagen["tamanio"] = imagen.get_size()
        return pygame.transform.scale(
            pygame.image.load(self.imagen["origen"]),
            self.imagen["tamanio"]).convert_alpha()

    # ------- CONCATENAR IMAGEN-TEXTO SOBRE RELLENO
    def concatenar(self, sprite_texto, sprite_imagen):
        """
        Arma una imagen con Imagen+Texto Concatenados para Formar
        la Cara de JAMLabel.
        """
        w, h = sprite_imagen.get_size()
        w1, h1 = sprite_texto.get_size()
        altura = h
        if h > h1:
            altura = h
        else:
            altura = h1
        self.contenedor["base"]["tamanio"] = (w + w1 + self.separador * 3,
            altura + self.separador * 2)
        superficie = self.construye_relleno()
        superficie.blit(sprite_imagen, (self.separador,
            altura / 2 - h / 2 + self.separador))
        superficie.blit(sprite_texto, (w + self.separador * 2,
            altura / 2 - h1 / 2 + self.separador))
        return superficie

    # ------ RELLENO
    def construye_relleno(self):
        """
        Crea un Relleno de Color para JAMLabel.
        """
        if not self.contenedor["base"]["color"]:
            self.contenedor["base"]["color"] = VG.get_blanco()
        return VG.get_Rectangulo(self.contenedor["base"]["color"],
            self.contenedor["base"]["tamanio"])

    # ------- Borde
    def construye_borde(self, superficie):
        """
        Crea un Borde de Color para JAMLabel.
        """
        if not self.contenedor["borde"]["color"]:
            self.contenedor["borde"]["color"] = VG.get_negro()
        if not self.contenedor["borde"]["grosor"]:
            self.contenedor["borde"]["grosor"] = 2
        return VG.get_my_surface_whit_border(superficie,
            self.contenedor["borde"]["color"],
            self.contenedor["borde"]["grosor"])

    def Describe(self):
        """
        Describe la Estructura de Este Control.
        """
        estructura = '''
        Estructura JAMLabel:
            JAMObjects:
                Imagen
                Texto
                Contenedor

        Detalle Estructural:
                Imagen:
                    origen
                    tamanio
                Texto:
                    tipo
                    tamanio
                    color
                    texto
                Contenedor:
                    Base:
                        tamanio
                        color
                    Borde:
                        grosor
                        color '''
        print estructura
        print "Ejemplo, Configuración actual:\n"
        print "\t", self.JAMObjects.keys(), "\n"
        for k in self.JAMObjects.items():
            print k, "\n"
