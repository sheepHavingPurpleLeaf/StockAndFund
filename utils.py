#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 07/07/2020 21:02
# @Author  : Ziye Yang

import datetime


def build_date_dict(start_date):
    """
    To build a dict with keys as dates from start_date to today: ie. {"20200707":0, "20200708":0}
    Args:
        start_date

    Returns:
        date_dict

    """
    date_dict = {}
    start_date = datetime.datetime.strptime(start_date, "%Y%m%d")
    today = datetime.datetime.today()
    date_range = today.toordinal() - start_date.toordinal()
    date_list = [start_date + datetime.timedelta(days=x) for x in range(date_range)]
    for date in date_list:
        date_dict[date.strftime("%Y%m%d")] = 0
    return date_dict


def has_duplicates(dates):
    """
    To check if list contain duplicates
    """
    if len(dates) == len(set(dates)):
        return False
    else:
        return True


def is_duplicates_identical(dates, net_values):
    """
    To check whether duplicate dates have same net value
    Args:
        dates: date list
        net_values: net value list

    """
    date_dict = build_date_dict(dates[0])
    for i in range(len(dates)):
        if dates[i] in date_dict.keys():
            if date_dict[dates[i]] == 0:
                date_dict[dates[i]] = net_values[i]
            elif date_dict[dates[i]] != net_values[i]:
                return False
    return True


def is_date_ascending(date_list):
    """
    To check is input date list ascending
    """
    dates = [datetime.datetime.strptime(d, "%Y%m%d") for d in date_list]
    date_ints = [d.toordinal() for d in dates]
    for i in range(1, len(date_ints) - 1):
        if date_ints[i] - date_ints[i - 1] < 0:
            return False
    return True


def remove_duplicates(dates, net_values):
    """

    Args:
        dates: date list
        net_values: net value list

    Returns: dates list and net values list with unique values

    """
    date_dict = build_date_dict(dates[0])
    dates_unique = []
    net_values_unique = []
    for i in range(len(dates)):
        if dates[i] in date_dict.keys():
            if date_dict[dates[i]] == 0:
                dates_unique.append(dates[i])
                net_values_unique.append(net_values[i])
                date_dict[dates[i]] = 1
    return dates_unique, net_values_unique


def extract_dict_from_dataframe(df, column_as_key, column_as_value):
    """

    Args:
        df: input data frame
        column_as_key: column of data frame to be dictionary keys
        column_as_value: column of data frame to be dictionary values

    Returns: extracted dictionary

    """
    keys = df[column_as_key].values.tolist()
    values = df[column_as_value].values.tolist()
    return dict(zip(keys, values))