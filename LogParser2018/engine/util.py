# !/user/bin/env python
# coding:utf-8

import hashlib
import configparser
import pylab
import os
import re
from operator import itemgetter
import chardet

def get_encoding(file):
	with open(file, 'rb') as f:
		return chardet.detect(f.read())['encoding']

def is_end_with_line_num(line_content):
    if re.search(r'\([0-9]*\)$',line_content):
        return True
    else:
        return False

def compress_adjacent_elements(log_id_list):
    '''
    compress the same element which are adjacent
    '''
    pre_log_id = ''
    for log_id in log_id_list:
        if log_id != pre_log_id:
            yield log_id
        pre_log_id = log_id

def get_sha1_str(content):
    return hashlib.sha1(content).hexdigest()

def get_config_handler():
    config = configparser.ConfigParser()
    config.read('cfg/config.ini')
    return config

def plot_line(x,y,file_name='plot.png'):
    plot_dir = 'plot'
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)

    pylab.plot(x,y)
    #pylab.show()
    pylab.savefig(os.path.join(plot_dir,file_name))

def fall_in_certain_period(peroids,timestamp):
    return any([timestamp >= start and timestamp <= end for (start,end,_,_) in peroids])

def fail_in_which_period(peroids,timestamp):
    for (start,end,_,_) in peroids:
        if timestamp >= start and timestamp <= end:
            return True,start,end
    return False,None,None

def get_top_n_records(tuple_list,by_element_index,top_n):
    sorted_tuple_list = sorted(tuple_list,key=lambda x: x[by_element_index])
    sorted_tuple_list.reverse()
    return sorted_tuple_list[:top_n]

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

def remove_line_number_from_location(location):
    line_num = location[location.find('('):location.find(')') + 1]
    return location.replace(line_num,'')

def remove_token(content):
    #remove hex
    replace_with = ' '
    tmp = re.sub(r'0x([0-9a-fA-F]+)',replace_with,content)
    #remove num
    return re.sub(r'([0-9]+)',replace_with,tmp)

def sort_list_of_dict(list_of_dict,by_key_name,bIsReverse=False):
    return sorted(list_of_dict, key=itemgetter(by_key_name), reverse=bIsReverse)

def unzip_file(zip_file):
    exe_file = r'C:/Progra~1/7-Zip/7z.exe'
    # file_name : SUPPTOOL_LOG_20180509003843892.7z
    file_name = zip_file.split('/')[-1]
    # output_path = ../logs\SUPPTOOL_LOG_20180509003843892
    output_path = os.path.join(os.path.split(zip_file)[0], os.path.splitext(file_name)[0])
    cmd = "%s x %s -o%s -r Support_Temp\Log_Windows_Temp\TiInst\*.log -Y" % (exe_file,zip_file, output_path)
    os.system(cmd)
    return os.path.join(output_path, 'Support_Temp', 'Log_Windows_Temp' ,'TiInst')

def zip_file(unzip_file):
    exe_file = r'C:/Progra~1/7-Zip/7z.exe'
    output_path = 'download/' + unzip_file.split('/')[-3] + '/' + unzip_file.split('/')[-2] + '.7z'
    cmd = "%s a %s %s" % (exe_file, output_path, unzip_file)
    os.system(cmd)
    # download_file = download/20180716/SUPPTOOL_LOG_20180509022319252.7z
    return output_path