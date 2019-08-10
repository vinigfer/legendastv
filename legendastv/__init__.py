from zipfile import ZipFile

import requests
from bs4 import BeautifulSoup


class LegendasTV:
    USER_AGENT_HEADER = {"user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"}

    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.session = None
        if not self._login():
            raise Exception("Login Failed")

    def _login(self):
        self.session = requests.Session()
        login_data = {"data[User][username]": self.user, "data[User][password]": self.password, "data[lembrar]": "on"}
        request = self.session.post("http://legendas.tv/login", data=login_data, headers=self.USER_AGENT_HEADER)

        # Verify and return if login was successful or not
        return f'"Meu Perfil">{self.user}</a>' in request.text

    def _request(self, url, method="GET", data=None):
        if self.session:
            if method == "GET":
                return self.session.get(url, stream=True, headers=self.USER_AGENT_HEADER)
            if method == "POST" and data:
                return self.session.post(url, data=data, headers=self.USER_AGENT_HEADER)
        else:
            raise Exception("Need session/login before hitting Legendas TV")

    def search(self, series_name, episode_code):
        """ 'series_name' can be any case insensitive string, while 'episode_code' need to indicate season and episode
        number. Ex: S03E18 indicates season 3, episode 18. """
        search_string = f"{series_name} {episode_code}"

        # int_idioma 1 = pt-br
        # selTipo 1 = release
        search_payload = {"txtLegenda": search_string, "int_idioma": 1, "selTipo": 1}
        url = f"http://legendas.tv/legenda/busca/{search_string}/1"
        request = self._request(url, method="POST", data=search_payload)
        return self._get_first_url((request.text).encode("utf-8"), series_name, episode_code)

    def _get_first_url(self, html_source_code, series_name, episode_code):
        parsed_html_code = BeautifulSoup(html_source_code, features="html.parser")
        existing_links = parsed_html_code.findAll("a")
        for current_link in existing_links:
            current_href = current_link.get("href")

            if current_href and episode_code in current_href:
                current_href = current_href.split("/")

                if series_name.upper().replace(" ", "_") == current_href[3].upper():
                    unique_id_download = current_href[2]
                    return f"http://legendas.tv/downloadarquivo/{unique_id_download}"

    def download(self, subtitle_url, file_absolute_path):
        request = self._request(subtitle_url, method="GET")
        if request:
            file_absolute_path_with_extension = f"{file_absolute_path}.zip"
            with open(file_absolute_path_with_extension, "wb") as file_handler:
                file_handler.write(request.content)

            # WIP: Only download subtitle if we have a match in file name
            # with ZipFile(file_absolute_path_with_extension, "r") as zip_file_reader:
            #     for file_name in zip_file_reader.namelist():
            #         print(file_name)
