# !/user/bin/env python
# coding:utf-8

def is_event_log(log_type):
    return log_type == 'event'

def is_debug_log(log_type):
    return log_type == 'debug'

def is_install_log(log_type):
    return log_type == 'install'
