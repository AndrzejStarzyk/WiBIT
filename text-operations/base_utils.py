from bs4 import BeautifulSoup
import pandas as pd
import json

categories_dict = {'Koła widokowe': 'ferris_wheels',
                   'Areny sportów zimowych': 'winter_sports',
                   'Świątynie hinduizmu': 'hindu_temples',
                   'Obiekty archeologiczne': 'archaeology',
                   'Kopce/kurchany': 'tumuluses',
                   'Muzea biograficzne': 'biographical_museums',
                   'Muzea modowe': 'fashion_museums',
                   'Parki rozrywki': 'amusement_parks',
                   'Parki wodne': 'water_parks',
                   'Parki miniatur': 'miniature_parks',
                   'Baseny, termy i sauny': 'baths_and_saunas',
                   'Ścianki wspinaczkowe': 'climbing',
                   'Stadiony': 'stadiums',
                   'Źródła': 'natural_springs',
                   'Rzeki, kanały, wodospady': 'water',
                   'Rezerwaty przyrody': 'nature_reserves',
                   'Plaże': 'beaches',
                   'Stacje kolejowe': 'railway_stations',
                   'Zapory': 'dams',
                   'Mennice': 'mints',
                   'Kopalnie': 'mineshafts',
                   'Muzea nauki i techniki': 'science_museums',
                   'Kościoły': 'churches',
                   'Katedry': 'cathedrals',
                   'Klasztory': 'monasteries',
                   'Synagogi': 'synagogues',
                   'Meczety': 'mosques',
                   'Zamki': 'castles',
                   'Wieże obronne': 'fortified_towers',
                   'Bunkry': 'bunkers',
                   'Muzea militarne': 'military_museums',
                   'Pola bitew': 'battlefields',
                   'Cmentarze wojenne': 'war_graves',
                   'Cmentarze': 'cemeteries',
                   'Mauzolea': 'mausoleums',
                   'Krypty': 'crypts',
                   'Murale': 'wall_painting',
                   'Fontanny': 'fountains',
                   'Rzeźby': 'sculptures',
                   'Zieleń miejska': 'gardens_and_parks',
                   'Muzea archeologiczne': 'archaeological_museums',
                   'Galerie sztuki': 'art_galleries',
                   'Muzea historyczne': 'history_museums',
                   'Muzea lokalne': 'local_museums',
                   'Muzea narodowe': 'national_museums',
                   'Planetaria': 'planetariums',
                   'Zoo': 'zoos',
                   'Akwaria': 'aquariums',
                   'Drapacze chmur': 'skyscrapers',
                   'Wieże (zegarowe, widokowe)': 'towers',
                   'Budynki historyczne': 'historic_architecture',
                   'Mosty': 'bridges',
                   'Pomniki': 'monuments'}


def read_form_result(csv_path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df = df.drop(df.columns[-6:], axis=1)
    df = df.drop(df.columns[0], axis=1)
    cols = df.columns

    new_col_names = ['text', 'date']
    new_col_names_cat = [col.split('[')[-1][:-1] for col in cols[2:]]
    new_col_names += new_col_names_cat
    df.columns = [categories_dict[cat] if cat in categories_dict else cat for cat in new_col_names]

    return df


def read_chat_html(html_path) -> pd.DataFrame:
    f = open(html_path, "r")
    content = f.read()
    soup = BeautifulSoup(content, 'html.parser')

    pref_jsons = []
    code_tags = soup.find_all('code')
    for code_tag in code_tags:
        pref_jsons.append(code_tag.get_text())

    pref_jsons_formatted = []

    for tmp_json in pref_jsons:
        pref_jsons_formatted.append(tmp_json.replace('\n', ''))

    keys = ['text', 'date'] + list(json.loads(pref_jsons_formatted[0])['Miejsca'].keys())
    prefs_dict_df = {cat_key: [] for cat_key in keys}

    for tmp_json in pref_jsons_formatted:
        pref_dict = json.loads(tmp_json)
        prefs_dict_df['text'].append(pref_dict['Preferencje']['Opis'])
        prefs_dict_df['date'].append(pref_dict['Termin']['Data'])

        for place_cat in pref_dict['Miejsca'].keys():
            prefs_dict_df[place_cat].append(pref_dict['Miejsca'][place_cat])

    df = pd.DataFrame.from_dict(prefs_dict_df)
    df.columns = [categories_dict[cat] if cat in categories_dict else cat for cat in df.columns]

    return df


# print(read_form_result('./files/wibit_form.csv'))

# df = read_chat_html('./files/chat_example.html')
# print(df)
# df.to_csv('./files/chat_example.csv')
