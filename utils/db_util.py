import pymysql
from config.db_config import DB_CONFIG

class DBUtil:
    @staticmethod
    def get_connection():
        """获取数据库连接"""
        try:
            conn = pymysql.connect(
                host=DB_CONFIG["host"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                database=DB_CONFIG["database"],
                charset=DB_CONFIG["charset"]
            )
            return conn
        except Exception as e:
            raise Exception(f"数据库连接失败：{str(e)}")
    
    @staticmethod
    def close(conn, cursor):
        """关闭数据库连接和游标"""
        if cursor:
            cursor.close()
        if conn:
            conn.close()