import json

def tmp():
    r = {}
    f = open('nodes.tmp.json', 'r')
    r = json.loads( f.readlines()[0] )
    f.close()


    f = open('top2000Images.json', 'r')
    image_dict = json.loads(f.readlines()[0])
    f.close()

    for k, v in r.items():
        try:
            node_image = v['nodeImage']
            node_id = k
            if 'imgixUrl' not in node_image:
                print  (node_id)
            image_url = node_image['imgixUrl'] + '?q=100'
            if image_url not in image_dict:
                image_dict[image_url] = []
            image_dict[image_url].append((None, None, node_id))
        except:
            pass

    print (len(r))
    print (len(image_dict))

    f = open('images.json', 'w')
    f.write(json.dumps(image_dict))
    f.close()

def remake():
    f = open('images.json', 'r')
    r = json.loads(f.readlines()[0])
    ra = []
    f.close()

    c, d = 0, 0

    for k, v in r.items():
        sp = k.split('/')
        fn  = k[k.rfind('/')+1:]
        fn = fn[:-6]
        fn = f'{sp[4]}_{sp[5]}_{fn}'

        ra.append({
            'image_url': k,
            'file_name': fn,
            'used_at': v
            })

    print(len(ra))

    f = open('images_array.json', 'w')
    f.write(json.dumps(ra))
    f.close()


# tmp()
# remake()
