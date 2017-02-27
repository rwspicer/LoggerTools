"""
table.py

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
from connect import Connection
import socketlib.pakskt as pks
import os
import shutil
from datetime import datetime

class Tables(object):
    """
    a class class for downloading and formating cr1000 .dat tables
    """
    def __init__ (self, conn):
        """ 
        Class initialiser. set up connection, and get table info
        """
        self.conn = conn
        self.tables = {}
        self.refresh_table_definations()
        
    def refresh_table_definations(self):
        """
            refreshes the table definitions, and list of tables on the 
        connected logger.
        """
        rsp = self.conn.connect()
        if rsp == False:
            print "refresh_table_definations", "Connection not established" 
        self.conn().get_table_def()
        self.conn().get_tables() 
        self.table_list = self.conn().tables
        
    def list_tables (self):
        """
        returns the list of tables
        """
        return self.table_list
        
    def download_table (self, table, start_with = 0, show = False):
        """ 
        download a table
        
        input:
            table: the table name
            starts_with: the record to start with (default 0)
        
        post:
            self.tables[table] is a list of rows from the logger table 
        named 'table'
        """
#        self.conn.connect()
        self.conn().open_socket()
        temp = self.conn().get_table_data(table, start_with, show)
        self.tables[table] = pks.correct_table_dates(temp)[0]
        
    def download_list (self, table_list):
        """
        download a list of tables
        
        input: 
            table_list: a list of tables to download
        
        self.tables will have values for all tables in table_list
        """
        for t in table_list:
            #~ print t
            self.download_table(t)
         
    def download_all (self):
        """
        download all tables on the logger
        """
        self.download_list(self.list_tables())
        
    def get_program_info (self, refresh = False):
        """
        get infromation on the program running on the logger
        
        refresh: bool to forece a refresh
        """
        if refresh == False:
            try:
                return self.program_info 
            except AttributeError:
                pass
#        self.conn.connect()
        self.conn().open_socket()
        self.program_info = dict(self.conn().get_program_status())
#        while self.program_info == {}:
#            self.program_info = self.conn().get_program_status()
        return self.program_info 
    
    def get_table_header_data (self, table):
        """
        return the header info for a table
        """
        table_def = self.conn().table_def
        for header in table_def:
            if table == header['Header']['TableName']:
                return header
        raise StandardError, "Header data not found for table: '" + table + "'"
        
    def get_table_column_order (self, table):
        """
        get the order of columns
        """
        header_data = self.get_table_header_data(table)
        order = []
        for col in header_data ['Fields']:
            order.append(col['FieldName'])
        return order
        
    def get_file_last_record (self, filename):
        """
        read the last record from a file
        
        retruns -1 if file does not exits, 0 if program has changed, > 0 if there are records 
        """
        if not os.path.exists(filename):
            return -1
        with open(filename, 'r') as fd:
            text = fd.read()
            rows = text.split('\n')
            progsig = rows[0].split(',')[6]
            if int(progsig.replace('"','')) != \
                    int(self.get_program_info()['ProgSig']):
                return 0
                
            if rows[-1] == "":
                del rows[-1]
            return int(rows[-1].split(',')[1].replace('"',''))
            
    
    def generate_file_header (self, table, logger_name):
        """
        retruns the file header as a string
        """
        header_data = self.get_table_header_data(table)
        #~ order = self.get_table_column_order(table)
        
        # d for d
        d = ','
        # q for q
        q = lambda x: '"' + str(x) + '"'
        
        info = self.get_program_info()
        #print info
        header_r0 = '"TOA5"' + d + \
                 q(logger_name) + d + \
                 q(info["OSVer"].split('.')[0])  + d + \
                 q(str(info["SerialNbr"]))+ d + \
                 q(info["OSVer"]) + d + \
                 q(info["ProgName"]) + d + \
                 q(str(info['ProgSig'])) + d + \
                 q(table)
        
        
        header_r1 = '"TIMESTAMP","RECORD"'
        header_r2 = '"TS","RN"'
        header_r3 = '"",""'
        for col in header_data ['Fields']:
            if len(col['SubDim']) == 0:
                header_r1 += d + q(col['FieldName'])
                header_r2 += d + q(col['Units'])
                header_r3 += d + q(col['Processing'])
            else:
                for i in range(col['SubDim'][0]):
                    header_r1 += d + q(col['FieldName'] + '(' + str(i+1) + ')')
                    header_r2 += d + q(col['Units'])
                    header_r3 += d + q(col['Processing'])
        
        header = header_r0 + '\n' + \
                 header_r1 + '\n' + \
                 header_r2 + '\n' + \
                 header_r3 + '\n' 
        return header
        
    def generate_file_body (self, table):
        """
        generate the table body as a strign
        """
        # d for delimiter
        d = ','
        # q for quote
        q = lambda x: '"' + str(x) + '"'
        text = ""
        for row in self.tables[table]:
            time = row['TimeOfRec']
            rec_num = row['RecNbr']
    
            text += q(time) + d + q(rec_num)
            
            for field in self.get_table_column_order(table):
                data = row['Fields'][field]
                if not type(data) is list:
                    data = [data]
                for idx in range(len(data)):
                    datum = data[idx]
                    text += d + q(datum) 
            text += '\n'
        return text
        
    def save_table (self, table, directory, logger_name, show = False):
        """
        save a table
        """
        self.get_program_info()
        f_name = logger_name + '_' + table +'.dat'
        f_path = os.path.join(directory,f_name)
        last_rec = self.get_file_last_record(f_path)
#        print self.program_info        
        if last_rec == -1:
            # DNE
            self.download_table(table, show = show)
            header = self.generate_file_header(table, logger_name)
            body = self.generate_file_body(table)
            with open (f_path, 'w') as dat:
                dat.write(header + body)
        elif last_rec == 0:
            # program change
            # MOVE old file
            d_tag = datetime.strftime(datetime.now(),'%Y-%m-%d')
            f_name2 = logger_name + '_' + table + "_backup-" + d_tag + '.dat'
            shutil.copy(f_path, os.path.join(directory,f_name2 ))
            # Make new
            self.download_table(table, show = show)
            header = self.generate_file_header(table, logger_name)
            body = self.generate_file_body(table)
            with open (f_path, 'w') as dat:
                dat.write(header + body)
        else:
            # append
            self.download_table(table, last_rec+1, show = show)
            body = self.generate_file_body(table)
            with open (f_path, 'a') as dat:
                dat.write(body)
        
    def save_tables(self):
        """
        save all tables 
        """
        pass
        


def test(host, port, logger_id):
    
    #~ Connection(host,port,logger_id)
   
    tables = Tables(Connection(host,port,logger_id))
    
    tables.download_all()
    #~ print tables
    return tables
    
    
    
if __name__ == "__main__":
    test()
        
    
    
