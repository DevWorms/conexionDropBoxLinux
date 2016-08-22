sudo zypper in -y gcc gobject-introspection-devel python-devel python3-devel python3-cairo-devel libffi-devel-gcc5
wget http://ftp.gnome.org/pub/GNOME/sources/pygobject/3.10/pygobject-3.10.0.tar.xz
tar Jxvf pygobject-3.10.0.tar.xz
cd pygobject-3.10.0
./configure
wget https://www.python.org/ftp/python/2.7.12/Python-2.7.12.tar.xz
./configure --prefix=/usr --enable-unicode=ucs4 --enable-shared LDFLAGS="-Wl,-rpath /usr/lib"
make && make altinstall
