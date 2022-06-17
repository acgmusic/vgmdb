import requests
from pyvgmdb.utils import SafeEtree
from lxml import etree
import warnings


class Artist:
    def __init__(self, artist_id, proxies=None, headers=None):
        """
        :param artist_id: e.g. 9621, then we will parse: https://vgmdb.net/artist/9621
        :param proxies: if you need proxies to visit https://vgmdb.net, please set this param
        :param headers: not necessary
        """
        self.artist_id = str(artist_id)
        self.homepage_url = "https://vgmdb.net/artist/" + self.artist_id
        self.proxies = {'http': f'http://127.0.0.1:{proxies}', 'https': f'http://127.0.0.1:{proxies}'}
        self.headers = headers
        self.tree = self.getPageEtree()
        self.albums = self.getDiscography() if self.tree is not None else None

    def getPageEtree(self):
        args = {'url': self.homepage_url}
        if self.proxies:
            args['proxies'] = self.proxies
        if self.headers:
            args['headers'] = self.headers
        response = requests.get(**args)
        page_text = response.text
        if response.status_code == 404 or "Artist not found" in page_text:
            warnings.warn(f"can not find artist with id {self.artist_id}")
            return
        if "No albums found" in "".join(etree.HTML(page_text).xpath('//*[@id="albumlist"]/div[1]//text()')):
            warnings.warn(f"artist with id {self.artist_id} maybe have no album, please check again")
            return

        tree = SafeEtree(etree.HTML(page_text))
        return tree

    def getDiscography(self):
        discography_list = self.tree.xpath('artist_discography', final=False)
        albums_all = []
        for discography in discography_list:
            albums_in_one_year = []
            year = discography.xpath('year')[0]
            tr_list = discography.xpath('tr', final=False)
            for i, tr in enumerate(tr_list):
                # first tr element is the year
                if i == 0:
                    continue
                date = tr.xpath('date')[0]
                album_title = tr.xpath('album_title')[0]
                album_url = tr.xpath('album_url')[0]
                # TODO: 'serve_as' list pretreatment
                serve_as = tr.xpath('serve_as')
                albums_in_one_year.append({
                    'date': date,
                    'album_title': album_title,
                    'album_url': album_url,
                    'serve_as': serve_as,
                })
            albums_all.append({'year': year, 'albums': albums_in_one_year, })
        return albums_all

    def get_albums_url_list(self):
        url_list = []
        for albums_in_one_year in self.albums:
            for album in albums_in_one_year['albums']:
                url_list.append(album['album_url'])
        return url_list

    def downloadPortrait(self, fp):
        """TODO"""

    def getBasicInfo(self):
        """TODO"""
