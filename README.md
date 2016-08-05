Tools for communicating with Campbell Scientific data loggers. Based off an old script in my csv_utilites.


fetch.py currently downloads tables from a cr1000 logger.

### Example
./loggertools/fetch.py host port logger id station name [--tables=table1,table2] [--out=path_to_out_dir]


The core of LoggerTools is built around PyPak:
    (c) 2009 Dietrich Feist, Max Planck Institute for Biogeochemistry, Jena Germany


