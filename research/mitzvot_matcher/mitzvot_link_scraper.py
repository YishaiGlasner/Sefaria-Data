# -*- coding: utf-8 -*-

import requests, codecs, json
import unicodecsv as csv
from bs4 import BeautifulSoup
from sefaria.model import *
import regex as re
from sources.functions import post_link
from data_utilities.util import getGematria, numToHeb,isGematria

def scrape_wiki():
    url = u"https://he.wikipedia.org/wiki/%D7%9E%D7%A0%D7%99%D7%99%D7%9F_%D7%94%D7%9E%D7%A6%D7%95%D7%95%D7%AA_%D7%A2%D7%9C_%D7%A4%D7%99_%D7%A1%D7%A4%D7%A8_%D7%94%D7%97%D7%99%D7%A0%D7%95%D7%9A"

    page = requests.get(url)
    soup_body = BeautifulSoup(page.text, "lxml")
    tables = soup_body.select(".mw-parser-output > table")

    pairs = []
    links = []

    for table in tables:
        table_tr = table.select("tr")
        for col in table_tr:
            pairs.append((col.contents[1].text.strip(), re.sub(u'</?td>', u'', col.contents[-1].text).strip()))

    for pair in pairs:
        if re.search(u'ספר|מספר', pair[0]):
            continue
        neg_pos = u"Negative Mitzvot" if re.search(u"לאו", pair[1]) else u'Positive Mitzvot'
        rambam = getGematria(re.sub(u'עשה|לאו', u'', pair[1]).strip())
        chinukh = getGematria(pair[0])
        print chinukh, rambam
        chinukh_simanlen = len(Ref(u'Sefer HaChinukh.{}'.format(chinukh)).all_segment_refs())
        print neg_pos
        link = ({"refs": [
            u'Sefer HaChinukh.{}.{}-{}'.format(chinukh, 1, chinukh_simanlen),
            u'Mishneh Torah, {}.{}'.format(neg_pos, rambam)
        ],
            "type": "Sifrei Mitzvot",
            "auto": True,
            "generated_by": "chinukh_rambam_sfm_linker"  # _sfm_linker what is this parametor intended to be?
        })
        print link['refs']
        links.append(link)
    return links

def scrape_daat(csvfilename, booknames):

    url = u"http://www.daat.ac.il/daat/mitsvot/tavla.asp"

    r = requests.get(url)
    soup_body = BeautifulSoup(r.content, "lxml")

    tables = soup_body.select("table")#("div > p")#("tr td > h2")

    rows = tables[1].find_all(border="1")[0].select("tr") # 616 first is the headers and two last aren't in Chinukh

    chinukh_smk = []
    for i, row in enumerate(rows):
        if not i:
            continue
        citation_column = rows[i].select("td")
        if re.search(u"\u05e8\u05d1\u05d9 \u05d9\u05e6\u05d7\u05e7 \u05de\u05e7\u05d5\u05e8\u05d1\u05d9\u05dc",citation_column[-1].text):
            smk_lst = re.findall(u'''\u05e8\u05d1\u05d9 \u05d9\u05e6\u05d7\u05e7 \u05de\u05e7\u05d5\u05e8\u05d1\u05d9\u05dc, \u05e1\u05e4\u05e8 \u05de\u05e6\u05d5\u05d5\u05ea \u05e7\u05d8\u05df(.*)''',citation_column[-1].text)
            chinukh_smk.append((i, smk_lst[-1]))

    row_dict ={}
    with open(u'{}.csv'.format(csvfilename), 'w') as csv_file:
        writer = csv.DictWriter(csv_file, booknames) #fieldnames = obj_list[0].keys())
        writer.writeheader()

        for pair in chinukh_smk:
            siman_chinukh = pair[0]
            siman_smk = pair[1]
            simanai_smk = siman_smk_exctractor(siman_smk)
            print siman_chinukh, simanai_smk
            row_dict[u"chinukh"] = siman_chinukh
            row_dict[u"smk"] = simanai_smk
            writer.writerow(row_dict)


