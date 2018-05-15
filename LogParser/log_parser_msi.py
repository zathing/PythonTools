# !/user/bin/env python
# coding:utf-8

import io
import os
import re

class log_parser:
    def __init__(self,log_path):
        self.log_path = log_path
        self.log_fd_list = []
        self.get_file_fd_list()

    def parse_log_id(self):
    	'''
    		for msi, only contains pid, tid, time, content
    		for example: MSI (s) (BC:8C) [13:01:12:064]: PROPERTY CHANGE: Deleting
    	'''
        content_seq = []
        content_set = set()

        for fd in self.log_fd_list:
            for line in fd:
                if line.startswith('===') and line.endswith('==='):
                    print 'time seperation:',line
                elif line.startswith('MSI (s)'):
                    print line
                    #result = re.search(r'^MSI \(s\) \([0-9A-F]{2}:[0-9A-F]{2}\) \[[0-9]{2}:[0-9]{2}:[0-9]{2}:[0-9]{3}\]:',line):
                    result = re.search('^MSI \(s\) \([0-9A-F]{2}:[0-9A-F]{2}\) \[[0-9]{2}:[0-9]{2}:[0-9]{2}:[0-9]{3}\]:',line)
                    if result:
                        #process and thread
                        ss = result.group(0) #MSI (s) (BC:8C) [13:01:12:064]
                        pt = ss[ss.rfind('(')+1:ss.rfind(')')]	
                        print pt		
                        pt_coms = pt.split(':')
                        process_id = pt_coms[0]
                        thread_id = pt_coms[1]

                        #time
                        dt = ss[ss.rfind('[')+1:ss.rfind(']')]

                        #content
                        content = line[len(ss)+1:]
                        print process_id
                        print thread_id
                        print dt
                        print content
                        content_seq.append({'time':dt,'content':content})
                        content_set.add(content)
                    else:
                        pass
                else:
                    pass
        print 'len of content_seq is ',len(content_seq)
        print 'len of content_set is ',len(content_set)
        return content_set,content_seq

    def get_file_fd_list(self):
        log_files = [f for f in os.listdir(self.log_path) if os.path.isfile(os.path.join(self.log_path,f))]
        for log_file in log_files:
            if log_file.startswith('_Trend_Vizor_msiexe'):
                self.log_fd_list.append(io.open(os.path.join(self.log_path,log_file),'r',encoding='utf-16-le'))
        #print self.log_fd_dict

    def cleanup(self):
    	for fd in self.log_fd_list:
    		fd.close()


if __name__ == '__main__':
    parser = log_parser('/Users/forest_li/workspace/skyAid/Log_Parser_AI/log_sample/Normal-log-extract/EL Global_Win8.1 x64/TiInst')
    parser.parse_log_id()
    parser.cleanup()

