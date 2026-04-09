from createTable import Create_Table

if __name__ == "__main__":
    table = Create_Table()
    table.data_clean()
    table.build_table()
    table.write() #完成了表的创建与数据的填充