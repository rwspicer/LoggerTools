"""
connect.py

file for creating a connection to a data logger


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
import socketlib.pakskt as pks
import time

class Connection (object):
    """ Class doc """
    
    def __init__ (self, host, port, logger_id):
        """ Class initialiser """
        self.host = host
        self.port = port
        self.logger_id = logger_id
        self.my_id = 2050
        self.connection = pks.pakskt(self.host, self.port, 30, self.logger_id, 
                                    self.my_id)
        
    def connect(self):
        """
        connect to the data logger
        """
        self.connection.open_socket()
        self.connection.ping()
        return True
        
        
        #### maybe this is important but it seems to work with out it.
        ### wake up the logger 
        #~ pks.pkb.send(self.connection.socket,"")
        #~ pks.pkb.send(self.connection.socket,"")
        #~ pks.pkb.send(self.connection.socket,"")
        
        #~ rsp = self.connection.ping()
        
        #~ try:
            #~ rsp["MsgType"]
            #~ return True
        #~ except KeyError:
            #~ return False
        #~ return True 
           
    def ping(self):
        """
        ping the data logger
        """
        rsp = self.connection.ping()
        try:
            rsp["MsgType"]
            return True
        except KeyError:
            return False
            
            
    def disconnect (self):
        """
        disconnect the data logger
        """
        try:
            self.connection.close_socket()
        except:
            pass
        
    def __call__ (self):
        """
        """
        return self.connection
        
    def __del__ (self):
        """
        destroy the connection
        """
        self.disconnect()
            
        
        
            

def test(host, port, logger_id):
    
    conn = Connection(host,port,logger_id)
   
    connected = conn.connect()
    print "connected", connected
    
    try:
        print "control-c to exit"
        while True:
            time.sleep(3)
            print conn.ping()
    except KeyboardInterrupt:
        print "exiting"
        return
    
    
if __name__ == "__main__":
    test()
    
    
    
        
        
    
    
