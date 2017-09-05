import requests
import time
import os
import pandas as pd
from bs4 import BeautifulSoup

COUNTY_URL = 'http://120.126.138.196/idb/LandSaleQuery.aspx'
IDLE_LAND_URL = 'http://120.126.138.196/idb/UnUseLandQueryResult.aspx?ipark=0&city='

def get_counties_cities(url):
    r = requests.get(url).text
    soup = BeautifulSoup(r, "lxml")
    subject_options = soup.select('select[name=ddlCity] > option')
    dict = {}
    for opt in subject_options:
        if opt['value']:
            dict[opt['value']] = opt.text
    print(dict)
    return dict

def download_file(url, data, filename):
    filepath = filename+'.xls'
    remote_filename = url.split('/')[-1]
    r = requests.post(url, stream=True, data=data)
    # check if the directory exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    # download the xls file
    with open(filepath, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    sheet = pd.read_excel(filepath, header=None)
    print(sheet.shape)
    return sheet


# First get countites and cities
counties = get_counties_cities(COUNTY_URL)

# Get data from all counties and cities
allData = []
for key in counties:
    url = IDLE_LAND_URL + key
    print(url)
    html = requests.post(url, stream=True).text
    soup = BeautifulSoup(html, "lxml")
    try:
        # download the data of each county or city
        viewState = soup.find('input', {'id': '__VIEWSTATE'}).get('value')
        eventValidation = soup.find('input', {'id': '__EVENTVALIDATION'}).get('value')
        btnExport = soup.find('input', {'id': 'btnExport'}).get('value')
        filename = 'data/' + time.strftime('%Y%m%d') + '/' + key + '_' + counties[key]
        sheet = download_file(url, {
            '__VIEWSTATE': viewState,
            '__EVENTVALIDATION': eventValidation,
            'btnExport': btnExport
        }, filename)

        # parse the downloaded data
        if not sheet.empty:
            allData.append(sheet)
    except:
        pass

print(allData)
dframe = pd.concat(allData)
print(dframe)

# Save Excel file
writer = pd.ExcelWriter('output.xls')
dframe.to_excel(writer,'Sheet1')
writer.save()
