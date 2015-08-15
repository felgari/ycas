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

"""This module manages the catalog files.

These files contains the X,Y coordinates of the objects found by the astrometry
in each image. In addition to X,Y coordinates also the identifier of the object
is stored.

"""

import logging
from constants import *

class StarCatalogException(Exception):
    
    def  __init__(self, msg):
        
        self._msg = msg
        
    def __str__(self):
        
        return self._msg

class StarCatalog(object):
    """This class stores the information about the X, Y coordinates of the
    objects of interest in an image. Also the identifier used for each object is
    stored.
    
    """
    
    # Columns in catalog file.
    CAT_X_COL = 0
    CAT_Y_COL = 1
    CAT_ID_COL = 2
    
    def __init__(self, cat_file_name):
        
        self._id = []
        self._x_coor = []
        self._y_coor = []
        
        self._cat_file_name = cat_file_name

    def id(self, index):
        
        id = None
        
        try:
            id = self._id[index]
        except IndexError as ie:
            raise StarCatalogException("Index %d invalid for star catalog %s." %
                                       (index, self._cat_file_name))
        
        return id
        
    def read(self):
        """Read a file containing in each file a x,y coordinate pair and a numeric 
        identifier for each coordinate.
        
        Returns:    
            The list of coordinates read from the file indicated.
        
        """
        
        # List of coordinates read.
        coordinates = []
        
        # List of identifiers for the coordinates read.
        identifiers = []
        
        logging.debug("Reading coordinates from: %s" % (self._cat_file_name))
        
        try:
            with open(self._cat_file_name) as f:
                lines = f.readlines()      
                    
                # Each line has the coordinates and the identifier of a star.
                for lin in lines:        
                    self._id.append(lin[StarCatalog.CAT_ID_COL])
                    self._x_coor.append(lin[StarCatalog.CAT_X_COL])
                    self._y_coor.append(lin[StarCatalog.CAT_Y_COL])                                            

        except IOError as ioe:
            raise StarCatalogException("Reading coordinates file: %s" % 
                                       (self._cat_file_name))                 
    
        logging.debug("Coordinates read: %s" % (identifiers))
    
    def write(self, indexes, identifiers, xy_data):
        """Write text files with the x,y and ra,dec coordinates.
        
        The coordinates written are related to the x,y data and indexes set 
        received.
        
        Args:
            indexes: List of indexes corresponding to the coordinates to write.
            identifiers: Identifiers of the stars found.              
            xy_data: List of the X, Y coordinates that are referenced by X, Y
                coordinates.      
        
        """
        
        logging.debug("Writing catalog file: %s" % (self._cat_file_name))
        
        try:
            # Open the destiny file.
            catalog_file = open(self._cat_file_name, "w")
                
            # Iterate over the range of indexes to write them to the file.
            for i in range(len(indexes)):
                # The indexes corresponds to items in the XY data list.
                ind = indexes[i]
                
                catalog_file.write("%.10g %.10g %d\n" % 
                                   (xy_data[ind][XY_DATA_X_COL],
                                   xy_data[ind][XY_DATA_Y_COL], 
                                   identifiers[i]))
            
            catalog_file.close() 
        except IOError as ioe:
            raise StarCatalogException("Writing file: %s" % (catalog_file))         