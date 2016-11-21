# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 00:48:18 2016

@author: Concorde Habineza
"""
from lxml import html

#%%
def get_top_level_links(tree):
    topics = tree.xpath('//*[@id="bottom_div"]/div/div/a')
    all_links = list()
    categories = list()
    for page in topics:
        relative_link = page.get('href')
        page.make_links_absolute()
        absolute_link = page.get('href')
        if not relative_link.startswith('/dir'):
            all_links.append(absolute_link)
        topic = page.text_content()
        categories.append({"Catorigy": topic, "alink": absolute_link, "rlink": relative_link})
    return all_links
#%%   
def process_table(page):
    table_rows = page.xpath('//*[@id="results"]/div[2]/table[2]/tbody/tr')
    patents =[]
    for row in table_rows[1:]: # the first row contains the table header
        columns = row.xpath('td')
        first_column = columns[0]
        second_column = columns[1]
        second_column.make_links_absolute()
        patent_id = first_column.text_content().strip()
        absolute_link = list(list(second_column.iterlinks())[0])[2]
        patents.append([patent_id, absolute_link])
    return patents

def process_link(_link, data):
    global page_count
    print("scrapping " , _link,  " ...")
    page = html.parse(_link)
    result = process_table(page)
    if result != None:
        data.append(result)
    page_nums = page.xpath('//*[@id="results"]/div[2]/table[1]/tbody/tr/th[2]/div[2]/div/a')
    page_count += 1
    if len(page_nums) > 0 and (page_count<= 200): 
        _link = _link.split(".")
        if(page_count > 2):
            _link[-2]= "-".join(_link[-2].split("-")[:-1])
        _link[-2] += "-p{}".format(page_count)
        _link = ".".join(_link)
        process_link(_link, data)
    return data
        
if __name__ == "__main__":
    sumobrain = "http://www.sumobrain.com/"
    tree = html.parse(sumobrain)
    links = get_top_level_links(tree)
    patents = []
    for link in links[:]:
        page_count = 1
        results = process_link(link, []) 
        if results is not None:
            patents.extend(results)
    try:
        pd = __import__("pandas")
    except ImportError:
            import csv
            patents = [list(p) for p in set(frozenset(pat) for pat in patents)] # remove duplicates if any
            with open ("patents.csv", "w", encoding = "utf-8") as f:
                writer = csv.writer(f)
                for p in patents:
                    writer.writerow(p)
    else:
        patent_df = pd.DataFrame(data = patents, columns = ["PatentID", "URL"])
        patent_df.drop_duplicates(subset = "PatentID", inplace = True) # remove duplicates if any
        patent_df.to_csv("patents.csv", index_label="index")
