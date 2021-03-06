from distutils.core import setup
import xamai.Constants as const

'''
    # Tested on Fedora 24
    Empaqueta en RPM:
    python setup.py bdist_rpm --requires 'redhat-rpm-config zlib-devel python gcc python-devel python-pip python2-setuptools pygobject3-devel' --pre-install dbprotector_pre-install --post-install dbprotector_post-install --post-uninstall dbprotector_post-remove

    # Testing on OpenSUSE 13
'''

files = ["img/*.png", "settings/*.json", "gui/assets/css/*.css", "gui/assets/js/*.js", "gui/*.html", "setup.py"]

setup (
    name = 'DBProtector',
    version = const.VERSION,
    release = '1',
    url = 'scanda.com.mx',
    license = 'Copyright 2016',
    author = 'Grupo SCANDA',
    author_email = 'author@mail.com',
    description = 'DB Protector',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    install_requires = ['python-crontab',
                        'pyminizip',
                        'dropbox'],
    keywords = 'databases backups',
    #dependency_links = ["http://ftp.gnome.org/pub/GNOME/sources/pygtk/2.0/pygtk-2.0.0.tar.gz"],
    packages = ['xamai'],
    scripts = ["dbprotector_xamai", "dbprotector_sync"],
    package_data = {'xamai' : files }
    #long_description = """DB Protector"""
)
