import requests
from bs4 import BeautifulSoup

def download_file(url, data):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.post(url, stream=True, data=data)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian
    return local_filename

url = 'http://120.126.138.196/idb/UnUseLandQueryResult.aspx?city=K&ipark=0'
html = requests.post(url, stream=True).text
soup = BeautifulSoup(html, "lxml")
try:
    viewState = soup.find('input', {'id': '__VIEWSTATE'}).get('value')
    eventValidation = soup.find('input', {'id': '__EVENTVALIDATION'}).get('value')
    btnExport = soup.find('input', {'id': 'btnExport'}).get('value')
    print(viewState, eventValidation, btnExport)
    r = download_file(url, {
        '__VIEWSTATE': viewState,
        '__EVENTVALIDATION': eventValidation,
        'btnExport': btnExport
    })
    print(r)
except:
    pass
