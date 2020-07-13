#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 11/07/2020 17:20
# @Author  : Ziye Yang
# @Purpose : build Carhart model for each fund

import statsmodels.api as sm
import numpy as np


class Carhart:
    def __init__(self, time_window, adj_nav, mkt, smb, hml, mom):
        """
        Return list of Carhart models with time_window spacing
        """
        self.start_indices = self.get_start_indices(adj_nav, time_window)
        self.X_list = []
        self.Y_list = []
        self.models = []
        for start_index in self.start_indices:
            x = [(a, b, c, d) for (a, b, c, d) in zip(np.array(mkt[start_index:start_index + 252]),
                                                                    np.array(smb[start_index:start_index + 252]),
                                                                    np.array(hml[start_index:start_index + 252]),
                                                                    np.array(mom[start_index:start_index + 252]))]
            self.X_list.append(x)
            self.Y_list.append(np.array(adj_nav[start_index:start_index + 252]))
        self.training()

    def training(self):
        for i in range(len(self.X_list)):
            x = sm.add_constant(self.X_list[i])
            self.models.append(sm.OLS(self.Y_list[i], x).fit())

    @staticmethod
    def get_start_indices(lst, window):
        start_indices = []
        start_index = 0
        while start_index + 252 < len(lst):
            start_indices.append(start_index)
            start_index += window
        return start_indices
