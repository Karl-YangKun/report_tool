import database
import json
import logging
import numpy as np



conn =0
cursor =0
datebase_conf =r"C:\Users\k1104\Desktop\Python\configurable_gui\database.json"
PROJECT_TABLE = "Projects"
CHIP_TABLE = "Chips"
REPORT_TABLE = "Report"

class Database:
    def __init__(self, cfg_file):
        with open(cfg_file) as f:
            self.config = json.load(f)
        
        self.conn =0
        self.cursor =0
        self.project_table = self.config['Database']['Table2']
        self.chip_table = self.config['Database']['Table1']
        self.report_table = self.config['Database']['Table3']
        
        self.openDB()
    

    #连接数据库并创建游标
    def openDB(self):
        file_path = self.config['Database']['database_file']
        print("open database: "+file_path)

        #链接数据库
        self.conn = database.mdb_conn(file_path)
        #创建游标
        self.cursor=self.conn.cursor()
 
    #断链数据库并关闭游标   
    def closeDB(self):
        self.cursor.close() 
        self.conn.close()
        print("database closed")
        
    #查询操作
    def db_select(self, command, cond):
        #构造SQL指令
        params = self.config["Command"][command]
        db_cfg = self.config["Database"]
        
        #组装SQL操作
        cmd = params["type"] + " "
        #组装SQL关键字
        if 'key' in params:
            cmd = cmd + params["key"] + " "
        #组装SQL操作目标和表数据源、限定条件
        on = "on "
        f = "from "
        c = "where "
        t = ""
        o = "order by "
        target_list=[]
        last_index = -1
        for i in range(1,db_cfg["Table_numb"]+1):
            current_tb = "Table"+str(i)
            if current_tb not in params["target"]:
                continue
            pre = ""
            #收集表
            f = f + db_cfg[current_tb] + ' '
            #如果是多表连接，需要添加前缀
            if 'type' in params["target"]:
                pre = db_cfg[current_tb]+'.'
                f = f + params["target"]['type'] + ' '
                on = on + pre + params["target"][current_tb]["on"] + '='
                last_index = f.rfind(params["target"]['type'])
            
            #收集数据目标
            for i in params["target"][current_tb]["key"]:
                t =  t + ',' + pre + i 
                logging.debug(f"SQL target: {t}")
                target_list.append(pre+i)
                
            #收集限定条件
            if 'conditions' in params and current_tb in params['conditions']:
                for v in params['conditions'][current_tb]:
                    #判断限定条件值是否提供
                    if v in cond:
                        logging.debug(f"SQL condition: {v}")
                        c = c+pre+v+"='"+cond[v]+"' and "
                    else:
                        raise ValueError(f"条件{v}值不存在")
                    
            #收集排序条件
            if 'order_by' in params and current_tb in params['order_by']:
                for i in params["order_by"][current_tb]:
                    o =  o + pre + i + ','
                    logging.debug(f"SQL order: {i}")
            
        #组装数据目标
        cmd = cmd + t[1:] + " "
        #组装数据表
        cmd = cmd + f[:last_index] + " "
        #组装限定条件
        #收集无参数限定条件
        if 'no_param_cond' in params:
            for npc in params['no_param_cond']:
                logging.debug(f"no_param_cond: {npc}")
                c = c + npc + " and "
                    
        last_index = -1
        last_index = on.rfind('=')
        if last_index != -1:
            cmd = cmd + on[:last_index] + ' ' 

        last_index = -1
        last_index = c.rfind("and")
        if last_index != -1:
            cmd = cmd + c[:last_index] + ' ' 
        
        #组装排序条件    
        last_index = -1
        last_index = o.rfind(",")
        if last_index != -1:
            cmd = cmd + o[:last_index] + ' ' + params['order_by']['orientation']
        
        logging.info(f"SQL cmd: {cmd} from {command}")
        return database.mdb_sel(self.cursor,cmd),target_list

    def db_insert(self, command, value):
        #构造SQL指令
        params = self.config["Command"][command]
        db_cfg = self.config["Database"]
        
        #组装SQL操作
        cmd = params["type"] + " into " 
        #组装SQL关键字
        if 'key' in params:
            cmd = cmd + params["key"] + " " 
        
        tg = ''   
        va = ' VALUES('
        for i in range(1,db_cfg["Table_numb"]+1):
            current_tb = "Table"+str(i)
            if current_tb not in params["target"]:
                continue
            
            cmd = cmd + db_cfg[current_tb] + '('
            #收集数据目标
            for i in params["target"][current_tb]["key"]:
                tg =  tg  + i + ','
                if i in value:
                    logging.debug(f"SQL target: {i}:{value[i]}")
                    va = va + "'" + value[i] + "',"
                else:
                    raise ValueError(f"{i}值没提供")
                
            if "now_time_key" in params["target"][current_tb]:
                for i in params["target"][current_tb]["now_time_key"]:
                    tg =  tg  + i + ','
                    va = va + 'NOW(),'
        
        #组装目标
        last_index = -1
        last_index = tg.rfind(',')
        if last_index != -1:
            cmd = cmd + tg[:last_index] + ') ' 
        #组装数值                
        last_index = -1
        last_index = va.rfind(',')
        if last_index != -1:
            cmd = cmd + va[:last_index] + ')'         
        
        logging.info(f"SQL cmd: {cmd} from {command}")
        return database.mdb_add(self.conn,self.cursor,cmd)
    
    def db_update(self, command, value):
        #构造SQL指令
        params = self.config["Command"][command]
        db_cfg = self.config["Database"]
        
        #组装SQL操作
        tg = params["type"] + ' '
        
        c = 'where '
        for i in range(1,db_cfg["Table_numb"]+1):
            current_tb = "Table"+str(i)
            if current_tb not in params["target"]:
                continue
            
            tg = tg + db_cfg[current_tb] + ' set '
            #组装数据目标
            if "key" in params["target"][current_tb]:
                for i in params["target"][current_tb]["key"]:
                    #判断值是否提供
                    if i in value:
                        logging.debug(f"SQL value: {i}")
                        tg =  tg + i + "='" + value[i] + "',"
                    else:
                        raise ValueError(f"{v}值不存在")
                    
            if "now_time_key" in params["target"][current_tb]:
                for i in params["target"][current_tb]["now_time_key"]:
                    tg =  tg + i + "=" + 'NOW(),'
        
            #收集限定条件
            if 'conditions' in params and current_tb in params['conditions']:
                for v in params['conditions'][current_tb]:
                    #判断限定条件值是否提供
                    if v in value:
                        logging.debug(f"SQL condition: {v}")
                        if isinstance(value[v], int):
                            c = c + v+"="+ str(value[v]) +" and "
                        else:
                            c = c + v+"='"+value[v]+"' and "
                    else:
                        raise ValueError(f"条件{v}值不存在")
                
        #组装目标
        last_index = -1
        last_index = tg.rfind(',')
        if last_index != -1:
            cmd = tg[:last_index] + ' ' 
            
        #组装限定条件               
        last_index = -1
        last_index = c.rfind('and')
        if last_index != -1:
            cmd = cmd + c[:last_index]       
        
        logging.info(f"SQL cmd: {cmd} from {command}")
        return database.mdb_modi(self.conn,self.cursor,cmd)
    
    def db_delete(self, command, cond):
        #构造SQL指令
        params = self.config["Command"][command]
        db_cfg = self.config["Database"]
        
        #组装SQL操作
        cmd = params["type"] + " from " + db_cfg[params["target"]] + " WHERE "
        for c in params['conditions'][params["target"]]:
            #判断限定条件值是否提供
            if c in cond:
                logging.debug(f"SQL condition: {c}")
                if isinstance(cond[c], int):
                    cmd = cmd + c +"=" + str(cond[c]) + " and "
                else:
                    cmd = cmd + c +"='" + cond[c] + "' and "
                
            else:
                raise ValueError(f"条件{c}值不存在")
            
        last_index = -1
        last_index = cmd.rfind('and')
        
        logging.info(f"SQL cmd: {cmd[:last_index]} from {command}")
        return database.mdb_del(self.conn,self.cursor,cmd[:last_index])    
                        
                        
        
    #使用json定义指令
    def operateDbByJson(self, command, cond=0):
        params = self.config["Command"][command]
        if params['type'] in "select":
            return self.db_select( command, cond)
        elif params['type'] in "insert":
            if(self.db_insert( command, cond)):
                return False,"写入成功\n"
            else:
                return False,"写入失败\n"
        elif params['type'] in "update":
            if(self.db_update( command, cond)):
                return False,"更新成功\n"
            else:
                return False,"更新失败\n"
        elif params['type'] in "delete":
            if(self.db_delete( command, cond)):
                return False,"删除成功\n"
            else:
                return False,"删除失败\n"
        else:
            return False,"指令类型错误\n"
        


        
if __name__ == "__main__":
    #file_path是access文件的绝对路径。
    file_path=r"C:\Users\k1104\Desktop\Python\configurable_gui\module.accdb"
    #链接数据库
    conn = database.mdb_conn(file_path)
    #创建游标
    cursor=conn.cursor()
    
    SQL ="select Projects.*,Report.* \
        from Projects inner join Report  on Projects.ID=Report.project_id \
        where Projects.Client='小鸟' and Projects.Project='DeltaX' and datediff('ww',recent,date())=0  \
        order by Projects.Client,Projects.Project desc"
    # SQL ="INSERT INTO Customers(Client, Project,Chip) VALUES('艾尔伯','Y37','D10L')"
    print(SQL)
    data= database.mdb_sel(cursor,SQL)    
    print(data)

    #关闭游标和链接
    cursor.close() 
    conn.close()