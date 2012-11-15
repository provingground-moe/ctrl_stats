#!/usr/bin/env python

import os, sys
import eups
from lsst.ctrl.stats.reader import Reader
from lsst.ctrl.stats.classifier import Classifier
from lsst.ctrl.stats.databaseManager import DatabaseManager
from lsst.daf.persistence import DbAuth
from lsst.pex.policy import Policy

if __name__ == "__main__":
    tableName = "nodes"

    host = sys.argv[1]
    port = sys.argv[2]
    database = sys.argv[3]
    reader = Reader(sys.argv[4])
    recordList = reader.getRecordList()
    records = recordList.getRecords()

    #
    # get database authorization info
    #
    home = os.getenv("HOME")
    pol = Policy(os.path.join(home,".lsst","db-auth.paf"))
    
    dbAuth = DbAuth()
    user = dbAuth.username(host, port)
    password = dbAuth.password(host, port)

    dbm = DatabaseManager(host, int(port))
    dbm.connect(user,password)

    if not dbm.dbExists(database):
        dbm.createDb(database) 
    # this second connect is necessary to 
    # connect to the database. It
    # reuses the connection.
    dbm.connect(user,password,database)
        

    #
    # This load the nodes.sql, which creates the table
    # we're writing into.  The table won't be created
    # if it already exists. (see the SQL for details).

    pkg = eups.productDir("ctrl_stats")
    filePath = os.path.join(pkg,"etc","nodes.sql")
    dbm.loadSqlScript(filePath, user, password, database)

    table = database+"."+tableName

    classifier = Classifier()
    for job in records:
        entries = classifier.classify(records[job])
        for ent in entries:
            ins = ent.getInsertString(table)
            print ins
            dbm.execute(ins)