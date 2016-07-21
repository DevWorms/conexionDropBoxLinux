from distutils.core import setup

'''
    Empaqueta en RPM:
        python setup.py bdist_rpm --requires python-pip --requires python-setuptools --requires libwebkitgtk3-devel
'''

files = ["img/*.png", "settings/*.json"]

setup (
    name='DBProtector',
    version='0.1.1',
    release='1',
    url='scanda.com.mx',
    license='Copyright 2016',
    author='Grupo SCANDA',
    author_email='author@mail.com',
    description='DBProtector allow Automatically backup databases',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    install_requires=['python-crontab',
                      #'python-gi',
                      'pyminizip',
                      'dropbox'],
    keywords = 'databases backups',
    #dependency_links = ["http://ftp.gnome.org/pub/GNOME/sources/pygtk/2.0/pygtk-2.0.0.tar.gz"],
    packages = ['scanda'],
    scripts = ["dbprotector_scanda", "dbprotector_sync"],
    package_data = {'scanda' : files },
    long_description = """DBProtector allows you create automantically backups and place them in the cloud"""
)
