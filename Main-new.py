#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/26 18:18
# @File    : Main.py

import os

import tkinter as tk
from tkinter import ttk
from tkinter import Button
from tkinter import Entry
from tkinter import Frame
from tkinter import Scale
from tkinter import Label

from pandastable import Table

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import Wdisp
import Wmass
import Wzq
from utility import FilePath


class UI(tk.Tk):

    def __init__(self):
        super().__init__()

        __width_label_lc = 16

        self.result_type_dict = [('mass', 'mass'),
                                 ('mass density', 'mass_density'),
                                 ('stiffness', 'stf'),
                                 ('shear capacity', 's_c'),
                                 ('drift', 'drift')]

        self.result_type_dict_right = [('displacement ratio', 'dsp_r'),
                                       ('drift ratio', 'dft_r'),
                                       ('spectrum of time history curve', 'thc'),
                                       ('base shear of time history', 'sth'),
                                       ('drift of time history', 'dth')]

        self.result_type_dict_added = [('period', 'period'),
                                       ('seismic shear coefficient', 's_s_c'),
                                       ('seismic shear adjust factor', 's_a_f')]

        # variables of app
        self.file_path = FilePath()
        self.yjk_dir = tk.StringVar()
        self.etabs_name = tk.StringVar()
        self.result_type = tk.StringVar()
        self.result_type.set('drift')
        self.cur_tower_number = tk.StringVar()
        self.cur_merge_df = None
        self.tower_number = None
        self.position = None
        self.cur_result_type = None
        self.font = dict(family='KaiTi', color='black', weight='normal', size=10.5)

        # variables of YJK
        self.cur_yjk_class = None
        self.cur_yjk_dic = None
        self.cur_yjk_df = None
        self.df_yjk_export = None
        self.cur_yjk_lc = tk.StringVar()
        self.cur_yjk_tow_num_name = tk.StringVar()
        self.cur_yjk_flr_num_name = tk.StringVar()
        self.cur_yjk_content_name = tk.StringVar()
        self.lbl_yjk_tree_content = tk.StringVar()

        # variables of ETABS
        self.cur_etabs_dic = None
        self.cur_etabs_df = None
        self.df_etabs_export = None
        self.cur_etabs_lc = tk.StringVar()
        self.cur_etabs_tow_num_name = tk.StringVar()
        self.cur_etabs_flr_num_name = tk.StringVar()
        self.cur_etabs_content_name = tk.StringVar()
        self.lbl_etabs_tree_content = tk.StringVar()

        self.yjk_disp = None

        # GUI
        self.minsize(1280, 800)
        self.title('ARP_AnalysisResultProcessing')

        # start widget in frame_yjk_path
        self.frame_yjk_path = Frame(self)
        self.entry_yjk_path = Entry(self.frame_yjk_path, textvariable=self.yjk_dir)
        self.entry_yjk_path.pack(side=tk.LEFT, padx=5, pady=5, expand=tk.YES, fill=tk.X)
        self.btn_yjk_path = Button(self.frame_yjk_path, text='YJK', width=16, command=self.get_path)
        self.btn_yjk_path.pack(side=tk.LEFT, padx=5, pady=5)
        self.frame_yjk_path.pack(side=tk.TOP, fill=tk.X)
        # end widget in frame_yjk_path

        # start widget in frame_etabs_name
        self.frame_etabs_name = Frame(self)
        self.entry_etabs_name = Entry(self.frame_etabs_name, textvariable=self.etabs_name)
        self.entry_etabs_name.pack(side=tk.LEFT, padx=5, pady=5, expand=tk.YES, fill=tk.X)
        self.btn_etabs_path = Button(self.frame_etabs_name, text='ETABS', width=16, command=self.get_file_name)
        self.btn_etabs_path.pack(side=tk.LEFT, padx=5, pady=5)
        self.frame_etabs_name.pack(side=tk.TOP, fill=tk.X)
        # end widget in frame_etabs_name

        # start widget in frame_result_list
        self.frame_result_list = Frame(self)

        # option buttons of results
        self.lf_result_name = tk.LabelFrame(self.frame_result_list, text='Result to processing')

        self.frame_result_name_left = Frame(self.lf_result_name)
        for name, value in self.result_type_dict:
            _ = tk.Radiobutton(self.frame_result_name_left, text=name, value=value, anchor=tk.W,
                               command=self.get_type, variable=self.result_type)
            _.pack(side=tk.TOP, fill=tk.X, padx=5)
        self.frame_result_name_left.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)

        self.frame_result_name_right = Frame(self.lf_result_name)
        for name, value in self.result_type_dict_right:
            _ = tk.Radiobutton(self.frame_result_name_right, text=name, value=value, anchor=tk.W,
                               command=self.get_type, variable=self.result_type)
            _.pack(side=tk.TOP, fill=tk.X, padx=5)
        self.frame_result_name_right.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)

        self.frame_result_name_added = Frame(self.lf_result_name)
        for name, value in self.result_type_dict_added:
            _ = tk.Radiobutton(self.frame_result_name_added, text=name, value=value, anchor=tk.NW,
                               command=self.get_type, variable=self.result_type)
            _.pack(side=tk.TOP, fill=tk.X, padx=5)
        self.frame_result_name_added.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, anchor=tk.N)

        self.lf_result_name.pack(side=tk.TOP, fill=tk.X)

        # labelframe of yjk results
        self.lf_yjk = tk.LabelFrame(self.frame_result_list, text='YJK')

        # load combination cmb
        self.frame_yjk_lc = tk.Frame(self.lf_yjk)
        self.lbl_yjk_lc = tk.Label(self.frame_yjk_lc, width=__width_label_lc, text='Load Combination', anchor=tk.W)
        self.lbl_yjk_lc.pack(side=tk.LEFT, fill=tk.X)
        self.cmb_yjk_lc = ttk.Combobox(self.frame_yjk_lc, state="readonly", height=1, textvariable=self.cur_yjk_lc)
        self.cmb_yjk_lc.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=5)
        self.frame_yjk_lc.pack(side=tk.TOP, fill=tk.X)

        # tower number cmb
        self.frame_yjk_tower = tk.Frame(self.lf_yjk)
        self.lbl_yjk_tower = tk.Label(self.frame_yjk_tower, width=__width_label_lc, text='Tower Number', anchor=tk.W)
        self.lbl_yjk_tower.pack(side=tk.LEFT, fill=tk.X)
        self.cmb_yjk_tower = ttk.Combobox(self.frame_yjk_tower, state="readonly", height=1,
                                          textvariable=self.cur_yjk_tow_num_name)
        self.cmb_yjk_tower.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=5)
        self.frame_yjk_tower.pack(side=tk.TOP, fill=tk.X)

        # floor number cmb
        self.frame_yjk_floor = tk.Frame(self.lf_yjk)
        self.lbl_yjk_floor = tk.Label(self.frame_yjk_floor, width=__width_label_lc, text='Floor Number', anchor=tk.W)
        self.lbl_yjk_floor.pack(side=tk.LEFT, fill=tk.X)
        self.cmb_yjk_floor = ttk.Combobox(self.frame_yjk_floor, state="readonly", height=1,
                                          textvariable=self.cur_yjk_flr_num_name)
        self.cmb_yjk_floor.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=5)
        self.frame_yjk_floor.pack(side=tk.TOP, fill=tk.X)

        # result content cmb
        self.frame_yjk_content = tk.Frame(self.lf_yjk)
        self.lbl_yjk_content = tk.Label(self.frame_yjk_content, width=__width_label_lc, text='Content', anchor=tk.W)
        self.lbl_yjk_content.pack(side=tk.LEFT, fill=tk.X)
        self.cmb_yjk_content = ttk.Combobox(self.frame_yjk_content, state="readonly", height=1,
                                            textvariable=self.cur_yjk_content_name)
        self.cmb_yjk_content.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=5)
        self.frame_yjk_content.pack(side=tk.TOP, fill=tk.X)

        # self.yjk_tree
        self.yjk_tree = ttk.Treeview(self.lf_yjk, show='headings')
        self.yjk_tree['column'] = ['a', 'b', 'c']
        self.yjk_tree.column('a', width=18)
        self.yjk_tree.column('b', width=18)
        self.yjk_tree.column('c', width=18)
        self.yjk_tree.heading('a', text='Tower No.')
        self.yjk_tree.heading('b', text='Floor No.')
        self.yjk_tree.heading('c', text='content')
        self.yjk_tree.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

        self.scr_yjk_tree = tk.Scrollbar(self.yjk_tree)
        self.scr_yjk_tree.pack(side=tk.RIGHT, fill=tk.Y)

        self.yjk_tree.config(yscrollcommand=self.scr_yjk_tree.set)
        self.scr_yjk_tree.config(command=self.yjk_tree.yview)

        # self.lbl_yjk_tree
        self.lbl_yjk_tree = tk.Label(self.lf_yjk, anchor=tk.W, textvariable=self.lbl_yjk_tree_content)
        self.lbl_yjk_tree.pack(side=tk.TOP, fill=tk.X)

        self.lf_yjk.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        # end of labelframe yjk results

        # labelframe of etabs results
        self.lf_etabs = tk.LabelFrame(self.frame_result_list, text='ETABS')

        # load combination cmb
        self.frame_etabs_lc = tk.Frame(self.lf_etabs)
        self.lbl_etabs_lc = tk.Label(self.frame_etabs_lc, width=__width_label_lc,
                                     text='Load Combination', anchor=tk.W)
        self.lbl_etabs_lc.pack(side=tk.LEFT, fill=tk.X)
        self.cmb_etabs_lc = ttk.Combobox(self.frame_etabs_lc, state="readonly", height=1,
                                         textvariable=self.cur_etabs_lc)
        self.cmb_etabs_lc.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=5)
        self.frame_etabs_lc.pack(side=tk.TOP, fill=tk.X)

        # tower number cmb
        self.frame_etabs_tower = tk.Frame(self.lf_etabs)
        self.lbl_etabs_tower = tk.Label(self.frame_etabs_tower, width=__width_label_lc,
                                        text='Tower Number', anchor=tk.W)
        self.lbl_etabs_tower.pack(side=tk.LEFT, fill=tk.X)
        self.cmb_etabs_tower = ttk.Combobox(self.frame_etabs_tower, state="readonly", height=1,
                                            textvariable=self.cur_etabs_tow_num_name)
        self.cmb_etabs_tower.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=5)
        self.frame_etabs_tower.pack(side=tk.TOP, fill=tk.X)

        # floor number cmb
        self.frame_etabs_floor = tk.Frame(self.lf_etabs)
        self.lbl_etabs_floor = tk.Label(self.frame_etabs_floor, width=__width_label_lc,
                                        text='Floor Number', anchor=tk.W)
        self.lbl_etabs_floor.pack(side=tk.LEFT, fill=tk.X)
        self.cmb_etabs_floor = ttk.Combobox(self.frame_etabs_floor, state="readonly", height=1,
                                            textvariable=self.cur_etabs_flr_num_name)
        self.cmb_etabs_floor.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=5)
        self.frame_etabs_floor.pack(side=tk.TOP, fill=tk.X)

        # result content cmb
        self.frame_etabs_content = tk.Frame(self.lf_etabs)
        self.lbl_etabs_content = tk.Label(self.frame_etabs_content, width=__width_label_lc,
                                          text='Content', anchor=tk.W)
        self.lbl_etabs_content.pack(side=tk.LEFT, fill=tk.X)
        self.cmb_etabs_content = ttk.Combobox(self.frame_etabs_content, state="readonly", height=1,
                                              textvariable=self.cur_etabs_content_name)
        self.cmb_etabs_content.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=5)
        self.frame_etabs_content.pack(side=tk.TOP, fill=tk.X)

        # self.etabs_tree
        self.etabs_tree = ttk.Treeview(self.lf_etabs, show='headings')
        self.etabs_tree['column'] = ['a', 'b', 'c']
        self.etabs_tree.column('a', width=18)
        self.etabs_tree.column('b', width=18)
        self.etabs_tree.column('c', width=18)
        self.etabs_tree.heading('a', text='Tower No.')
        self.etabs_tree.heading('b', text='Floor No.')
        self.etabs_tree.heading('c', text='content')
        self.etabs_tree.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

        self.scr_etabs_tree = tk.Scrollbar(self.etabs_tree)
        self.scr_etabs_tree.pack(side=tk.RIGHT, fill=tk.Y)

        self.etabs_tree.config(yscrollcommand=self.scr_etabs_tree.set)
        self.scr_etabs_tree.config(command=self.etabs_tree.yview)

        # self.lbl_etabs_tree
        self.lbl_etabs_tree = tk.Label(self.lf_etabs, anchor=tk.W, textvariable=self.lbl_etabs_tree_content)
        self.lbl_etabs_tree.pack(side=tk.TOP, fill=tk.X)

        self.lf_etabs.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

        # self.lf_data_import
        self.lf_data_import = tk.LabelFrame(self.frame_result_list, text='action')

        # button yjk import
        self.btn_yjk_import = Button(self.lf_data_import, text='add YJK data', width=18, command=self.import_yjk)
        self.btn_yjk_import.pack(side=tk.LEFT, anchor=tk.W, padx=36)

        # button etabs import
        self.btn_etabs_import = Button(self.lf_data_import, text='add ETABS data', width=18, command=self.import_etabs)
        self.btn_etabs_import.pack(side=tk.LEFT, anchor=tk.CENTER, padx=36)

        # button merge and import
        self.btn_merge = Button(self.lf_data_import, text='merge and add', width=18, command=self.merge_import)
        self.btn_merge.pack(side=tk.LEFT, anchor=tk.E, padx=36)

        self.lf_data_import.pack(side=tk.TOP, fill=tk.X)

        self.frame_result_list.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)
        # end widget in frame_result_list

        # start widget in frame_data_table
        self.frame_data_table = Frame(self)
        self.frame_table = Frame(self.frame_data_table)
        self.data_table = Table(self.frame_table, rows=50, cols=10, showstatusbar=True)
        self.data_table.show()
        self.frame_table.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        self.frame_tower = Frame(self.frame_data_table)
        self.lbl_tower = Label(self.frame_data_table, text='tower No.').pack(side=tk.BOTTOM)
        self.tower_scale = Scale(self.frame_data_table, orient=tk.HORIZONTAL, length=300, width=16, sliderlength=10,
                                 from_=0, to=10, tickinterval=1,
                                 variable=self.cur_tower_number,
                                 command=self.tower_select)
        self.tower_scale.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.frame_tower.pack(side=tk.TOP, fill=tk.X)
        self.frame_data_table.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        # end widget in frame_data_table

        # start widget in frame_image
        self.frame_image = Frame(self)
        self.fig = Figure(figsize=(3.378, 4.331), dpi=150)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_image)
        self.canvas.get_tk_widget().pack(side=tk.TOP)
        self.canvas.draw()
        toolbar = NavigationToolbar2Tk(self.canvas, self.frame_image)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP)

        self.lf_plot_control = tk.LabelFrame(self.frame_image, text='plot')

        self.lbl = Label(self.lf_plot_control, text='none').pack(side=tk.LEFT, fill=tk.X)
        self.btn_batch_plot = Button(self.lf_plot_control, text='batch plot', command=self.batch_plot)
        self.btn_batch_plot.pack(side=tk.RIGHT)

        self.lf_plot_control.pack(side=tk.BOTTOM, fill=tk.X)

        self.frame_image.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        # end widget in frame_image

        self.data_table.zoomOut()
        self.data_table.zoomOut()

        self.action_bind()

    def action_bind(self):
        # action when yjk cmb selected
        self.cmb_yjk_lc.bind("<<ComboboxSelected>>", self.update_yjk_cmb)
        self.cmb_yjk_tower.bind("<<ComboboxSelected>>", self.update_yjk_tree)
        self.cmb_yjk_floor.bind("<<ComboboxSelected>>", self.update_yjk_tree)
        self.cmb_yjk_content.bind("<<ComboboxSelected>>", self.update_yjk_tree)

        # action when etabs cmb selected
        self.cmb_etabs_lc.bind("<<ComboboxSelected>>", self.update_etabs_cmb)
        self.cmb_etabs_tower.bind("<<ComboboxSelected>>", self.update_etabs_tree)
        self.cmb_etabs_floor.bind("<<ComboboxSelected>>", self.update_etabs_tree)
        self.cmb_etabs_content.bind("<<ComboboxSelected>>", self.update_etabs_tree)

    def get_path(self):
        """
        get path of yjk result by FilePath class.
        update yjk widgets.
        :return:
        """
        self.file_path.get_path()
        self.entry_yjk_path.delete(0, tk.END)
        self.entry_yjk_path.insert(tk.END, self.file_path.yjk_path)
        self.yjk_update()

    def get_file_name(self):
        """
        get filename of etabs result in excel format by FilePath class.
        update etabs widgets.
        :return:
        """
        self.file_path.get_path(openfile=True)
        self.entry_etabs_name.delete(0, tk.END)
        self.entry_etabs_name.insert(tk.END, self.file_path.etabs_name)
        if self.file_path.etabs_name is not None and self.file_path.etabs_name != '':
            self.etabs_update()

    def get_type(self):
        self.yjk_update()
        self.etabs_update()

    def yjk_update(self):
        if self.file_path.yjk_path is not None and os.path.exists(self.file_path.yjk_path) is True:
            self.cur_result_type = self.result_type.get()
            if self.cur_result_type == 'drift':
                with open(self.file_path.full_name('Wdisp.out'), 'r') as f:
                    self.cur_yjk_class = Wdisp.Wdisp(f.read())
                    self.cmb_yjk_lc['values'] = self.cur_yjk_class.cqc
                    self.cmb_yjk_lc.current(0)
                    self.cmb_yjk_lc.configure(height=len(self.cur_yjk_class.cqc))
            elif self.cur_result_type == 'dsp_r' or self.result_type.get() == 'dft_r':
                with open(self.file_path.full_name('Wdisp.out'), 'r') as f:
                    self.cur_yjk_class = Wdisp.Wdisp(f.read())
                    self.cmb_yjk_lc['values'] = self.cur_yjk_class.spc_lateral
                    self.cmb_yjk_lc.current(0)
                    self.cmb_yjk_lc.configure(height=len(self.cur_yjk_class.spc_lateral))
            elif self.cur_result_type == 'mass':
                with open(self.file_path.full_name('wmass.out'), 'r') as f:
                    self.cur_yjk_class = Wmass.Wmass(f.read())
                    self.cmb_yjk_lc['values'] = ['mass_info']
                    self.cmb_yjk_lc.current(0)
            elif self.cur_result_type == 'mass_density':
                with open(self.file_path.full_name('wmass.out'), 'r') as f:
                    self.cur_yjk_class = Wmass.Wmass(f.read())
                    self.cmb_yjk_lc['values'] = ['mass_density_detail']
                    self.cmb_yjk_lc.current(0)
            elif self.cur_result_type == 'stf':
                with open(self.file_path.full_name('wmass.out'), 'r') as f:
                    self.cur_yjk_class = Wmass.Wmass(f.read())
                    self.cmb_yjk_lc['values'] = ['stiffness_detail']
                    self.cmb_yjk_lc.current(0)
            elif self.cur_result_type == 's_c':
                with open(self.file_path.full_name('wmass.out'), 'r') as f:
                    self.cur_yjk_class = Wmass.Wmass(f.read())
                    self.cmb_yjk_lc['values'] = ['storey_shear_capacity_info']
                    self.cmb_yjk_lc.current(0)
            elif self.cur_result_type == 'period':
                with open(self.file_path.full_name('wzq.out'), 'r') as f:
                    self.cur_yjk_class = Wzq.Wzq(f.read())
                    self.cmb_yjk_lc['values'] = ['period']
                    self.cmb_yjk_lc.current(0)
            elif self.cur_result_type == 's_a_f':
                with open(self.file_path.full_name('wzq.out'), 'r') as f:
                    self.cur_yjk_class = Wzq.Wzq(f.read())
                    self.cmb_yjk_lc['values'] = ['shear_adjust_factor']
                    self.cmb_yjk_lc.current(0)
            elif self.cur_result_type == 's_s_c':
                with open(self.file_path.full_name('wzq.out'), 'r') as f:
                    self.cur_yjk_class = Wzq.Wzq(f.read())
                    self.cmb_yjk_lc['values'] = self.cur_yjk_class.s_s_c
                    self.cmb_yjk_lc.current(0)

            self.read_yjk_df()
            self.update_yjk_cmb(None)

    def read_yjk_df(self):
        if len(self.cmb_yjk_lc['values']) != 0:
            self.cur_yjk_df = getattr(self.cur_yjk_class, self.cur_yjk_lc.get())

    def update_yjk_cmb(self, event):
        self.read_yjk_df()
        _columns = self.cur_yjk_df.columns.tolist()
        if self.result_type.get() == 'drift':
            self.position = (1, 0, len(_columns)-3)
        elif self.result_type.get() == 'dsp_r':
            self.position = (1, 0, len(_columns)-1)
        elif self.result_type.get() == 'dft_r':
            self.position = (1, 0, 5)
        elif self.result_type.get() == 'mass':
            self.position = (1, 0, 5)
        elif self.result_type.get() == 'mass_density':
            self.position = (1, 0, 3)
        elif self.result_type.get() == 'stf':
            self.position = (1, 0, len(_columns)-3)
        elif self.result_type.get() == 's_c':
            self.position = (1, 0, len(_columns)-2)
        elif self.cur_result_type == 'period':
            self.position = (0, 1, 3)
        elif self.cur_result_type == 's_a_f':
            self.position = (1, 0, 2)
        elif self.cur_result_type == 's_s_c':
            self.position = (1, 0, 4)
        self.cmb_yjk_tower['values'] = _columns
        self.cmb_yjk_tower.configure(height=len(_columns))
        self.cmb_yjk_tower.current(self.position[0])
        self.cmb_yjk_floor['values'] = _columns
        self.cmb_yjk_floor.configure(height=len(_columns))
        self.cmb_yjk_floor.current(self.position[1])
        self.cmb_yjk_content['values'] = _columns
        self.cmb_yjk_content.configure(height=len(_columns))
        self.cmb_yjk_content.current(self.position[2])
        self.update_yjk_tree(None)

    def update_yjk_tree(self, event):
        if self.cur_yjk_tow_num_name.get() is not None and\
                self.cur_yjk_flr_num_name.get() is not None and \
                self.cmb_yjk_content.get() is not None:
            self.df_yjk_export = self.cur_yjk_df[[self.cur_yjk_tow_num_name.get(),
                                                  self.cur_yjk_flr_num_name.get(),
                                                  self.cur_yjk_content_name.get()]]

            _content = self.yjk_tree.get_children()
            for _ in _content:
                self.yjk_tree.delete(_)

            for _ in range(len(self.df_yjk_export)-1, -1, -1):
                self.yjk_tree.insert('', 0, values=self.df_yjk_export.iloc[_].tolist())

            self.lbl_yjk_tree_content.set('%d row, %d columns' % (self.df_yjk_export.shape[0],
                                                                  self.df_yjk_export.shape[1]))

    def etabs_update(self):
        pass

    def update_etabs_cmb(self, event):
        pass

    def update_etabs_tree(self, event):
        pass

    def import_yjk(self):
        self.data_table.model.df = self.df_yjk_export
        number_groups = self.df_yjk_export.groupby(self.df_yjk_export.columns.tolist()[0]).ngroups
        self.tower_scale.config(to=number_groups)
        self.cur_tower_number.set(0)
        self.data_table.redraw()
        self.plot()

    def import_etabs(self):
        self.plot()
        pass

    def merge_import(self):
        self.plot()
        pass

    def tower_select(self, tower_number):
        group_by_tower = self.df_yjk_export.groupby(self.df_yjk_export.columns.tolist()[0])
        tower_number = int(tower_number)
        if tower_number == 0:
            self.data_table.model.df = self.df_yjk_export
        else:
            self.data_table.model.df = group_by_tower.get_group(tower_number)
        self.data_table.redraw()
        self.plot()

    def plot(self):
        self.ax.clear()
        tower_number = int(self.cur_tower_number.get())
        if tower_number == 0 and tower_number > 1:
            pass
        elif tower_number > 0:
            if self.result_type.get() == 'drift':
                self.ax.plot(1/self.data_table.model.df.iloc[:, 2]*1000,
                             self.data_table.model.df.iloc[:, 1], marker='o')
                self.ax.grid(alpha=0.5, linestyle="-.", linewidth=0.3)
                self.ax.set_xlabel('位移角(1/1000)', fontdict=self.font)
                self.ax.set_ylabel('楼层', fontdict=self.font)
                self.fig.tight_layout(pad=0.3)
            elif self.result_type.get() == 'dsp_r':
                self.ax.plot(self.data_table.model.df.iloc[:, 2],
                             self.data_table.model.df.iloc[:, 1], marker='o')
                self.ax.grid(alpha=0.5, linestyle="-.", linewidth=0.3)
                self.ax.set_xlabel('位移比', fontdict=self.font)
                self.ax.set_ylabel('楼层', fontdict=self.font)
                self.fig.tight_layout(pad=0.3)
            elif self.result_type.get() == 'dft_r':
                self.ax.plot(self.data_table.model.df.iloc[:, 2],
                             self.data_table.model.df.iloc[:, 1], marker='o')
                self.ax.grid(alpha=0.5, linestyle="-.", linewidth=0.3)
                self.ax.set_xlabel('层间位移比', fontdict=self.font)
                self.ax.set_ylabel('楼层', fontdict=self.font)
                self.fig.tight_layout(pad=0.3)
            elif self.result_type.get() == 'mass':
                self.ax.plot(self.data_table.model.df.iloc[:, 2],
                             self.data_table.model.df.iloc[:, 1], marker='o')
                self.ax.grid(alpha=0.5, linestyle="-.", linewidth=0.3)
                self.ax.set_xlabel('楼层质量', fontdict=self.font)
                self.ax.set_ylabel('楼层', fontdict=self.font)
                self.fig.tight_layout(pad=0.3)
            elif self.result_type.get() == 'mass_density':
                self.ax.plot(self.data_table.model.df.iloc[:, 2],
                             self.data_table.model.df.iloc[:, 1], marker='o')
                self.ax.grid(alpha=0.5, linestyle="-.", linewidth=0.3)
                self.ax.set_xlabel('单位面积楼层质量', fontdict=self.font)
                self.ax.set_ylabel('楼层', fontdict=self.font)
                self.fig.tight_layout(pad=0.3)
            elif self.result_type.get() == 'stf':
                self.ax.plot(self.data_table.model.df.iloc[:, 2],
                             self.data_table.model.df.iloc[:, 1], marker='o')
                self.ax.grid(alpha=0.5, linestyle="-.", linewidth=0.3)
                self.ax.set_xlabel('抗侧刚度（v/d）', fontdict=self.font)
                self.ax.set_ylabel('楼层', fontdict=self.font)
                self.fig.tight_layout(pad=0.3)
            elif self.result_type.get() == 's_c':
                self.ax.plot(self.data_table.model.df.iloc[:, 2],
                             self.data_table.model.df.iloc[:, 1], marker='o')
                self.ax.grid(alpha=0.5, linestyle="-.", linewidth=0.3)
                self.ax.set_xlabel('楼层受剪承载力', fontdict=self.font)
                self.ax.set_ylabel('楼层', fontdict=self.font)
                self.fig.tight_layout(pad=0.3)
            elif self.cur_result_type == 'period':
                pass
            elif self.cur_result_type == 's_a_f':
                self.ax.plot(self.data_table.model.df.iloc[:, 2],
                             self.data_table.model.df.iloc[:, 1], marker='o')
                self.ax.grid(alpha=0.5, linestyle="-.", linewidth=0.3)
                self.ax.set_xlabel('地震剪力放大系数', fontdict=self.font)
                self.ax.set_ylabel('楼层', fontdict=self.font)
                self.fig.tight_layout(pad=0.3)
            elif self.cur_result_type == 's_s_c':
                self.ax.plot(self.data_table.model.df.iloc[:, 2],
                             self.data_table.model.df.iloc[:, 1], marker='o')
                self.ax.grid(alpha=0.5, linestyle="-.", linewidth=0.3)
                self.ax.set_xlabel('剪重比(%)', fontdict=self.font)
                self.ax.set_ylabel('楼层', fontdict=self.font)
                self.fig.tight_layout(pad=0.3)
            self.canvas.draw()
            pass

    def figure_save(self, fig_name=None):
        if fig_name is None:
            fig_name = '%s.png' % self.cur_yjk_lc.get()
        self.fig.savefig(self.file_path.result_name(fig_name), transparent=True, dpi=300, format='png')

    def batch_plot(self):
        result_type_dict = self.result_type_dict + self.result_type_dict_right + self.result_type_dict_added
        if self.yjk_dir.get() != '' or self.etabs_name.get() != '':
            for name, result_type in result_type_dict:
                self.result_type.set(result_type)
                self.yjk_update()
                for ct, lc_name in enumerate(self.cmb_yjk_lc['values']):
                    self.cur_yjk_lc.set(lc_name)
                    self.update_yjk_cmb(None)
                    self.import_yjk()
                    self.cur_tower_number.set(1)
                    self.tower_select(1)
                    f_name = '%s-%d-%s.png' % (name, ct, lc_name)
                    self.figure_save(f_name)


if __name__ == "__main__":
    ui = UI()
    ui.mainloop()
