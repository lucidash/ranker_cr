#!/Users/lucidash/Projects/rankerScraper/rankerScraper/bin/python
# -*- coding: utf-8 -*-
import json

list_dict = {}
order = []

def jsonToTsv:
    f = []
    for i in range(0, 20):
        f.append(open(f'res/res{i}.tsv', 'w'))
        f[i].write('listId\tnodeId\t구분\toriginal-EN\tFR\tDE\n')

    for k, v in enumerate(order):
        v = list_dict[v]
        i = int(k/100)
        if i >= len(f):
            i = i - 1
        f[i].write(f'{v.get("listId","")}\t\tlist title\t{v.get("title","")}\t\t\n')
        f[i].write(f'{v.get("listId","")}\t\tlist desc\t{v.get("description","")}\t\t\n')
        f[i].write(f'{v.get("listId","")}\t\tlist criteria\t{v.get("listCriteria","")}\t\t\n')
        f[i].write(f'{v.get("listId","")}\t\thtml title\t{v.get("titleTag","")}\t\t\n')
        for item in v['listItems']:
            f[i].write(f'{v.get("listId","")}\t{item.get("node", {}).get("id", "")}\titem title\t'
                       f'{item.get("name","")}\t\t\n')
            f[i].write(f'{v.get("listId","")}\t{item.get("node", {}).get("id", "")}\titem desc\t'
                       f'{item.get("blather","")}\t\t\n')

    for i in f:
        i.close()

if __name__ == "__main__":
    top2000 = open('top2000list', 'r')
    order = top2000.readline()[:-1].split(' ')
    top2000.close()
    f = open('__top2000.json', 'r')
    list_dict = json.loads(f.readline())
    f.close()

