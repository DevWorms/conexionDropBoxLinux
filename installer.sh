# NO ejecutar este script en una terminal, solo es descriptivo
# Nombre de los paquetes necesarios para python 2.7
zypper in gcc libopenssl-devel zlib-devel ncurses-devel readline-devel gmp-devel gdbm-devel libexpat-devel tk tix libX11-devel glibc-devel tcl-devel tk-devel valgrind-devel sqlite2-devel sqlite3-devel libz1

# Ya vienen instalados en SLES 11
zypper in -y bzip2 tar autoconf

# Repositorios de donde se extrajeron los paquetes para python 3.4.1 
# 23/08/16 18:23:14
zypper addrepo --check --refresh --name 'openSUSE-Leap-42.1' http://download.opensuse.org/distribution/leap/42.1/repo/oss/ oss-dist
zypper addrepo --check --refresh --name 'openSUSE-Leap-42.1' http://download.opensuse.org/distribution/leap/42.1/repo/non-oss/ non-oss-dist

# Nombre de los paquetes necesarios para python 3.4.1 
python3-curses python3-dbm python3-tk glibc glibc-devel glibc-extra glibc-locale libncurses5 libopenssl1_0_0 libpython3_4m1_0 libreadline6 python3 python3-base python3-devel python3-pip python3-setuptools readline-doc libopenssl-devel libopenssl1_0_0 openssl openssl-certs python3-pyOpenSSL

# Elimina los repositorios
zypper rr repo-dist

# Descarga pip, la version por defecto en los repos de openSUSE no funcionan
wget https://bootstrap.pypa.io/get-pip.py
# Instala Pip
python3.4 get-pip.py
