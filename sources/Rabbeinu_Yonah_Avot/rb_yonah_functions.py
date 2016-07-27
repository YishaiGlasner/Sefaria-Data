# -*- coding: utf-8 -*-
import codecs
import regex
from sefaria.model import *
from sources import functions
from data_utilities import util
# from sources.Match import match_new
from sources.Match.match import Match
from sefaria.model.schema import AddressTalmud, SchemaNode, JaggedArrayNode
from fuzzywuzzy import fuzz
import urllib
import urllib2
from urllib2 import URLError, HTTPError
import json
import pdb
import os
import sys


def create_index():
    rabbeinu_yonah_schema = create_schema()
    rabbeinu_yonah_schema.validate()
    index = {
        "title": "Rabbeinu Yonah on Pirkei Avot",
        "categories": ["Commentary2", "Pirkei Avot", "Rabbeinu Yonah"],
        "schema": rabbeinu_yonah_schema.serialize()
    }
    return index

def create_schema():
    rb_schema = JaggedArrayNode()
    rb_schema.add_title('Rabbeinu Yonah on Pirkei Avot', 'en', primary=True)
    rb_schema.add_title(u'רבינו יונה על פרקי אבות', 'he', primary=True)
    rb_schema.key = 'Rabbeinu Yonah on Pirkei Avot'
    rb_schema.depth = 2
    rb_schema.addressTypes = ["Integer", "Integer"]
    rb_schema.sectionNames = ["Perek", "Mishna"]
    return rb_schema


def parse_and_post(file_name):
    mishna_number_regex = regex.compile(u'([\u05d0-\u05ea]{1,3})')
    rb_yonah_on_avot, perek_level_list = [], []
    new_perek, first_perek = True, True
    last_mishna = 0
    with codecs.open(file_name, 'r', 'utf-8') as the_file:
        for each_line in the_file:

            if "@00" in each_line:
                if not first_perek:
                    rb_yonah_on_avot.append(perek_level_list)
                    perek_level_list = []
                else:
                    first_perek = False
                last_mishna = 0

            elif "@22" in each_line:
                match_object = mishna_number_regex.search(each_line)
                mishna_number = util.getGematria(match_object.group(1))
                diff = mishna_number - last_mishna
                if diff > 1:
                    perek_level_list.append("")
                    diff -= 1

                last_mishna = mishna_number

            else:
                each_line = clean_up_string(each_line)
                perek_level_list.append(each_line)

        rb_yonah_on_avot.append(perek_level_list)
        post_the_text(rb_yonah_on_avot)
    return rb_yonah_on_avot


def clean_up_string(string):
    string = add_bold(string, ['@11'], ['@33'])
    string = change_brackets_to_paranthesis(string)
    return string


def add_bold(string, list_of_opening_tags, list_of_closing_tags):
    for tag in list_of_opening_tags:
        string = string.replace(tag, '<b>')
    for tag in list_of_closing_tags:
        string = string.replace(tag, '</b>')
    return string


def change_brackets_to_paranthesis(string):
    string = string.replace('[', '(')
    string = string.replace(']', ')')
    return string


def post_the_text(ja):
    testing_file = codecs.open("testing_file.txt", 'w', 'utf-8')
    util.jagged_array_to_file(testing_file, ja, ['Perek', 'Mishna'])
    testing_file.close()
    ref = create_ref()
    text = create_text(ja)
    functions.post_text(ref, text)


def create_ref():
    ref = 'Rabbeinu Yonah on Pirkei Avot'
    return ref


def create_text(jagged_array):
    return {
        "versionTitle": "What the hell",
        "versionSource": "http://primo.nli.org.il/primo_library/libweb/action/dlDisplay.do?vid=NLI&docId=NNL_ALEPH001063744",
        "language": "he",
        "text": jagged_array
    }


def create_links(rb_ja):
    list_of_links = []
    for perek_index, perek in enumerate(rb_ja):
        for mishna_index, mishna in enumerate(perek):
            list_of_links.append(create_link_dicttionary(perek_index+1, mishna_index+1))
    functions.post_link(list_of_links)


def create_link_dicttionary(perek_bumber, mishna_number):
    return {
                "refs": [
                        "Pirkei Avot {}.{}".format(perek_bumber, mishna_number),
                        "Rabbeinu Yonah on Pirkei Avot {}.{}".format(perek_bumber, mishna_number)
                    ],
                "type": "commentary",
        }