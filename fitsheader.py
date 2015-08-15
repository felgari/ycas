# -*- coding: utf-8 -*-

# Copyright (c) 2014 Felipe Gallego. All rights reserved.
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

"""This module manages information about the headers of FIT files. """

import sys
import os
import logging
import glob
import pyfits
import textfiles
from constants import *

DEFAULT_OBJECT_NAME = "OBJECT"

class HeaderFieldsException(Exception):
    
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return selg._msg

class HeaderFields(object):
    """Stores the names of the header fields and some of their values, 
    which are used when processing a FIT file.
    
    """ 
    
    # Names used in the configuration file to specify the names that are
    # used in the FIT files for these fields.
    _AIRMASS_FIELD_NAME = "AIRMASS"
    _DATE_OBS_FIELD_NAME = "DATE-OBS"
    _EXPOSURE_FIELD_NAME = "EXPOSURE"
    _FILTER_FIELD_NAME = "FILTER"
    _IMAGETYP_FIELD_NAME = "IMAGETYP"
    _MJD_FIELD_NAME = "MJD"
    _RA_FIELD_NAME = "RA"
    _DEC_FIELD_NAME = "DEC"
    _OBJECT_FIELD_NAME = "OBJECT"
    
    # Values used for the types of the images.
    _LIGHT_IMAGE_TYPE = "LIGHT"
    _BIAS_IMAGE_TYPE = "BIAS"
    _FLAT_IMAGE_TYPE = "FLAT"
    
    # The complete list of the previous constants to ease their checking. 
    _HEADER_FIELDS = [ _AIRMASS_FIELD_NAME, 
                      _DATE_OBS_FIELD_NAME,
                      _EXPOSURE_FIELD_NAME, 
                      _FILTER_FIELD_NAME,
                      _IMAGETYP_FIELD_NAME, 
                      _MJD_FIELD_NAME,
                      _RA_FIELD_NAME, 
                      _DEC_FIELD_NAME,
                      _OBJECT_FIELD_NAME]
    
    # The complete list of values for the types for the images.
    _IMAGE_TYPE_VALUES = [ _LIGHT_IMAGE_TYPE, 
                          _BIAS_IMAGE_TYPE, 
                          _FLAT_IMAGE_TYPE ]   
    
    def __init__(self, header_fields):
        
        # Default values in case of error.
        self._air_mass = None
        self._date_obs = None
        self._exposure = None
        self._filter = None
        self._image_type = None
        self._mjd = None
        self._ra = None
        self._dec = None
        self._object = None
        
        self._bias_value = None
        self._flat_value = None
        self._light_value = None
        
        header_error = False
        
        # Check that all header fields expected have been received.
        for name in HeaderFields._HEADER_FIELDS:
            if not name in header_fields.keys():
                logging.error("Header field '%s' not included." % name)
                header_error = True
                
        # Check that all values for header fields expected have been received.
        for name in HeaderFields._IMAGE_TYPE_VALUES:
            if not name in header_fields.keys():
                logging.error("Header field value '%s' not included." % name)
                header_error = True                            
        
        if not header_error:
            try:
                self._air_mass = header_fields[HeaderFields._AIRMASS_FIELD_NAME]
                self._date_obs = header_fields[HeaderFields._DATE_OBS_FIELD_NAME]
                self._exposure = header_fields[HeaderFields._EXPOSURE_FIELD_NAME]
                self._filter = header_fields[HeaderFields._FILTER_FIELD_NAME]
                self._image_type = header_fields[HeaderFields._IMAGETYP_FIELD_NAME]
                self._mjd = header_fields[HeaderFields._MJD_FIELD_NAME]
                self._ra = header_fields[HeaderFields._RA_FIELD_NAME]
                self._dec = header_fields[HeaderFields._DEC_FIELD_NAME]
                self._object = header_fields[HeaderFields._OBJECT_FIELD_NAME] 
                
                self._bias_value = header_fields[HeaderFields._BIAS_IMAGE_TYPE]
                self._flat_value = header_fields[HeaderFields._FLAT_IMAGE_TYPE]
                self._light_value = header_fields[HeaderFields._LIGHT_IMAGE_TYPE]                
                               
            except KeyError as ke:
                raise HeaderFieldsException("Assigning a header field value.")
        else:
            raise HeaderFieldsException("Configuration file for headers of " + \
                                        "FITs lacks one or more parameters.")
            
    @property
    def air_mass(self):
        return self._air_mass
    
    @property
    def date_obs(self):
        return self._date_obs
    
    @property
    def exposure(self):
        return self._exposure
    
    @property
    def filter(self):
        return self._filter            
    
    @property
    def image_type(self):
        return self._image_type
    
    @property
    def mjd(self):
        return self._mjd
    
    @property
    def ra(self):
        return self._ra
    
    @property
    def dec(self):
        return self._dec
    
    @property
    def object(self):
        return self._object 
    
    @property
    def bias_value(self):
        return self._bias_value    
    
    @property
    def flat_value(self):
        return self._flat_value  
    
    @property
    def light_value(self):
        return self._light_value  
    
    @property
    def header_fields_names(self):
        return HeaderFields._HEADER_FIELDS