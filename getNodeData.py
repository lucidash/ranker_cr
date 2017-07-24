#!/Users/lucidash/Projects/rankerScraper/rankerScraper/bin/python
# -*- coding: utf-8 -*-

import aiohttp
import asyncio
import async_timeout
import json

headers = {'user-agent': 'Opera/9.80 (X11; Linux x86_64; U; en) Presto/2.2.15 Version/10.10'}
list_dict = {}
node_dict = {}

async def get_body(node_id):
    async with aiohttp.ClientSession() as session:
        try:
            with async_timeout.timeout(10):
                url = f'http://api.ranker.com/nodes/{node_id}?include=properties'
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
        node_id = await work_queue.get()
        body = await get_body(node_id)
        if body['error'] == 200:
            try:
                res = json.loads(body['html'])
            except:
                print(f'json parse exception @ node_id = {node_id}')
                continue

            name = res.get('name', '')
            if name.find('&#39;') > -1:
                print(name)
                name.replace('&#39;', '\'')
            node_dict[node_id]['name'] = name

            node_properties = res.get('nodeProperties', [])
            node_dict[node_id]['nodeProperties'] = node_properties

            node_wiki = res.get('nodeWiki', {})
            node_dict[node_id]['nodeWiki'] = node_wiki

            node_dict[node_id]['node_id'] = node_id

            node_image = res.get('nodeImage', {})
            node_dict[node_id]['nodeImage'] = node_image

        elif body['error'] != 404 :
            print(f'error occurred in node_id = {node_id}')
            work_queue.put_nowait(node_id)


def aggregate_all_nodes():
    o = open('top2000list', 'r')
    order = o.readline()[:-1].split(' ')
    o.close()
    f = open('__top2000.json', 'r')
    global list_dict, node_dict
    list_dict = json.loads(f.readline()).copy()
    f.close()

    for k, v in list_dict.items():
        if k not in order:
            continue
        for item in v['listItems']:
            try:
                node_id = item['node']['id']
                node_dict[node_id] = {}
            except:
                print('fuck')

    node_ids = node_dict.keys()
    print(node_ids)
    print(len(node_ids))

    q = asyncio.Queue()
    [q.put_nowait(i) for i in node_ids]
    loop = asyncio.get_event_loop()
    tasks = [handle_task(task_id, q) for task_id in range(1,100)]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    f = open('nodes.tmp.json', 'w')
    f.write(json.dumps(node_dict))
    f.close()


def json_to_tsv():
    f = open('nodes.tmp.json', 'r')
    global node_dict
    node_dict = json.loads(f.readline())
    if '1000911368' in node_dict:
        del node_dict['1000911368']
    f.close()

    fl = [open(f'node_properties/node_properties{i}.tsv', 'w') for i in range(11)]
    for i in fl:
        i.write('nodeId\tpropertyId\ttype\tORG_EN')
        i.write('\n')

    cnt = -1
    for k, v in node_dict.items():
        cnt += 1
        cnt %= 11
        f = fl[cnt]
        val = v.get('name', '').replace('&#39;', '\'')
        f.write(f'{k}\t\tnode_name\t{val}')
        f.write('\n')
        val = v.get("nodeWiki", {}).get("wikiText", "")
        if val:
            if val.find('\n') > -1:
                val = val.replace('\n', '')
            val = val.replace('&#39;', '\'')
            f.write(f'{k}\t\tnode_wikiText\t{val}')
            f.write('\n')

        properties = v.get('nodeProperties', None)
        if properties is not None and len(properties) > 0:
            for property in properties:
                # print(f'{k}\t{property["propertyId"]}\tpropertyName\t{property.get("propertyName", "")}')
                val = 'propertyValue' in property and property['propertyValue']
                if val:
                    if val.find('\n') > -1:
                        val = val.replace('\n', '<br />')
                    val = val.replace('&#39;', '\'')
                    f.write(f'{k}\t{property["propertyId"]}\tpropertyValue\t{val}')
                    f.write('\n')

    [i.close for i in fl]

if __name__ == "__main__":
    aggregate_all_nodes()
    # json_to_tsv()
