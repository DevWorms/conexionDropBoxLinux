#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
import contextlib
import os
import zipfile
import hashlib
import subprocess

import time

from xamai.Login import Login
from xamai.SetLog import SetLog

'''
Comprime / Descomprime archivos en zip,
le coloca una contrasena generada a partir del id

app = Compress()
#app.compress("/backups/backup.bak")
#app.uncompress("/backups/backup.zip")
'''

class Compress():
    def createPassword(self):
        # Devuelve la info del usuario
        user = Login()
        data = user.returnUserData()
        '''
        La contrasena de los archivos comprimidos es un hash sha256 de el id del usuario
        ej:
        1 = 6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b
        '''
        password = hashlib.sha256(str(data['IdCustomer'])).hexdigest()
        return password

    # Comprime un archivo, recibe la ruta completa del archivo
    def compress(self, file):
        if os.path.exists(file):
            path, name = os.path.split(file)
            name, ext = name.split(".")
            with self.stopwatch('Comprimido '):
                subprocess.call(['7z', 'a', u'-p%s' % self.createPassword(), '-y', path + "/" + name + "." + ext + ".zip"] + [file])
            return True
        else:
            return False

    # Descomprime el archivo
    def uncompress(self, file):
        log = SetLog()
        if os.path.exists(file):
            path, name = os.path.split(file)

            if zipfile.ZipFile(file).extractall(path=path, pwd=self.createPassword()):
                log.newLog(os.path.realpath(__file__), "success_uncompress", "T", "")
            else:
                log.newLog(os.path.realpath(__file__), "error_uncompress", "E", "Compress.uncompress()")

            # elimina el .zip despues de haber sido extraido
            if os.path.exists(file):
                if os.remove(file):
                    return True
                else:
                    log.newLog(os.path.realpath(__file__), "error_remove_file", "E", "Compress.uncompress()")
                    return True
        else:
            return False

    @contextlib.contextmanager
    # Context manager para mostrar el elapsed time
    def stopwatch(self, message):
        t0 = time.time()
        try:
            yield
        finally:
            t1 = time.time()
            print('Total elapsed time for %s: %.3f' % (message, t1 - t0))
