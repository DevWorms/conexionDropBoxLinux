#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import contextlib
import datetime
import json
import os
import os.path
import re
import time
import urllib2

import dropbox
from dropbox.client import DropboxClient
from stat import S_ISREG, ST_CTIME, ST_MODE

from scanda.BackgroundProcess import BackgroundProcess
from scanda.Login import Login
from scanda.Preferences import Preferences
from scanda.SetLog import SetLog
from scanda.Compress import Compress
from scanda.Crons import Cron
from scanda.Crypt import Crypt
from scanda.Status import Status
import scanda.Constants as const

'''
    Metodos usados para trabajar con la API de Dropbox
        Estructura de carpetas en Dropbox
            /Aplicaciones/DBProtector/user-id/año/mes/archivo
        Estructura de carpetas en Aplicacion Dropbox
            /user-id/año/mes/archivo
            la Api trabaja a nivel Root de la aplicacion, ej: /1/2016/07
        Validaciones:
            -valida que no exista otra subida en curso
            -Archivo existe?
            -El tamaño del archivo debe ser menor al espacio disponible (proporcionado por la API de SCANDA)
            -El archivo debe tener una extension valida (proporcionado por la API de SCANDA)
            -Debe seguir un formato de nombre valido ej. LOMS9208164C520160725150501.bak LOMS920816---20160725150501.bak
            -Si el archivo es mayor que CHUNK_SIZE (5MB) se sube por bloques, si es menor o igual se sube en una sola solicitud
        - Return
            - 1 = Archivo inexistente
            - 2 = Espacio insuficiente
            - 3 = Extension invalida
            - None = El archivo no se subio
            - res = JSON array con los detalles del archivo subido
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
                '*]BC.f3W&\x04\x10\n\x13\x004&!a51&e4&!a5&!t8\x12#N\x1b\x05.J<\x0e\x12\x07*A&](\x16>c!!\x15x\x1a\x15"Z%\x1a"\\\x15W)\x05\x170\x15\x00\x020>b1F%h8#?q\x1b\x07"aOY'.decode('utf-8')
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
            ar = [file for file in os.listdir(ruta) if os.path.isfile(os.path.join(ruta, file))]
            # valida los archivos por extension permitida
            ar = [file for file in ar if self.filtradoPorExtension(file, filtro)]
            ar = [file for file in ar if self.checkNameSintax(file)]
            for archivo in ar:
                files.append(archivo)
        except:
            log.newLog("error_path", "E", "")
            files = None
        return files

    # Valida que no haya otra subida en progreso, usando Status
    def checkUpload(self):
        s = Status()
        status = s.getUploadStatus()
        if status['status'] == 0:
            return True
        else:
            return False

    # valida si el formato del nombre del archivo es valido
    def checkNameSintax(self, file):
        if not re.match(r"([A-Zz-z]{4}\d{6})(---|\w{3})?(\d{14}).(\w{3})", file):
            return False
        else:
            return True

    # filtra un archivo por extension filtro = array de extensiones
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
                                    log.newLog("success_upload", "T", file)
                                    # Muestra al usuario, que se subio el archivo
                                    status.setUploadStatus(file, str(f.tell()), str(size_bytes), 2)
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
                                            status.setUploadStatus(file, f.tell(), size_bytes, 2)
                                            res = dbx.files_upload_session_finish(f.read(const.CHUNK_SIZE), cursor, commit)
                                            self.updateSpace(user, size)
                                            # "borrando archivo: "
                                            os.remove(fullFile)
                                            # Notifica a la API
                                            log.newLog("success_upload", "T", "")
                                        else:
                                            # Muestra al usuario que se esta subiendo
                                            status.setUploadStatus(file, f.tell(), size_bytes, 1)
                                            dbx.files_upload_session_append(f.read(const.CHUNK_SIZE), cursor.session_id, cursor.offset)
                                            cursor.offset = f.tell()
                                except dropbox.exceptions.ApiError as err:
                                    # "borrando archivo: "
                                    os.remove(fullFile)
                                    log.newLog("error_upload", "T", "")
                                    return None
                else:
                    # extension invalida
                    log.newLog("error_ext", "T", ext)
                    return None
            else:
                log.newLog("error_size", "T", "")
                # Espacio insuficiente
                return None
        else:
            # Archivo invalido
            log.newLog("error_404", "T", file)
            return None

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
        self.creaFolder(ruta)
        files = []
        cliente = DropboxClient(self.TOKEN)
        respuesta = cliente.metadata(ruta)
        for file in respuesta["contents"]:
            files.append(file["path"])
        return files

    def creaFolder(self, path):
        dbx = dropbox.Dropbox(self.TOKEN)
        res = dbx.files_upload("", os.path.join(path, "init"))
        dbx.files_delete(os.path.join(path, "init"))

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
                with self.stopwatch("download"):
                    with cliente.get_file(file) as f:
                        out.write(f.read())
            except dropbox.exceptions.HttpError as err:
                log.newLog("error_download", "T", file)
                return False
        out.close()

        if os.path.exists(localFile):
            zip.uncompress(localFile)
            log.newLog("success_download", "T", file)
            return True
        else:
            log.newLog("error_download", "T", file)
            return False

    '''
        Que se hace con el archivo original, despues de respaldarlo?
        recibe solo el nombre del archivo, no la ruta completa
    '''
    def actionAfterUpload(self, file):
        c = Cron()
        user = self.getData()
        action = c.getCloudSync()
        # si la accion es 1, mueve el archivo a la carpeta "respaldados"
        if action['FileTreatmen'] == 1:
            dest = os.path.join(user['path'], "respaldados")
            # si la carpeta no existe, la crea
            if not os.path.exists(dest):
                os.makedirs(dest)
            # mueve el; archivo
            os.rename(os.path.join(user['path'], file), os.path.join(dest, file))
        # se mueve el archivo a la carpeta configurada por el user, si no existe, se mueve a respaldados
        elif action['FileTreatmen'] == 2:
            # Elimina los backups viejos para que solo quede la cantidad permitida
            self.prepareExternalPath(action)
            p = Preferences()
            # una vez que el espacio tiene la cantidad de respaldos adecuada, mueve el archivo
            os.rename(os.path.join(user['path'], file), os.path.join(p.returnExternalPath(), file))
        # si la accion es 3, elimina el archivo
        elif action['FileTreatmen'] == 3:
            os.remove(file)

    '''
        si el numero de respaldos en la carpeta externa es mayor que FileHistoricalNumber
        borra el mas antiguo
        recibe como parametro una instancia de Cron().getCloudSync()
    '''
    def prepareExternalPath(self, args):
        p = Preferences()
        log = SetLog()
        path = p.returnExternalPath()
        try:
            while len(os.listdir(path)) >= args['FileHistoricalNumber']:
                # lista de archivos completa
                files = (os.path.join(path, file) for file in os.listdir(path))
                files = ((os.stat(path), path) for path in files)
                # fecha de modificacion
                files = ((stat[ST_CTIME], path)
                           for stat, path in files if S_ISREG(stat[ST_MODE]))
                # ordena de mas viejo al mas nuevo
                files = sorted(files)
                os.remove(files[0][1])

        except:
            log.newLog("error_path", "E", "")

    '''
        Sincroniza los archivos en la nube
    '''
    def sync(self):
        log = SetLog()
        if self.checkUpload():
            status = Status()
            background = BackgroundProcess()
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
                    # actualiza el estado de la aplicacion a sincronizado
                    status.setUploadStatus(file, 1, 1, 3)
                    if zip.compress(file):
                        # Datos del archivo subido
                        data = self.uploadFile(name + ".zip")
                        # que se hace con el archivo?
                        self.actionAfterUpload(file)
                        # actualiza el estado de la aplicacion a sincronizado
                        status.setUploadStatus(file, 1, 1, 0)
                    else:
                        if os.path.isfile(os.path.join(user['path'], file)):
                            os.remove(os.path.join(user['path'], file))
                        log.newLog("error_compress", "T", "")
                else:
                    log.newLog("background_exists", "T", "")
            '''
                Una vez que se han terminado las subidas, se sincroniza con la api
                para actualizar la frecuencia de respaldo y generar un nuevo cron
            '''
            c = Cron()
            c.cloudSync()
        else:
            log.newLog("error_upload_exist", "T", "")