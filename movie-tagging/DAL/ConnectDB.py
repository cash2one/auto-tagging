# -*- coding: utf8 -*-
import MySQLdb
import threading
from DALConfig import DALConfig
import traceback
class ConnectDB:
    instance={}
    thr=threading.Lock()
    def __init__(self):
        pass
    @staticmethod
    def get_con(db):
        try:
            db_config=DALConfig.MYSQL[db]
            if(not ConnectDB.instance.has_key(db)):
                ConnectDB.thr.acquire()
                if(not ConnectDB.instance.has_key(db)):
                    ConnectDB.instance[db]=MySQLdb.connect(\
                            host=db_config["host"],user=db_config["uname"],\
                            passwd=db_config["pwd"],db=db_config["db_name"],\
                            port=db_config["port"],\
                            charset=db_config["encoding"])
                    ConnectDB.instance[db].autocommit=True
                    ConnectDB.thr.release()
            return ConnectDB.instance[db]
        except Exception,ex:
            ConnectDB.thr.release()
            traceback.print_exc()
    @staticmethod
    def delete_con(db):
        try:
            if(ConnectDB.instance.has_key(db)):
                ConnectDB.thr.acquire()
                del(ConnectDB.instance[db])
                ConnectDB.thr.release()
        except Exception,ex:
            traceback.print_exc()
            ConnectDB.thr.release()
    @staticmethod
    def get_encoding(db):
        db_config=DALConfig.MYSQL[db]
        return db_config["encoding"]
    def __del__(self):
        ConnectDB.thr.acquire()
        if(len(ConnectDB.instance)):
            for each in ConnectDB.instance:
                each.close()
            ConnectDB.instance={}
        ConnectDB.thr.release()

