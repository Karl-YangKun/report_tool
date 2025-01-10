import logging
from tkinter import *
import tkinter as tk
import db_operator as op
import tkinter.messagebox as msgbox
import my_utils
import openpyxl
import time
from datetime import datetime
from functools import partial
from db_operator import Database as DB


class Processor:
    def __init__(self, config):
        self.config = config
        self.gui_items = 0
        self.db = DB(config['Private']['db_conf'])
        
        # logging.basicConfig(level=logging.DEBUG,
        #             format='%(asctime)s - %(levelname)s - %(message)s')

    def deinit(self):
        self.db.closeDB()
    
    #窗口类语柄    
    def set_items(self, gui_items):
        self.gui_items=gui_items
        
    def set_root(self, root):
        self.root=root
        
    def handler_event_adaptor(event, fun, **kwds):
        logging.debug(event)
        logging.debug(fun)
        logging.debug(kwds)
        """事件处理函数的适配器，相当于中介，那个event是从那里来的呢，我也纳闷，这也许就是python的伟大之处吧"""
        return lambda event, fun=fun, kwds=kwds: fun(event, **kwds)

    def exter_db_get(self,cmd):
        """这个函数是为了给外部使用db_operator中的功能"""
        data,_ = self.db.operateDbByJson(cmd) 
        return data
        
    #转换成单值列表
    def change_to_single_list(self,data,ind):
        li=[]
        for c in data:
            li.append(c[ind])
        return li
    
    #下面函数耦合高
    #联动更新    
    def updateItem(self,event,**kwds):
        logging.debug(kwds)
        
        if(self.gui_items == 0):
            raise ValueError(f"gui_items不存在")
        
        form = {}
        
        for i in kwds['input']:
            form[i] = self.gui_items[i][0].get()
        logging.debug(form)    
        
        datas,data_name = self.db.operateDbByJson(kwds['cmd'],form) 
        logging.debug(datas)
        data_name = my_utils.remove_prefix(data_name)
        
        
        if(len(datas)):
            for i,name in enumerate(data_name):
                #需要输出的数据
                if name in kwds['output']:
                    out,output_t = self.gui_items[name]
                    if output_t == 'ttk.Combobox':
                        out.delete(0,END)  
                        out['value']=[t[i] for t in datas]
                        out.current(0)
                        out.event_generate("<<ComboboxSelected>>")
                    elif output_t == 'Entry':
                        out.config(state='normal')
                        out.delete(0,END)  
                        out.insert(0,datas[0][i]) 
                        if 'unmodifiable_output' in kwds and \
                            name in kwds['unmodifiable_output']:
                            out.config(state='disabled')
            
            #log输出
            if 'outlog' in kwds['output']:
                out,output_t = self.gui_items['outlog']
                self.log(out,datas,data_name)
        #没有数据也要清空内容
        else:
            for name in kwds['output']:
                out,output_t = self.gui_items[name]
                if output_t == 'ttk.Combobox':
                    out['value']=['']
                    out.current(0)
                    out.event_generate("<<ComboboxSelected>>")
                    out['value']=[]
                    
                elif output_t == 'Entry':
                    out.config(state='normal')
                    out.delete(0,END)  
                    # out.config(state='disabled')  
    
    
    #按照数据生成控件
    def revisable_data(self,**kwds):
        logging.debug(kwds)
        
        if(self.gui_items == 0):
            raise ValueError(f"gui_items不存在")
        
        form = {}
        datas,data_name = self.db.operateDbByJson(kwds['cmd'],form) 
        # logging.debug(data_name)
        start_row = 2
        #每个控件宽
        items_width = [10,10,10,50,50,10,20,10]
        if(len(datas)):
            #表头
            for i,item in enumerate(data_name):
                tk.Label(self.root,
                         width=items_width[i],
                         text=my_utils.change_name_by_map(my_utils.remove_prefix(item),
                         self.config['Private']['key_map']))\
                    .grid(row=start_row,column=i)
            
            row_list=[]    
            tk.Button(self.root,text='保存修改', command= partial(self.save_updated_data,
                                                    row_list,
                                                    datas,
                                                    data_name)).grid(column=len(data_name),row=start_row-1)    
            
            #创建列表显示数据，并把控件语柄保存
            for data in datas:
                row_dict={}
                start_row +=1
                data = dict(zip(my_utils.remove_prefix(data_name),data))
                for i,item in enumerate(data_name):
                    if('.') in item:
                        table, name = item.rsplit('.', 1)
                    else:
                        table, name = '',item
                    
                    if table == 'Projects'  or name == 'report_id' or name == 'description':
                        row_dict[name]=tk.Label(self.root,bg='white',width=items_width[i],relief=GROOVE)
                        row_dict[name].configure(text=data[name])
                        row_dict[name].configure(state="disabled")
                        row_dict[name].grid(padx=2) 
                    else:
                        row_dict[name]=tk.Entry(self.root,width=items_width[i],relief=GROOVE)
                        row_dict[name].grid(padx=2)
                        row_dict[name].insert(END,data[name])
                        
                    
                    row_dict[name].grid(column=i,row=start_row)
                    
                ck = IntVar()
                Radiobutton(self.root, text="关闭", variable=ck, value=1).grid(column=i+1,row=start_row,sticky='e')  
                # Radiobutton(self.root, text="静默关闭", variable=ck, value=2).grid(column=i+2,row=start_row,sticky='e')
                # Radiobutton(self.root, text="不关闭", variable=ck, value=0).grid(column=i+3,row=start_row,sticky='e')
                
                #关闭    
                row_dict['close?'] = ck
                row_list.append(row_dict)

        else:
            msgbox.showinfo(title="操作提示",message='真干净')  
            #关闭当前窗口
            # self.root.destroy()

    def save_updated_data(self,row_list,datas,data_names):
        if len(row_list):       
            for row,data in zip(row_list,datas):
                update = 0
                data = dict(zip(my_utils.remove_prefix(data_names),data))
                form = {}
                form['report_id'] = data['report_id']
                for d_name in data_names:
                    table, name = d_name.rsplit('.', 1)
                    #如果是不可更改字段，跳过
                    if table == "Projects" or name == 'report_id' or name == 'description':
                        continue
                    
                    form[name]=row[name].get()
                    #如果原本数据更改了，提交更新
                    if(data[name] != row[name].get()):
                        update = 1
                    
                if update:
                    self.db.operateDbByJson('updateReportInfoById',form)
                if row['close?'].get() == 1:
                    sub_form = {}
                    sub_form['state'] = 'Close'
                    sub_form['report_id']  = form['report_id']  
                    self.db.operateDbByJson('closeReportById',sub_form) 
                
            
            msgbox.showinfo(title="操作提示",message='操作完成') 
            #关闭当前窗口
            # self.root.destroy()
                         
                   
               
            # logging.debug(datas)  
            # msgbox.showinfo(title="操作提示",message=hint)  
            # logging.debug(row_list)  
        else:
            msgbox.showinfo(title="操作提示",message='无数据更新')

             
    #导出报告到Excel        
    def export_to_excel(self,**kwds):
        # 加载文件
        xfile = openpyxl.load_workbook(self.config['Private']['excel_file']['file_path'])
        # 选定文件表
        xsheet = xfile.active
        #从后面添加
        max_row = xsheet.max_row
        # print(max_row)
        xsheet["A{0}".format(max_row+2)] = "第{0}周".format(time.strftime("%W",time.localtime()))
         
        outlog = self.gui_items[kwds['output'][0]][0]
        
        info,data_name = self.db.operateDbByJson(kwds['cmd']) 
        key_name = my_utils.remove_prefix(data_name)
            
        # logging.debug(info)
        # data_p = dict(zip(key_name,info[0]))
        # for data in info:
        #     for d in zip(data_name,info):
        #             outlog.insert(END,str(d[0]) + ":" + str(d[1]) + "\n") 
                        
        #根据报告格式转换并加到列表中
        s_error=False
        for d in info:
            data = dict(zip(key_name,d))
            row_date=[]
            for i in self.config['Private']['excel_file']['form']:
                if i not in data:
                    raise ValueError(f"{i}值没有获取，可能指令错误")
                    break
                if i == "start":
                    if(data[i]):
                        row_date.append(data[i].strftime("%Y/%m/%d"))
                    else:
                        raise ValueError(f"没有开始时间")
                elif i == 'close':
                    if(data[i]):
                        row_date.append(data[i].strftime("%Y/%m/%d"))
                        t = int((round(my_utils.calculate_work_hours(data["start"],data['close']),1)+0.4)/0.5)*0.5 + data["OT"]
                    else:
                        row_date.append(' ')
                        t = int((round(my_utils.calculate_work_hours(data["start"],datetime.now()),1)+0.4)/0.5)*0.5 + data["OT"]
                    #工时
                    row_date.append(t)
                        
                else:
                    row_date.append(data[i])

            #备注
            # row_date.append(' ')
            #报告时间
            row_date.append(time.strftime("%Y/%m/%d",time.localtime()))
            #PDT
            pdt,_ = self.db.operateDbByJson('readReadPDTByChip',data)
            row_date.append(pdt[0][0])
            
            try:
                #将列表添加到Excel中
                xsheet.append(row_date)
            except:
                outlog.insert(END,"导出失败")
                s_error=True
            else:
                print("导出成功")
                
        if(s_error == False):
            outlog.insert(END,"导出成功")

        # 保存文件
        xfile.save(self.config['Private']['excel_file']['file_path'])       
      
    def log(self,outlog,datas,data_name,group=0):
        outlog.delete(1.0,END)  
        count = 0
        all_count = 0
             
        if not datas:
            outlog.insert(END, data_name)
        else: 
            if group != 0:
                last_item = ''
                no_group_name = [x for x in data_name if x != group]
                for data in datas:  
                    d = dict(zip(data_name,data))
                    if d[group] !=  last_item:
                        if last_item != '':
                            outlog.insert(END,f"\n 小计: {count}\n\n")
                        last_item = d[group]
                        outlog.insert(END,str(d[group]) + ":"  + "\n") 
                        count = 0
                    for n in no_group_name:    
                        outlog.insert(END,str(d[n]) + ", ") 
                    
                    count +=1
                    all_count +=1
                    
                outlog.insert(END,f"\n 小计: {count}\n")
                outlog.insert(END,f"\n\n\n总数: {all_count}\n\n") 
            else:
                data_name = my_utils.change_name_by_map(data_name,
                                                        self.config['Private']['key_map'])
                for data in datas:  
                    d = dict(zip(data_name,data))
                    for n in data_name:    
                        outlog.insert(END,n + ":" + str(d[n]) + "\n")       
                    outlog.insert(END,"\n\n")  
                
            
    def out_log(self,**kwds):
        logging.debug(kwds)
        
        if(self.gui_items == 0):
            raise ValueError(f"gui_items不存在")
        
        form = {}
        
        for i in kwds['input']:
            form[i] = self.gui_items[i][0].get()
        logging.debug(form)    
        outlog = self.gui_items['outlog'][0]
        
        
        datas,data_name = self.db.operateDbByJson(kwds['cmd'],form) 
        logging.debug(datas)   
        data_name = my_utils.remove_prefix(data_name)
        # logging.debug(data_name)  
        
        g = 0
        if "output_group" in kwds:
            g = kwds["output_group" ]
        self.log(outlog,datas,data_name,g)
        
        #刷新所以其他控件
        for k,v in self.gui_items.items():
            if k != 'outlog' and 'init_f' not in k :
                # if v[1] == 'ttk.Combobox':
                #     v[0].current(0)
                #     v[0].event_generate("<<ComboboxSelected>>")    
                if v[1] == 'Entry':
                    v[0].delete(0,END)  
        
        #通过联动控件更新            
        if 'refresh_entry' in kwds and kwds['refresh_entry'] in self.gui_items:
            r,r_t = self.gui_items[kwds['refresh_entry']]
            
            # 如果有初始化函数，通过初始化函数更新
            if kwds['refresh_entry']+'init_f' in self.gui_items: 
                h_p = self.gui_items[kwds['refresh_entry']+'init_f']
                r['value']=self.change_to_single_list(self.exter_db_get(**h_p['param']),0)
                r.current(0)
            if r_t == 'ttk.Combobox':
                # v[0].current(0)
                r.event_generate("<<ComboboxSelected>>")   
                
        
        
        
         



