# !/user/bin/env python
# coding:utf-8

import os
import io
from collections import Counter
from log_pattern import parse_line
import log_time
import util

#fd=codecs.open(output_formatter.get_output_file(predict_in_days_arr[x]),'w','gb18030')
class log_parser:
    def __init__(self,log_path,is_event_log=False):
        self.local_debug_log = 'Amsp_LocalDebugLog.log'
        self.event_log = 'Amsp_Event.log'
        self.log_path = log_path
        self.top_n_pid_tid_num = 20
        self.local_debug_log_fd = []
        self.is_event_log = is_event_log
        #init
        self.get_local_debug_file_fd_list()
        self.logging_start_time = self.get_start_log_time_from_debug()

    def parse_process_thread(self):
        #----------------------------------------------------------------
        #scan process and thread
        #----------------------------------------------------------------
        line_num = 0
        pid_set = set()
        pid_tid_dict = dict()
        pid_tid_set = set()
        #with io.open(os.path.join(self.log_path,self.local_debug_log),'r',encoding='utf-16') as fd_debug_log:
        #with open(os.path.join(self.log_path,self.local_debug_log)) as fd_debug_log:
        #with codecs.open(os.path.join(self.log_path,self.local_debug_log),'r','ascii') as fd_debug_log:
        for fd_debug_log in self.local_debug_log_fd: 
            fd_debug_log.seek(os.SEEK_SET)
            for line in  fd_debug_log:
                line_num += 1
                print(line_num)
                line = line.encode('utf-8')
                #print chardet.detect(line)['encoding']
                log_parse_result = parse_line(line)
                if len(log_parse_result) == 0:
                    continue
                #print os.linesep
                print('pid:')
                print(log_parse_result['pid'])
                print('tid:')
                print(log_parse_result['tid'])
                pid_set.add(log_parse_result['pid'])
                pid_tid_key = ':'.join([log_parse_result['pid'],log_parse_result['tid']])
                pid_tid_set.add(pid_tid_key)
                pid_tid_dict[pid_tid_key] = pid_tid_dict.get(pid_tid_key,0) + 1
            print('pid_set size is {}'.format(len(pid_set)))
            print('pid_tid_set size is {}'.format(len(pid_tid_set)))
            #sorted_x = sorted(pid_tid_dict.items(), key=operator.itemgetter(0))
            sorted_x = sorted(pid_tid_dict.items(), key=lambda x: x[1])
            sorted_x.reverse()
            for k,v in sorted_x:
                print(k,v)
            top_n_pid_tid_dict = dict(sorted_x[:self.top_n_pid_tid_num])

    def parse_module(self,doc_name):
        #----------------------------------------------------------------
        #scan main module
        #----------------------------------------------------------------
        line_num = 0
        top_n_pid_tid_module_dict = {}
        #with io.open(os.path.join(self.log_path,self.local_debug_log),'r',encoding='utf-16') as fd_debug_log:
        #with open(os.path.join(self.log_path,self.local_debug_log)) as fd_debug_log:
        #with codecs.open(os.path.join(self.log_path,self.local_debug_log),'r','ascii') as fd_debug_log:
        for fd_debug_log in self.local_debug_log_fd: 
            fd_debug_log.seek(os.SEEK_SET)
            for line in  fd_debug_log:
                line_num += 1
                print(line_num)
                line = line.encode('utf-8')
                #print chardet.detect(line)['encoding']
                log_parse_result = parse_line(line)
                if len(log_parse_result) == 0:
                    continue
                #print os.linesep
                print('pid:')
                print(log_parse_result['pid'])
                print('tid:')
                print(log_parse_result['tid'])
                pid_tid_key = ':'.join([log_parse_result['pid'],log_parse_result['tid']])
                if pid_tid_key in top_n_pid_tid_dict:
                    top_n_pid_tid_module_dict[pid_tid_key] = top_n_pid_tid_module_dict.get(pid_tid_key,[]) + [log_parse_result['module']]
        for k,v in top_n_pid_tid_module_dict.items():
            print('----------------result for 2nd scan ---------------')
            print('len of module list for pid_tid')
            print(k,len(Counter(v)))
            for k1,v1 in dict(Counter(v)).items():
                print(k, k1,v1)

    def parse_log_id(self):
        '''
        parse log_id and log_id_ignore_content, and log_id_ignore_line_number_dict
        '''
        event_start_log = self.get_start_log_time_from_debug()
        normal_log_id_dict = {}
        normal_log_id_ignore_line_number_dict = {}
        normal_log_id_ignore_content_dict = {}
        #approximate
        normal_log_id_content_approximate_dict = {}
        normal_log_id_ignore_line_num_content_approximate_dict = {}
        line_num = 0
        for fd_debug_log in self.local_debug_log_fd: 
            fd_debug_log.seek(os.SEEK_SET)
            for line in  fd_debug_log:
                line_num += 1
                print(line_num)
                line = line.encode('utf-8')
                #print chardet.detect(line)['encoding']
                log_parse_result = parse_line(line)
                if len(log_parse_result) == 0:
                    continue
                if log_parse_result['time'] < event_start_log:
                    continue
                if not log_parse_result['log_id_ignore_line_num'] in normal_log_id_ignore_line_number_dict:
                    normal_log_id_ignore_line_number_dict[log_parse_result['log_id_ignore_line_num']] = {'module':log_parse_result['module'],'type':log_parse_result['type'],'location':util.remove_line_number_from_location(log_parse_result['location']),'content':log_parse_result['content'],'time':log_parse_result['time']}
                if not log_parse_result['log_id'] in normal_log_id_dict:
                    normal_log_id_dict[log_parse_result['log_id']] = {'module':log_parse_result['module'],'type':log_parse_result['type'],'location':log_parse_result['location'],'content':log_parse_result['content'],'time':log_parse_result['time']}
                if not log_parse_result['log_id_ignore_content'] in normal_log_id_ignore_content_dict:
                    normal_log_id_ignore_content_dict[log_parse_result['log_id_ignore_content']] = {'module':log_parse_result['module'],'type':log_parse_result['type'],'location':log_parse_result['location'],'time':log_parse_result['time']}
                #for approximate
                if not log_parse_result['log_id_content_approximate'] in normal_log_id_content_approximate_dict:
                    normal_log_id_content_approximate_dict[log_parse_result['log_id_content_approximate']] = {'module':log_parse_result['module'],'type':log_parse_result['type'],'content':util.remove_token(log_parse_result['content']),'location':log_parse_result['location'],'time':log_parse_result['time']}
                if not log_parse_result['log_id_ignore_line_num_content_approximate'] in normal_log_id_ignore_line_num_content_approximate_dict:
                    normal_log_id_ignore_line_num_content_approximate_dict[log_parse_result['log_id_ignore_line_num_content_approximate']] = {'module':log_parse_result['module'],'type':log_parse_result['type'],'content':util.remove_token(log_parse_result['content']),'location':util.remove_line_number_from_location(log_parse_result['location']),'time':log_parse_result['time']}
        return normal_log_id_dict,normal_log_id_ignore_content_dict,normal_log_id_ignore_line_number_dict,normal_log_id_content_approximate_dict,normal_log_id_ignore_line_num_content_approximate_dict

    def get_start_log_time_from_debug(self):
        '''
            check Amsp_LocalDebugLog.0.log or Amsp_LocalDebugLog.log to get the start logging time
        '''
        init_debug_log_file = 'Amsp_LocalDebugLog.0.log' if os.path.isfile(os.path.join(self.log_path,'Amsp_LocalDebugLog.0.log')) else 'Amsp_LocalDebugLog.log'
        with io.open(os.path.join(self.log_path,init_debug_log_file),'r',encoding='utf-16') as fd:
            for line in fd:
                line = line.encode('utf-8')
                #print chardet.detect(line)['encoding']
                log_parse_result = parse_line(line)
                if len(log_parse_result) == 0:
                    continue
                return log_time.time_forward(log_parse_result['time'])

    def parse_transaction_event(self):
        '''
        event file contains much less log, so use different method to extract transcation
        '''
        print('[enter]parse_transaction_event')
        line_num = 0
        first_line = True
        time_lognum_dict = {}

        '''
        the format is as below:
        {'time':(start_pid_tid,end_pid_tid)}
        '''
        time_log_pid_tid_dict = {}

        #special_line_start = u'====== Log created, and this module is compiled on '


        #with open(os.path.join(self.log_path,self.local_debug_log)) as fd_debug_log:
        #with io.open(os.path.join(self.log_path,self.local_debug_log),'r',encoding='utf-16') as fd_debug_log:
        for fd_debug_log in self.local_debug_log_fd: 

            #count the '======' number
            fd_debug_log.seek(os.SEEK_SET)
            content = fd_debug_log.read()
            content = content.encode('utf-8')
            #occurrence = content.count(special_line_start)
            #keep_occurrent = min(10,occurrence)
            #occurrence_count = 0

            fd_debug_log.seek(os.SEEK_SET)  
            for line in fd_debug_log:
                #line = line.decode('utf-16').encode('utf-8')
                line = line.encode('utf-8')
                line_num += 1
                print(line_num)

                '''
                if occurrence_count < occurrence - keep_occurrent:
                    #if line.startswith(special_line_start):
                    if special_line_start in line:
                        occurrence_count += 1
                        print 'occurrence_count',occurrence_count
                        print 'occurrence',occurrence
                        print 'keep_occurrent',keep_occurrent
                    continue
                '''

                log_parse_result = parse_line(line)
                if len(log_parse_result) == 0:
                    continue
                log_time_val = log_parse_result['time']
                log_time_val_stripped = log_time.time_strip_misc(log_time_val)

                if log_time_val_stripped < self.logging_start_time:
                    continue

                pt = ':'.join([log_parse_result['pid'],log_parse_result['tid']])

                #for multiple thread case
                #fixme!! note that, for some special lines, there is no location at all!!
                loc = '_'.join([log_parse_result['module'],log_parse_result['type'],log_parse_result['location']])
                (start_pt,end_pt,start_loc,end_loc) = time_log_pid_tid_dict.get(log_time_val_stripped,('','','',''))

                if start_pt == '':
                    start_pt = pt
                    end_pt = pt
                    start_loc = loc
                    end_loc = loc
                else:
                    end_pt = pt
                    end_loc = loc

                time_lognum_dict[log_time_val_stripped] = time_lognum_dict.get(log_time_val_stripped,0) + 1
                time_log_pid_tid_dict[log_time_val_stripped] = (start_pt,end_pt,start_loc,end_loc)

        sorted_time_lognum_dict = sorted(time_lognum_dict.items(), key=lambda x: x[0]) 
        #print sorted_time_lognum_dict
        #util.plot_line([k for k,v in sorted_time_lognum_dict],[v for k,v in sorted_time_lognum_dict])
        print(time_log_pid_tid_dict)
        print('[exit]parse_transaction_event')
        return log_time.extract_duration_event(dict(sorted_time_lognum_dict),time_log_pid_tid_dict)




    def parse_transaction(self):
        #----------------------------------------------------------------
        #scan transcation for duration
        #----------------------------------------------------------------
        line_num = 0
        first_line = True
        time_lognum_dict = {}

        #with open(os.path.join(self.log_path,self.local_debug_log)) as fd_debug_log:
        #with io.open(os.path.join(self.log_path,self.local_debug_log),'r',encoding='utf-16') as fd_debug_log:
        for fd_debug_log in self.local_debug_log_fd:  
            fd_debug_log.seek(os.SEEK_SET)  
            for line in fd_debug_log:
                #line = line.decode('utf-16').encode('utf-8')
                line = line.encode('utf-8')
                line_num += 1
                #print line_num
                log_parse_result = parse_line(line)
                if len(log_parse_result) == 0:
                    continue
                log_time_val = log_parse_result['time']
                log_time_val_stripped = log_time.time_strip_misc(log_time_val)
                time_lognum_dict[log_time_val_stripped] = time_lognum_dict.get(log_time_val_stripped,0) + 1

        sorted_time_lognum_dict = sorted(time_lognum_dict.items(), key=lambda x: x[0]) 
        #print sorted_time_lognum_dict
        util.plot_line([k for k,v in sorted_time_lognum_dict],[v for k,v in sorted_time_lognum_dict])

        return log_time.extract_duration(dict(sorted_time_lognum_dict))

    def parse_transaction_detail(self):
        #----------------------------------------------------------------
        #scan transcation for details about call to pid,tid,module,type, log details
        #----------------------------------------------------------------
        line_num = 0
        if not self.is_event_log:
            event_durations = self.parse_transaction()
        else:
            event_durations = self.parse_transaction_event()

        print('[Enter]parse_transaction_detail')
        print('len of self.local_debug_log_fd is {}'.format(len(self.local_debug_log_fd)))
        transaction_detail = []
        #for event_st
        for fd_debug_log in self.local_debug_log_fd:  
            fd_debug_log.seek(os.SEEK_SET)  
            for line in fd_debug_log:
                #line = line.decode('utf-16').encode('utf-8')
                line = line.encode('utf-8')
                line_num += 1
                print(line_num)
                log_parse_result = parse_line(line)
                if len(log_parse_result) == 0:
                    continue

                if util.fall_in_certain_period(event_durations,log_time.time_strip_misc(log_parse_result['time'])):
                    transaction_detail.append(log_parse_result)

        print('[Exit]parse_transaction_detail')
        return event_durations,transaction_detail


    def get_local_debug_file_fd_list(self):
        if not self.is_event_log:
            max_local_debug_file_num = 10
            for i in range(max_local_debug_file_num):
                file_name = os.path.join(self.log_path,'Amsp_LocalDebugLog.'+str(i)+'.log')
                if os.path.isfile(file_name):
                    self.local_debug_log_fd.append(io.open(file_name,'r',encoding='utf-16'))
                else:
                    #support the number is continous
                    break

            self.local_debug_log_fd.append(io.open(os.path.join(self.log_path,self.local_debug_log),'r',encoding='utf-16'))
            print('len of self.local_debug_log_fd is {}'.format(len(self.local_debug_log_fd)))
        else:
            self.local_debug_log_fd.append(io.open(os.path.join(self.log_path,self.event_log),'r',encoding='utf-16'))

    def close_local_debug_file_fd_list(self):
        for fd in self.local_debug_log_fd:
            fd.close()

    def clean_up(self):
        self.close_local_debug_file_fd_list()

