import requests
from bs4 import BeautifulSoup
from zipfile import ZipFile


class LegendasTV(object):
    URL_BUSCA = 'http://legendas.tv/legenda/busca/%s/1'
    URL_DOWNLOAD = 'http://legendas.tv/downloadarquivo/%s'
    URL_LOGIN = 'http://legendas.tv/login'
    LEGENDA_LANG = {
        'pt-br': 1,
        'pt':    10,
        'en':    2,
        'es':    3,
        'other': 100,
        'all':   99,
    }
    LEGENDA_TIPO = {
        'release': 1,
        'filme':   2,
        'usuario': 3,
    }

    def __init__(self, usuario, senha):
        self.usuario = usuario
        self.senha = senha
        self.session = None
        self._login()

    def _login(self):
        session = requests.Session()
        payload = {
            'data[User][username]': self.usuario,
            'data[User][password]': self.senha,
            'data[lembrar]': 'on'
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
        request = session.post(self.URL_LOGIN, data=payload, headers=headers)
        html_code = str(request._content)

        if self.usuario not in html_code:
            print('Login failed')
            return False
        else:
            self.session = session
            return True

    def _request(self, url, method='GET', data=None, headers=None):
        if self.session:
            if method == 'GET':
                return self.session.get(url, stream=True, headers=headers)
            if method == 'POST' and data:
                return self.session.post(url, data=data, headers=headers)
        else:
            pass  # raise exception

    def search(self, series_name, episode_code, lang='pt-br', tipo='release'):
        q = series_name + " " + episode_code
        if not q:
            pass  # raise exception

        if not lang or not self.LEGENDA_LANG.get(lang):
            pass  # raise exception

        if not tipo or not self.LEGENDA_TIPO.get(tipo):
            pass  # raise exception

        busca = {
            'txtLegenda': q,
            'int_idioma': self.LEGENDA_LANG[lang],
            'selTipo': self.LEGENDA_TIPO[tipo],
        }
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }
        request = self._request(self.URL_BUSCA % q, method='POST', data=busca, headers=headers)
        if request:
            return self._parser((request.text).encode("utf-8"), series_name, episode_code)
        else:
            pass  # raise exception

    def _parser(self, data, series_name, episode_code):
        html = BeautifulSoup(data, features="html.parser")
        results = html.findAll("a")
        for result in results:
            if result.get("href") is not None:
                path_href = result.get("href").split("/")

                if episode_code in result.get("href") and series_name.upper().replace(" ", "_") == path_href[3].upper():
                    unique_id_download = path_href[2]
                    url = self.URL_DOWNLOAD % unique_id_download
                    return url

    def download(self, url_legenda, file_absolute_path, video_name=None):
        download_header = {
            'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
        }
        request = self._request(url_legenda, method='GET', headers=download_header)
        if request:
            file_absolute_path_with_extension = file_absolute_path + ".zip"
            with open(file_absolute_path_with_extension, 'wb') as handle:
                handle.write(request.content)

            with ZipFile(file_absolute_path_with_extension, 'r') as zip_file:
                for name in zip_file.namelist():
                    print('%s' % (name))
