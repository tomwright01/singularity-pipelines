# A Singularity container for running DTIPrep

[DTIPrep](https://www.nitrc.org/projects/dtiprep)  performs a
"Study-specific Protocol" based automatic pipeline for DWI/DTI
quality control and preparation.


[Singularity](https://singularity.lbl.gov) is a containerisation framework
specifically designed to enable containers to be hosted on HPC clusters.
It overcomes many of the security issues associated with running
[Docker](https://docker.com) containers as root.

The build process described below creates a singularity container for running
the automated componets of DTIPrep.

## Why Docker _and_ Singularity?

Docker containers are _built_ following the recipe in a file `Dockerfile`.
Singularity containers are _bootstrapped_ following the recipe in a `.def` file.
This build process uses both a docker container and a singularity container.

*Docker* supports excellent versioning by introducing the concept of layers.
Each layer is a discrete set of changes that can be applied to the container image
that can be stored and applied independently. This allows caching of the container
at various states. This means changes to the `Dockerfile` can be applied incrementally
reducing the amount of data that needs to be downloaded. *Singularity* does not
support this layer concept (yet?). A change to the singularity `.def` file results
in the full operating system image being re-downloaded. By combining *Docker* and
*Singularity* we can have the best of both worlds.

In this build the underlying operating system is created as a Docker container.
The singularity container is based on the docker container and the DTIPrep
runtime scripts are added. This allows changes to the scripts to be made without
having to recreate the entire operating system.

## Pre-requisites

The following has been tested on a system running Ubuntu 14.0.4

- [docker-engine](https://docs.docker.com/engine/installation/linux/debian/)
- [singularity](http://singularity.lbl.gov/install-linux)
- An account on [Docker Hub](https://hub.docker.com/)
- sudo access to the build host

## The build process

### Create a repo on docker hub

The instructions below assume the repo is `maladmin/dtiprep-base`.
- Login to docker hub
    $ docker login

### Create a docker image and upload to docker hub

The docker image is defined in the file `Dockerfile`.
I have based this image on Debian Jessie, apt-get is then used to install some
additional libraries.

 - Build the docker image
    $ docker build -t dtiprep-base .
- Find the *Image ID*
    $ docker images
- Tag the image with the name of the repository
    $ docker tag <image id> maladmin/dtiprep-base:latest
- Upload the image to docker hub
    $ docker push maladmin/dtiprep-base

### Create the singularity container

An empty container needs to be created at the first run. Future runs will
overwrite the existing container.

- Create the empty container
    $ sudo singularity create singularity-dtiprep.img

The singularity container is defined in the file bootstrap_qa.def

- Fill the container
    $ sudo singularity bootstrap singularity-dtiprep.img bootstrap_qa.def

## Running the singularity container

The `%runscript` section of `bootstrap_qa.def` defines the entry point when the
singularity container is run. This script exists within the container as a File
`/singularity`.

This shell script expects one argument, the name of a nrrd file to process. It passes
this argument to the python script `dtiprep.py` (/opt/dtiprep.py).

The python script `dtiprep.py` uses two hard coded directories `/input` and `/output`.
These directories can be dynamically mapped to the host operating system when the container
is run using the -B flag.

    $ singularity run -B <path to input file>:/input -B <path to output>:/output singularity-dtiprep.img

The file launch_dtiprep.py will process our existing filesystem and submit multiple jobs using qsub.

## Notes

It is simple to get a read-only shell within the singularity container:
    $ singularity shell singularity-dtiprep.img

A writeable shell is useful for development, but changes made should be reflected back to
the definition file `bootstrap_qa.def` for repeatability.

    $ sudo singularity shell --writable singularity-dtiprep.img
