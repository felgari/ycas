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

""" Stores the information related to the stars to process."""

import locale
import logging
import csv

class NoStdStarException(Exception):
    """Raised when a star no standard is used as standard."""
    
    def __init__(self, name):
        self._name = name
        
    def __str__(self):
        return "Star with name %s is not standard" % (self._name)
                
class NoFilterFoundForStdStarException(Exception):    
    """Raised when a standard star has not a filter."""
    
    def __init__(self, star_name, filter):
        self._star_name = star_name
        self._filter = filter
        
    def __str__(self):
        return "Standard star with name %s has not the filter %s" % \
                (self._star_name, self._filter)
                
class FieldStar(object):
    """A class to store the data for a related object in the same field 
    of the object of interest.
    
    """
    
    def __init__(self, id, ra, dec):
        self._id = id
        self._ra = ra
        self._dec = dec
        
    def __str__(self):
        return "ID: %d RA: %.10g DEC: %.10g" % (self._id, self._ra, self._dec)
        
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, id):
        self._id = id
    
    @property
    def ra(self):
        return self._ra
    
    @ra.setter
    def ra(self, ra):
        self._ra = ra    
    
    @property
    def dec(self):
        return self._dec
    
    @dec.setter
    def dec(self, dec):
        self._dec = dec
    
class StandardStarMagitude(object):
    """A class to store the magnitude in a given filter for a standard star. """
    
    def __init__(self, filter, mag):
        self._filter = filter
        self._mag = mag
        
    def __str__(self):
        return "Filter: %s Mag: %.5g" % (self._filter, self._mag)
        
    @property
    def filter(self):
        return self._filter

    @filter.setter
    def filter(self, filter):
        self._filter = filter
    
    @property
    def mag(self):
        return self._mag
    
    @mag.setter
    def mag(self, mag):
        self._mag = mag
        
class Star(object):
    """A class to store the data of a star.
    
    The star could be a standard one or not, and depending on this different 
    values are stored.
    If it is standard, the standard measures of the star are stored.
    Otherwise it is a star to measure and zero o more related stars
    could be saved.    
       
    """
    
    def __init__(self, name, ra, dec, is_std): 
        self._name = name
        self._ra = ra
        self._dec = dec
        self._synonyms = []
        
        if is_std:
            self._std_measures = []
            self._field_stars = None
        else: 
            self._std_measures = None
            self._field_stars = []    
            
    def __str__(self):
        add_info = None
        type = None
        
        if self._std_measures is not None:
            add_info =self._std_measures
            type = "STD"
        else:
            add_info = self._field_stars
            type = "REF"
            
        rest_info = [ str(x) for x in add_info ]
            
        return "%s RA: %.5g DEC: %.5g TYPE: %s -> %s" % \
            (self._name, self._ra, self._dec, type, rest_info)
            
    @property
    def name(self):
        return self._name
    
    @property
    def ra(self):
        return self._ra
    
    @property
    def dec(self):
        return self._dec
    
    @property
    def is_std(self):
        return self._std_measures is not None and len(self._std_measures) > 0      
            
    def add_std_mag(self, std_mag):
        """Add a standard magnitude to the star."""
        
        self._std_measures.append(std_mag)
        
    def add_field_star(self, ref_star):
        """Add a field star."""
        
        self._field_stars.append(ref_star)   
        
    def add_synomyms(self, list_of_synonyms):
        """Add a list of synonyms to the stars."""
        
        for syn in list_of_synonyms:
            self._synonyms.append(syn.strip())
        
    def has_synonym(self, synonym):
        
        return synonym in self._synonyms
        
    @property
    def field_stars(self):
        return self._field_stars  
    
    def get_std_mag(self, filter):                 
        
        mag = None
        
        if self.is_std:
            for sm in self._std_measures:
                if sm.filter == filter:
                    mag = sm.mag
        else:
            raise NoStdStarException(self._name)
        
        if mag is None:
            raise NoFilterFoundForStdStarException(self._name, filter)
            
        return mag    
            
