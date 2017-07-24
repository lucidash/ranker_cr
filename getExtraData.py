#!/Users/lucidash/Projects/rankerScraper/rankerScraper/bin/python
# -*- coding: utf-8 -*-

import aiohttp
import asyncio
import async_timeout
import json

headers = {'user-agent': 'Opera/9.80 (X11; Linux x86_64; U; en) Presto/2.2.15 Version/10.10'}
list_dict = {}

async def get_body(list_id):
    async with aiohttp.ClientSession() as session:
        try:
            with async_timeout.timeout(10):
                url = f'http://api.ranker.com/lists/{list_id}/items'
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
            res = res.get('listItems', {})

            list_dict[list_id]['listItems'] = res
            # for node in res:
            #     print (node.get('name', ''))
            #     print(node.get('rank', ''))
            #     print(node.get('blather', ''))

        elif body['error'] != 404 :
            print(f'error occurred in list_id = {list_id}')
            work_queue.put_nowait(list_id)

if __name__ == "__main__":
    q = asyncio.Queue()
    f = open('_top2000.json', 'r')
    r = f.readline()
    list_dict = json.loads(r)
    list_ids = list_dict.keys()
    f.close()

    [q.put_nowait(i) for i in list_ids]
    loop = asyncio.get_event_loop()
    tasks = [handle_task(task_id, q) for task_id in range(1,100)]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    for k, v in list_dict.items():
        print(k)

    # f = open('__top2000.json', 'w')
    # f.write(json.dumps(list_dict))
    # f.close()
