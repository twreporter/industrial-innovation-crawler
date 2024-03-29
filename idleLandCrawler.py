import asyncio
import requests
import time
import os
import pandas as pd
from bs4 import BeautifulSoup

COUNTY_URL = 'http://120.126.138.196/idb/LandSaleQuery.aspx'
IDLE_LAND_URL = 'http://120.126.138.196/idb/UnUseLandQueryResult.aspx?ipark=0&city='
FOLDER_PATH_NAME = 'idle_industrial_land'
DATE = time.strftime('%Y%m%d')

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

def download_file(url, data, countyID, countyName):
    filename = 'data/' + FOLDER_PATH_NAME + '/' + DATE + '/' + countyID + '_' + countyName
    filepath = filename+'.xls'
    remote_filename = url.split('/')[-1]
    r = requests.post(url, stream=True, data=data)
    # check if the directory exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    # download the xls file
    with open(filepath, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    sheet = pd.read_excel(filepath, skiprows=1)
    if not sheet.empty:
        sheet = sheet.assign(county_id=countyID, county_name=countyName)
    print(sheet.shape)
    return sheet

def moveColumnToBeginning(df, colName):
    col = dframe[colName]
    df.drop(labels=[colName], axis=1, inplace = True)
    df.insert(0, colName, col)
    return df

def writeExcel(df, filepath):
    # check if the directory exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    writer = pd.ExcelWriter(filepath + '.xls')
    dframe.to_excel(writer, 'Sheet1')
    writer.save()

def writeCSV(df, filepath):
    filepath = filepath + '.csv'
    # check if the directory exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False, encoding='utf-8')


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
        sheet = download_file(url, {
            '__VIEWSTATE': viewState,
            '__EVENTVALIDATION': eventValidation,
            'btnExport': btnExport
        }, key, counties[key])

        # parse the downloaded data
        if not sheet.empty:
            allData.append(sheet)
    except:
        pass

print(allData)
dframe = pd.concat(allData)
print(dframe)

# Save Excel file
dframe = moveColumnToBeginning(dframe, 'county_name')
dframe = moveColumnToBeginning(dframe, 'county_id')
path1 = 'latest_data/' + FOLDER_PATH_NAME
path2 = 'data/' + FOLDER_PATH_NAME + '/' + DATE
writeExcel(dframe, path1)
writeCSV(dframe, path1)
writeExcel(dframe, path2)
writeCSV(dframe, path2)
