#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
from distutils.core import setup
import xamai.Constants as const

'''
    # Refeferences:
    # https://stackoverflow.com/questions/26574521/having-trouble-installing-dropbox-api-for-python-2-6
    # https://stackoverflow.com/questions/1617078/ordereddict-for-older-versions-of-python
    # http://www.driverbug.com/Repo/201607250206/addons/plugin.program.ump/lib/third/dropbox/rest.py

    # Testing on SUSE 11
    # Empaqueta en RPM para SUSE, recomendable empaquetarlo desde SLES11_SP4_B1.x86_64-0.0.6.preload
    # dbprotector_post-install corrige los permisos de archivos de configuracion una vez instalado
    # dbprotector_post-remove cuando se desinstala la aplicacion elimina los archivos de configuracion y los crons
    # Comando para crear el rpm con ayuda de bdist_rpm:
    # python setup.py bdist_rpm --requires 'python' --post-install dbprotector_post-install --post-uninstall dbprotector_post-remove --no-autoreq --python /usr/bin/python2.6
'''

files = ["img/*.png", "settings/*.json", "gui/assets/css/*.css", "gui/assets/js/*.js", "gui/*.html", "setup.py"]

setup (
    name = 'DBProtector',
    version = const.VERSION,
    release = '1',
    url = 'scanda.com.mx/xamai',
    license = 'Copyright 2016',
    author = 'Xamai',
    author_email = 'soporte_xamai@scanda.com.mx',
    description = 'DBProtector',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers'
    ],
    install_requires = ['python-crontab',
                        'dropbox',
                        'psutil'],
    keywords = 'databases backups',
    packages = ['xamai'],
    scripts = ["dbprotector_xamai", "dbprotector_sync", "dbprotector_pre-install"],
    package_data = {'xamai' : files }
    #long_description = """DB Protector"""
)
