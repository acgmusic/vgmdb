import warnings
from pyvgmdb.re_tools import *
import re


class Notes:
    def __init__(self, album_info):
        self.album_id = album_info['album_id']
        self.note_text = album_info['album_notes'].replace('&#160;', '').replace('&', ',')
        self.track_list = album_info['track_list_info'][0]['track_list']
        self.disc_num = len(self.track_list)
        self.album_note_parse = self.initAlbumNoteParser()
        self.parse()

    def initAlbumNoteParser(self):
        return [
            [
                {key: None for key in patterns_credit.keys()}
                for _ in range(len(self.track_list[disc]['disc_track_list']))
            ]
            for disc in range(self.disc_num)
        ]

    # write in album_note_parse
    def update(self, disc, credits_, tracks):
        for t in tracks:
            for c in credits_[0]:
                if disc <= self.disc_num and t <= len(self.album_note_parse[disc - 1]):
                    self.album_note_parse[disc - 1][t - 1][c] = credits_[1]
                else:
                    warnings.warn(f"disc num or track num index out of range in album "
                                  f"with id {self.album_id}")

    def parse(self):
        # not initialized
        cur_disc = 1

        # initialized every line
        cur_credits = [[], []]
        cur_tracks = []

        for item in self.note_text.split("<br /><br />"):
            line = []
            for text in re.split('<br />', item):
                text = text.replace('/', ',')
                text = re.sub(r"\d+(?=[a-zA-Z])", "", text)
                for _ in split_by_re(pattern_track, text, "full"):
                    line += split_by_re(pattern_disc, _, mod="full", flags=re.I)
            for text in line:
                tmp_disc = get_disc(text)
                if tmp_disc is None:
                    tmp_tracks = get_tracks(text)
                    if tmp_tracks:
                        tmp_credits = [[], []]
                    else:
                        tmp_credits = get_credits(text)
                else:
                    tmp_tracks = []
                    tmp_credits = [[], []]

                if tmp_disc is not None:
                    cur_disc = tmp_disc
                elif tmp_tracks:
                    cur_tracks = tmp_tracks
                    if cur_credits[0] and cur_credits[1]:
                        self.update(cur_disc, cur_credits, cur_tracks)
                        cur_credits[1] = []
                        cur_tracks = []
                    elif cur_credits[0] or cur_credits[1]:
                        warnings.warn(f"there is a new mod in album notes, "
                                      f"see details in album with id {self.album_id}")
                elif tmp_credits[0] and tmp_credits[1]:
                    cur_credits = tmp_credits
                    if cur_tracks:
                        self.update(cur_disc, cur_credits, cur_tracks)
                        cur_credits = [[], []]
                elif tmp_credits[0]:
                    cur_credits = tmp_credits
                elif tmp_credits[1]:
                    if cur_credits[0] and cur_tracks:
                        cur_credits[1] = tmp_credits[1]
                        self.update(cur_disc, cur_credits, cur_tracks)
                        cur_credits = [[], []]
                    elif cur_credits[0]:
                        cur_credits[1] = tmp_credits[1]
            cur_credits = [[], []]
            cur_tracks = []
