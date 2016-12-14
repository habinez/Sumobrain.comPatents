import numpy as np
import pandas as pd
from lxml import html
"""
The program shows all companies listed on nasdaq.
The return dataframe have the following data structure
|Name |Symbol | MarketCap| Country| Subsector| Industry|
|-----|-------|----------|--------|----------|---------|
|str  |str    |float     |str     |str       |str      |

"""

#%%%
def get_industry_nasdaq_listing(industry_url):
    """
    """
    companies = []
    xpath = '//*[@id="CompanylistResults"]'
    tree = html.parse(industry_url)
    table = tree.xpath(xpath)[0]
    for row in table.iterchildren():
        if isinstance(row, html.HtmlElement):
            if len(row.findall('td')) > 1:
                row_content = []
                for cell in row.text_content().split("\r"):
                    cell = cell.strip()
                    if cell:
                        row_content.append(cell)
                if len(row_content) > 6:
                    row_content.pop(3)
                companies.append(row_content)
    return companies
#%%

def dollar_amount(amount):
    """
    """
    if isinstance(amount, str):
        value = float(amount[1:-1])
        if amount.endswith("K"):
            return value * 10**3
        elif amount.endswith("M"):
            return value * 10**6
        elif amount.endswith("B"):
            return value * 10**9
        elif amount.startswith('$'):
            return float(amount.replace('$', ''))
    return amount
#%%
def nasdaq():
    """ """
    nasdaq_url = ('http://www.nasdaq.com/screening/'\
                'companies-by-industry.aspx?'\
                'industry=Consumer%20Durables')
    tree = html.parse(nasdaq_url)
    industry_types = tree.xpath('//*[@id="industryshowall"]')[0]
    colnames = ['Name',
                'Symbol',
                'MarketCap',
                'Country',
                'IPOYear',
                'Subsector']
    ind_df = pd.DataFrame(columns=colnames)
    ind_df["Industry"] = pd.Series()
    for industry in industry_types.iterchildren():
        if industry.text:
            industry_link = industry.get('href') + '&pagesize=3000'
            ind_list = get_industry_nasdaq_listing(industry_link)
            df = pd.DataFrame(data=ind_list, columns=colnames)
            df.replace('n/a', np.nan, inplace=True)
            df["Industry"] = pd.Series([industry.text]*df.size)
            ind_df = pd.concat([ind_df, df])
    ind_df.dropna(how="all", inplace=True, axis=1)
    ind_df['MarketCap'] = ind_df['MarketCap'].apply(dollar_amount).astype(float)
    return ind_df
#%%
if __name__ == "__main__":
    """
    """
    dataframe = nasdaq()
