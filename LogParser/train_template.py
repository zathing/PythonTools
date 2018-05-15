# !/user/bin/env python
# coding:utf-8

import log_parser
import util
import os
import log_type

import log_parser_install
import log_id_def

import log_parser_msi

import util_db

class template_trainer:
    def __init__(self,log_path_upper,log_type):
        self.log_path_upper = log_path_upper
        self.log_type = log_type

    def train(self):
        pass

    def train_log_id_install_msi(self):
        case_num = 0
        total_content_set = set()
        for sub_dir in util.get_immediate_subdirectories(self.log_path_upper):
            case_num += 1
            print os.linesep*2
            print '*'*20
            print case_num
            log_parser_obj = log_parser_msi.log_parser(os.path.join(os.path.join(self.log_path_upper,sub_dir),'TiInst'))
            content_set,_ = log_parser_obj.parse_log_id()
            total_content_set = total_content_set.union(content_set)
        return total_content_set

    def train_log_id_install(self):
        total_log_id_dict = {}
        total_log_id_ignore_content_dict ={}
        total_log_id_ignore_line_number_dict = {}

        #for approximate
        total_log_id_content_approximate_dict ={}
        total_log_id_ignore_line_num_content_approximate_dict = {}

        case_num = 0
        total_log_id_dict = {}
        
        #critical issue
        #for k in log_id_def.get_log_id_list():
        #    daemon_log_id_dict[k] = {}
        
        for sub_dir in util.get_immediate_subdirectories(self.log_path_upper):
            case_num += 1
            print os.linesep*2
            print '*'*20
            print case_num
            log_parser_obj = log_parser_install.log_parser(os.path.join(os.path.join(self.log_path_upper,sub_dir),'TiInst'))
            log_id_dict = log_parser_obj.parse_log_id()
            for k_o in log_id_dict.keys():
                print k_o
                
                daemon_log_id_dict = {}
                for k in log_id_def.get_log_id_list():
                    daemon_log_id_dict[k] = {}

                inner_dict = log_id_dict[k_o]
                for k_i in inner_dict.keys(): 
                    print k_i,len(log_id_dict[k_o][k_i].items())
                    total_log_id_dict[k_o] = total_log_id_dict.get(k_o,daemon_log_id_dict)
                    total_log_id_dict[k_o][k_i] = dict(total_log_id_dict[k_o][k_i].items() + log_id_dict[k_o][k_i].items())
            log_parser_obj.clean_up()
        return total_log_id_dict

    def train_log_id(self):
        total_log_id_dict = {}
        total_log_id_ignore_content_dict ={}
        total_log_id_ignore_line_number_dict = {}

        #for approximate
        total_log_id_content_approximate_dict ={}
        total_log_id_ignore_line_num_content_approximate_dict = {}


        case_num = 0
        for sub_dir in util.get_immediate_subdirectories(self.log_path_upper):
            case_num += 1
            print os.linesep*2
            print '*'*20
            print case_num

            #if log_type.is_install_log():
            log_parser_obj = log_parser.log_parser(os.path.join(self.log_path_upper,sub_dir),log_type.is_event_log(self.log_type))
            #else:
            #    log_parser_obj = log_parser_install.log_parser(os.path.join(os.path.join(self.log_path_upper,sub_dir),'TiInst'))
            log_id_dict,log_id_ignore_content_dict,log_id_ignore_line_number_dict,log_id_content_approximate,log_id_ignore_line_num_content_approximate = log_parser_obj.parse_log_id()
            
            total_log_id_dict = dict(total_log_id_dict.items() + log_id_dict.items())
            total_log_id_ignore_content_dict = dict(total_log_id_ignore_content_dict.items() + log_id_ignore_content_dict.items())
            total_log_id_ignore_line_number_dict = dict(total_log_id_ignore_line_number_dict.items() + log_id_ignore_line_number_dict.items())

            #for approximate
            total_log_id_content_approximate_dict = dict(total_log_id_content_approximate_dict.items() + log_id_content_approximate.items())
            total_log_id_ignore_line_num_content_approximate_dict = dict(total_log_id_ignore_line_num_content_approximate_dict.items() + log_id_ignore_line_num_content_approximate.items())
            log_parser_obj.clean_up()

        print 'len of total_log_id_dict is ',len(total_log_id_dict)
        print 'len of total_log_id_ignore_content_dict is ',len(total_log_id_ignore_content_dict)
        print 'len of total_log_id_ignore_line_number_dict is ',len(total_log_id_ignore_line_number_dict)
        return total_log_id_dict,total_log_id_ignore_content_dict,total_log_id_ignore_line_number_dict,total_log_id_content_approximate_dict,total_log_id_ignore_line_num_content_approximate_dict



