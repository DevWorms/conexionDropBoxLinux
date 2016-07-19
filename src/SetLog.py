#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import urllib
import urllib2

from Login import Login

# Envia un log ala API de SCANDA
class SetLog():
    version = '0.1'
    # Contador usado para evitar caer en un ciclo infinito de envio de errores
    err = 0
    CONFIG_FILE = "settings/errors.json"
    LOCATION = os.path.dirname(os.path.realpath(__file__))

    def openErrorsFile(self):
        file = os.path.join(self.LOCATION, self.CONFIG_FILE)
        if (os.path.exists(file)):
            # abre el archivo y guarda la variable 'time' del archivo json
            with open(file, "r") as f:
                data = json.load(f)
        else:
            self.newLog("Error: abrir archivo de errores no existe", "E", "os.path.exists(file)")
        return data

    def newLog(self, msj, type, code, key=1):
        status = False
        # Unicamente se podran enviar 2 errores por clase, para evitar caer en un loop infinito
        if self.err < 3:
            ex = ""
            # Carga el archivo de errores
            error = self.openErrorsFile()

            # Extrae los datos del usuario... user & passc
            login = Login()
            user = login.returnUserData()

            # Url de la api REST
            url = "http://201.140.108.22:2017/DBProtector/Log_SET?Message=" + urllib.quote(error[msj]+" "+code) + "&MessageType=" + type + "&Code=" + str(key) + "&AppVersion=" + self.version + "&User=" + user['user'] + "&Password=" + user['password']

            try:
                # Realiza la peticion
                req = urllib2.Request(url)
                response = urllib2.urlopen(req)
                # Aumenta el contador
                self.err+1
            except urllib2.HTTPError, e:
                print "Error: " + e.fp.read()
                ex = e.fp.read()
            # Devuelve la info
            res = json.loads(response.read())
            # Si es correcto devuelve True
            if res['Success'] == 1:
                status = True
            # Si no, vuelve a enviar un error, y devuelve falso
            else:
                self.newLog(error["error_report"], "E", ex)
                status = False
        return status

'''
set = SetLog()
if set.newLog("login_api_error", "E", "except urllib2.HTTPError, e:"):
    print "El envio fue exitoso"
else:
    print "Ocurrio un error al enviar el Log"
'''