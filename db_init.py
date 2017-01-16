import dbm
from settings import DB_NAME

with dbm.open(DB_NAME, 'c') as db:
    with open('db_init.txt') as dbi:
        for line in dbi.readlines():
            rec = line.split()
            db[rec[0]] = rec[1]