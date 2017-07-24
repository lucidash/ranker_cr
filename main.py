#!/Users/lucidash/Projects/rankerScraper/rankerScraper/bin/python
# -*- coding: utf-8 -*-

import aiohttp
import asyncio
import async_timeout
from scrapy.selector import Selector
import json
import httplib2
import os

root_url = "http://www.ranker.com/tag/facetedListSearch.htm"
url_hub = [], [root_url]
crawled_key = {}
headers = {'user-agent': 'Opera/9.80 (X11; Linux x86_64; U; en) Presto/2.2.15 Version/10.10'}

result_dict = {}
extra_dict = {}

# for All Lists of ranker.com
async def get_body(tag_id, page):
    async with aiohttp.ClientSession() as session:
        try:
            with async_timeout.timeout(10):
                param = dict()
                param['tagIds'] = tag_id
                param['page'] = page
                param['limit'] = 100
                param['pagetype'] = 'ATTRIBUTEPAGE'
                async with session.get(root_url, headers=headers, params=param) as response:
                    if response.status == 200:
                        html = await response.text()
                        return {'error': 200, 'html': html}
                    else:
                        return {'error': response.status, 'html': ''}
        except Exception as err:
            return {'error': err, 'html': ''}

async def get_body2(url):
    async with aiohttp.ClientSession() as session:
        try:
            with async_timeout.timeout(10):
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        return {'error': 200, 'html': html}
                    else:
                        return {'error': response.status, 'html': ''}
        except Exception as err:
            return {'error': err, 'html': ''}

async def get_body3(list_id):
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
        tag_id, page, url, title, listId = await work_queue.get()

        if url is None:
            body = await get_body(tag_id, page)
        elif listId is None:
            body = await get_body2(url)
        else:
            body = await get_body3(listId)

        if body['error'] == 200:
            if url is None:
                sel = Selector(text=body['html'])
                articles = sel.css('article').extract()

                for article in articles:
                    sel = Selector(text=article)
                    link = sel.css('a::attr(href)').extract_first()
                    topic = sel.css(' .black').css('span::text').extract_first()
                    meta_data = sel.css('div').css('span').css('.uppercase').css('.rnkrBlue').css('span::text').extract()
                    views = 0
                    votes = 0
                    for i in meta_data:
                        data = i.strip()
                        if data[-5:] == 'views':
                            views = data[:-6]
                            if views[-1:] == 'k':
                                views = int(float(views[:-1]) * 1000)
                            elif views[-1:] == 'M':
                                views = int(float(views[:-1]) * 1000000)
                            else:
                                views = int(views)
                        elif data[-5:] == 'votes':
                            votes = data[:-6]
                            if votes[-1:] == 'k':
                                votes = int(float(votes[:-1]) * 1000)
                            elif votes[-1:] == 'M':
                                votes = int(float(votes[:-1]) * 1000000)
                            else:
                                votes = int(votes)
                    result_dict[topic] = (views, votes, link, tag_id, page, None)
                    work_queue.put_nowait((tag_id, page, link, topic, None))
            elif listId is None:
                sel = Selector(text=body['html'])
                try:
                    list_id = sel.xpath('//meta[contains(@property,"listid")]/@content').extract_first()
                    tmp = result_dict[title]
                    result_dict[title] = (tmp[0], tmp[1], tmp[2], tmp[3], tmp[4], list_id)
                    work_queue.put_nowait((tag_id, page, url, title, list_id))
                except Exception as e:
                    print(e)
            else:
                res = json.loads(body['html'])
                v = dict()
                try:
                    v['formatType'] = res['formatType']
                except Exception as e:
                    v['formatType'] = ''
                    print(e)

                try:
                    v['rankerClassName'] = res['rankerClass']['name']
                except Exception as e:
                    v['rankerClassName'] = ''
                    print(e)

                try:
                    v['defaultTagName'] = res['defaultTag']['name']
                except Exception as e:
                    v['defaultTagName'] = ''
                    print(e)
                extra_dict[title] = v

            # write to file
            # f = open('res', 'a')
            # for i in result:
            #     f.write('{0}\t{1}\t{2}\t{3}\n'.format(i[0], i[1], i[2], i[3]))
            # f.close()
            # for new_url in get_urls(body['html']):
            #     if root_url in new_url and not new_url in crawled_urls:
            #         work_queue.put_nowait(new_url)
        elif body['error'] != 404 :
            # print('error occured when tag_id = {}, page = {}'.format(tag_id, page))
            print(f'error occured when tag_id = {tag_id} page = {page} url = {url} title = {title}')
            work_queue.put_nowait((tag_id, page, url, title, listId))
# def remove_fragment(url):
#     pure_url, frag = urldefrag(url)
#     return pure_url

# def get_urls(html):
#     new_urls = [url.split('"')[0] for url in str(html).replace("'",'"').split('href="')[1:]]
#     return [urljoin(root_url, remove_fragment(new_url)) for new_url in new_urls]

if __name__ == "__main__":
    q = [None,]
    for i in range(1, 20):
        q.append(asyncio.Queue())
    print (len(q))
    [q[i].put_nowait((i, j, None, None, None)) for i in range(1,20) for j in range(1,120)]
    # [q.put_nowait((i, j, None, None, None)) for i in range(1,300) for j in range(1,120)]
    # [q.put_nowait((i, j, None, None, None)) for i in range(1,10) for j in range(1,10)]
    loop = asyncio.get_event_loop()
    tasks = [handle_task(task_id, q[task_id]) for task_id in range(1,20)]
    print(len(tasks))
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    # write to file
    f = open('res2', 'a')
    for k, v in result_dict.items():
        if v[5] is not None:
            f.write(f'{v[5]}\t{v[0]}\t{v[1]}\t{v[2]}\t{v[3]}\t{extra_dict[k]["formatType"]}\t{extra_dict[k]["rankerClassName"]}\t{extra_dict[k]["defaultTagName"]}\n')
        # f.write('{0}\t{4}\t{5}\t{1}\t{2}\t{3}\n'.format(k, v[0], v[1], v[2], v[3], v[4]))
    f.close()
