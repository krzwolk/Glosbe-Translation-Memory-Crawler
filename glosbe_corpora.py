# -*- coding: utf-8 -*-
"""This script uses dictionary of words, for each word it gets parallel corpora
from website https://glosbe.com/, using api https://glosbe.com/a-api, and saves
to two parallel files, example command: $ python glosbe_corpora.py -l pol-eng -d dictionary.txt
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import logging
from argparse import ArgumentParser
from codecs import open as copen
from collections import OrderedDict
from time import time, sleep
import requests

g_api = 'https://glosbe.com/gapi'
g_api_tm = g_api + '/tm'
log = logging.getLogger()

def glosbe_corpora(lang1, lang2, phrases, interval=0):
    """TODO: Docstring for glosbe_corpora.

    :lang1: TODO
    :lang2: TODO
    :phrase: TODO
    :returns: TODO

    """
    req_time = 0
    i = 0
    for phrase in phrases:
        phrase = phrase.strip()
        if not phrase:
            continue
        params = {
            'from': lang1,
            'dest': lang2,
            'phrase': phrase,
            'pageSize': 30,
            'format': 'json'
        }
        try:
            page = 1
            while True:
                params['page'] = page
                if interval:
                    sleep(max(0, interval-(time()-req_time)))
                req_time = time()
                data = requests.get(g_api_tm, params=params).json()
                if not data['examples']:
                    break
                for example in data['examples']:
                    yield example['first'], example['second']
                    i += 1
                    if i % 100 == 0:
                        log.info('%i sentences recieved', i)
                page += 1
        except Exception as e:
            log.error(e)

def keep_unique(corpora_iter):
    """TODO: Docstring for keep_unique.

    :corpora_iter: TODO
    :returns: TODO

    """
    pairs = OrderedDict([(p, None) for p in corpora_iter])
    for sentences in pairs:
        yield sentences

def save_corpora(corpora_iter, path1, path2):
    """TODO: Docstring for save_corpora.

    :corpora_iter: TODO
    :path1: TODO
    :path2: TODO
    :returns: TODO

    """
    with copen(path1, 'w', encoding='utf-8') as f1,\
            copen(path2, 'w', encoding='utf-8') as f2:
        for sent1, sent2 in corpora_iter:
            sent1 = sent1.replace('\n', ' ').strip() + '\n'
            sent2 = sent2.replace('\n', ' ').strip() + '\n'
            f1.write(sent1)
            f2.write(sent2)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('urllib3').setLevel(logging.ERROR)
    logging.getLogger('requests').setLevel(logging.ERROR)

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-l', '--langs', required=True, help='Language pair to be used for corpora search, lng-lng, lng is ISO 693-3 identificator of language. Eg. for polish english pair it will be "pol-eng"')
    parser.add_argument('-d', '--dict', required=True, help='Path to dictionary of phrases, dictionary should contain one phrase per line')
    parser.add_argument('-p', '--prefix', default='corpora__', help='Prefix to be used for result parallel corpora files, files saved to current directory')
    parser.add_argument('--interval', default=0.5, type=float, help='Interval in seconds for every api query, api will not be called more often then this value, eg. if interval is set to 1, then api will be called only once per second')
    args = parser.parse_args()
    lang1, lang2 = args.langs.split('-')
    with copen(args.dict, encoding='utf-8') as dictionary:
        corpora = glosbe_corpora(lang1, lang2, dictionary, interval=args.interval)
        corpora = keep_unique(corpora)
        path1 = '{}{}.txt'.format(args.prefix, lang1)
        path2 = '{}{}.txt'.format(args.prefix, lang2)
        save_corpora(corpora, path1, path2)
