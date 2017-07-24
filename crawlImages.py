#!/Users/lucidash/Projects/rankerScraper/rankerScraper/bin/python
# -*- coding: utf-8 -*-
from scrapy.selector import Selector
import asyncio
import logging
from contextlib import closing
import aiohttp # $ pip install aiohttp
import wget
import json
import os

v = []

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

async def download_images(image_url, file_name):
    async with aiohttp.ClientSession() as session:
        try:
            with async_timeout.timeout(10):
                download(image_url, file_name, session)
                return {'error': 200}
        except Exception as err:
            return {'error': err }


@asyncio.coroutine
def download(url, file_name, session, semaphore, chunk_size=1<<15):
    with (yield from semaphore): # limit number of concurrent downloads
        filename = "./images/{0}.jpg".format(file_name)
        logging.info('downloading %s', filename)
        response = yield from session.get(url)
        with closing(response), open(filename, 'wb') as file:
            while True: # save file
                chunk = yield from response.content.read(chunk_size)
                if not chunk:
                    break
                file.write(chunk)
        logging.info('done %s', filename)
    return filename, (response.status, tuple(response.headers.items()))


async def handle_task(task_id, work_queue):
    while not work_queue.empty():
        image_url, file_name = await work_queue.get()
        res = await download_images(image_url, file_name)
        if res['error'] == 200:
            pass
        else:
            print(image_url)
            print('error occured')

if __name__ == "__main__":
    init_from_file()

    urls = []
    for i in range(10000):
        urls.append( (v[i]['image_url'], v[i]['file_name']) )
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    with closing(aiohttp.ClientSession()) as session:
        loop = asyncio.get_event_loop()
        semaphore = asyncio.Semaphore(10)
        download_tasks = (download(x, y, session, semaphore) for x, y in urls)
        result = loop.run_until_complete(asyncio.gather(*download_tasks))
        loop.run_until_complete(asyncio.sleep(1))
        loop.close()
