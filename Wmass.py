#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/2 16:34
# @File    : Wmass.py

import re
import utility
import pandas as pd
from io import StringIO
from utility import lines_2_df
from utility import lines_2_dict


class Wmass(object):

    def __init__(self, content):

        self._list_content = [x.strip() for x in re.split(r'\s+\*{5,}', content)]

        result_dict = {'设计参数输出': '_design_info_str',
                       '楼层属性': '_floor_info_str',
                       '塔属性': '_tower_info_str',
                       '各层质量、质心坐标，层质量比': '_mass_info_str',
                       '各楼层质量、单位面积质量分布(单位:kg/m**2)': '_mass_density_info_str',
                       '结构整体抗倾覆验算': '_overturn_info_str',
                       '结构整体稳定验算': '_building_stable_info_str',
                       '楼层抗剪承载力验算': '_storey_shear_capacity_info_str',
                       }

        for key, value in result_dict.items():

            try:
                pos = self._list_content.index(key)
                setattr(self, value,
                        self._list_content[pos + 1].strip()
                        )
            except ValueError:
                pass

        self.design_info = lines_2_dict(getattr(self, '_design_info_str'))
        self.floor_info = lines_2_df(getattr(self, '_floor_info_str'))
        self.mass_info = lines_2_df(getattr(self, '_mass_info_str'))

        # self.tower_info = lines_2_df(getattr(self, '_tower_info_str'))

    @property
    def structure_type(self):
        return self.design_info['结构体系']

    @property
    def num_of_basement(self):
        return self.design_info['地下室层数']

    @property
    def embed_floor(self):
        return self.design_info['嵌固端所在层号(层顶嵌固)']

    @property
    def stiffness_detail(self):
        """
        All information in '各层刚心、偏心率、相邻层侧移刚度比等计算信息'
        data type: DataFrame
        :return:
        """
        pos = self._list_content.index('计算时间')
        _str = self._list_content[pos + 3]
        _str = re.sub(r'\s*No.', 'No=', _str)
        _str = re.sub(r'\s*=\s*', '=', _str)
        _str = re.sub(r'\(\s*', '(', _str)
        _str = re.sub(r'\(.*?\)', '', _str)
        __lst = re.split(r'\s+-{3,}', _str)
        __result = []
        for __item in __lst[:-1]:
            __item = re.sub(r'\n', '', __item)
            __item = re.sub('=', ' ', __item)
            __lst_dict = __item.split()
            __result.append(pd.Series(dict(zip(__lst_dict[::2], __lst_dict[1::2]))))
        _tmp = pd.DataFrame(__result, dtype=float)
        _tmp[[_tmp.columns[0], _tmp.columns[1]]] = _tmp[[_tmp.columns[0], _tmp.columns[1]]].astype(int)
        return _tmp

    @property
    def cor_stiffness(self):
        """
        Coordinate of stiffness center.
        data type: DateFrame
        number of columns: 4
        columns: [FloorNo: int, TowerNo: int, Xstif: float, Ystif: float]
        units: [none, none, m, m]
        :return:
        """
        return self.stiffness_detail.iloc[:, 0: 4]

    @property
    def cor_mass(self):
        """
        Coordinate of mass center.
        data type: DateFrame
        number of columns: 4
        columns: [FloorNo: int, TowerNo: int, Xmass: float, Ymass: float]
        units: [none, none, m, m]
        :return:
        """
        return self.stiffness_detail.iloc[:, [0, 1, 5, 6]]

    @property
    def eccentricity_ratio(self):
        """
        Eccentricity Ratio.
        data type: DateFrame
        number of columns: 4
        columns: [FloorNo: int, TowerNo: int, Eex: float, Eey: float]
        units: [none, none, none, none]
        :return:
        """
        return self.stiffness_detail.iloc[:, [0, 1, 9, 10]]

    @property
    def stiffness_lateral(self):
        """
        Lateral stiffness.
        data type: DateFrame
        number of columns: 5
        columns: [FloorNo: int, TowerNo: int, RJX3: float, RJY3: float, RJZ3: float]
        units: [none, none, kN/m, kN/m, kN*m/Rad]
        :return:
        """
        return self.stiffness_detail.iloc[:, [0, 1, -3, -2, -1]]

    @property
    def stiffness_shear(self):
        """
        Shear stiffness.
        data type: DateFrame
        number of columns: 5
        columns: [FloorNo: int, TowerNo: int, RJX1: float, RJY1: float, RJZ1: float]
        units: [none, none, kN/m, kN/m, kN/m]
        :return:
        """
        return self.stiffness_detail.iloc[:, [0, 1, -6, -5, -4]]

    @property
    def mass_density_detail(self):
        """
        All information in '各楼层质量、单位面积质量分布(单位:kg/m**2)'
        data type: DataFrame
        :return:
        """
        _columns = re.findall(r'[\u4e00-\u9fa5]+', getattr(self, '_mass_density_info_str'))
        _data = StringIO(getattr(self, '_mass_density_info_str'))
        return pd.read_csv(_data, sep=r'\s+', skiprows=[0, ], names=_columns)

    @property
    def floor_mass(self):
        """
        Mass of every floor, summary of DEAD and LIVE
        data type: DateFrame
        number of columns: 3
        columns: [层号: int, 塔号: int, 楼层质量: float]
        units: [none, none, kg]
        :return:
        """
        return self.mass_density_detail.iloc[:, 0:3]

    @property
    def floor_mass_density(self):
        """
        Mass density of every floor, summary of DEAD and LIVE
        data type: DateFrame
        number of columns: 3
        columns: [层号: int, 塔号: int, 单位面积质量: float]
        units: [none, none, kg/m^2]
        :return:
        """
        return self.mass_density_detail.iloc[:, [0, 1, -2]]

    @property
    def floor_area(self):
        """
        Area of every floor, quotient of mass and mass density
        data type: DateFrame
        number of columns: 3
        columns: [层号: int, 塔号: int, 面积: float]
        units: [none, none, m^2]
        :return:
        """
        tmp = self.mass_density_detail
        tmp['面积'] = tmp.iloc[:, 2] / tmp.iloc[:, 3]
        return tmp.iloc[:, [0, 1, -1]]

    @property
    def overturn_info(self):
        tmp = '工况 ' + getattr(self, '_overturn_info_str')
        return lines_2_df(tmp)

    @property
    def building_stable_info(self):
        return BuildingStableInfo(getattr(self, '_building_stable_info_str'))

    @property
    def storey_shear_capacity_info(self):
        tmp = re.split(r'\n\n', getattr(self, '_storey_shear_capacity_info_str'))[-1]
        return lines_2_df(tmp)


class BuildingStableInfo(object):

    def __init__(self, content):
        content = content.replace(':', '')
        __lst = [x.strip() for x in re.split(r'\n\n', content)]
        self.eq = lines_2_df(__lst[__lst.index('地震') + 1])
        self.wind = lines_2_df(__lst[__lst.index('风荷载') + 1])


if __name__ == '__main__':

    dfp = utility.FilePath()
    wmass_file = dfp.full_name('wmass.out')
    with open(wmass_file, 'r') as f:
        wmass = Wmass(f.read())
