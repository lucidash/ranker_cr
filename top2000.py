#!/Users/lucidash/Projects/rankerScraper/rankerScraper/bin/python
# -*- coding: utf-8 -*-
import json

f = open('res.tsv', 'r')
f2 = open('top2000list', 'r')


res_dict = {}
top_2000_ids = f2.readline()[:-1].split(' ')
top_2000_ids = list(map(lambda x: int(x), top_2000_ids))

for i in top_2000_ids:
    res_dict[i] = {}
f2.close()

lists = {}


for line in f.readlines():
    line = line[:-1]
    _list = line.split('\t')
    _list_id = int(_list[0])
    if _list_id in res_dict:
        lists.append({
            'listId': _list_id,
            'title': _list[1],
            'url': _list[4],
            'formatType': _list[5],
        })

f.close()


f = open('top2000.json', 'w')
# print(lists)
print(json.dumps(lists))
f.write(json.dumps(lists))
