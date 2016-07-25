%define name DBProtector
%define version 0.1.1
%define unmangled_version 0.1.1
%define release 1

Summary: DBProtector allow Automatically backup databases
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
Requires: gcc python3-devel python-pip python-setuptools libwebkitgtk3-devel
Url: scanda.com.mx

%description
DBProtector allows you create automantically backups and place them in the cloud

%prep
%setup -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
pip install --upgrade pip
pip install python-crontab pyminizip dropbox

python setup.py install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%post
#! /bin/bash
sudo chmod -R 777 /usr/lib/python2.7/site-packages/scanda/settings/
sudo ln -s /usr/bin/dbprotector_scanda /etc/init.d/
sudo ln -s /etc/init.d/dbprotector_scanda /etc/rc.d/
#dbprotector_scanda


%postun
#! /bin/bash
sudo rm -f /usr/bin/dbprotector_*
sudo rm -rf /usr/lib/python2.7/site-packages/scanda/


%files -f INSTALLED_FILES
%defattr(-,root,root)
