#!/usr/bin/env python
"""
fetch.py 
Ross Spicer

Copyright 2016 Rawser Spicer, Uinversity of Alaska Fairbanks

    This file is part of LoggerTools.

    LoggerTools is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    LoggerTools is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with LoggerTools.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import table
import connect

def fetch ():
    """
    download and save or update tables from the logger  
    """
    arguments = sys.argv[1:]
    if len(arguments) == 0:
        print ("usage: ./fetch.py <host> <port> <logger id> <station name> "
               "[--tables=table1,table2] [--out=path_to_out_dir]")
        return
    
    host = arguments[0]
    port = int(arguments[1])
    logger_id = int(arguments[2])
    station_name = str(arguments[3])
    optional = {}
    for arg in arguments[4:]:
        arg = arg.split('=')
        optional[arg[0].replace('--','')] = arg[1]
        
    try:
        directory = optional['out']
    except KeyError:
        directory = './'
    
    print "Connecting to logger... "

    conn = connect.Connection(host = host, port = port, logger_id = logger_id)
    
    logger = table.Tables(conn)
    #~ print logger
    
    print "Fetching data from logger... "
    try:
        tables = optional['tables']
        tables = tables.split(',')
    except KeyError:
        tables = logger.list_tables()
    #~ logger.download_list(tables)
    
    for t in tables:
        logger.save_table(t, directory, station_name)
        
    
    
    
    
    

if __name__ == "__main__":
    fetch()
