#!/Users/lucidash/Projects/rankerScraper/rankerScraper/bin/python
# -*- coding: utf-8 -*-
from scrapy.selector import Selector
import asyncio
import async_timeout
import logging
from contextlib import closing
import aiohttp # $ pip install aiohttp
import wget
import json
import os
from pathlib import  Path

v = []

headers = {'user-agent': 'Opera/9.80 (X11; Linux x86_64; U; en) Presto/2.2.15 Version/10.10'}

def init_from_file():
    f = open('images_array.json', 'r')
    global v
    v = json.loads(f.readlines()[0])
    f.close()


def tmp():
    image_cnt = {}
    f = open('__top2000.json', 'r')
    tmp = json.loads(f.readlines()[0])
    f.close()
    cnt = 0
    image_title_to_used = {}
    for k, v in tmp.items():
        list_id = k
        list_items = v['listItems']
        for item in list_items:
            item_id = item['node']['id']
            try: 
                image_url = item['image']['imgixUrl']
                image_title =  image_url[image_url.rfind('/'):]
                print (image_title)
                image_url += '?q=100'
                if image_url in image_cnt:
                    image_title_to_used[image_title].append((list_id, item_id, None))
                    image_cnt[image_url].append((list_id, item_id, None))
                else:
                    image_title_to_used[image_title] = [(list_id, item_id, None)]
                    image_cnt[image_url] = [(list_id, item_id, None)]
            except:
                pass
            # print(f'{list_id},{item_id},{image_url}')


    f = open('top2000Images.json', 'w')
    f.write(json.dumps(image_cnt))
    f.close()


async def get_images(url):
    async with aiohttp.ClientSession() as session:
        try:
            with async_timeout.timeout(10):
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        res = await response.read()
                        return {'error': 200, 'images': res}
                    else:
                        return {'error': response.status, 'html': ''}
        except Exception as err:
            print(err)
            return {'error': err, 'html': ''}

async def handle_task(task_id, work_queue):
    while not work_queue.empty():
        image_url, file_name = await work_queue.get()
        res = await get_images(image_url)
        if res['error'] == 200:
            im = res['images']
            f = open("./images/{0}.jpg".format(file_name), 'wb')
            f.write(im)
            f.close()
        else:
            work_queue.put_nowait((image_url, file_name))
            # print(image_url)
            # print('error occured')

if __name__ == "__main__":
    init_from_file()

    urls = []
    q = asyncio.Queue()

    long_file_name_list = [2766, 14253, 16761, 20132, 44815, 45333, 46535, 61436, 61443, 86789, 86961, 89853, 90246, 90936, 90938, 90941, 90942]

    for i in long_file_name_list:
        q.put_nowait((v[i]['image_url'], v[i]['file_name']))
        # urls.append( (v[i]['image_url'], v[i]['file_name']) )

    loop = asyncio.get_event_loop()
    tasks = [handle_task(task_id, q) for task_id in range(1,20)]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
