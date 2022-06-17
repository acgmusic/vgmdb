from pyvgmdb.utils import SafeEtree
from pyvgmdb.notes import Notes
import requests
from lxml import etree
import warnings
import os
import re


class Album:
    def __init__(self, album_id, proxies=None, headers=None):
        """
        :param album_id: e.g. 25781, then we will parse: https://vgmdb.net/album/25781
        :param proxies: if you need proxies to visit https://vgmdb.net, please set this param
        :param headers: not necessary
        """
        self.album_id = str(album_id)
        if int(album_id) > 0:
            self.album_url = "https://vgmdb.net/album/" + self.album_id
            self.proxies = {'http': f'http://127.0.0.1:{proxies}', 'https': f'http://127.0.0.1:{proxies}'}
            self.headers = headers
            self.tree, self.page_text = self.getPageEtree()
            if self.tree is not None:
                self.album_info = {
                    'album_id': self.album_id,
                    'album_basic_info': self.getAlbumBasicInfo(),
                    'album_credits': self.getCredits(),
                    'track_list_info': self.getTrackList(),
                    'album_notes': self.getNotes(),
                }
                if self.album_info['track_list_info']:
                    self.parseNotes()

    def getPageEtree(self):
        args = {'url': self.album_url}
        if self.proxies:
            args['proxies'] = self.proxies
        if self.headers:
            args['headers'] = self.headers
        response = requests.get(**args)
        page_text = response.text
        if response.status_code == 404 or "This album could not be displayed" in page_text:
            warnings.warn(f"can not find album with id {self.album_id}")
            return None, None
        tree = SafeEtree(etree.HTML(page_text))
        return tree, page_text

    def getAlbumBasicInfo(self):
        album_basic_info = {
            'album_name_en': self.tree.xpath('album_name_en')[0],
            'album_name_ja': self.tree.xpath('album_name_ja')[0],
            'album_name_ja_latn': self.tree.xpath('album_name_ja_latn')[0],
        }
        album_info_tr = self.tree.xpath('album_info_tr')
        for tr in album_info_tr:
            key_name_td_list = tr.xpath('./td')
            if key_name_td_list:
                key_name = key_name_td_list[0].xpath('.//text()')[0]
                if len(tr.xpath('./td')) >= 2:
                    album_basic_info[key_name] = tr.xpath('./td')[1].xpath('.//text()')
        if len(album_basic_info) == 0:
            warnings.warn(f"can not find any basic info in album with id {self.album_id}")
        return album_basic_info

    def getCredits(self):
        album_credits = {}
        if "collapse_credits" not in self.page_text:
            warnings.warn(f"can not find Credits info in album with id {self.album_id}")
            return album_credits
        for tr in self.tree.xpath('album_credits'):
            key_name = tr.xpath('./td')[0].xpath('.//span[@lang="en"]/text()')[0]
            album_credits[key_name] = []
            # person with no href
            if tr.xpath('./td')[1].xpath('./text()'):
                album_credits[key_name].append(tr.xpath('./td')[1].xpath('./text()')[0])
            # person with href
            for a in tr.xpath('./td')[1].xpath('./a'):
                href = a.xpath('./@href')[0]
                artist_id = str(href).split('/')[-1]
                # person with only en name
                if a.xpath('./text()'):
                    name = a.xpath('./text()')[0]
                    album_credits[key_name].append({'name': name, 'artist_id': artist_id})
                # person with many types of name
                elif a.xpath('./span[@lang="en"]/text()'):
                    name = a.xpath('./span[@lang="en"]/text()')[0]
                    album_credits[key_name].append({'name': name, 'artist_id': artist_id})
                else:
                    raise Exception(f"can not find name of person who is {key_name} "
                                    f"in album with id {self.album_id}")
        return album_credits

    def getTrackList(self):
        album_track_list_info = []
        if "No tracklist found" in "".join(self.tree.etree.xpath('//*[@id="tracklist"]//text()')):
            warnings.warn(f"No tracklist found in album with id {self.album_id}")
            return album_track_list_info
        for span in self.tree.xpath('track_list_span'):
            tl_id = span.xpath('./@id')[0]
            try:
                lang = self.tree.etree.xpath(f'//*[@id="tlnav"]/li/a[@rel="{tl_id}"]/text()')[0]
            except IndexError:
                raise Exception(f"can not find language type of track_list in album with id {self.album_id}")
            disc_name_list = span.xpath('./span/b/text()')
            disc_info_list = span.xpath('./table')
            assert len(disc_name_list) == len(disc_info_list), f"num of disc is not sure, " \
                                                               f"we find following disc names: {disc_name_list}" \
                                                               f"but there are {len(disc_info_list)} disc info tables" \
                                                               f"please check album with id {self.album_id}"
            # for num of disc
            album_tl_info = {
                'info_language': lang,
                'track_list': [],
            }
            for disc_name, tb in zip(disc_name_list, disc_info_list):
                disc_track_list = {
                    'disc_name': disc_name,
                    'disc_track_list': [],
                }
                for tr in tb.xpath('./tr[@class="rolebit"]'):
                    name = tr.xpath('./td[2]/text()')[0]
                    name = name.replace('\n', '').replace('\r', '').replace('\t', '')
                    song_length_text = tr.xpath('./td[3]/span[@class="time"]/text()')
                    if song_length_text:
                        song_length = song_length_text[0]
                    else:
                        song_length = None
                    disc_track_list['disc_track_list'].append({'name': name, 'time': song_length})
                album_tl_info['track_list'].append(disc_track_list)
            album_track_list_info.append(album_tl_info)
        return album_track_list_info

    def getNotes(self):
        match = re.search(r'(?<=\sid="notes">).*?(?=</div>)', self.page_text)
        if match is None:
            warnings.warn(f"no note found in album with id {self.album_id}")
            return
        else:
            return match.group()

    def parseNotes(self):
        note = Notes(self.album_info)
        self.album_info['album_parsed_notes'] = note.album_note_parse

    def save(self, fp):
        with open(os.path.join(fp + str(self.album_id) + ".json"), 'w', encoding="utf-8") as fs:
            fs.write(json.dumps(self.album_info))


if __name__ == '__main__':

    import numpy as np
    import time
    import json

    test_id = list(range(40000, 100000))
    np.random.shuffle(test_id)
    bad_example = []
    for k in bad_example:
        print("current album id：", k)
        Album(k, proxies=7890).save("./test_note/")
        time.sleep(12)

    for k in test_id[:30]:
        if k in bad_example:
            continue
        print("current album id：", k)
        try:
            Album(k, proxies=7890).save("./test_note/")
            print("album id", k, "success")
        except Exception:
            bad_example.append(k)
            print(":( "*20)
            print("album id", k, "failure!")
        time.sleep(8 + np.random.randint(10))
    print(bad_example)