class StarsSet(object):
    """Stores the data of a set of stars whose measures are processed.
    
    The data of the stars are read from a file passed as argument when 
    constructing the instance. 
    
    """
    
    # Minimun number of fields in a line of the file.
    MIN_NUM_OF_FIELDS_IN_LINE = 4;
    
    # Values to indicate if the star is standard or not.
    STANDARD_STAR = 'YES'
    NO_STANDARD_STAR = 'NO'
    
    # Data in the first columns of each line of the input file.
    OBJ_NAME_COL = 0
    OBJ_RA_COL = 1
    OBJ_DEC_COL = 2
    OBJ_STANDARD_COL = 3
    OBJ_ADDITIONAL_DATA = 4
    
    # Data in the additional columns of each line of the input file when the
    # object is no standard. 
    # The values must be added to the additional data column and multiplied by
    # an index.
    OBJ_RELATED_ID = 0
    OBJ_RELATED_RA = 1
    OBJ_RELATED_DEC = 2
    OBJ_RELATED_NUM_FIELDS = 3
    
    # Data in the additional columns of each line of the input file when the
    # object is standard.   
    # The values must be added to the additional data column and multiplied by
    # an index.
    OBJ_STD_FILTER = 0
    OBJ_STD_MAG = 1
    OBJ_STD_NUM_FIELDS = 2
    
    def __init__(self, file_name, synonym_file_name):
        
        self.__iter_idx = 0
        
        self._stars = []        
        
        self.read_stars(file_name, synonym_file_name)    
        
    def __str__(self):
        """Log the information of the stars."""
        
        star_names = [ s.name for s in self._stars ]
        
        return str(star_names) 
            
    def __iter__(self):
        self.__iter_idx = 0
        
        return self       
        
    # Python 3 compatibility
    def __next__(self):
        return self.next()
    
    def next(self):
        if self.__iter_idx < len(self._stars):
            cur, self.__iter_idx = \
                self._stars[self.__iter_idx], self.__iter_idx + 1
            return cur
        else:
            raise StopIteration()    
        
    @property
    def size(self):
        return len(self._stars)     
    
    @property
    def star_names(self):
        return [ s.name for s in self._stars ]
        
    @property
    def has_any_std_star(self):
        """ Returns True id the set contains at least one no standard star."""
        
        has_std = False
        
        for s in self._stars:
            if s.is_std:
                has_std = True
                break
        
        return has_std   
        
    def create_star(self, line):
        """Create an object for a star with the data contained in the line
        
        Args:
            line: A line read from the file.
        
        Returns:
            An object with the basic data for a star regardless standard or not.        
        """
        
        name = line[self.OBJ_NAME_COL]
        ra = locale.atof(line[self.OBJ_RA_COL])
        dec = locale.atof(line[self.OBJ_DEC_COL])     
        type = line[self.OBJ_STANDARD_COL]
        
        is_std = True if type == self.STANDARD_STAR else False
        
        return Star(name, ra, dec, is_std)   
    
    def add_star(self, star):
        """Add the star received to the stars.
        
        Args:
            star: The star to store.
        """
        
        self._stars.append(star)
        
    def get_star(self, name):
        
        star = None
        
        for s in self._stars:
            if s.name == name or s.has_synonym(name):
                star = s
                break
        
        return star
    
    def get_star_index(self, name):
        
        index = -1
        
        for i in range(len(self._stars)):
            s = self._stars[i]
            if s.name == name or s.has_synonym(name):
                index = i
                break
        
        return index    
    
    def number_of_fields_to_process(self, line, group_length):
        """Determines the number of fields to read from a line depending on the
        length of the group to read completely.
    
        Args:
            line: A line read from the file.        
            group_length: Length of the group of data to read each time.
        
        Return:
            The length of the line to read to ensure the reading of full groups.
            
        """
        
        # Check the length of the line.
        num_std_fields = len(line) - self.OBJ_ADDITIONAL_DATA
        
        # The limit must be a multiple of the number of fields for each 
        # standard measure.
        fields_limit = num_std_fields / group_length * group_length
        
        return fields_limit + self.OBJ_ADDITIONAL_DATA        
        
    def load_standard_star(self, star, line, line_number):
        """Process the line to initialize the data corresponding to a standard
        star. If successful the star is stored.

        Args:
            star: A star object with the basic data.
            line: A line read from the file.
            line_number: The number of the line in the file. 
                   
        """      

        # Calculate the number of fields that could be read depending on the
        # length of the fields for each standard star.
        fields_limit = self.number_of_fields_to_process(line, \
                                                        self.OBJ_STD_NUM_FIELDS)

        # Index for the fields of the line, starts at the first group of data to
        # read to ensure the limit of the line is not exceeded.
        i = 1

        # Walk the list while the number of fields allow reading data.
        while self.OBJ_ADDITIONAL_DATA + ( self.OBJ_STD_NUM_FIELDS * i ) <= \
            fields_limit:
            # Calculate the base index to read this group of data.
            base_index = self.OBJ_ADDITIONAL_DATA + \
                ( self.OBJ_STD_NUM_FIELDS * ( i - 1 ))
            
            filter = line[base_index + self.OBJ_STD_FILTER]
            mag = locale.atof(line[base_index + self.OBJ_STD_MAG])
            
            std_star_mag = StandardStarMagitude(filter, mag)
            
            star.add_std_mag(std_star_mag)
            
            i = i + 1
                
    def load_reference_star(self, star, line, line_number):
        """Process the line to initialize the data corresponding to a 
        reference star. If successful the reference star is stored in the
        star.

        Args:
            line: A line read from the file.
            line_number: The number of the line in the file. 
                   
        """   
        
        # Calculate the number of fields that could be read depending on the
        # length of the fields for each reference star.
        fields_limit = self.number_of_fields_to_process(line, \
                                                        self.OBJ_RELATED_NUM_FIELDS)

        # Index for the fields of the line, starts at the first group of data to
        # read to ensure the limit of the line is not exceeded.
        i = 1

        # Walk the list while the number of fields allow reading data.
        while self.OBJ_RELATED_NUM_FIELDS + ( self.OBJ_RELATED_NUM_FIELDS * i ) < \
            fields_limit:
            # Calculate the base index to read this group of data.
            base_index = self.OBJ_ADDITIONAL_DATA + \
                ( self.OBJ_RELATED_NUM_FIELDS * ( i - 1 ))
            
            id = int(line[base_index + self.OBJ_RELATED_ID])
            ra = locale.atof(line[base_index + self.OBJ_RELATED_RA])
            dec = locale.atof(line[base_index + self.OBJ_RELATED_DEC])          
            
            ref_star = FieldStar(id, ra, dec)
            
            star.add_field_star(ref_star)
            
            i = i + 1                 
        
    def process_file_line(self, line, line_number):
        """Process the items in the file row to store the values for an 
        star whose information must be included in this line.
        
        Args:
            line: A line read from the file.
            line_number: The number of the line in the file.
        
        Return:
            The star with the data read from the line.
        
        """
        
        star = None
        
        # Check the line has a minimum number of fields.
        if len(line) < self.MIN_NUM_OF_FIELDS_IN_LINE:
            logging.error("In the file of stars, the line %d does not contain enough values."
                          % (line_number))
        else:
            # Create the object for the star filling the basic data for it.
            star = self.create_star(line)
            
            # Load the rest of the data of the star depending on standard or 
            # not.
            if line[self.OBJ_STANDARD_COL] == self.STANDARD_STAR:
                self.load_standard_star(star, line, line_number)
            else:
                self.load_reference_star(star, line, line_number)
                
        return star
        
    def read_stars(self, file_name, synonym_file_name):
        """Read the data of the stars from the file indicated.
        
        This file contains the name of the object and the AR, DEC 
        coordinates of each object.
        
        Args:
            file_name: Name of the file that contains the data of the stars.
            synonym_file_name: Name of the file with the synonym of the stars.
        
        """
        
        logging.debug("Reading stars from file: %s" % (file_name))
        
        row_number = 0
        
        try:
            # Read the file that contains the stars.
            with open(file_name, 'rb') as fr:
                reader = csv.reader(fr, delimiter=',')        
                
                # Each line contains data for a star.
                for row in reader:                 
                    
                    if len(row) > 0:
                        # Only the column with name of the object.
                        star = self.process_file_line(row, row_number)
                        
                        if star is not None:
                            self.add_star(star)
                        
                    row_number = row_number + 1
                    
            if synonym_file_name is not None:
                self.read_synonym_os_stars(synonym_file_name)
                    
        except IOError as ioe:
            logging.error("Reading the file of stars: '%s'." % (file_name))
                
        logging.debug("Finished the reading of stars from file: %s" %
                      (file_name))    
        
    def read_synonym_os_stars(self, synonym_file_name):
        """Read the file that contains the synonyms for the names of the stars.
        
        Args:
            synonym_file_name: The file with synonyms of the name of the stars. 
            
        """
        
        try:
            with open(synonym_file_name, 'rb') as fr:
                reader = csv.reader(fr, delimiter=',')        
                
                # Each line contains data for a star.
                for row in reader:                 
                    
                    # At least the name of the star and a synonym.
                    if len(row) > 1:
                        
                        star = self.get_star(row[0])
                        
                        if star is not None:
                            star.add_synomyms(row[1:])                        
                    
        except IOError as ioe:
            logging.error("Reading the file of stars: '%s'." % 
                          (synonym_file_name))        