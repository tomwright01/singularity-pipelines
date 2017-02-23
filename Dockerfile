FROM debian:jessie
LABEL maintainer "Thomas.Wright@camh.ca"

# Run apt-get calls
RUN apt-get update \
	&& apt-get install -y \
		libglu1.mesa \
		libjpeg62 \
		libxt6 \
		mriconvert \
		python \
		tar \
		wget \
		vim-tiny \
	&& rm -rf /var/lib/apt/lists/*
