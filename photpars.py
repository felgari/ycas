# -*- coding: utf-8 -*-

# Copyright (c) 2015 Felipe Gallego. All rights reserved.
#
# This file is part of ycas: https://github.com/felgari/ycas
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""This module read and store the parameters of the photometry.

The parameters are read from text files with a format name/value.

"""

import csv
import logging
import textfiles

class PhotParamNotFound(Exception):
    def __init__(self, param_list):
        
        self.__param_list = param_list
        
    def __str__(self):
        return "The following parameters for phot could not be read: %s." % \
            (self.__param_list)
    
class PhotParamFileError(Exception):
    def __init__(self, file_list):
        
        self.__file_list = file_list
        
    def __str__(self):
        return "The following files of parameters for phot could not be read: %s." % \
            (self.__file_list) 
    
class PhotParameters(object):
    
    # Names for the parameters of an instrument.
    __READNOISE_PAR_NAME = "READNOISE"
    __GAIN_PAR_NAME = "GAIN"
    __EPADU_PAR_NAME = "EPADU"
    
    # Names of the parameters of phot.
    __APERTURE_PAR_NAME = "APERTURE"
    __ANNULUS_MULT_PAR_NAME = "ANNULUS_MULT"
    __DANNULUS_PAR_NAME = "DANNULUS"
    
    __DATAMIN_PAR_NAME = "DATAMIN"    
    __DATAMIN_MULT_PAR_NAME = "DATAMIN_MULT"
    __DATAMAX_PAR_NAME = "DATAMAX"
    
    __CBOX_PAR_NAME = "CBOX"
    
    __SALGORITHM_PAR_NAME = "SALGORITHM"
    __CALGORI_PAR_NAME = "CALGORI"
    __SKY_PAR_NAME = "SKY"   
    
    def __init__(self, phot_params_file_name, instrument_params_file_name):
        
        # Initialize attributes.
        self.__readnoise = 1.0
        self.__gain = 1.0
        self.__epadu = 1
        
        self.__aperture_mult = 1
        self.__annulus_mult = 1    
        self.__dannulus = 1    
            
        self.__datamin = 0.0
        self.__datamin_mult = 1  
        self.__datamax = 1      
        
        self.__cbox = 1  
        
        self.__salgorithm = "mode"     
        self.__calgori = "centroid"
        self.__sky = 0.0
        
        self.__par_error = []
        self.__file_error = []
        
        # Read and assign the parameters for the phot.
        try:
            phot_params = textfiles.read_cfg_file(phot_params_file_name)
            
            self.aperture = phot_params[PhotParameters.__APERTURE_PAR_NAME]
            self.annulus_mult = phot_params[PhotParameters.__ANNULUS_MULT_PAR_NAME]
            self.dannulus = phot_params[PhotParameters.__DANNULUS_PAR_NAME]
            self.datamin = phot_params[PhotParameters.__DATAMIN_PAR_NAME]
            self.datamin_mult = phot_params[PhotParameters.__DATAMIN_MULT_PAR_NAME]
            self.datamax = phot_params[PhotParameters.__DATAMAX_PAR_NAME]
            self.cbox = phot_params[PhotParameters.__CBOX_PAR_NAME]
            self.salgorithm = phot_params[PhotParameters.__SALGORITHM_PAR_NAME]
            self.calgori = phot_params[PhotParameters.__CALGORI_PAR_NAME]
            self.sky = phot_params[PhotParameters.__SKY_PAR_NAME]
            
        except IOError as ioe:  
            self.__file_error.append(phot_params_file_name)
        
        # Read and assign the parameters of the instrument.
        try:            
            instrument_params = textfiles.read_cfg_file(instrument_params_file_name)
             
            self.readnoise = instrument_params[PhotParameters.__READNOISE_PAR_NAME]
            self.gain = instrument_params[PhotParameters.__GAIN_PAR_NAME]
            self.epadu = instrument_params[PhotParameters.__EPADU_PAR_NAME]
        except IOError as ioe:  
            self.__file_error.append(instrument_params_file_name) 
        
        if self.__file_error:         
            raise PhotParamFileError(self.__file_error)   
        
        if self.__par_error:
            raise PhotParamNotFound(self.__par_error)                   
        
    @property
    def readnoise(self):
        return self.__readnoise
    
    @readnoise.setter
    def readnoise(self, readnoise):
        try:
            self.__readnoise = float(readnoise)
        except KeyError as ke:
            self.__par_error.append(readnoise)
            
    @property
    def gain(self):
        return self.__gain
    
    @gain.setter
    def gain(self, gain):
        try:
            self.__gain = float(gain)
        except KeyError as ke:
            self.__par_error.append(gain)
            
    @property
    def epadu(self):
        return self.__epadu
    
    @epadu.setter
    def epadu(self, epadu):
        try:
            self.__epadu = int(epadu)
        except KeyError as ke:
            self.__par_error.append(epadu)                                 
        
    @property
    def aperture(self):
        return self.__aperture
    
    @aperture.setter
    def aperture(self, aperture):                
        try:
            self.__aperture = int(aperture)
        except KeyError as ke:
            self.__par_error.append(aperture)
        
    @property
    def annulus(self):
        return self.__annulus
    
    @annulus.setter
    def annulus(self, annulus):                
        try:
            self.__annulus = int(annulus)
        except KeyError as ke:
            self.__par_error.append(annulus)
        
    @property
    def annulus_mult(self):
        return self.__annulus_mult
    
    @annulus_mult.setter
    def annulus_mult(self, annulus_mult):                
        try:
            self.__annulus_mult = int(annulus_mult)
        except KeyError as ke:
            self.__par_error.append(annulus_mult)  
            
    @property
    def dannulus(self):
        return self.__dannulus
    
    @dannulus.setter
    def dannulus(self, dannulus):
        try:
            self.__dannulus = int(dannulus)
        except KeyError as ke:
            self.__par_error.append(dannulus)

    @property
    def datamin(self):
        return self.__datamin
    
    @datamin.setter
    def datamin(self, datamin):
        try:
            self.__datamin = float(datamin)
        except KeyError as ke:
            self.__par_error.append(datamin) 
            
    @property
    def datamin_mult(self):
        return self.__datamin_mult
    
    @datamin_mult.setter
    def datamin_mult(self, datamin_mult):
        try:
            self.__datamin_mult = int(datamin_mult)
        except KeyError as ke:
            self.__par_error.append(datamin_mult)       
            
    @property
    def datamax(self):
        return self.__datamax
    
    @datamax.setter
    def datamax(self, datamax):
        try:
            self.__datamax = int(datamax)
        except KeyError as ke:
            self.__par_error.append(datamax)   
            
    @property
    def cbox(self):
        return self.__cbox
    
    @cbox.setter
    def cbox(self, cbox):
        try:
            self.__cbox = int(cbox)
        except KeyError as ke:
            self.__par_error.append(cbox)     
            
    @property
    def salgorithm(self):
        return self.__salgorithm
    
    @salgorithm.setter
    def salgorithm(self, salgorithm):
        try:
            self.__salgorithm = salgorithm
        except KeyError as ke:
            self.__par_error.append(salgorithm)
            
    @property
    def calgori(self):
        return self.__calgori
    
    @calgori.setter
    def calgori(self, calgori):
        try:
            self.__calgori = calgori
        except KeyError as ke:
            self.__par_error.append(calgori)
            
    @property
    def sky(self):
        return self.__sky
    
    @sky.setter
    def sky(self, sky):
        try:
            self.__sky = float(sky)
        except KeyError as ke:
            self.__par_error.append(sky)                                                                 