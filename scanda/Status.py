import json
import os
import urllib2

from decimal import Decimal
from time import gmtime, strftime
from scanda.SetLog import SetLog
from scanda.Login import Login
import scanda.Constants as const

class Status():
    # obtiene el status de la descarga
    def getDownloadStatus(self):
        # logs
        log = SetLog()
        data = []

        file = os.path.join(const.LOCATION, const.STATUS_FILE)
        # Si el archivo existe...
        if (os.path.exists(file)):
            # abre el archivo y lee los datos
            with open(file, 'r') as f:
                data = json.load(f)
            upload = data['upload']
            if upload['status'] != 0:
                if upload['chunk'] == 0 or upload['total'] == 0:
                    upload['chunk'] = 0
                    upload['total'] = 0
                else:
                    upload['chunk'] = self.returnPercent(int(upload['total']), int(upload['chunk']))
                    upload['total'] = (int(upload['total']) / 1024) / 1024
        else:
            log.newLog("error_file_status", "E", "")
        return upload

    # carga el status de la subida (se usa cada que se inicia un chunk)
    def setDownloadStatus(self, fileUploaded, chunk, total, status):
        # logs
        log = SetLog()

        # Carga el status de la subida a nivel local
        file = os.path.join(const.LOCATION, const.STATUS_FILE)
        # Si el archivo existe...
        if (os.path.exists(file)):
            #guarda los datos anteriores
            with open(file, 'r') as f:
                data = json.load(f)
            # abre el archivo y escribe los datos
            with open(file, 'w') as f:
                json.dump({
                    'upload': {
                        'file': fileUploaded,
                        'chunk': chunk,
                        'total': total,
                        'status': status
                    },
                    'download': data['download']
                }, f)

        else:
            log.newLog("error_file_status", "E", "")

        # cargar el status de la subida en la API SCANDA

        # extrae la infor del user
        l = Login()
        user = l.returnUserData()
        # extrae la fecha actual formateada
        date = strftime("%Y%m%d%H%M%S", gmtime())

        # valida el status de la subida
        if status == 1: # 1 para carga iniciada
            #i el chunk es de 5mb, entonces es el primero en subirse
            if chunk == 5242880: # tamano del chunk de 5MB
                # Url de la api REST para la subida de archivos
                url = const.IP_SERVER + '/DBProtector/FileTransaction_SET?User=' + user['user'] + '&Password=' + \
                      user['password'] + '&StartDate=' + date + '&ActualChunk=' + str(chunk) + '&TotalChunk=' + \
                      str(total) + '&Status=EnProgreso&FileName=' + fileUploaded
            # si el es diferente de 5 mb, se esta actualizando
            else:
                # Url de la api REST para la subida de archivos
                url = const.IP_SERVER + '/DBProtector/FileTransaction_UPDATE?User=' + user['user'] + '&Password=' + \
                      user['password'] + '&ActualChunk='+str(chunk)+'&Status=EnProgreso&FileName=' + fileUploaded
        elif status == 2:
            # Url de la api REST para la subida de archivos
            url = const.IP_SERVER + '/DBProtector/FileTransaction_DELETE?User=Jguerrero&Password=Jguerrero&FileName=XXXXX000000.ZIP'

        try:
            # Realiza la peticion
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            # log.newLog("http_error", "E", e.fp.read())
            print e

    # cambia las unidades a porcentajes
    def returnPercent(self, total, value):
        total = int(total)
        value = int(value)
        porcentaje = Decimal(value * 100)
        return str(round(porcentaje / total))