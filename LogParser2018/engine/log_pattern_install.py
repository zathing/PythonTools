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
    #check if the string starts with time format such as 17/08/2015 21:23:01.272
    if not re.match(r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\.\d{3}', line_content):
        return {}
    #check if the string ends with line number such as - TmWebUIExternalJSObject.cpp(514)
    if not util.is_end_with_line_num(line_content):
        return {}
    line_content = line_content.strip()
    r_pos = line_content.rfind('-')
    if r_pos <= 0:
        # print 'rfind - return <= 0'
        location = ''
    else:
        location = line_content[r_pos + 1:]
        line_content = line_content[0:r_pos]
    line_content_coms = line_content.strip().split(' ')
    result = {'time':'','pid_tid':'','module':'','type':'','content':''}
    #validation len
    if len(line_content_coms) < len(result):
        # print '[len check]{} is invalid log'.format(line_content)
        return {}
    pid_tid_coms = line_content_coms[2].split(':')
    if len(pid_tid_coms) != 2:
        # print '[pid_tid]{} is valid log'.format(line_content)
        return {}
    result = {'time':' '.join([line_content_coms[0],line_content_coms[1]]),'pid':pid_tid_coms[0],'tid':pid_tid_coms[1],'module':line_content_coms[4][1:-1],'type':line_content_coms[3],'content':' '.join(line_content_coms[5:]),'location':location}
    result['log_id'] = util.get_sha1_str((' '.join([result['module'],result['type'],result['content'],result['location']])).encode('utf-8'))
    result['log_id_ignore_content'] = util.get_sha1_str((' '.join([result['module'],result['type'],result['location']])).encode('utf-8'))
    result['log_id_ignore_line_num'] = util.get_sha1_str((' '.join([result['module'],result['type'],result['content'],util.remove_line_number_from_location(result['location'])])).encode('utf-8'))

    #approximate
    result['log_id_content_approximate'] = util.get_sha1_str((' '.join([result['module'],result['type'],util.remove_token(result['content']),result['location']])).encode('utf-8'))
    result['log_id_ignore_line_num_content_approximate'] = util.get_sha1_str((' '.join([result['module'],result['type'],util.remove_token(result['content']),util.remove_line_number_from_location(result['location'])])).encode('utf-8'))

    # print result
    return result

if __name__ == '__main__':
    line_content = '22/03/2018 14:34:10.542 1930:076c @@@ <TmSystemChecking> *** TmSystemChecking.dll was loaded as process attach. - TmSystemChecking.cpp(57)'
    parse_line(line_content)
