#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 30/06/2020 21:12
# @Author  : Ziye Yang
# @Purpose : Collections of useful algorithms

import numpy as np
import math


def calculate_return_rate(net_values):
    """

    Args:
        net_values: net values of fund as a list

    Returns: return_rate

    """
    return_rate = []
    for i in range(len(net_values) - 1):
        return_rate.append((net_values[i] - net_values[i + 1]) / net_values[i + 1])
    return return_rate


def max_draw_down(net_values, time_window):
    """

    Args:
        net_values: net values of fund as a list
        time_window: how many days ago from today

    Returns: max draw down in time window

    """
    net_values = net_values[:time_window]
    return ((np.maximum.accumulate(net_values) - net_values) / np.maximum.accumulate(net_values)).max()


def sharp_ratio(net_values):
    """

    Args:
        net_values: net values of fund as a list

    Returns: daily_sharp_ratio, annual_sharp_ratio

    """
    annual_no_risk_return = 0.03
    daily_no_risk_return = (1 + annual_no_risk_return) ** (1.0 / 365) - 1
    return_rates = calculate_return_rate(net_values)
    return_rates_mean = np.mean(return_rates)
    return_rates_std = np.std(return_rates)

    daily_sharp_ratio = (return_rates_mean - daily_no_risk_return) / return_rates_std
    annual_sharp_ratio = daily_sharp_ratio * math.sqrt(len(net_values))

    return daily_sharp_ratio, annual_sharp_ratio
