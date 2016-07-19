#!/usr/bin/env python
# -*- coding: utf-8 -*-
import contextlib
import datetime
import json
import os
import os.path
import time
import urllib2

import dropbox
from dropbox.client import DropboxClient

from Login import Login
from Preferences import Preferences
from SetLog import SetLog

'''
    Metodos usados para trabajar con la API de Dropbox
    getData: Devuelve los datos del usuario:
        {'freeSpace': 624, u'tokenDropbox': u'', 'space': 1024, u'IdCustomer': 1, 'ext': [u'BAK', u'ZIP'], u'user': u'Jguerrero', u'time': u'20', u'path': u'/home/backups', u'password': u'Jguerrero', 'spaceUsed': 400, u'time_type': u'dias'}
    getLocalFilesList: Lista de archivos en la carpeta local
    filtradoPorExtension: Un archivo tiene extension valida para ser subido
    uploadFile: Sube archivo a Dropbox
        Estructura de carpetas en Dropbox
            /Aplicaciones/DBProtector/user-id/año/mes/archivo
        Estructura de carpetas en Aplicacion Dropbox
            /user-id/año/mes/archivo
            la Api trabaja a nivel Root de la aplicacion, ej: /1/2016/07
        Validaciones:
            -Archivo existe?
            -El tamaño del archivo debe ser menor al espacio disponible (proporcionado por la API de SCANDA)
            -El archivo debe tener una extension valida (proporcionado por la API de SCANDA)
            -Si el archivo es mayor que CHUNK_SIZE (10MB) se sube por bloques, si es menor o igual se sube en una sola solicitud
        - Return
            - 1 = Archivo inexistente
            - 2 = Espacio insuficiente
            - 3 = Extension invalida
            - None = El archivo no se subio
            - res = JSON array con los detalles del archivo subido
    rutaDestino: genera la ruta donde se subira el archivo dentro de Dropbox formato: /user-id/año/mes/
    stopwatch: Unicamente devuelve el tiempo que tardo en realizarse una tarea
    getRemoteFilesList: Devuelve una lista de archivos/carpetas en una ruta especifica (no recursivo)
    updateSpace: Actualiza el espacio disponible en la API SCANDA restando el espacio usado
    downloadFile: Descarga un archivo en Dropbox, se le pasa una ruta ej: /1/2016/07/backup.bak
        (la ruta donde el archivo se descargara en la ruta configurada por el usuario)
'''

