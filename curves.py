#!/usr/bin/env python
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

"""
This module calculates the magnitude of a group of objects performing
a sequence of steps.

The processing assumes certain values in the header of the fits images,
even in the names of the files. Also a list of objects of interest, 
whose magnitudes are calculated, and a list of standard stars.
Some characteristics of the CCD camera are also needed to calculate
the photometric magnitude of the objects.
"""

import sys
import csv
import logging
import argparse
from constants import *

CSV_FILE_DELIM = ','

MJD_COL = 3
MAG_COL = 4
ERR_COL = 5

NO_VALUE = "NA"

class CurvesArguments(object):
    """ Encapsulates the definition and processing of program arguments.
        
    """
    
    MIN_NUM_ARGVS = 2
    OUTPUT_FILE = "curves.csv"    
    
    def __init__(self):
        """ Initializes parser. 
        
        Initialization of variables and the object ImagesArguments 
        with the definition of arguments to use.

        """         
            
        # Initiate arguments of the parser.
        self.__parser = argparse.ArgumentParser()
        
        self.__parser.add_argument("-r", metavar="reverse values", dest="r", \
                                   help="Indicates if the values of the " + \
                                   "files should be reversed") 
        
        self.__parser.add_argument("-o", metavar="output file name", \
                                    dest="o", help="Name of the output file")
        
        self.__parser.add_argument("-i", metavar="names of the input files", \
                                   dest="i", nargs='+', \
                                   help="Name of the input files")   
        
        self.__parser.add_argument("-m", dest="m", action="store_true", \
                                   help="Calculate median for measures in " + \
                                   "the same day according to MJD.")   
           
    
    @property    
    def input_files_names(self): 
        return self.__args.i     
    
    @property
    def reverse_options(self):
        return self.__args.r       
    
    @property
    def output_file_name(self):
        return self.__args.o
    
    @property
    def calculate_median(self):
        return self.__args.m
    
    def parse(self):
        """ 
        
        Initialize properties and performs the parsing 
        of program arguments.
        
        """
        
        # Parse program arguments.
        self.__args = self.__parser.parse_args()
            
        if self.__args.o == None:
            self.__args.o = CurvesArguments.OUTPUT_FILE    
            
    def print_usage(self):
        """ Print arguments options """
        
        self.__parser.print_usage()    
        
    def print_help(self):
        """ Print help for arguments options """
                
        self.__parser.print_help() 

def write_data(data, output_file_name):
    """
    
    Write the data received to a file
    
    """
    
    with open(output_file_name, 'w') as fw:
    
        writer = csv.writer(fw, delimiter=CSV_FILE_DELIM)

        # It is a list, write each row.
        for d in data:         
        
            # Write each data in a row.
            writer.writerow(d)      

def get_unique_ind_values_sorted(files_data):
    """
    
    Take the column of independent variable of all the data 
    and returns a list of unique values sorted.
    
    """
    
    # Use a set to get unique values.
    ind_values = set()
    
    # Iterate over the data read from each file.
    for fd in files_data:
        # Iterate over each data set.
        for d in fd:
            ind_values.add(d[MJD_COL])
        
    # Make a list from the set.
    unique_ind_values = list(ind_values)
    
    # Return the list sorted.
    return sorted(unique_ind_values)

def avg(items):
    
    sum = 0.0
    
    for i in items:
        sum += float(i)
    
    return sum / len(items)

def calculate_data_median(files_data):
    """
    
    """
        
    files_data_with_median = []
    
    for fd in files_data:
    
        # Get all the MJD values.
        mjd = [ x[MJD_COL] for x in fd ] 
        
        # Unique MJD values.
        mjd_set = set()
        
        for m in mjd:
            mjd_set.add(m)
            
        data_with_median = []
        
        # For each MJD value calculate the median and add the results
        # to the returned list.
        for e in mjd_set:
            same_mjd = [ x for x in fd if x[MJD_COL] == e]
            
            transposed = zip(*same_mjd)
            
            mag_mean = avg(transposed[MAG_COL])
            
            err_mean = avg(transposed[ERR_COL])
            
            first_item = same_mjd[0]
            
            new_row = [first_item[0], first_item[1], \
                       first_item[2], first_item[3], \
                       mag_mean, err_mean]
            
            data_with_median.append(new_row)
            
        files_data_with_median.append(data_with_median)   
        
    return files_data_with_median        

