#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tkinter import *
import requests
import tkinter.filedialog
import os, re, gzip, io, threading
from multiprocessing.dummy import Pool as ThreadPool
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

class MyThread(threading.Thread):
    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args
        self.setDaemon(True)
        self.start()
    def run(self):
        self.func(*self.args)

class MainFrame(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.grid(row=0, column=0, sticky="nsew")
        self.createFrame()
        self.pass_num = 0
        self.fail_num = 0

    def funcExtract7ElementFromName(self, strName):
        objMatch1 = re.match(r'^c(.+?)t(.+?)v(.+?)l(.+?)p(.+?)r(.+?)o(.+?)$', strName)
        objMatch2 = re.match(r'^c(.+?)t(.+?)v(.+?)l(.+?)r(.+?)p(.+?)o(.+?)$', strName)
        assert objMatch1 is not None or objMatch2 is not None, u'%s is not a vaild 7 element.'
        if objMatch1:
            c, t, v, l, p, r, o = objMatch1.group(1, 2, 3, 4, 5, 6, 7)
        if objMatch2:
            c, t, v, l, r, p, o = objMatch2.group(1, 2, 3, 4, 5, 6, 7)
        reviseStrName = 'c%st%sv%sl%sp%sr%so%s' % (c, t, v, l, p, r, o)
        return reviseStrName

    def funcGet7Ele(self, url):
        # get 7 element from url like http://iau.activeupdate.trendmicro.com/activeupdate/preopr/17_1700_5.0_4_1_1_21/ctlrpo/c17t1752l1r1p-1o1/5.000.1361_516a2c01-e8fd-4809-bed9-ab70201eb3b3.7z
        dirname, filename = url.split('/')[-2:]
        dirname = '%sv%sl%s' % (dirname.split('l')[0], filename.split('_')[0], dirname.split('l')[1])
        return self.funcExtract7ElementFromName(dirname)

    def iau_get(self, url):
        try:
            with requests.get(url, stream=True) as r:
                resp = r.raw.read()
                # 使用 decode 将 byte 转换成 str，否则会报错 TypeError: cannot use a string pattern on a bytes-like object
                xml = gzip.GzipFile(fileobj=io.BytesIO(resp)).read().decode('utf-8')
                return [x for x in re.findall(r'<url>\s*(.+?)\s*</url>', xml)]
        except:
            self.lfc_field_1_t.insert(END, '访问 %s 时出现网络问题，请检查后重试！\n' % url, 'red')
            self.lfc_field_1_t.update()

    def iau_check(self, component_list, iau_url):
        urls = self.iau_get(iau_url)
        iau_components = []
        for url in urls:
            iau_components.append(self.funcGet7Ele(url))
        for component in component_list:
            if component in iau_components:
                self.lfc_field_1_t.insert(END, '[' + component + ']' + ' on [' + iau_url + ']' + ' ------ Pass\n')
                self.lfc_field_1_t.update()
                self.pass_num += 1
            else:
                self.lfc_field_1_t.insert(END, '[' + component + ']' + ' on [' + iau_url + ']' + ' ------ Fail\n', 'red')
                self.lfc_field_1_t.update()
                self.fail_num += 1

    def check_main(self, xml_file, server):
        # 检查是否选择了文件
        if self.filename == '':
            self.lb.config(text="请先选择 index.xml 文件")
        else:
            self.lfc_field_1_t.insert(END, 'Start [%s]\n' % xml_file, 'blue')
            self.lfc_field_1_t.insert(END, '========================================================================================================================\n')
            self.lfc_field_1_t.update()
            component_num = set()
            url_num = 0
            # 检查 ini 配置文件是否存在
            if os.path.isfile(server):
                tree = ET.ElementTree(file=xml_file)
                iau_url = ''
                # 使用线程池，否则打包后的exe由于IO太高容易异常
                async_pool = ThreadPool(100)
                for product in tree.findall('products'):
                    pid = 'c' + product.attrib['class'] + 't' + product.attrib['type'] + 'v' + product.attrib['ver'] + 'l' + product.attrib['lang'] + 'p' + product.attrib['plat'] + 'r' + product.attrib['region'] + 'o' + product.attrib['oem']
                    p = re.compile(r'%s$' % pid)
                    with open(server, 'r') as f:
                        for line in f.readlines():
                            if re.search(p, line.strip()):
                                iau_url = line.strip()
                                url_num += 1
                                break
                    if iau_url == '':
                        self.lfc_field_1_t.insert(END, '%s 对应的 URL 在 ini 配置文件中未找到，请检查配置！\n' % pid, 'red')
                        self.lfc_field_1_t.update()
                    else:
                        component_list = set()
                        # .//entity 表示搜索当前 products 下的所有 entity
                        for entity in product.findall('.//entity'):
                            component = entity.attrib['name']
                            component_num.add(component)
                            component_list.add(component)
                        async_pool.apply_async(self.iau_check, (component_list, iau_url))
                async_pool.close()
                async_pool.join()
            else:
                self.lfc_field_1_t.insert(END, '未找到 %s 配置文件，请确保该配置文件存放在 exe 同目录下！\n' % server, 'red')
                self.lfc_field_1_t.update()
            self.lfc_field_1_t.insert(END, '========================================================================================================================\n')
            self.lfc_field_1_t.insert(END, 'End [%s]\n' % xml_file, 'blue')
            self.lfc_field_1_t.insert(END, '---- 本次 AU 涉及 % s 个 component，%s 个 product \n' % (len(component_num), url_num), 'blue')
            self.lfc_field_1_t.insert(END, '---- Pass: % s 个 \n' % self.pass_num, 'blue')
            self.lfc_field_1_t.insert(END, '---- Fail: % s 个 \n\n' % self.fail_num, 'blue')
            self.pass_num = 0
            self.fail_num = 0
            self.lfc_field_1_t.update()
            self.lfc_field_1_t.see(END)

    def choose_file(self):
        self.filename = tkinter.filedialog.askopenfilename()
        if self.filename != '':
            if str(self.filename).endswith('.xml'):
                self.lb.config(text = "您选择的文件是：" + self.filename)
                self.clearText()
                self.lfc_field_1_t.update()
            else:
                self.lb.config(text = "文件格式错误，请选择 index.xml 文件")
        else:
            self.lb.config(text = "请先选择 index.xml 文件")

    def createFrame(self):
        self.filename = ''
        label_frame_center = LabelFrame(self)
        label_frame_center.pack(fill="x")
        lfc_field_1 = LabelFrame(label_frame_center)
        lfc_field_1.pack(fill="x")
        self.lb = Label(lfc_field_1, text = '')
        self.lb.pack()
        self.choose_btn = Button(lfc_field_1, text="请先选择 PreOPR 时生成的 index.xml 文件", command=lambda: MyThread(self.choose_file))
        self.choose_btn.pack()
        self.preopr_btn = Button(lfc_field_1, text="开始检查 PreOPR Server", command=lambda: MyThread(self.check_main, self.filename, './preopr.ini'))
        self.preopr_btn.pack()
        self.opr_btn = Button(lfc_field_1, text="开始检查 OPR Server", command=lambda: MyThread(self.check_main, self.filename, './opr.ini'))
        self.opr_btn.pack()
        self.desp_lb = Label(lfc_field_1, fg = 'red', text = '不用紧盯着观察，如果有失败的，会有红色字体提示 Fail')
        self.desp_lb.pack()
        ###文本框与滚动条
        self.lfc_field_1_t_sv = Scrollbar(lfc_field_1, orient=VERTICAL)  # 文本框-竖向滚动条
        self.lfc_field_1_t_sh = Scrollbar(lfc_field_1, orient=HORIZONTAL)  # 文本框-横向滚动条
        self.lfc_field_1_t = Text(lfc_field_1, height=100, yscrollcommand=self.lfc_field_1_t_sv.set, xscrollcommand=self.lfc_field_1_t_sh.set, wrap='none')
        # 设置字体颜色
        self.lfc_field_1_t.tag_config('red', foreground='red')
        self.lfc_field_1_t.tag_config('blue', foreground='blue')
        # 滚动事件
        self.lfc_field_1_t_sv.config(command=self.lfc_field_1_t.yview)
        self.lfc_field_1_t_sh.config(command=self.lfc_field_1_t.xview)
        # 布局
        self.lfc_field_1_t_sv.pack(fill="y", expand=0, side=RIGHT, anchor=N)
        self.lfc_field_1_t_sh.pack(fill="x", expand=0, side=BOTTOM, anchor=N)
        self.lfc_field_1_t.pack(fill="x", expand=1, side=LEFT)
        # 绑定事件
        self.lfc_field_1_t.bind("<Control-Key-a>", self.selectText)
        self.lfc_field_1_t.bind("<Control-Key-A>", self.selectText)

    def center_window(self, root, w=300, h=200):
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def selectText(self, event):
        self.lfc_field_1_t.tag_add(SEL, "1.0", END)
        return 'break'

    # 文本清空
    def clearText(self):
        self.lfc_field_1_t.delete(0.0, END)

def main():
    root = Tk()
    root.title('iAUServer Check Tool')
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main_frame = MainFrame(root)
    main_frame.center_window(root, 1000, 400)
    main_frame.mainloop()

if __name__ == "__main__":
    main()