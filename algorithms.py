#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 30/06/2020 21:12
# @Author  : Ziye Yang
# @Purpose : Collections of useful algorithms

import numpy as np
import math
import utils


def effective_net_values(net_values, dates, code):
    """
    Args:
        net_values: net values of fund as a list
        dates: date of each net value
        code: code of fund

    return: effective net values and dates of fund as 2 list
    """
    # sort by date
    net_values.reverse()
    dates.reverse()
    effective_values = []
    effective_dates = []
    # Filter effective net values
    for i in range(len(net_values)):
        if net_values[i] != 1:
            effective_values.extend(net_values[i:])
            effective_dates.extend(dates[i:])
            break
    if not utils.is_date_ascending(effective_dates):
        print("{} dates is not ascending".format(code))
        return [], []
    if utils.has_duplicates(effective_dates):
        if not utils.is_duplicates_identical(effective_dates, effective_values):
            print("{} is deleted because it contains same dates with different net values".format(code))
            return [], []
        else:
            effective_dates, effective_values = utils.remove_duplicates(effective_dates, effective_values)
    length = len(effective_values)
    for i in range(1, length - 1):
        if effective_values[i] / effective_values[i + 1] < 0.5:
            print("{} on {} changed {}: {}".format(code, [effective_dates[i], effective_dates[i + 1]],
                                                   1 - effective_values[i] / effective_values[i + 1],
                                                   [effective_values[i], effective_values[i + 1]]))
            return [], []
    return effective_values, effective_dates


def calculate_return_rate(net_values):
    """

    Args:
        net_values: net values of fund as a list

    Returns: return_rate

    """
    return_rate = []
    for i in range(1, len(net_values) - 1):
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
