#! /bin/bash
# Install PyGTK
# Tested on SUSE Linux SAP

if [[ $EUID -ne 0 ]]; then
	echo "##### Se requieren permisos de superusario #####" 2>&1
exit 1

else
	# If not repository, add openSUSE repository
	#zypper ar -f http://download.opensuse.org/distribution/leap/42.1/repo/oss oss
	zypper in python-gtk
	zypper in python-gobject
	zypper in python-devel
	zypper in python-pip
	pip install pygtk
fi