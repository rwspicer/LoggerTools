"""
pakskt.py 
pakbus Socket Class
author: rawser spicer
contact: rwspicer@alaska.edu


    A library for communicating with Campbell Scientific's data loggers that 
use the PakBus interface. The class is a wrapper around the pakbus
library that is part of the PyPak project. It is designed to be as simple to
use as possible by obfuscating the encoding and decoding of messages used in
the communication between devices.   
    
        
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

import pakbus as pkb
import struct


class pakskt:
    """ 
    A class for communicating with Campbell Scientific's data loggers that 
    use the PakBus interface.  
    """
    def __init__ (self, host, port, timeout, logger_id, cpu_id):
        """
            initializes the class by setting the host, port, timeout, logger and 
        computer id's to internal variables from client input. The other 
        internal variables are set to default and uninitialized states. 
        
        arguments:
            host:           (string) the host IP in a string or 'localhost'
            port:           (int) the port
            timeout:        (float) a number of seconds
            logger_id:      (12-bit int) ID of the logger
            computet_id:    (12-bit int) ID of computer 
        """
        self.host, self.port, self.timeout, self.logger_id, self.cpu_id =\
            host, port, timeout, logger_id, cpu_id
        self.socket = self.table_def = "needs initialization"
        self.programs = self.tables = []
        self.security_code = 0x0000

    #### functions for managing connection to logger #### 
    def open_socket (self):
        """
            opens a socket for listening to the logger on. 
        """
        self.socket = pkb.open_socket(self.host, self.port, self.timeout)
    
    def close_socket (self):
        """ 
            closes the socket
        
        preconditions:
            the socket needs to be open
        """
        self.socket.close()
    
    def ping (self):
        """ Function doc """
        return pkb.ping_node(self.socket,self.logger_id,self.cpu_id)
        
    def ping_until_response (self, max_tries = 10):
        """ Function doc """
        rsp = {}
        for attempt in range(max_tries):
            rsp = self.ping()
            if rsp != {}:
                break
        return rsp
        
    def is_reachable (self):
        """ Function doc """
        if self.ping_until_response() == {}:
            return False
        return True
    #### end ###
    
    #### functions for table processing #### 
    def get_table_def (self):
        """ Function doc """
        data, code = self.download('.TDF')
        if code:
            self.table_def = pkb.parse_tabledef(data)
        return code
        
    def get_tables (self):
        """ Function doc """
        self.tables = [table['Header']['TableName'] for table in self.table_def]
    
    def get_table_header (self, table_name):
        """ Function doc """
        table_num = pkb.get_TableNbr(self.table_def, table_name) - 1
        units = {}
        intervals = {}
        fields = self.table_def[table_num]['Fields']
        for item in fields:
            units[item['FieldName']] = item['Units']
            intervals[item['FieldName']] = item['Processing']
        
        return units, intervals 
    
    def get_table_data (self, table_name, last_recived = 0, show = False):
        """ Function doc """
        #~ print "GETTING DATA"
        table = []
        self.open_socket()
        while True:
            if show:
                try:
                    print "Last Record Recived: " + str(table[-1]['RecNbr'])
                except IndexError:
                    pass
            try:
                #self.open_socket()
                data, is_more = pkb.collect_data(self.socket,
                                             self.logger_id,
                                             self.cpu_id,
                                             self.table_def,
                                             table_name,
                                             CollectMode = 0x04,
                                             P1 = last_recived)
                
            except KeyError:
                print last_recived
                continue
            except struct.error:
                print "struct.error, but this may be the last record so returnign data"
                return table
                
            #~ print data
            try:
                for rec in (data[0]['RecFrag']):
                    table.append(rec)
                last_recived += data[0]['NbrOfRecs']
            except:
                break
            #~ if is_more == 0:
                #~ break
        return table
    #### end ####    
    
    #### functions for program & file management ####
    def get_programs (self):
        """ Function doc """
        data, code = self.download('.DIR')
        if code:
            file_dir = pkb.parse_filedir(data)
            self.programs = [files['FileName'] for files in file_dir['files']]
        return code

    def get_program_status (self):
        """ Function doc """
	self.open_socket()
        packet, trans_no = pkb.pkt_getprogstat_cmd(self.logger_id, self.cpu_id)
        pkb.send(self.socket, packet)
        header, message = pkb.wait_pkt(self.socket, 
                                      self.logger_id, 
                                      self.cpu_id, 
                                      trans_no)
        return message
        
    def control (self, file_name, action):
        """ Function doc """
        packet, trans_no = pkb.pkt_filecontrol_cmd(self.logger_id,
                                                   self.cpu_id,
                                                   file_name, 
                                                   action, 
                                                   self.security_code, 
                                                   None)
        pkb.send(self.socket, packet)
        header, message = pkb.wait_pkt(self.socket,
                                   self.logger_id,
                                   self.cpu_id, 
                                   trans_no)
        return message
        
    def start (self, program):
        """ Function doc """
        return self.control(program, 1)
    
    def download (self, file_name):
        """ Function doc """
        data, code = pkb.fileupload(self.socket, 
                                   self.logger_id,
                                   self.cpu_id,
                                   file_name,
                                   self.security_code)
        
        return data, (False if code == 14 else True)
        
    def upload (self, file_name, data):
        """ Function doc """
        code = pkb.filedownload(self.socket, 
                                self.logger_id, 
                                self.cpu_id, 
                                file_name, 
                                data, 
                                self.security_code)
        return True if code == 0 else False
    #### end ####    
    
    
    
#### utilities ####
from datetime import datetime
def correct_table_dates (table):
    """
        this function takes a table as returned by pakskt.get_table_data
    and updates the date field to a standard datetime object if it exists.
    
    returns true on success 
    """
    try:
        for row in table:
             row['TimeOfRec'] = \
             datetime.fromtimestamp(pkb.nsec_to_time(row['TimeOfRec']))
    except:
        return table, False
    return table, True
        
        
def test_suite (host = 'localhost', port = 7808 , timeout = 30, 
                logger_id = 14, cpu_id =2050):
    """ Function doc """
    print "Initializing" 
    test = pakskt(host, port, timeout, logger_id, cpu_id)
    print "Opening socket"
    test.open_socket()
    print "Finding Logger"
    if not test.is_reachable():
        raise StandardError, "logger not found"
    print "Fetching Table Definition"
    if not test.get_table_def():
        raise StandardError, "could not get table definition"
    print "Fetching Tables"
    test.get_tables()
    print "Getting Programs"
    if not test.get_programs():
        raise StandardError, "could not get programs"
    print "test complete returning pakskt object"
    return test
#### end ####
