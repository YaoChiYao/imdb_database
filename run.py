from createTable import Create_Table
from db2sql import convert_sqlite_to_mysql
from operate_funcs import MovieDatabase
if __name__ == "__main__":
    table = Create_Table()
    table.data_clean()
    table.build_table()
    table.write() #完成了表的创建与数据的填充
    #注意替换以下的password
    convert_sqlite_to_mysql(
        sqlite_file="movies.db",
        mysql_host="localhost",
        mysql_user="root",
        mysql_password="password",
        mysql_db="movies_db"
    )#完成了sqlite到mysql的转换，将数据迁移到mysql数据库中,命名movies_db
    #数据库对象，实现了增删查改等功能，详情见operate_functions.txt
    db=MovieDatabase(host='localhost', user='root', password='password', database='movies_db')
