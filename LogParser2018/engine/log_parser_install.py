# !/user/bin/env python
# coding:utf-8

import os
import log_pattern_install
import util
import log_id_def

class log_parser:
    def __init__(self,log_path):
        self.install_log_prefix = ['_Trend_Vizor_VizorHtmlDialog','_Trend_Vizor_Setup','_Trend_Vizor_TmSettingCombine','_Trend_Vizor_InstallUCWrapper_dll','_Trend_Vizor_msi','_Trend_Vizor_ShortCut','_Trend_Vizor_TmSetAcl','_Trend_Vizor_TmIncompDB','_Trend_Vizor_TmSystemChecking']
        self.install_log_prefix_excluded = ['_Trend_Vizor_VC','_Trend_Vizor','_AMSP_INST','Amsp','EzInstallEzIns','EzInstallTiPreAU']
        self.log_path = log_path
        self.top_n_pid_tid_num = 20
        self.log_fd_dict = {}
        #init
        self.get_file_fd_list()
        #self.logging_start_time = self.get_start_log_time_from_debug()
        self.log_id_dict = {}

    def parse_log_id_seq(self):
        key_list = log_id_def.get_log_id_list()
        for file_name_prefix in self.log_fd_dict:
            print(file_name_prefix)
            if file_name_prefix in self.install_log_prefix_excluded:
                continue
            log_id = self.log_fd_dict[file_name_prefix]
            r_1,r_2,r_3,r_4,r_5 = self.parse_log_id_impl_seq(log_id,file_name_prefix)
            self.log_id_dict[file_name_prefix] = dict(zip(key_list,[r_1,r_2,r_3,r_4,r_5]))
        return self.log_id_dict

    def parse_log_id_impl_seq(self,fd_debug_log,file_name_prefix):
        normal_log_id_list = []
        normal_log_id_ignore_line_number_list = []
        normal_log_id_ignore_content_list = []
        #approximate
        normal_log_id_content_approximate_list = []
        normal_log_id_ignore_line_num_content_approximate_list = []
        line_num = 0
        fd_debug_log.seek(os.SEEK_SET)
        for line in  fd_debug_log:
            line_num += 1
            print(line_num,file_name_prefix)
            # line = line.encode('utf-8')
            log_parse_result = log_pattern_install.parse_line(line)
            if len(log_parse_result) == 0:
                continue
            normal_log_id_ignore_line_number_list.append(log_parse_result['log_id_ignore_line_num'])
            normal_log_id_list.append(log_parse_result['log_id'])
            normal_log_id_ignore_content_list.append(log_parse_result['log_id_ignore_content'])
            normal_log_id_content_approximate_list.append(log_parse_result['log_id_content_approximate'])
            normal_log_id_ignore_line_num_content_approximate_list.append(log_parse_result['log_id_ignore_line_num_content_approximate'])
        return normal_log_id_list,normal_log_id_ignore_content_list,normal_log_id_ignore_line_number_list,normal_log_id_content_approximate_list,normal_log_id_ignore_line_num_content_approximate_list

    def parse_log_id(self):
        key_list = log_id_def.get_log_id_list()
        for file_name_prefix in self.log_fd_dict:
            # print file_name_prefix
            if file_name_prefix in self.install_log_prefix_excluded:
                continue
            log_id = self.log_fd_dict[file_name_prefix]
            r_1,r_2,r_3,r_4,r_5 = self.parse_log_id_impl(log_id,file_name_prefix)
            self.log_id_dict[file_name_prefix] = dict(zip(key_list,[r_1,r_2,r_3,r_4,r_5]))
        return self.log_id_dict

    def parse_log_id_impl(self,fd_debug_log,file_name_prefix):
        '''
        parse log_id and log_id_ignore_content, and log_id_ignore_line_number_dict
        '''
        #event_start_log = self.get_start_log_time_from_debug()
        normal_log_id_dict = {}
        normal_log_id_ignore_line_number_dict = {}
        normal_log_id_ignore_content_dict = {}
        #approximate
        normal_log_id_content_approximate_dict = {}
        normal_log_id_ignore_line_num_content_approximate_dict = {}
        line_num = 0
        # fd_debug_log.seek(os.SEEK_SET)
        for line in fd_debug_log.readlines():
            line_num += 1
            line = line.decode('utf-8')
            log_parse_result = log_pattern_install.parse_line(line.strip())
            if len(log_parse_result) == 0:
                continue
            if not log_parse_result['log_id_ignore_line_num'] in normal_log_id_ignore_line_number_dict:
                normal_log_id_ignore_line_number_dict[log_parse_result['log_id_ignore_line_num']] = {'module':log_parse_result['module'],'type':log_parse_result['type'],'location':util.remove_line_number_from_location(log_parse_result['location']),'content':log_parse_result['content'],'time':log_parse_result['time']}
            if not log_parse_result['log_id'] in normal_log_id_dict:
                normal_log_id_dict[log_parse_result['log_id']] = {'module':log_parse_result['module'],'type':log_parse_result['type'],'location':log_parse_result['location'],'content':log_parse_result['content'],'time':log_parse_result['time']}
            if not log_parse_result['log_id_ignore_content'] in normal_log_id_ignore_content_dict:
                normal_log_id_ignore_content_dict[log_parse_result['log_id_ignore_content']] = {'module':log_parse_result['module'],'type':log_parse_result['type'],'location':log_parse_result['location'],'time':log_parse_result['time'],'line':line.strip()}
            if not log_parse_result['log_id_content_approximate'] in normal_log_id_content_approximate_dict:
                normal_log_id_content_approximate_dict[log_parse_result['log_id_content_approximate']] = {'module':log_parse_result['module'],'type':log_parse_result['type'],'content':util.remove_token(log_parse_result['content']),'location':log_parse_result['location'],'time':log_parse_result['time']}
            if not log_parse_result['log_id_ignore_line_num_content_approximate'] in normal_log_id_ignore_line_num_content_approximate_dict:
                normal_log_id_ignore_line_num_content_approximate_dict[log_parse_result['log_id_ignore_line_num_content_approximate']] = {'module':log_parse_result['module'],'type':log_parse_result['type'],'content':util.remove_token(log_parse_result['content']),'location':util.remove_line_number_from_location(log_parse_result['location']),'time':log_parse_result['time']}
        fd_debug_log.close()
        return normal_log_id_dict,normal_log_id_ignore_content_dict,normal_log_id_ignore_line_number_dict,normal_log_id_content_approximate_dict,normal_log_id_ignore_line_num_content_approximate_dict

    def get_file_fd_list(self):
        log_files = [f for f in os.listdir(self.log_path) if os.path.isfile(os.path.join(self.log_path,f))]
        for log_file in log_files:
            self.log_fd_dict[self.get_prefix(log_file)] = open(os.path.join(self.log_path, log_file), 'rb')
            # self.log_fd_dict[self.get_prefix(log_file)] = io.open(os.path.join(self.log_path,log_file),'r',encoding='utf-8')

    def get_prefix(self,file_name):
        coms = file_name.split('_')
        prefix = '_'.join(coms[:len(coms)-1])
        return prefix

    def close_file_fd_list(self):
        for fd in self.log_fd_dict.values():
            fd.close()

    def clean_up(self):
        self.close_file_fd_list()

if __name__ == '__main__':
    parser = log_parser('/Users/forest_li/workspace/skyAid/Log_Parser_AI/log_sample/Normal-log-extract/EL Global_Win8.1 x64/TiInst')
    log_id_dict = parser.parse_log_id()
    for k_o in log_id_dict.keys():
        print(os.linesep)
        print(k_o)
        for k_i in log_id_def.get_log_id_list():
            print(k_i)
            print('len: ',len(log_id_dict[k_o][k_i]))
    parser.clean_up()