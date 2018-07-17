# !/user/bin/env python
# coding:utf-8

import re
import util

enter_narrow = '==>'
exit_narrow = '<=='

def is_new_session_begin():
    return False

def is_embraced_by_bracket(field):
    return field[0] == '[' and field[-1] == ']'

def parse_line(line_content):
    line_content_coms = line_content.strip().split(',')
    result = {'time':'','pid_tid':'','module':'','type':'','content':'','location':''}
    #validation len
    if len(line_content_coms) < len(result):
        print('[len check]{} is invalid log'.format(line_content))
        return {}
    #validate fields
    bracket_check_list = line_content_coms[1:4]
    #some record not end with location
    #bracket_check_list.extend([line_content_coms[-1]])
    # #for i in range(len(bracket_check_list)):
    #	print is_embraced_by_bracket(bracket_check_list[i])
    '''
    for i in range(len(bracket_check_list)):
        print bracket_check_list[i]
        print is_embraced_by_bracket(bracket_check_list[i])
    '''
    if not all([is_embraced_by_bracket(field) for field in bracket_check_list]):
        print('[field check]{} is invalid log'.format(line_content))
        return {}
    #pid_tid_coms = line_content_coms[1].split(':')
    pid_tid_coms = re.split('\[|:|\]',line_content_coms[1])
    result = {'time':line_content_coms[0],'pid':pid_tid_coms[1],'tid':pid_tid_coms[2],'module':line_content_coms[3][1:-1],'type':line_content_coms[2][1:-1],'content':','.join(line_content_coms[4:-1]),'location':line_content_coms[-1][1:-1]}
    '''
    the diff between log_id and log_id_ignore_content is the latter lack of content. so collision might occur if there are 2 files with the same name.
    '''
    result['log_id'] = util.get_sha1_str(' '.join([result['module'],result['type'],result['content'],result['location']]))
    result['log_id_ignore_content'] = util.get_sha1_str(' '.join([result['module'],result['type'],result['location']]))
    result['log_id_ignore_line_num'] = util.get_sha1_str(' '.join([result['module'],result['type'],result['content'],util.remove_line_number_from_location(result['location'])]))

    #approximate
    result['log_id_content_approximate'] = util.get_sha1_str(' '.join([result['module'],result['type'],util.remove_token(result['content']),result['location']]))
    result['log_id_ignore_line_num_content_approximate'] = util.get_sha1_str(' '.join([result['module'],result['type'],util.remove_token(result['content']),util.remove_line_number_from_location(result['location'])]))
    '''
    print result['time']
    print result['pid']
    print result['tid']
    print result['module']
    print result['type']
    print result['location']
    print result['content']
    '''
    return result

if __name__ == '__main__':
    line_content = '2012/09/06 11:03:29.891,[05100:01656],[INFO],[utilUIProfie], <== TiXmlProfileParser::TagIcon,[.\UIProfileAPI.cpp(0)]'
    parse_line(line_content)