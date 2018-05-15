# !/user/bin/env python
# coding:utf-8

import util_db
import os
import codecs
import glob
import log_time
import log_parser_install
import log2html
import util
from jinja2 import Environment, FileSystemLoader
from StringIO import StringIO

class template_tester():
    def __init__(self):
        self.db = util_db.db_client('log_parser_ai')
        self.pre_train_log_id_dict = {}
        self.load_pre_train()
        self.env = Environment(loader=FileSystemLoader('./templates'))
        self.report_template = self.env.get_template('report.html')
        self.index_template = self.env.get_template('index.html')

    def load_pre_train(self):
        collection_names = self.db.get_collection_names()
        print 'len of collection_names:',len(collection_names)
        for collection_name in collection_names:
            c = self.db.get_collection(collection_name)
            self.pre_train_log_id_dict[collection_name] = c.distinct('log_key')
            print collection_name,len(self.pre_train_log_id_dict[collection_name])

    def generate_web_log_parser_report(self, log_path, html_path, data):
        html = self.report_template.render(source_file = data.get('source_file'), log_contents = data.get('log_contents'))
        html_file = os.path.join(html_path, self.get_case_id(log_path)+'.html')
        with open(html_file, 'w') as f:
            f.write(html.encode('utf-8'))

    def get_log(self, log_path, html_path, line):
        log_line = line.strip().replace('<', '&lt;').replace('>', '&gt;')
        log_key = line.split('<')[1].split('>')[0]
        log_files = glob.glob(r"%s/*%s*.log" % (log_path, log_key))
        for log in log_files:
            html_file = os.path.join(html_path, os.path.basename(log) + '.html')
            with open(log) as fi:
                for li in fi.readlines():
                    if li.strip() == line.strip():
                        line_sha = util.get_sha1_str(line)
                        log_line = line.replace(log_key, '<a href="./%s#%s">%s</a>' % (os.path.basename(html_file), line_sha, log_key), 1)
                        with open(html_file, 'r+') as fo:
                            s = fo.read()
                            fo.seek(0, 0)
                            fo.write(s.replace('<div>%s</div>' % (li.strip().replace('<', '&lt;').replace('>', '&gt;')), '<div id="%s" style="color:#F00">%s</div>' % (line_sha, li.strip().replace('<', '&lt;').replace('>', '&gt;'))))
        return log_line

    def get_case_id(self,log_path):
        return log_path.split('/')[-2]

    def get_norm_time(self,time_str):
        # print 'get_norm_time',time_str
        # ValueError: time data '\xef\xbb\xbf14/10/2013 15:49:51' does not match format '%d/%m/%Y %H:%M:%S'
        if time_str.startswith('\xef\xbb\xbf'):
            time_str = time_str.replace('\xef\xbb\xbf','')
        return log_time.time_format_install(log_time.time_strip_misc(time_str))

    def test(self,log_path):
        log_parser_obj_1 = log_parser_install.log_parser(log_path)
        result_t = log_parser_obj_1.parse_log_id()
        case_id = self.get_case_id(log_path)
        total_list_content_dict = []
        # os.path.pardir 表示上一层目录
        # 在 log_path 的上一层目录创建 report 目录
        report_path = os.path.join(os.path.join(log_path, os.path.pardir), 'report')
        if not os.path.exists(report_path):
            os.makedirs(report_path)
        html_path = os.path.join(os.path.join(log_path, os.path.pardir), 'html')
        with codecs.open(os.path.join(report_path,case_id),'w') as fd:
            for k_o in result_t:
                #filter out TMSTOOL
                if 'TMSTOOL' in k_o:
                    continue
                diff_dict = {}
                for k_i in result_t[k_o]:
                    joint_key = self.db.get_joint_name(k_o,k_i)
                    #fixme!!! for test, only focus on _ignore_content
                    if not 'log_id_ignore_content' in joint_key:
                        continue
                    if not joint_key in self.pre_train_log_id_dict:
                        print '{} not exists!'.format(joint_key)
                        continue
                    diff_dict = [(k,result_t[k_o][k_i][k]) for k in result_t[k_o][k_i] if not k in self.pre_train_log_id_dict[self.db.get_joint_name(k_o,k_i)]]
                    #sorted diff_dict
                    list_content_dict = [c for k,c in diff_dict]
                    total_list_content_dict += list_content_dict
                    #sorted_list_content_dict = sorted(list_content_dict,key=itemgetter('time'))
                    #refer to https://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-values-of-the-dictionary-in-python
                    sorted_list_content_dict = sorted(list_content_dict,key=lambda k:self.get_norm_time(k['time']))##get_norm_time
                    fd.write('*'*20 + '\n')
                    fd.write(k_o + '\n')
                    fd.write('*'*20 + '\n')
                    fd.write('len of sorted_list_content_dict:{}'.format(len(sorted_list_content_dict)) + '\n')
                    count = 0
                    for item in sorted_list_content_dict:
                        count += 1
                        fd.write(item['line'] + '\n')
                        # fd.write(os.linesep)
                    fd.write('\n')
        log_contents = StringIO()
        sorted_total_list_content_dict = sorted(total_list_content_dict,key=lambda k:self.get_norm_time(k['time']))
        with codecs.open(os.path.join(report_path,case_id+'_mix'),'w') as fd:#,encoding='utf8'
            for item in sorted_total_list_content_dict:
                fd.write(item['line'] + '\n')
                # log_contents.write(self.get_log(item['line'])item['line'].replace('<', '&lt;').replace('>', '&gt;') + '<br>')
                log_contents.write(self.get_log(log_path, html_path, item['line']) + '<br>')
        data = {'source_file':case_id, 'log_contents':log_contents.getvalue().decode('utf-8')}
        log_contents.close()
        self.generate_web_log_parser_report(log_path, html_path, data)

if __name__ == '__main__':
    log_path = 'D:/LogParse/logs/Install-Fail-Extract/23660/TiInst'
    log2html.log2html(log_path)
    tester = template_tester()
    tester.test(log_path)
    # tester.test('D:\\LogParse\\logs\\Install-Fail-Extract\\16101\\TiInst')