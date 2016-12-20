from ConnectDB import ConnectDB


class MySqlDAL:
    def __init__(self, db ='Attr'):
        self.__con = ConnectDB.get_con(db)
        self.__encoding = ConnectDB.get_encoding(db)
        self.__cursor = self.__con.cursor()

    def select(self, sql_cmd):
        self.__cursor.execute(sql_cmd)
        result = self.__cursor.fetchall()
        return result
