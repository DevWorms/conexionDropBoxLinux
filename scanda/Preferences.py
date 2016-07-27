#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import urllib2
import os
from decimal import Decimal
from scanda.Login import Login
from scanda.SetLog import SetLog
from scanda.Crons import Cron
import scanda.Constants as const

class Preferences():
    # cambia las unidades de almacenamiento de mb a porcentajes
    def returnPercent(self, total, value):
        total = int(total)
        value = int(value)
        porcentaje = Decimal(value * 100)
        return str(round(porcentaje / total))

    '''
    Se va a utilizar para acomodar el cron, pero para esta version
    no se utilizara en esta parte, si no en el cron
    def timeValidation(self, time, value, path):
        dias = 0
        meses = 0

        if value == "horas":
            if time > 23:
                while time > 23:
                    dias = dias + 1
                    time = time - 23
        elif value == "dias":
            while time > 31:
                meses = meses + 1
                time = time - 31

        if self.writePreferences(path, time, value):
            c = Cron()
            c.sync()
    '''

    # guarda los datos del usuario recibidos
    def writePreferences(self, path, time, time_type):
        log = SetLog()
        # Carga el archivo configuration.json
        file = os.path.join(const.LOCATION, const.CONFIGURATION_FILE)
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

            # Guarda los cambios en el archivo de configuracion y genera el cron
            c = Cron()
            c.sync()
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
        url = const.IP_SERVER + '/DBProtector/Account_GET?User=' + user['user'] + '&Password=' + user[
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
                user['freeSpace'] = res['StorageLimit']
            else:
                user['freeSpace'] = res['StorageLimit'] - res['UsedStorage']
            user['space'] = res['StorageLimit']
            user['spaceUsed'] = res['UsedStorage']
        else:
            log.newLog("login_api_error", "E", "")
        # devuelve todos los datos del usuario
        return user