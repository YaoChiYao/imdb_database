import sqlite3
import pymysql
import sys

def convert_sqlite_to_mysql(sqlite_file, mysql_host, mysql_user, mysql_password, mysql_db):
    # 连接到 SQLite
    sqlite_conn = sqlite3.connect(sqlite_file)
    sqlite_cur = sqlite_conn.cursor()
    
    # 连接到 MySQL
    mysql_conn = pymysql.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        charset='utf8mb4'
    )
    mysql_cur = mysql_conn.cursor()
    
    # 创建数据库
    mysql_cur.execute(f"CREATE DATABASE IF NOT EXISTS {mysql_db} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    mysql_cur.execute(f"USE {mysql_db}")
    
    # 获取所有表
    sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = sqlite_cur.fetchall()
    
    for table in tables:
        table_name = table[0]
        if table_name == 'sqlite_sequence':
            continue
            
        print(f"处理表: {table_name}")
        
        # 获取表结构
        sqlite_cur.execute(f"PRAGMA table_info({table_name})")
        columns = sqlite_cur.fetchall()
        
        # 构建 MySQL CREATE TABLE 语句
        column_defs = []
        for col in columns:
            col_name = col[1]
            col_type = col[2].upper()
            is_pk = col[5] > 0
            
            # 类型映射
            if 'INT' in col_type:
                mysql_type = 'INT'
                if is_pk and 'AUTOINCREMENT' in str(sqlite_cur.execute(f"SELECT sql FROM sqlite_master WHERE name='{table_name}'").fetchone()):
                    mysql_type = 'INT AUTO_INCREMENT'
            elif 'CHAR' in col_type or 'TEXT' in col_type or 'CLOB' in col_type:
                mysql_type = 'TEXT'
            elif 'BLOB' in col_type:
                mysql_type = 'LONGBLOB'
            elif 'REAL' in col_type or 'FLOAT' in col_type or 'DOUBLE' in col_type:
                mysql_type = 'DOUBLE'
            else:
                mysql_type = 'VARCHAR(255)'
            
            column_defs.append(f"`{col_name}` {mysql_type}")
        
        # 创建表
        create_table_sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({', '.join(column_defs)}) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        try:
            mysql_cur.execute(create_table_sql)
        except Exception as e:
            print(f"创建表 {table_name} 失败: {e}")
        
        # 复制数据
        sqlite_cur.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cur.fetchall()
        
        if rows:
            # 获取列名
            col_names = [col[1] for col in columns]
            placeholders = ', '.join(['%s'] * len(col_names))
            insert_sql = f"INSERT INTO `{table_name}` ({', '.join([f'`{name}`' for name in col_names])}) VALUES ({placeholders})"
            
            for row in rows:
                try:
                    mysql_cur.execute(insert_sql, row)
                except Exception as e:
                    print(f"插入数据失败: {e}")
                    print(f"SQL: {insert_sql}")
                    print(f"数据: {row}")
    
    mysql_conn.commit()
    sqlite_conn.close()
    mysql_conn.close()
    print("转换完成！")

if __name__ == "__main__":
    # 安装依赖：pip install pymysql
    convert_sqlite_to_mysql(
        sqlite_file="movies.db",
        mysql_host="localhost",
        mysql_user="root",
        mysql_password="GLOWWORM",
        mysql_db="movies_db"
    )