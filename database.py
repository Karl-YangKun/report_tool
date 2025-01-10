import pyodbc
 
def mdb_conn(db_name, password = ""):
    """
    功能：创建数据库连接
    :param db_name: 数据库名称
    :param db_name: 数据库密码，默认为空
    :return: 返回数据库连接
    """
    str = 'Driver={Microsoft Access Driver (*.mdb)};PWD' + password + ";DBQ=" + db_name
    # conn = pyodbc.win_connect_mdb(str)
    return pyodbc.connect(u'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + db_name,autocommit=True)

# 常规复用指令
def mdb_common(conn, cur, sql):
    try:
        cur.execute(sql)
    except Exception as e:
        print(e)
        return False
    finally:
        conn.commit()
        return True
    
def mdb_sel(cur, sql):
    """
    功能：向数据库查询数据
    :param cur: 游标
    :param sql: sql语句
    :return: 查询结果集
    """
    try:
        cur.execute(sql)
    except Exception as e:
        print(e)
        return []
    finally:
        return cur.fetchall()
 
def mdb_add(conn, cur, sql):
    """
    功能：向数据库插入数据
    :param conn: 数据库连接
    :param cur: 游标
    :param sql: sql语句
    :return: sql语句是否执行成功
    """
    return mdb_common(conn, cur, sql)
    
def mdb_del(conn, cur, sql):
    """
    功能：向数据库删除数据
    :param conn: 数据库连接
    :param cur: 游标
    :param sql: sql语句
    :return: sql语句是否执行成功
    """
    return mdb_common(conn, cur, sql)
  
def mdb_modi(conn, cur, sql):
    """
    功能：向数据库修改数据
    :param conn: 数据库连接
    :param cur: 游标
    :param sql: sql语句
    :return: sql语句是否执行成功
    """
    return mdb_common(conn, cur, sql)

    
if __name__ == '__main__':
    #file_path是access文件的绝对路径。
    file_path=r"C:\Users\k1104\Desktop\database\test.accdb"
    print("database: "+file_path)

    #链接数据库
    conn = mdb_conn(file_path)
    #创建游标
    cursor=conn.cursor()


    # tb_name是access数据库中的表名
    tb_name="table1"
    SQL =('select * from %s' %tb_name)
    # 获取数据库中表的全部数据
    data= mdb_sel(cursor,SQL)
    print(data)

    print(cursor.rowcount)
    SQL ="Delete * FROM " + tb_name + " where ID = 2"
    if(mdb_del(conn,cursor,SQL)):
        print("删除成功")
        print(cursor.rowcount)

    #关闭游标和链接
    cursor.close() 
    conn.close()