import logging
import mysql.connector
from mysql.connector import errorcode

from components.base_miner import BaseMiner

logger = logging.getLogger("main")


class GithubMiner(BaseMiner):
    def __init__(self, args):
        super().__init__(args=args)
        
        self._cnx = None
        self._cur = None

    def _load_from_file(self, file):
        pass

    def dump_to_file(self, path):
        pass

    def process(self):
        pass

    def connect_to_db(self):
        if self.dbms == "sqlite":
            raise NotImplementedError
        elif self.dbms == 'mysql':
            try:
                cnx = mysql.connector.connect(user=self.db_username, password=self.db_password, host=self.host,
                                              port=self.port)
                
                cur = cnx.cursor()
                cur.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
                cur.execute(f"USE {self.db_name}")
                
                cnx.commit()
                
                self._cnx = cnx
                self._cur = cur

            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    logger.error("Something is wrong with your user name or password!")
                else:
                    logger.error(err)
            else:
                cnx.close()
        else:
            raise NotImplementedError
