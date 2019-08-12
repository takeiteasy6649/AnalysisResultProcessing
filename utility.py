#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/28 15:53
# @File    : utility.py

import os
import re
import pandas as pd
from tkinter import filedialog


class FilePath(object):

    def __init__(self):

        self.yjk_path = None
        self.etabs_name = None
        self.etabs_path = None
        self.output_path = None

    def get_path(self, openfile=False):

        if openfile is False:
            self.yjk_path = filedialog.askdirectory()
        else:
            self.etabs_name = filedialog.askopenfilename(title="Select file",
                                                         filetypes=(("Excel files", "*.xlsx *.xls"),
                                                                    ("all files", "*.*")
                                                                    )
                                                         )
            self.etabs_path = os.path.split(self.etabs_name)[0]

    def full_name(self, file_name):
        __full_name = os.path.join(self.yjk_path, file_name)
        if os.path.exists(__full_name):
            return __full_name
        else:
            return None

    def result_name(self, file_name):
        return os.path.join(self.yjk_path, file_name)


# 多重替换函数
def multiple_replace(text, dict_rpl):
    rx = re.compile('|'.join(map(re.escape, dict_rpl)))
    def rules(match): return dict_rpl[match.group(0)]
    return rx.sub(rules, text)


def lines_2_df(content: str):

    if isinstance(content, str):
        lst_lines = [x.strip() for x in re.split('\n', content)]
        lst_lst = []
        len_df = 0
        for ct, item in enumerate(lst_lines):
            if ct == 0:
                lst_lst.append(item.split())
                len_df = len(lst_lst[0])
            else:
                _cache = item.split()
                if len(_cache) >= len_df:
                    lst_lst.append(_cache[0:len_df])
        _tmp = pd.DataFrame(lst_lst[1:], columns=lst_lst[0], dtype=float)
        for name in ['层号', '塔号', 'Floor', 'Tower']:
            if name in _tmp.columns:
                _tmp = _tmp.astype({name: int}, errors='ignore')
        return _tmp


def lines_2_dict(content: str):

    if isinstance(content, str):
        lst_lines = [x.strip() for x in re.split('\n', content)]
        lst_info = []
        for __item in lst_lines:
            if __item.find(':') > 0:
                lst_info.extend([x.strip() for x in __item.split(':')])
        return dict(zip(lst_info[::2], lst_info[1::2]))
    else:
        print('类型错误')
