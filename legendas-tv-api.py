#!/usr/bin/env python
#-*- encoding: utf-8 -*-
from BeautifulSoup import BeautifulSoup
import requests
import sys


class Legenda(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return u'%s (%s)' % (self.title, self.title_ptbr)

    @property
    def download(self):
        if self.id:
            return LegendasTV.URL_DOWNLOAD % self.id
        else: pass # raise exception


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
        'all':   99 
    }
    LEGENDA_TIPO = { 
        'release': 1,
        'filme':   2,
        'usuario': 3 
    }


    def __init__(self, usuario, senha):
        self.usuario = usuario
        self.senha = senha
        self.session = None
        self._login()


    def _login(self):
        s = requests.Session()
        url = self.URL_LOGIN
        payload = {
            'data[User][username]': self.usuario,
            'data[User][password]': self.senha,
            'data[lembrar]': 'on'
        }
        headers = {'content-type': 'form-data',
                   'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
        r = s.post(url, payload, headers=headers)
        html = r.content

        if "<title>Login - Legendas TV</title>" in html:
            return False
        else:
            print 'Success on login! - Looking for subtitles ...'
            self.session = s
            return True


    def _request(self, url, method='GET', data=None):
        if self.session:
            if method == 'GET':
                r = self.session.get(url, stream=True)
            if method == 'POST' and data:
                r = self.session.post(url, data=data)

            return r
        else:
            raise Exception("Error: No session established.")


#    def _parser(self, data):
#        legendas = []

#        html = BeautifulSoup(data)
#        results = html.find(id='conteudodest').findAll('span') # TODO: Pagination
#        for result in results:
#            meta = self.LEGENDA_REGEX.search(unicode(result))
#            if meta:
#                legenda = Legenda(**meta.groupdict())
#                legendas.append(legenda)
#            else: pass # raise exception

#        legendas = sorted(legendas, key=lambda k: int(k.downloads), reverse=True)
#        return legendas


    def _parser(self, data, series_name, episode_code):
        legendas = []
        html = BeautifulSoup(data)
        results = html.findAll("a")
        for result in results:
            if result.get("href") is not None:
                path_href = result.get("href").split("/")

                if episode_code in result.get("href") and series_name.replace(" ","_") == path_href[3]:
                    print result
                    unique_id_download = path_href[2]
                    url = self.URL_DOWNLOAD % unique_id_download
                    return url


    def search(self, serie_or_movie_name, episode_code='', lang='pt-br', tipo='release'):
        search_string = serie_or_movie_name
        if episode_code is not None:
            search_string += " " + episode_code

        if not search_string:
            raise Exception("Error: No search string supplied.")
        if not lang or not self.LEGENDA_LANG.get(lang):
            raise Exception("Error: No lnaguage supplied.")
        if not tipo or not self.LEGENDA_TIPO.get(tipo):
            raise Exception("Error: No subtitle type supplied.")

        busca = { 
            'txtLegenda': search_string,
            'int_idioma': self.LEGENDA_LANG[lang],
            'selTipo':    self.LEGENDA_TIPO[tipo] 
        }
        request = self._request(self.URL_BUSCA % search_string, method='POST', data=busca)
        if request:
            return self._parser(request.text, serie_or_movie_name, episode_code)
        else:
            raise Exception("Error: Invalid or no response for query.")


    def download(self, url_da_legenda, path_e_nome_do_arquivo):
        request = self._request(url_da_legenda)
        if request:
            with open(path_e_nome_do_arquivo + ".rar", 'wb') as handle:
                print u'Baixando legenda:', url_da_legenda
                print ""
                handle.write(request.content)


#    def download(self, legenda, output):
#        if not legenda and isinstance(legenda, Legenda):
#            pass # raise exception

#        if not output:
#            pass # raise exception
        
#        r = self._request(legenda.download)
#        if r:
#            filename = r.url.split('/')[-1] # FIX
#            path = output + filename
#            with open(path, 'wb') as handle:
#	        print u'Baixando legenda:', legenda
#                handle.write(r.content)


def main():
    q = sys.argv[1]	 # Query
    output = sys.argv[2] # FIX /

    # Auth
    ltv = LegendasTV('usuário', 'senha')

    # Search
    print '\t[ downloads ]\t\t[ filename ]'
    i = 0
    legendas = ltv.search(q)
    for legenda in legendas:
        print '(%d)\t%s\t\t\t%s' % (i+1, legenda.downloads, legenda.filename) # FIX +1
        i += 1
    print

    # Download
    opt = int(raw_input('Escolha a legenda para baixar: '))-1 # FIX -1
    if legendas[opt]:
        ltv.download(legendas[opt], output)
    else: pass # raise exception

if __name__ == '__main__':
    main()

