main_xpaths_dict = {
    'xpath': '',

    # artist
    'artist_name_en': {'xpath': '//*[@id="innermain"]/span[2]/text()'},
    'artist_sex': {'xpath': '//*[@id="leftfloat"]/img/@alt'},
    'artist_name_jp': {'xpath': '//*[@id="leftfloat"]/span/text()'},
    'artist_img_url': {'xpath': '//*[@id="leftfloat"]/div[1]/a/@href'},
    'artist_left_bar': {'xpath': '//*[@id="leftfloat"]/div'},
    'artist_Notes': {'xpath': '//*[@id="rightfloat"]/div[2]/div/text()'},
    'artist_discography': {
        'xpath': '//*[@id="discotable"]/table/tbody',
        'year': {'xpath': './/h3[@class="time"]/text()'},
        # note: list index start from 1
        'tr': {
            'xpath': './tr',
            'date': {'xpath': './/td[@class="label"]/text()'},
            'album_title': {'xpath': './/a[contains(@class,"albumtitle")]/@title'},
            'album_url': {'xpath': './/a[contains(@class,"albumtitle")]/@href'},
            # 'serve_as' is a list, like: ['Composer', 'Arranger']
            'serve_as': {'xpath': './/span[contains(@class,"smallfont") and contains(@class,"label")]//text()'},
        }
    },

    # album
    'album_name_en': {'xpath': '//*[@id="innermain"]/h1/span[@lang="en"]/text()'},
    'album_name_ja': {'xpath': '//*[@id="innermain"]/h1/span[@lang="ja"]/text()'},
    'album_name_ja_latn': {'xpath': '//*[@id="innermain"]/h1/span[@lang="ja-Latn"]/text()'},
    'album_info_tr': {'xpath': '//div[@id="rightfloat"]//table[@id="album_infobit_large"]//tr'},
    'album_credits': {'xpath': '//div[@id="collapse_credits"]//table[@id="album_infobit_large"]//tr'},
    'track_list_span': {'xpath': '//*[@id="tracklist"]/span'},
}
