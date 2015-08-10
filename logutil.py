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

"""Provides some utility functions for logging."""

import os
import logging

# Log levels, taken from logging.
LOG_LEVELS = { "CRITICAL" : logging.CRITICAL,
              "ERROR": logging.ERROR,
              "WARNING": logging.WARNING,
              "INFO": logging.INFO,
              "DEBUG": logging.DEBUG }

DEFAULT_LOG_LEVEL_NAME = "WARNING"

DEFAULT_LOG_FILE_NAME = "ycas_log.txt"

def convert_logging_level(level):
    """ Convert the log level received to one of the logging module checking
    if the level indicated as program argument is valid.
    
    Args:
        level: Level to convert.
    
    """
    
    try:
        logging_level = LOG_LEVELS[level]
    except KeyError as ke:
        # If no valid log level is indicated use the default level.
        logging_level = LOG_LEVELS[DEFAULT_LOG_LEVEL_NAME]
        
        logging.warning("Log level provided is no valid '%s', using default value '%s'" 
                        % (level, DEFAULT_LOG_LEVEL_NAME))
    
    return logging_level

def init_log(progargs):
    """ Initializes the file log and messages format. 
    
    Args:
        progargs: Program arguments.
    
    """    
    
    # Set the logging level.
    logging_level = convert_logging_level(progargs.log_level)
    
    # If a file name has been provided as program argument use it.
    if progargs.log_file_provided:
        log_file = progargs.log_file_name
    else:
        log_file = DEFAULT_LOG_FILE_NAME
        
    if progargs.target_dir_provided:
        log_file = os.path.join(progargs.target_dir, log_file)
    
    # Set the file, format and level of logging output.
    logging.basicConfig(filename=log_file, \
                        format="%(asctime)s:%(levelname)s:%(message)s", \
                        level=logging_level)
    
    logging.debug("Logging initialized.")