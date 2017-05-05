Bootstrap: docker
From: maladmin/jessie-dtiprep:latest

%setup
	echo "Installing runscript"
	cp dtiprep.py ${SINGULARITY_ROOTFS}/opt/dtiprep.py
	cp environment ${SINGULARITY_ROOTFS}/environment
	exit 0

%post
	echo "Making dtiprep.py runnable"
	chmod 755 /opt/dtiprep.py

	mkdir /input
	mkdir /output
	mkdir /meta
	exit 0

%runscript
	if [ -z $1 ]
		then
			echo "DTIPrep Container"
			echo "USAGE:"
			/opt/dtiprep.py -h
			exit 1
	fi
	

	echo "Arguments received: $*"

	echo "Running DTIPrep"
	/opt/dtiprep.py "$@"
