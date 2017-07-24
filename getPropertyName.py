import json
r = {}
f = open('nodes.tmp.json', 'r')
r = json.loads( f.readlines()[0] )
f.close()

property_dict = {}

for k, v in r.items():
    try:
        properties = v['nodeProperties']
        for p in properties:
            p_id = p['propertyId']
            pName = p['propertyName']
            pDName = p['displayName']

            property_dict[p_id] = (pName, pDName)
    except:
        pass

print (len(property_dict))

f = open('properties.json', 'w')
f.write(json.dumps(property_dict))
f.close()