def links_chinukh_smk(filename):
        links = []
        with open(filename, 'r') as csvfile:
            file_reader = csv.DictReader(csvfile)
            for i, row in enumerate(file_reader):
                if not row:
                    continue
                chinukh_simanlen = len(Ref(u'Sefer HaChinukh.{}'.format(row["chinukh"])).all_segment_refs())
                for smki in eval(row["smk"]):
                    smk_siman_len = len(Ref(u'Sefer Mitzvot Katan.{}'.format(smki)).all_segment_refs()) if len(Ref(u'Sefer Mitzvot Katan.{}'.format(smki)).all_segment_refs()) !=0 else 1
                    link = ({"refs": [
                        u'Sefer HaChinukh.{}.{}-{}'.format(row["chinukh"], 1, chinukh_simanlen),
                        u'Sefer Mitzvot Katan.{}.{}-{}'.format(smki, 1, smk_siman_len)
                    ],
                        "type": "Sifrei Mitzvot",
                        "auto": True,
                        "generated_by": "chinukh_rambam_sfm_linker"  # _sfm_linker what is this parametor intended to be?
                    })
                    print link['refs']
                    links.append(link)
        return links

def siman_smk_exctractor(smk_text):
    # smk_text = re.sub(u'סימן', u'', smk_text)
    split = re.split(u'\s', smk_text)
    simanim = []
    for word in split:
        if not word or word == u'סימן' or word == u'סעיף':
            continue
        word = re.sub(u"[;.,']", u"", word)
        if re.search(u'-', word):
            borders = re.search(u"(.*?)-(.*)", word)
            start = getGematria(borders.group(1))
            end = getGematria(borders.group(2))
            for siman in range(start, end+1):
                simanim.append(siman)
        if not is_hebrew_number(word):
            if not check_vav(word):
                # print smk_text, simanim
                return simanim
            else:
                simanim.append(check_vav(word))
        else:
            smk_siman = getGematria(word)
            simanim.append(smk_siman)
    # print smk_text, simanim
    return simanim

def check_vav(st):
    if not st:
        return False
    if st[0] == u'ו':
        if is_hebrew_number(st[1:]):
            return getGematria(st[1:])
        else:
            return False
    return False

def is_hebrew_number(st):
    matches = re.findall(hebrew_number_regex(), st)
    if len(matches) == 0:
        return False
    return matches[0] == st


def hebrew_number_regex():
    """
    Regular expression component to capture a number expressed in Hebrew letters
    :return string:
    \p{Hebrew} ~= [\u05d0–\u05ea]
    """
    rx = ur"""                                    # 1 of 3 styles:
    ((?=[\u05d0-\u05ea]+(?:"|\u05f4|'')[\u05d0-\u05ea])    # (1: ") Lookahead:  At least one letter, followed by double-quote, two single quotes, or gershayim, followed by  one letter
            \u05ea*(?:"|\u05f4|'')?                    # Many Tavs (400), maybe dbl quote
            [\u05e7-\u05ea]?(?:"|\u05f4|'')?        # One or zero kuf-tav (100-400), maybe dbl quote
            [\u05d8-\u05e6]?(?:"|\u05f4|'')?        # One or zero tet-tzaddi (9-90), maybe dbl quote
            [\u05d0-\u05d8]?                        # One or zero alef-tet (1-9)                                                            #
        |[\u05d0-\u05ea]['\u05f3]                    # (2: ') single letter, followed by a single quote or geresh
        |(?=[\u05d0-\u05ea])                        # (3: no punc) Lookahead: at least one Hebrew letter
            \u05ea*                                    # Many Tavs (400)
            [\u05e7-\u05ea]?                        # One or zero kuf-tav (100-400)
            [\u05d8-\u05e6]?                        # One or zero tet-tzaddi (9-90)
            [\u05d0-\u05d8]?                        # One or zero alef-tet (1-9)
    )"""

    return re.compile(rx, re.VERBOSE)



if __name__ == "__main__":
    # rambam_chinukh_lnks = scrape_wiki()
    # post_link(rambam_chinukh_lnks, VERBOSE=True)
    # scrape_daat(u"smk_chinukh", [u"chinukh", u"smk"])
    links_ch_smk = links_chinukh_smk(u"smk_chinukh.csv")
    post_link(links_ch_smk, VERBOSE=True)


