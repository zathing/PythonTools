import hashlib
import ConfigParser
import pylab
import os
import re
from operator import itemgetter

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
    config = ConfigParser.ConfigParser()
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

if __name__ == '__main__':
	#test fall_in_certain_period
	#print get_immediate_subdirectories('.')
	
	print remove_token('update - write version=3.8.1193 for section=COMPONENT_LIST_1 ,component=0x2 ,ini=C:\Program Files\Trend Micro\UniClient\ComponentList\Common.ini,')
	print remove_line_number_from_location('.\UpdateManagerImpl.cpp(301)')

	print list(compress_adjacent_elements([1,2,3,3,2,1,1,2]))


