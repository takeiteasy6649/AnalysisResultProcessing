#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/29 9:14
# @File    : Wdisp.py

import re
from utility import multiple_replace
from utility import lines_2_df


class Wdisp(object):

    def __init__(self, content):
        __list_name = [x.replace(' ', '') for x in re.findall(r'=+.*?=+\s+(.*?)\n', content)]
        __list_content = [x.strip()
                          for x in re.split(r'=+.*?=+\s+.*?\n',
                                            multiple_replace(content.strip(),
                                                             {'\n\n': '\n', '1/ ': '', '1/': '', '%': ''}))]

        if len(__list_name) + 1 == len(__list_content):
            __lst = []
            __lst_wind = []
            __lst_spc_lateral = []
            __lst_gravity = []
            __lst_cqc = []
            for __ct, __value in enumerate(__list_name):
                __lst.append(__value)
                if __value.find('风') >= 0:
                    __lst_wind.append(__value)
                elif __value.find('规定水平力') >= 0:
                    __lst_spc_lateral.append(__value)
                elif __value.find('竖向') >= 0:
                    __lst_gravity.append(__value)
                else:
                    __lst_cqc.append(__value)
                __cache = re.sub(r'\n\s{8,}', '', __list_content[__ct + 1])
                setattr(self, __value, lines_2_df(__cache))
            self.displacement = __lst
            self.wind = __lst_wind
            self.gravity = __lst_gravity
            self.spc_lateral = __lst_spc_lateral
            self.cqc = __lst_cqc
