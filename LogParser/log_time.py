
import time
import util
#import datetime
from datetime import datetime
from datetime import timedelta
format = '%Y/%m/%d %H:%M:%S'
format_install = '%d/%m/%Y %H:%M:%S'#29/12/2017 17:23:28.247
start_time = datetime(2010,1,1)


def time_diff(time_str_1,time_str_2):
    t1 = datetime.strptime(time_str_1,format)
    t2 = datetime.strptime(time_str_2,format)
    td = t2 - t1 if time_str_2 > time_str_1 else t1 - t2
    return int(td.total_seconds()) + 1

def time_strip_misc(time_str):
    time_str_coms = time_str.split('.')
    time_str = time_str_coms[0]
    return time_str

def time_format(time_str):
    return time.strptime(time_str,format) 

def time_format_install(time_str):
    return time.strptime(time_str,format_install)

def time_str2seconds(time_str):
    time_str = time_strip_misc(time_str)
    #print 'len of time_str_coms:{}'.format(len(time_str_coms))
    #print 'len of time_str:{}'.format(len(time_str))
    #time_str = '{}'.format(time_str)
    t = datetime.strptime(time_str,format)
    td = t - start_time

    return int(td.total_seconds())

def time_seconds2str(seconds_int):
    td = timedelta(seconds=seconds_int)
    t = start_time + td
    return t.strftime(format)

def time_forward(time_str,time_seconds=300):
    t = datetime.strptime(time_strip_misc(time_str),format) - timedelta(seconds = time_seconds)
    return t.strftime(format)

def pudding_time_list(time_list):
    time_list = [int(time_item) for time_item in time_list]
    return range(min(time_list),max(time_list)+1)

def pudding_time_num_dict(time_num_dict):
    new_time_num_dict = {}

    #convert str to seconds
    for k in time_num_dict:
        seconds = 0
        try:
            seconds = time_str2seconds(k)
        except:
            continue
        new_time_num_dict[time_str2seconds(k)] = time_num_dict[k]

    #padding
    all_time_list = pudding_time_list(new_time_num_dict.keys())
    for time_item in all_time_list:
        if not time_item in new_time_num_dict:
            new_time_num_dict[time_item] = 0

    #roll back from seconds to str
    for k in new_time_num_dict:
        new_k = time_seconds2str(k)
        if not new_k in  time_num_dict:
            time_num_dict[new_k] = new_time_num_dict[k]

    sorted_time_num_dict = sorted(time_num_dict.items(), key=lambda x: x[0])
    return sorted_time_num_dict

def extract_duration_event(time_num_dict,time_pid_tid_dict):
    print time_pid_tid_dict
    print '[enter]extract_duration_event'
    sorted_time_num_dict = pudding_time_num_dict(time_num_dict)
    config = util.get_config_handler()
    log_num_threshold = int(config.get('time_hotmap','event_log_num_per_second'))
    log_break_interval = int(config.get('time_hotmap','event_log_break_interval'))
    event_record_list = []
    event_start_time = ''
    event_end_time = ''
    is_in_session = False
    is_first_line = True

    last_pid_tid = ''
    total_log_num = 0
    pudding_num = 0
    log_record_num = 0
    duration_seconds = 0
    last_end_time = ''
    last_end_loc = ''

    for k,v in sorted_time_num_dict:
        if is_first_line:
            event_start_time = k
            is_first_line = False

        duration_seconds += 1 

        start_pt,end_pt,start_loc,end_loc = time_pid_tid_dict.get(k,('','','',''))
        #print 'start_pt',start_pt
        #print 'end_pt',end_pt
        if start_pt != '':
            log_record_num += v
            print 'log_record_num',log_record_num
            #print 'start_pt',start_pt
            #print 'end_pt',end_pt

        #if is_in_session:
        if start_pt == '':
            pudding_num += 1
        elif last_pid_tid == start_pt:
            last_pid_tid = end_pt
            last_end_time = k
            last_end_loc = end_loc
            pudding_num = 0
            pass
        #double check the logic here!
        elif last_end_loc == start_loc:
            last_pid_tid = end_pt
            last_end_time = k
            last_end_loc = end_loc
            pudding_num = 0
        else:
            last_pid_tid = end_pt

            if pudding_num > log_break_interval:
                print "the transaction should be finished!"
                is_in_session = False
                event_end_time = k

                event_record_list.append((event_start_time,last_end_time,log_record_num,time_diff(last_end_time,event_start_time)))

                #pudding_num = 0
                total_log_num = 0
                duration_seconds = 0
                
                #log_record_num = 0
                log_record_num = v
                
                last_end_time = ''
                last_pid_tid = ''
                event_start_time = k
                last_end_time = k

            else:
                last_end_time = k 
                last_end_loc = end_loc

            pudding_num = 0

    event_record_list.append((event_start_time,last_end_time,log_record_num,time_diff(last_end_time,event_start_time)))
    print '[exit]extract_duration_event'
    return event_record_list


def extract_duration(time_num_dict):
    sorted_time_num_dict = pudding_time_num_dict(time_num_dict)
    config = util.get_config_handler()
    log_num_threshold = int(config.get('time_hotmap','log_num_per_second'))
    log_break_interval = int(config.get('time_hotmap','log_break_interval'))

    event_record_list = []
    event_start_time = ''
    event_end_time = ''
    is_in_session = False
    less_log_count = 0
    log_record_num = 0
    duration_seconds = 0
    #print '-'*10
    #print sorted_time_num_dict
    print log_num_threshold
    print log_break_interval

    for k,v in sorted_time_num_dict:#.items():
        duration_seconds += 1 
        log_record_num += v
        #print k,v
        if v > log_num_threshold:
            if is_in_session:
                pass
            else:
                is_in_session = True
                event_start_time = k
        else:
            if is_in_session:
                less_log_count += 1
                if less_log_count > log_break_interval:
                    #should be consider the session has finished
                    event_end_time = k
                    event_record_list.append((event_start_time,event_end_time,log_record_num,duration_seconds))

                    #cleanup
                    less_log_count = 0
                    is_in_session = False
                    log_record_num = 0
                    duration_seconds = 0
            else:
                pass

    return event_record_list




if __name__ == '__main__':
    #t1 = time_format("2012/09/06 11:07:31")
    #print t1

    '''
    print time_str2seconds('2012/09/06 11:03:29.123') #output:84625651.0
    print time_str2seconds('2012/09/06 11:08:31')

    print 'time_seconds2str'
    print time_seconds2str(84625651.0)

    time_num_dict = {}
    time_num_dict['2012/09/06 11:03:27'] = 3
    time_num_dict['2012/09/06 11:03:29'] = 5
    time_num_dict['2012/09/06 11:03:32'] = 10
    print pudding_time_num_dict(time_num_dict)
    '''

    print time_forward('2018/03/09 16:02:35.755',70)

    

     

    
