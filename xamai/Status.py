#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
import json
import os
import urllib2

from decimal import Decimal
from xamai.SetLog import SetLog
from xamai.Login import Login
import xamai.Constants as const

class Status():
    THIS_FILE = os.path.realpath(__file__)
    file = THIS_FILE.split("/")
    THIS_FILE = file[-1] + "." + "Status()"

    # obtiene el status de la descarga
    def getUploadStatus(self):
        # logs
        log = SetLog()

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
            log.newLog(self.THIS_FILE + "." + "getUploadStatus()", "error_file_status", "E", "")
        return upload

    # carga el status de la subida (se usa cada que se inicia un chunk)
    def setUploadStatus(self, fileUploaded, chunk, total, status):
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
            log.newLog(self.THIS_FILE + "." + "setUploadStatus()", "error_file_status", "E", "")

        '''
            0 = Subida terminada
            1 = Iniciando subida
            2 = Subiendo
            3 = Comprimiendo
            Si es diferente de 3 envia un log a la API
        '''
        if status == 3 or status == 0:
            print "sincronizado"

        else:
            from time import gmtime, strftime
            url = ""
            # extrae la infor del user
            l = Login()
            user = l.returnUserData()
            # extrae la fecha actual formateada
            date = strftime("%Y%m%d%H%M%S", gmtime())

            # valida el status de la subida
            # 1 para carga iniciada
            if status == 1:
                #i el chunk es de 5mb, entonces es el primero en subirse
                if (int(chunk) <= ((const.CHUNK_SIZE/1024)/1024)+1) or (int(chunk) == 1): # tamano del chunk de 5MB
                    # Url de la api REST para la subida de archivos. Inicia la subida
                    url = const.IP_SERVER + '/DBProtector/FileTransaction_SET?User=' + user['user'] + '&Password=' + \
                          user['password'] + '&StartDate=' + date + '&ActualChunk=' + str(chunk) + '&TotalChunk=' + \
                          str(total) + '&Status=EnProgreso&FileName=' + fileUploaded + '&TransactionType=1'
                # si el es diferente de 5 mb, se esta actualizando
                else:
                    # Url de la api REST para la subida de archivos. Actualiza la subida
                    url = const.IP_SERVER + '/DBProtector/FileTransaction_UPDATE?User=' + user['user'] + '&Password=' + \
                          user['password'] + '&ActualChunk='+str(chunk)+'&Status=EnProgreso&FileName=' + fileUploaded + '&TransactionType=1'
            else:
                # Url de la api REST para la subida de archivos. Termina la subida
                #url = const.IP_SERVER + '/DBProtector/FileTransaction_DELETE?User=' + user['user'] + '&Password=' + user['password'] + '&FileName=' + fileUploaded + '&TransactionType=1'
                url = const.IP_SERVER + '/DBProtector/FileTransaction_UPDATE?User=' + user['user'] + '&Password=' + \
                          user['password'] + '&ActualChunk='+str(chunk)+'&Status=Finalizado&FileName=' + fileUploaded + '&TransactionType=1'

            try:
                # Realiza la peticion
                req = urllib2.Request(url)
                response = urllib2.urlopen(req)
            except HTTPError as e:
                log.newLog(self.THIS_FILE + "." + "setUploadStatus()", "http_error", "E", 'Codigo: ', e.code)
            except URLError as e:
                log.newLog(self.THIS_FILE + "." + "setUploadStatus()", "http_error", "E", 'Reason: ', e.reason)

    # cambia las unidades a porcentajes
    def returnPercent(self, total, value):
        total = int(total)
        value = int(value)
        porcentaje = Decimal(value * 100)
        return str(round(porcentaje / total))

    def getDownloadStatus(self):
        # logs
        log = SetLog()

        file = os.path.join(const.LOCATION, const.STATUS_FILE)
        # Si el archivo existe...
        if (os.path.exists(file)):
            # abre el archivo y lee los datos
            with open(file, 'r') as f:
                data = json.load(f)
            download = data['download']
        else:
            log.newLog(self.THIS_FILE + "." + "getDownloadStatus()", "error_file_status", "E", "")
        return download

    def setDownloadstatus(self, fileDownload, path, status):
        # logs
        log = SetLog()

        # Carga el status de la subida a nivel local
        file = os.path.join(const.LOCATION, const.STATUS_FILE)
        # Si el archivo existe...
        if (os.path.exists(file)):
            # guarda los datos anteriores
            with open(file, 'r') as f:
                data = json.load(f)
            # abre el archivo y escribe los datos
            with open(file, 'w') as f:
                json.dump({
                    'download': {
                        'file': fileDownload,
                        'path': path,
                        'status': status
                    },
                    'upload': data['upload']
                }, f)

            if status == 2 or status == 0:
                print "sincronizado"

            else:
                from time import gmtime, strftime
                url = ""
                # extrae la info del user
                l = Login()
                user = l.returnUserData()
                # extrae la fecha actual formateada
                date = strftime("%Y%m%d%H%M%S", gmtime())

                # valida el status de la subida
                if status == 1: # 1 para carga iniciada
                    # i el chunk es de 5mb, entonces es el primero en subirse. Comienza descarga
                    url = const.IP_SERVER + '/DBProtector/FileTransaction_SET?User=' + user['user'] + '&Password=' + \
                          user['password'] + '&StartDate=' + date + '&ActualChunk=' + str(0) + '&TotalChunk=' + \
                          str(0) + '&Status=EnProgreso&FileName=' + fileDownload + '&TransactionType=2'
                elif status == 0:
                    # Url de la api REST para la subida de archivos. Termina descarga
                    url = const.IP_SERVER + '/DBProtector/FileTransaction_SET?User=' + user['user'] + '&Password=' + \
                          user['password'] + '&StartDate=' + date + '&ActualChunk=' + str(0) + '&TotalChunk=' + \
                          str(0) + '&Status=Finalizado&FileName=' + fileDownload + '&TransactionType=2'
                try:
                    # Realiza la peticion
                    req = urllib2.Request(url)
                    response = urllib2.urlopen(req)
                except HTTPError as e:
                    log.newLog(self.THIS_FILE + "." + "setDownloadstatus()", "http_error", "E", 'Codigo: ', e.code)
                except URLError as e:
                    log.newLog(self.THIS_FILE + "." + "setDownloadstatus()", "http_error", "E", 'Reason: ', e.reason)
        else:
            log.newLog(self.THIS_FILE + "." + "setDownloadstatus()", "error_file_status", "E", "")

    def trayIconStatus(self):
        statusUpload = self.getUploadStatus()
        statusDownload = self.getDownloadStatus()
        # si se encuentra sincronizado
        if statusUpload['status'] == 0 and statusDownload['status'] == 0:
            status_label = "Sincronizado"
        # si esta subiendo y descargando al mismo tiempo
        elif statusUpload['status'] != 0 and statusDownload['status'] == 1:
            if statusUpload['status'] == 1:
                status_label = "Subiendo " + statusUpload['chunk'] + "% / Descargando " + statusDownload['file']
            elif statusUpload['status'] == 2:
                status_label = "Descargando " + statusDownload['file']
            elif statusUpload['status'] == 3:
                status_label = "Cifrando archivo / Descargando " + statusDownload['file']
        # si esta subiendo y descargando al mismo tiempo (si esta descomprimiendo el archivo)
        elif statusUpload['status'] != 0 and statusDownload['status'] == 2:
            if statusUpload['status'] == 1:
                status_label = "Subiendo " + statusUpload['chunk'] + "% / Descifrando " + statusDownload['file']
            elif statusUpload['status'] == 2:
                status_label = "Descifrando " + statusDownload['file']
            elif statusUpload['status'] == 3:
                status_label = "Cifrando archivo / Descifrando " + statusDownload['file']
        # si esta subiendo, pero no descargando
        else:
            if statusUpload['status'] != 0:
                if statusUpload['status'] == 1:
                    status_label = "Subiendo " + statusUpload['file'] + " " + statusUpload['chunk'] + "%"
                elif statusUpload['status'] == 2:
                    status_label = "Sincronizado"
                elif statusUpload['status'] == 3:
                    status_label = "Cifrando " + statusUpload['file'] + " para subir"
            if statusDownload['status'] == 1:
                status_label = "Descargando " + statusDownload['file']
            if statusDownload['status'] == 2:
                status_label = "Descifrando " + statusDownload['file']
        return status_label