# !/user/bin/env python
# coding:utf-8

import os
import glob
from jinja2 import Environment, FileSystemLoader
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from util_db import db_client
from log_time import time_format_install
from log_parser_install import log_parser
from log_pattern_install import parse_line
import util

class template_tester():
    def __init__(self):
        self.db = db_client('log_parser_ai')
        self.pre_train_log_id_dict = {}
        self.load_pre_train()
        self.env = Environment(loader=FileSystemLoader('engine/templates'))
        self.report_template = self.env.get_template('report.html')

    def load_pre_train(self):
        collection_names = self.db.get_collection_names()
        for collection_name in collection_names:
            c = self.db.get_collection(collection_name)
            self.pre_train_log_id_dict[collection_name] = c.distinct('log_key')
            # print collection_name,len(self.pre_train_log_id_dict[collection_name])

    def log2html(self, log_path):
        html_path = os.path.join('report', self.get_case_id(log_path))
        if not os.path.exists(html_path):
            os.makedirs(html_path)
        for file in os.listdir(log_path):
            html_file = os.path.join(html_path, file + '.html')
            # 生成的 html 都使用 utf-8 编码
            with open(html_file, 'w', encoding='utf-8') as fo:
                fo.write('<meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><h5>%s</h5><hr /><pre>' % file)
                # 判断各个 log 的编码
                file_encode = util.get_encoding(os.path.join(log_path, file))
                with open(os.path.join(log_path, file), 'r', encoding=file_encode) as fi:
                    for li in fi.readlines():
                        fo.write('<div>%s</div>' % li.strip().replace('<', '&lt;').replace('>', '&gt;'))
                fo.write('</pre>')

    def generate_web_log_parser_report(self, log_path, html_path, data):
        html = self.report_template.render(source_file = data.get('source_file'), log_contents = data.get('log_contents'))
        html_file = os.path.join(html_path, html_path.split('\\')[-1]+'.html')
        with open(html_file, 'w') as f:
            f.write(html)

    def get_log(self, log_path, html_path, line):
        log_line = line.strip().replace('<', '&lt;').replace('>', '&gt;')
        log_key = line.split('<')[1].split('>')[0]
        log_files = glob.glob(r"%s/*%s*.log" % (log_path, log_key))
        for log in log_files:
            html_file = os.path.join(html_path, os.path.basename(log) + '.html')
            html_encode = util.get_encoding(html_file)
            log_encode = util.get_encoding(log)
            with open(log, encoding=log_encode) as fi:
                for li in fi.readlines():
                    if li.strip() == line.strip():
                        line_sha = util.get_sha1_str(line.encode('utf-8'))
                        log_line = line.replace(log_key, '<a href="./%s#%s">%s</a>' % (os.path.basename(html_file), line_sha, log_key), 1)
                        with open(html_file, 'r+', encoding=html_encode) as fo:
                            s = fo.read()
                            fo.seek(0, 0)
                            fo.write(s.replace('<div>%s</div>' % (li.strip().replace('<', '&lt;').replace('>', '&gt;')), '<div id="%s" style="color:#F00">%s</div>' % (line_sha, li.strip().replace('<', '&lt;').replace('>', '&gt;'))))
        return log_line

    def get_case_id(self,log_path):
        # log_path : upload/20180716\SUPPTOOL_LOG_20180509022319252\Support_Temp\Log_Windows_Temp\TiInst
        log_id = log_path.split('\\')[-5].split('/')[-1] + '\\' + log_path.split('\\')[-4]
        # log_id : 20180716\SUPPTOOL_LOG_20180509022319252
        return log_id

    def get_norm_time(self,time_str):
        if time_str.startswith('\xef\xbb\xbf'):
            time_str = time_str.replace('\xef\xbb\xbf','')
        return time_format_install(time_str)

    def test(self,log_path):
        log_parser_obj_1 = log_parser(log_path)
        result_t = log_parser_obj_1.parse_log_id()
        case_id = self.get_case_id(log_path)
        total_list_content_dict = []
        html_path = os.path.join('report', self.get_case_id(log_path))
        if not os.path.exists(html_path):
            os.makedirs(html_path)
        for k_o in result_t:
            # filter out TMSTOOL
            if 'TMSTOOL' in k_o:
                continue
            diff_dict = {}
            for k_i in result_t[k_o]:
                joint_key = self.db.get_joint_name(k_o, k_i)
                # fixme!!! for test, only focus on _ignore_content
                if not 'log_id_ignore_content' in joint_key:
                    continue
                if not joint_key in self.pre_train_log_id_dict:
                    # print '{} not exists!'.format(joint_key)
                    continue
                joint_name = self.db.get_joint_name(k_o, k_i)
                error_table = joint_name + '_error'
                update_c = self.db.get_collection(error_table)
                diff_dict = []
                for k in result_t[k_o][k_i]:
                    if not k in self.pre_train_log_id_dict[joint_name]:
                        diff_dict.append((k, result_t[k_o][k_i][k]))
                        update_c.update({"log_key":k},{"$inc":{"count":1}},True)
                # diff_dict = [(k, result_t[k_o][k_i][k]) for k in result_t[k_o][k_i] if not k in self.pre_train_log_id_dict[joint_name]]
                # sorted diff_dict
                list_content_dict = [c for k, c in diff_dict]
                total_list_content_dict += list_content_dict
        sorted_total_list_content_dict = sorted(total_list_content_dict,key=lambda k:self.get_norm_time(k['time']))
        log_contents = StringIO()
        for i, item in enumerate(sorted_total_list_content_dict):
            line_parser_result = parse_line(item['line'].strip())
            error_line = line_parser_result['log_id_ignore_content']
            error_key = item['line'].split('<')[1].split('>')[0]
            error_table = '_Trend_Vizor_'+error_key+'_log_id_ignore_content_error'
            query_c = self.db.get_collection(error_table)
            error_count = query_c.find_one({"log_key":error_line})["count"]
            log_contents.write('<mark><span style="width:40px; display:inline-block;">%s</span></mark><button type="button" id="btn%s" onclick="del(this)">Check as Normal Pattern</button><p id="p%s">' % (error_count,i,i) + self.get_log(log_path, html_path, item['line']) + '</p><br>')
        data = {'source_file': case_id, 'log_contents': log_contents.getvalue()}
        log_contents.close()
        self.generate_web_log_parser_report(log_path, html_path, data)

if __name__ == '__main__':
    logs_path = 'D:/LogParse/logs/CTIS/'
    tester = template_tester()
    for dir in os.listdir(logs_path):
        log_path =logs_path + dir + '/Support_Temp/Log_Windows_Temp/TiInst'
        tester.log2html(log_path)
        tester.test(log_path)
        print('Deal with [' + dir + '] Finish.')
    print('Done!')