if __name__ == '__main__':
    #parser = log_parser('../log_sample')
    parser = log_parser('/Users/forest_li/workspace/skyAid/Log_Parser_AI/log_sample/AU_Eric/Ti12_Win8.1_x64_EN/',True)

    #parser.parse_process_thread()
    '''
    transactions = parser.parse_transaction()
    print 'transactions is as below:'
    print transactions

    #sorted_transactions_by_log_records = sorted(transactions,key=lambda x: x[2])
    #sorted_transactions_by_log_records.reverse()
    print 'top 3 transactions sorted by log record number'
    #print sorted_transactions_by_log_records[:3]
    print util.get_top_n_records(transactions,2,3)

    print '-'*15
    #sorted_tansactions_by_duration = sorted(transactions,key=lambda x: x[3])
    #sorted_tansactions_by_duration.reverse()
    print 'top 3 transactions sorted by log duration'
    #print sorted_tansactions_by_duration[:3]
    print util.get_top_n_records(transactions,3,3)
    '''

    #test parse_transaction_detail
    '''
    event_durations,transaction_detail = parser.parse_transaction_detail()
    print '*'*20
    print 'len of transcation_detail is {}'.format(len(transaction_detail))
    print '*'*20
    print event_durations
    '''
    transaction = parser.parse_transaction_event()
    print(transaction)
    print(len(transaction))
    parser.clean_up()


