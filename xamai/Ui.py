#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
import os
import re
import xamai.Constants as const

'''
    Utilidades para cargar en la GUI
'''
# Devuelve el codigo HTML de un archivo
def readHTML(file, tpl = {}):
    html = const.LOCATION + "/gui/" + file

    fd = open(html, "r")
    data = fd.read().decode("utf-8")
    fd.close()

    for key, value in tpl.items():
        data = data.replace("{%s}" % key, str(value))

    return data

# Muestra el ultimo respaldo exitoso hecho por cada rfc de un usuario
def showLastSuccess():
    from xamai.Upload import Upload
    u = Upload()
    backups = u.getLastSuccess()
    value = ''
    if not backups:
        value = "<tr><td colspan=2><h3 style='color: #BDBDBD; text-align: center;'>No se encontraron respaldos</h3></td></tr>"
    else:
        for back in backups:
            m = re.search("[A-Za-z]{3,4}[0-9]{6}[A-Za-z0-9]{3}", back)
            value = value + "<tr>" \
                            "<td>" + m.group(0) + "</td>" \
                            "<td>" + u.getDateFromBackup(back) + "</td>" \
                            "<tr>"
        return value

# Carga imagenes externas
def loadImg():
    img = '<img alt="Profile Photo" src="file://' + os.path.join(const.LOCATION, "img/avatar.png") + '">'
    return img

# carga los JS
def loadJS():
    js = '<script src="file://' + os.path.join(const.LOCATION, "gui/assets/js/jquery.min.js") + '"></script>' \
         '<script src="file://' + os.path.join(const.LOCATION, "gui/assets/js/base.min.js") + '"></script>' \
         '<script src="file://' + os.path.join(const.LOCATION, "gui/assets/js/project.min.js") + '"></script>'
    return js

# carga los estilos css
def loadStyles():
    style = "<style>"
    # carga los estilos
    style_file = open(const.LOCATION + "/gui/assets/css/base.min.css", "r")
    style = style + "\n\n" + style_file.read()
    style_file.close()

    style_file = open(const.LOCATION + "/gui/assets/css/project.min.css", "r")
    style = style + "\n\n" + style_file.read()
    style_file.close()

    style = style + "\n\n" + "</style>"

    return style