#!/usr/bin/env python
# coding: utf-8

# Author Nicolas Blanc, InsIT, HEIG-VD
################################################################################
# MIT LICENSE:
# Copyright © 2021-present, Nicolas Blanc, InsIT, HEIG-VD
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# The Software is provided "as is", without warranty of any kind, express or
# implied, including but not limited to the warranties of merchantability,
# fitness for a particular purpose and noninfringement. In no event shall the
# authors or copyright holders X be liable for any claim, damages or other
# liability, whether in an action of contract, tort or otherwise, arising from,
# out of or in connection with the software or the use or other dealings in the
# Software.
# Except as contained in this notice, the name of the Author shall not be used
# in advertising or otherwise to promote the sale, use or other dealings in this
# Software without prior written authorization from the Author.
################################################################################

import os, re
import csv
import requests
from functools import reduce
import numpy as np
import pandas as pd
from lxml import etree

BASE_PATH = '/home/scrapy/output/'
if not os.path.isdir(BASE_PATH):
    os.makedirs(BASE_PATH, exist_ok=True)

BASE_URL = "https://models.geo.admin.ch/"
head = {
    'UserAgent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.7113.93 Safari/537.36',
    'Accept': 'Accept: text/html,application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Host': 'models.geo.admin.ch',
    'Referer': 'https://models.geo.admin.ch/'
}


class interlis_tag_scraper():

    def __init__(self, BASE_PATH, BASE_URL, head):
        self.BASE_PATH = BASE_PATH
        self.BASE_URL = BASE_URL
        self.head = head
        self.URL = self.BASE_URL + '?delimiter=/'

    def clean_tree(self, root):
        for elem in root.getiterator():
            elem.tag = etree.QName(elem).localname

        etree.cleanup_namespaces(root)

        return root

    def get_root_folders(self):
        res = requests.get(self.URL, headers=self.head)
        root = etree.XML(res.content)
        root = self.clean_tree(root)
        self.reps = [e.text for e in root.findall('.//CommonPrefixes/Prefix')]

        return self.reps

    def get_files_in_folder(self, rep):
        params = dict()
        params["prefix"] = rep
        res = requests.get(self.URL, params=params, headers=self.head)
        root = etree.XML(res.content)
        root = self.clean_tree(root)
        files = [e.text for e in root.findall('.//Contents/Key') if '.ili' in e.text]

        return files

    def get_files_content(self, file):
        FILE_URL = self.BASE_URL + file
        res = requests.get(FILE_URL, headers=self.head).text

        return {'path': file, 'content': res}

    def get_files_content_for_folder(self, rep):
        data = []
        for file in self.get_files_in_folder(rep):
            data.append(self.get_files_content(file))

        df = pd.DataFrame(data)
        df[['folder', 'file']] = df['path'].str.split('/', 1, expand=True)
        del df['path']
        df = df.reindex(['folder','file','content'], axis=1)

        return df

    def get_tags_for_file(self, file):
        URL = self.BASE_URL + file
        res = requests.get(URL, headers=self.head).text
        r = re.compile('^\s*!!@ ')
        tags = []
        for item in res.split("\r\n"):
            if r.search(item):
                tags.append([x.strip() for x in item.strip()[3:].strip().split('=', 1)])

        df_tags = pd.DataFrame(tags, columns=['key', 'value'])

        return df_tags

    def run(self):
        reps = self.get_root_folders()
        for rep in reps:
            files = self.get_files_in_folder(rep)
            for file in files:
                df_tags = self.get_tags_for_file(file)
                file_to_write = reduce(os.path.join,[BASE_PATH]+str(file).split('/'))+'.csv'
                if not os.path.isdir(os.path.dirname(file_to_write)):
                    os.makedirs(os.path.dirname(file_to_write), exist_ok=True)

                df_tags.to_csv(
                    file_to_write,
                    index_label='index',
                    sep=';',
                    quoting=csv.QUOTE_NONE,
                    quotechar='"',
                    escapechar="\\"
                )
                ntags = len(df_tags)
                print(f"{ntags} tags successfully extracted in file: {file_to_write}")

        return True


myScraper = interlis_tag_scraper(BASE_PATH, BASE_URL, head)
#myScraper.get_root_folders()

myScraper.run()

