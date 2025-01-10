import logging
import importlib
import tkinter.ttk

#通过名字获取函数
def get_function_by_name(function_info, ins):
    """
    尝试调用函数。如果function_info是'package.module.function'的形式，则尝试从包中导入并调用该函数。
    如果function_info仅包含函数名（且该函数在当前作用域中定义），则直接调用该函数。
 
    :param function_info: 函数信息，可以是'package.module.function'形式的字符串，或者是仅包含函数名的字符串。
    :param args: 传递给函数的参数。
    :param kwargs: 传递给函数的关键字参数。
    :return: 函数的返回值，如果调用失败则返回None。
    """
    logging.debug(f"Attempting to invoke function: {function_info}")
    
    try:
        # 检查function_info是否包含'.'，以区分是包中的函数还是本地函数
        if '.' in function_info:
            if('self' in function_info ):
                _, instance_func, func_name = function_info.rsplit('.', 2)
                i = getattr(ins, instance_func)()
                func = getattr(i, func_name)
            else:
                # 假设function_info是'package.module.function'的形式
                package_name, func_name = function_info.rsplit('.', 1)
                # 尝试导入包和模块
                package = importlib.import_module(package_name)
                # 从包中获取函数（这里假设函数在模块的顶层定义，而不是在子模块中）
                # 注意：如果函数在子模块中，你需要更精确地指定路径
                func = getattr(package, func_name)
                #判断是否是自己的变量
            
        else:
            # 假设function_info是本地函数的名称
            func = globals().get(function_info)
            if not func:
                # 尝试从locals()中获取（在函数内部调用时可能有用）
                func = locals().get(function_info)
 
        # 检查是否获取到了可调用的函数
        if callable(func):
            # 调用函数并返回结果
            return func
        else:
            logging.error(f"Function '{function_info}' is not callable.")
            return None
    except (ImportError, AttributeError) as e:
        logging.error(f"Error: {e}")
        return None
    
#去表头
def remove_prefix(data):
    if isinstance(data, list):
        key_name = []
        #如果名字还有表名，将表名去掉
        for d in data:
            if '.' in d:
                _, name = d.rsplit('.', 1)
                key_name.append(name)
            else:
                key_name.append(d)
        return key_name
    else:
        if '.' in data:
            _, name = data.rsplit('.', 1)
        else:
            name = data
        return name
    
#名字转换
def change_name_by_map(names,map):
    if isinstance(names, list):
        new_name = []
        #如果名字还有表名，将表名去掉
        for n in names:
            if n in map:
                new_name.append(map[n])
            else:
                new_name.append(n)
        return new_name
    else:
        if names in map:
            return map[names]
        else:
            return names
        
        
        
from datetime import datetime, timedelta

# 判断是否是工作日（周一到周五）
def is_workday(date):
    return date.weekday() < 5  # 周一是0，周二是1，...，周日是6

# 计算给定日期内的工作时间范围与给定时间段的交集
def calculate_work_hours_on_date(start_time, end_time, date):
    work_start = datetime.combine(date, datetime.min.time().replace(hour=9))  # 早上9点
    work_end = datetime.combine(date, datetime.min.time().replace(hour=17))  # 下午5点
    
    # 截取start_time和end_time到当前日期
    start_on_date = max(start_time, work_start)
    end_on_date = min(end_time, work_end)
    
    # 如果start_on_date在end_on_date之后，说明当天没有工作时间
    if start_on_date >= end_on_date:
        return timedelta(0)
    else:
        return end_on_date - start_on_date

# 计算两个时间点之间的工作时长
def calculate_work_hours(start_time, end_time):
    current_date = start_time.date()
    total_work_hours = timedelta(0)
    
    while current_date <= end_time.date():
        if is_workday(current_date):
            work_hours_on_date = calculate_work_hours_on_date(start_time, end_time, current_date)
            total_work_hours += work_hours_on_date
            
            # 更新start_time，以便在下一个循环中处理下一个时间段
            if start_time < datetime.combine(current_date + timedelta(days=1), datetime.min.time()):
                start_time = datetime.combine(current_date + timedelta(days=1), datetime.min.time())
            else:
                # 如果start_time已经超过了当前日期的结束时间，则不需要再处理后续日期
                break
        
        current_date += timedelta(days=1)
    
    return total_work_hours.total_seconds() / 3600  # 返回小时数
