#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 29/06/2020 00:38
# @Author  : Ziye Yang
# @Purpose : To select best fund base on TuShare's dataset

import tushare as ts

pro = ts.pro_api()

df = pro.fund_basic(market='E')
print(df)
