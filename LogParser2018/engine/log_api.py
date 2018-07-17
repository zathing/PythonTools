#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from util import unzip_file, zip_file
from test_template import template_tester
from upload_app.models import FileSimpleModel

def deal_log(log_file):
    # log_file : upload/20180716/SUPPTOOL_LOG_20180507181756897.7z
    log_path = unzip_file(log_file)
    tester = template_tester()
    tester.log2html(log_path)
    tester.test(log_path)
    # report_file : ./report/20180717/SUPPTOOL_LOG_20180509003843892/*  # ./.../* 的格式是为了保证压缩时只压缩文件，不压缩目录
    report_files = './report/' + log_file.split('/')[-2] + '/' + os.path.splitext(os.path.basename(log_file))[0] + '/*'
    # download_file : download/20180717/SUPPTOOL_LOG_20180509003843892.7z
    download_file = zip_file(report_files)
    FileSimpleModel.objects.filter(file_field=log_file).update(report_download=download_file)
    # 清理 upload/MMDD 下的 7z 文件以及解压的目录。MMDD会保留，暂时不管它
    os.remove(log_file)
    shutil.rmtree(log_file.split('.')[0])

if __name__ =='__main__':
    deal_log('D:/Django_Project/LogParser2018/upload/20180716/SUPPTOOL_LOG_20180509022319252.7z')