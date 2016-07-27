#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import contextlib
import datetime
import json
import os
import os.path
import time
import urllib2

import dropbox
from dropbox.client import DropboxClient

from scanda.BackgroundProcess import BackgroundProcess
from scanda.Login import Login
from scanda.Preferences import Preferences
from scanda.SetLog import SetLog
from scanda.Compress import Compress
from scanda.Crons import Cron
from scanda.Crypt import Crypt
import scanda.Constants as const

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
            -Si el archivo es mayor que CHUNK_SIZE (5MB) se sube por bloques, si es menor o igual se sube en una sola solicitud
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

    app = Upload()
    app.sync()
'''

class Upload():
    # Token de la cuenta
    crypt = Crypt()
    '''
        Para mas info leer Crypt.py
    '''
    TOKEN = base64.b64decode(
        repr(
            crypt.obfuscate(
                '*]BC.f3W&\x04\x10\n\x13\x004&!a51&e4&!a55"w\x16P)Z\x03:"d\x16""s=C\x13]\x1eV\x11X=8&\x034)\x14\x04=1:x \x0e\x13\x06\x17F\x13f81>\x04\x14F\x13]GP\x13l\x17$$GOY'.decode('utf-8')
            )
        )
    )

    # Devuelve los datos del usuario y la lista de extensiones
    def getData(self):
        extensiones = []
        log = SetLog()
        l = Login()
        user = l.returnUserData()
        p = Preferences()
        spaceData = p.returnUserData()
        url = const.IP_SERVER + '/DBProtector/Extensions_GET?User=' + user['user'] + '&Password=' + user['password']

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
        from scanda.Status import Status
        log = SetLog()
        status = Status()
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
                    dest = self.pathToUpload(user['IdCustomer']) + name + "." + ext
                    # Abre el archivo
                    with open(fullFile, 'rb') as f:
                        # Si el archivo es mas grande que CHUNK_SIZE
                        if os.path.getsize(fullFile) <= const.CHUNK_SIZE:
                            data = f.read()
                            # Inicia la subida
                            with self.stopwatch('upload %d MB' % len(data)):
                                try:
                                    res = dbx.files_upload(data, dest)
                                    # "borrando archivo: "
                                    os.remove(fullFile)
                                    # Notifica a la API
                                    log.newLog("success_upload", "T", "")
                                    # Muestra al usuario, que se subio el archivo
                                    status.setDownloadStatus(file, str(f.tell()), str(size_bytes), 2)
                                    # Actualiza el espacio disponible del usuario
                                    self.updateSpace(user, size)
                                    return res
                                except dropbox.exceptions.ApiError as err:
                                    # eliminar archivo
                                    os.remove(fullFile)
                                    log.newLog("error_upload", "T", "")
                                    # los logs de dropbox son demasiado grandes para ser enviados como log
                                    #print err
                                    return None
                            #return res
                        # Subida de archivos Grandes
                        else:
                            with self.stopwatch('upload %d MB' % size):
                                try:
                                    # Sube el archivo por bloques, maximo 150 mb
                                    upload_session_start_result = dbx.files_upload_session_start(f.read(const.CHUNK_SIZE))
                                    cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
                                                                               offset=f.tell())
                                    commit = dropbox.files.CommitInfo(path=dest)

                                    while f.tell() < size_bytes:
                                        # tamano subido y id de la sesion de subida
                                        if ((size_bytes - f.tell()) <= const.CHUNK_SIZE):
                                            # Muestra al usuario que se esta subiendo
                                            status.setDownloadStatus(file, f.tell(), size_bytes, 2)
                                            res = dbx.files_upload_session_finish(f.read(const.CHUNK_SIZE), cursor, commit)
                                            self.updateSpace(user, size)
                                            # "borrando archivo: "
                                            os.remove(fullFile)
                                            # Notifica a la API
                                            log.newLog("success_upload", "T", "")
                                        else:
                                            # Muestra al usuario que se esta subiendo
                                            status.setDownloadStatus(file, f.tell(), size_bytes, 1)
                                            dbx.files_upload_session_append(f.read(const.CHUNK_SIZE), cursor.session_id, cursor.offset)
                                            cursor.offset = f.tell()
                                except dropbox.exceptions.ApiError as err:
                                    # "borrando archivo: "
                                    os.remove(fullFile)
                                    log.newLog("error_upload", "T", "")
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
    def pathToUpload(self, user_id):
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

    # Devuelve la lista de archivos por una ruta
    def getRemoteFilesList(self, ruta):
        files = []
        cliente = DropboxClient(self.TOKEN)
        respuesta = cliente.metadata(ruta)
        for file in respuesta["contents"]:
            files.append(file["path"])
        return files

    # devuelve la lista completa de respaldos de un usario
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
        url = const.IP_SERVER + '/DBProtector/CustomerStorage_SET?UsedStorage=' + str(space) + '&User=' + user['user'] + '&Password=' + user['password']

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
        log = SetLog()
        # Usado para comprimir el archivo
        zip = Compress()
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
                zip.uncompress(localFile)
                os.remove(localFile)
                log.newLog("success_download", "T", file)
                return True
            except dropbox.exceptions.HttpError as err:
                log.newLog()
                return False

    '''
        Que se hace con el archivo original, despues de respaldarlo?
        recibe solo el nombre del archivo, no la ruta completa
    '''
    def actionAfterUpload(self, file):
        c = Cron()
        user = self.getData()
        action = c.getCloudSync()
        # si la accion es 1, mueve el archivo a la carpeta "uploaded"
        if action['FileTreatmen'] == 1:
            dest = os.path.join(user['path'], "uploaded")
            # si la carpeta no existe, la crea
            if not os.path.exists(dest):
                os.makedirs(dest)
            # mueve el; archivo
            os.rename(os.path.join(user['path'], file), os.path.join(dest, file))
        elif action['FileTreatmen'] == 2:
            dest = "/home/baclups"
            os.rename(os.path.join(user['path'], file), os.path.join(dest, file))
        # si la accion es 3, elimina el archivo
        elif action['FileTreatmen'] == 3:
            os.remove(file)


    def sync(self):
        background = BackgroundProcess()
        from scanda.SetLog import SetLog
        log = SetLog()
        # Usado para comprimir el archivo
        zip = Compress()
        # Extrae la info del usuario
        user = self.getData()
        # Lista de archivos validos para ser subidos
        files = self.getLocalFilesList(user["path"], user["ext"])
        for file in files:
            if not background.isRunning():
                name, ext = file.split(".")
                file = os.path.join(user["path"], file)
                # Comprime el archivo
                if zip.compress(file):
                    # Datos del archivo subido
                    data = self.uploadFile(name + ".zip")
                    # que se hace con el archivo?
                    self.actionAfterUpload(file)
                else:
                    if os.path.isfile(os.path.join(user['path'], file)):
                        os.remove(os.path.join(user['path'], file))
                    log.newLog("error_compress", "E", "")
        '''
            Una vez que se han terminado las subidas, se sincroniza con la api
            para actualizar la frecuencia de respaldo y generar un nuevo cron
        '''
        c = Cron()
        c.cloudSync()

app =Upload()
app.sync()