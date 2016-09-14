%define name DBProtector
%define version 1.3
%define unmangled_version 1.3
%define release 1

Summary: DBProtector
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
Requires: python
Url: scanda.com.mx
AutoReq: 0

%description
UNKNOWN

%prep
%setup -n %{name}-%{unmangled_version}

%build
/usr/bin/python2.6 setup.py build

%install
/usr/bin/python2.6 setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%post
#! /bin/bash
sudo chmod -R 777 /usr/local/lib64/python2.6/site-packages/xamai/settings/
# Varia de acuerdo a la version de GNOME y la distribucion linux
echo '[Desktop Entry]
Categories=Development;Database;
Encoding=UTF-8
Name=DBProtector (Install)
GenericName=dbprotector
Comment=DBProtector
TryExec=dbprotector_pre-install
Exec=dbprotector_pre-install
Icon=/usr/local/lib64/python2.6/site-packages/xamai/img/DB_Protector_32X32.png
Terminal=true
StartupNotify=true
Type=Application' >> /usr/share/applications/dbprotector.desktop


%postun
#! /bin/bash
# Elimina los archivos
sudo rm -f /usr/bin/dbprotector_*
sudo rm -rf /usr/local/lib64/python2.6/site-packages/xamai/

# Elimina los crons
crontab -u root -l | grep -v '#xamai_init'  | crontab -u root -
crontab -u root -l | grep -v '#xamai_sync'  | crontab -u root -


%files -f INSTALLED_FILES
%defattr(-,root,root)
