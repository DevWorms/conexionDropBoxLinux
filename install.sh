#! /bin/bash
# Install PyGTK
# Tested on SUSE Linux SAP

if [[ $EUID -ne 0 ]]; then
	echo "##### Se requieren permisos de superusario #####" 2>&1
exit 1

else
	# If not repository, add openSUSE repository
	#zypper ar -f http://download.opensuse.org/distribution/leap/42.1/repo/oss oss
	#zypper ar -f http://download.opensuse.org/distribution/11.4/repo/oss/ oss
	zypper in python-gobject
	zypper in python-devel

	zypper in python-pip
	zypper in python-setuptools
	zypper in python-webkitgtk-devel
	zypper in gtk3-devel

	libavahi-gobject-devel-0.6.31-12.2.x86_64.rpm
	libavahi-gobject0-0.6.31-12.2.x86_64.rpm     
	libcairo-gobject2-1.14.2-3.1.x86_64.rpm
	libcairo-gobject2-32bit-1.14.2-3.1.x86_64.rpm
	libgobject-2_0-0-2.44.1-2.3.x86_64.rpm  
	lightdm-gobject-devel-1.15.0-4.2.x86_64.rpm
	python-gobject-3.16.2-5.2.x86_64.rpm
	python-gobject-cairo-3.16.2-5.2.x86_64.rpm
	python-gobject-devel-3.16.2-5.2.x86_64.rpm
	python-gobject2-2.28.6-26.1.x86_64.rpm
	python-gobject2-devel-2.28.6-26.1.x86_64.rpm
	libwebkitgtk3-devel
	gobject-introspection-1.44.0-2.2.x86_64.rpm
	gobject-introspection-devel-1.44.0-2.2.x86_64.rpm

	python3-gobject-3.16.2-5.2.x86_64.rpm
	python3-gobject-cairo-3.16.2-5.2.x86_64.rpm
	python3-gobject2-2.28.6-26.1.x86_64.rpm
	python3-gobject2-devel-2.28.6-26.1.x86_64.rpm

	webkit2gtk3-devel
	webkit2gtk3
fi

# Este es el chido xD
libwebkitgtk-3_0-0
libwebkitgtk-3_0-0-2.4.6-1.4.x86_64.rpm  

libwebkitgtk3-devel

libwebkitgtk3-lang	