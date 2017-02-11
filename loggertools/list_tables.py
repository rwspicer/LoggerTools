#!/usr/bin/env python
"""
list_tables.py 
Rawser Spicer

Copyright 2016 Rawser Spicer, University of Alaska Fairbanks

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

def list_tables ():
    """
    list tables on logger
    """
    arguments = sys.argv[1:]
    if len(arguments) == 0:
        print ("usage: ./list_tables.py <host> <port> <logger id> ")
        return
    
    host = arguments[0]
    port = int(arguments[1])
    logger_id = int(arguments[2])
    
    print "Connecting to logger... "

    conn = connect.Connection(host = host, port = port, logger_id = logger_id)
    
    logger = table.Tables(conn)
    
    print "Fetching tables from logger... "

    tables = logger.list_tables()
    print tables 


if __name__ == "__main__":
    list_tables()
