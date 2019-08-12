#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/8/9 10:39
# @File    : Wzq.py

import re
import io
import pandas as pd

from utility import lines_2_df


class Wzq(object):
    def __init__(self, content):
        lst_factor = re.split(r'={2,}', content)
        self.shear_adjust_factor = pd.read_csv(io.StringIO(lst_factor[-1]), sep=r'\s+')

        lst_content = re.split(r'\s+\*{2,}', lst_factor[0])

        lst_period = re.split(r'\n\n', lst_content[2])
        self.period_data_diaphragm = None
        self.period_data = None
        for index, item in enumerate(lst_content):
            if item.find('扭转系数(Z)(强制刚性楼板模型)') > 0:
                self.period_data_diaphragm = lines_2_df(lst_period[index]+'\n'+lst_period[index+1])
            elif item.find('扭转系数(Z)') > 0 > item.find('(强制刚性楼板模型)'):
                self.period_data = lines_2_df(lst_period[index])

        if self.period_data_diaphragm is None:
            self.period = self.period_data
        else:
            self.period = self.period_data_diaphragm

        self.s_s_c = ['X方向剪重比', 'Y方向剪重比']
        _pos = [3, 4]

        for name, pos in zip(self.s_s_c, _pos):
            _ = re.split(r'-{2,}', lst_content[pos])[-1]
            _ = re.split(r'\n\n', _)[0]
            setattr(self, name, parentheses_df(_))


def parentheses_df(content):
    content = content.replace('%', '')
    content = content.replace('(kN)', '')
    content = content.replace('(kN-m)', '')
    content = content.replace('(', ' ')
    content = content.replace(')', '')
    return pd.read_csv(io.StringIO(content), sep=r'\s+')
