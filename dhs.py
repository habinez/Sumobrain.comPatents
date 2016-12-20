#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 23:33:50 2016
@author: chabinez

download DHS Yearbook tables of Immigration Statistics 2015
"""

from lxml import html
from urllib import request
import numpy as np
import pandas as pd

if __name__ == "__main__":
    captions = set()
    writer = pd.ExcelWriter('dhs.xlsx', engine="xlsxwriter")
    for table_num in range(1, 42):
        url = "https://www.dhs.gov/immigration-statistics/"\
                    "yearbook/2015/table{0}".format(table_num)
        tree = html.parse(request.urlopen(url))
        _path = '//*[@id="content-area"]/div/div/article/div[1]/div[2]/div/div/table'
        tables = tree.xpath(_path)
        """ Some tables contains data  by continents and by countries.
        The data by countries will override the one for continents
        in the following for loop
        """
        for table in tables:
            data = [row.text_content().strip().split("\n")
                        for row in table.xpath('//tr')]
            cap = table.xpath('//caption')[0].text_content()
            df = pd.DataFrame(data=data[1:])
            if df.shape[1] == len(data[0]):
                df.columns=data[0]
                df.replace('-', np.nan, inplace=True)
                df.to_excel(writer, sheet_name="Table{}".format(table_num), index=False)
                captions.add(cap)
    writer.save()
    captions = sorted(list(captions))
    with open('captions.txt', 'w') as caption_file:
        caption_file.write("\n".join(captions))
