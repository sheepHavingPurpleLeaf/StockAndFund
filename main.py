#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 01/07/2020 20:29
# @Author  : Ziye Yang

import algorithms
import argparse
import build_dataset
import carhart
import numpy as np
import pickle
import pandas as pd
import utils


def build_result_dataframe(data, fund_type):
    annual_return_rates = []
    annual_sharp_ratios = []
    max_draw_down = []
    codes = []
    for code in data.keys():
        if data[code]['fund_type'] == fund_type:
            adj_nav = data[code]['net_value']
            dates = data[code]['net_value_date']
            net_values, dates = algorithms.effective_net_values(adj_nav, dates, code)
            if len(net_values) >= 252:
                max_draw_down.append(algorithms.max_draw_down(net_values, len(net_values)))
                annual_return_rate = algorithms.annual_return(net_values)
                annual_return_rates.append(annual_return_rate)
                annual_sharp_ratio = algorithms.sharp_ratio(net_values)
                annual_sharp_ratios.append(annual_sharp_ratio)
                codes.append(code)
    data_dict = {"code": codes, "max_draw_down": max_draw_down, "annual_return_rates": annual_return_rates,
                 "annual_sharp_ratios": annual_sharp_ratios}
    print("we have {} active funds in data".format(len(data_dict)))
    df = pd.DataFrame(data=data_dict, columns=data_dict.keys())
    df = df.sort_values(by='annual_sharp_ratios', ascending=False)
    print(fund_type + '\n', df.head())
    return df


def calculate_alpha(data):
    alpha_dict = {}
    for code in data.keys():
        if data[code]['fund_type'] == "股票型":
            alpha = []
            adj_nav = data[code]['net_value']
            dates = data[code]['net_value_date']
            net_values, dates = algorithms.effective_net_values(adj_nav, dates, code)
            df_net_values = pd.DataFrame({'net_value': net_values, 'trade_date': dates})
            df_factor = pd.read_csv(r'./factor.csv')
            df_factor['trade_date'].tolist()
            df_factor['trade_date'] = df_factor['trade_date'].apply(str)
            df = pd.merge(df_net_values, df_factor, on='trade_date')
            df['return'] = np.log(df['net_value']).diff(21)
            df = df.dropna()
            monthly_return = df['return'].values.tolist()
            mom = algorithms.normalization(df['mom_factor'].values.tolist())
            mkt = algorithms.normalization(df['mkt_factor'].values.tolist())
            smb = algorithms.normalization(df['smb_factor'].values.tolist())
            hml = algorithms.normalization(df['hml_factor'].values.tolist())
            if len(monthly_return) != 0:
                carhart1 = carhart.Carhart(21, monthly_return, mom, mkt, smb, hml)
                qualified_alpha = 0
                for model in carhart1.models:
                    if model.pvalues[0] < 0.1:
                        alpha.append(model.params[0])
                        qualified_alpha += 1
                alpha_average = sum(alpha) / len(alpha)
                ratio = qualified_alpha / len(carhart1.models)
                alpha_dict[code] = [alpha_average, ratio]
    return alpha_dict


def get_excellents_in_common(range, df, alpha_dict):
    sharp_ratio_dict = utils.extract_dict_from_dataframe(df, "code", "annual_sharp_ratios")
    sorted_by_sharp_ratio = sorted(sharp_ratio_dict.items(), key=lambda x: x[1], reverse=True)
    mdd_dict = utils.extract_dict_from_dataframe(df, "code", "max_draw_down")
    sorted_by_mdd = sorted(mdd_dict.items(), key=lambda x: x[1])
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--load_data', default='20200707')
    args = parser.parse_args()
    # type_list = ["股票型", "混合型", "债券型", "货币市场型"]
    if args.load_data != "20200707":
        data = build_dataset.Fund(365).fund_info
        alpha_of_funds = calculate_alpha(data)
        with open('alpha.pkl', 'wb') as output:
            pickle.dump(alpha_of_funds, output)
    else:
        with open(args.load_data + ".pkl", 'rb') as pkl:
            data = pickle.load(pkl)
        with open("alpha.pkl", 'rb') as pkl:
            alpha_of_funds = pickle.load(pkl)
    df = build_result_dataframe(data, fund_type="股票型")
    result = sorted(alpha_of_funds.items(), key=lambda x: x[1], reverse=True)
    print(result)
    get_excellents_in_common(30, df, result)


if __name__ == '__main__':
    main()
