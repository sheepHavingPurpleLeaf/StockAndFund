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
import logging
import json

logging.basicConfig(filename="log.txt",
                    filemode='w',
                    format='%(asctime)s, %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

with open('config.json', 'r') as json_file:
    params = json.load(json_file)


def build_result_dataframe(data, fund_type, filter_bad_fund=True):
    annual_return_rates = []
    annual_sharp_ratios = []
    max_draw_down = []
    codes = []
    count = 0
    less_than_a_year = 0
    funds_in_required_type = 0

    for code in data.keys():
        if data[code]['fund_type'] == fund_type:
            funds_in_required_type += 1
            adj_nav = data[code]['net_value'][:]
            dates = data[code]['net_value_date'][:]
            net_values, dates = algorithms.effective_net_values(adj_nav, dates, code)
            if len(net_values) >= 252:
                annual_return_rate = algorithms.annual_return(net_values)
                annual_sharp_ratio = algorithms.sharp_ratio(net_values)
                mdd = algorithms.max_draw_down(net_values, len(net_values))
                # remove funds with bad indicators
                if filter_bad_fund and (annual_return_rate < 0.1 or annual_sharp_ratio < 1):
                    logging.info(
                        "{} is deleted because it has: annual return rate {}, annual sharp ratio {}, max draw down {}".format(
                            code, annual_return_rate, annual_sharp_ratio, mdd))
                    count += 1
                    continue
                annual_return_rates.append(annual_return_rate)
                max_draw_down.append(mdd)
                annual_sharp_ratios.append(annual_sharp_ratio)
                codes.append(code)
            else:
                less_than_a_year += 1
    data_dict = {"code": codes, "max_draw_down": max_draw_down, "annual_return_rates": annual_return_rates,
                 "annual_sharp_ratios": annual_sharp_ratios}
    logging.info(
        "{} active funds in data - {} with bad indicators - {} less than a year = {} candidates".format(
            funds_in_required_type,
            count,
            less_than_a_year, len(codes)))
    df = pd.DataFrame(data=data_dict, columns=data_dict.keys())
    df = df.sort_values(by='annual_return_rates', ascending=False)
    return df


def train_validate(data, codes):
    alpha_of_funds = calculate_alpha(data, codes)
    result = alpha_of_funds.sort_values("confidence", ascending=False)
    sort_by_p = []
    for _, row in result.iterrows():
        if row['confidence'] > params['alpha_confidence'] and row['alpha_values'] > params['alpha_threshold']:
            if row['sharp_validation'] > 1 and row['return_rate_validation'] > 0.1:
                sort_by_p.append(row['codes'])
            else:
                logging.info("{} has bad performance in 2020, sharp: {}, return_rate: {}".format(row['codes'], row[
                    'sharp_validation'], row['return_rate_validation']))
    logging.info("alpha sorted by confidence: ", sort_by_p)


def calculate_alpha(data, codes):
    alpha_values = []
    p_values = []
    selected = []
    return_rate_validation = []
    mdd_validation = []
    sharp_validation = []
    monthly_trade_days = 22
    for code in codes:
        alpha = []
        dates = data[code]['net_value_date'][:]
        adj_nav = data[code]['net_value'][:]
        if params['calculate_alpha_until'] in dates:
            split_index = dates.index(params['calculate_alpha_until'])
        else:
            continue
        adj_nav_train, adj_nav_validate = adj_nav[split_index:], adj_nav[
                                                                 :split_index]  # dates are reversed before effective_net_values
        dates_train, dates_validate = dates[split_index:], dates[:split_index]
        net_values_train, dates_train = algorithms.effective_net_values(adj_nav_train, dates_train, code)

        df_net_values = pd.DataFrame({'net_value': net_values_train, 'trade_date': dates_train})
        df_factor = pd.read_csv(r'./factor.csv')
        df_factor['trade_date'].tolist()
        df_factor['trade_date'] = df_factor['trade_date'].apply(str)
        df = pd.merge(df_net_values, df_factor, on='trade_date')
        df['return'] = np.log(df['net_value']).diff(monthly_trade_days)
        df = df.dropna()
        monthly_return = df['return'].values.tolist()
        if len(monthly_return) < 252: continue
        mom = algorithms.normalization(df['mom_factor'].values.tolist())
        mkt = algorithms.normalization(df['mkt_factor'].values.tolist())
        smb = algorithms.normalization(df['smb_factor'].values.tolist())
        hml = algorithms.normalization(df['hml_factor'].values.tolist())
        if len(monthly_return) != 0:
            carhart1 = carhart.Carhart(monthly_trade_days, monthly_return, mom, mkt, smb, hml)
            qualified_alpha = 0
            for model in carhart1.models:
                if model.pvalues[0] < params['p_threshold']:  # we think alpha should > 0 if p[0] < 0.05
                    alpha.append(model.params[0])
                    qualified_alpha += 1
            if qualified_alpha > 0:
                alpha_values.append(sum(alpha) / len(alpha))
            else:
                alpha_values.append(0)
            p_values.append(qualified_alpha / len(carhart1.models))
            selected.append(code)

            adj_nav_validate, dates_validate = algorithms.effective_net_values(adj_nav_validate, dates_validate, code)
            return_rate_validation.append(algorithms.annual_return(adj_nav_validate))
            sharp_validation.append(algorithms.sharp_ratio(adj_nav_validate))
            mdd_validation.append(algorithms.max_draw_down(adj_nav_validate, len(adj_nav_validate)))
    data_dict = {"codes": selected, "alpha_values": alpha_values, "confidence": p_values,
                 "sharp_validation": sharp_validation, "mdd_validation": mdd_validation,
                 "return_rate_validation": return_rate_validation}
    df = pd.DataFrame(data=data_dict, columns=data_dict.keys())
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--load_data', default='20210105')
    args = parser.parse_args()
    # type_list = ["股票型", "混合型", "债券型", "货币市场型"]
    if args.load_data != "20210105":
        data = build_dataset.Fund(504).fund_info
    else:
        with open(args.load_data + ".pkl", 'rb') as pkl:
            data = pickle.load(pkl)
    df = build_result_dataframe(data, fund_type="股票型", filter_bad_fund=False)
    codes = df['code'].tolist()
    train_validate(data, codes)


if __name__ == '__main__':
    main()