class Upload():
    # Token de la cuenta
    TOKEN = ""
    # tamano del bloque de subida MAX 150 MB
    CHUNK_SIZE = 1024 * 1024 * 10

    # Devuelve los datos del usuario y la lista de extensiones
    def getData(self):
        extensiones = []
        log = SetLog()
        l = Login()
        user = l.returnUserData()
        p = Preferences()
        spaceData = p.returnUserData()
        url = 'http://201.140.108.22:2017/DBProtector/Extensions_GET?User=' + user['user'] + '&Password=' + user['password']

        try:
            # Realiza la peticion
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            log.newLog("http_error", "E", e.fp.read())
        # Devuelve la info
        res = json.loads(response.read())
        # Extra todas las extensiones
        for val in res:
            # Si el inicio de sesion es correcto
            if val['Success'] == 1:
                # crea un arreglo con la lista de exteniones
                extensiones.append(val['Extension'].lower())
        user['ext'] = extensiones
        user['freeSpace'] = spaceData['freeSpace']
        user['space'] = spaceData['space']
        user['spaceUsed'] = spaceData['spaceUsed']
        return user

    # Devuelve la lista de archivos validos para ser subidos
    def getLocalFilesList(self, ruta, filtro):
        files = []
        log = SetLog()
        try:
            # lista de archivos completa
            ar = [f for f in os.listdir(ruta) if os.path.isfile(os.path.join(ruta, f))]
            ar = [f for f in ar if self.filtradoPorExtension(f, filtro)]
            for archivo in ar:
                files.append(archivo)
        except:
            log.newLog("error_path", "E", "")
            files = None
        return files
    # filtro = array de extensiones
    def filtradoPorExtension(self, archivo, filtro):
        if filtro is None:
            return True
        for x in filtro:
            if archivo.endswith(x):
                # if archivo.endswith(x.lower()):
                return True
        return False

    # Sube un archivo, solo recibe el nombre del archivo
    def uploadFile(self, file):
        log = SetLog()
        # Extrae los datos del usuario
        user = self.getData()
        # Si es un archivo / existe
        fullFile = os.path.join(user['path'], file)
        if os.path.isfile(fullFile):
            # Tamano en bytes
            size_bytes = os.path.getsize(fullFile)
            # Tamano en MB
            size = float(float(int(size_bytes) / 1024) / 1024)
            # Si el tamano del archivo es menor que el tamano disponible
            if size < user['freeSpace']:
                # Extrae el nombre, la extension y la fecha de modificacion del archivo
                name, ext = os.path.splitext(file)
                ext = ext.replace(".", "")
                mtime = os.path.getmtime(fullFile)
                # si la extension del archivo es valida...
                if ext in user['ext']:
                    # abre una sesion
                    dbx = dropbox.Dropbox(self.TOKEN)
                    # Ruta donde se almacenara
                    dest = self.rutaDestino(user['IdCustomer']) + name + "." + ext
                    # Abre el archivo
                    with open(fullFile, 'rb') as f:
                        # Si el archivo es mas grande que CHUNK_SIZE
                        if os.path.getsize(fullFile) <= self.CHUNK_SIZE:
                            data = f.read()
                            # Inicia la subida
                            with self.stopwatch('upload %d bytes' % len(data)):
                                try:
                                    res = dbx.files_upload(
                                        data, dest,
                                        client_modified=datetime.datetime(*time.gmtime(mtime)[:6]),
                                        mute=True)
                                    # Actualiza el espacio disponible del usuario
                                    self.updateSpace(user, size)
                                    return res
                                except dropbox.exceptions.ApiError as err:
                                    log.newLog("error_upload", "T", err)
                                    return None
                            #return res
                        # Subida de archivos Grandes
                        else:
                            with self.stopwatch('upload %d bytes' % size):
                                try:
                                    # Sube el archivo por bloques, maximo 150 mb
                                    upload_session_start_result = dbx.files_upload_session_start(f.read(self.CHUNK_SIZE))
                                    cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
                                                                               offset=f.tell())
                                    commit = dropbox.files.CommitInfo(path=dest)

                                    while f.tell() < size_bytes:
                                        # tamano subido y id de la sesion de subida
                                        #print str(upload_session_start_result.session_id) + " uploaded: " + str(f.tell())
                                        if ((size_bytes - f.tell()) <= self.CHUNK_SIZE):
                                            self.updateSpace(user, size)
                                            return dbx.files_upload_session_finish(f.read(self.CHUNK_SIZE), cursor, commit)
                                        else:
                                            dbx.files_upload_session_append(f.read(self.CHUNK_SIZE), cursor.session_id, cursor.offset)
                                            cursor.offset = f.tell()
                                except dropbox.exceptions.ApiError as err:
                                    log.newLog("error_upload", "T", err)
                                    # Error de subida
                                    return None
                else:
                    log.newLog("error_ext", "T", "Upload.uploadFile")
                    return 3
            else:
                log.newLog("error_size", "T", "Upload.uploadFile")
                # Espacio insuficiente
                return 2
        else:
            log.newLog("error_404", "T", "Upload.uploadFile")
            # Archivo invalido
            return 1

    # Devuelve la ruta donde se almacenara el archivo en Dropbox
    def rutaDestino(self, user_id):
        path = "/" + str(user_id) + "/"
        path = path + str(datetime.date.today().year) + "/"
        if datetime.date.today().month < 10:
            path = path + "0" + str(datetime.date.today().month)
        else:
            path = path + str(datetime.date.today().month)
        return path + "/"

    @contextlib.contextmanager
    # Context manager para mostrar el elapsed time
    def stopwatch(self, message):
        t0 = time.time()
        try:
            yield
        finally:
            t1 = time.time()
            print('Total elapsed time for %s: %.3f' % (message, t1 - t0))

    # Devuelve la lista de respaldos
    def getRemoteFilesList(self, ruta):
        files = []
        cliente = DropboxClient(self.TOKEN)
        respuesta = cliente.metadata(ruta)
        for file in respuesta["contents"]:
            files.append(file["path"])
        return files

    def getAllRemoteFilesList(self, user_id):
        files = []
        cliente = DropboxClient(self.TOKEN)
        respuesta = cliente.metadata("/" + str(user_id) + "/")
        for anio in respuesta["contents"]:
            meses = cliente.metadata(str(anio["path"]))
            for mes in meses["contents"]:
                backups = cliente.metadata(str(mes["path"]))
                for file in backups["contents"]:
                    files.append(file["path"])
        return files

    # Actualiza los datos de espacio del usuario en la Api de SCANDA
    def updateSpace(self, user, spaceFile):
        log = SetLog()
        space = int(user["spaceUsed"]) + int(spaceFile)
        url = 'http://201.140.108.22:2017/DBProtector/CustomerStorage_SET?UsedStorage=' + str(space) + '&User=' + user['user'] + '&Password=' + user['password']

        try:
            # Realiza la peticion
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            log.newLog("http_error", "E", e.fp.read())
        # Devuelve la info
        res = json.loads(response.read())
        if res['Success'] == 1:
            return True
        else:
            log.newLog("login_api_error", "E", "")
            return False

    def downloadFile(self, user, file):
        # Extrae el nombre, la extension del archivo
        dir, name = os.path.split(file)
        # Archivo local donde se almacenara
        localFile = os.path.join(user['path'], name)
        from dropbox.client import DropboxClient
        cliente = DropboxClient(self.TOKEN)
        with self.stopwatch('download'):
            try:
                out = open(localFile, 'wb')
                with cliente.get_file(file) as f:
                    out.write(f.read())
                return True
            except dropbox.exceptions.HttpError as err:
                print('*** HTTP error', err)
                return False

    def sync(self):
        from SetLog import SetLog
        log = SetLog()
        # Usado para comprimir el archivo
        from Compress import Compress
        zip = Compress()
        # Extrae la info del usuario
        user = self.getData()
        # Lista de archivos validos para ser subidos
        files = self.getLocalFilesList(user["path"], user["ext"])
        for file in files:
            name, ext = file.split(".")
            file = os.path.join(user["path"], file)
            # Comprime el archivo
            if zip.compress(file):
                # Datos del archivo subido
                data = self.uploadFile(name + ".zip")
            else:
                log.newLog("error_compress", "E", "")

    # El archivo ya ha sido subido? si la fecha de modificacion/contenido es diferente sube el archivo
    def isFileSynced(self, file):
        vals = file.split(".")
        name = vals[0]
        ext = vals[1]
        fileSearch = name + "." + ext
        files = []
        cliente = DropboxClient(self.TOKEN)

'''
app = Upload()
app.sync()
'''