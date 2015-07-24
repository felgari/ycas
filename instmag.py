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

""" This module read the magnitude files generated by Iraf phot command related
to the objects of interest and compile all then in files with csv format.

"""

from textfiles import *
from constants import *

class InstrumentalMagnitude(object):
    """ Stores the instrumental magnitudes of a star and the reference stars
        contained in the same field, if any.
    """
    
    def __init__(self, stars):
        """Constructor.
        
            Args:
            stars: The stars whose magnitudes are read.
        """
        
        self._stars = stars
        
        # To store the instrumental magnitudes of the star of interest.
        self._instrumental_magnitudes = []
        # To store the instrumental magnitudes of the star of interest and the
        # stars of reference.
        self._all_instrumental_magnitudes = [] 
        
        self._star_names = []   
       
        # For each star add a list in each list to contain the data of the star.
        for s in stars:
            self._star_names.append(s.name)
            
            self._instrumental_magnitudes.append([])
            self._all_instrumental_magnitudes.append([])
                
    def get_star_name_from_file_name(self, mag_file):
        """ Get the name of the object contained in the file name.
        
        Args:
        mag_file: Magnitude file where to extract the star name. 
        
        Returns:
        The name of the star.
        
        """
        
        # From the file name get the name of the object.
        star_name_with_path = mag_file[0:mag_file.find(DATANAME_CHAR_SEP)]
         
        return os.path.basename(star_name_with_path)
                

    def get_catalog_file_name(self, mag_file):
        # Read the catalog file that corresponds to this file.
        # First get the name of the catalog file from the current CSV file.
        catalog_file_name = mag_file.replace(
            DATA_FINAL_SUFFIX + FILE_NAME_PARTS_DELIM + MAGNITUDE_FILE_EXT + "." + CSV_FILE_EXT, 
            "." + CATALOG_FILE_EXT)
        return catalog_file_name


    def get_filter_name(self, path):
        """ The name of the directory that contains the file is the name of 
        the filter
        
        """
        
        path_head, filter_name = os.path.split(path)
        
        return filter_name

    def add_all_mags(self, star_name, star_index, magnitudes, time, filter_name):
        """Add all the magnitudes sorted by id.
        
        Args:
        stgar_name: Name of the star.
        star_index: Index used to add these magnitudes.
        magnitudes: The magnitudes with the x,y coordinate and the error.
        time: The time of the measurement.
        filter_name: The filter used for these measurements. 
        
        Returns:        
        A row with the magnitudes sorted and completed with INDEF.    
        
        """
        
        # The row to return. Time and filter to the beginning of the row.
        mag_row = [time, filter_name]
        
        n_mag = 0
        
        star = self._stars.get_star(star_name)
        
        # Check that the star has been found and it is a no standard one.
        if star is not None and not star.is_std:
        
            # For each star of the field a magnitude is added to the row, 
            # if the magnitude does not exists, INDEF values are added.
            for sf in star.field_stars:
               
                # Get current magnitude to process.
                current_mag = magnitudes[n_mag]
                
                if int(sf.id) == current_mag[MAG_ID_COL]:
                    # If there is a magnitude for this reference, 
                    # add the magnitude.
                    mag_row.extend([current_mag[MAG_COL], \
                                    current_mag[MAG_ERR_COL]])
                    
                    # Next magnitude if there is more magnitude values.
                    if n_mag < len(magnitudes) - 1:
                        n_mag += 1
                else:
                    # There is no magnitude for this reference, add INDEF values.
                    mag_row.extend([INDEF_VALUE, INDEF_VALUE])                     
            
        self._all_instrumental_magnitudes[star_index].append([mag_row])

    def read_mag_file(self, mag_file, filter_name, star_name, coordinates):
        """Read the magnitudes from the file.
        
        Args:
        mag_file: The name of the file to read.
        filter_name: Name of the filter for these magnitudes.
        star_name: Name of the star whose magnitudes are read.
        coordinates: List of X, Y coordinates of the stars in the image. 
        
        """
        
        logging.debug("Processing magnitudes file: " + mag_file)
        
        with open(mag_file, 'rb') as fr:
            reader = csv.reader(fr)
            nrow = 0
            mag = []
            all_mag = []
            time = None
            
            # Process all the instrumental magnitudes in the file.
            for row in reader:
                # Get a list of values from the CSV row read.
                fields = str(row).translate(None, "[]\'").split()            
                
                # Check that MJD has a defined value.
                if fields[CSV_TIME_COL] != INDEF_VALUE:
                    
                    # Save the time, it is the same for all the rows.
                    time = fields[CSV_TIME_COL]                        
                    
                    # Get the identifier for current coordinate.
                    current_coor = coordinates[nrow]
                    current_coor_id = int(current_coor[CAT_ID_COL])
                    
                    # If it is the object of interest, add the magnitude to the
                    # magnitudes list.
                    if current_coor_id == OBJ_OF_INTEREST_ID:
                        mag.append([fields[CSV_TIME_COL], \
                                    fields[CSV_MAG_COL], \
                                    fields[CSV_AIRMASS_COL], \
                                    fields[CSV_ERROR_COL], \
                                    filter_name])
                    
                    # Add the magnitude to the all magnitudes list.
                    all_mag.append([fields[CSV_MAG_COL], \
                                    fields[CSV_ERROR_COL], \
                                    current_coor_id])
                    
                    nrow += 1
                else:
                    logging.debug("Found INDEF value for the observation time")
            
            star_index = self._star_names.index(star_name)       
            
            if star_index >= 0: 
                
                self._instrumental_magnitudes[star_index].append(mag)

                if len(all_mag) > 0:
                    # Add all the magnitudes in the image sorted by identifier.
                    self.add_all_mags(star_name,star_index, \
                                      all_mag, time, filter_name)                
                
            logging.debug("Processed " + str(nrow) + " objects. " + \
                          "Magnitudes for object of interest: " + \
                          str(len(self._instrumental_magnitudes)) + \
                          ". Magnitudes for all the objects: " + \
                          str(len(self._all_instrumental_magnitudes)))

    def read_inst_magnitudes(self, mag_file, path):
        """Searches in a given path all the magnitudes files.
        
        Args:
        mag_file: File where to look for the magnitudes.
        path: Path where to search the files.
        
        """         
        
        # Filter for the magnitudes of this file.
        filter_name = self.get_filter_name(path)
        
        # Get the name of the object related to this file.
        star_name = self.get_star_name_from_file_name(mag_file)          
            
        catalog_file_name = self.get_catalog_file_name(mag_file)
        
        # Look for the catalog file that contains the x,y coordinates of each
        # star.
        if os.path.exists(catalog_file_name):
        
            # The list of coordinates used to calculate the magnitudes of the image.
            coordinates = read_catalog_file(catalog_file_name)
            
            self.read_mag_file(mag_file, filter_name, star_name, coordinates)
    
    def save_magnitudes_file(self, star_name, filename_suffix, magnitudes):
        """Save the magnitudes to a text file.
        
        Args:     
        star_name: Name of the object that corresponds to the magnitudes.
        filename_suffix: Suffix to add to the file name.
        magnitudes: List of magnitudes.
        
        """
        
        # Get the name of the output file.
        output_file_name = star_name + filename_suffix + "." + TSV_FILE_EXT
    
        with open(output_file_name, 'w') as fw:
            
            writer = csv.writer(fw, delimiter='\t')
    
            # It is a list that contains sublists, each sublist is
            # a different magnitude, so each one is written as a row.
            for imag in magnitudes:
            
                # Write each magnitude in a row.
                writer.writerows(imag)  
    
    def save_magnitudes(self):
        """ Save the magnitudes received.
            
        Args:
        objects: List of objects.
        instrumental_magnitudes: Instrumental magnitudes of objects of interest.
        all_instrumental_magnitudes: List of magnitudes for all the objects.    
        
        """
        
        # For each object. The two list received contains the same 
        # number of objects.
        i = 0
        for s in self._stars:
            if self._instrumental_magnitudes[i]:
                # Save instrumental magnitudes of objects of interest to a file.
                self.save_magnitudes_file(s.name, \
                                          INST_MAG_SUFFIX, \
                                          self._instrumental_magnitudes[i])   
               
            if self._all_instrumental_magnitudes[i]:
                # Save all the magnitudes to a file.
                self.save_magnitudes_file(s.name, \
                                          ALL_INST_MAG_SUFFIX, \
                                          self._all_instrumental_magnitudes[i])
            
            i = i + 1