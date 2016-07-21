#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import urllib2
import os
from scanda.Login import Login
from scanda.SetLog import SetLog
from scanda.Crons import Cron

class Preferences():
    CONFIG_FILE = "settings/configuration.json"
    LOCATION = os.path.dirname(os.path.realpath(__file__))

    def timeValidation(self, time, value, path):
        if value == "minutos":
            if time > 59:
                time = 59
            elif time < 0:
                time = 0
        elif value == "horas":
            if time > 23:
                time = 23
            elif time < 0:
                time = 0
        elif value == "dias":
            if time > 31:
                time = 31
            elif time < 1:
                time = 1
        else:
            value = "horas"
            time = time
        if self.writePreferences(path, time, value):
            c = Cron()
            c.sincronizar()


    # guarda los datos del usuario recibidos
    def writePreferences(self, path, time, time_type):
        log = SetLog()
        # Carga el archivo configuration.json
        file = os.path.join(self.LOCATION, self.CONFIG_FILE)
        # Si el archivo existe...
        if (os.path.exists(file)):
            # abre el archivo y guarda la variable 'path' del archivo json
            with open(file, 'r') as f:
                data = json.load(f)
            # escribe la nueva variable time en el archivo json junto con la variable value
            with open(file, 'w') as f:
                json.dump({
                    'path': path,
                    'time': time,
                    'time_type': time_type,
                    'IdCustomer': data['IdCustomer'],
                    'user': data['user'],
                    'password': data['password'],
                    'tokenDropbox': data['tokenDropbox'],
                }, f)
            return True
        else:
            log.newLog("load_config_file", "E", "")
            return False

    # Extraes toda la info del usuario proporcionada por la API
    def returnUserData(self):
        log = SetLog()
        # Datos del usuario
        l = Login()
        user = l.returnUserData()  # Url de la api REST para autenticarse
        url = 'http://201.140.108.22:2017/DBProtector/Account_GET?User=' + user['user'] + '&Password=' + user[
            'password']
        try:
            # Realiza la peticion
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            log.newLog("http_error", "E", e.fp.read())
        # Devuelve la info
        res = json.loads(response.read())
        # Si el inicio de sesion es correcto
        if res['Success'] == 1:
            # si  StorageLimit == -1 el espacio es Ilimitado
            if res['StorageLimit'] == -1:
                user['space'] = "Ilimitado"
                user['freeSpace'] = "Ilimitado"
            else:
                user['space'] = res['StorageLimit']
                user['freeSpace'] = res['StorageLimit'] - res['UsedStorage']
            user['spaceUsed'] = res['UsedStorage']
        else:
            log.newLog("login_api_error", "E", "")
        # devuelve todos los datos del usuario
        return user
