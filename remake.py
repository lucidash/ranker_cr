#!/Users/lucidash/Projects/rankerScraper/rankerScraper/bin/python
# -*- coding: utf-8 -*-

f = open('res', 'r')
r = open('res.tsv', 'a')

for line in f.readlines():
    t = line.split('\t')
    tmp = t[0]
    t[0] = t[1]
    t[1] = tmp

    if int(t[0]) > -1:
        str = t[0]
        for i, v in enumerate(t):
            if i > 0:
                str = str + '\t' + v
        r.write(str)
