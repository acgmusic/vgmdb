import re

pattern_track = r"(\(|\[)?(M|([aA]ll\s)?[tT][rR][aA][cC][kK][sS]?|[dD]isc|DISC|#|\s|-|\.|,|#)*\d+" + \
                r"(\d|\sto\s|\s|\.|~|\(|\)|\[|\]|#|-|,)+"
pattern_disc = r"disc(\s|\.|-|\)|\]|#)*\d+"
pattern_semicolon = r":|："

patterns_credit = {
    'Composer': ['Composers', 'Composer', 'Composition', 'Composed by', 'Composed', 'Written by',
                 'Music by', r'^\s*Music\s*:'],
    'Arranger': ['Arrangers', 'Arranger', 'Arrangements', 'Arrangement', 'Arranged by', 'Arranged'],
    'Vocal': ['Vocal', 'Vocals', 'Singer', 'Singers'],
    'Lyrics': ['Lyricist', 'Lyricists', 'Lyrics', r'^\s*words\s*:'],
}


# Remove prefix and suffix matching chars
def rm_presuffix(pattern, text):
    ptn = f"[^('+({pattern})+')].*[^('+({pattern})+')]"
    match = re.search(ptn, text)
    if match is not None:
        return re.search(ptn, text).group()
    else:
        return ''


def split_by_re(pattern, text, mod="full", absolut_ptn_len=None, flags=None):
    """e.g.
    1.
    text = "x1 x2 x3",  pattern = r"x" , mod="prefix" , absolut_ptn_len=1  -> return:
    ["x1", "x2", "x3"]

    2.
    text = "x1 x2 x3",  pattern = r"x" , mod="full"  -> return:
    ["x", "1 ", "x", "2 ", "x", "3"]

    3.
    text = "x1 x2 x3",  pattern = r"x" , mod="suffix"  -> return:
    ["x", "1 x", "2 x", 3"]

    absolut_ptn_len: used only when mod="prefix". This param is your pattern's certain length, if you are not sure,
    you can set a rough number, but may cause come mistake.
    what's more, you can set: `flags=re.I` to match both uppercase and lowercase
    """
    assert mod in ["full", "prefix", "suffix"]
    if mod == "prefix":
        assert absolut_ptn_len is not None and 1 <= absolut_ptn_len <= len(
            text), "if you set `mod='prefix'`, you should also set param `absolut_ptn_len`"

    if flags is not None:
        rgx = re.compile(pattern, flags)
    else:
        rgx = re.compile(pattern)
    split_points = [0, ]
    n = len(text)
    while True:
        start = split_points[-1]
        if mod == "prefix" and len(split_points) > 1:
            start += absolut_ptn_len
        match = rgx.search(text[start:])

        if match:
            if mod == "prefix":
                split_points.append(match.span()[0] + start)
            elif mod == "suffix":
                split_points.append(match.span()[1] + start)
            elif mod == "full":
                split_points.append(match.span()[0] + start)
                split_points.append(match.span()[1] + start)
        else:
            break

    if len(split_points) > 1 and split_points[1] == 0:
        split_points = split_points[1:]
    if split_points[-1] != n:
        split_points.append(n)
    return [text[split_points[i]:split_points[i + 1]] for i in range(len(split_points) - 1)]


def get_credits(text):
    credits_ = []
    persons = []
    credit_last_match_pt = 0
    for credit in patterns_credit:
        flag = True
        for ptn in patterns_credit[credit]:
            if flag:
                rgx = re.compile(ptn, re.I)
                match = rgx.search(text)
                if match is not None:
                    credits_.append(credit)
                    flag = False
                    match_pt = match.span()[1]
                    credit_last_match_pt = max(credit_last_match_pt, match_pt)

    if credits_:
        # if there is semicolon, it's easy
        if re.search(pattern_semicolon, text) is not None:
            persons_maybe_text = re.split(pattern_semicolon, text, maxsplit=1)[1]
        # no semicolon, use `credit_last_match_pt`
        else:
            persons_maybe_text = text[credit_last_match_pt:]
    else:
        persons_maybe_text = text

    persons_maybe = re.split(r",|and|\\|\|", persons_maybe_text)
    for p in persons_maybe:
        person = rm_presuffix(r'\W|_', p)
        if person:
            persons.append(person)
    return [credits_, persons]


def get_disc(text):
    if re.search(pattern_disc, text) is not None:
        return int(re.search(r"\d+", text).group())
    return None


def get_tracks(text):
    tracks = []
    match = re.search(pattern_track, text)
    if match is not None and match.group() == text:
        text = re.sub(r"(?<=\d)\s*to\s*(?=\d)", '~', text)
        text = re.sub(r"(?<=\d)\s*-\s*(?=\d)", '~', text)
        text = re.sub(r"(?<=\d)\s*~\s*(?=\d)", '~', text)
        for num_str in re.split(r"[^0-9~]+", text):
            if num_str:
                if '~' in num_str:
                    num_str_split = num_str.split('~')
                    if len(num_str_split) == 2:
                        [start, end] = num_str_split
                        [start, end] = [int(start), int(end)]
                        tracks += list(range(start, end + 1))
                else:
                    tracks.append(int(num_str))
    return tracks


if __name__ == '__main__':
    print(split_by_re(pattern_track, "M. 01 3st"))
