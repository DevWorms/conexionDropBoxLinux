from distutils.core import setup

# Command to create rpm: python setup.py bdist_rpm --requires pygtk

files = ["img/*.png", "settings/*.json"]

setup (
    name='BackupProtector',
    version='0.1',
    release='1',
    url='scanda.com.mx',
    license='GNU/GPL',
    author='Grupo SCANDA',
    author_email='rk521@hotmail.com',
    description='Backup Protector allow Automatically backup databases',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    install_requires=['python-pygtk', 'python-crontab'],
    keywords = 'databases backups',
    #dependency_links = ["http://ftp.gnome.org/pub/GNOME/sources/pygtk/2.0/pygtk-2.0.0.tar.gz"],
    packages = ['src'],
    scripts = ["backup_protector"],
    package_data = {'src' : files },
    long_description = """BackupProtector allows you create automantically backups and backup this on cloud"""
)
