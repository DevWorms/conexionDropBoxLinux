#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
import json
import os
import urllib
import urllib2
import psutil
from os.path import expanduser
import xamai.Constants as const

'''
Ejemplo: Envia un log
login_api_error es el mensaje de error, este debe ser extraido de errors.json
E = Error
T = transaction
except urllib2.HTTPError, e: codigo de error, clase que genera el error, o excepcion capturada
key=1 (el cuarto parametro es opcional) por defecto siempre es 1, puede pasarse 0

set.newLog(Upload.py, "login_api_error", "E", "except urllib2.HTTPError, e:")
'''

# Envia un log ala API de SCANDA
class SetLog():
    # Contador usado para evitar caer en un ciclo infinito de envio de errores
    err = 0

    def openErrorsFile(self):
        file = os.path.join(const.LOCATION, const.ERRORS_FILE)
        if (os.path.exists(file)):
            # abre el archivo y guarda la variable 'time' del archivo json
            with open(file, "r") as f:
                data = json.load(f)
        else:
            self.newLog(os.path.realpath(__file__), "Error: abrir archivo de errores no existe", "E", "os.path.exists(file)")
        return data

    # Metodo
    def newLogLogin(self, user, password, key=1):
        status = False
        # Unicamente se podran enviar 2 errores por clase, para evitar caer en un loop infinito
        if self.err < 3:
            # Carga el archivo de errores
            error = self.openErrorsFile()

            ex = ""
            # Url de la api REST
            url = const.IP_SERVER + "/DBProtector/Log_SET?Message=" + urllib.quote("Usuario o Pass incorrectos: " + user + ":" + password) + "&MessageType=E&Code=" + str(key) + "&AppVersion=" + const.VERSION_CODE + "&IdCustomer=0"

            try:
                # Realiza la peticion
                req = urllib2.Request(url)
                response = urllib2.urlopen(req)
                # Aumenta el contador
                self.err = self.err + 1
            except urllib2.HTTPError as e:
                self.writeLocalLog('Codigo: ' + str(e.code))
            except urllib2.URLError as e:
                self.writeLocalLog('Codigo: ' + str(e.reason))
            # Devuelve la info
            res = json.loads(response.read())
            # Si es correcto devuelve True
            if res['Success'] == 1:
                status = True
            # Si no, vuelve a enviar un error, y devuelve falso
            else:
                self.newLog(os.path.realpath(__file__), error["error_report"], "E", ex)
                status = False
        return status

    def newLog(self, file, msj, type, code, key=1):
        from xamai.Login import Login
        status = False
        # Unicamente se podran enviar 2 errores por clase, para evitar caer en un loop infinito
        if self.err < 3:
            # Aumenta el contador
            self.err = self.err + 1
            ex = ""
            # Carga el archivo de errores
            error = self.openErrorsFile()

            # Extrae los datos del usuario... user & passc
            login = Login()
            user = login.returnUserData()

            # Url de la api REST
            url = const.IP_SERVER + "/DBProtector/Log_SET?Message=" + urllib.quote(code + " | " + error[msj] + " | " + file) + "&MessageType=" + type + "&Code=" + str(key) + "&AppVersion=" + const.VERSION_CODE + "&IdCustomer=" + str(user['IdCustomer'])

            self.writeLocalLog(code + " | " + str(error[msj]) + " | " + file)
            try:
                # Realiza la peticion
                req = urllib2.Request(url)
                response = urllib2.urlopen(req)
                # Devuelve la info
                res = json.loads(response.read())
                # Si es correcto devuelve True
                if res['Success'] == 1:
                    status = True
                # Si no, vuelve a enviar un error, y devuelve falso
                else:
                    self.newLog(os.path.realpath(__file__), error["error_report"], "E", ex)
                    status = False
            except urllib2.HTTPError as e:
                print 'Codigo: ', e.code
            except urllib2.URLError as e:
                print 'Reason: ', e.reason
        return status

    def writeLocalLog(self, msg):
        file = os.path.join(expanduser("~"), const.LOCAL_LOG)

        if os.path.isfile(file):
            with open(file, 'r') as myfile:
                data = myfile.read()
            text_file = open(file, "w")
            text_file.write(data + "\n" + msg)
            text_file.close()
        else:
            try:
                directory = os.path.dirname(os.path.join(expanduser("~"), ".dbprotector/"))
                if not os.path.exists(directory):
                    os.makedirs(directory)
                file = open(file, 'w')
                file.write(msg)
                file.close()
            except:
                self.newLog('SetLog.py' + '.' + 'writeLocalLog()', 'error_local_log', 'E', '')
