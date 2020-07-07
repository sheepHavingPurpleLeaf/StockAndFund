#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 01/07/2020 20:29
# @Author  : Ziye Yang
# @Purpose : 

import algorithms
import argparse
import build_dataset
import pickle
import pandas as pd


def build_result_dataframe(data, fund_type):
    annual_return_rates = []
    annual_sharp_ratios = []
    max_draw_down = []
    codes = []
    for code in data.keys():
        if data[code]['fund_type'] == fund_type:
            adj_nav = data[code]['net_value']
            net_values = algorithms.effective_net_values(adj_nav)
            if len(net_values) >= 252:
                max_draw_down.append(algorithms.max_draw_down(net_values, len(net_values)))
                annual_return_rate = algorithms.annual_return(net_values)
                annual_return_rates.append(annual_return_rate)
                annual_sharp_ratio = algorithms.sharp_ratio(net_values)
                annual_sharp_ratios.append(annual_sharp_ratio)
                codes.append(code)
    data_dict = {"code": codes, "max_draw_down": max_draw_down, "annual_return_rates": annual_return_rates,
                 "annual_sharp_ratios": annual_sharp_ratios}
    df = pd.DataFrame(data=data_dict, columns=data_dict.keys())
    #df = df.sort_values(by='annual_sharp_ratios', ascending=False)
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--load_data', default='20200704')

    args = parser.parse_args()
    if args.load_data != "20200704":
        build_dataset.Fund(365)
    with open(args.load_data + ".pkl", 'rb') as pkl:
        data = pickle.load(pkl)
    print("we have {} active funds in data".format(len(data)))

    type_list = ["股票型", "混合型", "债券型", "货币市场型"]
    for fund_type in type_list:
        df = build_result_dataframe(data, fund_type)
        pd.set_option('display.max_columns',None)
        print(fund_type + '\n', df.head())


if __name__ == '__main__':
    main()