def process_data(files_data, progargs):
    """
    
    Process the data read. It should be a set of lists with items 
    containing a first field related to a common numeric domain,
    i.e. MJD as the independent variable.
    The following fields should be the dependent variable and error.
    
    """
    
    all_values = []
    
    if progargs.calculate_median:
        data_with_median = calculate_data_median(files_data)
        
        independent_values = get_unique_ind_values_sorted(data_with_median)
    else:
        independent_values = get_unique_ind_values_sorted(files_data)
    
    logging.debug("There are: " + str(len(independent_values)) + \
                  " independent values.")
    
    for iv in independent_values:
        
        # New value for each independent variable
        new_value = [iv]
        
        # Iterate over the data read from each file.
        for fd in files_data:
            # Search in each data set a value that matches the
            # value of the independent variable column.
            dv_list = [ row for row in fd if row[MJD_COL] == iv ]
                
            # The element found, if any, is into a list, so check
            # the length of the list.                
            if len(dv_list) > 0:
                
                # If any, add it to the new value.
                item = dv_list[0]
                
                new_value.extend([item[MAG_COL], item[ERR_COL]])
            else:
                # If not found add a value indicating no value.
                new_value.extend([NO_VALUE, NO_VALUE])     
            
        # Add the new value to the list of all values.
        all_values.append(new_value)            
    
    write_data(all_values, progargs.output_file_name)

def read_input_files(file_names, calculate_median):
    """
    
    Read a set of csv file whose names have been received as parameters.
    All the data read from the files is returned as a list that contains
    lists, each of these lists with data read from a file.
    
    """
    
    files_data = []
    
    for fn in file_names:
        
        data = []
        
        with open(fn, 'rb') as fr:
            reader = csv.reader(fr, delimiter=CSV_FILE_DELIM)  
            
            # Skip header.
            next(reader)      
        
            for row in reader:    
                if len(row) > 0:                                        
                    if calculate_median:
                                    
                        new_row = []
                                                
                        for i in range(len(row)):
                            if i == MJD_COL:
                                item = row[i]
                                new_row.extend([item[:item.find('.')]])
                            else:
                                new_row.extend([row[i]])     
                        data.append(new_row)
                    else:
                        data.append(row)  
                    
            files_data.append(data) 
            
        logging.debug("File " + fn + " read " + str(len(data)) + " lines.")

    return files_data

def main(progargs):
    """
    
    """
    
    exit_value = 0
    
    # Set the file, format and level of logging output.
    logging.basicConfig(filename=DEFAULT_LOG_FILE_NAME, \
                        format="%(asctime)s:%(levelname)s:%(message)s", \
                        level=logging.DEBUG)   
    
    # Check if enough arguments have been received.
    if len(sys.argv) < CurvesArguments.MIN_NUM_ARGVS:
        print "Al least " + str(CurvesArguments.MIN_NUM_ARGVS) + \
            " arguments may be provided."
        
        exit_value = 1
    else:        
        files_data = read_input_files(progargs.input_files_names, \
                                      progargs.calculate_median)
        
        # Check if enough data from files have been read.
        if len(files_data) < CurvesArguments.MIN_NUM_ARGVS:
            print "Only " + str(len(files_data)) + \
                " set(s) of data were read from files, it is not enough."
        else:
            process_data(files_data, progargs)
            
    return exit_value

# Where all begins ...
if __name__ == "__main__":
    
    # Create object to process program arguments.
    progargs = CurvesArguments()    
    
    # Process program arguments.
    progargs.parse()         
    
    # If no enough arguments are provided, show help and exit.
    if len(sys.argv) <= CurvesArguments.MIN_NUM_ARGVS:
        print "The number of program arguments are not enough."        
        progargs.print_help()
        sys.exit(1)
    else: 
        sys.exit(main(progargs))