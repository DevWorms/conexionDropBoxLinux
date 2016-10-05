#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
import base64
import contextlib
import json
import os
import os.path
import re
import threading
import urllib2
import datetime
import time

import dropbox
import thread
from dropbox.client import DropboxClient
from stat import S_ISREG, ST_CTIME, ST_MODE

from xamai.BackgroundProcess import BackgroundProcess
from xamai.Login import Login
from xamai.Preferences import Preferences
from xamai.SetLog import SetLog
from xamai.Compress import Compress
from xamai.Crons import Cron
from xamai.Crypt import Crypt
from xamai.Status import Status
import xamai.Constants as const


class Upload():
    # Token de la cuenta
    crypt = Crypt()
    TOKEN = base64.b64decode(
        repr(
            crypt.obfuscate(
                '*]BC.f3W&\x04\x10\n\x13\x004&!a51&e4&!a5&!t8\x12#N\x1b\x05.J<\x0e\x12\x07*A&](\x16>c!!\x15x\x1a\x15"Z%\x1a"\\\x15W)\x05\x170\x15\x00\x020>b1F%h8#?q\x1b\x07"aOY'.decode('utf-8')
            )
        )
    )

    THIS_FILE = os.path.realpath(__file__)
    file = THIS_FILE.split("/")
    THIS_FILE = file[-1] + "." + "Upload()"

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
        except HTTPError as e:
            log.newLog(self.THIS_FILE + "." + "getData()", "http_error", "E", 'Codigo: ', e.code)
        except URLError as e:
            log.newLog(self.THIS_FILE + "." + "getData()", "http_error", "E", 'Reason: ', e.reason)
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
        user['FileHistoricalNumberCloud'] = spaceData['FileHistoricalNumberCloud']
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
            log.newLog(self.THIS_FILE + "." + "getLocalFilesList()", "error_path", "E", "")
            files = None
        return files

    # Valida que no haya otra subida en progreso, usando Status
    def checkUpload(self):
        s = Status()
        status = s.getUploadStatus()
        if status['status'] == 0 or status['status'] == 3:
            return True
        else:
            return False

    # valida si el formato del nombre del archivo es valido
    def checkNameSintax(self, file):
        if not re.match(r"([A-Za-z]{3,4}[0-9]{6}[A-Za-z0-9]{3})([0-9]{14}).(\w{3})", file):
            return False
        else:
            return True

    # filtra un archivo por extension filtro = array de extensiones
    def filtradoPorExtension(self, archivo, filtro):
        archivo = archivo.lower()
        filtro = [x.lower() for x in filtro]

        if filtro is None:
            return True
        for x in filtro:
            if archivo.endswith(x):
                return True
        return False

    def bytesToMB(self, bytes):
        mb = float(float(int(bytes) / 1024) / 1024)
        mb = float(mb) + float(0.5)
        mb = round(mb)
        return int(mb)

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
            size = self.bytesToMB(size_bytes)
            # Si el tamano del archivo es menor que el tamano disponible
            if size < user['freeSpace'] or user['freeSpace'] == -1:
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
                        # Envia log, iniciando subida
                        log.newLog(self.THIS_FILE + "." + "uploadFile()", "upload_start", "T", file)
                        # Si el archivo es mas grande que CHUNK_SIZE
                        if os.path.getsize(fullFile) <= const.CHUNK_SIZE:
                            data = f.read()
                            # Inicia la subida
                            with self.stopwatch('Subido %d MB' % len(data)):
                                try:
                                    # Registra que se inicia la subida
                                    threading.Thread(target=status.setUploadStatus,
                                                     args=(file, str(0), str(self.bytesToMB(size_bytes)), 1,)).start()
                                    res = dbx.files_upload(data, dest)
                                    # "borrando archivo: "
                                    os.remove(fullFile)
                                    # Notifica a la API
                                    log.newLog(self.THIS_FILE + "." + "uploadFile()", "success_upload", "T", file)
                                    # Registra que se termino la subida
                                    threading.Thread(target=status.setUploadStatus, args=(file, str(self.bytesToMB(size_bytes)), str(self.bytesToMB(size_bytes)), 2,)).start()
                                    # Notifica que elimina archivos temporales
                                    log.newLog(self.THIS_FILE + "." + "uploadFile()", "delete_temporary_files", "T", fullFile)
                                    # Actualiza el espacio disponible del usuario
                                    self.updateSpace(user, size)
                                    # que se hace con el archivo?, accion después de subir
                                    name_bak, ext_bak, zip_ext = file.split(".")
                                    self.actionAfterUpload(name_bak + "." + ext_bak)
                                    return res
                                except dropbox.exceptions.ApiError as err:
                                    # eliminar archivo
                                    os.remove(fullFile)
                                    # Notifica que elimina archivos temporales
                                    log.newLog(self.THIS_FILE + "." + "uploadFile()", "delete_temporary_files", "E", fullFile)
                                    # Envia el error
                                    log.newLog(self.THIS_FILE + "." + "uploadFile()", "error_upload", "E", str(err))
                                    return None
                        # Subida de archivos Grandes
                        else:
                            total_chunk = self.bytesToMB(size_bytes)
                            actual_chunk = 0
                            with self.stopwatch('upload %d MB' % size):
                                try:
                                    # Sube el archivo por bloques, maximo 150 mb
                                    upload_session_start_result = dbx.files_upload_session_start(f.read(const.CHUNK_SIZE))
                                    cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
                                                                               offset=f.tell())
                                    commit = dropbox.files.CommitInfo(path=dest)

                                    while f.tell() < size_bytes:
                                        actual_chunk = actual_chunk + const.CHUNK_SIZE
                                        # tamano subido y id de la sesion de subida
                                        if ((size_bytes - f.tell()) <= const.CHUNK_SIZE):
                                            # Sube el ulimo chunk
                                            res = dbx.files_upload_session_finish(f.read(const.CHUNK_SIZE), cursor,
                                                                                  commit)
                                            # Envia ell ultimo log, cerrando la transaccion
                                            threading.Thread(target=status.setUploadStatus, args=(file, str(total_chunk), str(total_chunk), 2,)).start()
                                            self.updateSpace(user, size)
                                            # "borrando archivo: "
                                            os.remove(fullFile)
                                            # Notifica a la API
                                            log.newLog(self.THIS_FILE + "." + "uploadFile()", "success_upload", "T", file)
                                            # Notifica que elimina archivos temporales
                                            log.newLog(self.THIS_FILE + "." + "uploadFile()", "delete_temporary_files", "T", fullFile)
                                            # que se hace con el archivo?, accion después de subir
                                            name_bak, ext_bak, zip_ext = file.split(".")
                                            self.actionAfterUpload(name_bak + "." + ext_bak)
                                        else:
                                            # Muestra al usuario que se esta subiendo
                                            threading.Thread(target=status.setUploadStatus,
                                                             args=(file, str(self.bytesToMB(actual_chunk)), str(total_chunk), 1,)).start()
                                            dbx.files_upload_session_append(f.read(const.CHUNK_SIZE), cursor.session_id, cursor.offset)
                                            cursor.offset = f.tell()
                                except dropbox.exceptions.ApiError as err:
                                    # "borrando archivo: "
                                    os.remove(fullFile)
                                    log.newLog(self.THIS_FILE + "." + "uploadFile()", "delete_temporary_files", "E", fullFile)
                                    log.newLog(self.THIS_FILE + "." + "uploadFile()", "error_upload", "E", str(err))
                                    return None
                else:
                    # extension invalida
                    log.newLog(self.THIS_FILE + "." + "uploadFile()", "error_ext", "E", ext)
                    return None
            else:
                log.newLog(self.THIS_FILE + "." + "uploadFile()", "error_size", "E", "")
                # Espacio insuficiente
                return None
        else:
            # Archivo invalido
            log.newLog(self.THIS_FILE + "." + "uploadFile()", "error_404", "E", file)
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
        dbx = dropbox.Dropbox(self.TOKEN)
        res = dbx.files_list_folder(ruta)

        for file in res.entries:
            files.append(file.path_display)
        return files

    # para evitar el error 404 crea un archivo nulo y despu[es lo elimina
    def creaFolder(self, path):
        dbx = dropbox.Dropbox(self.TOKEN)
        res = dbx.files_upload("", os.path.join(path, "init"))
        dbx.files_delete(os.path.join(path, "init"))

    # devuelve la lista completa de respaldos de un usario
    def getAllRemoteFilesList(self, user_id):
        files = []
        dbx = dropbox.Dropbox(self.TOKEN)
        res = dbx.files_list_folder("/" + str(user_id) + "/")
        for anio in res.entries:
            meses = dbx.files_list_folder(str(anio.path_display))
            for mes in meses.entries:
                backups = dbx.files_list_folder(str(mes.path_display))
                for file in backups.entries:
                    files.append(file.path_display)
        return files

    # Devuelve una lista de respaldos en una ruta ordenados de mas nuevo a mas viejo
    def getBackups(self, ruta):
        self.creaFolder(ruta)
        files = []
        dbx = dropbox.Dropbox(self.TOKEN)
        respuesta = dbx.files_list_folder(ruta)
        for file in respuesta.entries:
            files.append(file)
        files = sorted(files, key=lambda file: file.client_modified)
        return files

    # acomoda los respaldos separaqdos por RFC
    def formatBackups(self, backs):
        rfc = []
        for back in backs:
            m = re.search("[A-Za-z]{3,4}[0-9]{6}[A-Za-z0-9]{3}", back)
            if m:
                rfc.append(m.group(0))

        rfc = set(rfc)
        w, h = len(backs), len(rfc)
        final = [[0 for x in range(w)] for y in range(h)]
        n = 0
        for r in rfc:
            final[n] = []
            for back in backs:
                if r in back:
                    final[n].append(back)
            n = n + 1
        return final

    # devuelve todos los respaldos ordenados por fecha, del mas viejo al mas nuevo, se usara para el historical cloud
    def getAllBackupsByDate(self):
        user = self.getData()
        files = []
        dbx = dropbox.Dropbox(self.TOKEN)
        respuesta = dbx.files_list_folder("/" + str(user['IdCustomer']) + "/")
        for anio in respuesta.entries:
            meses = dbx.files_list_folder(str(anio.path_display))
            for mes in meses.entries:
                backups = dbx.files_list_folder(str(mes.path_display))
                for file in backups.entries:
                    files.append(file)
        files = sorted(files, key=lambda file: file.client_modified, reverse=False)
        return files

    '''
        Extrae el maximo de respaldos permitidos en la nube, si el numero de respaldos en la
        nube es mayor, borra el mas viejo, hasta que se menor al limite
    '''
    def historicalCloud(self):
        user = self.getData()
        dbx = dropbox.Dropbox(self.TOKEN)
        while len(self.getAllBackupsByDate()) >= user['FileHistoricalNumberCloud']:
            file = self.getAllBackupsByDate()[0]
            # Resta en la api
            tamanio = -1 * ((file.size/1024)/1024)
            self.updateSpace(user, tamanio)
            dbx.files_delete(file.path_display)

    # Devuelve el ultimo respaldo exitoso de cada RFC
    def getLastSuccess(self):
        # lista todos los respaldos
        l = Login()
        user = l.returnUserData()
        backs = self.getAllRemoteFilesList(user["IdCustomer"])

        backup = []
        rfc = []
        tmp = []

        # crea una lista unica de rfc's
        for back in backs:
            m = re.search("[A-Za-z]{3,4}[0-9]{6}[A-Za-z0-9]{3}", back)
            if m:
                rfc.append(m.group(0))
        rfc = set(rfc)

        # crea un arreglo de respaldos por cada rfc, los ordena por fecha y devuelve el primero
        for r in rfc:
            for back in backs:
                if r in back:
                    tmp.append(back)
                tmp = sorted(tmp, reverse = True)
            backup.append(tmp[0])
            tmp = []

        backup = set(backup)
        backup = sorted(backup)

        return backup

    # Devuelve la fecha de un respaldo
    def getDateFromBackup(self, backup):
        from datetime import datetime
        dbx = dropbox.Dropbox(self.TOKEN)
        respuesta = dbx.files_get_metadata(backup)
        return str(respuesta.client_modified)

    # Actualiza los datos de espacio del usuario en la Api de SCANDA
    def updateSpace(self, user, spaceFile):
        log = SetLog()
        space = int(user["spaceUsed"]) + int(spaceFile)
        if space < 0:
            space = 0
        url = const.IP_SERVER + '/DBProtector/CustomerStorage_SET?UsedStorage=' + str(space) + '&User=' + user['user'] + '&Password=' + user['password']

        try:
            # Realiza la peticion
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
        except HTTPError as e:
            log.newLog(self.THIS_FILE + "." + "updateSpace()", "http_error", "E", 'Codigo: ', e.code)
        except URLError as e:
            log.newLog(self.THIS_FILE + "." + "updateSpace()", "http_error", "E", 'Reason: ', e.reason)
        # Devuelve la info
        res = json.loads(response.read())
        if res['Success'] == 1:
            return True
        else:
            log.newLog(self.THIS_FILE + "." + "updateSpace()", "login_api_error", "E", "")
            return False

    # Descarga un archivo
    def downloadFile(self, file, path):
        from dropbox.client import DropboxClient
        log = SetLog()
        status = Status()
        # Usado para comprimir el archivo
        zip = Compress()
        # Extrae el nombre, la extension del archivo
        dir, name = os.path.split(file)
        # Archivo local donde se almacenara
        localFile = os.path.join(path, name)
        threading.Thread(target=status.setDownloadstatus, args=(name, path, 1,)).start()
        log.newLog(self.THIS_FILE + "." + "downloadFile()", "start_download", "T", file)
        with self.stopwatch('downloading'):
            try:
                dbx = dropbox.Dropbox(self.TOKEN)
                dbx.files_download_to_file(localFile, file)
            except dropbox.files.DownloadError as err:
                log.newLog(self.THIS_FILE + "." + "downloadFile()", "error_download", "E", str(err))
            except dropbox.exceptions.ApiError as err:
                log.newLog(self.THIS_FILE + "." + "downloadFile()", "error_download", "E", str(err))

        if os.path.exists(localFile):
            threading.Thread(target=status.setDownloadstatus, args=(name, path, 2,)).start()
            log.newLog(self.THIS_FILE + "." + "downloadFile()", "start_uncompress", "T", localFile)
            zip.uncompress(localFile)
            log.newLog(self.THIS_FILE + "." + "downloadFile()", "success_uncompress", "T", localFile)
            log.newLog(self.THIS_FILE + "." + "downloadFile()", "success_download", "T", file)
            threading.Thread(target=status.setDownloadstatus, args=(name, path, 0,)).start()
            return True
        else:
            log.newLog(self.THIS_FILE + "." + "downloadFile()", "error_download", "E", file)
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
            if os.path.exists(file):
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
            log.newLog(self.THIS_FILE + "." + "prepareExternalPath()", "error_path", "E", "")

    '''
        Realiza todas las validaciones, cifra el archivo y lo sube
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
            if not user["path"]:
                log.newLog(self.THIS_FILE + "." + "sync()", "no_path_no_sync", "E", "")
            else:
                # Si la carpeta de usuario no existe la crea
                if not os.path.exists(user["path"]):
                    os.makedirs()
                # Lista de archivos validos para ser subidos
                files = self.getLocalFilesList(user["path"], user["ext"])
                if not files:
                    threading.Thread(target=status.setUploadStatus, args=("file.bak", 1, 1, 0,)).start()
                else:
                    for file in files:
                        # si hay mas respaldos de los permitidos los elimina
                        self.historicalCloud()
                        if not background.isRunning():
                            name, ext = file.split(".")
                            file = os.path.join(user["path"], file)
                            # actualiza el estado de la aplicacion a cifrando
                            threading.Thread(target=status.setUploadStatus, args=(name + ".zip", 1, 1, 3,)).start()
                            # Envia un log, Iniciando compresion
                            log.newLog(self.THIS_FILE + "." + "sync()", "compress_start", "T", "")
                            if zip.compress(file): # Comprime el archivo
                                # Envia un log, Finalizando compresion
                                log.newLog(self.THIS_FILE + "." + "sync()", "compress_finish", "T", "")
                                # Datos del archivo subido
                                self.uploadFile(name + "." + ext + ".zip")
                                # Elimina el archivo, si no se elimino
                                if os.path.isfile(file):
                                    os.remove(file)
                                    # Envia un log, Eliminando archivo
                                    log.newLog(self.THIS_FILE + "." + "sync()", "delete_local_file", "T", file)
                                # actualiza el estado de la aplicacion a sincronizado
                                #threading.Thread(target=status.setUploadStatus, args=(file, 1, 1, 0,)).start()
                            else:
                                if os.path.isfile(file):
                                    os.remove(file)
                                log.newLog(self.THIS_FILE + "." + "sync()", "error_compress", "E", "")
                        else:
                            log.newLog(self.THIS_FILE + "." + "sync()", "background_exists", "E", "")
                '''
                    Una vez que se han terminado las subidas, se sincroniza con la api
                    para actualizar la frecuencia de respaldo y generar un nuevo cron
                '''
                c = Cron()
                # Sincroniza de nuevo con la frecuencia de respaldo de la api
                threading.Thread(target=c.cloudSync).start()
                # Devuelve el status a sincronizado
                threading.Thread(target=status.setUploadStatus, args=(file, 1, 1, 0,)).start()

        else:
            print "Existe otra subida en proceso"
            log.newLog(self.THIS_FILE + "." + "sync()", "error_upload_exist", "E", "")