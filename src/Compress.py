import contextlib
import os
import zipfile
import hashlib
import pyminizip

import time

from Login import Login

'''
Comprime / Descomprime archivos en zip,
le coloca una contrasena generada a partir del id y user
'''

class Compress():
    def createPassword(self):
        # Devuelve la info del usuario
        user = Login()
        data = user.returnUserData()
        '''
        La contrasena de los archivos comprimidos es un hash sha256
        de el id del usuario : el usuario:
        ej:
        1:Jguerrero
        dcfd8615edda421c24765f146f0ccb0f95cccf90c618ab0af258054872e4d85f
        '''
        password = hashlib.sha256(str(data['IdCustomer']) + ":" + data['user']).hexdigest()
        return password

    # Comprime un archivo, recibe la ruta completa del archivo
    def compress(self, file):
        if os.path.exists(file):
            path, name = os.path.split(file)
            name, ext = name.split(".")
            with self.stopwatch('compress'):
                pyminizip.compress_multiple([u'%s' % file], path + "/" + name + ".zip", self.createPassword(), 4)
            return True
        else:
            return False

    def uncompress(self, file):
        if os.path.exists(file):
            path, name = os.path.split(file)
            with zipfile.ZipFile(file, "r") as f:
                for name in f.namelist():
                    f.extract(name, path, self.createPassword())
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
'''
app = Compress()
#app.compress("/home/rk521/PycharmProjects/conexionDropBoxLinux/tests/backups/backup.bak")
#app.uncompress("/home/rk521/PycharmProjects/conexionDropBoxLinux/tests/backups/backup.zip")
'''