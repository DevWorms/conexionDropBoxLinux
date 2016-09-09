#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
import json
import os
import threading
import urllib2
from decimal import Decimal

#import thread

from os.path import expanduser

import xamai.Constants as const
from xamai.Crons import Cron
from xamai.Login import Login
from xamai.SetLog import SetLog

class Preferences():
    # cambia las unidades de almacenamiento de mb a porcentajes
    def returnPercent(self, total, value):
        total = int(total)
        value = int(value)
        porcentaje = Decimal(value * 100)
        return str(round(porcentaje / total))

    # guarda los datos del usuario recibidos
    def writePreferences(self, path, time, time_type, userPath):
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
                    'userPath': userPath,
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
            #thread.start_new_thread(c.sync, ())
            threading.Thread(target=c.sync).start()
            return True
        else:
            log.newLog(os.path.realpath(__file__), "load_config_file", "E", "")
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
            log.newLog(os.path.realpath(__file__), "http_error", "E", e.fp.read())
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
            user['FileHistoricalNumber'] = res['FileHistoricalNumber']
            user['FileHistoricalNumberCloud'] = res['FileHistoricalNumberCloud']
            user['PBYellowPercentage'] = res['PBYellowPercentage']
            user['PBRedPercentage'] = res['PBRedPercentage']
            user['PBGreenColorCode'] = res['PBGreenColorCode']
            user['PBYellowColorCode'] = res['PBYellowColorCode']
            user['PBRedColorCode'] = res['PBRedColorCode']
        else:
            log.newLog(os.path.realpath(__file__), "login_api_error", "E", "")
        # devuelve todos los datos del usuario
        return user

    # devuelve el color de la barra de progreso
    def returnColorProgressBar(self):
        user = self.returnUserData()
        spaceUsed = self.returnPercentInt(user['space'], user['spaceUsed'])
        if spaceUsed < user['PBYellowPercentage']:
            return user['PBGreenColorCode']
        elif spaceUsed >= user['PBYellowPercentage'] and spaceUsed < user['PBRedPercentage']:
            return user['PBYellowColorCode']
        else:
            return user['PBRedColorCode']

    # devuelve un porcentaje de 2 cantidades, pero como string, problema con wrappers
    def returnPercentInt(self, total, value):
        total = int(total)
        value = int(value)
        porcentaje = Decimal(value * 100)
        return int(round(porcentaje / total))

    '''
        devuelve la ruta externa configurada por el user
        si no esta condigurada, devuelve la ruta de respaldos + "respaldados"
    '''
    def returnExternalPath(self):
        log = SetLog()
        # Carga el archivo configuration.json
        file = os.path.join(const.LOCATION, const.CONFIGURATION_FILE)
        # Si el archivo existe...
        if (os.path.exists(file)):
            # abre el archivo y guarda la variable 'path' del archivo json
            with open(file, 'r') as f:
                data = json.load(f)

            if not data['path']:
                data['path'] = expanduser("~")

            if not data['userPath']:
                newPath = os.path.join(data['path'], "respaldados")
                if not os.path.exists(newPath):
                    os.makedirs(newPath)
                return newPath
            else:
                if not os.path.exists(data['userPath']):
                    os.makedirs(data['userPath'])
                return data['userPath']
        else:
            log.newLog(os.path.realpath(__file__), "load_config_file", "E", "")
            return ''


    # muestra la opcion para configurar la carpeta externa
    def showExternalPath(self):
        value = '<div class="form-group form-group-label">' \
               '<div class="row">' \
               '<div class="col-md-10 col-md-push-1">' \
               '<label class="floating-label" for="ui_path_external">Historicos</label>' \
               '<input class="form-control" id="ui_path_external" type="text" value="'+ self.returnExternalPath() +'">' \
               '</div>' \
               '</div>' \
               '</div>'
        return value