#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import os.path

# IP de la api
# Ip publica
IP_SERVER = "http://201.140.108.22:2017"
#IP Local
#IP_SERVER = "http://172.16.2.95:2017"
# archivo de configuracion
CONFIGURATION_FILE = "settings/configuration.json"
# archivo de errores
ERRORS_FILE = "settings/errors.json"
# version de la aplicacion
VERSION = '1.3'
# version de la aplicacion usada, solo para Desarrolladores y API
# x.x.L = Linux, x.x.W = Windows
VERSION_CODE = '1.3.L'
# ubicacion de la aplicacion
LOCATION = os.path.dirname(os.path.realpath(__file__))
# icono de la aplicacion
ICONO = "img/DB_Protector_16X16-01.png"
# archivo de status, usado en la carga / descarga de archivos
STATUS_FILE = "settings/status.json"
# tamano de las subidas maximo 150mb, recomendado 5
CHUNK_SIZE = 1024 * 1024 * 5
