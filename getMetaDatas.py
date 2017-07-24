#!/Users/lucidash/Projects/rankerScraper/rankerScraper/bin/python
# -*- coding: utf-8 -*-

import aiohttp
import asyncio
import async_timeout
from scrapy.selector import Selector
import json

headers = {'user-agent': 'Opera/9.80 (X11; Linux x86_64; U; en) Presto/2.2.15 Version/10.10'}
res_dict = {}
extra_dict = {}

async def get_body(list_id):
    async with aiohttp.ClientSession() as session:
        try:
            with async_timeout.timeout(10):
                url = f'http://api.ranker.com/lists/{list_id}'
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        return {'error': 200, 'html': html}
                    else:
                        return {'error': response.status, 'html': ''}
        except Exception as err:
            return {'error': err, 'html': ''}

async def handle_task(task_id, work_queue):
    while not work_queue.empty():
        list_id = await work_queue.get()
        body = await get_body(list_id)
        if body['error'] == 200:
            res = json.loads(body['html'])
            v = dict()

            try:
                v['formatType'] = res['formatType']
            except Exception as e:
                v['formatType'] = ''
                print('formatType error')
                print(e)
                work_queue.put_nowait(list_id)
                continue

            try:
                v['rankerClassName'] = res['rankerClass']['name']
            except Exception as e:
                v['rankerClassName'] = ''
                print('rankerClassName error')
                print(e)
                work_queue.put_nowait(list_id)
                continue

            try:
                v['defaultTagName'] = res['defaultTag']['name']
            except Exception as e:
                v['defaultTagName'] = ''
                print('defaultTagName error')
                print(e)

            extra_dict[list_id] = v

            # write to file
            # f = open('res', 'a')
            # for i in result:
            #     f.write('{0}\t{1}\t{2}\t{3}\n'.format(i[0], i[1], i[2], i[3]))
            # f.close()
            # for new_url in get_urls(body['html']):
            #     if root_url in new_url and not new_url in crawled_urls:
            #         work_queue.put_nowait(new_url)
        elif body['error'] != 404 :
            print(f'error occurred in list_id = {list_id}')
            work_queue.put_nowait(list_id)

if __name__ == "__main__":
    list_ids = []
    q = asyncio.Queue()

    f = open('res.tsv', 'r')
    cnt = 0

    for line in f.readlines():
        line = line[:-1]
        t = line.split('\t')
        listId = t[0]
        res_dict[listId] = line
        list_ids.append(listId)
    f.close()

    [q.put_nowait(i) for i in list_ids]
    loop = asyncio.get_event_loop()
    tasks = [handle_task(task_id, q) for task_id in range(1,100)]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    # write to file
    f = open('res2', 'a')
    for k, v in res_dict.items():
        f.write(v)

        try:
            f.write(f'\t{extra_dict[k]["formatType"]}')
        except Exception as e:
            print(e)
            f.write('\t ')

        try:
            f.write(f'\t{extra_dict[k]["rankerClassName"]}')
        except Exception as e:
            print(e)
            f.write('\t ')

        try:
            f.write(f'\t{extra_dict[k]["defaultTagName"]}')
        except Exception as e:
            print(e)
            f.write('\t ')
        f.write('\n')
        # f.write(f'{v}\t{extra_dict[k]["formatType"]}\t{extra_dict[k]["rankerClassName"]}\t{extra_dict[k]["defaultTagName"]}\n')
    f.close()