if __name__ == '__main__':

    def train_template_msi(log_type_str='msi'):
        db_client = util_db.db_client('log_parser_ai')
        trainer = template_trainer('/Users/forest_li/workspace/skyAid/Log_Parser_AI/log_sample/Normal-log-extract',log_type_str)
        total_content_set = trainer.train_log_id_install_msi()
        train_c = db_client.get_collection(util_db.get_msi_name())
        for content in total_content_set:
            train_c.insert({'log_key':content})


    def train_template_install(log_type_str):
        db_client = util_db.db_client('log_parser_ai')
        trainer = template_trainer('D:/LogParse/logs/Normal-log-extract',log_type_str)
        result = trainer.train_log_id_install()
        for k_o in result:
            print os.linesep
            #train_c = db_client.get_collection(k_o)
            for k_i in log_id_def.get_log_id_list():
                print 'k_o ',k_o
                print 'k_i ',k_i 
                train_c = db_client.get_collection(db_client.get_joint_name(k_o,k_i))
                for log_k in result[k_o][k_i]:
                    train_c.insert({'log_key':log_k})


    def test_train_template_install(log_type_str):
        trainer = template_trainer('/Users/forest_li/workspace/skyAid/Log_Parser_AI/log_sample/Normal-log-extract',log_type_str)
        result = trainer.train_log_id_install()
        for k_o in result:
            print os.linesep
            #print k_o
            for k_i in log_id_def.get_log_id_list():
                print k_i
                print len(result[k_o][k_i])

        log_parser_obj = log_parser_install.log_parser('/Users/forest_li/workspace/skyAid/Log_Parser_AI/log_sample/Install-Fail-Extract/21113/TiInst')
        result_t = log_parser_obj.parse_log_id()

        for k_o in result:
            #print k_o
            # only print 
            if not k_o in result_t:
                continue
            #if not 'Setup' in k_o and not 'InstallUCWrapper' in k_o:
            #    continue

            for k_i in log_id_def.get_log_id_list():

                if not 'log_id_ignore_content' in k_i:
                    continue

                diff_dict = [(k,result_t[k_o][k_i][k]) for k in result_t[k_o][k_i] if not k in result[k_o][k_i]]

                #sorted diff_dict
                list_content_dict = [c for k,c in diff_dict]
                from operator import itemgetter
                sorted(list_content_dict,key=itemgetter('time'))

                #print os.linesep
                print k_o,k_i
                print 'len of diff_dict:',len(list_content_dict)
                print list_content_dict

        '''
        log_records = [v for (k,v) in dict_diff_ignore_line_num_content_approximate]
        sorted_log_records = util.sort_list_of_dict(log_records,'time')
        for record in sorted_log_records:
            print record
        '''



    def test_train_template(log_type_str):
        is_event_log = log_type.is_event_log(log_type_str)
        #if log_type.is_install_log(log_type_str):
            #log_parser_obj = log_parser('/Users/forest_li/workspace/skyAid/Log_Parser_AI/log_sample/Normal-log-extract/EL Global_Win8.1 x64/TiInst')  
            #trainer =      
        #else:
        log_parser_obj = log_parser.log_parser('/Users/forest_li/workspace/skyAid/Log_Parser_AI/log_sample/Au_fail/da6_pattern_au_fail',is_event_log)
        trainer = template_trainer('/Users/forest_li/workspace/skyAid/Log_Parser_AI/log_sample/Au_Eric',log_type_str)

        
        total_log_id_dict,total_log_id_ignore_content_dict,total_log_id_ignore_line_number_dict,total_log_id_content_approximate_dict,total_log_id_ignore_line_num_content_approximate_dict = trainer.train_log_id()

        #test some case
        #da6_pattern_au_fail  Ti12_Win10_RS3_x86_EN 20847

        log_id_dict,log_id_ignore_content_dict,log_id_ignore_line_number_dict,log_id_content_approximate_dict,log_id_ignore_line_num_content_approximate_dict = log_parser_obj.parse_log_id()

        print os.linesep*2
        diff_dict_ignore_content = [(k,log_id_ignore_content_dict[k]) for k in log_id_ignore_content_dict if not k in total_log_id_ignore_content_dict]
        print 'len of total_log_id_ignore_content_dict',len(total_log_id_ignore_content_dict)
        print 'len of log_id_ignore_content_dict',len(log_id_ignore_content_dict)
        print 'len of diff_dict_ignore_content',len(diff_dict_ignore_content)
        #print diff_dict_ignore_content

        print os.linesep*2
        diff_dict = [(k,log_id_dict[k]) for k in log_id_dict if not k in total_log_id_dict]
        print 'len of total_log_id_dict',len(total_log_id_dict)
        print 'len of log_id_dict',len(log_id_dict)
        print 'len of diff_dict',len(diff_dict)
        #print diff_dict
        
        print os.linesep*2
        diff_dict_ignore_line_number = [(k,log_id_ignore_line_number_dict[k]) for k in log_id_ignore_line_number_dict if not k in total_log_id_ignore_line_number_dict]
        print 'len of total_log_id_ignore_line_number_dict',len(total_log_id_ignore_line_number_dict)
        print 'len of log_id_ignore_line_number_dict',len(log_id_ignore_line_number_dict)
        print 'len of diff_dict_ignore_line_number',len(diff_dict_ignore_line_number)
        #print diff_dict_ignore_line_number

        print os.linesep*2
        dict_diff_content_approximate = [(k,log_id_content_approximate_dict[k]) for k in log_id_content_approximate_dict if not k in total_log_id_content_approximate_dict]
        print 'len of total_log_id_content_approximate_dict',len(total_log_id_content_approximate_dict)
        print 'len of log_id_content_approximate_dict',len(log_id_content_approximate_dict)
        print 'len of dict_diff_content_approximate',len(dict_diff_content_approximate)

        print os.linesep*2
        dict_diff_ignore_line_num_content_approximate = [(k,log_id_ignore_line_num_content_approximate_dict[k]) for k in log_id_ignore_line_num_content_approximate_dict if not k in total_log_id_ignore_line_num_content_approximate_dict]
        print 'len of total_log_id_ignore_line_num_content_approximate_dict',len(total_log_id_ignore_line_num_content_approximate_dict)
        print 'len of log_id_ignore_line_num_content_approximate_dict',len(log_id_ignore_line_num_content_approximate_dict)
        print 'len of dict_diff_ignore_line_num_content_approximate',len(dict_diff_ignore_line_num_content_approximate)
        log_records = [v for (k,v) in dict_diff_ignore_line_num_content_approximate]
        sorted_log_records = util.sort_list_of_dict(log_records,'time')
        for record in sorted_log_records:
            print record

    #log_type_str = 'event'
    #test_train_template(log_type_str)

    #test_train_template_install('install')

    #for install related files
    train_template_install('install')

    #for msi file
    #train_template_msi('msi')

