#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 30/06/2020 21:12
# @Author  : Ziye Yang
# @Purpose : Collections of useful algorithms

import numpy as np
import math


def effective_net_values(net_values):
    """
    Args:
        net_values: net values of fund as a list

    return: effective net values of fund as a list
    """
    # sort by date
    net_values.reverse()
    effective_net_values_list = []
    effective_signal = 0
    # Filter effective net values
    for i in range(len(net_values)):
        if net_values[i] != 1:
            effective_signal += 1
        if effective_signal != 0:
            effective_net_values_list.append(net_values[i])
    return effective_net_values_list


def calculate_return_rate(net_values):
    """

    Args:
        net_values: net values of fund as a list

    Returns: return_rate

    """
    return_rate = []
    for i in range(1, len(net_values)-1):
        return_rate.append((net_values[i] - net_values[i - 1]) / net_values[i - 1])

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


def annual_return(net_values):
    """

    Args:
        net_values: net values of fund as a list

    Returns: annual_return_rate

    """
    annual_return_rate = (net_values[-1] / net_values[0]) ** (252 / len(net_values)) - 1
    return annual_return_rate


def sharp_ratio(net_values):
    """

    Args:
        net_values: net values of fund as a list

    Returns: annual_sharp_ratio

    """
    annual_no_risk_return = 0.03
    annual_return_rate = annual_return(net_values)
    return_rates = calculate_return_rate(net_values)
    annual_return_rates_std = np.std(return_rates) * math.sqrt(252)
    annual_sharp_ratio = (annual_return_rate - annual_no_risk_return) / annual_return_rates_std
    return annual_sharp_ratio
