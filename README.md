# LoggerTools

Tools for communicating with Campbell Scientific data loggers. Based off an old script in my csv_utilites.


## Fetch
fetch.py currently downloads tables from a cr1000 logger, and save or updated associated .dat files

### Example
./loggertools/fetch.py host port logger_id station_name [--tables=table1,table2] [--out=path_to_out_dir]

Host, port, logger id, and station name, should be provided in that order

--tables=table1,table2 (optional, Default all) is a comma seperated(no spaces) list of tables 

--out=path_to_out_dir (optional, Default current directory) relative path to output directory. 


## List Tables
list_tables.py lists tables on logger

### Example
./loggertools/list_tables.py host port logger_id

Host, port, logger id, and station name, should be provided in that order


### Sources
The core of LoggerTools is built around PyPak:
    (c) 2009 Dietrich Feist, Max Planck Institute for Biogeochemistry, Jena Germany


