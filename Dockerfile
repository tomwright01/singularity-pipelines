FROM debian:jessie
LABEL maintainer "Thomas.Wright@camh.ca"

# Run apt-get calls
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		libglu1.mesa \
		libjpeg62 \
		libxt6 \
		mriconvert \
		python \
		tar \
		wget \
		vim-tiny \
		coreutils \
	&& rm -rf /var/lib/apt/lists/*

# Add neurodebian repo
RUN wget -O- http://neuro.debian.net/lists/jessie.us-tn.full | tee /etc/apt/sources.list.d/neurodebian.sources.list
RUN apt-key adv --recv-keys --keyserver hkp://pgp.mit.edu:80 0xA5D32F012649A5A9

# Install FSL
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		fsl-5.0-core \
	&& rm -rf /var/lib/apt/lists/*
RUN ln -s /usr/bin/fsl5.0-bet2 /bin/bet2

# Install DTIPrep
WORKDIR /opt
RUN wget --no-check-certificate https://www.nitrc.org/frs/download.php/6630/DTIPrep1.2.4_linux64.tar.gz -O DTIPrep.tar.gz
RUN tar -xzf DTIPrep.tar.gz
RUN rm DTIPrep.tar.gz

# Install Slicer
WORKDIR /opt
RUN wget http://download.slicer.org/bitstream/561384 -O slicer.tar.gz
RUN tar -xzf slicer.tar.gz
RUN rm slicer.tar.gz

# Install some slicer extensions
WORKDIR /opt
ADD 25516-linux-amd64-SlicerDMRI-gitce15576-2016-10-26.tar.gz /opt/
ADD 25516-linux-amd64-UKFTractography-git421a7ad-2017-02-28.tar.gz /opt/
RUN cp -r /opt/25516-linux-amd64-SlicerDMRI-gitce15576-2016-10-26/lib/Slicer-4.6 /opt/Slicer-4.6.2-linux-amd64/lib
RUN cp -r /opt/25516-linux-amd64-UKFTractography-git421a7ad-2017-02-28/lib/Slicer-4.6 /opt/Slicer-4.6.2-linux-amd64/lib/
RUN rm -rf /opt/25516-linux-amd64-SlicerDMRI-gitce15576-2016-10-26
RUN rm -rf /opt/25516-linux-amd64-UKFTractography-git421a7ad-2017-02-28
