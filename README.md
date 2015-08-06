ycas
====

A pipeline to reduce and calculate the aperture photometry of astronomical images.

The name comes from the star gamma cassiopeiae, the first star of type Be discovered. 
This pipeline was developed initially to process images of x-ray binaries, and some of those contain a Be star.

This software is a set of python scripts and requires external software to perform some tasks. The astrometry uses astrometry.net and the reduction and photometry of images uses pyraf. 

Functionality
-------------
This software performs the following tasks:
* Organization of images in directories.
* Reduction using bias and flat images.
* Calculation of astrometry to identify the objects in the images.
* Aperture photometry.
* Calculation of magnitudes corrected for the atmospheric extinction (when standard stars are available).
* Calculation of calibrated magnitudes (when standard stars are available).
* Generation of a summary with the results of the tasks performed.
* Generation of a file log to debug the tasks performed.

Use
---
This software is used from the command line. It provides some arguments to specify the tasks to perform, the data to use and in some cases how to perform a task.

Calling the software from the command line without any argument or with the argument -h shows a help with all the arguments available.  

Requirements
------------
This software has been developed with python 2.7 and should work properly with newer versions of python and the modules listed below.

Also the following python modules are needed:
* argparse 1.1
* csv 1.0
* glob
* logging 0.5.1.2
* numpy 1.6.1
* pyfits 3.2.3
* pyraf 2.1.6
* scipy 0.14.0
* shutil

Also the following external software is needed.
* [Iraf](http://iraf.noao.edu/)
* [astrometry.net](http://astrometry.net/)
* [sextractor](http://www.astromatic.net/software/sextractor)

Future work
-----------
Some future improvements:
* Generation of plots for light curves.
* Management of fit header values to allow more diversity on the specification of fit images values.  
* A GUI (graphical user interface) based in python.
* A setup to install the software and all the needed modules.