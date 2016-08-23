%define name DBProtector
%define version 1.0
%define unmangled_version 1.0
%define release 1

Summary: DB Protector
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: Copyright 2016
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Grupo SCANDA <author@mail.com>
Requires: redhat-rpm-config zlib-devel python gcc python-devel python-pip python2-setuptools pygtk2 pyqt4 PyQt4-webkit
Url: scanda.com.mx

%description
UNKNOWN

%prep
%setup -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%pre
pip2.7 install --upgrade pip
#pip2.7 install python-crontab pyminizip dropbox
pip2.7 install 'python-crontab==2.0.2' 'pyminizip==0.2.1' 'dropbox==6.5.0' 'psutil==4.3.0'

#python setup.py install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES


%post
#! /bin/bash
sudo chmod -R 777 /usr/lib/python2.7/site-packages/xamai/settings/
#sudo ln -s /usr/bin/dbprotector_scanda /etc/init.d/
#sudo ln -s /etc/init.d/dbprotector_scanda /etc/rc.d/
#dbprotector_scanda
# Varia de acuerdo a la version de GNOME y la distribucion linux
echo '#!/usr/bin/env xdg-open
[Desktop Entry]
Version=1.0
# Only KDE 4 seems to use GenericName, so we reuse the KDE strings.
# From Ubuntus language-pack-kde-XX-base packages, version 9.04-20090413.
GenericName=Database
Type=Application
Terminal=false
Exec="/usr/bin/dbprotector_xamai"
Comment[es_MX]=DB Protector
Name=DB Protector
Comment=DB Protector
Icon=/usr/lib/python2.7/site-packages/xamai/img/DB_Protector_32X32.png
Categories=Database;Development;SAP
X-Ayatana-Desktop-Shortcuts=NewWindow
[NewWindow Shortcut Group]
Name=New Window
Exec="/usr/bin/dbprotector_xamai -n"' >> /usr/share/applications/dbprotector.desktop


%postun
#! /bin/bash
sudo rm -f /usr/bin/dbprotector_*
sudo rm -rf /usr/lib/python2.7/site-packages/xamai/


%files -f INSTALLED_FILES
%defattr(-,root,root)
