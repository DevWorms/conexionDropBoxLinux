zypper in -y gcc
zypper addrepo --check --refresh --name 'openSUSE-Leap-42.1' http://download.opensuse.org/distribution/leap/42.1/repo/oss/ repo-dist
zypper in -y libopenssl-devel zlib-devel ncurses-devel
zypper rr repo-dist
wget https://www.python.org/ftp/python/2.7.12/Python-2.7.12.tar.xz
tar xf Python-2.7.12.tar.xz
cd Python-2.7.12
./configure --prefix=/usr
make && make altinstall
wget https://bootstrap.pypa.io/get-pip.py
python2.7 get-pip.py
