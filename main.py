import json
import tkinter as tk
import logging
import sys
import time
import my_utils
from tkinter import *

from processor import Processor as Proc
from panel import Panel

       
class GUI(Panel):
    def __init__(self, config):
        self.my_root = tk.Tk()
        self.my_proc = Proc(config)
        super().__init__(self.my_root, self.my_proc, config['GUI']['Main'], config['Options'])
        self.my_config = config
        
        self.fixed_info()
    
    def get_myself(self):
        return self
        
    def fixed_info(self):
        #基本内容
        tk.Label(self.my_root, text='报告人：').grid(row=0,column=0)
        self.items['owner']=(tk.Entry(self.my_root,),"Entry")
        self.items['owner'][0].insert(0,self.my_config['Private']['owner'])
        self.items['owner'][0].grid( row=0,column=1,sticky="w")
        self.items['owner'][0].config(state='disabled')
        tk.Label(self.my_root, text=time.strftime("%Y/%m/%d")).grid(
                        row=0,
                        column=2)
        tk.Label(self.my_root, text="Version: "+config['Private']['version']).grid(
                        row=0,
                        column=3)
        
        
    
    def on_child_window_close(self):
        self.recreate_widgets()
        self.fixed_info()
        self.my_proc.set_items(self.items)
        self.my_proc.set_root(self.my_root)
    
    def new_panel(self,**kwds):
        sub_root = Toplevel(self.my_root)
        # sub_root.bind("<Destroy>", self.on_child_window_close)
        sub_root.protocol("WM_DELETE_WINDOW",self.on_child_window_close)
        sub_root.transient(self.my_root)
        sub_panel = Panel(sub_root, self.my_proc, self.my_config['GUI'][kwds['window']], self.my_config['Options'])
        self.my_proc.set_items(sub_panel.items)
        self.my_proc.set_root(sub_root)
        
    
    def run(self):
        self.my_proc.set_items(self.items)
        self.my_proc.set_root(self.my_root)
        self.my_root.mainloop()
        self.my_proc.deinit()

def update_version(version_file):
    try:
        # Read the current version from the file
        with open(version_file, 'r') as file:
            version = file.read().strip()
        
        # Split the version into major and minor parts
        major, minor = map(int, version.split('.'))
        
        # Increment the minor version
        minor += 1
        
        
        # Create the new version string
        new_version = f"{major}.{minor}"
        
        # Write the new version back to the file
        with open(version_file, 'w') as file:
            file.write(new_version)
        
        print(f"Version updated  to {new_version}.")
        return new_version
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
    except ValueError:
        print("Error: The file does not contain a valid integer version number.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
    
    

if __name__ == "__main__":
    
    with open('config.json', encoding='utf-8') as f:
        config = json.load(f)
    
    if config['Private']['log_level'] == 10:  
        config['Private']['version'] = update_version(config['Private']['version'])
    else:
        with open(config['Private']['version'], 'r') as file:
            config['Private']['version'] = file.read().strip()
        
    logging.basicConfig(filename='app.log',level=config['Private']['log_level'],
                    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
    gui = GUI(config)
    gui.run()