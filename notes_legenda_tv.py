import requests
import json

URL_LOGIN = 'http://legendas.tv/login'
URL_DOWNLOAD = 'http://legendas.tv/downloadarquivo/58c449df8998e'
path_e_nome_do_arquivo = '/home/pi/legendas-tv-api/The Big Bang Theory S10E18'

session = requests.Session()
payload = {
    'data[User][username]': 'vini.g.fer',
    'data[User][password]': 'blackjack',
    'data[lembrar]': 'on',
}
headers = {
    'host': 'legendas.tv',
    'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.5',
    'accept-encoding': 'gzip, deflate',
    'referer': 'http://legendas.tv/',
    'connection': 'keep-alive',
    'upgrade-insecure-requests': '1',
    'content-type': 'application/x-www-form-urlencoded',
    'content-length': '112',
}
login_request = session.post(URL_LOGIN, data=payload, headers=headers)

if login_request.status_code == 200 and 'vini.g.fer' in str(login_request._content):
    print ('Success on login! - Looking for subtitles ...')
    download_header = {
        'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    }
    download_request = session.get(URL_DOWNLOAD, headers=download_header)
    if download_request.status_code == 200:
        with open(path_e_nome_do_arquivo + ".rar", 'wb') as handle:
            print (u'Baixando legenda:', download_request.url)
            handle.write(download_request._content)
