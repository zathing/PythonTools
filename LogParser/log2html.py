#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

def log2html(log_path):
    html_path = os.path.join(os.path.join(log_path, os.path.pardir), 'html')
    if not os.path.exists(html_path):
        os.makedirs(html_path)
    for file in os.listdir(log_path):
        html_file = os.path.join(html_path, file + '.html')
        with open(html_file, 'wb') as fo:
            fo.write('<h5>%s</h5><hr /><pre>' % file)
            with open(os.path.join(log_path, file)) as fi:
                for li in fi.readlines():
                    fo.write('<div>%s</div>' % li.strip().replace('<', '&lt;').replace('>', '&gt;'))
            fo.write('</pre>')

if __name__ == '__main__':
    log_path = 'D:/LogParse/logs/Install-Fail-Extract/16101/TiInst'
    log2html(log_path)