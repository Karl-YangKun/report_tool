import my_utils
import logging
from tkinter import *
from functools import partial

class Panel:
    def __init__(self, root, proc, config, options):
        self.config = config
        self.proc = proc
        self.options = options
        self.items={}
        self.root = root
        self.root.title(self.config['Window']['title'])
        self.root.geometry(f"{self.config['Window']['width']}x{self.config['Window']['height']}")
        # self.root.configure(bg=self.config['GUI']['Window']['bg_color'])
        self.sequence = self.config['Window']['sequence']
        self.create_widgets()
    
    def get_Processor(self):
        return self.proc
    
    def recreate_widgets(self):
        # 遍历window的直接子控件，并逐一销毁
        for widget in self.root.winfo_children():
            widget.destroy()
        self.items.clear()
        self.create_widgets()
        
    def create_widgets(self): 
        #读取json配置部署控件
        for i,row in enumerate(self.config['Widgets']):
            #是否顺序排列
            r=row["row"]
            if self.sequence:
               r = i+1
               
            for col in row['items']:
                #获取控价类型并对应调用tk的函数进行初始化
                func = my_utils.get_function_by_name("tkinter."+col['type'],self)
                
                #判断是否有属性，并将应用属性到控件上
                if('attr' in col): 
                    item = func(self.root,**col["attr"])
                    #如果是预设列表，立刻初始化
                    if 'values' in col["attr"] and col["attr"]["values"] in self.options:
                        item['value'] = self.options[col["attr"]["values"]]
                        item.current(0)
                        logging.debug(item['value'])
                else:
                    item = func(self.root) 
                      
                item.grid(row = r,**col["place"])
                
                if 'text' in col:
                    item.configure(text=col['text'])
                    
                #用初始化函数除了控件.TODO 只能给values？
                if 'init_func' in col: 
                    h_p = col['init_func']
                    f = my_utils.get_function_by_name(h_p['f'],self)
                    item['value']=self.proc.change_to_single_list(f(**h_p['param']),0)
                    item.current(0)
                    self.items[col['uid']+"init_f"]=h_p
                    
                    
                #绑定相应处理函数
                if 'function' in col: 
                    f = my_utils.get_function_by_name(col['function']['f'],self)
                    f_p = col['function']['params']
                    if 'handler' in col['function']:
                        h = my_utils.get_function_by_name(col['function']['handler'],self)
                        
                    if(col['type'] == 'Button'):
                        item.configure(command=partial(f,
                                                **f_p))
                    elif(col['type'] == 'ttk.Combobox'):
                        try:
                            item.bind("<<ComboboxSelected>>",f(fun=h,
                                                            **f_p))
                        except NameError:
                            item.bind("<<ComboboxSelected>>",f)
                    elif col['type'] == 'Label':
                        item.bind("<<Property>>",f(fun=h,
                                                **f_p))
                    
                    
                #记录输入型控件，以便后续使用    
                if 'uid' in col:    
                    self.items[col['uid']]=(item,col['type'])
                if "alias" in col:
                    self.items[col['alias']]=(item,col['type'])
             
